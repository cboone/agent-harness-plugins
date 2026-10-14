# Local review ledger: feature/prevent-subagent-notifications

No issue. Base `84e83462`. Local review order: structural reviews, `review-pr-with-codex`, trims, semgrep, `lint-and-fix --no-push`.

## Step 1, round 1: `review-anti-patterns` and `/simplify`, report only

Reviewed head: `5f1ea972`.

- **`review-anti-patterns`:** installed 1.1.1 through Codex. Model `gpt-6.1-sol`, effort `high`, window `872000`, read-only sandbox, output schema `result-schema.json`. Completion checks: exit 0, non-empty reply, one JSON value, schema check passed. Result: `success`, `complete: true`, 1 Important. Unverified: scrut, `make validate` and a live cross-mode resume (no `--run-checks`); the calling session ran the tests and validators.
- **`/simplify`:** read-only general-purpose subagent, Opus at `high`. 2 Important and 11 Nits.

| #   | Finding                                                                                                                                | Reviewer label | Our severity | Decision                                                                                                                                                                     |
| --- | -------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | A resumed Codex session keeps its first `session_meta` source, so `codex exec resume` of a TUI session posts and the reverse is silent | important      | Important    | Fixed: the Codex parent's command line decides `exec` or interactive, the transcript only when the parent is not Codex; 4 scrut cases, and removing `exec` detection fails 2 |
| 2   | `TURN_ORIGIN_JQ` duplicates `TURN_JQ`'s record classification and turn boundary, and the copies disagree                               | Important      | Important    | Fixed: `is_user` and `is_result` move into `TURN_JQ`; the origin filter runs after it and uses `kind`                                                                        |
| 3   | Without `promptId`s the origin pass reads the whole transcript, contradicting the README                                               | Important      | Important    | Fixed: the pass stops at the current turn's prompt when no `promptId` came first; new `turn-without-prompt-id` case; README corrected                                        |
| 4   | Collected records keep whole tool results in memory                                                                                    | Nit            | Nit          | Fixed: each record is reduced to the fields the filter reads                                                                                                                 |
| 5   | The compaction-only fallback is untested and may be unreachable                                                                        | Nit            | Nit          | Fixed: dropped; compaction summaries are left out of the meta check only, and their `turnOrigin` still counts                                                                |
| 6   | The new predicates read `transcript_path` themselves, and `do_stop` reads it again                                                     | Nit            | Nit          | Fixed: `do_stop` reads it once and passes it                                                                                                                                 |
| 7   | Two harness predicates in a nested `if` decide one policy                                                                              | Nit            | Nit          | Fixed: one `turn_started_by_user`                                                                                                                                            |
| 8   | The pipefail comment repeats `reverse_lines`                                                                                           | Nit            | Nit          | Fixed: removed                                                                                                                                                               |
| 9   | The filter's header comment is long for its altitude                                                                                   | Nit            | Nit          | Fixed: rewritten around the boundary and origin rules; step 3's trims review it again                                                                                        |
| 10  | The README states the behavior three times, and the feature bullet carries mechanism                                                   | Nit            | Nit          | Fixed: the bullet states behavior; mechanism moved to Notes                                                                                                                  |
| 11  | The fixture's nested Codex `case` has an unreachable default                                                                           | Nit            | Nit          | Fixed: flat scenario arms                                                                                                                                                    |
| 12  | The fixture builds the same payload twice                                                                                              | Nit            | Nit          | Fixed: built once after the scenario `case`                                                                                                                                  |
| 13  | `transcript_turn` repeats the prompt and result helpers; `codex_transcript` writes an `originator` the script never reads              | Nit            | Nit          | Fixed: the helpers take optional extra fields, and the sample data drops `originator`                                                                                        |

The 30 most recent local transcripts gave the same verdicts before and after the rewrite, and a 442 MB transcript classifies in 0.007 s. `notifications.md` passes 76 cases and `notification-sounds.md` 13; lint and validation pass.

Fixes committed as `34e553b0`. Round 1 found Important findings and the fixes change behavior, so step 1 runs a second round.

## Step 1, round 2: `review-anti-patterns` and `/simplify`, report only

Reviewed head: `04674a9b`. Same reviewers and settings. Codex completion checks passed; result `success`, `complete: true`, 1 Important. `/simplify` confirmed all 13 round 1 fixes and reported 2 Important and 6 Nits; it reviewed the committed head and not the working-tree edits for finding 1 below, which were already under way.

| #   | Finding                                                                                                                                               | Reviewer label | Our severity | Decision                                                                                                                                                                                                                |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `ps` joins arguments with spaces, so `codex --cd '/tmp/sample project' exec` reads as interactive and posts (Codex)                                   | important      | Important    | Fixed: a bare word that names no command is decided by the parent's terminal, which the interactive TUI always has; new spaced-value and terminal-prompt cases                                                          |
| 2   | `codex exec --ephemeral`, which every headless caller in this repository uses, writes no transcript, and the hook returned before checking the parent | Important      | Important    | Fixed: the Codex parent decides without a transcript; new `quiet-codex-exec-ephemeral` case, which the previous script fails. A live `codex exec` with a spaced `--cd` and this branch's hook left no completion marker |
| 3   | `codex review` runs non-interactively but counted as interactive                                                                                      | Important      | Important    | Fixed with finding 1: `review` is headless; the comment names the Codex version the lists follow                                                                                                                        |
| 4   | A transcript whose `promptId`s start partway is read to its first line                                                                                | Nit            | Nit          | Fixed: any prompt without a `promptId` ends the read; recent transcripts lack `promptId` only on `/clear`                                                                                                               |
| 5   | The filter's `prompt` field and `kind == "prompt"` mean different things                                                                              | Nit            | Nit          | Fixed: the field is `message`, and `origin` is reduced when collected                                                                                                                                                   |
| 6   | README says the transcript decides only for a non-Codex parent, but a subagent source is always silent                                                | Nit            | Nit          | Fixed                                                                                                                                                                                                                   |
| 7   | README's "previous turn's first record" reads as chronological                                                                                        | Nit            | Nit          | Fixed: "newest record"                                                                                                                                                                                                  |
| 8   | Fixture dispatch by name substring can catch future scenarios                                                                                         | Nit            | Nit          | Fixed: anchored patterns                                                                                                                                                                                                |
| 9   | `transcript_turn` starts an extra `jq` to build `{promptId}`                                                                                          | Nit            | Nit          | Fixed: the id field is a literal                                                                                                                                                                                        |

Fixing finding 5 first dropped records without any origin, since jq yields no object when a field's value is empty; the meta-turn cases caught it, and the field now defaults to `null`. The 60 most recent local transcripts give the same verdicts as the first version of the filter. `notifications.md` passes 80 cases and `notification-sounds.md` 13; lint and validation pass.

Fixes committed as `7dc916d2`. Step 1 allows at most two rounds, so it ends here; the fixes go to step 2's review.

## Step 2, round 1: `review-pr-with-codex`

Reviewed snapshot `f1d82cd1` at head `73c94bc4`. Installed `review-pr-with-codex` 2.1.0 through `codex exec`, `gpt-6.1-sol` at `xhigh`, window `872000`, guide name `CLAUDE.md`. Aspects `code`, `errors`, `tests`, `comments` and `types` ran in parallel and all succeeded; `types` ran because the change reads transcript and payload shapes, and the skill runs an aspect when unsure. `simplify` was not selected. The tree check found no lasting changes.

| #   | Finding                                                                                                                                  | Reviewer label | Our severity                                                     | Decision                                                                                                                                                                                                                                                                                       |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Flattened `ps` text still misreads option values with spaces that end in a command name, such as `--cd '/tmp/sample exec'` (code, types) | important      | Important                                                        | Fixed: the command line decides only when the first argument after plain flags names a command; after an option that may take a value, or with a prompt, the parent's terminal decides. Codex sets no environment variable on hooks that could replace this (checked with a live `codex exec`) |
| 2   | Quiet assertions pass under bash 3.2 even when an alert was posted (tests)                                                               | important      | Important                                                        | Fixed: `\|\| exit 1` on the quiet, alert-expected and reset assertions; with the first version of the script, the old fixture printed `No alert` and exited 0, and the new one fails                                                                                                           |
| 3   | The `--image` comment says no command can follow, but clap stops its values at the next option (comments)                                | important      | Nit: wrong comment; its code path is replaced by finding 1's fix | Fixed: the option-skipping code and its comment are gone                                                                                                                                                                                                                                       |

New cases: an option value ending in `exec` in a terminal posts, and `codex exec` in a terminal is silent. `notifications.md` passes 82 cases and `notification-sounds.md` 13; lint and validation pass. Known trade-off, documented in the README: a `codex exec` started in a terminal with a value-taking option before `exec` posts its banner.

Findings at Important with behavior-changing fixes, so step 2 runs another round.

## Step 2, round 2: `review-pr-with-codex`

Reviewed snapshot `3cf10ef7` at head `259aade4`. Same settings and aspects; all five succeeded, and the tree check found no lasting changes.

| #   | Finding                                                                                                     | Reviewer label | Our severity | Decision                                                                |
| --- | ----------------------------------------------------------------------------------------------------------- | -------------- | ------------ | ----------------------------------------------------------------------- |
| 1   | The alias case reaches suppression through the terminal fallback, so removing `e` leaves it passing (tests) | suggestion     | Nit          | Fixed: the case runs `codex e` in a terminal; removing `e` now fails it |
| 2   | The origin filter's comment omits that records need a `promptId` (comments)                                 | suggestion     | Nit          | Fixed                                                                   |
| 3   | The README's Codex suppression claims omit the terminal exception (comments)                                | suggestion     | Nit          | Fixed: both claims point to Notes and caveats                           |

No finding at Important, so step 2 ends after this round. Fixes committed as `8ef49204`.

## Step 3: `trim-comments` and `trim-text` through Codex

Head `600bec5f`. Both as Codex dry runs: `gpt-6.1-sol`, effort `low`, window `872000`, read-only sandbox, in parallel. Both exited 0 with a reply holding the file list and a table, and every file in scope was listed. `trim-comments` used the default scope with merge base `84e83462`, leaving out `dist/`; `trim-text` got `plugins/notify/README.md`, limited to changed text, under the `none` profile. The completed plan, this ledger and the scrut document's headings were left out.

- `trim-comments`: 6 proposals. The three function headers in `notify` were rewritten to middle versions: the proposals dropped the terminal reason, the Codex version the lists follow and the per-harness rules. The two fixture comments were rewritten to keep what the stub's default terminal stands for; the comment above the payload block was deleted as proposed.
- `trim-text`: 5 proposals, all sentence splits, applied as proposed.

Committed as `d8298e96`. `notifications.md` passes 82 cases and `notification-sounds.md` 13; lint and validation pass.

## Step 4: semgrep baseline scan

`semgrep` 1.180.0, `--config auto --baseline-commit 84e83462`, in a disposable `git clone --shared` of head `951cce2a` in the session scratchpad, with `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`. 6 paths scanned; no new findings.

Coverage gap: semgrep's shell parser reports partial parsing for `plugins/notify/scripts/notify` from line 11 to the end, so the script is effectively unscanned. The same error occurs at the merge base, so it predates the branch; `shellcheck` covers the script.

## Step 5: `lint-and-fix --no-push`

The repository's documented commands: `make format`, `make build`, `make lint` and `make validate`. All exited 0, and nothing changed on disk, so no lint commit was needed. The full scrut suite passed all 28 documents. An earlier full run failed `launch-workmux.md`, which this branch does not touch; it passed on that rerun and twice more on its own, so the failure reads as intermittent under parallel load.

The local review order is complete; the branch is at the push and draft-PR gate.
