# Process group cleanup after EPERM

Base commit `ca6a5e18`. Fix commit `12d2017f`. The group recheck applies
only to `EPERM` from normal TERM or KILL. A remaining live member, another
errno, or an unreliable snapshot still rejects cleanup.

## Exit race audit

- `checked-plant` delegates process execution and supervision to `checked_core`. It has no per-PID inspection of its own.
- `stop_group` now checks a fresh snapshot after either normal signal returns `EPERM`. The fallback signal runs only after a cleanup failure and cannot publish a successful departure. `terminate_group` still tolerates `ESRCH`.
- `live_group` reads PID, PGID and status from a process-table snapshot. Its `EPERM` recheck ignores zombies and Darwin's `E` status modifier. A diagnostic on stderr invalidates that recheck even with exit zero. Apple's `ps` can return zero on a failed table read. [Process table read](https://github.com/apple-oss-distributions/adv_cmds/blob/main/ps/ps.c#L575-L611) and [status formatting](https://github.com/apple-oss-distributions/adv_cmds/blob/main/ps/print.c#L444-L474).
- `leader_identity` requests start time and command for the recorded PID. Darwin's `ps` falls back to the process name when the argument read fails. During `command` registration, the parent still holds the child unreaped. At reconciliation, a failed identity read already triggers a group snapshot to establish whether the group departed. A remaining group without identity stays unconfirmed. The reconciliation table snapshot also reads only PID, PGID and status. [Argument lookup](https://github.com/apple-oss-distributions/adv_cmds/blob/main/ps/print.c#L179-L185) and [fallback](https://github.com/apple-oss-distributions/adv_cmds/blob/main/ps/print.c#L284-L288).
- `command` observes the owned child with `waitid(WNOWAIT)` and reaps with `Popen.wait`. Exiting produces a wait status. A missing wait status prevents confirming cleanup.
- Pipeline `collect_exits` polls owned children. `cleanup_started` uses `Popen.send_signal` for a single PID and the subprocess implementation tolerates disappearance. XNU returns success for a zombie or `ESRCH` for a missing PID on this path. [Single-PID signal handling](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/kern/kern_sig.c#L1315-L1336).

## Plant detectors

- Drop the recheck. `test_eperm_confirms_exiting_group` and `test_eperm_confirms_zombie_group` must reject the false cleanup error.
- Accept EPERM without consulting the snapshot. `test_eperm_refuses_live_group_member` must reject the false departure.
- Ignore `ps` diagnostics on exit zero. `test_eperm_refuses_unreliable_snapshot` must reject the false departure.

## Local checks

- `corepack yarn install --immutable`, `make build` and `make lint` each exited 0. The version audit against `origin/main` exited 0. It verified all 61 marketplace entries and the `plant-defects` patch bump from 1.3.0 to 1.3.1.
- The first `make validate` exited 2 when temporary fixture JSON files disappeared during its scan. After the Python runs finished, `make validate` exited 0 with its temporary directory under the validator's existing `node_modules` exclusion.
- `uv run --no-project tests/checked_plant_test.py -q -k group` exited 0 (6 tests). With `CHECKED_PLANT_BEHAVIOR_ONLY=1`, `uv run --no-project tests/checked_plant_test.py -q` exited 0 (50 tests).
- `uv run --no-project tests/checked_plant_test.py -q RunnerTests.test_runner_guards_detect_their_own_plants` exited 0 in partitions 1 and 8.
- `uv run --no-project tests/checked_gate_test.py -q` exited 0 (40 tests, including gate guard partition 1).
- `uv run --no-project tests/checked_python_test.py -q` and `uv run --no-project tests/notification_load_test.py -q` each exited 0 (1 and 22 tests).
- `uv run --no-project python` ran 22 tests from `checked_timeout_budget_test.py` and exited 0. The scheduler test `test_checked_documents_serialize_and_other_documents_overlap` was excluded because it runs the Scrut wrapper with a stub.
- `uv run --script plugins/plant-defects/scripts/checked-plant` subcommands `run` and `render` each exited 0. The JSON records baseline exit 0 for each row.
- Scrut was not run. Direct checked-plant coverage is in `checked-plant.md`, `checked-plant-guards-{1..15}.md`, `checked-python.md` and `checked-timeout-budgets.md`. The `checked-gate-plants*.md` documents use checked-plant to test gate guard mutations.

<!-- checked-plants:start -->

## Verified plants and controls

plant drop-eperm-recheck: named assertion reached; red exit 1; restored; green exit 0.

plant accept-eperm-blindly: named assertion reached; red exit 1; restored; green exit 0.

plant ignore-ps-diagnostics: named assertion reached; red exit 1; restored; green exit 0.

Evidence: `/Users/ctm/Work/projects/tooling/agent-harness-plugins/770-killpg-eperm/.workmux/770/plant-run/results.json`.

<!-- checked-plants:end -->
