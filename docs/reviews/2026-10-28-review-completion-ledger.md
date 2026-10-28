# Reviewer completion and ledger reruns

Current state: local review and required checks complete; publication pending. No unresolved findings.

Scope: issues 524 and 541 in `cboone/agent-harness-plugins`. Build through a ready PR; TOOLING owns merging.

## Implementation

The skill calls `check-completion` before transcription. The helper checks the captured status and raw reply, emitting terminal `failed` on mechanical failure. Passing the helper does not establish semantic completion, schema validity, report mode or snapshot validity; the existing skill checks still decide those. Tests invoke only the committed backend, guarded by its resolved path.

Reruns use distinct ledger files. This is simpler than appending because each file retains its own header, findings and result without renumbering or duplicate headings. Earlier declines carry only while their code is unchanged. `save-ledger` reserves a distinct filename and retains the temporary source.

## Sibling sweep

- `review-pr-with-codex/scripts/codex-aspects`, `aspect_status`: checks exit status, missing file, empty file, exactly one JSON value, schema, aspect and snapshot. Existing `tests/fixtures/codex-stub` already supplies missing, empty, malformed and non-zero modes. Retained unchanged.
- `review-anti-patterns` shared `references/codex-exec.md`, Completion checks: requires zero status, a reply with non-whitespace content, exactly one JSON value when structured, schema and completed report shape. Its caller names `result-check.jq`. Retained unchanged.
- `trim-comments` and `trim-text`: generated copies of that shared reference, plus their own finished-report shapes. Retained unchanged. No missing mechanical completion path found in this sweep.

## Validation

Focused Scrut: 13 cases passed, including after all plants were restored. Required full reviews, lint, Semgrep baseline, full suite and version audit remain pending.

## Plants

| Planted defect          | Instrument    | Observed result                                                                     | Regression case                      |
| ----------------------- | ------------- | ----------------------------------------------------------------------------------- | ------------------------------------ |
| Bypass exit status      | Focused Scrut | One failure: valid output with exit 7 passed                                        | Non-zero exit with valid output      |
| Bypass content check    | Focused Scrut | Three failures; silent and whitespace text passed, empty JSON failed later at parse | Empty stdout, empty file, whitespace |
| Remove existence check  | Focused Scrut | Missing-file diagnostic failed; readability remains a redundant failure guard       | Missing reply                        |
| Bypass JSON check       | Focused Scrut | Two failures: malformed and multiple JSON replies passed                            | Malformed and multiple JSON          |
| Remove ledger noclobber | Focused Scrut | Three failures: earlier ledger, empty reservation and symlink                       | Rerun collision cases                |

## Review rounds

Structural loop, Nit round: anti-patterns returned one Important finding; report-only simplify returned none. Both completed successfully through read-only Codex, `gpt-6.1-sol`, high effort, window 872000. Base: `45b89f1c43cb012d6cf0a4bc9b2c53611f4cc55f`. Raw artifacts: `/tmp/524-reviews.ym2EXx`.

F1 reviewer label: `important`, Agent-prose control flow: JSON mode rejects a valid mixed-format reviewer report. Our severity: Important, because a supported reviewer would fail despite completing. Take: clarify exclusively JSON versus mixed reports and retain validation of the unchanged structured portion; add a mixed-report case. Review again: yes, the instruction changes behavior. No downgrade, design change or recurrence. Next structural round: Important. Aspect and trim reviews pending.

Structural Important round: anti-patterns and report-only simplify both completed with no findings. End state: clean at Important. No recurrence. The mixed-report fix passed the 14-case focused suite. Existing Codex-aspects suite: 81 cases passed. `make validate`: passed. Review processes exited zero; anti-pattern replies passed raw completion and the shipped `result-check.jq`, with `complete: true` and no unread files. Reviewer sandbox GitHub checks were unavailable; repository identity was verified in the parent before implementation.

Aspect loop starts at Nit: code, errors, tests and comments selected; types excluded because no type definitions or typed interfaces changed. Runs use read-only Codex `gpt-6.1-sol`, high effort, window 872000.

Aspect Nit round: all four processes exited zero with validated schema, aspect and snapshot. The before/after scope was identical; no lasting changes found.

- F2 reviewer label: `suggestion`, write-bash-scripts: Errors to stderr: Preserve unexpected reservation diagnostics. Our severity: Nit. Take: capture the shell diagnostic without suppressing unexpected filesystem failures, naming the destination and retained source. Review again: yes, error output changes.
- F3 reviewer label: `important`, write-scrut-tests: Behavioral coverage omits concurrent ledger reservations. Our severity: Important. Take: synchronize two real helper processes immediately before reservation, capture both statuses and paths, and verify both complete ledgers. Review again: tests alone would not require it.
- F4 reviewer label: `suggestion`, write-scrut-tests: Behavioral coverage omits ledger persistence failures. Our severity: Nit. Take: add committed command stubs for deterministic reservation and copy failures, with resolution guards, retained-source assertions and reservation deadline. Review again: tests alone would not require it.

All are the branch's own new boundaries; no downgrade, design change or recurring defect. The focused suite now passes 17 cases, and ShellCheck passes. The aspect loop proceeds to Important because F2 changes observable error output. Synchronized tests use a test-only Bash DEBUG trap from `BASH_ENV`; production code has no test hook.

Additional plants, each restored afterward:

| Planted defect                                               | Instrument    | Observed result                                                                                                                         | Regression case      |
| ------------------------------------------------------------ | ------------- | --------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| Replace exclusive create with an existence check then create | Focused Scrut | Concurrent writers both exited zero but returned the same path; concurrency assertion failed. Symlink and diagnostics cases also failed | Concurrent runs      |
| Treat every reservation error as a collision                 | Focused Scrut | Reservation test reached its deadline and failed instead of accepting a retained-source result                                          | Reservation failure  |
| Ignore copy failure                                          | Focused Scrut | Copy case failed on unexpected success and destination output                                                                           | Copy failure         |
| Suppress underlying reservation diagnostic                   | Focused Scrut | Reservation diagnostic assertion failed                                                                                                 | Reservation failure  |
| Parse text reports as JSON                                   | Focused Scrut | Valid mixed-report case failed                                                                                                          | Mixed JSON and prose |

Raw plant outputs are `/tmp/524-plant-check-then-create.log`, `/tmp/524-plant-collision-loop.log`, `/tmp/524-plant-copy-success.log`, `/tmp/524-plant-diagnostics.log` and `/tmp/524-plant-mixed.log`. The concurrency fixture captures each writer's process status and waits for both; its deadline owns the complete fixture process group. These test fixtures and command stubs are committed with their cases.

## Stop: recurring defect

Aspect Important round: all four reviewers exited zero and passed their output, aspect and snapshot checks. The scope did not change; no lasting changes found. Code, tests and comments had no findings. Errors raised one suggestion:

F5 reviewer label: `suggestion`, write-bash-scripts: Errors to stderr: Preserve jq's validation diagnostics. Location: `plugins/review-until-clean/scripts/check-completion:30`. `jq` stderr is discarded, so parser locations and unexpected execution or input/output errors become the generic message that the output is not exactly one JSON value. Our severity: Nit, matching the suggestion label; this loses diagnostic context while still refusing the round. Take or record: recorded unresolved pending the recurrence decision. Review again: not decided; no edits made for F5.

This repeats F2's defect class, suppressed unexpected diagnostics, in the sibling completion helper after F2 was fixed in the save helper. The project recurrence rule requires stopping and reporting to TOOLING for a structural decision, even though F5 is below the active Important threshold. End state: stopped: recurring defect. No downgrade or Critical finding is involved.

Latest reviewed HEAD: `54d7f278`. Artifacts: `/tmp/524-reviews.ym2EXx/aspects-important/` and `/tmp/524-reviews.ym2EXx/aspect-important-statuses.json`. The last unmodified focused run passed all 17 cases. Full local review is incomplete: trims, Semgrep baseline, final lint-and-fix, `make test-all`, final version audit, tidy, push, PR creation and CI remain pending. Nothing was pushed, no PR was opened, and no merge was attempted.

Next step: TOOLING decides the consistent diagnostic policy for both new helpers and relays the next go-ahead. Preserve this worktree and branch. Review counts persist: structural Nit plus one Important, clean at Important; aspect Nit plus one Important, stopped: recurring defect. Trims have not started. Version is 3.2.0 with mirrors rebuilt; version audit remains pending.

## TOOLING recurrence decision and continuation

TOOLING authorized fixing F5 and closing diagnostic suppression across both helpers. Decision: each terminal tool failure sends the helper's one-line reason, then the tool's original stderr, to stderr; stdout holds only the verdict or successful destination. No bare stderr-to-null redirect may decide the outcome. Expected filename collisions remain handled, nonterminal outcomes. Sweep covers both helpers and all four added stub/support scripts; no other suppressed outcome-deciding stderr remains.

F5 is taken under that decision. `check-completion` now captures and reports grep, command lookup and jq diagnostics; `save-ledger` reports directory creation, reservation and copy failures in the same order. Tests isolate jq, grep, mkdir and copy failures, assert stream separation, failed status or non-zero exit, and retained source. A source guard covers all six added helper/stub files. The focused suite passes 21 cases before plants.

Counts carry forward as instructed: structural loop remains clean at Important, with Nit plus one Important. The aspect loop resumes at Important round 1 after the recurrence decision, retaining the Nit round and stopped Important attempt in its history. A further instance of diagnostic suppression stops the loop again. Trims, baseline scan and final validation are still pending.

Diagnostic plants: suppress jq stderr, grep stderr, mkdir stderr, copy stderr and reservation stderr, one at a time. Each made the source guard fail and the matching diagnostic assertion fail (jq also failed the malformed-output assertion). Results: jq 3 failing cases; each other plant 2 failing cases. Raw logs: `/tmp/524-plant-jq-stderr.log`, `/tmp/524-plant-grep-stderr.log`, `/tmp/524-plant-mkdir-stderr.log`, `/tmp/524-plant-copy-stderr.log`, `/tmp/524-plant-reservation-stderr.log`. Every plant was restored. The unmodified focused suite passes all 21 cases. F5 is fixed under TOOLING's class-wide decision; no further diagnostic instance was found in the six-file sweep.

Resumed Important round 1 completed: code, errors, tests and comments all exited zero, with validated output and no findings. Before/after snapshots and trees match; no lasting changes found. No further diagnostic-suppression instance. End state: clean at Important. Raw results: `/tmp/524-reviews.ym2EXx/aspects-important-resumed/`. The prior stopped attempt remains in the history; no review count was restarted at Nit. Proceed to the single comment/prose trim round, then baseline and final checks.

Trims: one read-only Codex round each for comments and text, `gpt-6.1-sol`, low effort, window 872000. Both exited zero with complete file classifications and proposal tables. Applied three comment rewrites and three prose edits after checking them against the source and applicable profiles. Historical review evidence remains intact. Behavior unchanged, so no additional review round. Artifacts: `/tmp/524-reviews.ym2EXx/trim-comments.txt` and `/tmp/524-reviews.ym2EXx/trim-text.txt`. End state: ended: fixes changed no behavior.

Semgrep baseline: completed in shared disposable clone `/tmp/524-semgrep.LwQP4f/repo`, using `SEMGREP_REPO_NAME=cboone/agent-harness-plugins semgrep scan --config auto --baseline-commit 45b89f1c43cb012d6cf0a4bc9b2c53611f4cc55f --json`. Exit zero, 165 rules, 9 targets, zero findings, zero errors and no skipped rules; 11 files excluded by ignore policy. JSON and log retained beside the clone. No `--metrics off` override was used.

`lint-and-fix --no-push`: `make lint` passed. Markdownlint/Prettier were check-only by project policy because the repository-wide writer includes Scrut files, which the project instructions say are never reformatted; the installed lint skill requires downgrading writers that reach protected paths. ShellCheck, shfmt and actionlint all passed their documented checks. No fixes or skipped findings. Full `make test-all` is running as separately required by the brief.

Version check: verified GitHub default branch `main` and actual `origin/main` merge base. Only `review-until-clean` changed: 3.1.4 to 3.2.0, a forward minor bump for the new helpers. Marketplace coverage, manifest-only version ownership and source/generated Codex manifest parity passed across all 60 plugins. No recommended actions.

Final local validation: `make test-all` exited zero. All 40 Scrut documents passed, including the 21-case completion/ledger document; lint, JSON and plugin validation passed in the same run. The earlier sibling Codex-aspects run passed all 81 cases, and it also passed in the full suite. No real reviewer was invoked by the tests. All added scripts passed explicit ShellCheck and macOS Bash 3.2 syntax checks. No software was installed or real user configuration changed.

PR body trimmed in-session under the PR/issue profile: describes the completion gate, distinct-file reruns, unchanged-code decline carry, diagnostic streams, version and validation. No review history or unrelated follow-ups in the body. Closing references are only the two authorized public issues in this repository. Title convention: sentence case, no type prefix.

Final handoff will record the tidy's exact-tree comparison, pushed HEAD, PR URL and CI result in the worker checkpoint and mailbox. TOOLING owns merging. Required merge method remains a merge commit; this worker will not merge.
