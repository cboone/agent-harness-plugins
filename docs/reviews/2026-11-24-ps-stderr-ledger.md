# Process listing failures during group cleanup

Stacked base `179e3582`. The [prior liveness audit](2026-11-24-killpg-eperm-ledger.md)
identifies the process inspection sites. A diagnostic, nonzero exit, or
unparseable row invalidates its listing before it can establish departure.

| Site                               | Disposition and coverage                                                                                                                                                                                                                                               |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `is_live_state`                    | Confirms departure only for a well-formed zombie or exiting state. The live group tests cover recognized states, unknown macOS states and malformed zombie states.                                                                                                     |
| `process_rows`                     | Requires three fields and parses both numeric columns. The stop and reconciliation tests cover missing columns and malformed integers. `test_live_group_ignores_unrelated_unknown_state` covers accepting an unrelated row with an unknown state.                      |
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

## Review round 1 part 2

Stock macOS emits `?`, `?+` and `?E`. Rejecting these states while parsing the
system-wide listing prevented valid checks from completing. `process_rows`
requires three fields and integer PID and PGID fields. `is_live_state` treats an
unknown or malformed state as live. It confirms departure only for a state
matching `[DIRSTtUWXZ][<>+AELNsVWXl]*` with a leading `Z` or a trailing `E` flag.
`live_group` checks liveness for target-group rows, so unrelated unknown rows
leave its result intact. Reconciliation shares the same state interpretation.

### Part 2 verified plants

plant drop-well-formed-state-check: named assertion reached; red exit 1; restored; green exit 0.

Evidence: `/Users/ctm/Work/projects/tooling/agent-harness-plugins/771-ps-stderr/node_modules/.771-round1-part2.gbdmLh/drop-well-formed-state-check/results.json`.

plant restore-row-state-rejection: named assertion reached; red exit 1; restored; green exit 0.

Evidence: `/Users/ctm/Work/projects/tooling/agent-harness-plugins/771-ps-stderr/node_modules/.771-round1-part2.gbdmLh/restore-row-state-rejection/results.json`.

## Review round 2

`checked_core` trusts the system `ps` to emit its documented row format.
Rows must split into the expected fields. PID, PGID and start time fields must
parse. Both parsers rely on `ps` for semantic details such as status flag order,
ID signs and the weekday. Round 1's checks still apply.

- Finding 1, Nit. The reported flag order `S+E` is outside the output of the
  system formatters. Apple emits `E` before `+`, and procps has no `E` suffix.
- Finding 2, Nit. The negative PGID in the sample is outside the process table
  format for `pgid=`.
- Finding 3, Nit. The weekday and date in a real `lstart` field come from the
  same timestamp. The contradictory weekday requires fabricated output.
- Finding 4, Important, fixed. Runtime `ps` calls use `COLUMNS=10000`,
  `LINES=1000` and `stdin=subprocess.DEVNULL`. `launch` forwards `stdin` to
  `subprocess.run`. Procps 4.0.4 can still check `/dev/tty` when it has a
  controlling terminal. It applies the fixed dimensions before checking for a
  screen-size warning. [Procps screen sizing](https://github.com/procps-ng/procps/blob/v4.0.4/src/ps/global.c#L235-L278).

Width can change where `ps` truncates `command=`. Registration and
reconciliation both call `leader_identity` with the same fixed width and
`LC_ALL=C` and `TZ=UTC`. The width therefore applies equally to both sides of
`classify_leader`. A macOS probe returned matching 1,135-character commands
with different inherited dimensions, including a marker at the end of the
argument. [Procps column formatting](https://github.com/procps-ng/procps/blob/v4.0.4/src/ps/output.c#L2066-L2095).

### Environment warning audit

Six executable source sites were audited, three changed. The three changed
sites also appear in the generated Codex copy. Both the stacked-base diff and
the additional files in the `origin/main` merge-base diff were inspected.

| Site                                                                                                             | Verdict                                                                                                      |
| ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `checked_core.py`, `live_group` table                                                                            | Fixed dimensions and null stdin. Covers initial, polling and EPERM cleanup and the reconciliation follow-up. |
| `checked_core.py`, `leader_identity` PID                                                                         | Fixed dimensions and null stdin. Registration and reconciliation share this lookup.                          |
| `checked_core.py`, `reconcile` initial table                                                                     | Fixed dimensions and null stdin before any pending group is classified.                                      |
| Codex `checked_core.py`, `live_group` table                                                                      | Regenerated from the same checked source launch.                                                             |
| Codex `checked_core.py`, `leader_identity` PID                                                                   | Regenerated from the same checked source launch.                                                             |
| Codex `checked_core.py`, `reconcile` initial table                                                               | Regenerated from the same checked source launch.                                                             |
| `tests/checked_plant_test.py`, PID probe in `test_normally_exiting_step_stops_its_group`                         | Test-only teardown probe. Its output cannot affect the runtime's group records.                              |
| `tests/checked_plant_test.py`, PID probe in `test_term_ignoring_group_is_stopped`                                | Test-only teardown probe. Its output cannot affect the runtime's group records.                              |
| `tests/checked_plant_test.py`, delayed process table in `test_inspection_failure_retains_subprocess_diagnostics` | Passes the runtime options through to the process that execs `ps`. The fixture needs no separate options.    |

`checked-plant` delegates through `checked_core` and contains no direct `ps`
launch. The `ps` string in `tests/checked_timeout_budget_test.py` only feeds
source analysis. The other touched files contain no `ps` launches.

`test_ps_uses_fixed_dimensions_and_devnull` observes all three runtime sites
with both caller dimensions set to one. At each site, the plants independently
drop `COLUMNS`, `LINES` and null stdin.

### Round 2 local checks

- `make build` and `make lint` exited 0. The first `make validate` exited 2
  because the interactive width probe wrote a bytecode file in the plugin
  scripts directory. Removing that file and its empty directory restored
  `make validate` to exit 0.
- `uv run --no-project -m unittest discover -s tests -p '*_test.py' -q`
  exited 0 with 156 tests in five tracked modules using the default guard
  partitions. The scheduler case used the fixture stub. The Scrut suite was
  deferred to the full gate. The behavior snapshot expects 69 tests.
- Checked-plant `run` and `render` each exited 0.

### Round 2 verified plants

plant drop-live-group-columns: named assertion reached; red exit 1; restored; green exit 0.

plant drop-live-group-lines: named assertion reached; red exit 1; restored; green exit 0.

plant drop-live-group-stdin: named assertion reached; red exit 1; restored; green exit 0.

plant drop-leader-identity-columns: named assertion reached; red exit 1; restored; green exit 0.

plant drop-leader-identity-lines: named assertion reached; red exit 1; restored; green exit 0.

plant drop-leader-identity-stdin: named assertion reached; red exit 1; restored; green exit 0.

plant drop-reconcile-columns: named assertion reached; red exit 1; restored; green exit 0.

plant drop-reconcile-lines: named assertion reached; red exit 1; restored; green exit 0.

plant drop-reconcile-stdin: named assertion reached; red exit 1; restored; green exit 0.

Evidence: `/Users/ctm/Work/projects/tooling/agent-harness-plugins/771-ps-stderr/node_modules/.771-round2.4OMWGp/run/results.json`.
