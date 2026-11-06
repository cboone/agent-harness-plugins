"""Checked gate behavior and real source plants, invoked by Scrut."""

import contextlib
import ast
import copy
import difflib
import importlib.machinery
import importlib.util
import io
import json
import os
import shutil
import signal
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from checked_test_diagnostics import restart_diagnostic

sys.dont_write_bytecode = True
GATE = Path(os.environ['CHECKED_GATE_BIN'])
PLANT = Path(os.environ['CHECKED_PLANT_BIN'])
BUDGETS = Path(os.environ.get('CHECKED_TIMEOUT_BUDGETS', Path(__file__).parent / 'data/checked-timeout-budgets.json'))
sys.path.insert(0, str(GATE.parent))
import checked_core as core
loader = importlib.machinery.SourceFileLoader('checked_gate', str(GATE))
spec = importlib.util.spec_from_loader(loader.name, loader)
gate = importlib.util.module_from_spec(spec)
loader.exec_module(gate)


PARTIAL_DRIVER = r"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import time
sys.path.insert(0, sys.argv[1])
import checked_core as core
phase, sentinel, oracle = sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4])
original_spawn, original_file = core.subprocess.Popen, core.regular_file
started = []
deadline = min(core.parse_json(core.read_regular(Path(sys.argv[6]))[0])["deadline"], core.deadline_after(5))
def independent_observation():
    while not sentinel.exists():
        if time.monotonic() >= deadline:
            raise RuntimeError('independent sentinel missing')
        time.sleep(0.01)
    code = None if phase == 'running' else started[0].wait(timeout=core.remaining(deadline, 'independent reap'))
    core.write_json(oracle, dict(sentinel=sentinel.read_text(), exit_code=code, pid=started[0].pid))
def spawn(args, **options):
    if phase != 'capture' and len(started) == (2 if phase == 'third' else 1):
        independent_observation()
        if phase != 'pump':
            error = PermissionError if phase == 'permission' else FileNotFoundError
            raise error('injected later spawn failure')
    process = original_spawn(args, **options)
    started.append(process)
    return process
def regular_file(path, **options):
    if phase == 'capture' and path.name == 'stage-1-stdout':
        independent_observation()
        raise PermissionError('injected capture setup failure')
    return original_file(path, **options)
def fail_start(thread):
    raise RuntimeError('injected pump setup failure')
core.subprocess.Popen = spawn
core.regular_file = regular_file
if phase == 'pump':
    core.threading.Thread.start = fail_start
with core.root_supervision():
    raise SystemExit(core.pipeline_worker(Path(sys.argv[6]), Path(sys.argv[7])))
"""


class GateTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(core.root_supervision())
        self.temp = tempfile.TemporaryDirectory(prefix='checked-gate-test-')
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.root = self.work / 'repo'
        self.root.mkdir()
        self.git('init', '--quiet', '--template=')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.root / 'subject').write_text('valid\n')
        self.git('add', 'subject')
        tree = self.git('write-tree')
        head = self.git('commit-tree', tree, '-m', 'fixture')
        self.git('update-ref', 'HEAD', head)
        self.head = head
        self.action = self.work / 'action.log'
        self.manifest = dict(checks=[dict(argv=['bash', '-c', 'echo checked'], inputs=['HEAD', 'tree'])],
                             action=['bash', '-c', 'echo action >> "$1"', '--', str(self.action)])
        self.path = self.work / 'manifest.json'
        self.count = 0

    def git(self, *args):
        result = subprocess.run(['git', *args], cwd=self.root, text=True, capture_output=True, check=True)
        return result.stdout.strip()

    def run_gate(self):
        self.count += 1
        self.path.write_text(json.dumps(self.manifest))
        self.out = self.work / f'out-{self.count}'
        with contextlib.redirect_stdout(io.StringIO()):
            self.code = gate.run(self.path, self.out, self.root)
        self.receipt = self.out / 'receipt.json'
        return json.loads(self.receipt.read_text())

    def rendered(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            gate.render(gate.load(self.receipt))
        return output.getvalue()

    def test_good_action_runs_once(self):
        value = self.run_gate()
        self.assertEqual(self.code, 0, value.get("cause"))
        self.assertEqual(self.action.read_text(), 'action\n')
        self.assertIn('Check 1: exit 0; exited;', self.rendered())
        self.assertIn('Action: exit 0; exited; refused False;', self.rendered())
        gate.verify(gate.load(self.receipt), head=self.head)
        gate.verify(gate.load(self.receipt), tree=value['before']['tree'])
        self.assertEqual(value['before'], value['after_checks'])
        self.assertGreaterEqual(value['checks'][0]['duration_seconds'], 0)

    def test_apply_failure_refuses_commit(self):
        patch = self.work / 'invalid.patch'
        patch.write_text('not a patch\n')
        self.manifest['checks'][0]['argv'] = ['git', 'apply', '--check', str(patch)]
        self.manifest['checks'].append(dict(argv=['git', 'diff', '--check'], inputs=['tree']))
        self.manifest['action'] = ['git', 'commit', '-S', '--allow-empty', '-m', 'must not happen']
        value = self.run_gate()
        self.assertNotEqual(self.code, 0)
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.head)
        self.assertTrue(value['action_refused'])
        self.assertEqual(value['checks'][0]['exit_code'], 128)
        self.assertIn('Check 1: exit 128; exited;', self.rendered())
        with self.assertRaises(ValueError):
            gate.verify(gate.load(self.receipt), head=self.head)

    def test_pipeline_first_stage_failure(self):
        self.manifest['checks'][0] = dict(pipeline=[['false'], ['true']], inputs=['tree'])
        value = self.run_gate()
        self.assertEqual(self.code, 1)
        self.assertEqual(value['checks'][0]['exit_code'], 1)
        self.assertEqual([r['exit_code'] for r in value['checks'][0]['result']['stages']], [1, 0])
        self.assertIn('Check 1 stage 1: exit 1;', self.rendered())
        self.assertFalse(self.action.exists())
        self.assertIn('Check 1: exit 1; exited;', self.rendered())

    def test_pipeline_passes_data_and_records_captures(self):
        self.manifest['checks'][0] = dict(pipeline=[['printf', 'payload'], ['cat']], inputs=['tree'])
        value = self.run_gate()
        self.assertEqual(self.code, 0, value.get("cause"))
        self.assertEqual([r['exit_code'] for r in value['checks'][0]['result']['stages']], [0, 0])
        self.assertEqual([r['result']['stdout'] for r in value['checks'][0]['result']['stages']], ['payload', 'payload'])
        gate.verify(gate.load(self.receipt), head=self.head)

    def test_interpreter_argv_is_opaque(self):
        commands = [[sys.executable, '-c', 'import subprocess; subprocess.run(["false"]); print("opaque")']]
        if shutil.which('tcsh'):
            commands.append([shutil.which('tcsh'), '-f', '-c', '/usr/bin/false | /usr/bin/true; echo opaque'])
        for args in commands:
            with self.subTest(argv=args):
                self.manifest['checks'][0]['argv'] = args
                value = self.run_gate()
                self.assertEqual(self.code, 0, value.get("cause"))
                self.assertEqual(value['checks'][0]['argv'], args)
                self.assertEqual(value['checks'][0]['exit_code'], 0)
                self.assertIn('opaque', value['checks'][0]['result']['stdout'])

    def test_no_interpreter_classification(self):
        for path in (GATE, GATE.with_name('checked_core.py')):
            source = path.read_text()
            self.assertNotIn('SHELLOPTS', source)
            self.assertNotIn('strict_argv', source)
            names = {'bash', 'sh', 'zsh', 'dash', 'ksh', 'csh', 'tcsh', 'fish'}
            for node in ast.walk(ast.parse(source)):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    self.assertNotIn(node.value, names)

    def test_render_setup_failures_and_partial_receipt(self):
        for contents in (None, '{broken', '{"unused": NaN}'):
            self.count += 1
            path = self.work / f'bad-{self.count}.json'
            if contents is not None:
                path.write_text(contents)
            self.out = self.work / f'failed-{self.count}'
            with contextlib.redirect_stdout(io.StringIO()):
                code = gate.run(path, self.out, self.root)
            self.receipt = self.out / 'receipt.json'
            self.assertEqual(code, 1)
            rendered = subprocess.run([sys.executable, str(GATE), 'render', str(self.receipt)], capture_output=True, text=True)
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            self.assertIn('Action: exit None; not-run; refused True;', self.rendered())
            value = json.loads(self.receipt.read_text(), parse_constant=lambda value: self.fail('invalid JSON receipt: ' + value))
            if contents == '{"unused": NaN}':
                self.assertIn('non-finite JSON constant', value['cause'])
            self.assertIn(json.dumps(value['cause']), self.rendered())
            self.assertIn('cause ', self.rendered())
            value = core.fold_receipt([fact for fact in value['journal'] if fact['kind'] != 'finished'])
            core.write_receipt(self.receipt, value)
            self.assertIn('Action: exit None;', self.rendered())
            with self.assertRaises((ValueError, TypeError)):
                gate.verify(gate.load(self.receipt), head=self.head)

    def test_pipeline_timeout_and_capture_bound(self):
        for stages, limit in (([[sys.executable, '-c', 'import time; print("started", flush=True); time.sleep(3)'], ['cat']], 0.4),
                              ([[sys.executable, '-c', 'import os; os.write(1, b"x" * 2097152)'], ['wc', '-c']], 5)):
            self.manifest['checks'][0] = dict(pipeline=stages, inputs=['tree'], timeout=limit)
            value = self.run_gate()
            self.assertEqual(self.code, 1, value.get("cause"))
            self.assertFalse(self.action.exists())
            self.assertIn('Action: exit None;', self.rendered())
            for row in value['checks'][0]['result']['stages']:
                if row['result'] is not None:
                    self.assertLessEqual(len(row['result']['stdout']), 1048576)

        ready = self.work / 'delayed-stage-ready'
        term_wait = 0.4
        pipeline_limit = term_wait * 12 * 3
        delayed = ('import os, signal, sys, time; from pathlib import Path\n'
                   'def stop(signum, frame):\n'
                   '    signal.signal(signal.SIGTERM, signal.SIG_IGN)\n'
                   f'    time.sleep({term_wait!r})\n'
                   '    os.write(2, b"delayed cleanup complete\\n")\n'
                   '    raise SystemExit(7)\n'
                   'signal.signal(signal.SIGTERM, stop)\n'
                   'Path(sys.argv[1]).write_text("ready")\n'
                   'while True: time.sleep(60)\n')
        self.manifest['checks'][0] = dict(pipeline=[[sys.executable, '-c', delayed, str(ready)], ['cat']],
                                          inputs=['tree'], timeout=pipeline_limit)
        value = self.run_gate()
        self.assertTrue(ready.exists(), 'delayed cleanup stage never became ready')
        self.assertEqual(self.code, 1)
        self.assertFalse(self.action.exists())
        result = value['checks'][0]['result']
        timeout_facts = [fact['data']['timed_out'] for fact in value['journal']
                         if fact['target'] == 'check/0' and fact['kind'] == 'flags' and 'timed_out' in fact['data']]
        self.assertFalse(timeout_facts[-1], 'pipeline supervisor interrupted reserved cleanup')
        self.assertEqual(result['exit_code'], 1)
        stage = result['stages'][0]
        self.assertEqual(stage['exit_code'], 7)
        self.assertTrue(stage['result']['reaped'])
        self.assertIn('delayed cleanup complete', stage['result']['stderr'])

    def test_downstream_closure_retains_complete_capture(self):
        producer = [sys.executable, '-c',
                    'import os;\nfor i in range(128):\n try: os.write(1, b"x" * 4096)\n except BrokenPipeError: break']
        consumer = [sys.executable, '-c', 'import os; os.read(0, 1)']
        self.manifest['checks'][0] = dict(pipeline=[producer, consumer], inputs=['tree'])
        value = self.run_gate()
        self.assertEqual(self.code, 0, value.get("cause"))
        self.assertEqual(len(value['checks'][0]['result']['stages'][0]['result']['stdout']), 128 * 4096)

    def test_completed_stage_exit_survives_later_timeout(self):
        self.manifest['checks'][0] = dict(pipeline=[['false'], ['sleep', '3']], inputs=['tree'], timeout=1)
        value = self.run_gate()
        self.assertEqual(self.code, 1)
        self.assertEqual(value['checks'][0]['result']['stages'][0]['exit_code'], 1)
        self.assertIn('Check 1 stage 1: exit 1;', self.rendered())

    def test_failure_shapes_load_render_and_refuse_verification(self):
        original, append = gate.command, core.FactJournal.append
        cases = ['setup', 'spawn', 'timeout', 'truncation', 'capture', 'cleanup', 'reap']
        for phase in cases:
            with self.subTest(phase=phase):
                self.manifest['checks'][0]['inputs'] = ['missing'] if phase == 'setup' else ['tree']
                def facts(journal, kind, target='root', **data):
                    if phase == 'reap' and target == 'check/0' and kind in ('exit', 'reap'):
                        return None
                    return append(journal, kind, target, **data)
                def fault(argv, *args, **kwargs):
                    if argv == ['bash', '-c', 'echo checked'] and phase == 'spawn':
                        raise FileNotFoundError('spawn failed')
                    result = original(argv, *args, **kwargs)
                    if argv == ['bash', '-c', 'echo checked']:
                        journal, target = kwargs['journal'], kwargs['target']
                        if phase in ('timeout', 'truncation'):
                            journal.append('flags', target, **{'timed_out' if phase == 'timeout' else 'output_truncated': True})
                        elif phase == 'cleanup':
                            journal.append('cleanup', target, remaining_pids=[123], cause='PermissionError: cleanup failed')
                        elif phase in ('capture', 'reap'):
                            journal.append('error', target, cause='injected ' + phase + ' failure')
                    return result
                gate.command, core.FactJournal.append = fault, facts
                try:
                    try:
                        value = self.run_gate()
                        loaded, rendered = gate.load(self.receipt), self.rendered()
                    except (ValueError, KeyError, TypeError) as error:
                        self.fail('emitter/loader contract failed: ' + str(error))
                finally:
                    gate.command, core.FactJournal.append = original, append
                self.assertEqual(self.code, 1, value.get('cause'))
                self.assertFalse(self.action.exists())
                self.assertIn(json.dumps(value['cause']), rendered)
                expected = {'setup': 'not-run', 'spawn': 'setup-error', 'reap': 'exit-unknown'}.get(phase, 'exited')
                self.assertEqual(loaded['checks'][0]['state'], expected)
                with self.assertRaises(ValueError):
                    gate.verify(loaded, head=self.head)

    def test_emitter_requires_row_constructor(self):
        original = core.row_for
        core.row_for = lambda *args, **kwargs: dict(original(*args, **kwargs))
        try:
            with self.assertRaisesRegex(ValueError, 'constructor'):
                self.run_gate()
        finally:
            core.row_for = original
        self.assertFalse(self.action.exists())

    def test_pipeline_failures_preserve_observed_facts(self):
        original = core.read_regular
        cases = ['capture-0-stdout', 'capture-0-stderr', 'capture-1-stdout', 'capture-1-stderr',
                 'response-absent', 'response-corrupt', 'missing-first-stage', 'missing-later-stage',
                 'missing-stream', 'missing-duration', 'setup', 'spawn', 'timeout', 'bad-complete', 'missing-complete']
        for phase in cases:
            with self.subTest(phase=phase):
                stages = [['printf', 'contract'], ['cat']]
                if phase == 'setup': stages[0] = ['/no/such/checked-gate-stage']
                if phase == 'spawn': stages[1] = ['/no/such/checked-gate-stage']
                if phase == 'timeout': stages[1] = ['sleep', '3']
                self.manifest['checks'][0] = dict(pipeline=stages, inputs=['tree'], timeout=1 if phase == 'timeout' else 5)
                reads, expected = set(), {}
                def observed():
                    facts = core.FactJournal(self.out / 'facts.jsonl').facts()
                    found = {}
                    for index, args in enumerate(stages):
                        events = [f for f in facts if f['target'] == f'check/0/stage/{index}']
                        starts = [f for f in events if f['kind'] == 'started']
                        exits = [f for f in events if f['kind'] == 'exit']
                        commands = [f for f in events if f['kind'] == 'command']
                        found[tuple(args)] = (bool(starts), exits[0]['data']['code'] if exits else None,
                                              exits[0]['at'] - commands[0]['at'] if exits else None)
                    return found
                def read(path, **kwargs):
                    if path.name == 'response.json':
                        expected.update(observed())
                        if phase == 'response-absent': raise FileNotFoundError('worker response unavailable')
                        data, mode = original(path, **kwargs)
                        if phase == 'response-corrupt': return b'{broken', mode
                        report = json.loads(data)
                        if phase == 'missing-first-stage': report['stages'][0] = None
                        if phase == 'missing-later-stage': report['stages'][1] = None
                        if phase == 'missing-stream': del report['stages'][0]['streams']['stdout']
                        if phase == 'missing-duration': report['stages'][0]['elapsed'] = None
                        if phase == 'bad-complete': report['complete'] = 'unknown'
                        if phase == 'missing-complete': del report['complete']
                        return json.dumps(report).encode(), mode
                    if path.name.startswith('stage-'):
                        self.assertEqual(observed(), expected, 'execution facts changed before capture IO')
                        reads.add(path.name)
                        if phase == 'capture-' + path.name.removeprefix('stage-'):
                            raise OSError('injected capture read failure')
                    return original(path, **kwargs)
                core.read_regular = read
                try:
                    try:
                        value = self.run_gate()
                        loaded = gate.load(self.receipt)
                        self.rendered()
                    except (ValueError, KeyError, TypeError) as error:
                        self.fail('pipeline evidence contract: ' + str(error))
                finally:
                    core.read_regular = original
                self.assertEqual(self.code, 1, value.get('cause'))
                self.assertFalse(self.action.exists())
                result = value['checks'][0]['result']
                self.assertIsInstance(result, dict, value.get('cause'))
                rows = result['stages']
                for number, row in enumerate(rows, 1):
                    line = next(line for line in self.rendered().splitlines() if line.startswith(f"Check 1 stage {number}:"))
                    self.assertIn("cause " + json.dumps(row["cause"]) + ".", line)
                    started, code, duration = expected[tuple(row['argv'])]
                    self.assertEqual(row['started'], started if started else row['started'])
                    self.assertEqual(row['exit_code'], code)
                    if code is not None:
                        self.assertTrue(row['started'] and row['exit_observed'])
                        self.assertEqual(row['duration_seconds'], duration)
                if phase.startswith('capture-'):
                    self.assertEqual(len(reads), 4)
                    index, channel = int(phase.split('-')[1]), phase.split('-')[2]
                    self.assertFalse(rows[index]['captures'][channel]['loaded'])
                    self.assertIn('injected', rows[index]['captures'][channel]['cause'])
                    self.assertTrue(rows[index]['captures'][channel]['eof_observed'])
                with self.assertRaises(ValueError): gate.verify(loaded, head=self.head)

    def test_command_facts_are_monotonic(self):
        result = core.command(['printf', 'stable'], self.root, 5)
        row = core.row_for(['printf', 'stable'])
        core.record_result(row, result, 1.0)
        self.assertTrue(core.row_complete(row))
        later = dict(result, exit_code=None, reaped=False, stdout='', stderr='', capture_error='later capture unavailable')
        captures = {key: dict(eof_observed=False, loaded=False, cause='later capture unavailable') for key in ('stdout', 'stderr')}
        core.record_result(row, later, None, started=None, captures=captures)
        self.assertEqual(row['exit_code'], 0)
        self.assertTrue(row['started'] and row['exit_observed'])
        self.assertEqual(row['duration_seconds'], 1.0)
        self.assertEqual(row['result']['stdout'], 'stable')
        self.assertTrue(all(f['loaded'] and f['eof_observed'] for f in row['captures'].values()))
        self.assertFalse(core.row_complete(row))
        with self.assertRaises(ValueError):
            core.record_error(row, 'later setup failure', 2.0)
        self.assertEqual(row['exit_code'], 0)
        invalid = core.row_for(['printf', 'stable'])
        invalid['started'] = True
        with self.assertRaises(ValueError):
            core.validate_row(invalid)

    def test_supervisor_spool_failure_preserves_observations(self):
        original = gate.command
        def failing(args, root, limit, **kwargs):
            if kwargs.get('target') == 'check/0':
                with mock.patch.object(core, 'read_spool', side_effect=OSError('spool unavailable')):
                    return original(args, root, limit, **kwargs)
            return original(args, root, limit, **kwargs)
        for pipeline in (False, True):
            with self.subTest(pipeline=pipeline):
                if pipeline:
                    self.manifest['checks'][0] = dict(pipeline=[['printf', 'checked\n'], ['cat']], inputs=['tree'])
                with mock.patch.object(gate, 'command', side_effect=failing), mock.patch.object(core, 'command', side_effect=failing):
                    value = self.run_gate()
                self.assertEqual(self.code, 1)
                row = value['checks'][0]
                self.assertEqual(row['exit_code'], 0)
                self.assertTrue(row['exit_observed'])
                self.assertTrue(row['result']['reaped'])
                self.assertEqual(row['result']['stdout'], 'checked\n')
                self.assertIn('spool unavailable', row['cause'])
                if pipeline:
                    self.assertEqual([r['exit_code'] for r in row['result']['stages']], [0, 0])
                self.assertIn('Check 1: exit 0;', self.rendered())
                with self.assertRaises(ValueError):
                    gate.verify(gate.load(self.receipt), head=self.head)
                self.assertFalse(self.action.exists())

    def test_strict_json_codec(self):
        for token in ('1e309', '-1e309', 'NaN', 'Infinity', '-Infinity'):
            with self.subTest(token=token), self.assertRaises(ValueError):
                core.parse_json('{"value": ' + token + '}')
        for number in (float('inf'), float('-inf'), float('nan')):
            with self.assertRaises(ValueError):
                core.encode_json(dict(value=number))
        self.path.write_text('{"unused": 1e309}')
        self.out = self.work / 'overflow'
        with contextlib.redirect_stdout(io.StringIO()):
            code = gate.run(self.path, self.out, self.root)
        self.receipt = self.out / 'receipt.json'
        self.assertEqual(code, 1)
        self.assertIn('non-finite JSON number', gate.load(self.receipt)['cause'])
        self.assertIn('Action: exit None;', self.rendered())

    def test_receipt_cannot_bypass_journal(self):
        self.run_gate()
        value = gate.load(self.receipt)
        value['checks'][0]['exit_code'] = 17
        value['checks'][0]['result']['exit_code'] = 17
        with self.assertRaisesRegex(ValueError, 'journal fold'):
            core.write_receipt(self.receipt, value)
        self.receipt.write_text(core.encode_json(value))
        with self.assertRaisesRegex(ValueError, 'journal fold'):
            gate.load(self.receipt)

    def test_json_codec_is_centralized(self):
        violations = []
        for path in (GATE, PLANT, GATE.with_name('checked_core.py')):
            tree = ast.parse(path.read_text())
            parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module == 'json':
                    violations.append((path.name, node.lineno))
                if isinstance(node, ast.Import):
                    violations.extend((path.name, node.lineno) for name in node.names if name.name == 'json' and name.asname)
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == 'json' and node.attr in ('load', 'loads', 'dump', 'dumps'):
                    ancestor = parents.get(node)
                    while ancestor is not None and not isinstance(ancestor, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        ancestor = parents.get(ancestor)
                    allowed = path.name == 'checked_core.py' and ancestor is not None and (ancestor.name, node.attr) in (('parse_json', 'loads'), ('encode_json', 'dumps'))
                    if not allowed:
                        violations.append((path.name, node.lineno))
        self.assertEqual(violations, [], 'JSON codec bypass')

    def test_generic_argv_and_expected_exits(self):
        cases = [(['printf', '%s', ''], 0), ([sys.executable, '-c', 'raise SystemExit(128)'], 128),
                 ([sys.executable, '-c', 'import os, signal; os.kill(os.getpid(), signal.SIGTERM)'], -signal.SIGTERM)]
        for args, expected in cases:
            self.manifest['checks'][0] = dict(argv=args, expected_exit=expected, inputs=['tree'])
            value = self.run_gate()
            self.assertEqual(self.code, 0, value.get('cause'))
            self.assertEqual(value['checks'][0]['exit_code'], expected)
            gate.verify(gate.load(self.receipt), head=self.head)

    def test_declared_index_flags_change_refuses_action(self):
        self.manifest['checks'][0] = dict(argv=['git', 'update-index', '--assume-unchanged', 'subject'], inputs=['index'])
        value = self.run_gate()
        self.assertEqual(self.code, 1)
        self.assertEqual(value['before']['tree'], value['after_checks']['tree'])
        self.assertNotEqual(value['before']['index'], value['after_checks']['index'])
        self.assertFalse(self.action.exists())

    def test_verify_accepts_action_commit_at_checked_tree(self):
        tree = self.git('rev-parse', 'HEAD^{tree}')
        script = ('import subprocess, sys; '
                  'head=subprocess.check_output(["git", "commit-tree", sys.argv[1], "-p", sys.argv[2], "-m", "fixture action"]).decode().strip(); '
                  'subprocess.run(["git", "update-ref", "HEAD", head], check=True)')
        self.manifest['action'] = [sys.executable, '-c', script, tree, self.head]
        value = self.run_gate()
        self.assertEqual(self.code, 0, value.get('cause'))
        after = self.git('rev-parse', 'HEAD')
        self.assertNotEqual(after, self.head)
        result = subprocess.run([sys.executable, str(GATE), 'verify', str(self.receipt), '--head', after],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(value['before']['tree'], value['after_action']['head_tree'])

    def test_entry_scripts_do_not_write_module_bytecode(self):
        environment = {key: value for key, value in os.environ.items() if key not in
                       ('PYTHONPYCACHEPREFIX', 'PYTHONDONTWRITEBYTECODE')}
        for entry in (GATE, PLANT):
            with self.subTest(entry=entry.name):
                folder = self.work / ('entry-' + entry.name)
                folder.mkdir()
                for source in (GATE, PLANT, GATE.with_name('checked_core.py')):
                    (folder / source.name).write_bytes(source.read_bytes())
                result = subprocess.run([sys.executable, str(folder / entry.name), '--help'],
                                        env=environment, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('usage:', result.stdout.lower())
                self.assertEqual(list(folder.glob('__pycache__/*')), [], 'entry script wrote module bytecode')

    def test_action_failures_preserve_evidence(self):
        cases = [('exit', ['sh', '-c', 'printf attempted; exit 7'], 5),
                 ('spawn', ['/no/such/checked-gate-action'], 5), ('timeout', ['sleep', '3'], 0.1)]
        for phase, args, limit in cases:
            with self.subTest(phase=phase):
                self.manifest.update(action=args, action_timeout=limit)
                value = self.run_gate()
                self.assertEqual(self.code, 1)
                self.assertFalse(value['action_refused'])
                row = value['action']
                if phase == 'spawn':
                    self.assertEqual(row['state'], 'setup-error')
                    self.assertFalse(row['started'])
                    self.assertIsNone(row['exit_code'])
                    self.assertIn('FileNotFoundError', row['cause'])
                else:
                    self.assertTrue(row['started'] and row['exit_observed'])
                    self.assertTrue(row['result']['reaped'])
                    if phase == 'exit':
                        self.assertEqual(row['exit_code'], 7)
                        self.assertEqual(row['result']['stdout'], 'attempted')
                    else:
                        self.assertTrue(row['result']['timed_out'])
                        self.assertLess(row['exit_code'], 0)
                self.assertIn(f"Action: exit {row['exit_code']};", self.rendered())
                self.assertIn("command cause " + json.dumps(row["cause"]), self.rendered())
                self.assertIn("argv " + json.dumps(row["argv"]), self.rendered())
                with self.assertRaises(ValueError):
                    gate.verify(gate.load(self.receipt), head=self.head)

    def test_declared_ignored_file_content_and_mode_gate_action(self):
        info = self.root / '.git/info'
        info.mkdir(exist_ok=True)
        (info / 'exclude').write_text('/config\n')
        config = self.root / 'config'
        config.write_text('valid\n')
        config.chmod(0o644)
        check = self.manifest['checks'][0]
        check.update(argv=['true'], inputs=['tree', 'config'])
        good = self.run_gate()
        self.assertEqual(self.code, 0, good.get('cause'))
        gate.verify(gate.load(self.receipt), tree=good['before']['tree'])
        for phase, args in [('content', ['sh', '-c', 'printf changed > config']), ('mode', ['chmod', '600', 'config'])]:
            with self.subTest(phase=phase):
                self.action.unlink(missing_ok=True)
                config.write_text('valid\n')
                config.chmod(0o644)
                check['argv'] = args
                value = self.run_gate()
                self.assertEqual(self.code, 1)
                self.assertEqual(value['checks'][0]['exit_code'], 0)
                self.assertEqual(value['before']['tree'], value['after_checks']['tree'])
                self.assertNotEqual(value['before']['files']['config'], value['after_checks']['files']['config'])
                self.assertFalse(self.action.exists())
                self.assertIn('Check 1: exit 0;', self.rendered())
                with self.assertRaises(ValueError):
                    gate.verify(gate.load(self.receipt), tree=good['before']['tree'])

    def test_each_check_fingerprint_boundary_is_required(self):
        self.manifest['checks'] = [dict(argv=['sh', '-c', script], inputs=['tree']) for script in
                                   ('printf unchecked > subject', 'test "$(cat subject)" = unchecked', 'printf "valid\\n" > subject')]
        value = self.run_gate()
        self.assertEqual(self.code, 1)
        self.assertEqual([row['exit_code'] for row in value['checks']], [0, 0, 0])
        self.assertEqual(value['before'], value['after_checks'])
        self.assertNotEqual(value['checks'][0]['input_fingerprints']['end'][0]['value'], value['before'])
        self.assertFalse(self.action.exists())
        self.assertIn('Check 3: exit 0;', self.rendered())
        with self.assertRaises(ValueError):
            gate.verify(gate.load(self.receipt), head=self.head)
        self.manifest['checks'] = [dict(argv=['true'], inputs=['tree'])]
        good = self.run_gate()
        self.assertEqual(self.code, 0, good.get('cause'))
        self.action.unlink()
        missing = core.fold_receipt([fact for fact in good['journal'] if not
                                   (fact['target'] == 'check/0' and fact['kind'] == 'fingerprint' and fact['data']['phase'] == 'start')])
        self.assertFalse(missing['success'])
        core.write_receipt(self.receipt, missing)
        with self.assertRaises(ValueError):
            gate.verify(gate.load(self.receipt), head=self.head)
        original = gate.fingerprint
        calls = 0
        def unavailable(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('boundary unavailable')
            return original(*args, **kwargs)
        with mock.patch.object(gate, 'fingerprint', side_effect=unavailable):
            value = self.run_gate()
        self.assertEqual(self.code, 1)
        self.assertEqual(value['checks'][0]['exit_code'], 0)
        self.assertIn('boundary unavailable', value['checks'][0]['input_fingerprints']['start'][0]['cause'])
        self.assertFalse(self.action.exists())
        with self.assertRaises(ValueError):
            gate.verify(gate.load(self.receipt), head=self.head)

    def test_partial_pipeline_setup_retains_independent_observations(self):
        original = core.command
        driver = self.work / 'partial-worker.py'
        driver.write_text(PARTIAL_DRIVER)
        for phase in ('spawn', 'permission', 'capture', 'third', 'running', 'pump'):
            with self.subTest(phase=phase):
                sentinel, oracle = self.work / ('sentinel-' + phase), self.work / ('oracle-' + phase)
                script = ('import os,sys,time; from pathlib import Path; '
                          'os.write(1,b"early out\\n"); os.write(2,b"early diagnostic\\n"); '
                          'Path(sys.argv[1]).write_text("wrote"); '
                          + ('time.sleep(60)' if phase == 'running' else 'raise SystemExit(7)'))
                stages = [[sys.executable, '-c', script, str(sentinel)], ['/no/such/later-stage']]
                if phase == 'third': stages.insert(1, ['sleep', '60'])
                if phase == 'pump': stages[1] = ['cat']
                self.manifest['checks'][0] = dict(pipeline=stages, inputs=['tree'], timeout=5)
                def command(args, root, limit, **options):
                    if len(args) > 2 and args[2] == 'pipeline-worker':
                        args = [args[0], str(driver), str(GATE.parent), phase, str(sentinel), str(oracle), *args[2:]]
                    return original(args, root, limit, **options)
                with mock.patch.object(core, 'command', side_effect=command):
                    value = self.run_gate()
                self.assertTrue(oracle.is_file(), value.get('cause'))
                independent = json.loads(oracle.read_text())
                self.assertEqual(independent['sentinel'], 'wrote')
                self.assertEqual(independent['exit_code'], None if phase == 'running' else 7)
                self.assertEqual(self.code, 1)
                self.assertFalse(self.action.exists())
                result = value['checks'][0]['result']
                self.assertIsInstance(result, dict, value.get('cause'))
                rows = result['stages']
                first = rows[0]
                self.assertIsNotNone(first['exit_code'])
                if phase != 'running': self.assertEqual(first['exit_code'], 7)
                else: self.assertLess(first['exit_code'], 0)
                self.assertEqual(first['result']['stdout'], 'early out\n')
                self.assertEqual(first['result']['stderr'], 'early diagnostic\n')
                for row in rows:
                    if row['started']:
                        self.assertIsNotNone(row['exit_code'])
                        self.assertTrue(row['result']['reaped'])
                self.assertIn('injected', value['checks'][0]['cause'])
                self.assertIn('early diagnostic', first['result']['stderr'])
                self.rendered()
                with self.assertRaises(ValueError):
                    gate.verify(gate.load(self.receipt), head=self.head)

    def test_journal_persistence_failures_retain_facts_and_refuse_action(self):
        original_append, original_flush = core.FactJournal.append, core.FactJournal.flush
        for phase in ('append', 'flush', 'partial'):
            with self.subTest(phase=phase):
                injected = False
                def append(journal, kind, target='root', **data):
                    nonlocal injected
                    fact = original_append(journal, kind, target, **data)
                    if target == 'check/0' and kind == 'loaded' and not injected and phase in ('append', 'partial'):
                        injected = True
                        if phase == 'append':
                            raise OSError('injected append acknowledgement failure')
                        with journal.path.open('ab') as output:
                            output.write(b'\n{"schema":1,"id":"torn-record')
                    return fact
                def flush(journal):
                    nonlocal injected
                    if phase == 'flush' and not injected and journal.pending and journal.pending[0]['target'] == 'check/0' and journal.pending[0]['kind'] == 'exit':
                        injected = True
                        raise OSError('injected journal flush failure')
                    return original_flush(journal)
                with mock.patch.object(core.FactJournal, 'append', append), mock.patch.object(core.FactJournal, 'flush', flush):
                    value = self.run_gate()
                self.assertTrue(injected)
                row = value['checks'][0]
                self.assertEqual(row['exit_code'], 0)
                self.assertEqual(row['result']['stdout'], 'checked\n')
                self.assertTrue(row['started'] and row['exit_observed'] and row['result']['reaped'])
                self.assertTrue(all(stream['loaded'] and stream['eof_observed'] for stream in row['captures'].values()))
                self.assertTrue(value['journal_errors'])
                self.assertEqual(self.code, 1)
                self.assertTrue(value['action_refused'])
                self.assertFalse(self.action.exists())
                self.assertIn('Check 1: exit 0;', self.rendered())
                if phase == 'partial': self.assertIn(b'torn-record', (self.out / 'facts.jsonl').read_bytes())
                with self.assertRaises(ValueError):
                    gate.verify(gate.load(self.receipt), head=self.head)

    def test_empty_check_manifest_refuses_action(self):
        self.manifest['checks'] = []
        value = self.run_gate()
        self.assertEqual(self.code, 1)
        self.assertTrue(value['action_refused'])
        self.assertFalse(self.action.exists())
        self.assertIn('declare at least one check', value['cause'])
        self.assertIn('Action: exit None;', self.rendered())
        with self.assertRaises(ValueError):
            gate.verify(gate.load(self.receipt), head=self.head)

    def test_checked_plant_automatically_fingerprints_its_core(self):
        plugin, inputs = self.work / 'plugin-copy', self.work / 'plant-inputs'
        plugin.mkdir()
        inputs.mkdir()
        for source in (GATE, PLANT, GATE.with_name('checked_core.py')):
            shutil.copy2(source, plugin / source.name)
        (inputs / 'subject.txt').write_text('valid\n')
        (inputs / 'check.sh').write_text(
            'if [[ "$(cat subject.txt)" == valid ]]; then\n'
            '  echo "check OK"\nelse\n  echo "ASSERT subject valid" >&2\n  exit 1\nfi\n')
        (inputs / 'change.patch').write_text('--- a/subject.txt\n+++ b/subject.txt\n@@ -1 +1 @@\n-valid\n+wrong\n')
        manifest = dict(inputs=['subject.txt', 'check.sh', 'change.patch'], check='check.sh', timeout=5,
                        green=dict(exit_code=0, contains=['check OK']),
                        variants=[dict(name='subject-valid', patch='change.patch',
                                       red=dict(exit_code=1, contains=['ASSERT subject valid']))])
        self.assertNotIn('checked_core.py', manifest['inputs'])
        path, out = inputs / 'manifest.json', self.work / 'plant-output'
        path.write_text(json.dumps(manifest))
        result = subprocess.run([sys.executable, str(plugin / PLANT.name), 'run', str(path), str(out)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        evidence = json.loads((out / 'results.json').read_text())
        self.assertTrue(evidence['success'])
        ledger, status = self.work / 'plant-ledger.md', self.work / 'plant-status.md'
        ledger.write_text('# Existing ledger\n')
        status.write_text('existing status\n')
        def render():
            return subprocess.run([sys.executable, str(plugin / PLANT.name), 'render', str(out / 'results.json'),
                                   '--ledger', str(ledger), '--status', str(status)], capture_output=True, text=True)
        self.assertEqual(render().returncode, 0)
        records = ledger.read_bytes(), status.read_bytes()
        module = plugin / 'checked_core.py'
        original, mode = module.read_bytes(), module.stat().st_mode & 0o7777
        for phase in ('content', 'mode'):
            with self.subTest(phase=phase):
                try:
                    if phase == 'content': module.write_bytes(original + b'\n# copied-core change\n')
                    else: module.chmod(mode ^ 0o100)
                    refused = render()
                    self.assertNotEqual(refused.returncode, 0, refused.stdout)
                    self.assertEqual((ledger.read_bytes(), status.read_bytes()), records)
                finally:
                    module.write_bytes(original)
                    module.chmod(mode)
        self.assertEqual(render().returncode, 0)
        linked = self.work / 'linked-checked-plant'
        linked.symlink_to(plugin / PLANT.name)
        linked_out = self.work / 'linked-plant-output'
        prefix = ['uv', 'run', '--script', str(linked)]
        linked_run = subprocess.run([*prefix, 'run', str(path), str(linked_out)], capture_output=True, text=True)
        self.assertEqual(linked_run.returncode, 0, linked_run.stderr)
        def linked_render(destination=ledger):
            return subprocess.run([*prefix, 'render', str(linked_out / 'results.json'), '--ledger', str(destination),
                                   '--status', str(status)], capture_output=True, text=True)
        self.assertEqual(linked_render().returncode, 0)
        linked_records = ledger.read_bytes(), status.read_bytes()
        try:
            module.write_bytes(original + b'\n# linked-core change\n')
            self.assertNotEqual(linked_render().returncode, 0)
            self.assertEqual((ledger.read_bytes(), status.read_bytes()), linked_records)
        finally:
            module.write_bytes(original)
            module.chmod(mode)
        self.assertEqual(linked_render().returncode, 0)
        try:
            protected = linked_render(module)
            self.assertNotEqual(protected.returncode, 0, protected.stdout)
            self.assertEqual(module.read_bytes(), original)
            self.assertEqual(status.read_bytes(), linked_records[1])
        finally:
            module.write_bytes(original)
            module.chmod(mode)

    def test_external_manifest_change_refuses_action(self):
        self.manifest['checks'][0]['argv'] = ['sh', '-c', 'printf changed >> "$1"', '--', str(self.path)]
        value = self.run_gate()
        self.assertEqual(self.code, 1)
        self.assertEqual(value['checks'][0]['exit_code'], 0)
        self.assertEqual(value['before'], value['after_checks'])
        self.assertFalse(self.action.exists())
        self.assertIn('manifest changed', value['cause'])
        self.assertIn('Check 1: exit 0;', self.rendered())
        with self.assertRaises(ValueError):
            gate.verify(gate.load(self.receipt), head=self.head)

    def test_untracked_files_contribute_to_tree_and_refuse_changes(self):
        untracked = self.root / 'untracked'
        untracked.write_text('initial\n')
        self.manifest['checks'][0]['argv'] = ['true']
        good = self.run_gate()
        self.assertEqual(self.code, 0, good.get('cause'))
        self.assertIn('untracked', self.git('ls-tree', '--name-only', good['before']['tree']).splitlines())
        self.assertNotEqual(good['before']['tree'], self.git('rev-parse', 'HEAD^{tree}'))
        gate.verify(gate.load(self.receipt), tree=good['before']['tree'])
        for script in ('printf changed > untracked', 'printf created > another-untracked'):
            with self.subTest(script=script):
                self.action.unlink(missing_ok=True)
                untracked.write_text('initial\n')
                self.manifest['checks'][0]['argv'] = ['sh', '-c', script]
                value = self.run_gate()
                self.assertEqual(self.code, 1)
                self.assertEqual(value['checks'][0]['exit_code'], 0)
                self.assertNotEqual(value['before']['tree'], value['after_checks']['tree'])
                self.assertFalse(self.action.exists())
                self.assertIn('Check 1: exit 0;', self.rendered())
                with self.assertRaises(ValueError):
                    gate.verify(gate.load(self.receipt), tree=value['before']['tree'])

    def test_tree_change_refuses_action(self):
        self.manifest['checks'][0]['argv'] = ['bash', '-c', 'echo changed > subject']
        value = self.run_gate()
        self.assertEqual(self.code, 1)
        self.assertTrue(value['action_refused'])
        self.assertIn('inputs changed', value['cause'])
        self.assertFalse(self.action.exists())

    def test_declared_unrun_check_fails(self):
        self.manifest['checks'].append(dict(argv=['bash', '-c', 'echo last'], inputs=['tree']))
        original = gate.execute
        try:
            def skip_last(row, root, limit, **kwargs):
                if row['argv'] != ['bash', '-c', 'echo last']:
                    original(row, root, limit, **kwargs)
            gate.execute = skip_last
            value = self.run_gate()
        finally:
            gate.execute = original
        self.assertEqual(self.code, 1)
        self.assertEqual(value['checks'][1]['state'], 'not-run')
        self.assertTrue(value['action_refused'])
        self.assertFalse(self.action.exists())
        self.assertIn('Check 2: exit None; not-run;', self.rendered())

    def test_expected_nonzero_and_all_checks_run(self):
        self.manifest['checks'][0].update(argv=['bash', '-c', 'exit 3'], expected_exit=3)
        self.manifest['checks'].append(dict(argv=['bash', '-c', 'echo second'], inputs=['tree']))
        value = self.run_gate()
        self.assertEqual(self.code, 0, value.get("cause"))
        self.assertEqual([r['exit_code'] for r in value['checks']], [3, 0])
        self.manifest['checks'][0]['expected_exit'] = 0
        value = self.run_gate()
        self.assertEqual(self.code, 1)
        self.assertEqual([r['state'] for r in value['checks']], ['exited', 'exited'])

    def test_declared_index_change_refuses_action(self):
        (self.root / 'subject').write_text('staged later\n')
        self.manifest['checks'][0].update(argv=['git', 'add', 'subject'], inputs=['tree', 'index'])
        value = self.run_gate()
        self.assertEqual(self.code, 1)
        self.assertEqual(value['before']['tree'], value['after_checks']['tree'])
        self.assertNotEqual(value['before']['index'], value['after_checks']['index'])
        self.assertFalse(self.action.exists())

    def test_verify_refuses_missing_failed_partial_other_tree_schema(self):
        with self.assertRaises(FileNotFoundError):
            gate.load(self.work / 'missing.json')
        good = self.run_gate()
        self.assertEqual(self.code, 0, good.get("cause"))
        for change in ({'success': False}, {'complete': False}, {'action_refused': True},
                       {'schema': 99}, {'checks': []}):
            value = copy.deepcopy(good)
            value.update(change)
            self.receipt.write_text(json.dumps(value))
            with self.subTest(change=change), self.assertRaises((ValueError, KeyError, TypeError)):
                gate.verify(gate.load(self.receipt), head=self.head)
        self.receipt.write_text(json.dumps(good))
        with self.assertRaises(ValueError):
            gate.verify(gate.load(self.receipt), tree='0' * 40)
        with self.assertRaises(ValueError):
            gate.verify(gate.load(self.receipt), head='0' * 40)
        gate.verify(gate.load(self.receipt), tree=good['before']['tree'])

    def test_dirty_head_and_missing_fingerprint_refused(self):
        (self.root / 'subject').write_text('dirty before checks\n')
        value = self.run_gate()
        self.assertEqual(self.code, 0, value.get("cause"))
        with self.assertRaises(ValueError):
            gate.verify(gate.load(self.receipt), head=self.head)
        gate.verify(gate.load(self.receipt), tree=value['before']['tree'])
        del value['before']['files']
        value['after_checks'] = copy.deepcopy(value['before'])
        self.receipt.write_text(json.dumps(value))
        with self.assertRaises((ValueError, KeyError)):
            gate.verify(gate.load(self.receipt), tree=value['before']['tree'])

    def test_timeout_and_spawn_error(self):
        for args in (['bash', '-c', 'sleep 3'], ['/no/such/checked-gate-command']):
            self.manifest['checks'][0].update(argv=args, timeout=3)
            value = self.run_gate()
            self.assertEqual(self.code, 1, value.get("cause"))
            self.assertFalse(self.action.exists())
            self.assertTrue(value['complete'])

    def test_cli_verify_and_render(self):
        value = self.run_gate()
        for args, code in ((['verify', str(self.receipt), '--head', self.head], 0),
                           (['verify', str(self.receipt), '--tree', '0' * 40], 1),
                           (['verify', str(self.work / 'missing'), '--head', self.head], 1),
                           (['render', str(self.receipt)], 0)):
            result = subprocess.run([sys.executable, str(GATE), *args], text=True, capture_output=True)
            self.assertEqual(result.returncode, code, result.stderr)
            if args[0] == 'render':
                self.assertIn('Check 1: exit 0;', result.stdout)


class PlantTests(unittest.TestCase):
    def test_restart_guards_detect_real_plants(self):
        with tempfile.TemporaryDirectory(prefix='checked-gate-plants-') as work:
            root = Path(work)
            sources = {'checked-gate': GATE.read_text(), 'checked_core.py': GATE.with_name('checked_core.py').read_text(),
                       'checked-plant': PLANT.read_text(),
                       'plant-regressions.py': (Path(__file__).parent / 'checked_plant_test.py').read_text(),
                       'detached.py': (Path(__file__).parent / 'fixtures/checked-plant-detached.py').read_text(),
                       'budgets.json': BUDGETS.read_text(),
                       'checked_test_diagnostics.py': Path(__file__).with_name('checked_test_diagnostics.py').read_text(),
                       'regressions.py': Path(__file__).read_text()}
            for name, source in sources.items():
                (root / name).write_text(source)
            check = ('env CHECKED_GATE_BIN="$PWD/checked-gate" '
                     'CHECKED_TIMEOUT_BUDGETS="$PWD/budgets.json" CHECKED_PLANT_BIN="$PWD/checked-plant" CHECKED_PLANT_DETACHED_BIN="$PWD/detached.py" uv run --no-project regressions.py GateTests -q\n')
            (root / 'check.sh').write_text(check)
            changes = [
                ('action-verdict', 'require(all(passed(r, c.get("expected_exit", 0)) for r, c in',
                 'require(all(True for r, c in', 'test_apply_failure_refuses_commit'),
                ('action-once', 'execute(receipt["action"], root, manifest.get("action_timeout", 60), journal=journal, target="action", plan=plan)',
                 'execute(receipt["action"], root, manifest.get("action_timeout", 60), journal=journal, target="action", plan=plan); execute(receipt["action"], root, manifest.get("action_timeout", 60), journal=journal, target="action", plan=plan)',
                 'test_good_action_runs_once'),
                ('pipeline-verdict', 'report["complete"] and all(row["code"] == 0 for row in report["stages"])',
                 'report["complete"]', 'test_pipeline_first_stage_failure'),
                ('no-interpreter-classification', 'def execute(row, root, limit, *, journal, target, plan=None):',
                 'def execute(row, root, limit, *, journal, target, plan=None):\n    interpreter = "tcsh"', 'test_no_interpreter_classification'),
                ('failure-rendering', 'def load(path):',
                 'def load(path):\n    validate(parse_json(read_regular(path)[0])["manifest"])',
                 'test_render_setup_failures_and_partial_receipt'),
                ('duplicate-reader', 'def argv(value):',
                 'def regular_file(path):\n    return path.read_bytes()\n\ndef argv(value):',
                 'test_external_read_paths_are_centralized'),
                ('downstream-capture', 'destination = None\n                            break',
                 'return', 'test_downstream_closure_retains_complete_capture'),
                ('persist-exits', 'journal.append("exit", f"{target}/stage/{index}", code=process.returncode)',
                 'pass', 'test_completed_stage_exit_survives_later_timeout'),
                ('stage-capture-bound', 'room = OUTPUT_LIMIT - count\n', 'room = len(chunk)\n',
                 'test_pipeline_timeout_and_capture_bound'),
                ('stage-evidence-order', 'elif kind == "exit":',
                 'elif kind == "ignored-exit":', 'test_pipeline_failures_preserve_observed_facts'),
                ('monotonic-exit', 'if row["exit_observed"]:', 'if False:', 'test_command_facts_are_monotonic'),
                ('empty-argument', "isinstance(s, str) and '\\0' not in s", "isinstance(s, str) and s and '\\0' not in s",
                 'test_generic_argv_and_expected_exits'),
                ('expected-exit-range', 'require(type(expected) is int,',
                 'require(type(expected) is int and 0 <= expected <= 125,', 'test_generic_argv_and_expected_exits'),
                ('index-flags', '"ls-files", "--stage", "-v", "-z"',
                 '"ls-files", "--stage", "-z"', 'test_declared_index_flags_change_refuses_action'),
                ('finite-json', 'json.loads(data, parse_constant=reject, parse_float=finite)', 'json.loads(data, parse_float=finite)',
                 'test_render_setup_failures_and_partial_receipt'),
                ('typed-start-state', 'require(row["state"] not in ("not-run", "setup-error") or row["started"] is not True,',
                 'require(True,', 'test_command_facts_are_monotonic'),
                ('row-states', 'row["state"] in ROW_STATES', 'row["state"] in ROW_STATES - {"exit-unknown"}',
                 'test_failure_shapes_load_render_and_refuse_verification'),
                ('row-constructor', 'require(isinstance(row, CommandRow),', 'require(True,',
                 'test_emitter_requires_row_constructor'),
                ('tree-guard', 'require(receipt["before"] == receipt["after_checks"],',
                 'require(True,', 'test_tree_change_refuses_action'),
                ('unrun-guard', 'require(all(passed(r, c.get("expected_exit", 0)) for r, c in',
                 'require(all(True for r, c in', 'test_declared_unrun_check_fails'),
                ('verify-action-head', 'for state in (value["before"], value["after_action"]))',
                 'for state in (value["before"],))', 'test_verify_accepts_action_commit_at_checked_tree'),
                ('verify-tree', 'value["before"]["tree"] == tree', 'True',
                 'test_verify_refuses_missing_failed_partial_other_tree_schema'),
                ('verify-complete', 'value["complete"] is True', 'True',
                 'test_verify_refuses_missing_failed_partial_other_tree_schema'),
                ('verify-success', 'value["success"] is True', 'True',
                 'test_verify_refuses_missing_failed_partial_other_tree_schema'),
                ('verify-membership', 'len(value["checks"]) == len(manifest["checks"])', 'True',
                 'test_verify_refuses_missing_failed_partial_other_tree_schema'),
                ('completion-envelope', 'isinstance(report, dict) and type(report.get("complete")) is bool and report["complete"],', 'isinstance(report, dict),',
                 'test_pipeline_failures_preserve_observed_facts'),
                ('supervisor-spool', 'observe(journal, "exit", target, code=', 'observe(None, "exit", target, code=',
                 'test_supervisor_spool_failure_preserves_observations'),
                ('exponent-overflow', 'parse_float=finite', 'parse_float=float', 'test_strict_json_codec'),
                ('journal-bypass', 'require(encode_json(value, sort_keys=True) == encode_json(folded, sort_keys=True),',
                 'require(True,', 'test_receipt_cannot_bypass_journal'),
                ('stage-render-cause', 'print(f"Check {index} stage {number}: exit {stage[\'exit_code\']}; {stage[\'state\']}; argv {encode_json(stage[\'argv\'])}; cause {encode_json(stage[\'cause\'])}.")', 'print(f"Check {index} stage {number}: exit {stage[\'exit_code\']}; {stage[\'state\']}; argv {encode_json(stage[\'argv\'])}.")', 'test_pipeline_failures_preserve_observed_facts'),
                ('action-render-cause', 'f"cause {encode_json(value[\'cause\'])}; argv {encode_json(row[\'argv\'])}; command cause {encode_json(row[\'cause\'])}.")', 'f"cause {encode_json(value[\'cause\'])}.")', 'test_action_failures_preserve_evidence'),
                ('manifest-stability', 'require(read_regular(path)[0] == raw,', 'require(True,', 'test_external_manifest_change_refuses_action'),
                ('untracked-tree', '["add", "--all", "--", "."]', '["add", "--update", "--", "."]', 'test_untracked_files_contribute_to_tree_and_refuse_changes'),
                ('partial-setup-capture', '            for index, process in enumerate(processes):\n                row, streams = report["stages"][index], spools[index]', '            if report["cause"] is not None:\n                return 1\n            for index, process in enumerate(processes):\n                row, streams = report["stages"][index], spools[index]', 'test_partial_pipeline_setup_retains_independent_observations'),
                ('partial-setup-reap', 'for requested_signal, phases_left in ((signal.SIGTERM, 3), (signal.SIGKILL, 2)):', 'for requested_signal, grace in ():', 'test_partial_pipeline_setup_retains_independent_observations'),
                ('journal-error-action', 'require(not receipt["journal_errors"],', 'require(True,', 'test_journal_persistence_failures_retain_facts_and_refuse_action'),
                ('journal-error-marker', 'if self.failures:', 'if False:', 'test_journal_persistence_failures_retain_facts_and_refuse_action'),
                ('empty-check-manifest', 'isinstance(checks, list) and checks', 'isinstance(checks, list)', 'test_empty_check_manifest_refuses_action'),
                ('automatic-core-fingerprint', 'fingerprints[name]["core"] = dict(sha256=digest(module_data), mode=module_mode)', 'pass', 'test_checked_plant_automatically_fingerprints_its_core'),
                ('automatic-core-content', 'fingerprints[name]["core"] = dict(sha256=digest(module_data), mode=module_mode)', 'fingerprints[name]["core"] = dict(sha256=digest(b""), mode=module_mode)', 'test_checked_plant_automatically_fingerprints_its_core'),
                ('automatic-core-mode', 'fingerprints[name]["core"] = dict(sha256=digest(module_data), mode=module_mode)', 'fingerprints[name]["core"] = dict(sha256=digest(module_data), mode=0)', 'test_checked_plant_automatically_fingerprints_its_core'),
                ('linked-core-resolution', 'read_regular(Path(__file__).resolve().with_name("checked_core.py"))', 'read_regular(Path(__file__).with_name("checked_core.py"))', 'test_checked_plant_automatically_fingerprints_its_core'),
                ('linked-core-protection', ', Path(__file__).resolve().with_name("checked_core.py").resolve()', '', 'test_checked_plant_automatically_fingerprints_its_core'),
                ('entry-gate-bytecode', 'sys.dont_write_bytecode = True\nfrom checked_core import (command',
                 'sys.dont_write_bytecode = False\nfrom checked_core import (command', 'test_entry_scripts_do_not_write_module_bytecode'),
                ('entry-plant-bytecode', 'sys.dont_write_bytecode = True\nfrom checked_core import (\n',
                 'sys.dont_write_bytecode = False\nfrom checked_core import (\n', 'test_entry_scripts_do_not_write_module_bytecode'),
                ('action-outcome', 'def passed(row, expected):', 'def passed(row, expected):\n    return True',
                 'test_action_failures_preserve_evidence'),
                ('declared-file-content', 'files[name] = dict(sha256=digest(data), mode=mode)',
                 'files[name] = dict(sha256=digest(b""), mode=mode)', 'test_declared_ignored_file_content_and_mode_gate_action'),
                ('declared-file-mode', 'files[name] = dict(sha256=digest(data), mode=mode)',
                 'files[name] = dict(sha256=digest(data), mode=0)', 'test_declared_ignored_file_content_and_mode_gate_action'),
                ('check-boundaries', 'def boundaries_match(value):', 'def boundaries_match(value):\n    return True',
                 'test_each_check_fingerprint_boundary_is_required'),
                ('codec-bypass', 'def argv(value):', 'def unused_parser(data):\n    import json\n    return json.loads(data)\n\ndef argv(value):',
                 'test_json_codec_is_centralized'),
            ]
            policy = json.loads(BUDGETS.read_text())
            documents = {name: row for name, row in policy['documents'].items() if 'gate_variants' in row}
            declared = [variant for row in documents.values() for variant in row['gate_variants']]
            self.assertEqual(sorted(declared), sorted(row[0] for row in changes))
            self.assertEqual(len(declared), len(set(declared)))
            partition = int(os.environ.get('CHECKED_GATE_GUARD_PART', '1'))
            document = 'checked-gate-plants' + ('' if partition == 1 else '-' + str(partition)) + '.md'
            selected = documents[document]['gate_variants']
            for name, old, new, method in (row for row in changes if row[0] in selected):
                with self.subTest(plant=name):
                    target = next(target for target, source in sources.items() if old in source)
                    mutated = sources[target].replace(old, new)
                    if name in ('verify-complete', 'verify-success', 'verify-membership'):
                        mutated = mutated.replace('strict=True', 'strict=False') if name == 'verify-membership' else mutated
                    if name == 'tree-guard':
                        mutated = mutated.replace('require(boundaries_match(receipt),', 'require(True,')
                    if name == 'stage-capture-bound':
                        mutated = mutated.replace('require(len(buffers[channel]) + len(raw) <= OUTPUT_LIMIT,', 'require(True,')
                    patch = ''.join(difflib.unified_diff(sources[target].splitlines(True), mutated.splitlines(True),
                                                         fromfile='a/' + target, tofile='b/' + target))
                    extras = {}
                    if name == 'pipeline-verdict':
                        extras['checked_core.py'] = sources['checked_core.py'].replace('and all(passed(stage, 0) for stage in row["result"]["stages"])', 'and True')
                    if name in ('verify-complete', 'verify-success', 'verify-membership'):
                        extras['checked_core.py'] = sources['checked_core.py'].replace('require(encode_json(value, sort_keys=True) == encode_json(folded, sort_keys=True),', 'require(True,').replace('    return folded\n', '    return value\n')
                    if name == 'verify-membership':
                        extras['checked_core.py'] = extras['checked_core.py'].replace('def boundaries_match(value):', 'def boundaries_match(value):\n    return True')
                    for extra, alternate in extras.items():
                        patch += ''.join(difflib.unified_diff(sources[extra].splitlines(True), alternate.splitlines(True), fromfile='a/' + extra, tofile='b/' + extra))
                    (root / (name + '.patch')).write_text(patch)
                    selected = check.replace('GateTests -q', 'GateTests.' + method + ' -q')
                    if name == 'duplicate-reader':
                        selected = selected.replace('regressions.py GateTests.', 'plant-regressions.py RunnerTests.')
                    (root / 'check.sh').write_text(selected)
                    manifest = dict(inputs=[*sources, 'check.sh', name + '.patch'], check='check.sh',
                                    timeout=policy['gate_checks'][name], git_timeout=policy['git_timeout'],
                                    green=dict(exit_code=0, contains=['Ran 1 test', '\nOK\n'],
                                               excludes=['ERROR:', 'skipped', 'SKIP']),
                                    variants=[dict(name=name, patch=name + '.patch',
                                                   red=dict(exit_code=1, contains=['FAIL: ' + method, 'Ran 1 test',
                                                                                  'FAILED (failures='],
                                                            excludes=['ERROR:', 'skipped', 'SKIP']))])
                    path = root / 'plants.json'
                    path.write_text(json.dumps(manifest))
                    out = root / name
                    result = subprocess.run([sys.executable, str(PLANT), 'run', str(path), str(out)],
                                            capture_output=True, text=True)
                    value = json.loads((out / 'results.json').read_text())
                    self.assertEqual(result.returncode, 0, restart_diagnostic(
                        value, retain=result.returncode != 0, fixture=name))
                    self.assertEqual([r['status'] for r in value['results']], ['red'])
                    rendered = subprocess.run([sys.executable, str(PLANT), 'render', str(out / 'results.json'),
                                               '--ledger', str(root / 'ledger.md'), '--status', str(root / 'status.md')],
                                              capture_output=True, text=True)
                    self.assertEqual(rendered.returncode, 0, rendered.stderr)
                    self.assertIn('red exit 1; restored; green exit 0.', rendered.stdout)
                    print(rendered.stdout.strip())


if __name__ == '__main__':
    unittest.main()
