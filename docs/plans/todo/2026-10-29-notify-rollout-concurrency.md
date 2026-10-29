# Notify rollout concurrency flake

Scope: fix the concurrent rollout delivery test for issue 686. Hooks and live
configuration stay outside this work. TOOLING receives reports and merges the PR.

1. Publish temporary per-reader claim stderr, timing and filesystem diagnostics
   in an early PR, as the brief requires. Collect both reader statuses before
   cleanup. Establish the cause on CI or through a failing local reproduction.
2. Correct the cause and remove temporary diagnostics. Prefer a deterministic
   ready/release handshake over extending a scheduling timeout. Change the
   watcher only if evidence identifies a watcher defect.
3. Demonstrate stability with repeated CI passes or local stress that reproduced
   the original defect. Plant a guarded defect for new boundary coverage.
4. Run the full local review order, baseline Semgrep in a disposable clone,
   version checks and `make test-all`. Preserve pushed history. Report the ready
   PR and review ledger to TOOLING; never merge.

## Prior art

The repository's `tests/fixtures/ledger-concurrency` and
`ledger-reservation-barrier.bash` coordinate real processes using a ready FIFO
and one release FIFO per writer. This provides explicit arrival and release
without depending on two processes reaching a polling barrier within three
seconds. The resource-claims interleave fixtures instead use ready/release
files with bounded polls. Reuse the FIFO approach if synchronization is the
cause, rather than adding a new helper or tool.

## Evidence and review ledger

- Issue and TOOLING's CI comparison read in full. Passing and failing jobs have
  identical notify sources; claim stderr is currently suppressed.
- Initial diagnostics retain both reader statuses before cleanup, and record
  every intercepted mkdir, barrier arrivals and release, and failure filesystem
  state. No plugin content changes yet, so no version bump applies yet.
- Reviews, stress results, Semgrep, lint and final CI: pending.
