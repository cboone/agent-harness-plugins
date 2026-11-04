"""Shared bounded execution, regular-file IO and evidence publication."""

from contextlib import contextmanager, ExitStack
import hashlib
import base64
import fcntl
from contextvars import ContextVar
import uuid
import json
import math
import os
from pathlib import Path
import selectors
import signal
import stat
import subprocess
import sys
import threading
import tempfile
import time

OUTPUT_LIMIT = 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def failure_cause(error):
    cause = f"{type(error).__name__}: {error}"
    for name in ("stdout", "stderr"):
        value = getattr(error, name, None)
        if value is not None:
            value = value[:OUTPUT_LIMIT]
            if isinstance(value, bytes):
                value = value.decode("utf-8", errors="replace")
            cause += f"; {name}: {value!r}"
    return cause


def write_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(encode_json(value, indent=2) + "\n")
    temporary.replace(path)


def relative(value):
    require(isinstance(value, str) and value, "input path must be a string")
    path = Path(value)
    require(not path.is_absolute() and all(p not in ("", ".", "..") for p in value.split("/")),
            "input paths must be normalized relative paths")
    return path


@contextmanager
def regular_file(path, *, root=None, reserve=False, write=False, read=True, lock=None):
    current = path.parent.resolve() if root is None else root.resolve()
    parts = (path.name,) if root is None else path.relative_to(root).parts
    for part in parts:
        current = current / part
        require(not current.is_symlink(), "symlinked input paths are unsupported: " + str(path))
    created = False
    flags = os.O_RDWR if reserve else os.O_RDONLY
    try:
        if reserve:
            try:
                descriptor = os.open(current, flags | os.O_NONBLOCK | os.O_CREAT | os.O_EXCL, 0o666)
                created = True
            except FileExistsError:
                descriptor = os.open(current, flags | os.O_NONBLOCK)
        elif write:
            descriptor = os.open(current, os.O_RDWR | os.O_NONBLOCK)
        else:
            descriptor = os.open(current, os.O_RDONLY | os.O_NONBLOCK)
        try:
            info = os.fstat(descriptor)
            require(stat.S_ISREG(info.st_mode), "input must be a regular file")
            if lock is not None:
                deadline = time.monotonic() + 0.25
                while True:
                    try:
                        fcntl.flock(descriptor, lock | fcntl.LOCK_NB)
                        break
                    except BlockingIOError:
                        if time.monotonic() >= deadline:
                            raise TimeoutError("journal lock deadline exceeded")
                        time.sleep(0.001)
            with os.fdopen(descriptor, "r+b" if reserve or write else "rb", closefd=False) as stream:
                data = stream.read() if read else b""
                yield stream, data, stat.S_IMODE(info.st_mode), created
        finally:
            os.close(descriptor)
    except RuntimeError as error:
        raise ValueError(failure_cause(error)) from error


def read_regular(path, *, root=None, lock=False):
    with regular_file(path, root=root, lock=fcntl.LOCK_SH if lock else None) as (_, data, mode, _):
        return data, mode


def terminate_group(pid, requested_signal=signal.SIGKILL):
    try:
        os.killpg(pid, requested_signal)
    except ProcessLookupError:
        pass


def live_group(pid):
    listing = subprocess.run(["ps", "-axo", "pid=,pgid=,stat="], capture_output=True,
                             text=True, check=True, timeout=0.25)
    members = []
    for line in listing.stdout.splitlines():
        member, group, state = line.split()
        if int(group) == pid and not state.startswith("Z"):
            members.append(int(member))
    return members


def stop_group(pid):
    remaining, error = None, None
    try:
        remaining = live_group(pid)
        if not remaining:
            return remaining, None
        for requested_signal in (signal.SIGTERM, signal.SIGKILL):
            terminate_group(pid, requested_signal)
            deadline = time.monotonic() + 0.2
            while True:
                remaining = live_group(pid)
                if not remaining:
                    return remaining, None
                if time.monotonic() >= deadline:
                    break
                time.sleep(0.01)
    except (OSError, ValueError, subprocess.SubprocessError) as failure:
        error = failure_cause(failure)
        try:
            if isinstance(failure, PermissionError) and not live_group(pid):
                return [], None
            terminate_group(pid)
        except OSError as failure:
            error += "; cleanup: " + failure_cause(failure)
    return remaining, error


def observe(journal, kind, target, **data):
    if journal is not None:
        try:
            journal.append(kind, target, **data)
        except (OSError, ValueError) as error:
            journal.note_failure(failure_cause(error))


def read_spool(stream):
    stream.seek(0)
    return stream.read(OUTPUT_LIMIT + 1)


def command(argv, root, timeout, *, git_boundary=False, env_overrides=None, journal=None, target=None):
    require(callable(getattr(os, "waitid", None)) and hasattr(os, "WNOWAIT"),
            "runtime requires waitid and WNOWAIT for safe group cleanup")
    journal = journal or ACTIVE_JOURNAL.get()
    target = target or "aux/" + uuid.uuid4().hex
    observe(journal, "command", target, argv=argv)
    with tempfile.TemporaryDirectory(prefix="checked-plant-cache-") as cache:
        env = dict(os.environ, PYTHONPYCACHEPREFIX=cache, PYTHONDONTWRITEBYTECODE="1")
        env.update(env_overrides or {})
        if git_boundary:
            env = {key: value for key, value in env.items() if not key.startswith("GIT_")}
            env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull,
                       GIT_CONFIG_NOSYSTEM="1", GIT_CEILING_DIRECTORIES=str(root.parent.resolve()),
                       GIT_TERMINAL_PROMPT="0")
        with (Path(cache) / "stdout").open("w+b") as stdout_file, (Path(cache) / "stderr").open("w+b") as stderr_file:
            try:
                process = subprocess.Popen(argv, cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           start_new_session=True)
            except OSError as error:
                observe(journal, "error", target, cause=failure_cause(error))
                raise
            observe(journal, "started", target, pgid=process.pid)
            deadline = time.monotonic() + timeout
            timed_out, output_truncated, reaped = False, False, False
            termination_requested, capture_error = False, None
            counts = {process.stdout: 0, process.stderr: 0}
            channels = {process.stdout: "stdout", process.stderr: "stderr"}
            try:
                with selectors.DefaultSelector() as selector:
                    for transport, destination in ((process.stdout, stdout_file), (process.stderr, stderr_file)):
                        os.set_blocking(transport.fileno(), False)
                        selector.register(transport, selectors.EVENT_READ, destination)
                    while selector.get_map():
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            timed_out = True
                            observe(journal, "flags", target, timed_out=True)
                            break
                        for key, _ in selector.select(remaining):
                            try:
                                chunk = os.read(key.fd, 65536)
                            except BlockingIOError:
                                continue
                            if not chunk:
                                observe(journal, "eof", target, channel=channels[key.fileobj])
                                selector.unregister(key.fileobj)
                                continue
                            room = OUTPUT_LIMIT - counts[key.fileobj]
                            if chunk[:room]:
                                observe(journal, "bytes", target, channel=channels[key.fileobj], offset=counts[key.fileobj],
                                        base64=base64.b64encode(chunk[:room]).decode("ascii"))
                            key.data.write(chunk[:room])
                            counts[key.fileobj] += min(len(chunk), room)
                            if len(chunk) > room:
                                output_truncated = True
                                observe(journal, "flags", target, output_truncated=True)
                                break
                        if output_truncated:
                            break
                if not (timed_out or output_truncated):
                    while (exited := os.waitid(os.P_PID, process.pid, os.WEXITED | os.WNOWAIT | os.WNOHANG)) is None:
                        if time.monotonic() >= deadline:
                            timed_out = True
                            observe(journal, "flags", target, timed_out=True)
                            break
                        time.sleep(min(0.01, max(0, deadline - time.monotonic())))
                    if exited is not None:
                        code = exited.si_status if exited.si_code == os.CLD_EXITED else -exited.si_status
                        observe(journal, "exit", target, code=code)
            except OSError as error:
                capture_error = failure_cause(error)
                observe(journal, "error", target, cause=capture_error)
            finally:
                process.stdout.close()
                process.stderr.close()
                # Keep the leader unreaped until its owned group is stopped and checked.
                termination_requested = True
                observe(journal, "flags", target, timed_out=timed_out, output_truncated=output_truncated,
                        termination_requested=True)
                remaining_pids, cleanup_error = stop_group(process.pid)
                observe(journal, "cleanup", target, remaining_pids=remaining_pids, cause=cleanup_error)
                if not reaped:
                    try:
                        process.wait(timeout=1)
                        reaped = True
                        observe(journal, "exit", target, code=process.returncode)
                    except subprocess.TimeoutExpired:
                        pass
                observe(journal, "reap", target, reaped=reaped)
            output = []
            for channel, stream in (("stdout", stdout_file), ("stderr", stderr_file)):
                try:
                    data = read_spool(stream)
                    output.append(data)
                    observe(journal, "loaded", target, channel=channel, sha256=digest(data), size=len(data))
                except OSError as error:
                    capture_error = failure_cause(error)
                    output.append(b"")
                    observe(journal, "capture-error", target, channel=channel, cause=capture_error)
            output_truncated = output_truncated or any(len(data) > OUTPUT_LIMIT for data in output)
            observe(journal, "flags", target, output_truncated=output_truncated)
            stdout, stderr = [data[:OUTPUT_LIMIT].decode("utf-8", errors="replace") for data in output]
    return dict(exit_code=process.returncode, stdout=stdout, stderr=stderr, timed_out=timed_out,
                termination_requested=termination_requested, terminated=process.returncode is not None and process.returncode < 0,
                reaped=reaped, output_truncated=output_truncated, capture_error=capture_error,
                pgid=process.pid, remaining_pids=remaining_pids, cleanup_error=cleanup_error)


def valid_step(result):
    return (result["timed_out"] is False and result["reaped"] is True and result["output_truncated"] is False
            and result["capture_error"] is None and result["remaining_pids"] == [] and result["cleanup_error"] is None)


def identity(info):
    return info.st_dev, info.st_ino


@contextmanager
def reserve_outputs(paths, protected):
    streams, contents, created = [], [], []
    published = False
    with ExitStack() as stack:
        try:
            for path in paths:
                stream, data, _, is_new = stack.enter_context(regular_file(path, reserve=True))
                if is_new:
                    created.append((path, identity(os.fstat(stream.fileno()))))
                streams.append(stream)
                contents.append(data)
            identities = [identity(os.fstat(stream.fileno())) for stream in streams]
            protected_ids = {identity(path.stat()) for path in protected}
            require(len(set(identities)) == len(identities) and not (set(identities) & protected_ids),
                    "record destination aliases evidence, input or another record")
            yield streams, contents
            published = True
        finally:
            if not published:
                for path, reserved in created:
                    if path.exists() and identity(path.stat()) == reserved:
                        path.unlink()


ROW_STATES = {"not-run", "setup-error", "exited", "exit-unknown"}
ROW_FIELDS = {"argv", "pipeline", "state", "exit_code", "duration_seconds", "capture_digests", "result", "cause", "started", "exit_observed", "captures", "input_fingerprints"}


class CommandRow(dict):
    """Constructor provenance retained until an emitted receipt is published."""


def row_for(args, pipeline=None):
    return CommandRow(argv=args, pipeline=pipeline, state="not-run", exit_code=None, duration_seconds=None,
                      capture_digests=None, result=None, cause="not attempted", started=False, exit_observed=False,
                      captures={key: dict(eof_observed=False, loaded=False, cause=None) for key in ("stdout", "stderr")},
                      input_fingerprints={phase: [] for phase in ("start", "end")})


def valid_duration(value):
    return (value is None or type(value) is int and value >= 0
            or type(value) is float and value >= 0 and math.isfinite(value))


def validate_row(row):
    require(isinstance(row, dict) and set(row) == ROW_FIELDS, "invalid command row fields")
    require(row["state"] in ROW_STATES, "unknown command state")
    require(row["cause"] is None or isinstance(row["cause"], str), "invalid command cause")
    require(row["started"] is None or type(row["started"]) is bool, "invalid start fact")
    require(type(row["exit_observed"]) is bool, "invalid exit observation")
    require(set(row["captures"]) == {"stdout", "stderr"}, "missing stream facts")
    for facts in row["captures"].values():
        require(set(facts) == {"eof_observed", "loaded", "cause"}
                and type(facts["eof_observed"]) is bool and type(facts["loaded"]) is bool
                and (facts["cause"] is None or isinstance(facts["cause"], str)), "invalid stream facts")
    require(isinstance(row["input_fingerprints"], dict) and set(row["input_fingerprints"]) == {"start", "end"},
            "missing input fingerprint phases")
    for observations in row["input_fingerprints"].values():
        require(isinstance(observations, list), "invalid input fingerprint observations")
        for observation in observations:
            require(isinstance(observation, dict) and set(observation) == {"phase", "value", "cause"}
                    and observation["phase"] in ("start", "end")
                    and (observation["value"] is None or isinstance(observation["value"], dict))
                    and (observation["cause"] is None or isinstance(observation["cause"], str)), "invalid input fingerprint")
    duration = row["duration_seconds"]
    require(valid_duration(duration),
            "invalid command duration")
    require(row["state"] not in ("not-run", "setup-error") or row["started"] is not True, "observed start cannot be unrun")
    if row["state"] in ("not-run", "setup-error"):
        require(not row["exit_observed"] and row["exit_code"] is None and row["result"] is None and row["capture_digests"] is None,
                "unavailable command result must be null")
        return
    result = row["result"]
    known = row["state"] == "exited"
    require(row["exit_observed"] is known and (not known or row["started"] is True), "inconsistent execution facts")
    require(type(row["exit_code"]) is int if known else row["exit_code"] is None, "inconsistent command exit state")
    require(isinstance(result, dict) and type(result["exit_code"]) is type(row["exit_code"])
            and result["exit_code"] == row["exit_code"], "inconsistent command exit")
    require(all(isinstance(result[key], str) for key in ("stdout", "stderr")), "invalid captures")
    require(row["capture_digests"] == {key: digest(result[key].encode()) for key in ("stdout", "stderr")},
            "capture digest mismatch")
    if row["pipeline"] is not None:
        for stage in result["stages"]:
            validate_row(stage)


def record_result(row, result, duration, *, started=True, captures=None):
    result = dict(result)
    if row["exit_observed"]:
        require(result["exit_code"] is None or result["exit_code"] == row["exit_code"], "conflicting observed exits")
        result["exit_code"] = row["exit_code"]
        if row["result"]["reaped"]:
            result["reaped"] = True
    if row["duration_seconds"] is not None:
        duration = row["duration_seconds"]
    if captures is None:
        eof = not (result["timed_out"] or result["output_truncated"] or result["capture_error"])
        captures = {key: dict(eof_observed=eof, loaded=True, cause=result["capture_error"]) for key in ("stdout", "stderr")}
    for channel, incoming in captures.items():
        previous = row["captures"][channel]
        if previous["loaded"] and not incoming["loaded"]:
            result[channel] = row["result"][channel]
        row["captures"][channel] = dict(eof_observed=previous["eof_observed"] or incoming["eof_observed"],
                                        loaded=previous["loaded"] or incoming["loaded"],
                                        cause=previous["cause"] or incoming["cause"])
    causes = [result[key] for key in ("capture_error", "cleanup_error") if result[key] is not None]
    for key, message in (("timed_out", "timeout"), ("output_truncated", "capture truncated")):
        if result[key]:
            causes.append(message)
    if result["exit_code"] is None:
        causes.append("process exit unavailable")
    if result["remaining_pids"]:
        causes.append("process group cleanup incomplete")
    known = type(result["exit_code"]) is int
    row.update(state="exited" if known else "exit-unknown", started=True if row["started"] is True or known else started,
               exit_observed=known, exit_code=result["exit_code"], result=result, duration_seconds=duration,
               capture_digests={key: digest(result[key].encode()) for key in ("stdout", "stderr")},
               cause="; ".join(causes) if causes else None)
    validate_row(row)


def row_complete(row):
    return (row["state"] == "exited" and row["started"] is True and row["exit_observed"] is True
            and row["duration_seconds"] is not None and valid_step(row["result"])
            and all(facts["eof_observed"] and facts["loaded"] and facts["cause"] is None
                    for facts in row["captures"].values()))


def passed(row, expected):
    return (row["state"] == "exited" and type(row["exit_code"]) is int and row["exit_code"] == expected
            and row_complete(row)
            and (row["pipeline"] is None or row["result"]["pipeline_complete"] is True
                 and all(passed(stage, 0) for stage in row["result"]["stages"])))


def record_error(row, cause, duration):
    require(row["started"] is not True and not row["exit_observed"], "cannot discard observed execution")
    row.update(state="setup-error", started=None, cause=cause, duration_seconds=duration, exit_code=None, result=None, capture_digests=None)
    validate_row(row)


def receipt_rows(value):
    pending = [*value["checks"], value["action"]]
    while pending:
        row = pending.pop()
        yield row
        if isinstance(row.get("result"), dict) and "stages" in row["result"]:
            pending.extend(row["result"]["stages"])


def write_receipt(path, value):
    require(isinstance(value, ReceiptFold), "receipt bypassed journal constructor")
    validate_fold(value)
    for row in receipt_rows(value):
        require(isinstance(row, CommandRow), "receipt row bypassed constructor")
        validate_row(row)
    write_json(path, value)


def parse_json(data):
    def reject(value):
        raise ValueError("non-finite JSON constant: " + value)
    def finite(value):
        result = float(value)
        require(math.isfinite(result), "non-finite JSON number: " + value)
        return result
    return json.loads(data, parse_constant=reject, parse_float=finite)


def encode_json(value, **options):
    return json.dumps(value, allow_nan=False, **options)


FACT_KINDS = {"begin", "manifest", "fingerprint", "allow-action", "refused", "finished", "command",
              "started", "exit", "bytes", "eof", "loaded", "capture-error", "flags", "cleanup", "reap", "error", "journal-error"}
ACTIVE_JOURNAL = ContextVar("checked_gate_journal", default=None)


class ReceiptFold(dict):
    """A receipt projection created exclusively by folding recorded facts."""


class FactJournal:
    def __init__(self, path, *, create=False):
        self.path = Path(path)
        self.pending, self.failures = [], set()
        self.mutex = threading.RLock()
        if create:
            with regular_file(self.path, reserve=True, read=False, lock=fcntl.LOCK_EX) as (_, _, _, created):
                require(created, "journal already exists")
        else:
            read_regular(self.path, lock=True)

    def note_failure(self, cause):
        with self.mutex:
            self.failures.add(cause)

    def append(self, kind, target="root", **data):
        with self.mutex:
            require(kind in FACT_KINDS and isinstance(target, str), "unknown journal fact")
            fact = dict(schema=1, id=uuid.uuid4().hex, kind=kind, target=target, at=time.monotonic(), data=data)
            encode_json(fact)
            self.pending.append(fact)
            try:
                self.flush()
            except (OSError, ValueError) as error:
                self.failures.add(failure_cause(error))
                raise
            return fact

    def flush(self):
        with self.mutex:
            if self.failures:
                self.pending.append(dict(schema=1, id=uuid.uuid4().hex, kind="journal-error", target="root",
                                         at=time.monotonic(), data=dict(cause="; ".join(sorted(self.failures)))))
                self.failures.clear()
            if not self.pending:
                return
            with regular_file(self.path, write=True, read=False, lock=fcntl.LOCK_EX) as (stream, _, _, _):
                while self.pending:
                    fact = self.pending[0]
                    stream.seek(0, os.SEEK_END)
                    stream.write(("\n" + encode_json(fact, separators=(",", ":")) + "\n").encode())
                    stream.flush()
                    self.pending.pop(0)

    def facts(self):
        self.flush()
        facts, failures, seen = [], [], {}
        for line in read_regular(self.path, lock=True)[0].splitlines():
            if not line.strip():
                continue
            try:
                fact = parse_json(line)
                require(isinstance(fact, dict) and fact.get("schema") == 1 and fact.get("kind") in FACT_KINDS,
                        "invalid journal fact")
                if fact["id"] in seen:
                    require(encode_json(seen[fact["id"]], sort_keys=True) == encode_json(fact, sort_keys=True),
                            "conflicting journal fact identity")
                    continue
                seen[fact["id"]] = fact
                facts.append(fact)
            except (ValueError, TypeError, KeyError) as error:
                failures.append((digest(line), failure_cause(error)))
        recorded = {f["data"].get("fragment") for f in facts if f["kind"] == "journal-error"}
        for fragment, cause in failures:
            if fragment not in recorded:
                facts.append(self.append("journal-error", fragment=fragment, cause=cause))
                recorded.add(fragment)
        return facts

    def receipt(self):
        return fold_receipt(self.facts())


@contextmanager
def journal_context(journal):
    token = ACTIVE_JOURNAL.set(journal)
    try:
        yield
    finally:
        ACTIVE_JOURNAL.reset(token)


def fold_command(facts, target, args, pipeline=None):
    row = row_for(args, pipeline)
    events = [f for f in facts if f["target"] == target]
    if not events:
        return row
    result = dict(exit_code=None, stdout="", stderr="", timed_out=False, termination_requested=False,
                  terminated=False, reaped=False, output_truncated=False, capture_error=None,
                  pgid=None, remaining_pids=None, cleanup_error=None)
    if pipeline is not None:
        result.update(stages=[], pipeline_complete=False)
    buffers = {key: bytearray() for key in ("stdout", "stderr")}
    captures = {key: dict(eof_observed=False, loaded=False, cause=None) for key in buffers}
    errors, started, observed, attempted, start, finish = [], False, False, False, None, None
    for fact in events:
        kind, data = fact["kind"], fact["data"]
        if kind == "command":
            attempted = True
            start = fact["at"] if start is None else start
        elif kind == "fingerprint":
            require(data["phase"] in row["input_fingerprints"], "unknown check boundary")
            row["input_fingerprints"][data["phase"]].append(data)
        elif kind == "started":
            started = True
            result["pgid"] = data["pgid"]
        elif kind == "exit":
            if observed:
                require(result["exit_code"] == data["code"], "conflicting observed exits")
            else:
                result["exit_code"], finish, observed = data["code"], fact["at"], True
        elif kind == "bytes":
            channel, raw = data["channel"], base64.b64decode(data["base64"], validate=True)
            require(data["offset"] == len(buffers[channel]), "noncontiguous captured bytes")
            require(len(buffers[channel]) + len(raw) <= OUTPUT_LIMIT, "journal capture exceeds limit")
            buffers[channel].extend(raw)
        elif kind == "eof":
            captures[data["channel"]]["eof_observed"] = True
        elif kind == "loaded":
            channel = data["channel"]
            captures[channel]["loaded"] = True
            if data["sha256"] != digest(buffers[channel]) or data["size"] != len(buffers[channel]):
                captures[channel]["cause"] = "capture file differs from observed bytes"
        elif kind == "capture-error":
            captures[data["channel"]]["cause"] = data["cause"]
        elif kind == "flags":
            for key in ("timed_out", "termination_requested", "output_truncated"):
                result[key] = result[key] or data.get(key, False)
        elif kind == "cleanup":
            result["remaining_pids"] = data["remaining_pids"]
            if data["cause"]:
                result["cleanup_error"] = data["cause"]
        elif kind == "reap":
            result["reaped"] = result["reaped"] or data["reaped"]
        elif kind == "error":
            errors.append(data["cause"])
    errors.extend(f"{key}: {value['cause']}" for key, value in captures.items() if value["cause"])
    if not attempted and not started and not observed:
        if errors:
            record_error(row, "; ".join(errors), None)
        return row
    duration = (finish if finish is not None else max(f["at"] for f in events)) - start if start is not None else None
    if not started and not observed and errors:
        record_error(row, "; ".join(errors), duration)
        row["started"] = False
        return row
    result.update(stdout=bytes(buffers["stdout"]).decode("utf-8", errors="replace"),
                  stderr=bytes(buffers["stderr"]).decode("utf-8", errors="replace"),
                  capture_error="; ".join(dict.fromkeys(errors)) or None,
                  terminated=observed and result["exit_code"] < 0)
    record_result(row, result, duration, started=started or None, captures=captures)
    return row


def boundaries_match(value):
    try:
        before, checks = value["before"], value["manifest"]["checks"]
        if before is None or len(value["checks"]) != len(checks):
            return False
        for row, declaration in zip(value["checks"], checks, strict=True):
            names = set(declaration["inputs"])
            expected = dict(before, index=before["index"] if "index" in names else None,
                            files={name: before["files"][name] for name in names - {"HEAD", "tree", "index"}})
            for phase in ("start", "end"):
                observations = row["input_fingerprints"][phase]
                if len(observations) != 1 or observations[0]["cause"] is not None or observations[0]["value"] != expected:
                    return False
        return True
    except (KeyError, TypeError):
        return False


def fold_receipt(facts):
    require(isinstance(facts, list) and facts, "missing fact journal")
    require(facts[0]["kind"] == "begin", "journal has no beginning")
    value = ReceiptFold(schema=1, kind="checked-gate", complete=False, success=False, manifest=None,
                        manifest_sha256=None, checks=[], action=row_for(None), before=None, after_checks=None,
                        after_action=None, action_refused=True, cause="run did not complete", journal_errors=[], journal=facts)
    causes, allowed, requested_success = [], False, False
    for fact in facts:
        require(fact["schema"] == 1 and fact["kind"] in FACT_KINDS, "unknown journal schema")
        kind, data = fact["kind"], fact["data"]
        if fact["target"] != "root":
            continue
        if kind == "manifest":
            value.update(manifest=data["value"], manifest_sha256=data["sha256"])
        elif kind == "fingerprint":
            require(data["phase"] in ("before", "after_checks", "after_action"), "unknown fingerprint phase")
            value[data["phase"]] = data["value"]
        elif kind == "allow-action":
            allowed = True
        elif kind == "refused":
            causes.append(data["cause"])
        elif kind == "finished":
            require(type(data["success"]) is bool, "invalid completion fact")
            value["complete"], requested_success = True, data["success"]
        elif kind == "journal-error":
            value["journal_errors"].append(data["cause"])
    manifest = value["manifest"]
    if isinstance(manifest, dict) and isinstance(manifest.get("checks"), list):
        for index, declaration in enumerate(manifest["checks"]):
            declaration = declaration if isinstance(declaration, dict) else {}
            target = f"check/{index}"
            row = fold_command(facts, target, declaration.get("argv"), declaration.get("pipeline"))
            if isinstance(row["pipeline"], list) and row["result"] is not None:
                row["result"]["stages"] = [fold_command(facts, f"{target}/stage/{i}", argv)
                                             for i, argv in enumerate(row["pipeline"])]
                row["result"]["pipeline_complete"] = all(row_complete(stage) for stage in row["result"]["stages"])
            value["checks"].append(row)
        value["action"] = fold_command(facts, "action", manifest.get("action"))
    value["action_refused"] = not allowed
    causes.extend(value["journal_errors"])
    value["success"] = (value["complete"] and requested_success and not causes and isinstance(manifest, dict)
                        and value["before"] is not None and value["before"] == value["after_checks"] and boundaries_match(value)
                        and len(value["checks"]) == len(manifest["checks"])
                        and all(passed(row, declaration.get("expected_exit", 0)) for row, declaration in
                                zip(value["checks"], manifest["checks"], strict=True))
                        and passed(value["action"], 0))
    value["cause"] = "; ".join(dict.fromkeys(causes)) if causes else None if value["success"] else "run did not complete"
    return value


def validate_fold(value):
    folded = fold_receipt(value["journal"])
    require(encode_json(value, sort_keys=True) == encode_json(folded, sort_keys=True), "receipt bypassed journal fold")
    return folded



def pipeline_worker(request, response):
    """Capture, stop and reap every started stage, including partial setup."""
    request_value = parse_json(read_regular(request)[0])
    stages, target = request_value["stages"], request_value["target"]
    deadline = request_value["deadline"]
    journal = FactJournal(request_value["journal"])
    current_stage = target
    report = dict(complete=False, stages=[dict(command=args, code=None, elapsed=None) for args in stages], cause=None)
    for row in report["stages"]:
        row.update(started=False, started_at=None, output_truncated=False, capture_error=None,
                   streams={key: dict(eof=False, cause=None) for key in ("stdout", "stderr")})
    processes, threads, spools, pending_pumps = [], [], [], []
    stopping = threading.Event()

    def fail(cause, stage_target):
        if report["cause"] is None:
            report["cause"] = cause
        observe(journal, "error", stage_target, cause=cause)
        if stage_target != target:
            observe(journal, "error", target, cause=cause)

    def collect_exits():
        for index, process in enumerate(processes):
            row = report["stages"][index]
            if row["code"] is None and process.poll() is not None:
                row.update(code=process.returncode, elapsed=time.monotonic() - row["started_at"])
                try:
                    journal.append("exit", f"{target}/stage/{index}", code=process.returncode)
                except (OSError, ValueError) as error:
                    journal.note_failure(failure_cause(error))
                observe(journal, "reap", f"{target}/stage/{index}", reaped=True)

    def pump(transport, destination, spool, row, channel, stage_target):
        count = 0
        try:
            os.set_blocking(transport.fileno(), False)
            if destination is not None:
                os.set_blocking(destination.fileno(), False)
            while True:
                try:
                    chunk = os.read(transport.fileno(), 65536)
                except BlockingIOError:
                    if stopping.is_set():
                        raise OSError("capture ended before EOF during pipeline cleanup")
                    stopping.wait(0.01)
                    continue
                if not chunk:
                    row["streams"][channel]["eof"] = True
                    observe(journal, "eof", stage_target, channel=channel)
                    break
                room = OUTPUT_LIMIT - count
                if chunk[:room]:
                    observe(journal, "bytes", stage_target, channel=channel, offset=count,
                            base64=base64.b64encode(chunk[:room]).decode("ascii"))
                require(os.write(spool.fileno(), chunk[:room]) == min(room, len(chunk)), "short capture write")
                count += min(room, len(chunk))
                if len(chunk) > room:
                    row["output_truncated"] = True
                    row["streams"][channel]["cause"] = "capture truncated"
                    observe(journal, "flags", stage_target, output_truncated=True)
                    break
                if destination is not None:
                    pending = memoryview(chunk)
                    while pending:
                        try:
                            written = os.write(destination.fileno(), pending)
                            require(written > 0, "pipeline forwarding made no progress")
                        except BlockingIOError:
                            if stopping.is_set():
                                if destination is not sys.stdout.buffer:
                                    destination.close()
                                destination = None
                                break
                            stopping.wait(0.01)
                            continue
                        except BrokenPipeError:
                            if destination is not sys.stdout.buffer:
                                destination.close()
                            destination = None
                            break
                        pending = pending[written:]
        except (OSError, ValueError) as error:
            row["capture_error"] = failure_cause(error)
            row["streams"][channel]["cause"] = row["capture_error"]
            observe(journal, "capture-error", stage_target, channel=channel, cause=row["capture_error"])
        finally:
            transport.close()
            if destination is not None and destination is not sys.stdout.buffer:
                destination.close()
            try:
                spool.flush()
            except (OSError, ValueError) as error:
                row["capture_error"] = failure_cause(error)
                row["streams"][channel]["cause"] = row["capture_error"]
                observe(journal, "capture-error", stage_target, channel=channel, cause=row["capture_error"])

    def cleanup_started():
        collect_exits()
        for requested_signal, grace in ((signal.SIGTERM, 0.2), (signal.SIGKILL, 0.5)):
            for index, process in enumerate(processes):
                if process.returncode is None:
                    observe(journal, "flags", f"{target}/stage/{index}", termination_requested=True)
                    try:
                        process.send_signal(requested_signal)
                    except OSError as error:
                        fail(failure_cause(error), f"{target}/stage/{index}")
            until = time.monotonic() + grace
            while True:
                collect_exits()
                if all(p.returncode is not None for p in processes) or time.monotonic() >= until:
                    break
                time.sleep(0.01)
        stopping.set()
        for transport, _, spool, row, channel, stage_target in pending_pumps:
            pump(transport, None, spool, row, channel, stage_target)
        until = time.monotonic() + 0.3
        for thread, index, channel in threads:
            thread.join(max(0, until - time.monotonic()))
            if thread.is_alive():
                cause = "capture thread did not finish during pipeline cleanup"
                report["stages"][index]["capture_error"] = cause
                observe(journal, "capture-error", f"{target}/stage/{index}", channel=channel, cause=cause)
        unjoined = any(thread.is_alive() for thread, _, _ in threads)
        for index, process in enumerate(processes):
            if process.stdin is not None and not unjoined:
                process.stdin.close()
            remaining = [] if process.returncode is not None else [process.pid]
            cause = None if not remaining else "pipeline stage did not reap during bounded cleanup"
            observe(journal, "cleanup", f"{target}/stage/{index}", remaining_pids=remaining, cause=cause)
            observe(journal, "reap", f"{target}/stage/{index}", reaped=not remaining)
            if cause:
                fail(cause, f"{target}/stage/{index}")
        return unjoined

    with ExitStack() as stack:
        try:
            try:
                write_json(response, report)
                for index, row in enumerate(report["stages"]):
                    current_stage = f"{target}/stage/{index}"
                    streams = {}
                    for channel in ("stdout", "stderr"):
                        path = response.parent / f"stage-{index}-{channel}"
                        stream, _, _, _ = stack.enter_context(regular_file(path, reserve=True))
                        streams[channel] = (stream, path)
                    spools.append(streams)
                    if time.monotonic() >= deadline:
                        raise subprocess.TimeoutExpired(row["command"], 0)
                    journal.append("command", current_stage, argv=row["command"])
                    processes.append(subprocess.Popen(row["command"], stdin=subprocess.PIPE if index else subprocess.DEVNULL,
                                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0))
                    row.update(started=True, started_at=time.monotonic())
                    journal.append("started", current_stage, pgid=os.getpgrp(), pid=processes[-1].pid)
                    write_json(response, report)
            except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
                fail(failure_cause(error), current_stage)

            for index, process in enumerate(processes):
                row, streams = report["stages"][index], spools[index]
                next_input = processes[index + 1].stdin if index + 1 < len(processes) else (
                    sys.stdout.buffer if len(processes) == len(stages) and report["cause"] is None else None)
                for transport, destination, channel in ((process.stdout, next_input, "stdout"),
                                                         (process.stderr, None, "stderr")):
                    pending_pumps.append((transport, destination, streams[channel][0], row, channel, f"{target}/stage/{index}"))
            while pending_pumps:
                args = pending_pumps[0]
                index, channel = int(args[-1].rsplit("/", 1)[-1]), args[-2]
                thread = threading.Thread(target=pump, args=args, daemon=True)
                thread.start()
                threads.append((thread, index, channel))
                pending_pumps.pop(0)
            checkpoint = None
            while True:
                collect_exits()
                current = encode_json(report, sort_keys=True)
                if current != checkpoint:
                    write_json(response, report)
                    checkpoint = current
                if report["cause"] is not None or any(row["output_truncated"] or row["capture_error"] for row in report["stages"]):
                    break
                if all(row["code"] is not None for row in report["stages"]) and not any(t.is_alive() for t, _, _ in threads):
                    report["complete"] = True
                    break
                if time.monotonic() >= deadline:
                    fail("pipeline execution deadline expired", target)
                    break
                time.sleep(0.01)
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
            fail(failure_cause(error), target)
        finally:
            if time.monotonic() >= deadline:
                observe(journal, "flags", target, timed_out=True)
                for index, process in enumerate(processes):
                    if process.returncode is None:
                        observe(journal, "flags", f"{target}/stage/{index}", timed_out=True)
            unjoined = cleanup_started()
            write_json(response, report)
            if unjoined:
                # Exit before closing descriptors still owned by capture threads.
                os._exit(1)
    return 0 if report["complete"] and all(row["code"] == 0 for row in report["stages"]) else 1


def validate_worker_response(report, stages):
    require(isinstance(report, dict) and type(report.get("complete")) is bool and report["complete"],
            "incomplete worker response")
    require(isinstance(report.get("stages"), list) and len(report["stages"]) == len(stages), "missing worker stage metadata")
    for raw, args in zip(report["stages"], stages, strict=True):
        require(isinstance(raw, dict) and raw["command"] == args and type(raw["started"]) is bool,
                "invalid worker start metadata")
        require(raw["code"] is None or type(raw["code"]) is int, "invalid worker exit metadata")
        require(valid_duration(raw["elapsed"]) and (raw["code"] is None or raw["elapsed"] is not None),
                "missing worker duration")
        for channel in ("stdout", "stderr"):
            facts = raw["streams"][channel]
            require(type(facts["eof"]) is bool and (facts["cause"] is None or isinstance(facts["cause"], str)),
                    "invalid worker stream metadata")


def pipeline_command(stages, root, timeout, *, journal=None, target=None):
    journal = journal or ACTIVE_JOURNAL.get()
    require(journal is not None and target is not None, "pipeline requires a fact journal")
    with tempfile.TemporaryDirectory(prefix="checked-gate-pipeline-") as work:
        request, response = Path(work) / "request.json", Path(work) / "response.json"
        write_json(request, dict(stages=stages, journal=str(journal.path), target=target, deadline=time.monotonic() + timeout))
        command([sys.executable, str(Path(__file__).resolve()), "pipeline-worker", str(request), str(response)],
                root, timeout + 2, journal=journal, target=target)
        try:
            report = parse_json(read_regular(response)[0])
            validate_worker_response(report, stages)
            if report.get("cause"):
                journal.append("error", target, cause=report["cause"])
        except (OSError, ValueError, KeyError, TypeError) as error:
            journal.append("error", target, cause=failure_cause(error))
        snapshot = journal.facts()
        supervisor = fold_command(snapshot, target, None)
        for index, args in enumerate(stages):
            stage_target = f"{target}/stage/{index}"
            stage = fold_command(snapshot, stage_target, args)
            if supervisor["result"] is not None:
                group = supervisor["result"]
                journal.append("cleanup", stage_target, remaining_pids=group["remaining_pids"], cause=group["cleanup_error"])
                journal.append("flags", stage_target, termination_requested=group["termination_requested"],
                               timed_out=group["timed_out"] and not stage["exit_observed"])
            if stage["started"] is not True:
                continue
            for channel in ("stdout", "stderr"):
                try:
                    data, _ = read_regular(Path(work) / f"stage-{index}-{channel}")
                    journal.append("loaded", stage_target, channel=channel, size=len(data), sha256=digest(data))
                except (OSError, ValueError) as error:
                    journal.append("capture-error", stage_target, channel=channel, cause=failure_cause(error))
        return fold_command(journal.facts(), target, None)["result"]


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] != "pipeline-worker":
        print("Internal pipeline worker arguments required", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(pipeline_worker(Path(sys.argv[2]), Path(sys.argv[3])))
