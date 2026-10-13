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

| # | Finding | Reviewer label | Our severity | Decision |
| --- | --- | --- | --- | --- |
| 1 | Resolved trim file names are passed back to Codex and expanded with `:(glob)` again, so `[slug]` in a name selects other files (Codex) | important | Important | Fixed: the prompt makes each path a literal file name |
| 2 | Nothing checks that the Codex trim run covered every file in scope (`/simplify` #10) | Nit | Important: a dropped file reads as nothing to trim | Fixed: the reply starts with the files classified, and missing files are classified in session |
| 3 | Shared-reference Copilot instructions describe only the progress model in general terms | Important | Nit: Copilot reviews are off until 2026-11-01 | Fixed: the bullets name the progress model |
| 4 | "A Codex session runs the skill in place" is false for review-anti-patterns' fallback order; README claims the sandbox in that case | Nit | Nit | Fixed |
| 5 | Plugin development guide's general shared-reference rule sits inside one bullet; "both plugins" is wrong for two copies | Nit | Nit | Fixed |
| 6 | `mktemp` wrapper adds nothing and defeats the permission rule | Nit | Nit | Fixed: bare `mktemp -d` |
| 7 | Missing `jq` found only after a full Codex run | Nit | Nit | Fixed: a "When to use it" condition |
| 8 | "`--files` paths made root-relative" is a no-op | Nit | Nit | Fixed |
| 9 | "Skip to step 4" in step 1 bypasses the proposal checks | Nit | Nit | Fixed: step 1 defers to the Codex section |
| 10 | trim-text forces one profile on every file in the Codex run | Nit | Nit | Fixed: `--profile` only when the user gave one |
| 11 | `--run-checks` mostly ends unverified in the sandbox | Nit | Nit | Fixed: `--run-checks` skips Codex |
| 12 | The `--window` default does not follow `--model` | Nit | Nit | Fixed: documented |
| 13 | `def strings` shadows a jq built-in | Nit | Nit | Fixed: `string_array` |
| 14 | Small `codex-exec.md` cleanups | Nit | Nit | Fixed |

Step 1 allows at most two rounds, so it ends here; the fixes go to step 2's review.
