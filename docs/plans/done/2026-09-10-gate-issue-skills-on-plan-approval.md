# Gate the issue skills on plan approval

## Context

Three problems with the current issue and worktree skills:

1. **`address-issue` does not reliably stop for approval.** Step 6 presents a plan in chat and says "Wait for the user to confirm, adjust, or reject the plan before proceeding," but that is a single unemphasized prose line with no enforcement. No skill in this repository uses plan mode: `EnterPlanMode`, `ExitPlanMode`, and the phrase "plan mode" have zero occurrences anywhere in `plugins/`.

2. **`create-worktree-from-issue` is misnamed and does less than its name implies.** It never invokes, mentions, or links `address-issue`. The prompt it injects into the new session is only `Work on issue #N: TITLE` plus labels and body. There is no chained workflow and no approval gate anywhere in the skill.

3. **`create-worktree` cannot take an issue number,** so the only way to get a worktree named after an issue is to go through the from-issue skill, which then also injects issue context you may not want.

The intended end state is three distinct, composable commands:

| Command                         | Behavior                                                                                |
| ------------------------------- | --------------------------------------------------------------------------------------- |
| `/create-worktree 42`           | Worktree + branch named from issue 42, issue context injected, then stop.               |
| `/create-worktree Fix a bug`    | Worktree + branch named from the description, task prompt injected, then stop.          |
| `/address-issue-in-worktree 42` | Same as `/create-worktree 42`, plus the new session is told to run `/address-issue 42`. |
| `/address-issue 42`             | Fetch, analyze, plan, **stop for approval**, then execute and commit.                   |

The approval gate lives in exactly one place: `address-issue`. `address-issue-in-worktree` gets the gate for free by chaining into it, because the plan is produced in the child session, not the parent.

## Design decisions

- **Gate implementation**: conditional tool use plus a hard prose gate. Claude Code gets a real edit lock via `EnterPlanMode` / `ExitPlanMode`; the `dist/codex/` and `dist/opencode/` mirrors fall back to prose. Neither `EnterPlanMode` nor `ExitPlanMode` exists in Codex CLI or OpenCode, and there is no SKILL.md frontmatter field that can request a permission mode.
- **No plan file.** The plan stays a markdown block in the conversation, as it is today.
- **Self-contained plugins.** `create-worktree` and `address-issue-in-worktree` each ship their own `compose-issue-prompt` and `launch-workmux`. Validator rule 18 requires every `${CLAUDE_PLUGIN_ROOT}/scripts/NAME` reference to resolve inside its own plugin, so cross-plugin script sharing is not available. The two copies of each script are made byte-identical and a test enforces that.

## Changes

### A. `address-issue`: make the approval gate real

**`plugins/address-issue/skills/address-issue/SKILL.md`**

Add to `## Options`:

- `--no-approval`: skip the approval stop and proceed straight from plan to execution.

`--dry-run` keeps its current meaning (present the plan and stop permanently). The three states are: default stops and resumes on approval, `--dry-run` stops permanently, `--no-approval` never stops.

Rewrite step 6 as a hard gate:

```markdown
### 6. Plan the Work

**Do not create, modify, or delete any file until the plan is approved.** This is a hard gate, not a suggestion. Asking the user a clarifying question is allowed; editing is not.

**If your harness provides plan mode** (Claude Code): call `EnterPlanMode` before exploring, do the exploration read-only, then call `ExitPlanMode` with the plan below. Wait for the approval result.

**Otherwise** (Codex CLI, OpenCode, or any harness without those tools): present the plan below, then stop and wait for the user to confirm, adjust, or reject it.

1. Explore the codebase to understand the relevant areas
1. Identify the files that need to be created, modified, or deleted
1. Present the plan
```

Keep the existing plan block format verbatim, then:

```markdown
**If `--dry-run` was specified**: stop here permanently. Do not make any changes even if the user approves.

**If `--no-approval` was specified**: skip the stop and continue to step 7. Do not call `EnterPlanMode`.
```

Enter plan mode at step 6, **not** at step 1. Steps 1 and 4 are read-only, but step 3 (`gh issue edit --add-assignee`, `gh label create`, `gh issue edit --add-label`) writes to GitHub and plan mode would block it.

Add to step 3 and to `## Error Handling`: if the session is already in plan mode when the skill starts, the status-marking commands will be blocked. Step 3 is already best-effort, so skip it, note that the issue was not marked in progress, and continue.

Update the frontmatter `description` to mention the approval stop. It is currently ~470 characters against a 1024 limit, so there is room.

**Description change** (must be byte-identical in all four places: `plugins/address-issue/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, the root `README.md` "What it does" cell, and the first paragraph of `plugins/address-issue/README.md`):

> Fetch a GitHub issue, plan the work, stop for approval, then execute changes and commit with issue references.

**`plugins/address-issue/README.md`**: add `--no-approval` to the usage examples and the options table; update the See Also link to `../address-issue-in-worktree/README.md`.

### B. `create-worktree`: accept an issue number

**`plugins/create-worktree/skills/create-worktree/SKILL.md`**

Rewrite step 1 to classify the argument first:

- A bare integer or `#N` -> **issue number**.
- A string containing `/` that looks like `type/slug` -> **explicit branch name** (existing behavior, used as-is).
- Anything else -> **task description** (existing behavior).

Add an `## Options` section with the escape hatches:

- `--issue <number>`: force issue lookup, for when a task description is itself a number.
- `--no-issue`: force description handling.
- `--base <branch>`: existing passthrough, now documented as an option.

On the issue path:

1. `gh issue view NUMBER --json number,title,labels,body,state`
2. Branch name is `TYPE/N-slug`, where `TYPE` is `fix` when the labels contain "bug" or "fix" and `feature` otherwise. **Leading with the issue number is required**: the `pr` skill's primary issue-linking strategy reads `TYPE/N-description` straight out of the branch name (`plugins/pr/skills/pr/SKILL.md:91-136`). Carry over the rationale paragraph from the from-issue skill verbatim.
3. The injected prompt is the output of `compose-issue-prompt`, not the hand-built `Work on: ...` block.

On the description path, everything stays as it is today.

Then create the worktree and **stop**. No chained instruction.

Add the `${CLAUDE_PLUGIN_ROOT}/scripts/compose-issue-prompt` invocation and its fallback glob, matching the existing `launch-workmux` treatment. The glob must keep the `/**/` segment (`**/create-worktree/**/scripts/compose-issue-prompt`) or validator rule 18b rejects it.

**Requirements**: `gh` becomes a conditional dependency, needed only for the issue path. Update the `**Requires:**` line in `plugins/create-worktree/README.md` and the External tools bullet in the root `README.md`.

**Description change** (four places):

> Create a git worktree, branch, and tmux window from an issue number or a task description, with a prompt injected using workmux.

### C. Rename `create-worktree-from-issue` to `address-issue-in-worktree`

Follow the shape of `docs/plans/done/2026-03-10-rename-write-shell-scripts-to-write-bash-scripts.md`, which is the precedent for a plugin plus skill rename.

1. `git mv plugins/create-worktree-from-issue plugins/address-issue-in-worktree`
2. `git mv plugins/address-issue-in-worktree/skills/create-worktree-from-issue plugins/address-issue-in-worktree/skills/address-issue-in-worktree`
3. `plugin.json`: `name`, `description`, `version` -> `2.0.0`
4. `.claude-plugin/marketplace.json`: `name`, `source`, `description`, `version`, and **move the entry** so the array stays alphabetical (rule 9). New position is directly after `address-issue`, since `address-issue` < `address-issue-in-worktree` < `address-review`.
5. `SKILL.md` frontmatter `name` and `description`
6. The two fallback globs become `**/address-issue-in-worktree/**/scripts/compose-issue-prompt` and `**/address-issue-in-worktree/**/scripts/launch-workmux`
7. Plugin `README.md`: title, first paragraph, trigger, usage examples, See Also

**New chained behavior.** After composing the issue prompt, append an instruction that points the new session at `address-issue`. Generate the footer from the script rather than assembling it in prose, so it is covered by scrut. The injected prompt becomes:

```text
Work on issue #42: Fix login crash

Labels: bug

BODY_CONTENT

---

Start by running this command:

/address-issue 42
```

The footer deliberately says nothing about stopping for approval. That is now `address-issue`'s default, and keeping the gate defined in one place avoids the two drifting apart.

Add a `--no-approval` passthrough: when the user runs `/address-issue-in-worktree 42 --no-approval`, the injected command becomes `/address-issue 42 --no-approval`.

Step 2 (Mark Issue In Progress) stays where it is. Creating a worktree is a commitment to the work, so claiming the issue at that point is correct, and `address-issue` re-marking it in the child session is idempotent.

**Description change** (four places):

> Create a worktree, branch, and tmux window for a GitHub issue, then have the new session run address-issue to plan the work and stop for approval.

### D. Unify the bundled scripts

The two `launch-workmux` copies have already diverged, which is the failure mode this step closes.

**`launch-workmux`**: build one superset script, then place byte-identical copies in both plugins.

- From `plugins/create-worktree/scripts/launch-workmux`: the `--base <branch>` option loop in `main` and the `cmd` array assembly in `do_launch`.
- From `plugins/create-worktree-from-issue/scripts/launch-workmux`: `worktree_path_for_branch`, `codex_pane_for_path`, `send_prompt_to_codex_pane`, and `run_workmux_with_existing_prompt_fallback`.

Everything else (`remove_file_if_present`, `write_escaped_prompt` and its MiniJinja `sed` escaping, `tmux_socket_candidates`, `resolved_tmux_env`, `run_workmux_command`, `run_workmux_and_cleanup_prompt`) is already identical.

**`compose-issue-prompt`**: copy `plugins/create-worktree-from-issue/scripts/compose-issue-prompt` to `plugins/create-worktree/scripts/`, and add one option to both copies:

- `--chain-command "<command>"`: append the `---` separator, `Start by running this command:`, and the given command. Omitted, the output is unchanged from today.

A single generic flag keeps one code path and lets `address-issue-in-worktree` vary the command (`/address-issue 42` or `/address-issue 42 --no-approval`) without the script knowing anything about `address-issue`. `create-worktree` simply never passes it.

`bin/list-shell-scripts` globs `plugins/*/scripts/*`, so the new `create-worktree/scripts/compose-issue-prompt` is linted automatically with no glob to widen.

### E. Cross-references

Every remaining occurrence of `create-worktree-from-issue` outside `docs/plans/done/`:

| File                                                                | What changes                                                                                                              |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `plugins/create-issue/README.md:46`                                 | See Also link                                                                                                             |
| `plugins/suggest-next-issue/README.md:45`                           | See Also link                                                                                                             |
| `plugins/suggest-next-issue/skills/suggest-next-issue/SKILL.md:116` | "offer to create a worktree ... via the `...` skill"                                                                      |
| `plugins/create-plugin/skills/create-plugin/SKILL.md:35`            | verb-noun naming example; swap for another plugin name                                                                    |
| `plugins/use-git/skills/use-git/references/common-operations.md:98` | branch-naming note naming both worktree skills                                                                            |
| `plugins/create-worktree/skills/create-worktree/SKILL.md:8`         | frontmatter says "use create-worktree-from-issue for that"; now stale, since create-worktree handles issue numbers itself |

`docs/plans/done/` is archival. Leave it alone, per the rename precedent.

### F. Infrastructure

**Tests** (`tests/scrut/`):

- `compose-issue-prompt.md`: add `--chain-command` cases (present, absent, and with a command containing a flag).
- `launch-workmux.md`: rename `CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN` to `ADDRESS_ISSUE_IN_WORKTREE_LAUNCH_WORKMUX_BIN` and update the eight testcase headings that carry the human name. Add `--base` cases for that copy, which now supports it.
- `repo-tooling.md`: add two testcases asserting the copies are byte-identical, resolved through `REPO_ROOT`:

  ```text
  $ cmp -s "${REPO_ROOT}/plugins/create-worktree/scripts/launch-workmux" "${REPO_ROOT}/plugins/address-issue-in-worktree/scripts/launch-workmux"
  $ cmp -s "${REPO_ROOT}/plugins/create-worktree/scripts/compose-issue-prompt" "${REPO_ROOT}/plugins/address-issue-in-worktree/scripts/compose-issue-prompt"
  ```

**`Makefile`** `SCRUT_ENV` block (lines 20-26) and **`.github/workflows/ci.yml`** `scrut-env` list (lines 85-91) must change in lockstep, as both files state:

- `COMPOSE_ISSUE_PROMPT_BIN` -> `plugins/address-issue-in-worktree/scripts/compose-issue-prompt`
- add `CREATE_WORKTREE_COMPOSE_ISSUE_PROMPT_BIN` -> `plugins/create-worktree/scripts/compose-issue-prompt`
- `CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN` -> `ADDRESS_ISSUE_IN_WORKTREE_LAUNCH_WORKMUX_BIN`, pointing at the renamed path

**Docs**:

- `AGENTS.md:85`: the prose list of script-bundling plugins. The tree example below it uses `create-worktree`, which still bundles scripts, so it stands.
- Root `README.md`: rename and reorder the Issues and Worktrees table row (display order becomes Address Issue, Address Issue in Worktree, Create Issue, Create Worktree, Suggest Next Issue), update all three descriptions, and update the External tools bullets, since `create-worktree` now needs `gh` too.
- Root `README.md:216` and `:227`: the Codex CLI and OpenCode `${CLAUDE_PLUGIN_ROOT}` caveat paragraphs name `/create-worktree-from-issue`. Rename it there.
- The `## Contents` section is section-level navigation only and does not list plugins, so it does not change.

**Generated trees**: run `make build` and commit `dist/codex/`, `dist/opencode/`, and `.agents/plugins/marketplace.json`. Validator rules 15 and 16 byte-compare the regenerated tree, and both `ci.yml:64` and `release.yml:57` fail on drift. The OpenCode mirror is keyed on the skill directory name, so the symlink `dist/opencode/skills/create-worktree-from-issue` is replaced by `dist/opencode/skills/address-issue-in-worktree`.

**Formatting**: the root README catalog tables are width-aligned and the name length changes, so run `make format` to reflow.

## Versioning

| Plugin                                                      | Version        | Reason                                |
| ----------------------------------------------------------- | -------------- | ------------------------------------- |
| `address-issue`                                             | 1.0.4 -> 1.1.0 | New gating behavior and a new flag    |
| `create-worktree`                                           | 1.1.5 -> 1.2.0 | New capability: issue numbers         |
| `create-worktree-from-issue` -> `address-issue-in-worktree` | 1.4.0 -> 2.0.0 | Rename is breaking for existing users |
| `create-issue`                                              | patch          | Cross-reference wording               |
| `suggest-next-issue`                                        | patch          | Cross-reference wording               |
| `create-plugin`                                             | patch          | Cross-reference wording               |
| `use-git`                                                   | patch          | Cross-reference wording               |

Then recompute `metadata.version` in `.claude-plugin/marketplace.json` with `bin/compute-catalog-state` (validator rule 10 fails otherwise). Current value is `catalog-M63-m93-p143-n51`; the expected new value is `catalog-M64-m91-p138-n51`, but take whatever the script prints, not this number.

Note that the rename precedent plan claimed no `metadata.version` bump was needed for a rename. That was wrong then and is wrong now: `compute-catalog-state` sums the version fields, so a major bump moves `M` and `m`.

## Verification

1. `grep -rn "create-worktree-from-issue" . --exclude-dir=docs` returns zero results. `docs/plans/done/` keeps its 23 archival hits.
2. `make build` produces no diff after being run twice, and `git status --porcelain dist/ .agents/` is empty after committing.
3. `make validate` passes, in particular rule 3 (plugin.json name equals directory basename), rule 9 (alphabetical marketplace order), rule 10 (catalog state), rule 17 (skill description budget: three descriptions grow by roughly 75 characters total against a 12000 budget), and rule 18 (both new script references resolve and both fallback globs keep the `/**/` segment).
4. `make test-scrut` passes, including the two new byte-identity testcases.
5. `make lint` passes, including `markdownlint-rule-relative-links` on the renamed plugin README paths in the four See Also sections.
6. `make test-all` as the single gate before opening a PR.
7. Run the repo-local `/check-versions` skill to confirm `plugin.json` and `marketplace.json` versions agree across all seven touched plugins.
8. Manual end-to-end, in a scratch repo with an open issue:
   - `/create-worktree 42` creates `feature/42-<slug>` with issue context injected, and stops.
   - `/create-worktree Fix a bug` creates `fix/fix-a-bug`, and stops.
   - `/address-issue-in-worktree 42` creates the same branch as the first case, and the new session's `.workmux/PROMPT-*.md` ends with `/address-issue 42`.
   - `/address-issue 42` in Claude Code enters plan mode, presents the plan through `ExitPlanMode`, and makes no edit until approval.
   - `/address-issue 42 --no-approval` runs through without stopping.
