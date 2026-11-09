"""Contract checks for notification fixture clocks and draining snapshot readers."""

import os
from pathlib import Path
import shlex
import shutil
import signal
import time
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
PROCESS_LIMIT = 180


def write_python_fixture(path, source):
    compile(source, str(path), 'exec')
    path.write_text(source)


class NotificationLoadTests(unittest.TestCase):
    def setUp(self):
        for tool in ('bash', 'git', 'jq', 'sed', 'head', 'ps'):
            if shutil.which(tool) is None:
                raise RuntimeError('required fixture tool unavailable: ' + tool)

    def fixture_environment(self, **extra):
        environment = {key: value for key, value in os.environ.items() if not key.startswith('NOTIFY_TEST_')}
        environment.pop('BASH_ENV', None)
        environment.update(REPO_ROOT=str(ROOT), NOTIFY_BIN=str(ROOT / 'plugins/notify/scripts/notify'),
                           NOTIFICATION_CLOCK_BIN=str(ROOT / 'tests/fixtures/notification-clock.bash'))
        environment.update(extra)
        return environment

    def execute_fixture(self, scenario, **extra):
        return subprocess.run([str(ROOT / 'tests/fixtures/check-notifications'), scenario],
                              env=self.fixture_environment(**extra), capture_output=True, text=True,
                              timeout=PROCESS_LIMIT)

    def run_fixture(self, scenario, **extra):
        result = self.execute_fixture(scenario, **extra)
        if result.returncode == 2:
            raise RuntimeError('fixture prerequisite failed: ' + result.stdout + result.stderr)
        return result

    def test_prerequisite_error(self):
        observation = subprocess.CompletedProcess(['fixture'], 2, stdout='', stderr='missing observer')
        with mock.patch('subprocess.run', autospec=True, return_value=observation):
            with self.assertRaisesRegex(RuntimeError, 'fixture prerequisite failed: missing observer'):
                self.run_fixture('completion')

    def test_writer_prerequisite(self):
        with tempfile.TemporaryDirectory(prefix='notification-writer-') as directory:
            with self.assertRaises(SyntaxError):
                write_python_fixture(Path(directory) / 'writer.py', 'invalid ! syntax\n')

    def test_entrypoint_guard(self):
        with tempfile.TemporaryDirectory(prefix='notification-entry-') as directory:
            plugin = Path(directory) / 'plugin'
            shutil.copytree(ROOT / 'plugins/notify', plugin)
            notifier = plugin / 'scripts/notify'
            notifier.write_text(notifier.read_text() + '\n')
            result = self.run_fixture('completion', NOTIFY_BIN=str(notifier))
            self.assertEqual((result.returncode, result.stdout), (1, ''))
            self.assertIn('check-notifications: unexpected notifier entry point\n', result.stderr)

    def test_copy_declaration(self):
        result = self.execute_fixture('fixture-copy')
        self.assertEqual((result.returncode, result.stderr), (0, ''))
        self.assertEqual(result.stdout.count('function notification_original_run_alerter() {'), 1)
        self.assertNotIn('function run_alerter() {', result.stdout)

    def test_backend_declaration_guard(self):
        with tempfile.TemporaryDirectory(prefix='notification-declaration-') as directory:
            plugin = Path(directory) / 'plugin'
            shutil.copytree(ROOT / 'plugins/notify', plugin)
            notifier = plugin / 'scripts/notify'
            source = notifier.read_text()
            if source.count('function run_alerter() {') != 1:
                raise RuntimeError('canonical backend declaration missing or ambiguous')
            notifier.write_text(source.replace('function run_alerter() {', 'function changed_backend() {', 1))
            result = self.execute_fixture('fixture-copy', NOTIFY_BIN=str(notifier))
            self.assertEqual((result.returncode, result.stdout), (2, ''))
            self.assertIn('check-notifications: expected one backend function declaration\n', result.stderr)

    def test_blocked_startup(self):
        result = self.run_fixture('completion', NOTIFY_TEST_GATE_START='1')
        self.assertEqual((result.returncode, result.stdout, result.stderr),
                         (0, 'Done\nsample-repo · Sample task\nCompleted sample\nGlass\ncodex.png\n', ''))

    def test_grace_ticks(self):
        for scenario in ('delivery', 'delivery-leading-zero'):
            with self.subTest(scenario=scenario):
                result = self.run_fixture(scenario, NOTIFY_TEST_GATE_START='1')
                self.assertEqual((result.returncode, result.stdout, result.stderr),
                                 (0, 'Alerter stops after the grace period without SIGTERM\n', ''))

    def test_join_retains_failure(self):
        result = subprocess.run(['/bin/bash', '-c',
                                 'source "$1"; (exit 23) & disown; notification_finish',
                                 'clock-test', str(ROOT / 'tests/fixtures/notification-clock.bash')],
                                env=self.fixture_environment(), capture_output=True, text=True, timeout=PROCESS_LIMIT)
        self.assertEqual(result.returncode, 23)
        self.assertRegex(result.stderr, r'^notification-clock: detached notifier [0-9]+ exited 23\n$')

    def test_join_retains_prerequisite_error(self):
        result = subprocess.run(['/bin/bash', '-c',
                                 'source "$1"; (exit 2) & disown; (exit 23) & disown; notification_finish',
                                 'clock-test', str(ROOT / 'tests/fixtures/notification-clock.bash')],
                                env=self.fixture_environment(), capture_output=True, text=True, timeout=PROCESS_LIMIT)
        self.assertEqual(result.returncode, 2)
        self.assertRegex(result.stderr, r'^notification-clock: detached notifier [0-9]+ exited 2\n'
                         r'notification-clock: detached notifier [0-9]+ exited 23\n$')

    def process_state(self, pid):
        result = subprocess.run([shutil.which('ps'), '-ww', '-p', str(pid), '-o', 'ppid=', '-o', 'stat=',
                                 '-o', 'command='], capture_output=True, text=True, timeout=PROCESS_LIMIT)
        if result.returncode == 1 and not (result.stdout.strip() or result.stderr.strip()):
            return None
        if result.returncode:
            raise RuntimeError('process inspection failed: ' + result.stdout + result.stderr)
        fields = result.stdout.strip().split(None, 2)
        if len(fields) != 3 or not fields[0].isdigit() or not fields[1]:
            raise RuntimeError('malformed process inspection')
        return int(fields[0]), fields[1], fields[2]

    def registered_backend(self, path, process):
        deadline = time.monotonic() + PROCESS_LIMIT
        while True:
            if path.exists():
                text = path.read_text()
                if text.endswith('\n'):
                    fields = text.rstrip('\n').split('\t')
                    if len(fields) != 2 or not fields[0].isdigit() or int(fields[0]) <= 1:
                        raise RuntimeError('malformed backend registration')
                    if not Path(fields[1]).is_absolute() or not fields[1].endswith('/bin/alerter'):
                        raise RuntimeError('malformed backend identity')
                    return int(fields[0]), os.path.dirname(os.path.dirname(fields[1]))
            if process.poll() is not None:
                stdout, stderr = process.communicate(timeout=PROCESS_LIMIT)
                raise RuntimeError('fixture ended before backend registration: ' + stdout + stderr)
            if time.monotonic() >= deadline:
                raise TimeoutError('backend registration liveness bound expired')
            time.sleep(0.02)

    def test_registration_path_spelling(self):
        with tempfile.TemporaryDirectory(prefix='notification-registration-path-') as temporary:
            path = Path(temporary) / 'registration'
            for directory in ('/tmp/fixture.sample', '/tmp//fixture.sample', '/tmp/./fixture.sample'):
                with self.subTest(directory=directory):
                    path.write_text(f'12345\t{directory}/bin/alerter\n')
                    process = mock.Mock()
                    self.assertEqual(self.registered_backend(path, process), (12345, directory))

    def owned_backend_present(self, backend):
        pid, directory = backend
        state = self.process_state(pid)
        if state is None:
            return False
        if state[1].startswith('Z'):
            return True
        if directory not in state[2]:
            raise RuntimeError('registered PID has an unknown identity; no signal sent')
        return True

    def cleanup_control(self, process, backend):
        if backend is not None:
            pid, directory = backend
            state = self.process_state(pid)
            if state is not None and not state[1].startswith('Z'):
                if directory not in state[2]:
                    raise RuntimeError('cleanup refused an unknown PID identity')
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        if process.poll() is None:
            process.terminate()
        process.communicate(timeout=PROCESS_LIMIT)

    def lifecycle_control(self, *, cancel=False, observation_error=False, deferred=False,
                          signal_number=signal.SIGTERM):
        with tempfile.TemporaryDirectory(prefix='notification-owner-') as directory:
            registration = Path(directory) / 'registered'
            observation = Path(directory) / 'observation'
            extra = dict(NOTIFY_TEST_GATE_START='1', NOTIFY_TEST_REGISTRATION=str(registration),
                         NOTIFY_TEST_OBSERVATION=str(observation))
            if cancel:
                extra['NOTIFY_TEST_PAUSE_READY'] = '1'
            elif deferred:
                extra['NOTIFY_TEST_INTERRUPT_BEFORE_REGISTER'] = str(128 + signal_number)
            else:
                extra['NOTIFY_TEST_FAIL_READY'] = '1'
            if observation_error:
                extra['NOTIFY_TEST_FAIL_OBSERVATION'] = '1'
            process = subprocess.Popen([str(ROOT / 'tests/fixtures/check-notifications'), 'delivery'],
                                       env=self.fixture_environment(**extra), stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, text=True)
            backend = None
            try:
                backend = self.registered_backend(registration, process)
                if cancel:
                    state = self.process_state(backend[0])
                    if state is None or backend[1] not in state[2] or state[0] <= 1:
                        raise RuntimeError('cannot identify the registered backend owner')
                    owner = self.process_state(state[0])
                    if owner is None or backend[1] not in owner[2]:
                        raise RuntimeError('cannot verify the backend owner identity')
                    os.kill(state[0], signal_number)
                stdout, stderr = process.communicate(timeout=PROCESS_LIMIT)
                self.assertFalse(self.owned_backend_present(backend), 'backend must be reaped before return')
                expected_status = 128 + signal_number if cancel or deferred else 2
                self.assertEqual((process.returncode, stdout), (expected_status, ''))
                expected_cause = f'owner interrupted {expected_status}' if cancel or deferred else 'injected readiness failure'
                self.assertIn(expected_cause, stderr)
                if observation_error:
                    self.assertIn('injected observation failure', stderr)
                else:
                    try:
                        output = observation.read_text()
                    except FileNotFoundError:
                        output = ''
                    self.assertEqual(output, 'none running 137\n', 'backend finalizer observation output')
            finally:
                self.cleanup_control(process, backend)

    def test_registration_error_diagnostic(self):
        with tempfile.TemporaryDirectory(prefix='notification-registration-') as directory:
            result = self.execute_fixture('completion', NOTIFY_TEST_GATE_START='1',
                                          NOTIFY_TEST_REGISTRATION=directory)
            self.assertEqual((result.returncode, result.stdout), (2, ''))
            self.assertIn('notification-clock: cannot record backend registration at ' + directory, result.stderr)

    def test_publication_error_after_success(self):
        result = self.execute_fixture('completion', NOTIFY_TEST_GATE_START='1', NOTIFY_TEST_FAIL_OBSERVATION='1')
        self.assertEqual((result.returncode, result.stdout), (2, ''))
        self.assertIn('notification-clock: injected observation failure', result.stderr)
        self.assertIn('notification-clock: cannot publish backend observation', result.stderr)

    def test_backend_error_diagnostic(self):
        result = self.execute_fixture('completion', NOTIFY_TEST_GATE_START='1', NOTIFY_TEST_BACKEND_EXIT='7')
        self.assertEqual((result.returncode, result.stdout), (7, ''))
        self.assertIn('injected backend failure', result.stderr)
        self.assertIn('notification-clock: backend exited 7', result.stderr)

    def test_readiness_error_cleanup(self):
        self.lifecycle_control()

    def test_observation_error_cleanup(self):
        self.lifecycle_control(observation_error=True)

    def test_cancellation_cleanup(self):
        for value in (signal.SIGHUP, signal.SIGTERM):
            with self.subTest(signal=value):
                self.lifecycle_control(cancel=True, signal_number=value)

    def test_deferred_cancellation_cleanup(self):
        for value in (signal.SIGHUP, signal.SIGTERM):
            with self.subTest(signal=value):
                self.lifecycle_control(deferred=True, signal_number=value)

    def test_cancellation_status_survives_observation_error(self):
        self.lifecycle_control(cancel=True, observation_error=True)

    def test_failure_diagnostic(self):
        result = self.run_fixture('fixture-failure')
        self.assertEqual((result.returncode, result.stdout, result.stderr),
                         (1, '', 'check-notifications: scenario fixture-failure exited 1\n'))

    def test_no_alert_after_dispatch(self):
        for scenario in ('visible', 'subagent', 'permission-question'):
            with self.subTest(scenario=scenario):
                result = self.run_fixture(scenario, NOTIFY_TEST_GATE_START='1')
                self.assertEqual((result.returncode, result.stdout, result.stderr), (0, 'No alert\n', ''))

    def test_reported_deliveries_after_blocked_startup(self):
        cases = {
            'sound-full': ('Chord-stop-4\n' * 2 + 'Chord-permission-4\n' + 'Chord-attention-4\n' * 4),
            'tier-top': ('stop: Done | hub: coordinator | Glass\n'
                         'permission: Approve Bash? | hub: coordinator | Funk\n'
                         'plan: none\nquestion: none\nelicit: Question | hub: coordinator | Tink\n'
                         'codex-question: none\ncodex-stop: Done | hub: coordinator | Glass\n'),
            'tier-failure-boundaries': (
                'system: Refusal: thread-42 | atlas: w 42-fix-parser | Funk\n'
                'metadata: Refusal: thread-42 | atlas: w 42-fix-parser | Funk\n'
                'local-output: Refusal: thread-42 | atlas: w 42-fix-parser | Funk\n'
                'new-turn: Error: thread-42 | atlas: w 42-fix-parser | Funk\n'
                'new-reply: Error: thread-42 | atlas: w 42-fix-parser | Funk\n'
                'delayed: Refusal: thread-42 | atlas: w 42-fix-parser | Funk\n'
                'missing: Error: thread-42 | atlas: w 42-fix-parser | Funk\n'
                'subagent: none\nTurn ended in a safeguard refusal.\nTurn ended in an API error.\n'),
        }
        for scenario, expected in cases.items():
            with self.subTest(scenario=scenario):
                result = self.run_fixture(scenario, NOTIFY_TEST_GATE_START='1')
                self.assertEqual((result.returncode, result.stdout, result.stderr), (0, expected, ''))

    def test_draining_snapshot_readers(self):
        source = (ROOT / 'tests/scrut/bugs-gather.md').read_text()
        # Identify snapshot sites from their subjects, independently of reader syntax.
        contracts = {
            '"${work}/linked-bugs" --help': 1,
            'CDPATH=. bash plugins/publish-report-board/scripts/bugs-gather --help': 1,
            '"${work}/corrupt-reused.json"': 2,
            '"${work}/listed.json"': 3,
            '"${work}/no-state.json"': 2,
            '"${work}/zenhub-down.json"': 2,
            'bugs score "${work}/config.json" 2>&1': 1,
            'bugs frobnicate 2>&1': 1,
        }
        readers = []
        for subject, count in contracts.items():
            lines = [line for line in source.splitlines() if line.startswith('$ ') and subject in line]
            if len(lines) != 1:
                raise RuntimeError('missing or ambiguous snapshot subject: ' + subject)
            lexer = shlex.shlex(lines[0][2:], posix=True, punctuation_chars='|;')
            lexer.whitespace_split = True
            tokens = list(lexer)
            if '|' not in tokens:
                raise RuntimeError('snapshot prefix pipeline missing: ' + subject)
            start = tokens.index('|') + 1
            end = next((i for i in range(start, len(tokens)) if tokens[i] in ('|', ';')), len(tokens))
            if start == end:
                raise RuntimeError('snapshot prefix reader missing: ' + subject)
            readers.append((subject, shlex.join(tokens[start:end]), count))
        with tempfile.TemporaryDirectory(prefix='notification-pipe-') as directory:
            writer = Path(directory) / 'writer.py'
            write_python_fixture(writer, 'import os, signal\nsignal.signal(signal.SIGPIPE, signal.SIG_DFL)\n'
                              'for start in range(0, 65536, 256):\n'
                              ' data = b"".join(("row %s\\n" % i).encode() for i in range(start, start+256))\n'
                              ' while data: data = data[os.write(1, data):]\n'
                              'raise SystemExit(1)\n')
            for subject, reader, count in readers:
                with self.subTest(site=subject, reader=reader):
                    result = subprocess.run(['/bin/bash', '-c',
                                             '"$1" "$2" | ' + reader + '; printf "exit %s\\n" "${PIPESTATUS[0]}"',
                                             'pipe-test', sys.executable, str(writer)],
                                            capture_output=True, text=True, timeout=PROCESS_LIMIT)
                    expected = ''.join(f'row {i}\n' for i in range(count)) + 'exit 1\n'
                    self.assertEqual((result.returncode, result.stdout, result.stderr), (0, expected, ''))


if __name__ == '__main__':
    unittest.main()
