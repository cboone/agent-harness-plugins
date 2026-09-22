# New skill: review-until-clean, a pre-push review-and-fix loop

Tracks #465.

## Context

Almost all automated review in this repository happens after a pull request opens. Every finding then costs a push, a CI run, and a round trip, and the `review-in-depth` analysis of six recent branches (`docs/plans/todo/2026-09-14-new-skill-review-in-depth.md`) measured 5 to 46 external rounds per branch, with most findings created during review rather than present at the first one.

The fixer half of a local loop already exists in `address-review`. What is missing is a reviewer and a correct rule for when to stop. `review-branch` reviews committed changes only and is explicitly a report, not a fix-it pass. `review-in-depth` (#425, in progress) is a self-review using in-repo lenses, and its plan puts "choosing or configuring an external reviewer, or its effort level" out of scope. That is exactly the gap this skill fills, so the two are siblings and neither depends on the other.

`DheerG/codex-review-loop` sets out the invariants worth adopting. Every round reviews the whole scope, never just the latest patch. The reviewer is read-only and the host agent owns all edits. Empty or malformed reviewer output is not a clean result. A clean result is bound to a content snapshot, so any later edit invalidates it.

**Intended outcome:** `/review-until-clean` runs before a branch is pushed. It computes a snapshot of every local change, runs a read-only reviewer from a different model family over that whole scope, records findings in a durable ledger, fixes the ones at or above a severity threshold through `address-review`, and repeats until the reviewer returns a well-formed empty result for the snapshot actually on disk, or a round limit stops it.

## Design decisions

Settled with the user before implementation. Do not quietly revisit them.

| Decision               | Choice                                                                                                                                                      |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name                   | `review-until-clean`, category `code-review`, version `1.0.0`                                                                                               |
| Delivery               | Agent-invoked skill only. No pre-push hook. The README documents wiring one by hand; a shipped hook is a separate issue                                     |
| Backends               | Codex (`codex exec`, read-only sandbox) and Claude (`/code-review`). CodeRabbit is deferred to a follow-up issue because its `--agent` output is unverified |
| Default backend        | The model family the host is not. Codex under Claude Code, Claude under Codex CLI, Codex under OpenCode                                                     |
| Snapshot               | A bundled `scripts/review-scope` helper, with scrut coverage and CI registration                                                                            |
| Severity vocabulary    | `REVIEW.md`'s existing Important and Nit, with per-backend mapping. No fourth ladder                                                                        |
| Fix threshold          | Important by default; `--severity nit` includes everything                                                                                                  |
| Round limit            | 3 by default                                                                                                                                                |
| Declined findings      | Recorded in the ledger with a reason, carried forward across rounds, excluded from the clean check, never silently dropped                                  |
| Persistence            | A ledger at `docs/reviews/<date>-<branch>-until-clean.md`, appended per round. Never pushed, never committed by this skill                                  |
| Codex discovery budget | Fit inside the remaining headroom. No other plugin's description changes in this PR                                                                         |

## Verified backend facts

These were measured against `codex-cli 0.155.1` in this worktree on 2026-09-21 and 2026-09-22 by running the commands, not by reading documentation. They are load-bearing, and they changed the design twice.

1. **`codex exec review` cannot meet the output contract, and is not the backend.** This was the plan's original choice and three measurements ruled it out:
   - `--output-schema` is accepted and ignored. A review run with a schema returned prose as its final message, so its output cannot be validated.
   - The scope flags are mutually exclusive with each other: `error: the argument '--base <BRANCH>' cannot be used with '--uncommitted'`. No single review covers committed and uncommitted work.
   - The scope flags are mutually exclusive with a custom prompt: `error: the argument '--base <BRANCH>' cannot be used with '[PROMPT]'`, and the same for `--uncommitted` and `--commit`. So the contract cannot be supplied in instructions either.

   Any two of those have workarounds. All three together mean the subcommand gives a review this loop has no way to check.

1. **Plain `codex exec` does meet it, in one invocation.** `codex exec --sandbox read-only --ephemeral --output-schema <file> -o <file> "<prompt>"` honored the schema exactly, returning `{"findings":[],"reviewed":"snap-abc123"}`. The prompt sets the scope, so all four buckets are covered without a second pass, and `--sandbox read-only` makes the read-only invariant structural. **This replaced the two-pass design in the plan's first draft.**
1. **`codex exec review --json` emits its final message as an `item.completed` event whose `item.type` is `agent_message`.** `-o` writes that same message to a file. This holds for plain `codex exec` too, and is how the output is read.
1. **`/code-review` reviews "your branch's commits ahead of its upstream plus any uncommitted changes".** It supports effort levels `low` through `max`, `--fix`, and `--comment`. It does not read `REVIEW.md`. Claude may start it without the user typing it. Whether its scope includes untracked files is not documented; it is treated as excluded until a run shows otherwise, which is what the staging question exists for.
1. **`/code-review ultra` is billed, needs an interactive confirmation, and cannot be launched by the agent.** It is out of scope as a backend.
1. **`git init` here is affected by a global `init.templateDir`,** which makes `--initial-branch` be ignored and warns `re-init`. The scrut fixtures pass `--template=` and create the base branch with `git checkout -b`, so they do not depend on the developer's git configuration. They also pass `-c commit.gpgsign=false`, since signing is on globally here and absent in CI.

## Approach

### Plugin layout

```text
plugins/review-until-clean/
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── scripts/
│   └── review-scope
└── skills/
    └── review-until-clean/
        ├── SKILL.md
        └── references/
            ├── backends.md
            ├── scope-and-snapshot.md
            ├── ledger.md
            └── stop-rules.md
```

No `.codex-plugin/plugin.json`; rule 14 requires one only for hook plugins.

### Descriptions and the Codex discovery budget

Rule 17 is the tightest constraint on this change. `bin/validate-plugins` currently reports 62 skills costing 4,770 of 4,840 available tokens, so there are 70 tokens of headroom. The rendered inventory line for this plugin is 169 bytes before its description, which leaves **111 bytes for the routing description**.

Proposed `SKILL.md` description, measured at 101 bytes and 68 tokens, leaving 2 tokens spare:

```yaml
description: >-
  Loop a read-only reviewer and fix findings until the snapshot is clean. Use
  for "review until clean".
```

Re-measure after `make build` and use the `Codex skill inventory` line that `make validate` prints as the authority. If a reworded description does not fit, shorten it rather than touching another plugin.

Catalog description, used verbatim in `marketplace.json`, `plugin.json`, the plugin README's opening paragraph, and the root README cell. It is not charged against rule 17:

```text
Run a read-only reviewer from another model family over every local change, fix the findings at or above a severity threshold, and repeat until the exact snapshot on disk comes back clean or a round limit stops the loop.
```

### `scripts/review-scope`

A Bash helper, written under `write-bash-scripts`, that owns the two things the loop cannot afford the agent to improvise. Default mode prints one JSON object; `--schema` prints the findings schema instead.

```text
review-scope [--base <ref>]   # {head, base, merge_base, snapshot, committed[], staged[], unstaged[], untracked[]}
review-scope --schema         # the JSON Schema the Codex backend passes to --output-schema
review-scope -h | --help
```

The snapshot must be **representation-independent**: it is a digest over `HEAD`, the resolved base commit, and the sorted set of `(path, blob hash)` pairs for every path in the union of `git diff --name-only HEAD` and `git ls-files --others --exclude-standard`, with deleted paths recorded as deleted. Hashing `git status` output or `git diff HEAD` alone is wrong, because `git add -N` moves a file from untracked to tracked without changing a byte of content and would falsely invalidate a clean result. Content hashes come from `git hash-object`, which is already verified to work here.

`--schema` keeps the JSON in the one file the skill already has to locate, instead of adding a second `${CLAUDE_PLUGIN_ROOT}` lookup for an asset. Emit it from a quoted heredoc, the way `plugins/create-worktree/scripts/compose-issue-prompt` emits its usage text.

Locate the script as `${CLAUDE_PLUGIN_ROOT}/scripts/review-scope`, per rule 18, with the repository's documented named-glob fallback and `test -x` confirmation, because Codex CLI substitutes the placeholder only in hook commands and OpenCode does not substitute it at all. Follow `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md` for the exact wording.

### `SKILL.md`

Sections in the repository's order: H1 and summary, `## Options`, `## Skill dependencies`, `## Workflow`, `## Key Conventions`, `## Reference Navigation`, `## Example Output`, `## Error Handling`.

#### Options

- **--reviewer `<codex|claude>`**: choose the backend instead of taking the model-diverse default
- **--base `<ref>`**: compare committed changes against this ref instead of the merge base with the default branch
- **--effort `<low|medium|high|max>`**: effort for the Claude backend
- **--severity `<important|nit>`**: lowest severity the loop fixes; default `important`
- **--max-rounds `<n>`**: cap the rounds; default 3
- **--report-only**: run one round, write the ledger, change nothing
- **--no-save**: write the ledger to a temporary path instead of `docs/reviews/`

#### Skill dependencies

```markdown
## Skill dependencies

- **Required:** `address-review`
- **Optional:** None
```

Every use written as "Invoke the `address-review` skill", with the repository's missing-required-skill message before the first fix.

#### Workflow

1. **Resolve scope.** Run `review-scope`. Record `head`, `base`, `snapshot`, and the four file lists. With an empty scope, report that there is nothing to review and stop.
1. **Select the backend.** Take `--reviewer`, or pick the family the host is not. Confirm the backend is installed and authenticated. If the chosen one is unavailable, say so, name the fallback, and record the substitution in the ledger.
1. **Check coverage.** Compare the backend's scope against the resolved scope. For the Codex backend, both passes together cover it. For the Claude backend, if untracked files are in scope, ask once whether to stage them with `git add -N` so the reviewer can see them, or to exclude them. Restore the index with `git reset -- <paths>` after the round. Use the structured-question capability where it exists, and a numbered list otherwise.
1. **Run the reviewer, read-only.** The reviewer never edits. For Codex, run the `--base` and `--uncommitted` passes with `--json`, `--output-schema "$(review-scope --schema)"`, and `-o`, then merge. For Claude, run `/code-review` at the chosen effort **without** `--fix`; under a non-Claude host, run it through `claude -p` with `Edit`, `Write`, and `NotebookEdit` disallowed.
1. **Validate the output.** Parse into the findings schema. Empty output, a non-zero exit, a truncated stream, or output that does not parse is a **failed round**, never a clean one. Report the failure and stop; do not retry silently.
1. **Record the round.** Append a round section to the ledger with the snapshot it reviewed, the backend and passes used, the coverage, and every finding with a stable identifier and a mapped severity.
1. **Apply carried declines.** Match this round's findings against declines recorded in earlier rounds. A match is marked declined with its original reason, not re-asked.
1. **Decide.** A round is clean when the output was well formed, no finding at or above the threshold remains undeclined, and `review-scope` still reports the snapshot the review ran against. Otherwise continue.
1. **Fix.** Invoke the `address-review` skill on the ledger, with items below the threshold pre-skipped and a parent continuation block. Never push.
1. **Loop.** Recompute the snapshot. If it did not change and findings remain, the loop cannot converge: stop with `decisions-needed`. Otherwise start the next round, up to `--max-rounds`.
1. **Report.** Print the status line, the ledger path, and the coverage.

#### Terminal statuses

`Review-until-clean status: clean | clean-with-declines | decisions-needed | stopped | failed`, each followed by its coverage. A clean result that excluded untracked files is reported as `clean, partial scope`, never as plain `clean`.

### References

| File                    | Covers                                                                                                                                                |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `backends.md`           | Per-backend invocation, the verified flag list, why `codex exec review` is not usable, output parsing, severity mapping, availability and auth checks |
| `scope-and-snapshot.md` | What the snapshot covers, why it is representation-independent, the `git add -N` interaction, and how to check the script by hand                     |
| `ledger.md`             | The document format, round sections, the finding schema, statuses, and the handoff shape `address-review` consumes                                    |
| `stop-rules.md`         | The clean rule, malformed and empty output, carried declines and convergence, the round limit, and the terminal statuses                              |

Severity mapping in `backends.md`:

| Backend | Reviewer severity        | Mapped to |
| ------- | ------------------------ | --------- |
| Claude  | Important                | Important |
| Claude  | Nit, Pre-existing        | Nit       |
| Codex   | P0, P1                   | Important |
| Codex   | P2 and below, unlabelled | Nit       |

### README and catalog

- `plugins/review-until-clean/README.md`: opening paragraph is the catalog description verbatim, then `**Type:** Skill` and `**Trigger:** /review-until-clean`, `## Installation` linking `../../README.md#install`, `## What It Does` stating the four invariants, `## Requirements` naming `codex` or `claude`, `## Usage` with the options table, `## Recommended Permissions` covering the git reads plus `Bash(codex exec *)`, `## Examples`, and `## See Also` linking `address-review`, `review-branch`, `review-in-depth` once it exists, `plant-defects`, and `../../README.md`.
- `.claude-plugin/marketplace.json`: one entry with the nine alphabetized keys and no `version`, inserted between `review-plan` and `scaffold-go-cli`.
- Root `README.md`: one row in the Code Review table immediately after `Review Plan`, plus an `**External tools:**` bullet naming `codex` and `claude` as the backends. Do not touch `## Contents`.

### Tests

`tests/scrut/review-scope.md`, written under `write-scrut-tests`, calling the script through `"${REVIEW_SCOPE_BIN}"` and working in `$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")`. Fixture repositories need `-c user.name`, `-c user.email`, and `-c commit.gpgsign=false`, since commits are signed by default here.

Cases: an empty scope; a staged change; an unstaged change; an untracked file; a deleted file; **the snapshot unchanged across `git add -N`**; the snapshot changed by a one-byte edit; the snapshot changed by a new commit; `--schema` output passing `jq empty`; `--help`; and an unknown flag exiting non-zero.

Register `REVIEW_SCOPE_BIN` in the `SCRUT_ENV` block in `Makefile` and in the matching `scrut-env` list in `.github/workflows/ci.yml`, where the value must start with `./`. A local-only registration leaves CI testing a different environment.

### Repository bookkeeping

1. Manifest version exactly `1.0.0`; `release.yml` fails a new plugin at any other value.
1. `make build`, then commit `.agents/plugins/marketplace.json`, `dist/codex/plugins/review-until-clean/`, and the `dist/opencode/skills/review-until-clean` symlink. Never hand-edit them.
1. Keep every `./references/...` path resolvable; declare illustrative paths with `<!-- validate-plugins: ignore ... -->`.
1. Use the `check-versions` skill before opening the PR.

## Verification

### Mechanical

- `make test-all` passes: `lint`, `validate`, and `test-scrut`. Observe the final result before reporting a pass.
- `make validate` prints a `Codex skill inventory` line that is at or under 4,840 tokens. Record the exact number in this plan's done copy.
- `make build` leaves `git status --porcelain dist/ .agents/` empty.
- `shellcheck` and `shfmt -d` pass on `scripts/review-scope` through `bin/list-shell-scripts`.

### Behavioral

CI cannot answer whether the loop is correct. Run these and record the results.

1. **Snapshot stability.** In a scratch repository, create an untracked file, record the snapshot, run `git add -N`, and confirm the snapshot is unchanged. Then change one byte and confirm it changes. This is the invariant the scrut suite encodes; run it by hand once first.
1. **Full-scope control, the invariant most likely to regress.** Put one defect in a committed change and a second in an untracked file. Run one round and confirm both are reported. Following `plant-defects`, record a plant table of scope, defect, reported, and verified. A round that reports only the committed defect means the prompt is not naming the untracked paths.
1. **Not-clean positive control.** Confirm the loop refuses to report clean on a reviewer that returns nothing: point the backend at a stub that exits zero with empty stdout, and confirm the status is `failed`, not `clean`. Repeat with malformed output and with a non-zero exit.
1. **Snapshot invalidation.** Reach a clean round, edit a file before the final check, and confirm the run does not report clean.
1. **Convergence with a decline.** Decline a finding in round 1 and confirm round 2 marks it declined from the ledger instead of re-asking, and that the run ends `clean-with-declines` rather than looping to the round limit.
1. **Claude backend scope.** Two questions are still open, and `backends.md` records both as open rather than guessing: whether `/code-review` sees untracked files, and whether a ref-range target keeps uncommitted changes in scope or replaces them. Until the second is answered, a branch whose upstream differs from its base either runs two rounds or reports partial scope.
1. **Codex `--output-schema`.** Done, and it changed the design. See the verified facts above.
1. **Dogfood.** Done on 2026-09-22, and it changed the design again. One round was run by hand using the documented Codex invocation, over this branch's real scope (0 committed, 0 staged, 5 unstaged, 19 untracked). Results:
   - The output came back schema-valid, with `reviewed` equal to the snapshot `review-scope` had reported. The Codex backend meets its contract.
   - **Full-scope control passed for free.** Both findings were in untracked files, which no diff contains. That is the first invariant working on real input, not a fixture.
   - It found two genuine Important defects, both in the Claude backend's own specification, and both were fixed:
     1. `/code-review` emits no structured output and does not echo the snapshot, so step 5 as first written would have rejected every Claude review as malformed and the default Codex CLI path would always have ended `failed`. The contract now separates "findings reach the schema", which may be by transcription, from "a completed review is distinguishable from a crashed one", which may never rest on a transcription.
     1. `/code-review` measures from the branch's upstream, not the merge base, so on a pushed branch a no-target run reviews none of the committed work while still looking complete. Step 3 now compares `@{upstream}` against the base and either passes a `<base>...HEAD` target or records the bucket as not covered.
   - An empty bucket rendered as `git diff <sha> <sha>` in the prompt, which invites the reviewer to think the scope is smaller than it is. `backends.md` now says to omit empty buckets.
1. **Remaining behavioral checks.** The not-clean positive control, snapshot invalidation, and convergence-with-a-decline are loop behaviors rather than script behaviors, so they need the plugin installed and the skill driven end to end. Run them on the first real use and record the results here.

## Risks

- **Codex discovery budget.** This plugin consumes 68 of the 70 remaining tokens under rule 17. The catalog is effectively full, and the next skill added will not fit without tightening the largest routing descriptions. File that as a follow-up issue rather than doing it here.
- **The two backends are not equally trustworthy.** Codex is schema-constrained, echoes the snapshot, and covers the whole scope in one run. Claude does none of those: its findings are transcribed by the host, and its scope can silently omit committed work on a pushed branch. Both are usable, and the skill says which signal carries the weight for each, but a clean result from Codex is a stronger claim than a clean result from Claude. The control is that coverage is reported rather than assumed.
- **A clean result is still a sample.** One reviewer pass is not proof the branch is defect-free. The report states coverage, matching `review-in-depth`'s rule.
- **`address-review` asks for confirmation.** Its step 3 stalls an unattended loop. This skill is an interactive pre-push gate, so one confirmation per round is acceptable; say so in the README rather than working around it.
- **Index mutation.** `git add -N` for the Claude backend changes the user's index. It is reversible, asked for once, and recorded, and the snapshot is designed not to move because of it.

## Out of scope

- A pre-push git hook. The README documents wiring one by hand.
- The CodeRabbit backend, until its `--agent` output has been observed.
- `/code-review ultra`, which is billed and cannot be agent-launched.
- Changing `review-branch`, `address-review`, or anything in `review-in-depth` (#425).
- Tightening other plugins' routing descriptions.

## Follow-ups to file

- CodeRabbit CLI as a third backend, once `cr --agent` output has been captured.
- An optional pre-push hook for `review-until-clean`.
- Tighten the largest routing descriptions; rule 17 has no room for the next skill.

## Commits

1. `feat: add the review-until-clean plugin skeleton and catalog entry (#465)`
1. `feat: add the review-scope helper with scrut coverage (#465)`
1. `feat: add the review-until-clean workflow and references (#465)`
1. `docs: add the review-until-clean README and root catalog row (#465)`
1. `chore: regenerate the Codex and OpenCode mirrors (#465)`
