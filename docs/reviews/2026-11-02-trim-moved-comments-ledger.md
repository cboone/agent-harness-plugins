# Moved trim text review ledger

Both trim skills treat moved and copied text as branch-owned, check disputed dated facts and warnings against current code, and report every decline. Commit and PR callers relay the new continuation field. SL-VF ledger and précis policy remains outside this branch.

## Scope and decisions

- Issue: [stale moved comments](https://github.com/cboone/agent-harness-plugins/issues/718), read with all comments; no issue comments were present.
- Base: `origin/main`, merge base `2a694d70` at the first review. Revalidate before publication.
- TOOLING approved the commit/PR caller integration by mailbox after the structural Nit finding. Changes stay within the same reporting concern.
- Canonical plugins changed: `trim-comments` 3.0.0 to 3.0.1; `trim-text` 1.3.0 to 1.3.1; `commit` 1.5.0 to 1.5.1; `pr` 1.11.2 to 1.11.3. Mirrors generated with `make build`.
- The existing evaluator was extended. The final fixture moves the docstring across files and asserts that both dated notes are added diff lines. An earlier same-file fixture retained one note as unchanged diff context and was replaced before final evidence was accepted.

## Local reviews

All fresh review contexts run `gpt-6.1-sol`, high effort, window `872000`, read-only sandbox, approval `never`, web search disabled, stdin closed. No review runs repository tests. Each completed run must have exit 0, a nonempty reply and valid report shape. Generated mirrors are excluded.

| Loop and round                | Result and disposition                                                                                                                                                                                         |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Structural Nit, anti-patterns | Reviewer Nit: callers omit `Declined`. Our severity Nit: caller instructions can omit an otherwise complete trim report. Take both relay sentences and patch bumps. Behavior changes, so advance to Important. |
| Structural Nit, simplify      | Reviewer suggestion: avoid alias policy duplication. Our severity Nit: duplicated maintenance. Take the concise shared-policy reference. Comment-only edit. Three other suggestions recorded below.            |
| Structural Important          | Anti-patterns and report-only simplify completed at `d3861bb4`; no Important defects. Structural loop: clean at Important.                                                                                     |
| Focused Codex aspects         | One Nit round, five successful aspects; took two test suggestions. Ended: fixes changed no behavior.                                                                                                           |
| Comment and prose trims       | One round each; comment no-op, two prose edits taken. All declines recorded below.                                                                                                                             |
| Baseline Semgrep              | Exit 0, zero findings, no errors; baseline scan in a disposable shared clone.                                                                                                                                  |
| Lint and final full suite     | Format, lint and validate passed; locked full suite passed all 76 documents and 2,220 cases.                                                                                                                   |

Simplify completed all four angles inline in one read-only run. Recorded proposals: extracting fixture setup would also touch unchanged code; hoisting six path constructions has negligible cost; extracting the readable variant conditional adds indirection. No behavior change warranted for these suggestions. Their original labels are `suggestion`; our severity is Nit; record rather than take. No cleanup edits were made by the reviewer.

## Regression and plants

The [saved reports](2026-11-02-trim-moved-comments-evidence.json) preserve the final positive cases and the planted-policy result. Live checks are opt-in and separate from CI; they measure read-only proposal decisions and report fields, not apply-mode writes or universal model compliance. They use `gpt-6.1-sol`, low effort, window `872000`.

| Planted defect                          | Instrument                | Measured result                                                                                       | Regression home                          |
| --------------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| Treat moved/copied text as pre-existing | Live moved-note evaluator | Exit 1 at `Stale notes must be trimmed`; alias declined both stale proposals because of the exemption | `trim-text-scopes.py --moved-only`       |
| Omit one declined proposal              | Saved-report judge        | Rejected                                                                                              | `check_moved` exact expected declines    |
| Remove current-code evidence            | Saved-report judge        | Rejected                                                                                              | `check_moved` supported-warning evidence |
| Empty a decline reason                  | Saved-report judge        | Rejected                                                                                              | `check_moved` nonempty reason            |

Positive control: final alias, direct comment and prose cases passed, including an unverifiable redirect warning that must be flagged. Commit and PR reporting cases also passed. Current `_campaign_link` builds `/campaign/{code}`, so the 2020 `/legacy/CODE` note is stale. `_validate` rejects `/`, supporting the retained path-segment warning. The redirect callback implementation is unavailable, so its provider constraint remains unresolved. Every expected decline has a location and reason; source files, index and HEAD stay unchanged. The policy plant ran only in an owned skill copy; canonical skills remained unchanged.

## Checks and limits

- `error-output-guard.md`: 102 of 102 passed.
- Initial `environment-isolation.md`: 48 passed, 3 failed. The run used `make -s`, suppressing expected make output, and overlapped generator writes while fixture copies were taken. This run is invalid evidence for the final tree, not a pass. The final stable run with normal make output passed all 51 cases.
- Initial thermal checks reported no warnings. Before the full suite, wait while any `run-scrut`, `unittest discover`, `pytest` or `make test` process is present, then acquire `~/Work/projects/.locks/tooling-full-suite.d` and use `SCRUT_JOBS=2`. Hold tests if a thermal warning appears.
- Full suite, lint and version checks passed. Publication uses logical signed commits and an exact-tree comparison before push.

## Focused review and trim dispositions

The focused Nit round ran code, tests, comments, errors and types through the installed `review-pr-with-codex` 2.3.3 helper, three aspects then two. All returned schema-valid success at snapshot `20614357c21fc1525d818e2729eb031e50576f80`, head `90d9d442`. The after-scope check found no lasting changes: `scope_changed: false`, `changed: []`. A repository-local helper correctly refused to run; the installed helper was used without bypassing its guard.

Only the tests aspect reported findings. For each: reviewer label `suggestion`; our severity Nit; take missing tests for new behavior. Added the unresolved-provider case and both parent-report cases. Tests only, so the loop ends: ended: fixes changed no behavior. Code, comments, errors and types reported no findings. Structural round 2's repeated fixture-setup suggestion was already recorded, never a fixed defect recurring.

New plants: suppressing unresolved checks failed `Unverifiable warning must be flagged`. Removing decline relay from each parent produced a report without `draft:constraint`; both failed `Parent lost decline details`. Canonical skills remained unchanged while owned copies carried the plants.

Comment trim: fresh read-only Codex at low effort, no eligible changed comments or docstrings; no proposals or declines. Python prompt and fixture strings are data. Prose trim: same model/settings, three proposals. Took clearer retention wording while preserving explicit confirmation, and the README sentence simplification. Declined replacing "the branch's own" with "branch-owned": preserve plain language and the issue's wording.

The prose reviewer also declined four cuts, each retained with its reason:

- Alias reminder: preserves the shared scope/check/report handoff.
- TOOLING approval record: preserves authorization for the caller integration.
- Superseded-fixture explanation: distinguishes rejected evidence from final evidence.
- Model settings and coverage limits: confirmed against `evaluate` and `evaluate_moved`; the evaluator checks read-only reports, not apply-mode writes.

Both trims exited 0 with nonempty, complete reports. No new comment changes, cut material or unresolved classification checks remained. Full raw reports and all finding labels are in the evidence JSON.

## Baseline Semgrep and lint setup

Baseline Semgrep ran in an owned disposable `git clone --shared` at `70efd980`, with `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`, `--config auto`, and `--baseline-commit 2a694d7048750199ce8d292043156a6046299fd6`. Exit 0, 128 rules on 12 files, zero findings and `errors: []`. Defaults excluded tests and generated mirrors; this is not analysis of the Python evaluator.

`check-versions` confirmed four forward patch bumps, 61 catalog entries with matching directories, and manifest-only version ownership. Lint-and-fix runs with `--no-push`: Markdownlint and Prettier fix modes come from `make format`; ShellCheck, shfmt, actionlint, the fixture-environment guard and repository validators are enforced by Makefile targets and CI. ShellCheck, actionlint and validators have no automatic fixer. No inferred-only checks were added. Project dependencies were prepared with `corepack yarn install --immutable` after the initial formatter reported missing Yarn state.

Lint-and-fix completed with no code changes: `make format`, `make lint` and `make validate` all exited 0. Its formatter changed only pending ledger/evidence formatting; Markdownlint, Prettier, ShellCheck, shfmt, fixture guard, actionlint, JSON/plugin validators and Claude plugin validation all ran. Unresolved or skipped required lint work: none. No advisory inferred-only checks. The required full suite will repeat checks through `make test-all` with normal output. Latest fetch advanced `origin/main` to `70e3d907` with two unrelated process documents; the merge base remains `2a694d70` and changed plugin versions do not overlap.

## Final full suite and publication

The one full-suite run waited for machine-wide test processes, acquired `~/Work/projects/.locks/tooling-full-suite.d`, checked thermal status again, and ran `make test-all` with `SCRUT_JOBS=2`. It exited 0: all 76 documents and 2,220 cases passed, zero failures or skips. Both `error-output-guard.md` and `environment-isolation.md` passed. Sources remained unchanged throughout the run at `fab0b67c`; only this completion record and plan status were updated afterward. The wrapper released its owned lock. No thermal warnings were reported before the run.

Completion records receive scoped Markdown/Prettier checks. The local pre-tidy backup is `fix/718-trim-moved-comments-pre-tidy`; publication requires the rebuilt feature, tests and docs commits to match its tree exactly. The ready PR and measured tidy result are handed to TOOLING, which merges. No Copilot review is requested or awaited.
