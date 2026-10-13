# Local review ledger: feature/627-default-codex-review-settings

Issue #627. Base `db9eb7e4`. Local review order: structural reviews, `review-pr-with-codex`, trims, semgrep, `lint-and-fix --no-push`.

## Step 1, round 1: `review-anti-patterns` and `/simplify`, report only

Reviewed head: `d0756ceb`.

- **`review-anti-patterns`:** through Codex, using this branch's own `codex-exec.md` path. Model `gpt-6.1-sol`, effort `high`, window `872000`, read-only sandbox, output schema `result-schema.json`. Completion checks: exit 0, non-empty reply, one JSON value, schema check passed. Result: `success`, `complete: true`, 1 Important and 1 Nit. Unverified: validators and scrut not run (no `--run-checks`); the calling session ran them.
- **`/simplify`:** read-only general-purpose subagent, Opus at `high`. 5 Important and 6 Nit.

| #   | Finding                                                                                                               | Reviewer label        | Our severity                                     | Decision                                                                                                   |
| --- | --------------------------------------------------------------------------------------------------------------------- | --------------------- | ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| 1   | Trim paths relative to the caller's directory resolve from the repository root inside Codex (both reviewers)          | important / Important | Important                                        | Fixed: pass step 1's root-relative files; pass the merge base for the default scope                        |
| 2   | A trim dry-run reply has no defined shape; a question or empty answer reads as "nothing to trim"                      | Important             | Important                                        | Fixed: require the table or exactly `No changes proposed.`                                                 |
| 3   | trim-comments' paths branch says "go to step 2", skipping the Codex step                                              | Important             | Important                                        | Fixed: skip to the filter and continue from there                                                          |
| 4   | "Refuse to continue" on an in-tree `TMPDIR` reads as stopping the skill                                               | Important             | Nit: an agent would most likely fall back anyway | Fixed: a "When to use it" condition                                                                        |
| 5   | review-pr-with-codex README says `--effort high` raises effort                                                        | Important             | Important (docs drift)                           | Fixed: `--effort medium`, lower effort                                                                     |
| 6   | Inline `jq` check duplicates the schema and accepts a non-integer `line` and non-string array items                   | Nit                   | Nit                                              | Fixed: `references/result-check.jq`, checked against valid and invalid replies                             |
| 7   | `jq` missing from review-anti-patterns' requirements                                                                  | Nit                   | Nit                                              | Fixed                                                                                                      |
| 8   | Reporting rules repeated in each skill and the shared reference                                                       | Nit                   | Nit                                              | Fixed: kept only the skill-specific parts                                                                  |
| 9   | trim-text's summarized multi-unit rows cannot be applied                                                              | Nit                   | Nit                                              | Fixed: prompt asks for them in full                                                                        |
| 10  | trim-text skips the whole-text reread on the Codex path                                                               | Nit                   | Nit                                              | Fixed                                                                                                      |
| 11  | Codex `failure`/`unavailable` replies are ambiguous; caller context and default-branch lookup are lost in the sandbox | Nit                   | Nit                                              | Fixed: such replies fail the shape check and fall back; caller context and default branch go in the prompt |
| 12  | READMEs promise fixed settings even when started from a Codex session (Codex)                                         | nit                   | Nit                                              | Fixed                                                                                                      |

Not taken: changing `review-until-clean`'s `--effort high` examples. They remain accurate descriptions of a high-effort run and are outside this branch's change.

Round 1 found Important findings and the fixes change agent behavior, so step 1 runs a second round.

## Step 1, round 2: `review-anti-patterns` and `/simplify`, report only

Reviewed head: `221d5844`. Same reviewers and settings. Codex completion checks passed; result `success`, `complete: true`, 1 Important. `/simplify` confirmed every round 1 fix, and reported 1 Important and 13 Nits.

| #   | Finding                                                                                                                                | Reviewer label | Our severity                                       | Decision                                                                                       |
| --- | -------------------------------------------------------------------------------------------------------------------------------------- | -------------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 1   | Resolved trim file names are passed back to Codex and expanded with `:(glob)` again, so `[slug]` in a name selects other files (Codex) | important      | Important                                          | Fixed: the prompt makes each path a literal file name                                          |
| 2   | Nothing checks that the Codex trim run covered every file in scope (`/simplify` #10)                                                   | Nit            | Important: a dropped file reads as nothing to trim | Fixed: the reply starts with the files classified, and missing files are classified in session |
| 3   | Shared-reference Copilot instructions describe only the progress model in general terms                                                | Important      | Nit: Copilot reviews are off until 2026-11-01      | Fixed: the bullets name the progress model                                                     |
| 4   | "A Codex session runs the skill in place" is false for review-anti-patterns' fallback order; README claims the sandbox in that case    | Nit            | Nit                                                | Fixed                                                                                          |
| 5   | Plugin development guide's general shared-reference rule sits inside one bullet; "both plugins" is wrong for two copies                | Nit            | Nit                                                | Fixed                                                                                          |
| 6   | `mktemp` wrapper adds nothing and defeats the permission rule                                                                          | Nit            | Nit                                                | Fixed: bare `mktemp -d`                                                                        |
| 7   | Missing `jq` found only after a full Codex run                                                                                         | Nit            | Nit                                                | Fixed: a "When to use it" condition                                                            |
| 8   | "`--files` paths made root-relative" is a no-op                                                                                        | Nit            | Nit                                                | Fixed                                                                                          |
| 9   | "Skip to step 4" in step 1 bypasses the proposal checks                                                                                | Nit            | Nit                                                | Fixed: step 1 defers to the Codex section                                                      |
| 10  | trim-text forces one profile on every file in the Codex run                                                                            | Nit            | Nit                                                | Fixed: `--profile` only when the user gave one                                                 |
| 11  | `--run-checks` mostly ends unverified in the sandbox                                                                                   | Nit            | Nit                                                | Fixed: `--run-checks` skips Codex                                                              |
| 12  | The `--window` default does not follow `--model`                                                                                       | Nit            | Nit                                                | Fixed: documented                                                                              |
| 13  | `def strings` shadows a jq built-in                                                                                                    | Nit            | Nit                                                | Fixed: `string_array`                                                                          |
| 14  | Small `codex-exec.md` cleanups                                                                                                         | Nit            | Nit                                                | Fixed                                                                                          |

Step 1 allows at most two rounds, so it ends here; the fixes go to step 2's review.

## Step 2, round 1: `review-pr-with-codex`

Reviewed snapshot `2e377ed2` at head `28b56bd3`. Installed `review-pr-with-codex` 2.0.3 through `codex exec`, `gpt-6.1-sol` at `xhigh`, window from the global Codex config. Aspects `code`, `errors`, `tests`, `comments` and `types` ran in parallel and all succeeded; `simplify` was not selected. The tree check found no lasting changes.

| #   | Finding                                                                                                                    | Reviewer label | Our severity | Decision                                                                                                                       |
| --- | -------------------------------------------------------------------------------------------------------------------------- | -------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| 1   | The subagent fallback cannot ask for a base branch, so it returns `unavailable` where the old in-session flow asked (code) | important      | Important    | Fixed: the calling session resolves the default branch before either delegated path                                            |
| 2   | No test exercises `result-check.jq` (tests)                                                                                | important      | Important    | Fixed: `tests/scrut/result-check.md`, 14 cases, registered in the Makefile and CI; removing the invariant line fails 2 of them |
| 3   | The check accepts `complete: true` with a non-success status or a non-empty `not_reviewed` (types)                         | important      | Important    | Fixed: the check enforces the invariant                                                                                        |
| 4   | The plan says omitted flags fell back to the user's settings, though model and effort were already set (comments)          | suggestion     | Nit          | Fixed                                                                                                                          |

Findings at Important with behavior-changing fixes, so step 2 runs another round.

## Step 2, round 2: `review-pr-with-codex`

Reviewed snapshot `ed119301` at head `6adffbda`. Same settings and aspects; all five succeeded, and the tree check found no lasting changes.

| #   | Finding                                                                                                            | Reviewer label | Our severity                                                                                                               | Decision                                                                                                       |
| --- | ------------------------------------------------------------------------------------------------------------------ | -------------- | -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| 1   | No test drives the Codex fallback dispatch: stubbed Codex failures, several JSON values, `failure` replies (tests) | important      | Nit: the dispatch is agent prose with no runner to drive; each check it names is executable, and the `jq` check is covered | Recorded, not fixed. Covering it needs a new runner script, a design change. Downgrade reported for a decision |
| 2   | README promises the window to Codex subagents, which may keep the session's settings (comments)                    | suggestion     | Nit                                                                                                                        | Fixed                                                                                                          |
| 3   | A `success` reply may have an empty `reviewed` or `report` (types)                                                 | suggestion     | Nit                                                                                                                        | Fixed, with 3 scrut cases                                                                                      |

No finding at Important by our severity, so step 2 ends after this round, pending the decision on the downgrade.

Decision: Chris accepted the downgrade of step 2 round 2's finding 1 and the move to step 3.

## Step 3: `trim-comments` and `trim-text` through Codex

Head `08285906`. Both as Codex dry runs through this branch's own path: `gpt-6.1-sol`, effort `low`, window `872000`, read-only sandbox, in parallel. Both exited 0 with a reply holding the file list and a table, and every file in scope was listed. `trim-comments` used the default scope with merge base `db9eb7e4`; `trim-text` got the 15 canonical prose files the branch changed, limited to changed text.

- `trim-comments`: 2 proposals. The `result-check.jq` header was rewritten to a middle version that keeps its usage line; the `codex-aspects` window comment was kept, since the proposal dropped that 872000 is the model's largest window.
- `trim-text`: 13 proposals. 12 applied as proposed; the `codex-exec.md` settings bullet was kept, since the rewrite was no shorter and less clear.

Committed as `361e824b`.

## Step 4: semgrep baseline scan

`semgrep` 1.180.0, `--config auto --baseline-commit db9eb7e4`, in a disposable `git clone --shared` of head `9757e969` in the session scratchpad, with `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`. 29 paths scanned; no new findings.

Coverage gap: semgrep's shell parser reports partial parsing for `plugins/review-pr-with-codex/scripts/codex-aspects` (lines 3 to the end, so effectively unscanned) and four short spans of `bin/build-shared-references`. Both errors occur at the merge base too, so they predate the branch; `shellcheck` covers both scripts.

## Step 5: `lint-and-fix --no-push`

The repository's documented commands: `make format`, `make build`, `make lint` and `make validate`. All exited 0, and nothing changed on disk, so no lint commit was needed. The full scrut suite last passed after step 2 round 2 (28 documents); step 3 changed only prose and one comment, and the affected `result-check` and `build-shared-references` documents passed again after it.

The local review order is complete; the branch is at the push and draft-PR gate.
