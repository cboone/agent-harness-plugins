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

| # | Finding | Reviewer label | Our severity | Decision |
| --- | --- | --- | --- | --- |
| 1 | `ps` joins arguments with spaces, so `codex --cd '/tmp/sample project' exec` reads as interactive and posts (Codex) | important | Important | Fixed: a bare word that names no command is decided by the parent's terminal, which the interactive TUI always has; new spaced-value and terminal-prompt cases |
| 2 | `codex exec --ephemeral`, which every headless caller in this repository uses, writes no transcript, and the hook returned before checking the parent | Important | Important | Fixed: the Codex parent decides without a transcript; new `quiet-codex-exec-ephemeral` case, which the previous script fails. A live `codex exec` with a spaced `--cd` and this branch's hook left no completion marker |
| 3 | `codex review` runs non-interactively but counted as interactive | Important | Important | Fixed with finding 1: `review` is headless; the comment names the Codex version the lists follow |
| 4 | A transcript whose `promptId`s start partway is read to its first line | Nit | Nit | Fixed: any prompt without a `promptId` ends the read; recent transcripts lack `promptId` only on `/clear` |
| 5 | The filter's `prompt` field and `kind == "prompt"` mean different things | Nit | Nit | Fixed: the field is `message`, and `origin` is reduced when collected |
| 6 | README says the transcript decides only for a non-Codex parent, but a subagent source is always silent | Nit | Nit | Fixed |
| 7 | README's "previous turn's first record" reads as chronological | Nit | Nit | Fixed: "newest record" |
| 8 | Fixture dispatch by name substring can catch future scenarios | Nit | Nit | Fixed: anchored patterns |
| 9 | `transcript_turn` starts an extra `jq` to build `{promptId}` | Nit | Nit | Fixed: the id field is a literal |

Fixing finding 5 first dropped records without any origin, since jq yields no object when a field's value is empty; the meta-turn cases caught it, and the field now defaults to `null`. The 60 most recent local transcripts give the same verdicts as the first version of the filter. `notifications.md` passes 80 cases and `notification-sounds.md` 13; lint and validation pass.

Fixes committed as `7dc916d2`. Step 1 allows at most two rounds, so it ends here; the fixes go to step 2's review.
