"""Reject independent supervision limits and document budgets above CI policy."""

import ast
import copy
import contextlib
import io
import inspect
import json
import os
from pathlib import Path
import sys
import subprocess
import runpy
import tempfile
import unittest
import time
from unittest import mock

from checked_test_diagnostics import restart_diagnostic
from checked_fixture_limits import declared_waits, fixture_margins

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(os.environ["CHECKED_PLANT_BIN"]).parent))
import checked_core as core


def assertion_messages(source):
    messages = []
    for call in ast.walk(ast.parse(source)):
        if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
            continue
        if not isinstance(call.func.value, ast.Name) or call.func.value.id != "self":
            continue
        name = call.func.attr
        if not name.startswith("assert") and name != "fail":
            continue
        method = getattr(unittest.TestCase, name, None)
        if method is None or any(isinstance(arg, ast.Starred) for arg in call.args) or any(
                keyword.arg is None for keyword in call.keywords):
            raise ValueError("unsupported assertion form")
        try:
            signature = inspect.signature(method)
            bound = signature.bind(None, *call.args, **{kw.arg: kw.value for kw in call.keywords})
        except (TypeError, ValueError) as error:
            raise ValueError("unsupported assertion signature") from error
        values = [bound.arguments["msg"]] if "msg" in bound.arguments else []
        for parameter in signature.parameters.values():
            if parameter.kind == inspect.Parameter.VAR_KEYWORD:
                value = bound.arguments.get(parameter.name, {}).get("msg")
                if value is not None:
                    values.append(value)
        for value in values:
            messages.append("".join(node.value for node in ast.walk(value)
                                    if isinstance(node, ast.Constant) and isinstance(node.value, str)))
    return messages


def launch_references_outside(source, *, allow_boundary=False):
    tree = ast.parse(source)
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    modules = {"subprocess": "subprocess", "os": "os"}
    imported = {}
    boundaries = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "launch"]
    boundary = boundaries[0] if allow_boundary and len(boundaries) == 1 else None
    violations = []

    def forbidden(name):
        return name in ("subprocess.Popen", "subprocess.run") or name.startswith(("os.spawn", "os.exec"))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules[alias.asname or alias.name] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module in ("subprocess", "os"):
            for alias in node.names:
                imported[alias.asname or alias.name] = node.module + "." + alias.name

    def module_name(node):
        if isinstance(node, ast.Name):
            return modules.get(node.id)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "__import__":
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                return node.args[0].value
        return None

    for node in ast.walk(tree):
        reference = None
        if isinstance(node, ast.Attribute):
            module = module_name(node.value)
            if module:
                reference = module + "." + node.attr
        elif isinstance(node, ast.Name):
            reference = imported.get(node.id)
        elif isinstance(node, ast.ImportFrom) and node.module in ("os", "subprocess"):
            if any(alias.name == "*" or forbidden(node.module + "." + alias.name) for alias in node.names):
                reference = "subprocess.run"
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "getattr" and len(node.args) >= 2:
            module = module_name(node.args[0])
            if module in ("os", "subprocess"):
                name = node.args[1]
                reference = module + "." + name.value if isinstance(name, ast.Constant) and isinstance(name.value, str) else "subprocess.run"
        if reference is None or not forbidden(reference):
            continue
        parent = parents.get(node)
        while parent is not None and not isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            parent = parents.get(parent)
        if parent is not boundary or boundary is None:
            violations.append(node.lineno)
    return sorted(set(violations))


def literal_limits(source):
    tree = ast.parse(source)
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg == "timeout":
            parent = parents[node]
            if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name) and parent.func.id == "dict":
                continue
            if not (isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, (ast.Name, ast.Attribute))
                    and (node.value.func.id if isinstance(node.value.func, ast.Name) else node.value.func.attr) == "remaining") or any(
                        isinstance(child, ast.Constant) and type(child.value) in (int, float) and child.value > 0
                        for child in ast.walk(node.value)):
                violations.append(node.lineno)
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [target.id if isinstance(target, ast.Name) else target.attr
                     for target in targets if isinstance(target, (ast.Name, ast.Attribute))]
            if any("deadline" in name or name == "until" for name in names):
                if any(isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute)
                       and child.func.attr == "monotonic" for child in ast.walk(node.value)) and any(
                        isinstance(child, ast.Constant) and type(child.value) in (int, float) and child.value > 0
                        for child in ast.walk(node.value)):
                    violations.append(node.lineno)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and
                                               any(part in t.id for part in ("TIMEOUT", "GRACE", "MARGIN", "DEADLINE"))
                                               for t in node.targets):
            if any(isinstance(child, ast.Constant) and type(child.value) in (int, float) for child in ast.walk(node.value)):
                if not all(isinstance(t, ast.Name) and t.id == "CLEANUP_MARGIN" for t in node.targets):
                    violations.append(node.lineno)
    return violations


def document_budgets(policy):
    import checked_plant_test as plant_tests
    totals = {}
    for name, document in policy["documents"].items():
        if "variants" in document or "gate_variants" in document:
            key, checks = ("variants", "checks") if "variants" in document else ("gate_variants", "gate_checks")
            plans = [plant_tests.runner.execution_plan(dict(timeout=policy[checks][variant],
                                                            git_timeout=policy["git_timeout"]))
                     for variant in document[key]]
            total = sum(step["timeout"] for plan in plans for step in plan)
            for plan in plans:
                core.validate_fixed_limits(plan, policy["limit"])
        else:
            total = document["limit"]
            core.validate_fixed_limits([dict(timeout=total)], policy["limit"])
        if total > policy["limit"]:
            raise ValueError(f"{name}: outer limits exceed document cap")
        totals[name] = total
    return totals


class BudgetTests(unittest.TestCase):
    def test_plant_fixture_execution_covers_declared_detector_waits(self):
        policy = json.loads((ROOT / "tests/data/checked-timeout-budgets.json").read_text())
        with self.assertRaisesRegex(ValueError, "undeclared detector wait"):
            declared_waits('def test_unknown():\n    subprocess.run(["true"], timeout=unknown)\n',
                           [], policy, core.CLEANUP_MARGIN)
        module_wait = declared_waits('subprocess.run(["true"], timeout=8)\n'
                                     'class Checks:\n    def test_selected(self): pass\n'
                                     '    def test_unused(self): subprocess.run(["true"], timeout=90)\n',
                                     ["Checks.test_selected"], policy, core.CLEANUP_MARGIN)
        self.assertTrue([row["seconds"] for row in module_wait] == [8],
                        "module detector wait was omitted or unrelated method widened the check")
        old = copy.deepcopy(policy)
        old["detector_budget"], old["checks"]["bounded-capture"] = 60, 60
        _, old_violations = fixture_margins(ROOT, old, core)
        self.assertTrue(any(row.get("fixture") == "checks/bounded-capture" and row.get("seconds") == 45
                            for row in old_violations), "old detector wait was accepted by the static guard")
        rows, violations = [], []
        try:
            rows, violations = fixture_margins(ROOT, policy, core)
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            violations.append(dict(cause=str(error)))
        diagnostic = restart_diagnostic(dict(checks=rows, violations=violations), retain=bool(violations),
                                        fixture="declared-detector-waits")
        self.assertTrue(not violations, "fixture execution does not cover declared detector waits; " + diagnostic)
        self.assertTrue(any(row["fixture"] == "checks/bounded-capture" for row in rows),
                        "bounded-capture fixture was absent from static coverage")

    def test_restart_diagnostics_retain_inner_results_without_printing(self):
        payload = dict(complete=True, success=False, results=[dict(stdout="Result: 0 succeeded, 1 failed and 0 skipped",
                                                                  stderr="FAILED (failures=1)")])
        stream = io.StringIO()
        with tempfile.TemporaryDirectory(prefix="checked-result-retention-") as directory:
            with mock.patch.dict(os.environ, CHECKED_PLANT_DIAGNOSTICS_DIR=directory), contextlib.redirect_stdout(stream):
                diagnostic = restart_diagnostic(payload, retain=True, fixture="retention-test")
            metadata = ast.literal_eval(diagnostic)
            self.assertTrue(isinstance(metadata, dict) and isinstance(metadata.get("result_file"), str),
                            "result retention did not provide a result file")
            path = Path(metadata["result_file"])
            self.assertTrue(path.is_relative_to(directory) and path.is_file(),
                            "retained result is unavailable in its owned directory")
            retained = json.loads(path.read_text())
            self.assertTrue(retained == dict(fixture="retention-test", result=payload),
                            "retained inner result differs from the runner result")
            quiet = not stream.getvalue() and all(row not in diagnostic for row in ("Result:", "FAILED (failures="))
            self.assertTrue(quiet, "result retention printed nested runner output")

    def test_retention_fixture_asserts_before_missing_metadata(self):
        stream = io.StringIO()
        case = BudgetTests("test_restart_diagnostics_retain_inner_results_without_printing")
        with mock.patch.object(sys.modules[__name__], "restart_diagnostic", return_value=repr(dict(complete=True))):
            outcome = unittest.TextTestRunner(stream=stream).run(unittest.TestSuite([case]))
        self.assertTrue(not outcome.errors and len(outcome.failures) == 1,
                        "retention fixture accessed absent metadata before its assertion")

    def test_restart_fixture_diagnostics_omit_runner_output(self):
        payload = dict(exit_code=1, stdout="Result: 1 succeeded, 0 failed and 0 skipped\n",
                       stderr="Ran 1 test in 0.001s\n\nOK\n", timed_out=False, reaped=True, output_truncated=False)
        stream = io.StringIO()
        case = BudgetTests("test_checked_documents_serialize_and_other_documents_overlap")
        with mock.patch.object(core, "command", return_value=payload):
            outcome = unittest.TextTestRunner(stream=stream).run(unittest.TestSuite([case]))
        self.assertEqual(len(outcome.failures), 1)
        forbidden = (payload["stdout"].strip(), payload["stderr"].strip())
        clean = all(token not in stream.getvalue() for token in forbidden)
        self.assertTrue(clean, "restart assertion diagnostic included nested runner output")

    def test_process_launches_share_one_guarded_boundary(self):
        scripts = Path(core.__file__).parent
        for path in sorted(scripts.iterdir()):
            if not path.is_file() or not (path.suffix == ".py" or path.stat().st_mode & 0o111):
                continue
            with self.subTest(script=path.name):
                self.assertEqual(launch_references_outside(path.read_text(), allow_boundary=path.name == "checked_core.py"), [],
                                 "process launch bypasses the shared deadline boundary")
        for source in ("import subprocess\nsubprocess.Popen(['true'])", "import subprocess as child\nrun = child.run\nrun(['true'])",
                       "from subprocess import Popen as start\nstart(['true'])", "import os as system\nsystem.spawnv(0, 'true', [])",
                       "import os\ngetattr(os, 'execvp')('true', [])", "import os\ngetattr(os, operation)()",
                       "def launch():\n def nested():\n  subprocess.run(['true'])"):
            with self.subTest(source=source):
                self.assertTrue(launch_references_outside(source, allow_boundary=True),
                                "launch alias escaped the AST boundary guard")
        self.assertEqual(launch_references_outside("def launch():\n operation = subprocess.Popen\n return operation(['true'])",
                                                  allow_boundary=True), [])
        self.assertEqual(launch_references_outside("import os\ngetattr(os, 'waitid', None)"), [])

    def test_pipeline_journal_lock_cannot_launch_expired_stage(self):
        fixture = ROOT / "tests/fixtures/checked-pipeline-launch-lock.py"
        with core.root_supervision(), tempfile.TemporaryDirectory(prefix="checked-pipeline-launch-lock-") as directory:
            result = core.command([sys.executable, str(fixture), directory, str(Path(core.__file__).parent)], ROOT, 90)
            self.assertEqual(result["exit_code"], 0, restart_diagnostic(result))
            value = json.loads(result["stdout"])
            self.assertEqual(value["holder_exit"], 0)
            self.assertFalse(value["report"]["complete"])
            self.assertFalse(value["report"]["stages"][0]["started"],
                             "pipeline journal wait allowed an expired stage launch")
            self.assertIn("process launch deadline", value["report"]["cause"])

    def test_audit_lock_obeys_inclusive_call_limit(self):
        fixture = ROOT / "tests/fixtures/checked-audit-lock.py"
        with core.root_supervision(), tempfile.TemporaryDirectory(prefix="checked-audit-lock-") as directory:
            result = core.command([sys.executable, str(fixture), directory, str(Path(core.__file__).parent)], ROOT, 60)
            self.assertEqual(result["exit_code"], 0, restart_diagnostic(result))
            record = json.loads(result["stdout"])
            self.assertEqual(record["holder_exit"], 0)
            self.assertIsNotNone(record["call_error"], "audit lock did not expire the call")
            self.assertIn("TimeoutError: journal lock deadline", record["call_error"])
            self.assertLessEqual(record["elapsed"], record["limit"] + min(core.CLEANUP_MARGIN, record["limit"] / 3),
                                 "audit lock wait escaped inclusive call limit")
            self.assertFalse(record["spawned"], "expired allocation reached spawn")
            self.assertIn("incomplete supervision audit", record["finalization_error"])

    def test_parent_state_reads_use_call_deadline_and_expired_launch_refuses(self):
        with core.root_supervision() as runtime, tempfile.TemporaryDirectory(prefix="checked-pre-spawn-") as directory:
            original_states = runtime.states
            seen = []
            def states():
                seen.append(core.ACTIVE_DEADLINE.get())
                return original_states()
            with mock.patch.object(runtime, "states", side_effect=states):
                result = core.command([sys.executable, "-c", "pass"], Path(directory), 6)
            self.assertEqual(result["exit_code"], 0)
            self.assertEqual(seen[0], result["supervision"]["allocation"]["deadline"],
                             "parent state inspection did not inherit call deadline")
            allocation = runtime.allocate(3)
            original_record, original_clock = runtime.record, time.monotonic
            expired = [False]
            def clock():
                return allocation["deadline"] + 1 if expired[0] else original_clock()
            def record(scope, event, **data):
                original_record(scope, event, **data)
                if event == "reserved":
                    expired[0] = True
            with mock.patch.object(runtime, "record", side_effect=record), mock.patch.object(
                    core.time, "monotonic", side_effect=clock), mock.patch.object(
                    core.subprocess, "Popen", side_effect=OSError("unexpected expired launch")) as spawn:
                failure = None
                try:
                    core.command([sys.executable, "-c", "pass"], Path(directory), 3, allocation=allocation)
                except (OSError, ValueError) as error:
                    failure = error
            self.assertIsInstance(failure, TimeoutError, "expired launch did not report its deadline")
            self.assertIn("process launch deadline", str(failure))
            spawn.assert_not_called()

    def test_reconciliation_refuses_survivors_and_unknown_identities(self):
        recorded = dict(start="Thu Nov 5 23:22:01 2026", command="fixture")
        cases = [("absent", None, True),
                 ("reused", dict(recorded, start="Thu Nov 5 23:22:51 2026"), True),
                 ("survivor", dict(recorded), False),
                 ("exec-changed", dict(recorded, command="replacement"), False),
                 ("unreadable", None, False)]
        with core.root_supervision() as parent, tempfile.TemporaryDirectory(prefix="checked-reconcile-") as directory:
            for name, current, clears in cases:
                journal = mock.Mock(path=Path(directory) / name)
                runtime = core.SupervisionRuntime(journal, "fixture-parent")
                states = runtime.cache["states"]
                def record(kind, target, **data):
                    self.assertEqual(kind, "supervision")
                    row = states.setdefault(target, {})
                    row.update(data)
                    runtime.cache["children"].setdefault(row.get("parent"), set()).add(target)
                journal.append.side_effect = record
                runtime.states = mock.Mock(return_value=states)
                allocation = runtime.allocate(1)
                runtime.record(allocation["scope"], "reserved", reserved=True, pgid=123, leader=recorded)
                listing = subprocess.CompletedProcess([], 0, stdout="" if name == "absent" else "123 123 S\n")
                failure = PermissionError("identity denied") if name == "unreadable" else None
                with mock.patch.object(core.subprocess, "run", return_value=listing), mock.patch.object(
                        core, "leader_identity", return_value=current, side_effect=failure), mock.patch.object(
                        core, "live_group", return_value=[123]), mock.patch.object(core, "terminate_group") as signals:
                    if clears:
                        try:
                            runtime.finish()
                        except ValueError as error:
                            self.fail(name + " was not cleared: " + str(error))
                        self.assertEqual(runtime.pending(), [], name)
                    else:
                        with self.assertRaisesRegex(ValueError, "unconfirmed possibly live groups", msg=name) as refused:
                            runtime.finish()
                        self.assertEqual(runtime.pending(), [123], name + " was incorrectly cleared")
                        if failure is not None:
                            self.assertIn("PermissionError: identity denied", str(refused.exception))
                    signals.assert_not_called()

    def test_group_identity_classifies_reuse_survival_and_unknown(self):
        recorded = dict(start="Thu Nov 5 23:22:01 2026", command="fixture")
        self.assertEqual(core.classify_leader(recorded, dict(recorded)), "survivor")
        self.assertEqual(core.classify_leader(recorded, dict(recorded, start="Thu Nov 5 23:22:51 2026")),
                         "reused", "reused group was treated as surviving work")
        self.assertEqual(core.classify_leader(recorded, dict(recorded, command="exec-replacement")),
                         "unknown", "exec-changed command was treated as PID reuse")
        self.assertEqual(core.classify_leader(recorded, None), "unknown")
        self.assertEqual(core.classify_leader(None, recorded), "unknown")

    def test_document_diagnostics_survive_finalization_failure(self):
        with tempfile.TemporaryDirectory(prefix="checked-document-diagnostics-") as directory:
            root = Path(directory)
            (root / "data").mkdir()
            driver = root / "run_checked_budget.py"
            driver.write_bytes((ROOT / "tests/run_checked_budget.py").read_bytes())
            (root / "data/checked-timeout-budgets.json").write_text(json.dumps(
                dict(limit=60, documents={"probe.md": dict(behavior=True)})))
            stdout, stderr = io.StringIO(), io.StringIO()
            args = [str(driver), "probe.md", sys.executable, "-c", 'print("retained document output")']
            with mock.patch.object(sys, "argv", args), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                with mock.patch.object(core.SupervisionRuntime, "finish", side_effect=ValueError("final observation unavailable")):
                    try:
                        runpy.run_path(str(driver), run_name="__main__")
                    except (SystemExit, ValueError) as error:
                        code = error.code if isinstance(error, SystemExit) else 1
                    else:
                        code = 0
            self.assertIn("retained document output", stdout.getvalue(), "finalization discarded captured document output")
            self.assertEqual(code, 1)
            self.assertIn("Document finalization failed: ValueError: final observation unavailable", stderr.getvalue())

    def test_first_term_during_cleanup_is_deferred(self):
        with tempfile.TemporaryDirectory(prefix="checked-cleanup-term-") as directory:
            root = Path(directory)
            script = root / "supervisor.py"
            ready = root / "command-ready"
            child = ('import signal,time; from pathlib import Path; '
                     'signal.signal(signal.SIGTERM,signal.SIG_IGN); '
                     f'Path({str(ready)!r}).write_text("ready"); time.sleep(5)')
            script.write_text(
                'import os,sys,signal\nfrom pathlib import Path\n'
                'sys.path.insert(0,sys.argv[1])\nimport checked_core as core\n'
                'original=core.stop_group\n'
                'def stop(*args, **options):\n'
                '    os.kill(os.getpid(),signal.SIGTERM)\n'
                '    return original(*args, **options)\n'
                'core.stop_group=stop\n'
                'with core.root_supervision():\n'
                f'    core.command([sys.executable,"-c",{child!r}],Path.cwd(),3)\n')
            with core.root_supervision() as runtime:
                result = core.command([sys.executable, str(script), str(Path(core.__file__).parent)], root, 60)
                pending = runtime.pending()
                until = core.deadline_after(30)
                while runtime.pending() and time.monotonic() < until:
                    runtime.reconcile()
                    time.sleep(0.01)
                self.assertFalse(runtime.pending())
                self.assertTrue(ready.exists(), "command fixture never became ready")
                self.assertTrue(core.valid_step(result), "first TERM interrupted command cleanup confirmation: " + restart_diagnostic(result))
                self.assertEqual(result["exit_code"], 143)
                self.assertEqual(pending, [])

                journal = core.FactJournal(root / "pipeline.jsonl", create=True)
                term_wait = 0.4
                # Worker TERM observes one twelfth of the inclusive pipeline limit.
                pipeline_limit = term_wait * 12 * 3
                stage = ('import os,signal,time\n'
                         'def stop(signum,frame):\n'
                         '    signal.signal(signal.SIGTERM,signal.SIG_IGN)\n'
                         '    os.kill(os.getppid(),signal.SIGTERM)\n'
                         f'    time.sleep({term_wait!r})\n'
                         '    raise SystemExit(7)\n'
                         'signal.signal(signal.SIGTERM,stop)\n'
                         'print("pipeline ready",flush=True)\n'
                         'while True: time.sleep(2)\n')
                result = core.pipeline_command([[sys.executable, "-c", stage], ["cat"]], root, pipeline_limit,
                                               journal=journal, target="cleanup-term")
                self.assertIn("pipeline ready", result["stdout"], restart_diagnostic(result))
                first = core.fold_command(journal.facts(), "cleanup-term/stage/0", [sys.executable, "-c", stage])
                self.assertEqual(first["exit_code"], 7, "first TERM interrupted pipeline cleanup")
                self.assertTrue(first["result"]["reaped"], "pipeline cleanup did not reap its stage")

    def test_supervised_calls_require_parent_and_fixed_limits(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "enclosing supervision"):
                core.command([sys.executable, "-c", "pass"], ROOT, 3)
            with tempfile.TemporaryDirectory(prefix="checked-fixed-limit-") as directory:
                with core.root_supervision(directory) as runtime:
                    first = runtime.allocate(3)
                    with mock.patch.object(core.time, "monotonic", return_value=first["deadline"] + 100):
                        later = runtime.allocate(3)
                    self.assertAlmostEqual(first["deadline"] - first["started_at"], 3)
                    self.assertAlmostEqual(later["deadline"] - later["started_at"], 3)
                    escaped = dict(first, deadline=first["deadline"] + 1)
                    with self.assertRaisesRegex(ValueError, "fixed limit"):
                        runtime.validate_allocation(escaped)
                    with mock.patch.object(runtime, "states", return_value={}):
                        with self.assertRaisesRegex(ValueError, "durable parent record"):
                            core.command([sys.executable, "-c", "pass"], ROOT, 3, allocation=first)
            with mock.patch.dict(os.environ, CHECKED_SUPERVISION_AUDIT="incomplete"):
                with self.assertRaisesRegex(ValueError, "incomplete inherited"):
                    with core.root_supervision():
                        self.fail("partial inheritance was accepted")

    def test_nested_limits_are_checked_without_elapsed_admission(self):
        core.validate_fixed_limits([dict(timeout=3)], 3)
        with self.assertRaisesRegex(ValueError, "nested fixed limit"):
            core.validate_fixed_limits([dict(timeout=4)], 3)
        with mock.patch.dict(os.environ, CHECKED_STEP_LIMIT="3"):
            with mock.patch.object(core.time, "monotonic", return_value=1e12):
                plan = core.StepPlan([dict(name="fixed", kind="check", timeout=3)])
                self.assertEqual(plan.steps[0]["timeout"], 3)

    def test_nested_supervisor_unwinds_and_lost_supervisor_is_red(self):
        with tempfile.TemporaryDirectory(prefix="checked-nested-budget-") as directory:
            root = Path(directory)
            for lost in (False, True):
                ready = root / ("lost" if lost else "unwind")
                script = root / "supervisor.py"
                script.write_text(
                    'import os,sys,signal,threading,time\nfrom pathlib import Path\n'
                    'sys.path.insert(0, sys.argv[1])\nimport checked_core as core\n'
                    'ready=Path(sys.argv[2])\n'
                    'def interrupt():\n'
                    '    while not ready.exists(): time.sleep(0.01)\n'
                    '    if sys.argv[3] == "True": os._exit(19)\n'
                    '    os.kill(os.getpid(), signal.SIGTERM)\n'
                    'with core.root_supervision():\n'
                    '    threading.Thread(target=interrupt, daemon=True).start()\n'
                    '    core.command([sys.executable,"-c",'
                    '"import time; from pathlib import Path; Path("+repr(str(ready))+").write_text(\\\"ready\\\"); time.sleep(2)"],'
                    'Path.cwd(),30)\n')
                audit = root / ("audit-lost" if lost else "audit-unwind")
                audit.mkdir()
                with core.root_supervision(audit) as runtime:
                    result = core.command([sys.executable, str(script), str(core.Path(core.__file__).parent),
                                           str(ready), str(lost)], root, 60)
                    self.assertTrue(ready.exists(), restart_diagnostic(result))
                    self.assertEqual(result["exit_code"], 19 if lost else 143, restart_diagnostic(result))
                    states = runtime.states()
                    descendants = runtime.descendants()
                    inherited = [row for scope, row in states.items()
                                 if scope in descendants and row.get("event") == "inherited"]
                    self.assertEqual(len(inherited), 1, states)
                    for row in inherited:
                        self.assertTrue(states[row["parent"]]["reserved"])
                    pending = runtime.pending()
                    until = core.deadline_after(30)
                    while runtime.pending() and time.monotonic() < until:
                        runtime.reconcile()
                        time.sleep(0.01)
                    self.assertFalse(runtime.pending(), "lost supervisor left a live recorded group")
                    if lost:
                        self.assertFalse(core.valid_step(result), "lost supervisor was accepted")
                        self.assertTrue(result["possibly_live_pgids"], restart_diagnostic(result))
                        self.assertIn("supervisor lost", result["cleanup_error"])
                    else:
                        self.assertTrue(core.valid_step(result), restart_diagnostic(result))
                        self.assertEqual(pending, [], "cooperative supervisor left unconfirmed groups")

    def test_supervision_limits_derive_from_deadlines(self):
        for name in ("checked_core.py", "checked-plant"):
            source = (ROOT / "plugins/plant-defects/scripts" / name).read_text()
            self.assertEqual(literal_limits(source), [], name)
        tree = ast.parse((ROOT / "plugins/plant-defects/scripts/checked_core.py").read_text())
        factories = {"allocate", "deadline_after", "phase_deadline"}
        for function in (node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)):
            if function.name not in factories:
                for node in ast.walk(function):
                    if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name)
                                                           and "deadline" in target.id for target in node.targets):
                        self.assertFalse(any(isinstance(part, ast.Call) and isinstance(part.func, ast.Attribute)
                                             and part.func.attr == "monotonic" for part in ast.walk(node.value)),
                                         "independent deadline outside root allocation: " + function.name)
        self.assertEqual(sum(isinstance(node, ast.Assign) and any(isinstance(target, ast.Name)
                             and target.id == "CLEANUP_MARGIN" for target in node.targets) for node in ast.walk(tree)), 1)
        source = ast.parse((ROOT / "tests/checked_gate_test.py").read_text())
        driver = next(ast.literal_eval(node.value) for node in source.body if isinstance(node, ast.Assign)
                      and any(isinstance(target, ast.Name) and target.id == "PARTIAL_DRIVER" for target in node.targets))
        self.assertEqual(literal_limits(driver), [])
        self.assertTrue(literal_limits("subprocess.run(['ps'], timeout=0.25)"))
        self.assertTrue(literal_limits("deadline = time.monotonic() + 0.5"))

    def test_document_bounds_use_executed_declarations(self):
        policy = json.loads((ROOT / "tests/data/checked-timeout-budgets.json").read_text())
        self.assertEqual(policy["limit"], 300)
        try:
            totals = document_budgets(policy)
        except ValueError as error:
            self.fail(str(error))
        documents = {p.name for p in (ROOT / "tests/scrut").glob("checked-plant*.md")}
        documents |= {p.name for p in (ROOT / "tests/scrut").glob("checked-gate*.md")}
        documents.add("checked-timeout-budgets.md")
        self.assertEqual(documents, set(totals))
        import checked_plant_test as plant_tests
        source = ast.parse((ROOT / "tests/checked_plant_test.py").read_text())
        method = next(node for node in ast.walk(source) if isinstance(node, ast.FunctionDef)
                      and node.name == "test_runner_guards_detect_their_own_plants")
        declarations = {node.targets[0].id: ast.literal_eval(node.value) for node in method.body
                        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                        and node.targets[0].id in {"changes", "expected_detectors"}
                        and isinstance(node.value, (ast.List, ast.Set))}
        actual = {name for row in declarations["changes"] for name in plant_tests.guard_methods(row[0], row[3])}
        self.assertEqual(actual, declarations["expected_detectors"], "named detector inventory differs from execution")
        variants = [v for row in policy["documents"].values() for v in row.get("variants", [])]
        self.assertEqual(sorted(variants), sorted(policy["checks"]))
        self.assertEqual(len(variants), len(set(variants)))
        self.assertLessEqual(policy["detector_budget"], policy["checks"]["bounded-capture"])
        gates = [v for row in policy["documents"].values() for v in row.get("gate_variants", [])]
        self.assertEqual(sorted(gates), sorted(policy["gate_checks"]))
        self.assertEqual(len(gates), len(set(gates)))
        for name in totals:
            source = (ROOT / "tests/scrut" / name).read_text()
            self.assertIn('tests/run_checked_budget.py" ' + name, source)
        oversized = copy.deepcopy(policy)
        oversized["checks"]["bounded-capture"] = policy["limit"]
        with self.assertRaises(ValueError):
            document_budgets(oversized)

    def test_checked_documents_serialize_and_other_documents_overlap(self):
        with tempfile.TemporaryDirectory(prefix="checked-document-lanes-") as directory:
            root = Path(directory)
            for name in ("docs", "stub", "state"):
                (root / name).mkdir()
            stub = root / "stub/scrut"
            stub.write_bytes((ROOT / "tests/fixtures/scrut-stub").read_bytes())
            stub.chmod(0o755)
            names = ("lane-parallel-a.md", "lane-parallel-b.md", "checked-gate-lane.md", "checked-plant-lane.md")
            for name in names:
                (root / "docs" / name).touch()
            path = str(stub.parent) + os.pathsep + os.environ["PATH"]
            import shutil
            self.assertEqual(shutil.which("scrut", path=path), str(stub), "scheduler requires its scrut stub")
            with core.root_supervision():
                result = core.command(["bash", str(ROOT / "bin/lib/run-scrut-documents"), "docs"], root, 30,
                                      env_overrides=dict(PATH=path, SCRUT_JOBS="2",
                                                         STUB_SCRUT_SCHEDULER_DIR=str(root / "state")))
            self.assertEqual(result["exit_code"], 0, "scheduler lane contract: " + restart_diagnostic(result))
            self.assertTrue(core.valid_step(result), "scheduler did not finish supervision")
            self.assertTrue(all((root / "state" / name).exists() for name in names[:2]))
            self.assertIn("All 4 scrut documents passed.", result["stdout"])

    def test_runner_mutations_are_valid_python(self):
        source = (ROOT / "tests/checked_plant_test.py").read_text()
        method = next(n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.FunctionDef)
                      and n.name == "test_runner_guards_detect_their_own_plants")
        changes = next(ast.literal_eval(n.value) for n in method.body if isinstance(n, ast.Assign)
                       and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "changes")
        sources = [(ROOT / "plugins/plant-defects/scripts" / name).read_text()
                   for name in ("checked-plant", "checked_core.py", "checked-gate")]
        for name, old, new, marker in changes:
            original = next(text for text in sources if old in text)
            try:
                ast.parse(original.replace(old, new))
            except SyntaxError:
                self.fail("invalid mutation: " + name)

    def test_runtime_support_fixture_does_not_reserve_a_mock_process(self):
        import checked_plant_test as plant_tests
        with tempfile.TemporaryDirectory(prefix="checked-mock-reservation-") as directory:
            journal = mock.Mock(path=Path(directory) / "audit")
            runtime = core.SupervisionRuntime(journal, "fixture-parent")
            states = runtime.cache["states"]
            def append(kind, scope, **data):
                row = states.setdefault(scope, {})
                row.update(data)
                runtime.cache["children"].setdefault(row.get("parent"), set()).add(scope)
            journal.append.side_effect = append
            runtime.states = mock.Mock(return_value=states)
            actor = plant_tests.RunnerTests("test_unsupported_runtime_refuses_before_spawn")
            actor.runtime, actor.root = runtime, Path(directory)
            original = core.require
            def require(condition, message):
                if not message.startswith("runtime requires waitid"):
                    original(condition, message)
            token = core.ACTIVE_RUNTIME.set(runtime)
            try:
                with mock.patch.object(core, "require", side_effect=require):
                    with self.assertRaises(AssertionError):
                        actor.test_unsupported_runtime_refuses_before_spawn()
                self.assertEqual(runtime.pending(), [], "fixture reserved a mocked process")
            finally:
                core.ACTIVE_RUNTIME.reset(token)

    def test_pipeline_fixture_asserts_before_stage_access(self):
        import checked_gate_test as gate_tests
        actor = gate_tests.GateTests("test_pipeline_failures_preserve_observed_facts")
        actor.manifest = dict(checks=[{}])
        actor.out, actor.receipt = ROOT, ROOT / "unused-receipt"
        actor.code = 1
        actor.action = mock.Mock()
        actor.action.exists.return_value = False
        actor.run_gate = mock.Mock(return_value=dict(checks=[dict(result=None)], cause="unavailable pipeline result"))
        actor.rendered = mock.Mock(return_value="")
        failure = None
        with mock.patch.object(gate_tests.gate, "load", return_value={}):
            try:
                actor.test_pipeline_failures_preserve_observed_facts()
            except Exception as error:
                failure = error
        self.assertIsInstance(failure, AssertionError, "pipeline fixture accessed absent stage data")
        self.assertIn("unavailable pipeline result", str(failure))

    def test_assertion_messages_avoid_verdict_exclusions(self):
        selected = {
            "tests/checked_timeout_budget_test.py": None,
            "tests/checked_plant_test.py": {"test_inspection_failure_retains_subprocess_diagnostics",
                                             "test_git_budget_and_execution_plan"},
            "tests/checked_gate_test.py": {"test_pipeline_timeout_and_capture_bound"},
        }
        self.assertEqual(assertion_messages('self.assertIsNotNone(value, "sample diagnostic")'),
                         ["sample diagnostic"])
        self.assertEqual(assertion_messages('self.assertRaisesRegex(ValueError, "pattern", msg="sample diagnostic")'),
                         ["sample diagnostic"])
        for source in ('self.assertUnsupported(value)', 'self.assertTrue(*values)',
                       'self.assertTrue(value, **options)', 'self.assertIsNone()'):
            with self.assertRaisesRegex(ValueError, "unsupported assertion"):
                assertion_messages(source)
        excluded = ("ERROR:", "skipped", "SKIP", "SyntaxError", "ImportError")
        for path, methods in selected.items():
            tree = ast.parse((ROOT / path).read_text())
            for method in ast.walk(tree):
                if not isinstance(method, ast.FunctionDef) or not method.name.startswith("test_"):
                    continue
                if methods is not None and method.name not in methods:
                    continue
                for text in assertion_messages(ast.unparse(method)):
                    self.assertTrue(all(word not in text for word in excluded),
                                    "reserved verdict token in assertion message")

    def test_document_driver_enforces_execution_deadline(self):
        with tempfile.TemporaryDirectory(prefix="checked-document-budget-") as directory:
            root = Path(directory)
            (root / "data").mkdir()
            driver = root / "run_checked_budget.py"
            driver.write_bytes((ROOT / "tests/run_checked_budget.py").read_bytes())
            policy = dict(limit=3, documents={"probe.md": dict(behavior=True)})
            (root / "data/checked-timeout-budgets.json").write_text(json.dumps(policy))
            result = subprocess.run([sys.executable, str(driver), "probe.md", sys.executable, "-c",
                                     'import time; print("budget probe started", flush=True); time.sleep(4)'],
                                    text=True, capture_output=True, timeout=policy["limit"] + core.CLEANUP_MARGIN)
            self.assertEqual(result.returncode, 1, "document driver ignored its declared deadline")
            self.assertIn("budget probe started", result.stdout)
            self.assertIn("Document supervision failed", result.stderr)


if __name__ == "__main__":
    unittest.main()
