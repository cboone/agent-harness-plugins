# Scrut runner process-group review ledger

## Scope and design

Issue [697](https://github.com/cboone/agent-harness-plugins/issues/697), base
`5205fada80635f7d9dd4a1967c94a256e60a99cb`. TOOLING approved core Perl POSIX
child-only setup after seeing the native reproduction. Keep cancellation,
tool stderr and exit status; do not filter diagnostics or change live config.
No plugin content changes, so no plugin version bump applies.

## Cause evidence

Native C probe on macOS 26.7.1, Darwin 25.6.0: for each of 1,000 iterations,
create a pipe and fork. Parent calls `setpgid(child, child)`; child calls
`setpgid(0, 0)` and writes its result, errno and `getpgrp() == getpid()` to
the pipe, then exits. Parent reads the record and waits. Neither process execs.
Result: 16 child `EPERM`, two parent `EPERM`, 63 parent `ESRCH` after child
exit, zero children outside the intended group. This confirms concurrent
double setup, rather than a parent after-exec race.

A DYLD interposer delaying the child by `usleep(100000)` made the parent call
succeed first and the child call succeed second. One exploratory interposer
using `dlsym(RTLD_NEXT, "setpgid")` returned exit 139; replacing that lookup
with the original symbol call made the probe valid. The failed probe provides
no cause evidence. Sources and binaries are under `/tmp/issue697-probe/`;
the regression tests require no compiler or interposer.

The committed Perl probe wraps the actual POSIX call. Its race mode returns
`EPERM` when the process is already its own group leader. This deterministically
models the failing redundant call. Exact probe-call output proves the fixture
ran. Successful setup checks the real group. Error modes return Perl's
actual failure shape, `undef`, with `EPERM` or `EACCES`. The runner must stop
before exec in both cases. An exec mode selects a missing executable; a wait
mode holds the leader before group setup for cancellation coverage.

## Plants

| Planted defect                                     | Instrument                         | Measured result                                                      | Regression coverage                                   |
| -------------------------------------------------- | ---------------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------- |
| Restore Bash job control around launches           | Redundant-call probe               | 24 passed, 6 failed; both intended race cases failed                 | Single and parallel group cases                       |
| Compare undefined POSIX result numerically to zero | Setup error cases                  | 29 passed, 1 failed; setup errors incorrectly ran the tool           | Genuine group setup failures                          |
| Remove leader signal before group signal           | Startup cancellation case          | 29 passed, 1 failed; tool ran after cancellation                     | Stop a leader before group setup                      |
| Disable the probe's redundant-call rejection       | Probe positive control             | 30 passed, 1 failed; control reported accepted redundant setup       | Confirm the race probe rejects a redundant setup call |
| Remove the inherited-monitor guard                 | Race probe with exported SHELLOPTS | 30 passed, 1 failed; expected tool exit 7 became setup EPERM, exit 1 | Single-document group with inherited monitor mode     |

### Signal plants

| Planted defect               | Instrument                    | Measured result                                      | Regression coverage                                 |
| ---------------------------- | ----------------------------- | ---------------------------------------------------- | --------------------------------------------------- |
| Remove INT/QUIT restoration  | Signal-default stub           | 32 passed, 1 failed; ignored INT/QUIT traps appeared | Restore interrupt signal defaults before exec       |
| Remove the stub's trap query | Signal probe positive control | 32 passed, 1 failed; ignored traps were missing      | Confirm the signal probe exposes ignored interrupts |

## Review rounds

Correctness and simplify reviews use fresh read-only Codex contexts,
`gpt-6.1-sol`, high effort and
872000 context window. Scope snapshot for the first rounds:
`e3204e8dd4d2ec13983e7991cca628231d12f74a`.

- Structural Nit round: anti-pattern review completed with zero findings;
  report-only simplify completed with zero suggestions, using its inline
  four-angle fallback. Neither edited files. Runtime tests were deliberately
  unrun in reviewers; the parent owns their evidence.
- A preliminary simplify invocation ran before its prompt file existed and
  returned an unscoped `code` reply. Rejected as incomplete; no review coverage.
  The scoped simplify run completed and passed schema and snapshot validation.
- Aspect Nit round: code, errors, tests and comments all completed, zero findings.
  Types skipped because no type definitions changed. Reviewer GitHub queries
  could not reach the API; the parent had verified active, non-fork ownership
  and absence of an open PR outside the sandbox.
- Author validation after these replies found exported `SHELLOPTS` imports
  monitor mode. Reproduction: `bash -c 'set -m; export SHELLOPTS; exec "$@"'`
  launching the runner under the race probe gave setup `EPERM`, exit 1,
  rather than the stub's exit 7. Reviewer label: author validation, no tool
  label. Assessed severity: Important, because an inherited shell option
  restores the reported failure. Take: explicitly disable monitor mode and
  exercise this input in the single-document race case. Review again: yes,
  behavior changes; continue both loops at Important without resetting counts.
- Structural Important round: anti-pattern and report-only simplify completed
  with zero findings. Aspect Important round: code, errors, tests and comments
  completed with zero findings. Both loops ended clean at Important on snapshot
  `5ba339390952fd7879d55aa20ab5f4c9252ac6ff`. No further round is needed because
  neither round took a finding or changed behavior.
- Trim round: fresh read-only `gpt-6.1-sol`, low effort, 872000 window.
  Comment trim completed with no proposals. Prose trim completed with five
  proposals; took three wording changes. Kept the explicit success of both
  serialized probe calls and the outcome-first review conclusion. No code,
  test commands or snapshots changed.
- Final validation required the shared environment reset to remain the first
  executable entry. Moved the monitor guard immediately after that reset.
  Native tracing showed the reset's children join its existing group, then the
  worker establishes its own group once. No worker behavior changed. Focused
  checks passed all 31 cases; removing the relocated guard failed only the
  intended inherited-monitor case, 30 passed and one failed. Guard restored.
  TOOLING accepted the ordering correction; this check fix adds no review round.
- A conductor warning during the first full run prompted a signal probe.
  Reviewer label: conductor warning and author validation, no tool label.
  The current runner passed ignored `SIGINT` and `SIGQUIT` dispositions into a
  stub (`trap -p INT QUIT` printed both); the original base runner printed
  neither. Assessed severity: Important, because interrupt handlers in test
  children cannot run. Take: reset both signals to default in the Perl child,
  add a stub signal probe and plant. Review again: yes, continue both loops at
  Important 2. TOOLING approved the design. This is a signal-contract defect,
  distinct from the earlier group-creation race.
  Important 2 completed on the signal correction: anti-pattern and report-only
  simplify reported zero findings; code, errors, tests and comments all passed
  validation with zero findings. Both loops ended clean at Important after
  one Nit and two Important rounds, snapshot
  `72d9bed9d70563ca6723369a66db92582bac7116`. No Critical round follows because
  the last rounds took no findings and changed no behavior.
- Final signal-delta comment and prose checks completed in fresh read-only
  `gpt-6.1-sol` contexts at low effort, 872000 window. Both returned the complete
  classified file lists and no proposals; no further edits.

## Unfinished full run

The first locked sequence used `SCRUT_JOBS=2`. Standard `make test-all` stopped
at the known fixture lint failure before tests, then one full Scrut run started.
TOOLING stopped this run because the signal correction changes the tested tree.
Recorded driver PID 25185, make PID 45279 and runner PID 45282 before sending
`SIGTERM` to runner 45282. The runner stopped its workers; make and the driver
exited and the EXIT trap released the owned lock. No other worker was stopped.
46 of 56 documents finished; only environment-isolation reported a failure.
No final Scrut summary or full-suite pass: the run is stopped unfinished.
Preserved its logs separately before the final run overwrites the active log.
TOOLING authorized runner and codex-aspects checks in the foreground, Important 2
reviews, and one complete locked full suite on the corrected tree before push.

## Semgrep and lint

Baseline Semgrep 1.180.0 ran with `--config auto --baseline-commit
5205fada80635f7d9dd4a1967c94a256e60a99cb` in an owned disposable shared clone,
with `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`. It ran 51 rules over four
changed files: zero findings, approximately 99.9 percent parsed. One
`PartialParsing` warning covers the `:-` token in the pre-existing `${!:-}`
expression, baseline line 87. Tests and the Perl probe were ignored by default.
No claim of complete Semgrep coverage. TOOLING accepted the documented parser
limit with a confirmed ShellCheck pass on the runner. The ordering rescan again
reported zero findings and the same token at line 102, columns 14 to 16. Signal
correction rescan also reported zero findings with the same token at line 104,
columns 14 to 16. Current runner and stub pass ShellCheck; the documented parser
limit remains accepted, without a claim of complete Semgrep coverage.

`lint-and-fix --no-push`: changed Bash and process docs were formatted with
shfmt, Markdown lint fixes and Prettier. Global fixers were restricted because
Scrut snapshots must not be reformatted and the known fixture defect is outside
scope. Global Markdown, Prettier, ShellCheck and shfmt passed. `make lint`
failed only the known rooted-operand checks in
`tests/fixtures/review-submodule-fixture` at lines 132 to 134 and 254.
TOOLING authorized a ready PR with this and the known environment-isolation
failure disclosed. No baseline fixture edits.

## Validation

- Focused runner Scrut: 33 testcases passed, zero failed or skipped, including
  both signal cases. All seven distinct plants were caught and restored.
- Foreground `codex-aspects.md`: all 83 testcases passed after signal restoration,
  including interrupt behavior. No full-suite pass is inferred from this check.
- ShellCheck, shfmt and Perl syntax: passed on changed code.
- Pinned Yarn dependencies: installed with `corepack yarn install --immutable`.
- macOS system Perl: core POSIX group setup succeeded.
- `make validate`: passed JSON, environment-reset, manifests, catalog, references
  and generated-mirror checks after the ordering correction.
- `check-versions`: verified remote default `main` and merge base, all changed
  paths and marketplace/manifest validation. No plugin content changed, so no
  plugin version bump applies; the runner has no separate version surface.
- After signal restoration: `make validate`, global Markdown, Prettier,
  ShellCheck and shfmt pass. Repository lint still fails only the accepted
  fixture rooted-operand checks. No new lint failures.
- Complete corrected-tree full suite on `389361b1`, under the atomic shared lock
  with `SCRUT_JOBS=2`: 55 of 56 documents passed; 1,888 of 1,889 testcases passed,
  one failed, zero skipped. The only failing assertion is
  `environment-isolation.md:39`, reporting the unchanged fixture rooted-operand
  defects at lines 132 to 134 and 254. Runner 33 and codex-aspects 83 cases passed
  in this full run. No new failures or unrun documents.
- Standard `make test-all` exited 2 at the accepted fixture lint failure before
  Scrut; the separately invoked complete `make test-scrut` exited 2 solely for
  that known assertion. Both commands ran in the foreground under one owned
  lock, which the EXIT trap released. No full-suite pass is claimed.
- Source, Makefile, test stub, Perl probe and runner test document remain
  byte-identical to the complete tested tree. Only process records change for
  the publication handoff. Exact-tree signed tidy and publication follow.
