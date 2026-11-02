# Aspect process-group review ledger

## Scope

Issue [715](https://github.com/cboone/agent-harness-plugins/issues/715), base
`46d31ef74e3b72aa2cf73bcb354f11880ddcde91` from `origin/main`. Replace monitor-mode
launch with checked child-only Perl POSIX setpgid and exec. Preserve group
shutdown, escalation, inspection failure reporting and launch registration.
Plugin version: 2.3.2 to 2.3.3; mirrors regenerated with `make build`.

## Structural loop

Nit round: fresh read-only `codex exec` runs, `gpt-6.1-sol`, high effort,
872000-token window, anti-patterns and report-only simplify in parallel.
Both completed with exit 0 and nonempty valid JSON. Anti-patterns covered every
canonical changed file and all thirteen checklist items; simplify had no findings.
The review could not write and did not run runtime tests. Static checks passed.

| Reviewer label                                                              | Assessed severity and impact                                                                                       | Take or record                                                                                                              | Review again                     |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| important: Stale writes: completed leader PIDs remain cancellation targets  | Important: a waited PID could be reused while another aspect runs, causing a direct signal to an unrelated process | Taken: remove each PID immediately after wait; DEBUG hook rejects a prior waited entry at the next wait                     | Yes, production behavior changed |
| important: Parallel paths: pre-group leaders bypass cancellation escalation | Important: a stopped leader before setpgid could leave cleanup waiting indefinitely                                | Taken: include registered pre-group leaders in liveness checks; test stops the leader and requires escalation before rescue | Yes, production behavior changed |

First Important round: both runs completed with exit 0 and valid nonempty JSON.
Simplify reported no findings. Anti-patterns found the same stale-PID class in
completed, un-waited children. A live check independently confirmed Bash 3.2 and
Bash 5 collect background children before explicit wait while preserving wait's
status. Assessment: Important; direct signals can reach a reused unrelated PID.
The loop stopped under the recurrence rule. No downgrade.

TOOLING's structural call: use one ownership-checking signal helper, checking
current parent PID and PGID immediately before choosing a group or leader
signal. Do not introduce a handshake protocol. TOOLING clarified that recorded leaderless groups remain targets while members
persist. A PID equal to a live group's ID cannot be reused. Implemented one
signal helper with a parent ownership check, group-member inspection, bounded
escalation and artifact retention on inspection failure. Every production kill
now goes through that helper. Loop count remains Nit plus first Important;
verification of the structural call continues at that count.

## Defect plants

Checks were committed before plants. Plants run only in a recorded disposable
shared clone; the implementation worktree stays intact.

| Plant                                        | Instrument                          | Observed result                                          | Regression coverage                            |
| -------------------------------------------- | ----------------------------------- | -------------------------------------------------------- | ---------------------------------------------- |
| Restore set -m, direct codex exec and set +m | Launch diagnostics and monitor hook | Exit 50: launch case fails; 83/86 cases pass, three fail | Silent launch and distinct leader-owned groups |
| Remove direct leader signalling              | Pre-group cancellation case         | Exit 50: early-cancellation case fails; 85/86 pass       | Cancellation before child-side group setup     |

| Remove waited-PID removal | Launch hook's second-wait assertion | Exit 50: launch case fails; 85/86 pass | Completed leaders removed after wait |
| Remove pending-leader liveness | Stopped pre-group cancellation test | Unexpected pass: 86/86 pass on macOS | Insufficient sensitivity; deterministic fixture required |

The unexpected plant pass is incomplete escalation evidence, not a clean check.
Replaced its platform-dependent stopped-process assumption with a committed
ps/kill fixture. It invokes the actual cleanup functions, rejects unexpected ps
queries, verifies both signal commands are shell-function stubs, and simulates a
pre-group child that stays active through TERM until KILL. Cases also cover a
reused PID, an established group and a leaderless group. No real target is
signalled by this fixture. Updated plants are recorded below.

## Validation

- Focused document: 86/86 passed on Bash 5.3 and macOS Bash 3.2 after review fixes.
- Error-output guard: 102/102 passed before review fixes.
- Environment-isolation: first run 48/51 because `make -s` propagated into nested
  commands and suppressed expected command echoes; normal invocation passed 51/51.
- Load deviation: environment-isolation was started before both first documents
  finished, briefly exceeding the two-document limit. Subsequent runs use at most
  two documents concurrently.
- Ownership-focused document: 87/87 passed on Bash 5.3.
- Final suite, Semgrep, trim, lint and version results are recorded below.

## Ownership verification outcome

Resumed first Important verification completed with valid JSON and exit 0.
Simplify had no findings. Anti-patterns reported these two findings:

| Reviewer label                                                                   | Assessed severity and impact                                                                          | Take or record                                                                                                                                            | Review again                  |
| -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| important: Stale writes: recycled leaderless groups bypass the ownership check   | Important, pre-existing: group retention on main has the same reuse gap                               | Record: TOOLING explicitly deferred this risk to [the group-identity follow-up](https://github.com/cboone/agent-harness-plugins/issues/716); no downgrade | No implementation change here |
| important: Parallel paths: denied-inspection coverage leaves its workers running | Important: inspection denial now prevents signals and the old test leaves real sample workers running | Taken: use the committed ps/kill fixture for denial, assert no signals and retained artifacts; no real workers start                                      | No: tests only                |

TOOLING confirmed the new direct-PID exposure is the class to close in this
brief; pre-existing group reuse is out of scope. Three remaining sample groups
were identified from their recorded task fixture paths and open script file
descriptors; all were stopped or had completed, with final PID inspection empty.
Added a reasoned SC2016 annotation for literal DEBUG command matching.
Structural loop end state: **ended: fixes changed no behavior**. Counts remain
Nit and first Important, with two verification continuations after structural
calls; no fresh Nit budget or additional round.

Both updated plants failed the deterministic ownership case (86/87 passed):
removing the parent check and treating a pre-group target as inactive after TERM.
This replaces the earlier insufficient escalation plant. Ownership-focused
Bash 5.3 and macOS Bash 3.2 runs passed 87/87; guard passed 102/102. Denial fixture
revision passed in the final 89-case focused document.

## Focused aspect Nit round

Installed immutable helper: code, errors, tests and comments, gpt-6.1-sol/high,
872000-token window, read-only. Types omitted because no types or schemas changed.
All four returned exit 0 and valid nonempty schema-matching results. Before/after
scope snapshots matched, with no changed paths. Code and errors had no findings.

| Reviewer label                                                                             | Assessed severity and impact                                                            | Take or record                                                                                         | Review again               |
| ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | -------------------------- |
| important: Cover cancellation after an aspect has already been waited for (rating 7/10)    | Important: dropping an already-waited aspect's group could leave its descendants active | Taken: integration case with first aspect exiting, second hanging, and cancellation at the second wait | No: tests only             |
| suggestion: Verify that executed workers receive restored interrupt defaults (rating 6/10) | Nit: missing check for new INT/QUIT restoration                                         | Taken: stub records initial traps; assertions require both signal records and default dispositions     | No: tests only             |
| important: The leaderless-group comment overstates the ownership guarantee                 | Important: new comment claims stronger ownership than the implementation establishes    | Taken: qualify source comment and invocation reference with the deferred reuse limitation              | No: comments and docs only |

Focused loop end state: **ended: fixes changed no behavior**. Added boundary
plants and focused verification are recorded below; no additional aspect round required.

## Boundary verification and trim

Focused document passed 89/89 on Bash 5.3 and macOS Bash 3.2. Removing the
waited aspect's group at wait completion failed the new lifecycle case;
removing INT/QUIT default restoration failed its signal-record assertion.
Each plant returned Scrut exit 50, with 88/89 passing. Sample cleanup runs even
when lifecycle assertions fail. Plants were restored in the disposable clone.

One combined trim-comments/trim-text read-only Codex pass used
gpt-6.1-sol/low/872000. Exit 0, complete file classification and two full proposals.
Both taken: one fixture comment and one test-description paragraph. Code stayed
unchanged, verified by comparing Bash parser/minifier output before and after.
ShellCheck, shfmt and Markdown checks cover the edits; full-suite results are recorded below.

## Semgrep baseline

The requested baseline invocation ran in a disposable shared clone of d828ab82,
with SEMGREP_REPO_NAME=cboone/agent-harness-plugins, config auto, the recorded
merge base and no metrics override. Exit 0, 103 rules, seven scanned paths,
zero findings. Coverage is incomplete: approximately 31.1% parsed, PartialParsing
across codex-aspects lines 3-1388, and nine paths excluded by default ignores.
Semgrep skipped baseline comparison because it found no current findings.

An initial setup invocation ran from the scratchpad before the clone existed
and failed Git-baseline validation; it was not a scan. The corrected invocation
above supplies the gate evidence. A separate AST diagnostic on the exact main
version also failed across lines 3-1343, confirming the parser limitation is
pre-existing, without substituting for the baseline invocation.

TOOLING relayed the standing shell-file rule accepting this limitation with
coverage recorded and ShellCheck passing on affected shell files. No clean-scan
claim is made. Full project ShellCheck and final lint verification passed.

## Final validation and publication handoff

One `make test-all` run used SCRUT_JOBS=2 under the designated full-suite lock,
after pmset reported no thermal warning. Lint and repository validation passed;
75/76 Scrut documents passed. The only failure was
`validate-plugins-codex-exec.md`: rule 23 stopped recognizing the launch because
its line started with run_in_group, so its committed missing-approval mutation
produced five errors instead of six.

TOOLING approved a continuation-line fix: keep run_in_group on one line and
codex exec at the next line's start, with a short explanatory comment. The Bash
ASTs before and after match after removing source positions and comments; every
other semantic field is retained. Bash 3.2 syntax checking passed. No validator
implementation or executable command changed; mirrors were rebuilt.

The failed document then passed 5/5. Post-fix `make lint` and `make validate`
passed. TOOLING explicitly approved these scoped retests without another full
suite for this layout-only fix. The initial full invocation remains recorded as
a failure, not relabeled a pass. CI must validate the final published tree.

Version checks against origin/main's actual merge base passed: only
review-pr-with-codex changed, 2.3.2 to 2.3.3, with its generated manifest matching;
all 61 plugins are registered, and versions belong only to manifests.
Lint-and-fix result: no file fixes needed, all enforced checks passed, no skipped
required checks and no advisory-only tools. Markdown/Prettier ran in check mode
to preserve Scrut files. Final process-record edits receive a final lint check;
implementation and tests remain those already checked above.
