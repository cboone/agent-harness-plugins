# Codex cancellation cleanup

## Authority and scope

The 2026-10-27 Inbox go-ahead for the tooling cancellation workstream authorizes
building through a ready PR with green checks; merging remains excluded.
TOOLING subsequently authorized the documented worktree dependency setup and
continuation. `corepack yarn install --immutable` succeeded.

Each Codex run gets a Bash process group. Cleanup repeatedly signals recorded
groups, escalates from TERM to KILL, and checks for active members. Launch
registration defers cancellation until the group is recorded. Repeated TERM or
INT cannot interrupt cleanup. Failed inspection retains artifacts and exits 4.
The invocation reference documents deliberate group/session escapes and
uncatchable stops of the helper.

## Validation

- Focused scrut document: 81 cases passed on macOS with Bash 5.3.
- Bash 3.2 cancellation subsets: repeated TERM, repeated INT and the launch boundary passed.
- `make build` passed. Pinned project Prettier runs after dependency setup.
- Publication gate: PR CI must pass; merging remains excluded.

## Defect plants

| Planted defect                              | Instrument                                        | Actual result                                                        | Regression case                                                                                                  |
| ------------------------------------------- | ------------------------------------------------- | -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Signal only the leader PID                  | Descendant PID checks                             | Failed: orphan and late child active; helper exit 4                  | Cancellation stops orphaned and late-starting descendants                                                        |
| Deliver TERM only once, with no escalation  | Late-child PID check                              | Failed: late child active; helper exit 4                             | Cancellation stops orphaned and late-starting descendants                                                        |
| Remove repeated-signal guard during cleanup | Late-child PID checks after repeated TERM and INT | Both cases failed: late child still running, helper status unchanged | Cancellation stops orphaned and late-starting descendants; Interrupting the helper stops the same process groups |
| Disable cancellation deferral during launch | Stub/child PID checks and delayed-write absence   | Failed: stub and child active; delayed-write assertion failed        | Cancellation between launch and registration still owns the process group                                        |

All four mutations were restored. The unchanged isolated test passed before the
plants. The recorded descendant PIDs were stopped by the test on failure; the
unrelated process stayed running until its explicit test cleanup.

## Structural review: first Nit round

Fresh standalone `codex exec` runs used `gpt-6.1-sol`, high effort, window 872000,
and the built-in read-only sandbox. Anti-patterns and report-only simplify ran
in parallel. Both exited 0 and returned nonempty complete reports;
anti-patterns JSON passed its result checker. Scope snapshots matched before
and after: no lasting changes found. No Important or Critical finding was
reported.

| Reviewer label                                         | Assessed severity and impact                                           | Take or record                                      | Review again        |
| ------------------------------------------------------ | ---------------------------------------------------------------------- | --------------------------------------------------- | ------------------- |
| Anti-patterns: nit, obsolete README pgrep prerequisite | Nit: documentation lists an unused dependency                          | Taken: remove pgrep from the plugin prerequisites   | No: docs only       |
| Anti-patterns: nit, stale remaining-work list          | Nit: status summary contradicts completed plants                       | Taken in this record                                | No: docs only       |
| Simplify: suggestion, dense fixture TERM handler       | Nit: multiline handler would expose the inherited TERM-ignore behavior | Taken: expand the handler without changing behavior | No: formatting only |
| Simplify: suggestion, group loop uses pid name         | Nit: group and child identifiers are harder to distinguish             | Taken: rename the group-loop variable               | No: naming only     |
| Simplify: suggestion, stale earlier-stop section       | Nit: old instructions contradict resolved setup                        | Taken in this record                                | No: docs only       |

The Nit round ended after behavior-preserving takes. No further structural
round is required.

## Continuation authority

TOOLING authorized fixing this branch's SC2217 diagnostic, taking the pending
review items, and continuing through the ready PR. The orphan and late-child
sleep commands no longer redirect unused stdin. All pending structural takes
are applied; none changes runtime behavior. Structural loop end state:
**ended: fixes changed no behavior**.

TOOLING also established that local `launch-workmux.md` failures are pre-existing
and out of scope: reproduced independently with 17 of 62 cases failing, with CI
on main passing at 9aa57802. Known load/flakiness issues are
[cboone/agent-harness-plugins#439](https://github.com/cboone/agent-harness-plugins/issues/439),
[cboone/agent-harness-plugins#397](https://github.com/cboone/agent-harness-plugins/issues/397)
and [cboone/agent-harness-plugins#435](https://github.com/cboone/agent-harness-plugins/issues/435).
Treat local `make test-all` as passing only when that document is the sole
failure, name the caveat in the PR, and require PR CI to pass. Do not investigate
or change that document.

Semgrep must run `semgrep scan --config auto --baseline-commit <merge-base>`
without a metrics override, in a disposable shared clone.

## Focused aspect review: first Nit round

The installed immutable helper ran code, errors, tests and comments in parallel,
with `gpt-6.1-sol`, high effort, window 872000 and the read-only sandbox. Types
was inapplicable because no type or schema changed. Every aspect exited 0,
returned nonempty schema-valid JSON and reported `ok`. Before/after snapshots
matched: no lasting changes found. Code, errors and comments had no findings.

| Reviewer label                                                                           | Assessed severity and impact                                                               | Take or record                                                                                                                              | Review again                                  |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| Tests: important, launch-registration cancellation lacks a deterministic regression test | Important: losing the guard could leave an unregistered process running after cancellation | Taken: committed BASH_ENV DEBUG hook signals immediately before PID registration, checks stopped worker/child and absence of delayed writes | No: tests only; production behavior unchanged |

The instrumented boundary case passed. The full focused document passed 81/81.
The hook validates that the worker has its own group before signalling; test
cleanup uses only that recorded group. Makefile and CI register the same hook.
ShellCheck suggestions in the new hook were resolved: explicit required
environment input and a default case. Focused aspect loop end state:
**ended: fixes changed no behavior**. The launch-guard defect plant failed as expected: stub and child stayed active,
and the delayed-write absence assertion failed. The guard was restored and the
case passed under Bash 3.2.

## Trims

One read-only Codex pass each for trim-comments and trim-text, using
`gpt-6.1-sol`, low effort and window 872000. Both exited 0 and returned full
classification/proposal reports. Took one shorter process-inspection comment,
split two prose sentences, and removed stale/duplicate ledger text. No behavior
changed. A supplemental numbered-line read in trim-comments failed because its
shell-local variable shadowed PATH; its complete proposal used the diff hunk
and was checked against the actual source before application.

The local `main` ref lags `origin/main`: the worktree began at 9aa57802, while
local main is 5c1ad075. Structural anti-patterns used origin/main correctly;
the aspect/trim scope additionally covered already-merged effort-default
changes. Final baseline, version and tidy comparisons use origin/main so the
PR contains only cancellation work.

## Semgrep baseline

Ran the exact authorized invocation against merge base 9aa57802 in a disposable
`git clone --shared` of 07ec2950, with
`SEMGREP_REPO_NAME=cboone/agent-harness-plugins`. Exit 0; 137 rules ran on 7
changed targets, with 0 findings. Semgrep skipped the baseline checkout because
there were no current findings. Coverage is limited: about 36.7% of lines
parsed; 7 files matched default ignore patterns. No full-coverage claim is made.
Rule-registry warnings concern future include-pattern interpretation, not this
branch. No metrics override was supplied.

## Lint and fix

Applied the lint-and-fix skill with `--no-push`: documented `make format` ran
Markdownlint/Prettier and shfmt fixers; `make lint` verified Markdownlint,
Prettier, ShellCheck, shfmt and actionlint. Both exited 0. The formatter changed
only this record; no code fixes were needed.

- Lint status: success.
- Unresolved or skipped: none.
- Check-only by project policy: none.
- Caller resume target: required full tests, version check, tidy and ready PR.

## Final local checks

`make test-all` finished with shell status 2: lint and validation passed, and
30 of 31 scrut documents passed. The sole failure was
`tests/scrut/launch-workmux.md`, the exact pre-existing exception authorized by
TOOLING above. The cancellation document passed all 81 cases within this run.
No launch-workmux investigation or changes were made. Local acceptance uses
that exception; PR CI must pass without it.

The check-versions skill compared against merge base 9aa57802: only
review-pr-with-codex changed, with a valid forward patch from 2.1.2 to 2.1.3.
Catalog coverage, manifest version ownership and Codex manifest agreement
passed.

Launch-test assertion controls used a temporary copy with the already-proven
launch-guard defect. Weakening each of the stub-state, child-state and
no-delayed-write checks individually still left another assertion failing.
All three controls failed as expected, while setup passed. Production source
remained unchanged during these controls.

## Publication boundary

Local review and checks are complete with the named local test and Semgrep
coverage caveats. Publication requires a tree-preserving signed-commit tidy, a push to
cboone/agent-harness-plugins, a ready PR fixing issue 623, and green PR CI.
Never merge. Copilot reviews remain paused; report any that arrives.
