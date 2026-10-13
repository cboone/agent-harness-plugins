# Local review ledger: feature/627-default-codex-review-settings

Issue #627. Base `db9eb7e4`. Local review order: structural reviews, `review-pr-with-codex`, trims, semgrep, `lint-and-fix --no-push`.

## Step 1, round 1: `review-anti-patterns` and `/simplify`, report only

Reviewed head: `d0756ceb`.

- **`review-anti-patterns`:** through Codex, using this branch's own `codex-exec.md` path. Model `gpt-6.1-sol`, effort `high`, window `872000`, read-only sandbox, output schema `result-schema.json`. Completion checks: exit 0, non-empty reply, one JSON value, schema check passed. Result: `success`, `complete: true`, 1 Important and 1 Nit. Unverified: validators and scrut not run (no `--run-checks`); the calling session ran them.
- **`/simplify`:** read-only general-purpose subagent, Opus at `high`. 5 Important and 6 Nit.

| # | Finding | Reviewer label | Our severity | Decision |
| --- | --- | --- | --- | --- |
| 1 | Trim paths relative to the caller's directory resolve from the repository root inside Codex (both reviewers) | important / Important | Important | Fixed: pass step 1's root-relative files; pass the merge base for the default scope |
| 2 | A trim dry-run reply has no defined shape; a question or empty answer reads as "nothing to trim" | Important | Important | Fixed: require the table or exactly `No changes proposed.` |
| 3 | trim-comments' paths branch says "go to step 2", skipping the Codex step | Important | Important | Fixed: skip to the filter and continue from there |
| 4 | "Refuse to continue" on an in-tree `TMPDIR` reads as stopping the skill | Important | Nit: an agent would most likely fall back anyway | Fixed: a "When to use it" condition |
| 5 | review-pr-with-codex README says `--effort high` raises effort | Important | Important (docs drift) | Fixed: `--effort medium`, lower effort |
| 6 | Inline `jq` check duplicates the schema and accepts a non-integer `line` and non-string array items | Nit | Nit | Fixed: `references/result-check.jq`, checked against valid and invalid replies |
| 7 | `jq` missing from review-anti-patterns' requirements | Nit | Nit | Fixed |
| 8 | Reporting rules repeated in each skill and the shared reference | Nit | Nit | Fixed: kept only the skill-specific parts |
| 9 | trim-text's summarized multi-unit rows cannot be applied | Nit | Nit | Fixed: prompt asks for them in full |
| 10 | trim-text skips the whole-text reread on the Codex path | Nit | Nit | Fixed |
| 11 | Codex `failure`/`unavailable` replies are ambiguous; caller context and default-branch lookup are lost in the sandbox | Nit | Nit | Fixed: such replies fail the shape check and fall back; caller context and default branch go in the prompt |
| 12 | READMEs promise fixed settings even when started from a Codex session (Codex) | nit | Nit | Fixed |

Not taken: changing `review-until-clean`'s `--effort high` examples. They remain accurate descriptions of a high-effort run and are outside this branch's change.

Round 1 found Important findings and the fixes change agent behavior, so step 1 runs a second round.
