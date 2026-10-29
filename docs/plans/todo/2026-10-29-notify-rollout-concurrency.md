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
- Validation and review results are recorded below.

## Cause and selected fix

Diagnostic CI run 40958083851, job 123743437288, records both readers entering
the `first` branch, with only `first` on disk and both statuses 1. Neither
reader entered `second`. This is the uutils mkdir double-success race already
established by issue 677, rather than evidence of slow scheduling alone.

TOOLING selected the structural fix: FIFO ready/release synchronization and
exclusive file claims at the existing hashed paths. The existing
`plugins/workmux/scripts/owner-lock.bash` uses Bash noclobber plus descriptor
identity and release tracking. Rollout claims are permanent, never released
and contain no PID data, so this change matches its exclusive-create idiom
without copying its ownership and release machinery into notify. Existing
directory markers remain valid; new claims are empty regular files. Claim
errors retain filesystem stderr. Notify advances from 4.4.0 to 4.4.1.

The FIFO endpoints stay open in the parent while both readers run, so ready
reads and release reads have bounded waits and release writes cannot block on
opening an endpoint. Each reader has a distinct release FIFO. Both process
statuses are collected before cleanup.

| Planted defect                  | Instrument                | Actual result      | Regression coverage |
| ------------------------------- | ------------------------- | ------------------ | ------------------- |
| Disable exclusive creation      | Concurrent-reader case    | Exit 1; two alerts | `concurrent`        |
| Reject historical directories   | Historical directory case | Exit 1             | `legacy-claim`      |
| Discard claim filesystem stderr | Claim failure case        | Exit 1             | `claim-error`       |

## Validation and review stop

- Fixed tree: all 22 cases in the rollout document pass. ShellCheck and shfmt
  pass on the changed Bash files. Generated mirrors rebuilt. Another 20 local
  concurrent pairs pass. These local runs alone do not satisfy the brief's
  before/after stress requirement; repeated green CI remains pending.
- All three plants fail; restoring the original implementation makes their
  controls pass. Plant logs are under `/tmp/notify-686-worker/plant-*.log`.
- An earlier document run overlapped a fixture edit and failed with shell EOF;
  that run is invalid and superseded by the complete 22-case passing run.
- Structural Nit round attempted: anti-patterns and report-only simplify,
  through fresh read-only `codex exec`, gpt-6.1-sol, high, window 872000.
  Both reported `timed out negotiating with the code-mode host` before any
  completed review. The brief requires stopping without fallback. Recorded
  process IDs 22767 and 22770 were stopped and reaped, both exit 143. No review
  findings or clean result exist; round completion remains pending.
- Review artifacts: `/tmp/notify-686-worker/structural-review/`. No lasting
  working-tree changes were found after stopping reviewers. No fallback or
  retry was attempted. Remaining review steps, Semgrep baseline, lint-and-fix,
  version validation, `make test-all` and final CI remain pending.
- Local fix is signed commit `7d18c56e`; PR 687 still has diagnostic head
  `f08171fd`. Do not merge it. TOOLING receives the stop and chooses resumption.

## Resumed local review

TOOLING reported the host available and resumed the original full review order.
The earlier host failures remain failed, not clean rounds. A later full-aspect
attempt was interrupted by the worker after a broad log search matched quoted
timeout history in this ledger. No runtime host error occurred in that attempt.
Its processes were stopped and reaped, artifacts preserved as incomplete, and
the pending Nit round restarted. Runtime error detection now checks anchored
runtime ERROR lines rather than quoted history.

Structural loop, completed Nit round: anti-patterns plus report-only simplify,
fresh read-only Codex, gpt-6.1-sol/high/872000. Simplify covered all four cleanup
angles inline with zero findings. Anti-patterns found one Nit: the failure
diagnostic listed only directories, omitting new file claims. Our severity is
Nit; take, include both formats; no further round for a test-only diagnostic
edit. Ended: fixes changed no behavior. Snapshots found no lasting review edits.

Full aspect loop, completed Nit round: code, errors, tests and comments, same
read-only settings; types skipped because no types or schemas changed. Every
aspect completed and validated; snapshots found no lasting review edits.

| Reviewer label                                                  | Our severity and impact                                            | Take or record                                                                           | Review again                    |
| --------------------------------------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- | ------------------------------- |
| Important: readiness timeout loses diagnostics                  | Important: missing reader arrival exits silently and removes state | Take: report arrival phase, identities and both reader statuses; add missing-reader case | No: test-only code and coverage |
| Suggestion: legacy zero-alert assertion races detached delivery | Nit: compatibility test could pass before a duplicate arrives      | Take: run through child capture before asserting no alert                                | No: test-only boundary fix      |

Code and comments had zero findings. Full loop ended: fixes changed no behavior,
under the tests-only advancement rule. No reviewer severity downgrade or design
change was needed. Both findings concern distinct mechanisms from the earlier
structural listing defect. Fixes are signed in `3ec7f859`.

The revised document passes all 23 cases. Additional plants: removing the
readiness-phase diagnostic fails `concurrent-timeout`; deliberately dispatching
despite a historical directory fails `legacy-claim` after captured child output
closes. Restored controls pass. Logs: `plant-timeout-diagnostic.log` and
`plant-legacy-delivery.log` in the evidence directory.

Trims: one read-only Codex round per skill, gpt-6.1-sol/low/872000, both completed.
Text proposed no changes. Two comment rewrites taken; the proposed removal of
the reason for keeping FIFO endpoints open was set aside to preserve the
non-obvious nonblocking guarantee. No behavioral edits.

Artifacts remain under `/tmp/notify-686-worker/`: `structural-resumed`,
`full-review` (interrupted), `full-review-resumed` and `trims`.

## Baseline scan and version check

Baseline Semgrep ran in the disposable shared clone
`/tmp/notify-686-worker/semgrep-clone`, verified at `65132fc2`, with
`SEMGREP_REPO_NAME=cboone/agent-harness-plugins`, `--config auto` and
`--baseline-commit 7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71`. Exit 0:
54 rules, four changed targets, zero findings and zero parser errors, about
100% parsed lines. Six paths were excluded by Semgrep ignore rules, including
test fixtures; the changed Bash fixtures pass ShellCheck. With no current
findings the native baseline engine skipped its second checkout. No baseline
checkout touched the worker tree. Artifacts: `semgrep.json`, `semgrep.log` and
`semgrep-clone.log` in the evidence directory.

The check-versions skill confirmed default branch `main`, unchanged merge base
after fetching it, matching canonical Claude/Codex manifests at 4.4.1 versus
4.4.0 at the base, and unchanged notify registration with versions owned only
by manifests. Repository-wide registration validation runs in `make test-all`.

Lint-and-fix runs with `--no-push`. Project policy protects Scrut snapshots
from reformatting, so broad Markdown and Prettier fix commands are downgraded
to their verified check commands. Scoped formatting covers changed Bash and
the process record; mechanical lint failures remain a required stop if they
cannot be resolved in scope.

## Final local verification

Lint-and-fix completed successfully with no code fixes required. Markdownlint,
Prettier, ShellCheck, shfmt and actionlint all passed. `make test-all` then
completed with all validators and all 52 Scrut documents passing: 1,826 cases,
zero failures and zero skips. This includes rollout (23 cases), notification
failures and environment isolation. Log: `/tmp/notify-686-worker/test-all.log`.

Only unpushed history is tidied above the published diagnostic commit
`f08171fd`, with a pre-tidy backup and exact-tree comparison. Pushed history
remains unchanged. Final hosted CI is pending; TOOLING receives its observed
results and merges, never this worker. No hook files or live configuration
changed.
