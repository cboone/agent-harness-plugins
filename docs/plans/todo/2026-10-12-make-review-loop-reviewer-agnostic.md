# Make review-until-clean independent of the reviewer (#611)

## Context

`review-until-clean` has two hard-wired backends, Codex and Claude, and `references/backends.md` documents how to invoke, scope and parse each. Every new reviewer means another backend section (#522 asks for CodeRabbit). Issue #611 makes the loop own only scope, snapshot, ledger, fixing and stop rules, and accept any skill, slash command or shell command as `--reviewer`. This is a breaking change: `review-until-clean` goes to 3.0.0, the major version after the 2.0.0 that `main` reached while this branch was open.

Decisions taken during planning:

- **Round mode is observed, not declared.** No mode flag. If the snapshot moved while the reviewer ran, the round was an edit round: the change is recorded as that round's result, and any findings it also reported are recorded as notes and never queued for `address-review`; the next round reviews the resulting snapshot and raises any findings that still apply. A round is clean only when the run completed, nothing blocking was reported, and the snapshot did not move. Under `--report-only`, an edit is reported and never reverted.
- **Coverage is verified from the reviewer's report.** Before each round, `git add -N` is offered for untracked files, for every reviewer. Afterwards, what the reviewer says it covered is compared against the four buckets. Coverage is `full`, `partial` (naming the buckets left out), or `unverified`. A clean round with unverified coverage reports `clean, coverage unverified`.
- **The default reviewer comes from agent config.** Use a reviewer that the repository's `AGENTS.md` or `CLAUDE.md` names for `review-until-clean`. If none is named, ask once and mention that naming one avoids the question. #510 can replace the lookup later.

## Changes

### 1. `plugins/review-until-clean/skills/review-until-clean/SKILL.md`

- Frontmatter: description becomes reviewer-neutral (for example "Loop any reviewer and fix its findings until the snapshot is clean. Use for \"review until clean\"."). `argument-hint`: `--reviewer <command>`, `--effort` removed.
- Options: `--reviewer <command>` is free-form, taking a slash command or skill (`/pr-review-toolkit:review-pr`, `/review-pr-with-codex --effort high`, `/simplify`) or a shell command (`coderabbit review --agent --fresh`). The reviewer's own options go inside the value, and it takes exactly one reviewer. `--effort` is removed. The other options are unchanged.
- Invariants, rewritten:
  1. Every round reviews the whole scope (unchanged), now with coverage verified from the reviewer's report.
  1. **The loop knows each round's mode** (report or edit, observed from the snapshot) and decides cleanliness from that mode's signal. This replaces "the reviewer is read-only".
  1. **A run that does not finish is never clean.** A CLI is clean only on exit 0 with non-empty stdout. A skill or command is clean only when its report says it completed. Silence, errors and truncated output are a failed round.
  1. A clean result is bound to a content snapshot (unchanged).
- Workflow:
  - Step 2 (select the reviewer): `--reviewer`, else agent config, else ask once. Record the source.
  - Step 3 (prepare coverage): generic untracked handling, the `git add -N` offer and the index restore.
  - Step 4 (run): skills and slash commands run in-session, and shell commands run through Bash with `< /dev/null`, capturing stdout and stderr to the temporary directory. Snapshot taken immediately before and after the run.
  - Step 5 (validate): the completion signal, then a verbatim raw reply, then transcription.
  - Step 6 (record): mode, coverage, and an edit round's changed paths.
  - Steps 8 and 10: the edit-round rules.
  - Coverage, availability and severity text that points at `backends.md` is rewritten to point at the loop's own references.
- Example output and error handling move to a generic reviewer (for example `coderabbit review --agent --fresh`), with a "reviewer not found" entry.

### 2. New `references/reviewers.md`, replacing `references/backends.md`

Delete `backends.md`. The new file contains only rules that apply to every reviewer:

- **The contract:** completion signals by kind, and a transcription is never evidence.
- **How to run each kind:** in-session skill or slash command, or a shell command with `< /dev/null` and a temporary directory outside the tree. Nothing the round writes may land in the working tree.
- **Report and edit modes:** detected from the snapshot, with what each records.
- **Coverage verification:** `full`, `partial` or `unverified`. Untracked files are offered through `git add -N`.
- **The untracked-symlink rule,** moved verbatim in substance.
- **The verbatim-reply capture and fence sizing,** moved from the Claude section.
- **A generic severity mapping into Important and Nit.** Critical, high, important, blocking, P0 and P1 map to Important. Lower labels map to Nit. **Unlabelled findings map to Important**, because a reviewer that does not grade would otherwise never block.
- **Not a reviewer:** anything that needs interactive confirmation or billing approval an agent cannot give, for example `/code-review ultra`.

### 3. The other `review-until-clean` references

- **`stop-rules.md`:** a "well formed" clean rule per kind. Reword "Empty is not clean" for reviewer kinds, with the `reviewed`-echo row generalized. "Proving the rule works" covers every reviewer kind (CLI stub, skill that reports nothing, edit round), linking #524's intent without implementing its test. "What a clean result does not mean" drops "at one effort".
- **`ledger.md`:** header `Reviewer: <the --reviewer value>` and its source. Round fields `Mode: report | edit` and `Coverage: full | partial (...) | unverified`. An edit round lists changed paths. Fix the `./references/backends.md` cross-reference to point at `./reviewers.md`. Location checks no longer say "the Claude backend has no schema"; they say the transcription is the gate for any reviewer without a schema.
- **`scope-and-snapshot.md`:** generic wording only, if any backend-specific phrases remain.

### 4. `plugins/review-until-clean/README.md`, `plugin.json`, catalog and root README

- **README:** rewrite the invariants, and replace "Model diversity" with "Choosing a reviewer" (free-form, default from agent config, one per run, editing reviewers allowed). Requirements become: one reviewer, plus `git` and `jq`. Update the Usage block, option table, permissions JSON (drop the Codex- and Claude-specific allow rules) and examples.
- **`.claude-plugin/plugin.json`:** version `3.0.0` (`main` reached 2.0.0 independently while this branch was open), the new description, and the `codex` keyword dropped.
- **Description, verbatim in all three places:** `.claude-plugin/marketplace.json`, the root `README.md` catalog row and the plugin README intro.

### 5. `review-pr-with-codex` owns the Codex invocation details

- **`references/invocation.md`:** remove the sentence that defers to `review-until-clean`'s `backends.md`. Add the measured details that only existed there: the exact `codex exec review` errors against `codex-cli 0.155.1`, the stdin hang that never creates `-o`, and the schema-keyword note (no lookaround, measured against 0.157.1).
- **Version:** patch bump to 2.0.1, over the 2.0.0 `main` reached meanwhile.

### 6. Cross-references in other plugins

- **`review-anti-patterns/README.md`:** "a looping review with fixes, from another model family" becomes reviewer-neutral. Patch bump to 1.0.2, over the 1.0.1 `main` reached meanwhile.
- **Remaining hits:** check every other `grep` hit for "backend", "codex|claude" or "model family" in relation to `review-until-clean`, then fix wording only where it is now false.

### 7. Generated output and the plan file

- **Generated output:** `make build` regenerates `dist/` and `.agents/`. Commit the results.
- **The plan file:** rename this file to `docs/plans/todo/2026-10-12-make-review-loop-reviewer-agnostic.md`, and commit it with the work.

## Commits

Each is signed, references (#611), and lands at a logical boundary:

1. `docs: add plan for reviewer-agnostic review-until-clean (#611)`
1. `feat!: make review-until-clean independent of the reviewer (#611)`: covers the skill, references, README, manifest, catalog and root README.
1. `docs: move Codex invocation details into review-pr-with-codex (#611)`
1. `docs: describe review-until-clean without a fixed reviewer (#611)`: covers the other plugins' cross-references.
1. `chore: regenerate the Codex mirror (#611)`

## Related issues, handled at PR time

- **#522:** close as superseded (`--reviewer "coderabbit review --agent --fresh"`).
- **#538:** close as moot, since there is no Claude backend. The scope concern now lives in the generic coverage check.
- **#510 and #524:** stay open. Comment on them only if asked.

## Verification

- `make build`, then `make lint`, `make validate` (catalog description match and cross-references, including no dangling `backends.md` links) and `make test-scrut`. Finish with `make test-all`, and observe the final result.
- No plugin source, README or generated mirror references `backends.md` (plans and review records that describe its removal keep the name), no loop-level `--effort` option is documented (a reviewer's own `--effort` inside a quoted `--reviewer` value is expected), and no `review-until-clean` source mentions a named reviewer outside examples.
- The `check-versions` skill confirms the version bumps: review-until-clean 3.0.0, review-pr-with-codex 2.0.1 and review-anti-patterns 1.0.2.
- Read-through check of the workflow against the four invariants above. In particular, no path turns an empty, error-only or missing reply into `"findings": []`, and an edit round can never be reported clean.
