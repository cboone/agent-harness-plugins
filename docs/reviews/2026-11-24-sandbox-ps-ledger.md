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
- **Linux procfs.** `/proc/<pid>/stat` includes group, state, flags, thread
  count and start ticks. The parser splits after the final closing delimiter
  because the process name can contain parentheses and newlines. It treats
  `Z`, `X`, legacy `x` and `PF_EXITING` as departed when no other threads
  remain. The kernel reports these fields for the thread-group leader, which
  can exit before the other threads. [Linux procfs stat][linux-stat] and
  [Linux flags][linux-flags].

The trust boundary is in the checked runner reference. Registration and
reconciliation both use the same platform-tagged start time. Legacy records
without that format cannot establish reuse. Reconciliation still confirms
group absence through a fresh read when leader identity is unavailable.

The new reader removes the subprocess scan described by the
[checked-gate load issue][gate-issue] from the same cleanup path.
The original load case and cleanup-error test in that issue were not replayed.
The existing cleanup error handling and fixed fingerprint budget remain in
place, so this branch does not close that issue.

## Behavioral sites and detectors

- Darwin record layout, zombie state, exit flag, unknown state and failed
  syscall, including `ENOMEM` retry.
- Linux stat layout, zombie and dead states, exit flag, live threads, unknown
  state, unreadable stat, hidden procfs and confirmed PID disappearance.
- Snapshot dispatch, visibility check and deadline enforcement.
- Group member selection, leader identity lookup and start-time comparison,
  and reconciliation's initial and follow-up snapshots.

## Sandbox proof

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

## Local checks

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

## Defect plants

Each variant used `uv run --offline --python <interpreter> --script <checked-plant> run`
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
[linux-flags]: https://github.com/torvalds/linux/blob/v6.12/include/linux/sched.h
