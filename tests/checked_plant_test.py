"""Behavior and restart checks for the bundled plant runner, run by Scrut."""

import contextlib
import ast
import copy
import difflib
import importlib.machinery
import importlib.util
import io
import json
import os
import signal
import stat
import time
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


sys.dont_write_bytecode = True
RUNNER = Path(os.environ["CHECKED_PLANT_BIN"])
DETACHED = Path(os.environ["CHECKED_PLANT_DETACHED_BIN"])
sys.path.insert(0, str(RUNNER.parent))
import checked_core as core
CORE = Path(core.__file__)
GATE = RUNNER.with_name("checked-gate")
loader = importlib.machinery.SourceFileLoader("checked_plant", str(RUNNER))
spec = importlib.util.spec_from_loader(loader.name, loader)
runner = importlib.util.module_from_spec(spec)
loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="checked-plant-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.subject = self.root / "subject.txt"
        self.subject.write_text("valid\n")
        (self.root / "check.sh").write_text(
            '#!/usr/bin/env bash\nset -euo pipefail\n'
            'if [[ "$(cat subject.txt)" == valid ]]; then\n'
            '  echo "one check ran: OK"\nelse\n'
            '  echo "one check ran: ASSERT subject valid" >&2\n  exit 1\nfi\n'
        )
        (self.root / "setup.sh").write_text('test -f subject.txt\n')
        self.patch = self.root / "invalid.patch"
        self.patch.write_text(self.patch_for("subject.txt", "valid\n", "wrong\n"))
        self.manifest = dict(
            inputs=["subject.txt", "check.sh", "setup.sh", "invalid.patch"],
            check="check.sh", setup="setup.sh", timeout=10,
            green=dict(exit_code=0, contains=["one check ran: OK"], excludes=["SKIP", "ERROR"]),
            variants=[dict(name="subject-valid", patch="invalid.patch",
                           red=dict(exit_code=1, contains=["one check ran: ASSERT subject valid"], excludes=["ERROR", "SKIP"]))],
        )
        self.path = self.root / "plants.json"
        self.ledger = self.root / "ledger.md"
        self.status = self.root / "status.md"
        self.ledger.write_text("# Existing ledger\n")
        self.status.write_text("existing status\n")
        self.count = 0

    @staticmethod
    def patch_for(name, before, after):
        return "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                            fromfile="a/" + name, tofile="b/" + name))

    def execute(self):
        self.path.write_text(json.dumps(self.manifest))
        self.count += 1
        self.out = self.root / f"run-{self.count}"
        with contextlib.redirect_stdout(io.StringIO()):
            self.code = runner.run(self.path, self.out)
        self.result = json.loads((self.out / "results.json").read_text())
        return self.result

    def render(self, value=None):
        if value is not None:
            (self.out / "results.json").write_text(json.dumps(value))
        with contextlib.redirect_stdout(io.StringIO()):
            return runner.render(self.out / "results.json", self.ledger, self.status)

    def refused(self, value=None):
        before = (self.ledger.read_bytes(), self.status.read_bytes())
        with self.assertRaises((ValueError, KeyError, TypeError)) as refused:
            self.render(value)
        self.assertEqual(before, (self.ledger.read_bytes(), self.status.read_bytes()))
        return str(refused.exception)

    def test_real_plants_red_restore_green(self):
        second = copy.deepcopy(self.manifest["variants"][0])
        second["name"] = "second-assertion"
        self.manifest["variants"].append(second)
        result = self.execute()
        self.assertEqual(self.code, 0)
        self.assertTrue(result["success"])
        self.assertEqual([r["status"] for r in result["results"]], ["red", "red"])
        for row in result["results"]:
            self.assertEqual([row[p]["exit_code"] for p in ("baseline", "red", "green")], [0, 1, 0])
            self.assertTrue(row["restored"] and row["green_passed"])
        self.assertEqual(self.subject.read_text(), "valid\n")
        self.assertEqual(set(result["inputs"]), {"manifest", "runner", *self.manifest["inputs"]})
        self.assertEqual(self.render(), 0)
        self.assertIn("subject-valid: named assertion reached; red exit 1; restored; green exit 0.", self.ledger.read_text())
        self.assertIn("Verification from JSON:", self.status.read_text())
        self.render()
        self.assertEqual(self.ledger.read_text().count(runner.BEGIN), 1)

    def test_broken_variant_blocks_records_and_marks_unrun(self):
        self.patch.write_text("not a patch\n")
        self.manifest["variants"].append(dict(self.manifest["variants"][0], name="never-ran"))
        result = self.execute()
        self.assertEqual(self.code, 1)
        self.assertEqual([r["status"] for r in result["results"]], ["setup-error", "unrun"])
        self.assertIn("step failed", result["results"][0]["reason"])
        self.assertFalse(result["success"])
        self.refused()

    def test_strict_setup_and_cause(self):
        for source in ('false\necho "unchecked success"\n', 'false | true\necho "unchecked success"\n', 'echo "${MISSING_PLANT_VARIABLE:?missing}"\n'):
            with self.subTest(source=source):
                (self.root / "setup.sh").write_text(source)
                result = self.execute()
                row = result["results"][0]
                self.assertEqual(self.code, 1)
                self.assertEqual(row["status"], "setup-error")
                self.assertIn("baseline setup failed", row["reason"])
                self.assertIn("restore:", row["reason"])
                self.assertNotIn("unchecked success", row["baseline_setup"]["stdout"])
                self.refused()

    def test_missing_input_fingerprints_and_outcome(self):
        self.subject.unlink()
        result = self.execute()
        self.assertEqual(self.code, 1)
        self.assertIsNone(result["inputs"]["subject.txt"])
        self.assertEqual(set(result["inputs"]), {"manifest", "runner", *self.manifest["inputs"]})
        self.assertEqual(result["results"][0]["status"], "setup-error")
        self.assertIn("missing/unreadable input subject.txt", result["reason"])
        self.refused()

    def test_unexpected_pass_and_unrelated_error_are_failures(self):
        for after in ('echo "one check ran: OK"\n', 'echo "ERROR unrelated" >&2\nexit 1\n'):
            with self.subTest(after=after):
                self.patch.write_text(self.patch_for("check.sh", (self.root / "check.sh").read_text(), after))
                result = self.execute()
                self.assertEqual(self.code, 1)
                self.assertEqual(result["results"][0]["status"], "setup-error")
                self.assertIn("named assertion", result["results"][0]["reason"])
                self.refused()

    def test_failed_restore_preserves_original_failure(self):
        original = runner.materialize
        calls = 0

        def fail_restore(*args):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("restore cause retained")
            return original(*args)

        self.patch.write_text("broken patch\n")
        with mock.patch.object(runner, "materialize", side_effect=fail_restore):
            result = self.execute()
        row = result["results"][0]
        self.assertEqual(self.code, 1)
        self.assertIn("step failed", row["reason"])
        self.assertIn("restore cause retained", row["reason"])
        self.assertEqual(row["status"], "setup-error")
        self.refused()

    def test_restored_check_error_preserves_cause(self):
        original = runner.check

        def fail_green(root, manifest, row, phase):
            if phase == "green":
                raise OSError("restored check cause")
            return original(root, manifest, row, phase)

        with mock.patch.object(runner, "check", side_effect=fail_green):
            result = self.execute()
        self.assertEqual(self.code, 1)
        self.assertIn("restored check cause", result["results"][0]["reason"])
        self.refused()

    def test_render_rejects_incomplete_or_failed_rows(self):
        good = self.execute()
        for key in ("complete", "success", "inputs_unchanged"):
            bad = copy.deepcopy(good)
            bad[key] = False
            self.refused(bad)
        for key, replacement in (("status", "unrun"), ("restored", False), ("green_passed", False)):
            bad = copy.deepcopy(good)
            bad["results"][0][key] = replacement
            self.refused(bad)
        for phase in ("baseline", "red", "green", "red_setup"):
            bad = copy.deepcopy(good)
            del bad["results"][0][phase]
            self.refused(bad)
        for phase in ("baseline", "red", "green", "baseline_setup", "red_setup", "green_setup"):
            for flag, corrupt in (("timed_out", True), ("reaped", False), ("output_truncated", True),
                                  ("capture_error", "capture failure"), ("remaining_pids", [123]),
                                  ("cleanup_error", "cleanup failure")):
                with self.subTest(phase=phase, flag=flag):
                    bad = copy.deepcopy(good)
                    bad["results"][0][phase][flag] = corrupt
                    self.refused(bad)
                    del bad["results"][0][phase][flag]
                    self.refused(bad)
            if phase.endswith("_setup"):
                bad = copy.deepcopy(good)
                bad["results"][0][phase]["exit_code"] = 2
                self.refused(bad)
        bad = copy.deepcopy(good)
        bad["results"] = []
        self.refused(bad)
        bad = copy.deepcopy(good)
        bad["results"][0]["red"]["stdout"] = "SKIP"
        bad["results"][0]["red"]["stderr"] = ""
        self.refused(bad)

    def test_stale_inputs_refused(self):
        self.execute()
        for name in self.manifest["inputs"] + ["plants.json"]:
            with self.subTest(name=name):
                path = self.root / name
                before = path.read_bytes()
                path.write_bytes(before + b"\n")
                self.refused()
                path.write_bytes(before)

    def test_input_change_during_run_fails(self):
        original = runner.run_variant

        def mutate(*args):
            original(*args)
            self.subject.write_text("concurrent edit\n")

        with mock.patch.object(runner, "run_variant", side_effect=mutate):
            result = self.execute()
        self.assertEqual(self.code, 1)
        self.assertFalse(result["inputs_unchanged"])
        self.assertIn("inputs changed", result["reason"])
        self.refused()

    def test_cli_missing_manifest_writes_failed_json(self):
        proc = subprocess.run([sys.executable, str(RUNNER), "run", str(self.path), str(self.root / "missing")],
                              text=True, capture_output=True, timeout=5)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        value = json.loads((self.root / "missing/results.json").read_text())
        self.assertTrue(value["complete"])
        self.assertFalse(value["success"])
        self.assertIn("FileNotFoundError", value["reason"])

    def test_external_read_paths_are_centralized(self):
        allowed = {
            "os.read(key.fd, 65536)": 1,
            "os.read(transport.fileno(), 65536)": 1,
            "(Path(cache) / 'stdout').open('w+b')": 1,
            "(Path(cache) / 'stderr').open('w+b')": 1,
            "stream.read(OUTPUT_LIMIT + 1)": 1,
        }
        observed = {}
        for path in (RUNNER, CORE, GATE):
            tree = ast.parse(path.read_text())
            parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
            functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
                if name not in {"open", "fdopen", "read", "read_text", "read_bytes", "readline", "readlines", "pread"}:
                    continue
                function = parents.get(node)
                while function is not None and not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    function = parents.get(function)
                if path == CORE and function is not None and function is functions.get("regular_file"):
                    continue
                call = ast.unparse(node)
                if call == "os.read(transport.fileno(), 65536)":
                    self.assertEqual(path, CORE)
                    self.assertEqual(function.name, "pump")
                elif call == "stream.read(OUTPUT_LIMIT + 1)":
                    self.assertEqual(path, CORE)
                    self.assertIs(function, functions.get("read_spool"), "owned spool reader bypass: " + call)
                else:
                    self.assertIs(function, functions.get("command"), "external reader bypass: " + call)
                self.assertIn(call, allowed, "external reader bypass: " + call)
                observed[call] = observed.get(call, 0) + 1
        self.assertEqual(observed, allowed)

    def test_unsupported_manifests_write_failed_json(self):
        for kind in ("fifo", "directory", "symlink"):
            with self.subTest(kind=kind):
                path = self.root / (kind + ".json")
                if kind == "fifo":
                    os.mkfifo(path)
                elif kind == "directory":
                    path.mkdir()
                else:
                    target = self.root / "target.json"
                    target.write_text(json.dumps(self.manifest))
                    path.symlink_to(target)
                out = self.root / (kind + "-run")
                try:
                    proc = subprocess.run([sys.executable, str(RUNNER), "run", str(path), str(out)],
                                          text=True, capture_output=True, timeout=3)
                except subprocess.TimeoutExpired:
                    self.fail("manifest reader waited on unsupported input")
                self.assertEqual(proc.returncode, 1, proc.stderr)
                value = json.loads((out / "results.json").read_text())
                self.assertTrue(value["complete"])
                self.assertFalse(value["success"])
                self.assertIn("unsupported" if kind == "symlink" else "regular file", value["reason"])

    def test_stale_render_fifo_refuses_without_records(self):
        self.execute()
        if self.code != 0:
            raise RuntimeError("stale-render baseline failed")
        result = self.out / "results.json"
        for path in (self.path, result, self.ledger, self.status):
            with self.subTest(path=path.name):
                saved = path.read_bytes()
                path.unlink()
                os.mkfifo(path)
                try:
                    try:
                        proc = subprocess.run([sys.executable, str(RUNNER), "render", str(result),
                                               "--ledger", str(self.ledger), "--status", str(self.status)],
                                              text=True, capture_output=True, timeout=3)
                    except subprocess.TimeoutExpired:
                        self.fail("render reader waited on unsupported input")
                    self.assertEqual(proc.returncode, 1, proc.stderr)
                    self.assertIn("regular file", proc.stderr)
                    self.assertTrue(stat.S_ISFIFO(path.stat().st_mode))
                finally:
                    path.unlink()
                    path.write_bytes(saved)

    def test_parsed_manifest_bytes_match_fingerprint(self):
        original = runner.load_manifest

        def change(path):
            value = original(path)
            path.write_text(path.read_text() + "\n")
            return value

        with mock.patch.object(runner, "load_manifest", side_effect=change):
            value = self.execute()
        self.assertEqual(self.code, 1)
        self.assertIn("manifest changed after parsing", value["reason"])
        self.refused()

    def test_bytecode_isolation_each_phase(self):
        prefixes = []
        for _ in range(3):
            result = core.command([sys.executable, "-c",
                                     "import os; print(os.environ['PYTHONPYCACHEPREFIX']); "
                                     "print(os.environ['PYTHONDONTWRITEBYTECODE'])"], self.root, 5)
            self.assertEqual(result["exit_code"], 0, result["stderr"])
            prefix, disabled = result["stdout"].splitlines()
            prefixes.append(prefix)
            self.assertEqual(disabled, "1")
        self.assertEqual(len(set(prefixes)), 3)

    def test_normally_exiting_step_stops_its_group(self):
        child_file = self.root / "child.pid"
        result = core.command(["bash", "-c", 'sleep 60 >/dev/null 2>&1 & echo $! > child.pid; echo marker'],
                                self.root, 3)
        child = int(child_file.read_text())
        listing = subprocess.run(["ps", "-o", "stat=", "-p", str(child)], capture_output=True, text=True, timeout=2)
        alive = listing.returncode == 0 and not listing.stdout.strip().startswith("Z")
        try:
            self.assertFalse(alive, "same-group background child survived")
            self.assertEqual(result["exit_code"], 0, result)
            self.assertEqual(result["remaining_pids"], [])
            self.assertIsNone(result["cleanup_error"])
            self.assertTrue(result["reaped"])
        finally:
            if alive:
                os.kill(child, signal.SIGKILL)

    def test_term_ignoring_group_is_stopped(self):
        script = ('bash -c \'trap "" TERM; echo $$ > child.pid; exec sleep 60\' >/dev/null 2>&1 &\n'
                  'while [[ ! -s child.pid ]]; do sleep 0.01; done\necho marker\n')
        result = core.command(["bash", "-c", script], self.root, 3)
        child = int((self.root / "child.pid").read_text())
        listing = subprocess.run(["ps", "-o", "stat=", "-p", str(child)], capture_output=True, text=True, timeout=2)
        alive = listing.returncode == 0 and not listing.stdout.strip().startswith("Z")
        try:
            self.assertFalse(alive, "TERM-ignoring same-group child survived")
            self.assertEqual(result["exit_code"], 0, result)
            self.assertIn("marker", result["stdout"])
            self.assertEqual(result["remaining_pids"], [])
            self.assertIsNone(result["cleanup_error"])
            self.assertTrue(result["reaped"])
        finally:
            if alive:
                os.kill(child, signal.SIGKILL)

    def test_unnormalized_inputs_refuse_before_materialization(self):
        outside = tempfile.TemporaryDirectory(prefix="checked-plant-outside-", dir=self.root.parent)
        self.addCleanup(outside.cleanup)
        sibling = Path(outside.name) / "source.txt"
        sibling.write_text("outside source\n")
        original = copy.deepcopy(self.manifest)
        for name in (str(self.subject), "../" + sibling.parent.name + "/source.txt"):
            with self.subTest(name=name):
                self.manifest = copy.deepcopy(original)
                self.manifest["inputs"].append(name)
                before = self.subject.read_bytes(), sibling.read_bytes()
                with mock.patch.object(runner, "materialize") as materialize:
                    value = self.execute()
                self.assertEqual(self.code, 1)
                self.assertTrue(value["complete"])
                self.assertFalse(value["success"])
                self.assertIn("normalized relative paths", value["reason"])
                materialize.assert_not_called()
                self.assertEqual((self.subject.read_bytes(), sibling.read_bytes()), before)
                self.refused()

    def test_unsupported_runtime_refuses_before_spawn(self):
        with mock.patch.object(core.os, "waitid", None), mock.patch.object(
                core.subprocess, "Popen", side_effect=AssertionError("unsupported runtime reached spawn")) as spawn:
            with self.assertRaisesRegex(ValueError, "waitid and WNOWAIT"):
                core.command(["bash", "-c", "echo marker"], self.root, 1)
            spawn.assert_not_called()

    def test_failure_recording_is_centralized(self):
        for path in (RUNNER, CORE, GATE):
            tree = ast.parse(path.read_text())
            parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
            for handler in ast.walk(tree):
                if not isinstance(handler, ast.ExceptHandler) or not handler.name:
                    continue
                for node in ast.walk(handler):
                    if not isinstance(node, ast.Name) or node.id != handler.name or not isinstance(node.ctx, ast.Load):
                        continue
                    parent = parents[node]
                    if isinstance(parent, ast.Raise) and parent.cause is node:
                        continue
                    self.assertIsInstance(parent, ast.Call, "cause recording bypasses shared formatter")
                    self.assertIsInstance(parent.func, ast.Name)
                    self.assertIn(parent.func.id, ("failure_cause", "isinstance"))

    def test_inspection_failure_retains_subprocess_diagnostics(self):
        for failure in (subprocess.CalledProcessError(2, ["ps"], output="inspection stdout", stderr="inspection denied"),
                        subprocess.TimeoutExpired(["ps"], 0.25, output=b"inspection stdout", stderr=b"inspection timed out")):
            with self.subTest(failure=type(failure).__name__):
                with mock.patch.object(core, "live_group", side_effect=failure), mock.patch.object(core, "terminate_group"):
                    remaining, cause = core.stop_group(123)
                self.assertIsNone(remaining)
                self.assertIn(type(failure).__name__, cause)
                self.assertIn("inspection stdout", cause)
                self.assertIn("inspection denied" if isinstance(failure, subprocess.CalledProcessError)
                              else "inspection timed out", cause)
        huge = core.failure_cause(subprocess.CalledProcessError(2, ["ps"], stderr="x" * (core.OUTPUT_LIMIT + 1)))
        self.assertNotIn("x" * (core.OUTPUT_LIMIT + 1), huge)

    def test_closed_stdio_parent_timeout_writes_failure(self):
        parents = self.root / "parents"
        (self.root / "setup.sh").write_text('echo $$ >> "${CHECKED_PLANT_PARENT_PIDS}"\nexec >/dev/null 2>&1\nsleep 60\n')
        self.manifest["timeout"] = 0.1
        self.path.write_text(json.dumps(self.manifest))
        self.out = self.root / "closed-stdio-run"
        timed_out = False
        try:
            try:
                proc = subprocess.run([sys.executable, str(RUNNER), "run", str(self.path), str(self.out)],
                                      env=dict(os.environ, CHECKED_PLANT_PARENT_PIDS=str(parents)),
                                      text=True, capture_output=True, timeout=3)
            except subprocess.TimeoutExpired:
                timed_out = True
                self.fail("closed-stdio parent prevented failure JSON")
            self.assertEqual(proc.returncode, 1, proc.stderr)
            self.result = json.loads((self.out / "results.json").read_text())
            self.assertTrue(self.result["complete"])
            row = self.result["results"][0]
            self.assertEqual(row["status"], "setup-error")
            self.assertTrue(row["baseline_setup"]["timed_out"])
            self.assertTrue(row["baseline_setup"]["reaped"])
            self.assertEqual(row["baseline_setup"]["stdout"], "")
            self.assertEqual(row["baseline_setup"]["stderr"], "")
            self.refused()
        finally:
            if timed_out and parents.exists():
                for value in parents.read_text().splitlines():
                    pid = int(value)
                    try:
                        if os.getpgid(pid) == pid:
                            os.killpg(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass

    def test_disappearing_manifest_preserves_cause(self):
        original = runner.load_manifest

        def remove(path):
            value = original(path)
            path.unlink()
            return value

        with mock.patch.object(runner, "load_manifest", side_effect=remove):
            value = self.execute()
        self.assertEqual(self.code, 1)
        self.assertIsNone(value["inputs"]["manifest"])
        self.assertIn("missing/unreadable input manifest", value["reason"])
        self.assertIn(str(self.path), value["reason"])
        self.assertIn("No such file", value["reason"])
        self.refused()

    def test_render_preserves_surrounding_ledger(self):
        self.execute()
        before, after = "# Existing notes\n\nBEFORE sentinel\n", "\nAFTER sentinel\n"
        self.ledger.write_text(before)
        self.assertEqual(self.render(), 0)
        first = self.ledger.read_text()
        self.assertTrue(first.startswith(before))
        self.ledger.write_text(before + runner.BEGIN + "\nold generated section\n" + runner.END + after)
        self.assertEqual(self.render(), 0)
        replaced = self.ledger.read_text()
        self.assertTrue(replaced.startswith(before))
        self.assertTrue(replaced.endswith(after))
        self.assertNotIn("old generated section", replaced)
        self.assertEqual(replaced.count(runner.BEGIN), 1)
        self.assertEqual(self.render(), 0)
        self.assertEqual(self.ledger.read_text(), replaced)

    def test_timeout_is_setup_error(self):
        (self.root / "setup.sh").write_text('echo "timeout stdout"\necho "timeout stderr" >&2\nsleep 10\n')
        self.manifest["timeout"] = 0.05
        result = self.execute()
        self.assertEqual(self.code, 1)
        self.assertEqual(result["results"][0]["status"], "setup-error")
        row = result["results"][0]
        self.assertTrue(row["baseline_setup"]["timed_out"])
        self.assertIn("timeout stdout", row["baseline_setup"]["stdout"])
        self.assertIn("timeout stderr", row["baseline_setup"]["stderr"])
        self.assertLess(row["baseline_setup"]["exit_code"], 0)
        self.refused()

    def test_executable_modes_preserved_and_fingerprinted(self):
        helper = self.root / "helper"
        helper.write_text('#!/usr/bin/env bash\n[[ "$(cat subject.txt)" == valid ]]\n')
        helper.chmod(0o755)
        self.manifest["inputs"].append("helper")
        (self.root / "setup.sh").write_text('./helper || [[ "$(cat subject.txt)" == wrong ]]\n')
        result = self.execute()
        self.assertEqual(self.code, 0, result)
        self.assertEqual(result["inputs"]["helper"]["mode"], 0o755)
        helper.chmod(0o644)
        self.refused()

    def test_hardlinked_destinations_refused(self):
        self.execute()
        for name, target in (("subject-alias", self.subject), ("manifest-alias", self.path),
                             ("result-alias", self.out / "results.json"), ("ledger-alias", self.ledger)):
            alias = self.root / name
            alias.hardlink_to(target)
            before = target.read_bytes()
            with self.assertRaises(ValueError):
                runner.render(self.out / "results.json", self.ledger if target == self.ledger else alias,
                              alias if target == self.ledger else self.status)
            self.assertEqual(target.read_bytes(), before)

    def test_green_controls_are_separate_and_checked(self):
        control = dict(name="ignored-subject", patch="invalid.patch")
        self.manifest["variants"] = []
        self.manifest["controls"] = [control]
        original = (self.root / "check.sh").read_text()
        (self.root / "check.sh").write_text(original.replace('== valid', '!= unrelated'))
        good = self.execute()
        self.assertEqual(self.code, 0, good)
        self.assertEqual(good["results"][0]["kind"], "control")
        self.assertEqual(good["results"][0]["status"], "control-green")
        self.assertNotIn("red", good["results"][0])
        self.assertEqual(self.render(), 0)
        self.assertIn("control ignored-subject: green control verified; control exit 0", self.ledger.read_text())
        bad = copy.deepcopy(good)
        bad["results"][0]["status"] = "red"
        self.refused(bad)
        bad = copy.deepcopy(good)
        bad["results"][0]["control"]["exit_code"] = 1
        self.refused(bad)
        bad = copy.deepcopy(good)
        del bad["results"][0]["control"]
        self.refused(bad)
        (self.root / "check.sh").write_text(original)
        failed = self.execute()
        self.assertEqual(self.code, 1, failed)
        self.assertEqual(failed["results"][0]["status"], "setup-error")
        self.assertEqual(failed["results"][0]["control"]["exit_code"], 1)
        self.refused()

    def test_absent_record_aliases_and_refusal_cleanup(self):
        self.execute()
        upper, lower = self.root / "Records.md", self.root / "records.md"
        # Probe only runner-owned paths to exercise this filesystem's name rules.
        upper.touch()
        aliases = lower.exists()
        upper.unlink()
        if aliases:
            with self.assertRaises(ValueError):
                runner.render(self.out / "results.json", upper, lower)
            self.assertFalse(upper.exists())
            self.assertFalse(lower.exists())
        else:
            self.assertEqual(runner.render(self.out / "results.json", upper, lower), 0)
            self.assertIn(runner.BEGIN, upper.read_text())
            self.assertIn("Verification from JSON:", lower.read_text())
        missing = self.root / "new-record.md"
        self.ledger.write_text("malformed " + runner.BEGIN)
        with self.assertRaises(ValueError):
            runner.render(self.out / "results.json", self.ledger, missing)
        self.assertFalse(missing.exists())
        self.assertEqual(self.ledger.read_text(), "malformed " + runner.BEGIN)

    def test_leading_dash_scripts_execute(self):
        for key in ("setup", "check"):
            old = self.manifest[key]
            new = "-" + old
            (self.root / old).rename(self.root / new)
            self.manifest["inputs"][self.manifest["inputs"].index(old)] = new
            self.manifest[key] = new
        result = self.execute()
        self.assertEqual(self.code, 0, result)
        self.assertEqual(self.render(), 0)

    def test_skipped_unittest_control_refused(self):
        (self.root / "control_test.py").write_text(
            'from pathlib import Path\nimport unittest\n'
            'class Control(unittest.TestCase):\n'
            '    @unittest.skipIf(Path("subject.txt").read_text() != "valid\\n", "SKIP property")\n'
            '    def test_subject(self):\n        self.assertTrue(True)\n'
            'unittest.main()\n'
        )
        self.manifest["inputs"].append("control_test.py")
        (self.root / "check.sh").write_text('uv run --no-project control_test.py -q\n')
        self.manifest["variants"] = []
        self.manifest["controls"] = [dict(name="skipped-property", patch="invalid.patch")]
        self.manifest["green"] = dict(exit_code=0, contains=["Ran 1 test", "\nOK\n"],
                                      excludes=["skipped", "SKIP", "ERROR:"])
        result = self.execute()
        self.assertEqual(self.code, 1, result)
        row = result["results"][0]
        self.assertEqual(row["status"], "setup-error")
        self.assertEqual(row["control"]["exit_code"], 0)
        self.assertIn("OK (skipped=1)", row["control"]["stderr"])
        self.refused()

    def test_detached_stdio_does_not_block_failure_json(self):
        parent_pids, child_pids = self.root / "parents", self.root / "children"
        (self.root / "launcher.py").write_bytes(DETACHED.read_bytes())
        self.manifest["inputs"].append("launcher.py")
        (self.root / "setup.sh").write_text('exec "${CHECKED_PLANT_TEST_PYTHON}" launcher.py\n')
        self.manifest["timeout"] = 0.5
        self.path.write_text(json.dumps(self.manifest))
        out = self.root / "detached-run"
        owned_tmp = self.root / "command-tmp"
        owned_tmp.mkdir()
        env = dict(os.environ, TMPDIR=str(owned_tmp), CHECKED_PLANT_PARENT_PIDS=str(parent_pids),
                   CHECKED_PLANT_CHILD_PIDS=str(child_pids), CHECKED_PLANT_TEST_PYTHON=sys.executable)
        try:
            try:
                proc = subprocess.run([sys.executable, str(RUNNER), "run", str(self.path), str(out)],
                                      env=env, text=True, capture_output=True, timeout=5)
            except subprocess.TimeoutExpired:
                self.fail("detached stdio prevented bounded failure reporting")
            self.assertEqual(proc.returncode, 1, proc.stderr)
            result = json.loads((out / "results.json").read_text())
            self.assertTrue(result["complete"])
            self.assertFalse(result["success"])
            row = result["results"][0]
            self.assertEqual(row["status"], "setup-error")
            self.assertTrue(row["baseline_setup"]["timed_out"])
            self.assertTrue(row["baseline_setup"]["terminated"])
            self.assertTrue(row["baseline_setup"]["reaped"])
            self.assertIn("detached stdout", row["baseline_setup"]["stdout"])
            self.assertIn("detached stderr", row["baseline_setup"]["stderr"])
            with self.assertRaises(ValueError):
                runner.render(out / "results.json", self.ledger, self.status)
        finally:
            for path in (parent_pids, child_pids):
                if path.exists():
                    for value in path.read_text().splitlines():
                        try:
                            os.kill(int(value), signal.SIGTERM)
                        except ProcessLookupError:
                            pass
            if child_pids.exists():
                for value in child_pids.read_text().splitlines():
                    stopped = self.root / (value + ".stopped")
                    deadline = time.monotonic() + 3
                    while not stopped.exists() and time.monotonic() < deadline:
                        time.sleep(0.01)
                    self.assertTrue(stopped.exists(), "recorded detached child did not stop")

    def test_truncated_output_cannot_pass(self):
        (self.root / "setup.sh").write_text(
            '"${CHECKED_PLANT_TEST_PYTHON}" -c \'print("x" * (2 * 1024 * 1024))\'\n')
        with mock.patch.dict(os.environ, CHECKED_PLANT_TEST_PYTHON=sys.executable):
            result = self.execute()
        self.assertEqual(self.code, 1)
        step = result["results"][0]["baseline_setup"]
        self.assertTrue(step["output_truncated"])
        self.assertLessEqual(len(step["stdout"]), core.OUTPUT_LIMIT)
        self.refused()

    def test_invalid_manifests_refuse_records(self):
        original = copy.deepcopy(self.manifest)
        for case, reason in (("empty", "declare at least one"), ("zero-red", "invalid expected check exit"),
                             ("no-assertion", "require named assertion")):
            with self.subTest(case=case):
                self.manifest = copy.deepcopy(original)
                if case == "empty":
                    self.manifest["variants"] = []
                elif case == "zero-red":
                    self.manifest["variants"][0]["red"]["exit_code"] = 0
                else:
                    self.manifest["variants"][0]["red"]["contains"] = []
                result = self.execute()
                self.assertEqual(self.code, 1)
                self.assertTrue(result["complete"])
                self.assertFalse(result["success"])
                self.assertIn(reason, result["reason"])
                self.refused()

    def test_recheck_io_causes_preserved(self):
        original = runner.run_variant
        def remove_input(*args):
            original(*args)
            self.subject.unlink()
        with mock.patch.object(runner, "run_variant", side_effect=remove_input):
            result = self.execute()
        self.assertEqual(self.code, 1)
        self.assertIn("missing/unreadable input subject.txt", result["reason"])
        self.assertIn("No such file", result["reason"])
        self.subject.write_text("valid\n")
        self.execute()
        self.subject.unlink()
        reason = self.refused()
        self.assertIn("missing/unreadable input subject.txt", reason)
        self.assertIn("No such file", reason)

    def test_private_patches_ignore_ancestor_git_context(self):
        checkout = self.root / "checkout"
        subprocess.run(["git", "init", "-q", str(checkout)], check=True, capture_output=True)
        private_tmp = checkout / "tmp:area"
        private_tmp.mkdir()
        check = 'echo "observed $(cat subject.txt)"\n' + (self.root / "check.sh").read_text()
        (self.root / "check.sh").write_text(check)
        self.patch.write_text(self.patch_for("subject.txt", "valid\n", "ignored\n")
                              + self.patch_for("check.sh", check, check.replace("== valid", "== ignored")))
        self.manifest["variants"] = []
        self.manifest["controls"] = [dict(name="private-git-control", patch="invalid.patch")]
        with mock.patch.object(runner.tempfile, "tempdir", str(private_tmp)), mock.patch.dict(
                os.environ, TMPDIR=str(private_tmp), GIT_DIR=str(checkout / ".git"),
                GIT_WORK_TREE=str(checkout), GIT_INDEX_FILE=str(checkout / "external-index")):
            result = self.execute()
        self.assertEqual(self.code, 0, result)
        self.assertIn("observed ignored", result["results"][0]["control"]["stdout"])
        self.assertEqual(self.render(), 0)

    def test_continuous_output_keeps_spools_bounded(self):
        (self.root / "writer.py").write_text(
            'import os, time\nfor _ in range(32):\n    os.write(1, b"x" * 65536)\n'
            '    time.sleep(0.005)\ntime.sleep(10)\n')
        self.manifest["inputs"].append("writer.py")
        (self.root / "setup.sh").write_text('exec "${CHECKED_PLANT_TEST_PYTHON}" writer.py\n')
        self.manifest["timeout"] = 0.5
        factory, stored = runner.tempfile.TemporaryDirectory, []
        @contextlib.contextmanager
        def measured(*args, **kwargs):
            with factory(*args, **kwargs) as folder:
                try:
                    yield folder
                finally:
                    for name in ("stdout", "stderr"):
                        path = Path(folder) / name
                        if path.is_file():
                            stored.append(path.stat().st_size)
        with mock.patch.object(runner.tempfile, "TemporaryDirectory", measured), mock.patch.dict(
                os.environ, CHECKED_PLANT_TEST_PYTHON=sys.executable):
            result = self.execute()
        self.assertEqual(self.code, 1)
        self.assertTrue(stored)
        self.assertLessEqual(max(stored), core.OUTPUT_LIMIT)
        self.assertEqual(max(stored), core.OUTPUT_LIMIT)
        self.assertTrue(result["results"][0]["baseline_setup"]["output_truncated"])
        self.refused()

    def test_fifo_input_fails_without_waiting(self):
        fifo = self.root / "input.fifo"
        os.mkfifo(fifo, 0o600)
        self.manifest["inputs"].append("input.fifo")
        self.path.write_text(json.dumps(self.manifest))
        self.out = self.root / "fifo-run"
        try:
            proc = subprocess.run([sys.executable, str(RUNNER), "run", str(self.path), str(self.out)],
                                  text=True, capture_output=True, timeout=3)
        except subprocess.TimeoutExpired:
            self.fail("input fingerprinting waited for a FIFO writer")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        result = json.loads((self.out / "results.json").read_text())
        self.assertTrue(result["complete"])
        self.assertFalse(result["success"])
        self.assertIsNone(result["inputs"]["input.fifo"])
        self.assertIn("input must be a regular file", result["reason"])
        self.refused()

    def test_symlink_inputs_are_refused(self):
        (self.root / "alias.txt").symlink_to("subject.txt")
        real = self.root / "real"
        real.mkdir()
        (real / "extra.txt").write_text("extra\n")
        (self.root / "linked").symlink_to("real", target_is_directory=True)
        original = copy.deepcopy(self.manifest)
        for index, name in enumerate(("alias.txt", "linked/extra.txt")):
            with self.subTest(name=name):
                self.manifest = copy.deepcopy(original)
                self.manifest["inputs"].append(name)
                self.path.write_text(json.dumps(self.manifest))
                self.out = self.root / f"link-run-{index}"
                try:
                    proc = subprocess.run([sys.executable, str(RUNNER), "run", str(self.path), str(self.out)],
                                          text=True, capture_output=True, timeout=3)
                except subprocess.TimeoutExpired:
                    self.fail("symlink input did not produce a bounded refusal")
                self.assertEqual(proc.returncode, 1)
                result = json.loads((self.out / "results.json").read_text())
                self.assertTrue(result["complete"])
                self.assertFalse(result["success"])
                self.assertIsNone(result["inputs"][name])
                self.assertIn("symlinked input paths are unsupported", result["reason"])
                self.refused()

    def test_forbidden_output_blocks_records(self):
        original = (self.root / "check.sh").read_text()
        for forbidden in ("ERROR: unrelated", "SKIP unrelated"):
            with self.subTest(forbidden=forbidden):
                (self.root / "check.sh").write_text(original.replace(
                    '  exit 1\n', '  echo "' + forbidden + '" >&2\n  exit 1\n'))
                result = self.execute()
                self.assertEqual(self.code, 1)
                row = result["results"][0]
                self.assertEqual(row["red"]["exit_code"], 1)
                self.assertIn("one check ran: ASSERT subject valid", row["red"]["stderr"])
                self.assertIn(forbidden, row["red"]["stderr"])
                self.refused()
        (self.root / "check.sh").write_text(original)
        good = self.execute()
        self.assertEqual(self.code, 0)
        for phase in ("baseline", "red", "green"):
            for forbidden in ("ERROR: unrelated", "SKIP unrelated"):
                with self.subTest(phase=phase, forbidden=forbidden):
                    bad = copy.deepcopy(good)
                    bad["results"][0][phase]["stderr"] += "\n" + forbidden + "\n"
                    self.refused(bad)

    def test_runner_guards_detect_their_own_plants(self):
        sources = {"candidate": RUNNER.read_text(), "checked_core.py": CORE.read_text(), "checked-gate": GATE.read_text()}
        source = sources["candidate"]
        candidate = self.root / "candidate"
        candidate.write_text(source)
        for name in ("checked_core.py", "checked-gate"):
            (self.root / name).write_text(sources[name])
        (self.root / "regressions.py").write_bytes(Path(__file__).read_bytes())
        (self.root / "detached.py").write_bytes(DETACHED.read_bytes())
        (self.root / "contracts.sh").write_text(
            'env CHECKED_PLANT_BIN="${PWD}/candidate" CHECKED_PLANT_DETACHED_BIN="${PWD}/detached.py" uv run --no-project regressions.py '
            'RunnerTests.test_unexpected_pass_and_unrelated_error_are_failures '
            'RunnerTests.test_render_rejects_incomplete_or_failed_rows '
            'RunnerTests.test_executable_modes_preserved_and_fingerprinted '
            'RunnerTests.test_hardlinked_destinations_refused '
            'RunnerTests.test_timeout_is_setup_error '
            'RunnerTests.test_green_controls_are_separate_and_checked '
            'RunnerTests.test_absent_record_aliases_and_refusal_cleanup '
            'RunnerTests.test_leading_dash_scripts_execute '
            'RunnerTests.test_skipped_unittest_control_refused '
            'RunnerTests.test_detached_stdio_does_not_block_failure_json '
            'RunnerTests.test_truncated_output_cannot_pass '
            'RunnerTests.test_invalid_manifests_refuse_records '
            'RunnerTests.test_recheck_io_causes_preserved '
            'RunnerTests.test_private_patches_ignore_ancestor_git_context '
            'RunnerTests.test_continuous_output_keeps_spools_bounded '
            'RunnerTests.test_fifo_input_fails_without_waiting '
            'RunnerTests.test_symlink_inputs_are_refused '
            'RunnerTests.test_external_read_paths_are_centralized '
            'RunnerTests.test_unsupported_manifests_write_failed_json '
            'RunnerTests.test_stale_render_fifo_refuses_without_records '
            'RunnerTests.test_parsed_manifest_bytes_match_fingerprint '
            'RunnerTests.test_normally_exiting_step_stops_its_group '
            'RunnerTests.test_term_ignoring_group_is_stopped '
            'RunnerTests.test_unnormalized_inputs_refuse_before_materialization '
            'RunnerTests.test_unsupported_runtime_refuses_before_spawn '
            'RunnerTests.test_disappearing_manifest_preserves_cause '
            'RunnerTests.test_render_preserves_surrounding_ledger '
            'RunnerTests.test_closed_stdio_parent_timeout_writes_failure '
            'RunnerTests.test_failure_recording_is_centralized '
            'RunnerTests.test_inspection_failure_retains_subprocess_diagnostics '
            'RunnerTests.test_forbidden_output_blocks_records -q\n'
        )
        changes = [
            ("assertion-verdict", 'require(matches(row["red"], variant["red"]),', 'require(True,',
             "FAIL: test_unexpected_pass_and_unrelated_error_are_failures"),
            ("publication-verdict", 'require(row["status"] == outcome(kind) and row["restored"] is True and row["green_passed"] is True,',
             'require(True,', "FAIL: test_render_rejects_incomplete_or_failed_rows"),
            ("executable-mode", "target.chmod(mode)", "pass", "FAIL: test_executable_modes_preserved_and_fingerprinted"),
            ("hardlink-protection", "require(len(set(identities)) == len(identities) and not (set(identities) & protected_ids),", "require(True,",
             "FAIL: test_hardlinked_destinations_refused"),
            ("timeout-evidence", "timed_out = True", "timed_out = False", "FAIL: test_timeout_is_setup_error"),
            ("control-verdict", 'require(matches(row["control"], manifest["green"]),', 'require(True,',
             "FAIL: test_green_controls_are_separate_and_checked"),
            ("script-operands", '["bash", "-euo", "pipefail", "--",', '["bash", "-euo", "pipefail",',
             "FAIL: test_leading_dash_scripts_execute"),
            ("skip-evidence", 'and all(s in output for s in wanted["contains"])\n            and not any(s in output for s in wanted.get("excludes", [])))',
             'and True)', "FAIL: test_skipped_unittest_control_refused"),
            ("bounded-capture", "remaining = deadline - time.monotonic()", "remaining = timeout",
             "FAIL: test_detached_stdio_does_not_block_failure_json"),
            ("truncated-evidence", "output_truncated = output_truncated or any(len(data) > OUTPUT_LIMIT for data in output)",
             "output_truncated = False", "FAIL: test_truncated_output_cannot_pass"),
            ("manifest-empty", "and (variants or controls)", "and True", "FAIL: test_invalid_manifests_refuse_records"),
            ("manifest-zero-red", "1 <= code <= 125 if red", "0 <= code <= 125 if red", "FAIL: test_invalid_manifests_refuse_records"),
            ("manifest-no-assertion", 'require(bool(value.get("contains")),', 'require(True,', "FAIL: test_invalid_manifests_refuse_records"),
            ("step-evidence", "return (valid_step(result) and type", "return (True and type",
             "FAIL: test_render_rejects_incomplete_or_failed_rows"),
            ("recheck-cause", '\"; \".join(failures.values())', '\"lost input failure\"',
             "FAIL: test_recheck_io_causes_preserved"),
            ("private-git", '"--git-dir=" + str(git_context.resolve()), "--work-tree=" + str(root.resolve()),',
             '', "FAIL: test_private_patches_ignore_ancestor_git_context"),
            ("disk-bound", "room = OUTPUT_LIMIT - counts[key.fileobj]", "room = len(chunk)",
             "FAIL: test_continuous_output_keeps_spools_bounded"),
            ("regular-input", "os.O_RDONLY | os.O_NONBLOCK", "os.O_RDONLY",
             "FAIL: test_fifo_input_fails_without_waiting"),
            ("symlink-input", "require(not current.is_symlink(),", "require(True,",
             "FAIL: test_symlink_inputs_are_refused"),
            ("forbidden-output", 'and not any(s in output for s in wanted.get("excludes", []))', 'and True',
             "FAIL: test_forbidden_output_blocks_records"),
            ("parallel-reader", "def load_manifest(path):", "def unchecked(path):\n    return path.read_text()\n\n\ndef load_manifest(path):",
             "FAIL: test_external_read_paths_are_centralized"),
            ("manifest-reader", "data, mode = read_regular(path)\n    manifest = parse_json(data)",
             'data, mode = path.read_bytes(), __import__("stat").S_IMODE(path.stat().st_mode)\n    manifest = parse_json(data)',
             "FAIL: test_unsupported_manifests_write_failed_json"),
            ("render-manifest-reader", "data, mode = read_regular(path)\n    manifest = parse_json(data)",
             'data, mode = path.read_bytes(), __import__("stat").S_IMODE(path.stat().st_mode)\n    manifest = parse_json(data)',
             "FAIL: test_stale_render_fifo_refuses_without_records"),
            ("manifest-fingerprint", 'require(before["manifest"] == parsed,', 'require(True,',
             "FAIL: test_parsed_manifest_bytes_match_fingerprint"),
            ("background-group", "for requested_signal in (signal.SIGTERM, signal.SIGKILL):",
             "for requested_signal in (signal.SIGTERM,):", "FAIL: test_term_ignoring_group_is_stopped"),
            ("runtime-support", 'require(callable(getattr(os, "waitid", None)) and hasattr(os, "WNOWAIT"),',
             'require(True,', "FAIL: test_unsupported_runtime_refuses_before_spawn"),
            ("manifest-cause", 'require(all(v is not None for v in before.values()),',
             'require(before["manifest"] == parsed, "manifest changed after parsing")\n        require(all(v is not None for v in before.values()),',
             "FAIL: test_disappearing_manifest_preserves_cause"),
            ("ledger-preservation", "text = before + block + after", "text = block",
             "FAIL: test_render_preserves_surrounding_ledger"),
        ]
        partitions = [changes[index::4] for index in range(4)]
        all_names = [entry[0] for entry in changes]
        partition_names = [entry[0] for part in partitions for entry in part]
        self.assertEqual(len(changes), 28)
        self.assertEqual([len(part) for part in partitions], [7, 7, 7, 7])
        self.assertEqual(sorted(partition_names), sorted(all_names))
        self.assertEqual(len(set(partition_names)), len(changes))
        partition = int(os.environ.get("CHECKED_PLANT_GUARD_PART", "1"))
        self.assertIn(partition, (1, 2, 3, 4))
        changes = partitions[partition - 1]
        probe = self.root / "CaseProbe"
        probe.touch()
        case_aliases = (self.root / "caseprobe").exists()
        probe.unlink()
        variants = []
        for name, old, new, marker in changes:
            extra_core = None
            target = next(name for name, text in sources.items() if old in text)
            original = sources[target]
            self.assertGreaterEqual(original.count(old), 1)
            patch = name + ".patch"
            methods = [marker.removeprefix("FAIL: ")]
            required = [marker, "FAILED (failures="]
            if name == "hardlink-protection":
                methods.append("test_absent_record_aliases_and_refusal_cleanup")
                if case_aliases:
                    required.append("FAIL: test_absent_record_aliases_and_refusal_cleanup")
            if name == "bounded-capture":
                methods.append("test_closed_stdio_parent_timeout_writes_failure")
                required.append("FAIL: test_closed_stdio_parent_timeout_writes_failure")
            if name == "recheck-cause":
                methods.extend(["test_inspection_failure_retains_subprocess_diagnostics", "test_failure_recording_is_centralized"])
                required.extend(["FAIL: test_inspection_failure_retains_subprocess_diagnostics",
                                 "FAIL: test_failure_recording_is_centralized"])
            if name == "manifest-empty":
                methods.append("test_unnormalized_inputs_refuse_before_materialization")
                required.append("FAIL: test_unnormalized_inputs_refuse_before_materialization")
            selected = " ".join("RunnerTests." + method for method in methods)
            red_script = ('env CHECKED_PLANT_BIN="${PWD}/candidate" '
                          'CHECKED_PLANT_DETACHED_BIN="${PWD}/detached.py" '
                          'uv run --no-project regressions.py ' + selected + ' -q\n')
            mutated = original.replace(old, new)
            if name == "bounded-capture":
                mutated = mutated.replace('if time.monotonic() >= deadline:\n                            timed_out = True',
                                          'if False:\n                            timed_out = True')
            if name == "recheck-cause":
                extra_core = sources["checked_core.py"].replace('for name in ("stdout", "stderr"):', 'for name in ():')
                mutated += '\ndef unchecked_cause():\n    try:\n        raise ValueError("sample")\n    except ValueError as failure:\n        return str(failure)\n'
            if name == "manifest-empty":
                extra_core = sources["checked_core.py"].replace('require(not path.is_absolute() and all(p not in ("", ".", "..") for p in value.split("/")),', 'require(True,')
            if name == "private-git":
                self.assertEqual(mutated.count("git_boundary=True"), 1)
                mutated = mutated.replace("git_boundary=True", "git_boundary=False")
            (self.root / patch).write_text(
                self.patch_for(target, original, mutated)
                + (self.patch_for("checked_core.py", sources["checked_core.py"], extra_core) if extra_core is not None else "")
                + self.patch_for("contracts.sh", (self.root / "contracts.sh").read_text(), red_script))
            required.append(f"Ran {len(methods)} test" + ("s" if len(methods) != 1 else ""))
            variants.append(dict(name=name, patch=patch,
                                 red=dict(exit_code=1, contains=required,
                                          excludes=["\nERROR:", ", skipped="])))
        self.manifest = dict(
            inputs=["candidate", "checked_core.py", "checked-gate", "regressions.py", "contracts.sh", "detached.py"] + [v["patch"] for v in variants],
            check="contracts.sh", timeout=30,
            green=dict(exit_code=0, contains=["Ran 31 tests", "\nOK\n"], excludes=["skipped", "SKIP", "ERROR:"]), variants=variants,
        )
        result = self.execute()
        self.assertEqual(self.code, 0, result)
        self.assertEqual([r["status"] for r in result["results"]], ["red"] * len(changes))
        self.assertEqual(self.render(), 0)

    def test_input_and_evidence_destinations_protected(self):
        self.execute()
        for target in [self.path, self.subject, self.out / "results.json"]:
            with self.assertRaises(ValueError):
                runner.render(self.out / "results.json", target, self.status)
        with self.assertRaises(FileExistsError):
            runner.run(self.path, self.out)


if __name__ == "__main__":
    unittest.main()
