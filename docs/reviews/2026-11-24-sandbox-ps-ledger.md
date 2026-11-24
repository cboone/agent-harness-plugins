# Native process inspection for checked plants

Base `a9bad10d`. The [sandbox issue][issue] follows the
[liveness audit](2026-11-24-killpg-eperm-ledger.md) and the
[process-listing audit](2026-11-24-ps-stderr-ledger.md).

## Source survey

- **Darwin sysctl.** `KERN_PROC_PGRP` supplies group rows, `KERN_PROC_PID`
  supplies a leader row, and `KERN_PROC_ALL` supplies the reconciliation
  snapshot. The XNU implementation visits active and zombie lists. LP64
  `kinfo_proc` contains PID, `e_pgid`, `p_stat`, `p_flag` and the start
  timeval. The SL-VF branch already uses this interface in
  `tests/process_snapshot.py`. This implementation reads only those fields
  and uses group selection for the cleanup poll. SDK compile-time assertions
  for the row layout and constants exited 0 on arm64 and x86_64. [XNU query][xnu-query] and [XNU layout][xnu-layout].
- **Darwin pgrep.** The installed `pgrep(1)` supports `-g` and emits PIDs,
  optionally with names. It supplies neither the state nor a comparable start
  time, so it would require a second reader.
- **Darwin libproc.** `PROC_PIDTBSDINFO` returns status, group, start time and
  a translated exit flag. Group listing through `proc_listpids` returns PIDs
  and would require a separate per-PID query for metadata. The sysctl returns
  those fields together and exposes `P_WEXIT` directly. [XNU libproc fields][libproc].
- **psutil.** The package exposes process status and creation time, and would
  add a native dependency. The kernel sources directly supply the needed
  fields on both supported platforms. [psutil process reference][psutil].
- **Linux procfs.** The stat reader takes group, state and start ticks. The
  parser splits after the final closing delimiter because the process name can
  contain parentheses and newlines. The reader checks task states for departure.
  [Linux procfs stat][linux-stat].

The trust boundary is in the checked runner reference. Registration and
reconciliation both use the same platform-tagged start time. Legacy records
without that format cannot establish reuse. Reconciliation still confirms
group absence through a fresh read when leader identity is unavailable.

The native reader replaces the external process listing described by the
[checked-gate load issue][gate-issue] from the same cleanup path.
The original load case and cleanup-error test in that issue were not replayed.
The existing cleanup error handling and fixed fingerprint budget remain in
place, so this branch does not close that issue.

## Behavioral sites and detectors

- Darwin record layout, zombie state, exit flag, unknown state and failed
  syscall, including `ENOMEM` retry.
- Linux stat layout, zombie and dead states, live and unknown states,
  unreadable stat, hidden procfs and confirmed PID disappearance.
- Isolated reader launch, output validation, visibility check and deadline
  enforcement.
- Group member selection, leader identity lookup and start-time comparison,
  and reconciliation's initial and follow-up snapshots.

## Round 1 review

- **Finding 1, Nit.** The Linux process snapshot can miss a child forked
  during enumeration, as could the previous `ps` snapshot. Whenever cleanup
  signals, `killpg` still targets the whole group. Accepted as a known limit.
- **Finding 2, fixed.** Linux classifies departure from the state field alone.
  The test's live-state records detect any return to flag-based departure.
- **Finding 3, fixed.** The supervisor runs the native reader through
  `launch()` with null stdin, an empty environment and a deadline. A hanging
  reader leaves membership unknown and cleanup still signals the group.
  A nonzero exit, stderr or invalid JSON also leaves membership unconfirmed.

### Round 1 sandbox proof

The replay used the same SL-VF profile generator and path identity helper
from `0e5c007fbc55`. The probe copy retained the original commands and added
a direct invocation of the isolated reader. The artifacts are in
`.workmux/issue-774/round1.DDkhcQ6I/`.

```bash
uv run --no-project --offline --python 3.13 python -B \
  .workmux/issue-774/round1.DDkhcQ6I/prove_sandbox.py
```

The probe exited 0. Under the generated sandbox profile, `/bin/ps` exited 71,
the reader child and its snapshot and identity probe each exited 0, and the
end-to-end `checked-plant` run exited 0. The retained receipt is
`sandbox-results.json`.

### Round 1 plants

Both `checked-plant run` and `checked-plant render` exited 0 for each variant.
The receipts are at `plants-checked/<variant>/run/results.json` under the round 1
artifact directory.

- `linux-flag-departure` made `test_linux_process_states` fail with exit 1.
  Restoring the source passed with exit 0.
- `in-process-reader` made `test_process_reader_timeout_fails_closed` fail
  with exit 1. Restoring the source passed with exit 0.

### Round 1 local checks

The first targeted Scrut invocation exited 2. The fake procfs readlink had
intercepted symlink resolution for the temporary directory, and the manifest
inventory included retained artifacts from earlier runs. The fixture now
intercepts only the procfs self link. Python and Scrut use a copy of the
tracked files, which excludes the retained artifacts.

The first two full Python invocations exited 1. The deadline guard required
the reader reap to call `remaining()`. The second Scrut invocation exited 2
because the reader could emit a resource warning if its reap budget elapsed.
The reader now delegates a delayed reap after signaling the child. The final
targeted Scrut invocation exited 0 with 70 behavior tests. `make build`,
`make lint` and `make validate` each exited 0.

```bash
bin/run-heavy-suite uv run --no-project --offline --python 3.13 python -B \
  -m unittest discover -s tests -p '*_test.py' -v
```

The final Python run exited 0 with 157 tests. On macOS, the Linux reader
checks used fixture procfs records.

## Round 2 Linux thread liveness audit

The review of `7a482da9` recorded one Important finding and zero Critical
findings. These are the 14 sites checked in the reader and its callers.

1. `darwin_rows` keeps the process-level `SZOMB` and `P_WEXIT` rules.
1. `linux_tasks_live` now requires a missing task directory or only
   `Z`, `X` or `x` tasks to confirm departure. An unreadable directory
   or task stat counts as live.
1. `linux_snapshot` uses that rule for each row in a table scan. It
   still drops an unreadable process stat only on confirmed PID disappearance.
1. The PID-specific `linux_snapshot` uses the same row reader and still
   requires the process stat for the PID's identity and group.
1. `live_group` filters by group and the reader's liveness result.
1. `stop_group` skips signals only when its initial group read returns no
   live members.
1. The issue 770 `EPERM` recheck after either signal requires a fresh,
   empty live-group read within the signal deadline.
1. Polling after either signal returns success when the live-group read is
   empty.
1. Reconciliation's initial snapshot marks a group absent only when it
   contains no live rows for that group.
1. `leader_identity` supplies the start time for registration and
   reconciliation from the row's identity fields.
1. Reconciliation's reused-PGID branch records the original group gone
   after a different comparable start time.
1. Matching or incomparable identities and unavailable identities all
   proceed to the fresh group read.
1. Reconciliation's fresh group read records absence only when it returns
   no live members.
1. Command finalization records a group gone only after successful group
   cleanup and leader reap. Its separate spawn-error branch uses launch
   failure as evidence.

The Darwin probe ran the test's Python child with libc `pthread_exit`.
During worker heartbeats, three `KERN_PROC_PID` reads returned `p_stat=2`
(`SRUN`) and `p_flag=0x4004`, with `P_WEXIT` clear. The probe exited 0,
and the child exited -9 after cleanup.

### Round 2 plants and sandbox

- Removing the live-task state check made `test_linux_process_states`
  fail on live worker states, exit 1. Restoring it passed, exit 0.
  `test_linux_task_read_failures` covers a missing or unreadable task
  directory and a missing task stat.
- Accepting the leader's `Z` state alone made
  `test_live_group_with_departed_linux_leader` fail on the group assertion,
  exit 1. Its zombie-leader and live-worker assertions passed first.
  Restoring the task check passed, exit 0. This test and plant require Linux
  procfs. The test runs in the checked-plant Scrut document on Ubuntu CI.

Both plants ran in disposable copies on Colima Linux `6.8.0-117-generic`
with its installed Python 3.12.3. Logs are in
`.workmux/issue-774/round2.z2tgHkd3/linux-plants.log`.

```bash
uv run --no-project --offline --python 3.13 python -B \
  .workmux/issue-774/round2.z2tgHkd3/prove_sandbox.py
```

The SL-VF profile generator and path identity helper matched `0e5c007fbc55`.
The replay exited 0. The subprocess exits were 71 for
`/bin/ps` and 0 each for the isolated reader, snapshot and identity probe,
and end-to-end `checked-plant`. The replay retained `sandbox-results.json`
in the round 2 directory.

### Round 2 local checks

- `make build`, `make lint` and `make validate` each exited 0.
- `make test-scrut SCRUT_TEST_DIR=tests/scrut/checked-plant.md` exited 0
  with 72 behavior tests. The procfs case was skipped on Darwin and passed
  separately on Linux.
- The first full Python discovery exited 1 because its fixture environment
  was unset. With `CHECKED_PLANT_BIN`, `CHECKED_GATE_BIN` and
  `CHECKED_PLANT_DETACHED_BIN` set to the copied tree's files, the rerun
  exited 0 with 159 tests and one Linux-only skip.

```bash
bin/run-heavy-suite uv run --no-project --offline --python 3.13 python -B \
  -m unittest discover -s tests -p '*_test.py' -v
```

## Initial sandbox proof

The remote-tracking ref and remote branch were absent. The local SL-VF branch
`fix/3-scrut-guard-writes` resolved to `0e5c007fbc55`. The probe compared the
worktree's profile generator and path identity helper to the same files from
that commit, then called `write_sandbox(account_home())` without changing its
rules or protected paths.

```bash
uv run --no-project --offline --python 3.13 python -B .workmux/issue-774/prove_sandbox.py
```

The probe exited 0. Its subprocesses each ran under the generated
`/usr/bin/sandbox-exec` command.

1. `/bin/ps -p 1 -o pid=` exited 71 with `Operation not permitted`.
1. `python -B -c <probe> <plugin-scripts>` exited 0. It found its own PID in
   a group query and the full snapshot, then compared two reads of its start
   time.
1. `uv run --offline --python <interpreter> --script <checked-plant> run plants.json result`
   exited 0. The one-variant receipt records the expected assertion exit 1 and
   restored exit 0. The real profile denies writes under the worktree. The
   runner used a private temporary directory outside the protected paths, which
   the probe removed. The receipt is retained at
   `.workmux/issue-774/sandbox-results.json`.

## Initial local checks

- `make build` and `make lint` exited 0. The version audit exited 0 and confirmed
  the canonical and generated manifests at 1.3.3, up from 1.3.2 on the base.
- `make test-scrut SCRUT_TEST_DIR=tests/scrut/checked-plant.md` exited 0 on
  the second run. The document ran 68 behavior cases.
- The first full Python run exited 1, and the first targeted Scrut run exited 2. The shared file-reader guard rejected direct procfs file reads, and two
  fixtures still used the previous command-based identity. Procfs now uses
  the shared reader and the fixtures use kernel start times. The six focused
  rerun tests exited 0.
- `uv run --no-project --offline --python 3.13 python -B -m unittest discover -s tests -p '*_test.py' -v`
  exited 0 with 155 tests in a copy of the tracked files. The macOS suite
  exercised the Linux reader with fake procfs data.
- The first `make validate` exited 2 when the reference checker treated the
  absolute procfs path as a skill link. The documentation wording correction
  validated successfully. A later concurrent run exited 2 because JSON
  fixtures were removed between discovery and validation. The final
  `make validate` ran after the suite and exited 0.

## Initial defect plants

These receipts record the initial implementation. The round 1 Linux plant
replaces the initial exit-flag and thread-count checks.
Each initial variant used `uv run --offline --python <interpreter> --script <checked-plant> run`
followed by `render`. All 21 run and render commands exited 0. Each variant's
manifest, patch, check, and `run/results.json` are under
`.workmux/issue-774/plants-final/<variant>/`.

<!-- checked-plants:start -->

## Verified plants and controls

plant accept-partial-darwin-record: named assertion reached; red exit 1; restored; green exit 0.

plant accept-invalid-darwin-start: named assertion reached; red exit 1; restored; green exit 0.

plant count-darwin-zombie: named assertion reached; red exit 1; restored; green exit 0.

plant count-darwin-exiting: named assertion reached; red exit 1; restored; green exit 0.

plant drop-unknown-darwin-state: named assertion reached; red exit 1; restored; green exit 0.

plant drop-darwin-growth-retry: named assertion reached; red exit 1; restored; green exit 0.

plant swallow-darwin-read-error: named assertion reached; red exit 1; restored; green exit 0.

plant accept-truncated-linux-record: named assertion reached; red exit 1; restored; green exit 0.

plant count-linux-zombie-and-dead: named assertion reached; red exit 1; restored; green exit 0.

plant count-linux-exiting: named assertion reached; red exit 1; restored; green exit 0.

plant discard-linux-live-threads: named assertion reached; red exit 1; restored; green exit 0.

plant drop-unknown-linux-state: named assertion reached; red exit 1; restored; green exit 0.

plant treat-hidden-linux-table-as-empty: named assertion reached; red exit 1; restored; green exit 0.

plant discard-unreadable-linux-pid: named assertion reached; red exit 1; restored; green exit 0.

plant accept-incomplete-snapshot: named assertion reached; red exit 1; restored; green exit 0.

plant accept-late-snapshot: named assertion reached; red exit 1; restored; green exit 0.

plant skip-group-member-filter: named assertion reached; red exit 1; restored; green exit 0.

plant accept-unrelated-leader: named assertion reached; red exit 1; restored; green exit 0.

plant treat-legacy-start-as-reuse: named assertion reached; red exit 1; restored; green exit 0.

plant clear-live-group-from-initial-snapshot: named assertion reached; red exit 1; restored; green exit 0.

plant skip-fresh-reconciliation-snapshot: named assertion reached; red exit 1; restored; green exit 0.

<!-- checked-plants:end -->

[issue]: https://github.com/cboone/agent-harness-plugins/issues/774
[gate-issue]: https://github.com/cboone/agent-harness-plugins/issues/754
[xnu-query]: https://github.com/apple-oss-distributions/xnu/blob/main/bsd/kern/kern_sysctl.c
[xnu-layout]: https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/sysctl.h
[libproc]: https://github.com/apple-oss-distributions/xnu/blob/main/bsd/kern/proc_info.c
[psutil]: https://psutil.readthedocs.io/stable/#process-class
[linux-stat]: https://github.com/torvalds/linux/blob/v6.12/fs/proc/array.c
