# Process group cleanup after EPERM

Base commit `ca6a5e18`. Initial fix commit `12d2017f`. The signal-error
exception applies only to `EPERM` from normal TERM or KILL. A remaining live member, another
errno, or an unreliable snapshot still rejects cleanup.

## Exit race audit

- `checked-plant` delegates process execution and supervision to `checked_core`. It has no per-PID inspection of its own.
- `stop_group` now checks a fresh snapshot after either normal signal returns `EPERM`. The fallback signal runs only after a cleanup failure and cannot publish a successful departure. `terminate_group` still tolerates `ESRCH`.
- `live_group` reads PID, PGID and status from a process-table snapshot. It excludes zombies and members trying to exit, including members held in `E` for a long time. A diagnostic on stderr invalidates the `EPERM` recheck even with exit zero. Apple's `ps` can return zero on a failed table read. [Process table read](https://github.com/apple-oss-distributions/adv_cmds/blob/main/ps/ps.c#L575-L611) and [status formatting](https://github.com/apple-oss-distributions/adv_cmds/blob/main/ps/print.c#L444-L474).
- `leader_identity` requests start time and command for the recorded PID. Darwin's `ps` falls back to the process name when the argument read fails. During `command` registration, the parent still holds the child unreaped. During reconciliation, a changed start time identifies reuse. After any other identity result, a new PID, PGID and status snapshot determines whether the group departed. A remaining group stays unconfirmed. [Argument lookup](https://github.com/apple-oss-distributions/adv_cmds/blob/main/ps/print.c#L179-L185) and [fallback](https://github.com/apple-oss-distributions/adv_cmds/blob/main/ps/print.c#L284-L288).
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

## Original verified plants

plant drop-eperm-recheck: named assertion reached; red exit 1; restored; green exit 0.

plant accept-eperm-blindly: named assertion reached; red exit 1; restored; green exit 0.

plant ignore-ps-diagnostics: named assertion reached; red exit 1; restored; green exit 0.

Evidence: `/Users/ctm/Work/projects/tooling/agent-harness-plugins/770-killpg-eperm/.workmux/770/plant-run/results.json`.

## Review round 1

One local review, the Nit round. The review reported three Important findings. Finding 1, about potentially incomplete process listings, remains open by instruction.

- Finding 2. `stop_group` checks the active signal deadline after parsing the EPERM recheck and before confirming departure. The test advances the clock while parsing the snapshot. A separate test verifies that EPERM after SIGKILL accepts a timely exiting-only snapshot.
- Finding 3. After the leader identity lookup fails, reconciliation applies the same `ignore_exiting` rule. The tests confirm departure for exiting and zombie members and keep the group pending for either a live member or a `ps` diagnostic.

### Round 1 plant detectors

- Remove the post-parse deadline check. `test_eperm_refuses_snapshot_after_signal_deadline` detects the false departure.
- Remove `ignore_exiting` from the follow-up reconciliation snapshot. `test_reconcile_clears_exiting_group_after_leader_exit` detects the false pending group.

### Round 1 local checks

- `make build`, `make lint` and `make validate` each exited 0.
- `uv run --no-project tests/checked_plant_test.py -q -k eperm -k reconcile` exited 0 with 8 tests.
- Python unittest discovery via `uv run --no-project python` initially exited 1. The manifest inventory was the sole failure among 140 tests because it scanned local plant evidence under `.workmux`. All 140 tests exited 0 in a copy of the tracked tree with the fixes applied, using the default guard partitions. The round 1 evidence now lives under the inventory's existing `node_modules` exclusion.
- `uv run --script plugins/plant-defects/scripts/checked-plant` subcommands `run` and `render` each exited 0.
- The Scrut snapshot count increased from 50 to 54, verified against the Python behavior test list. Scrut was not run. The Python run excludes the scheduler test that invokes the Scrut wrapper with a stub.

### Round 1 verified plants

plant accept-late-eperm-snapshot: named assertion reached; red exit 1; restored; green exit 0.

plant count-exiting-reconciliation-members: named assertion reached; red exit 1; restored; green exit 0.

Evidence: `/Users/ctm/Work/projects/tooling/agent-harness-plugins/770-killpg-eperm/node_modules/.770-round1.9Ep95E/plant-run-final/results.json`.

## Review round 2

The second local review was at Important and reported one finding in the
approved process-state class. Both reconciliation snapshots now use the same
rule as signal cleanup. The existing stderr handling for the initial
snapshots and signal polling remains in
[the process inspection diagnostics issue](https://github.com/cboone/agent-harness-plugins/issues/771).

### Execution sites

Eight sites audited, six with changed behavior. The three `ps` invocations
and four `live_group` callers are listed individually, along with the shared
predicate. All eight are in `plugins/plant-defects/scripts/checked_core.py`.
`plugins/plant-defects/scripts/checked-plant` delegates supervision to
`checked_core` and has zero `ps` invocations or `live_group` callers.

| Site                               | Round 2 verdict                                                                                                                                                                 | Test or plant                                                                                                                                                                                                          |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `is_live_state`                    | Added. Leading `Z` and trailing `E` exclude a member. Duration in `E` plays no part.                                                                                            | `test_live_group_parses_state_and_flags_in_their_own_positions`, `read-exiting-as-leading-state` and `read-zombie-anywhere`.                                                                                           |
| `live_group` table `ps`            | Changed. Always applies the state rule. Guarded callers still reject stderr.                                                                                                    | `bypass-live-group-state-filter` and `ignore-guarded-ps-stderr`.                                                                                                                                                       |
| `leader_identity` PID `ps`         | Unchanged. Start time establishes reuse. The command, including `(sh)`, supplies identity data only.                                                                            | `test_group_identity_classifies_reuse_survival_and_unknown` and `treat-command-fallback-as-reuse`.                                                                                                                     |
| `stop_group` initial `live_group`  | Changed via the predicate. Skips signaling for a departed group.                                                                                                                | `signal-after-initial-departure`.                                                                                                                                                                                      |
| `stop_group` EPERM `live_group`    | Behavior preserved. Checks a fresh snapshot with clean stderr and the active deadline. Other permission errors reject cleanup.                                                  | `accept-eperm-without-recheck`, `ignore-guarded-ps-stderr`, `test_eperm_refuses_snapshot_after_signal_deadline`, `test_eperm_confirms_exiting_group_after_sigkill` and `test_eacces_refuses_even_if_group_has_exited`. |
| `stop_group` polling `live_group`  | Changed via the predicate. Polls while a live member remains and can stop once only departed members remain.                                                                    | `accept-live-poll` and `test_stop_group_polls_until_only_departed_members_remain`.                                                                                                                                     |
| `reconcile` initial table `ps`     | Changed. Excludes groups containing only departing members before identity lookup.                                                                                              | `count-exiting-in-initial-reconciliation`.                                                                                                                                                                             |
| `reconcile` follow-up `live_group` | Changed. Runs after both successful and failed identity reads when reuse has not been established. Clears an exiting-only group, keeps a live group pending and rejects stderr. | `skip-group-after-successful-identity`, `treat-command-fallback-as-reuse`, `skip-group-after-failed-identity` and `test_reconcile_refuses_unconfirmed_group_after_leader_exit`.                                        |

`test_normally_exiting_step_stops_its_group` and `test_term_ignoring_group_is_stopped`
cover whole-group signaling, normal polling and reaping.
`test_eperm_refuses_live_group_member` covers retaining the cleanup error after
the fallback signal. The reap subcase in
`test_failure_shapes_load_render_and_refuse_verification` covers an unconfirmed
exit when reap evidence is missing.
`test_reconciliation_refuses_survivors_and_unknown_identities` covers rejection
of live groups and clearance on PID reuse without signaling.
The pipeline polls owned subprocesses and uses their exit status, which
`test_pipeline_first_stage_failure` and `test_pipeline_timeout_and_capture_bound`
exercise. The fallback command spelling and operating-system behavior in the
exit race audit come from the linked Apple sources.

### Branch files

Seven files audited against `ca6a5e18`, five updated in round 2.

| File                                                          | Round 2 verdict                                                                                                                                       |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugins/plant-defects/scripts/checked_core.py`               | Updated. The execution-site table covers its liveness logic and documentation.                                                                        |
| `dist/codex/plugins/plant-defects/scripts/checked_core.py`    | Regenerated with `make build`. The mirror matches the canonical source byte for byte and carries the same coverage.                                   |
| `plugins/plant-defects/.claude-plugin/plugin.json`            | Unchanged. Retains the branch's patch bump and makes no liveness claim.                                                                               |
| `dist/codex/plugins/plant-defects/.claude-plugin/plugin.json` | Unchanged. Retains the corresponding generated patch bump and makes no liveness claim.                                                                |
| `tests/checked_plant_test.py`                                 | Added state and path coverage. Existing per-PID `ps` checks independently verify actual child teardown and do not make supervisor liveness decisions. |
| `tests/scrut/checked-plant.md`                                | Updated only the test count. The tracked Python discovery and the behavior selector confirm the count.                                                |
| `docs/reviews/2026-11-24-killpg-eperm-ledger.md`              | Updated. The execution-site table maps the liveness claims to detectors.                                                                              |

### Round 2 local checks

- `make build`, `make lint` and `make validate` each exited 0.
- `uv run --no-project tests/checked_plant_test.py -q -k live_group -k stop_group -k eperm -k reconcile`
  exited 0 with 14 tests. Direct behavior mode in the worktree exited 1
  because its manifest inventory picked up ignored `.workmux` evidence.
- `uv run --no-project python` unittest discovery in a copy of tracked files
  exited 0 with 146 tests. The snapshot matches the 60 behavior tests.
  Scrut and the Python scheduler case that invokes the Scrut wrapper were excluded.
- The first checked-plant `run` exited 1. A mocked call failure printed
  unrelated arguments that invalidated the intended red result. With the
  assertion reduced to the call count, `run` and `render` each exited 0.

<!-- checked-plants:start -->

## Verified plants and controls

plant bypass-live-group-state-filter: named assertion reached; red exit 1; restored; green exit 0.

plant read-exiting-as-leading-state: named assertion reached; red exit 1; restored; green exit 0.

plant read-zombie-anywhere: named assertion reached; red exit 1; restored; green exit 0.

plant signal-after-initial-departure: named assertion reached; red exit 1; restored; green exit 0.

plant accept-live-poll: named assertion reached; red exit 1; restored; green exit 0.

plant accept-eperm-without-recheck: named assertion reached; red exit 1; restored; green exit 0.

plant ignore-guarded-ps-stderr: named assertion reached; red exit 1; restored; green exit 0.

plant count-exiting-in-initial-reconciliation: named assertion reached; red exit 1; restored; green exit 0.

plant skip-group-after-successful-identity: named assertion reached; red exit 1; restored; green exit 0.

plant treat-command-fallback-as-reuse: named assertion reached; red exit 1; restored; green exit 0.

plant skip-group-after-failed-identity: named assertion reached; red exit 1; restored; green exit 0.

Evidence: `/Users/ctm/Work/projects/tooling/agent-harness-plugins/770-killpg-eperm/node_modules/.770-round2.jcXuuq/plant-run-final/results.json`.

<!-- checked-plants:end -->
