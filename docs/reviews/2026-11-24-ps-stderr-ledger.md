# Process listing failures during group cleanup

Stacked base `179e3582`. The [prior liveness audit](2026-11-24-killpg-eperm-ledger.md)
identifies the process inspection sites. A diagnostic, nonzero exit, or
unparseable row invalidates its listing before it can establish departure.

| Site                               | Disposition and coverage                                                                                                                                                                                                                                               |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `is_live_state`                    | Preserves the existing status interpretation. `test_live_group_parses_state_and_flags_in_their_own_positions` covers leading zombie states and trailing exit flags.                                                                                                    |
| `process_rows`                     | Parses both numeric columns for every row before either caller can accept absence. The stop and reconciliation process table tests cover missing columns and malformed PID and PGID values.                                                                            |
| `live_group` table `ps`            | Requires clean stderr and zero exit. The stop and reconciliation process table tests cover failure and clean departure.                                                                                                                                                |
| `leader_identity` PID `ps`         | Requires clean stderr, zero exit, and a parseable start time and command. `test_reconciliation_requires_reliable_leader_identity_for_reuse` covers empty and malformed identities, diagnostics with and without a replacement identity, nonzero exit, and clean reuse. |
| `command` leader registration      | Uses the same identity check and existing registration error handling. Registration supplies identity for later reconciliation.                                                                                                                                        |
| `stop_group` initial `live_group`  | Rejects a failed listing through the existing cleanup error path.                                                                                                                                                                                                      |
| `stop_group` polling `live_group`  | Keeps the last observed members and returns a cleanup error when a listing fails.                                                                                                                                                                                      |
| `stop_group` EPERM `live_group`    | Uses the unconditional check and retains the existing signal deadline. `test_stop_group_requires_reliable_process_table` covers all three stop paths.                                                                                                                  |
| `reconcile` initial table `ps`     | Rejects a failed snapshot before changing any pending group.                                                                                                                                                                                                           |
| `reconcile` leader lookup          | Records an inspection failure and requires a fresh, reliable group snapshot to clear a pending group.                                                                                                                                                                  |
| `reconcile` follow-up `live_group` | A failed snapshot leaves the group pending. `test_reconciliation_requires_reliable_process_table` covers both group snapshots.                                                                                                                                         |

The generated Codex copy carries the same three readers. The two standalone
PID `ps` calls in `tests/checked_plant_test.py` are teardown assertions.
The delayed `ps` fixture forwards to the runtime reader and exercises its
deadline. The launch-analysis fixture in `tests/checked_timeout_budget_test.py`
contains a `ps` source string and performs no inspection.

## Local checks

- `make build`, `make lint`, and `make validate` each exited 0.
- The version and snapshot count audit exited 0. All 61 marketplace entries
  passed. The canonical and generated manifests agree at 1.3.2, up from 1.3.1
  on the stacked base. The snapshot count matches the 63 behavior cases.
- `uv run --no-project tests/checked_plant_test.py -q -k requires_reliable`
  exited 0 with three tests.
- The first tracked-tree Python run exited 1. The reconciliation fixture
  omitted captured stderr. After that fixture supplied an empty captured
  stderr, its targeted test and the full tracked-tree rerun exited 0. The
  rerun passed 149 tests across five modules with the default guard partitions.
- The checked-plant `run` and `render` commands both exited 0. The evidence
  records each detector's failure and restored pass.
- Scrut was excluded, including the Python scheduler case that invokes it
  with a stub.

## Initial verified plants and controls

plant ignore-live-group-stderr: named assertion reached; red exit 1; restored; green exit 0.

plant ignore-reconciliation-stderr: named assertion reached; red exit 1; restored; green exit 0.

plant ignore-leader-stderr: named assertion reached; red exit 1; restored; green exit 0.

plant ignore-live-group-exit: named assertion reached; red exit 1; restored; green exit 0.

plant ignore-reconciliation-exit: named assertion reached; red exit 1; restored; green exit 0.

plant ignore-leader-exit: named assertion reached; red exit 1; restored; green exit 0.

plant ignore-malformed-member: named assertion reached; red exit 1; restored; green exit 0.

plant ignore-malformed-group: named assertion reached; red exit 1; restored; green exit 0.

plant ignore-malformed-table-row: named assertion reached; red exit 1; restored; green exit 0.

plant ignore-malformed-leader-time: named assertion reached; red exit 1; restored; green exit 0.

Evidence: `/Users/ctm/Work/projects/tooling/agent-harness-plugins/771-ps-stderr/node_modules/.771-plants.3B5Ecs/run/results.json`.

## Review round 1

The review of `2e03f8fc` found three Important issues. All three fixes change
behavior. The macOS state codes observed in local checks need a design decision
before confirmation review.

- `process_rows` rejects malformed state fields before either group reader can
  conclude that a process group has departed. The test covers the exact
  leading letters, allowed suffixes and malformed states including `Zgarbage`.
  The accepted state letters come from both manuals. The requested suffixes
  exclude Apple's legacy FIFO page replacement flag `S`, which the current
  Apple formatter does not emit. [Apple ps(1)][apple-ps], [procps ps(1)][linux-ps],
  [Apple state formatter][apple-state].
- `leader_identity` parses the five `lstart` fields with `time.strptime`. The
  reconciliation test keeps the group pending for `Nov 99`, and a direct test
  accepts the space-padded day in `Nov  4`.
- `ps_environment` removes `LINES` and `COLUMNS` for all three `ps` calls while
  retaining `LC_ALL=C` and `TZ=UTC` for the leader lookup. The fake observes
  the initial table, leader and follow-up table environments with both display
  settings present in the caller.

### Round 1 local checks

- `make build`, `make lint`, and `make validate` each exited 0.
- Seven focused Python tests exited 0. The behavior snapshot now counts 66
  cases.
- The tracked-tree Python run exited 1 across 152 tests. The suite reported
  `ValueError: unreadable process state: ?` in live group inspection and
  reconciliation. Across 60 separate snapshots, stock macOS `ps` returned
  two `?` rows and one `?+` row. A subsequent isolated run of
  `test_good_action_runs_once` exited 1 after a `?E` row invalidated the group
  listing. The required allowlist rejects all three forms. Scrut and the
  Python scheduler case that invokes its stub were skipped.
- The initial checked-plant run exited 1 because the environment assertion
  printed the subprocess mapping, which tripped a verdict exclusion. The
  assertion now reports only the display variable names. The rerun and
  `checked-plant render` each exited 0.

[apple-ps]: https://github.com/apple-oss-distributions/adv_cmds/blob/main/ps/ps.1
[linux-ps]: https://man7.org/linux/man-pages/man1/ps.1.html#PROCESS_STATE_CODES
[apple-state]: https://github.com/apple-oss-distributions/adv_cmds/blob/main/ps/print.c

<!-- checked-plants:start -->

## Verified plants and controls

plant accept-malformed-state: named assertion reached; red exit 1; restored; green exit 0.

plant accept-impossible-leader-date: named assertion reached; red exit 1; restored; green exit 0.

plant inherit-display-dimensions: named assertion reached; red exit 1; restored; green exit 0.

Evidence: `/Users/ctm/Work/projects/tooling/agent-harness-plugins/771-ps-stderr/node_modules/.771-round1-plants.dRkCz2/run/results.json`.

<!-- checked-plants:end -->
