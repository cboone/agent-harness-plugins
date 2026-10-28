# Resource claims concurrency ledger

## Scope and authority

- Issue: [Concurrent resource claims](https://github.com/cboone/agent-harness-plugins/issues/656).
- Go-ahead: Inbox, 2026-10-27, 8:54 PM ET, thread "Tooling next Codex workers": build through a PR ready for review. TOOLING merges.
- Branch: `fix/656-resource-claims-race`, originally based on `main` at `741bf751`; main at `84b350ef` was merged for final validation.
- Nighttime boundary: commit and report at approximately 9:45 PM ET; TOOLING parks the worker.

## Baseline evidence

- Read the issue body and its sole comment in full.
- Ownership check: origin is `cboone/agent-harness-plugins`; GitHub reports neither archived nor a fork.
- `corepack yarn install --immutable`: passed.
- macOS, Bash 5.3.20: 100 iterations of two concurrent writers claiming distinct resources, with each writer's PID waited individually. Missing claims: 0/100 pairs. Writer errors: 0/200 writers.
- `make test-scrut SCRUT_TEST_DIR=tests/scrut/manage-resource-claims.md`: 96 succeeded, 0 failed, 0 skipped.
- Failing CI run `40605137170`, job `122542696345`: the concurrent case printed only `resource=logic`. The test redirects both writers' diagnostics to `/dev/null` and uses bare `wait`, so the record cannot distinguish a failed writer from an overwritten claim.
- The canonical script is byte-identical between that CI head (`d7a344966374cd39bbc9fa9dde3064e330b76621`) and this branch's base.

## Source assessment

The existing implementation already acquires a `mkdir` lock before `read_claims`, holds it through `write_claims`, and replaces the JSON through a temporary file and rename in the same directory. The wait is bounded at ten one-second retries. An EXIT trap recursively removes the lock directory. A process that cannot execute cleanup can leave that directory behind; the current policy reports it and requires manual removal rather than reclaiming it automatically.

No source fix has been selected. The observed CI output does not establish that concurrent successful writers overwrite each other. The deterministic interleaving test and writer-status capture provide evidence for the next diagnostic run.

## Checkpoint and conductor decision

TOOLING's mailbox reply `000001-20261028T014000Z-TOOLING.md` directs a checkpoint and stop for the night, with restart after 8 AM ET. The reply records these decisions:

- No software installation or further containers. Use CI for Linux reproduction.
- Capturing both writer exit statuses and diagnostics is an authorized test-quality fix within scope.
- Investigate automatic stale-lock breaking and a timeout treated as a non-fatal skip before selecting any source fix.
- Keep the directory lock; no kernel-owned lock or Perl dependency. The brief's cleanup requirement does not extend to SIGKILL.

Both source suspects were checked. `acquire_lock` never breaks or reclaims a directory automatically, whether its recorded owner has exited or is still running. At the bounded wait, `die` exits with status 1. `cmd_claim`, `cmd_release` and `cmd_prune` call it directly, without swallowing that status. There is no non-fatal timeout path in this helper.

The new fixture holds the first writer at its worktree-listing call, after its snapshot read, and observes whether the second writer attempts the held lock or reads without it. Without serialization, the second writer finishes before the first resumes. Both writer statuses are checked. The fixture passes against the unchanged source, including with the writers running under macOS Bash 3.2.

Removing the three `acquire_lock` calls from the real source produced `["logic"]`; the expected `["logic","simulator"]` assertion failed with exit 1. The source was restored byte-for-byte, and the fixture passed again. This proves the interleaving detects missing serialization, not that the current implementation lacks it.

The existing concurrent-claims case now waits on both recorded writer PIDs, checks both exit statuses and prints captured diagnostics on failure. Its first development run failed because the new log paths were beneath the not-yet-created claim directory; moving those logs to the existing stub directory corrected the test setup without precreating the claim directory or changing the original creation race. Final affected Scrut run: 97 succeeded, 0 failed, 0 skipped. ShellCheck, shfmt and Bash syntax checks passed for both fixtures.

At the overnight checkpoint, no source change, version bump, push, PR, review rounds, Semgrep baseline or full-suite run existed. The scratch directory held the stress script, raw CI failure log, source backup, plant output, final Scrut log and scope-question text. Its `stress-root` file records the stress data directory. The resumed review section records its new location.

## Publication gates

- Trims, Semgrep, lint, full tests and version checks must pass before publication. Tidy must preserve the tested tree. Use CI as the Linux reproduction with writer diagnostics visible.
- Do not claim the correctness issue is fixed or open a PR that closes it based only on test changes. Select a source fix only if the reproduction establishes one, maintaining Bash 3.2 compatibility and bounded serialization; report another scope question if the evidence still does not establish a source defect.
- Keep the unresolved issue open when publishing the diagnostic PR. No production-source fix has been selected, so no after-fix loss rate exists.

## Plant table

| Planted defect              | Instrument expected to catch it       | Observed result                                       | Permanent coverage                                     |
| --------------------------- | ------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------ |
| Remove writer serialization | Deterministic interleaving regression | Only logic survived; expected pair assertion exited 1 | A writer waits while another holds an earlier snapshot |

## Resumed diagnostic review

The Inbox yes on 2026-10-28 at 8:21 AM ET, thread "Tooling overnight", reopened the worker through the ready PR. TOOLING relayed a subsequent restart after the command host was restored on Codex 0.165.0. The morning command-host launch failure ran no commands and changed no files. The current nighttime checkpoint is approximately 9:45 PM ET.

The recorded scratch directory was moved outside the checkout to `/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/resource-claims-review.BcszR9/checkpoint-scratch`, so evidence files do not join the review scope. Review artifacts are in its parent directory.

Structural loop, Nit round: anti-patterns returned `status=success`, `complete=true`, with no findings; report-only simplify returned a validated result with no findings. Both ran as fresh read-only `codex exec` processes, model `gpt-6.1-sol`, high effort, window 872000. Project instructions required this path despite the installed anti-pattern skill's default Codex-caller fallback. The report-only project rule overrode simplify's edit default. Both processes exited 0, their output contracts validated, and the scope comparison found no lasting changes. End state: clean at Nit. Fresh execution and planting were excluded from the reviewers' read-only checks and remain the worker's validation obligation.

A subsequent manual requirement check, independent of both structural reviewers, found that the parallel helper checked numeric statuses without printing them. Commit `f507895b` added explicit statuses in the parallel helper and deterministic fixture, including for a writer that exits without stderr. Neither structural reviewer reported this finding; both returned empty finding lists. The structural loop therefore took no findings and ended clean at Nit. The focused review covered the diagnostic refinement.

Focused loop, Nit round: code, errors, tests and comments all exited 0 and passed the helper's output checks. Settings: standalone read-only Codex, `gpt-6.1-sol`, high effort, window 872000, aspects in parallel. Types was skipped because no types or schemas changed; editing simplify was not selected. The scope comparison found no lasting changes. The errors reviewer could not query GitHub from the sandbox; the parent already verified repository ownership and that no PR exists.

| Reviewer's label                                                                              | Our severity                                                                                                                       | Take or record                                                                                                                                                      | Review again                                                                                                 |
| --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| important: write-bash-scripts: Safe temporary files requires cleanup of the fixture directory | Important: the new helper retains copied tools and logs, and interruption can leave recorded writers active after its caller exits | Take: add EXIT and signal cleanup, release the barrier, wait for the recorded writer PIDs, then remove only the recorded invocation directory; add cleanup coverage | Yes: the cleanup handler changes fixture behavior, so the focused loop advances to its first Important round |

The production claims helper remains unchanged. The focused review does not establish a cause for the CI failure.

Trims: one read-only Codex round each for comments and prose, model `gpt-6.1-sol`, low effort, window 872000. Both exited 0 with complete proposal tables. Applied one comment rewrite and three prose rewrites, with ledger statements updated to distinguish the overnight checkpoint from the resumed run. The comments run could not resolve bare `realpath`; the parent verified all four eligible paths with the installed `/bin/realpath` before applying proposals. No tool installation was needed. Prose profile: none.

The committed Scrut cases were extracted verbatim into external focused documents for planting against the real source and fixture. Removing serialization failed the expected resource pair; forcing `logic` to exit 23 without stderr failed the parallel case with `logic=23 simulator=0`; removing fixture cleanup failed the empty-parent assertion. Each intentional Scrut run exited 50 at the intended assertion. Restoring the files produced 4 succeeded, 0 failed, 0 skipped. A separate Bash 3.2 TERM check, using the recorded fixture PID while the first writer was paused, exited 143 and removed the invocation directory after waiting for its writers.

| Planted defect                 | Instrument expected to catch it  | Observed result                           | Permanent coverage                                       |
| ------------------------------ | -------------------------------- | ----------------------------------------- | -------------------------------------------------------- |
| Writer exits 23 without stderr | Parallel writer status check     | Numeric statuses printed; Scrut exited 50 | Concurrent claims on different resources both survive    |
| Remove fixture cleanup         | Empty temporary-parent assertion | Parent retained files; Scrut exited 50    | The interleaving fixture removes its temporary directory |

Semgrep baseline: `SEMGREP_REPO_NAME=cboone/agent-harness-plugins semgrep scan --config auto --baseline-commit 741bf751c143a1e82277b7eb29e2899e431744f7` ran in a disposable `git clone --shared` of branch head `2ae1246d`, with JSON output and without disabling metrics. Exit 0; 82 rules, 3 targets, 0 findings, no errors or skipped rules. Coverage was limited to the changed CI workflow, Makefile and ledger. Default Semgrep ignore patterns excluded the three changed test paths, so this scan does not establish Bash-test coverage; ShellCheck, shfmt, static reviews and planted Scrut checks cover those paths separately.

Round-count correction: the earlier worker report applied the test-only exception too broadly to the cleanup fix. A fixture runtime change is behavior, so the focused loop requires its first Important round. This correction changes no code. The structural status-output refinement was a separate manual requirement check, not a finding taken from that loop; TOOLING received that distinction by mailbox.

Focused loop, first Important round: code, errors, tests and comments all exited 0 and validated. No Important or Critical findings were reported. The scope comparison found no lasting changes. Same read-only model, effort and window as the Nit round.

| Reviewer's label                                                                            | Our severity                                                                                             | Take or record                                                                                                                                                                 | Review again                                                                |
| ------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------- |
| suggestion: write-bash-scripts: Checked commands should preserve writer statuses on timeout | Nit: a writer that exits silently before a fixture barrier is obscured by a timeout message              | Take: capture and print statuses in both barrier-timeout branches; this is a trivial diagnostic fix in the change's own code                                                   | No finding met the Important threshold, so the loop does not advance        |
| suggestion: write-scrut-tests: Error testing leaves interruption cleanup uncovered          | Nit: successful cleanup was covered, but removing interruption cleanup had no permanent regression check | Take: add a synchronized TERM case for the new cleanup boundary, checking exit 143, stopped recorded writers, barrier-release acknowledgment and an empty invocation directory | No finding met the Important threshold, so the loop ends clean at Important |

The additional test uses the existing fixture and stub. A control directory holds writer PIDs and a ready marker while the fixture stays at its barrier; the test sends TERM only after that marker. The stub acknowledges observing the released barrier, so a timeout alone cannot satisfy the release assertion.

TOOLING's mailbox `000006-20261028T180622Z-TOOLING.md` withdrew the launcher-test exception and explicitly directed a merge of `origin/main` before the final suite. Signed merge `2426436d` incorporated main at `84b350efe84c04abedaf3aadbf0b7f96dde520ee` without conflicts. The upstream claims helper and its existing Scrut document were unchanged; the main changes include the launcher reliability fix. The pre-sync full suite passed 31 documents and failed only `launch-workmux.md`; it is not the final acceptance run. No dependency lockfile changed. The final suite must pass every document. Version comparison now uses main at that merged SHA; the branch still changes no plugin content or manifests.

The synchronized interruption case passed. Removing the real fixture's cleanup barrier release made that permanent case fail with Scrut exit 50; restoring the fixture produced 2 succeeded, 0 failed, 0 skipped in the extracted document. The affected full document passed all 99 cases after merging main. The private interruption-control variable is cleared in the local runner and CI before each document; only the interruption case sets it for its child fixture.

The focused loop ends clean at Important. The two suggestions were taken below threshold for the change's own test and diagnostic paths; neither was another implementation instance of the temporary-directory leak fixed in the Nit round. No further round is triggered because no finding met the Important threshold. Final trims and the baseline scan are refreshed after these changes and the directed base merge; the final full suite has no accepted failure exception.

Final trims after the behavior changes and base merge: both read-only Codex runs exited 0 and returned complete file lists and proposal tables, using `gpt-6.1-sol`, low effort and window 872000. Comments proposed no changes. The prose run's clearer reference to the second writer was applied; its noun-heavy rewrite of the overwrite statement was declined to preserve the original active wording. No code changed.

Final Semgrep baseline at the merged base `84b350efe84c04abedaf3aadbf0b7f96dde520ee`: a fresh shared clone of `7c9ed877` completed the same `scan --config auto --baseline-commit` command, with metrics enabled, exit 0, 82 rules, 3 scanned targets, 0 findings and no errors. The same three test paths were ignored by default. A subsequent defensive check makes the interruption test reject missing or nonnumeric recorded PIDs and a failed TERM delivery before asserting process absence; it changes only an ignored test path, so scanned content is unchanged apart from this ledger's result record.

## Final local validation

`make test-all SCRUT_JOBS=4` exited 0 on the merged base: all 35 Scrut documents passed, including both launcher documents and all 99 resource-claims cases. No failure exception was used. The final synchronized interruption case also passed with macOS Bash 3.2: 2 extracted cases succeeded, none failed or skipped. `make build` left no generated-file drift.

`lint-and-fix --no-push` completed successfully. Shell formatting produced no changes, and every required check passed. Markdown and Prettier used check mode because the loaded project instructions say Scrut snapshots are never reformatted; a blanket writer would include those snapshots. Formatting of authored ledger prose was performed separately before its targeted checks.

| Tool                                                 | Mode and project command                                                     | Result                  |
| ---------------------------------------------------- | ---------------------------------------------------------------------------- | ----------------------- |
| shfmt                                                | Fix shell files from `bin/list-shell-scripts`, then `make lint-shell` checks | Passed; no fixes needed |
| markdownlint and Prettier                            | Check-only by Scrut policy, through `make lint`                              | Passed                  |
| ShellCheck and actionlint                            | Check-only, through `make lint`                                              | Passed                  |
| JSON, plugin, catalog and cross-reference validators | `make validate`                                                              | Passed                  |
| Generated mirrors                                    | `make build` and empty diff                                                  | Passed                  |

Version check report: comparison base `84b350efe84c04abedaf3aadbf0b7f96dde520ee`; no plugin content or manifest changes in the branch, so no version bump is required. Repository validation confirmed marketplace coverage, manifest-owned versions and Codex version parity. No corrective action was needed.

Evidence for the PR: macOS measured 0 missing pairs out of 100 two-writer pairs, with 0 writer errors out of 200 writers. No many-pair Linux rate has been measured. CI exercises one uncontrolled parallel pair and the controlled fixture cases. The writer already holds its directory lock across `read_claims` and `write_claims`; atomic replacement is inside `write_claims`. This branch changes no production code. Besides diagnostics and tests, it changes runner registrations and this ledger. The cause of the original CI loss remains unknown: hidden writer failures prevent distinguishing an overwritten claim from a failed writer, and no evidence assigns the cause to the writer, fixture or environment. Issue 656 remains open.

Tidy uses the local backup `fix/656-resource-claims-race-pre-tidy`, then rebuilds from the merged main SHA as separate signed test and documentation commits. Publication requires an identical-tree comparison against that backup. PR CI results and the final handoff are recorded in the worker mailbox checkpoint, without a metadata-only push after opening the PR.
