# Add create-worktree skill with prompt injection

## Context

The `create-worktree-from-issue` skill creates worktrees via `workmux add` but does not pass any context to the agent that opens in the new tmux window. Workmux supports prompt injection via `-p "text"` (inline) and `-P file` (from file). This plan adds a general-purpose `create-worktree` skill and updates `create-worktree-from-issue` to inject issue context into the new session.

## Approach

Two independent, self-contained skills (skills can't call each other -- they're just SKILL.md instructions). They share conventions but each is complete on its own.

## Files to create

### 1. `plugins/create-worktree/.claude-plugin/plugin.json`

Standard plugin metadata. Name: `create-worktree`, version `1.0.0`, category `productivity`, keywords: `git`, `tmux`, `workmux`, `worktree`.

### 2. `plugins/create-worktree/skills/create-worktree/SKILL.md`

General-purpose worktree creation skill. Workflow:

1. **Determine branch name** -- user provides explicit name or a task description to slugify (same `TYPE/SLUG` convention: `feature/` default, `fix/` for bug-related)
1. **Compose task prompt** -- build a short prompt from the user's description and branch context
1. **Create worktree** -- `workmux add BRANCH_NAME -p "PROMPT" --open-if-exists`. Do not specify `--base`; let workmux use its default. Only pass `--base` if the user explicitly requests a specific base branch.
1. **Report success** -- branch name, tmux window, note that prompt was injected

Trigger phrases: "create worktree", "new worktree", "start working on", "spin up a worktree".

Shell escaping note: instruct Claude to write the prompt to a temp file and use `-P` if the prompt contains characters that resist inline escaping.

## Files to modify

### 3. `plugins/create-worktree-from-issue/skills/create-worktree-from-issue/SKILL.md`

Add prompt injection between current steps 2 and 3. New workflow:

1. Find the Issue (unchanged)
1. Build the Branch Name (unchanged)
1. **Compose the Issue Prompt** (new) -- build prompt from issue number, title, labels, and body. Truncate body at ~2000 chars at a paragraph/sentence boundary if needed, with a note to run `gh issue view` for full details. Use `-P` (temp file) to avoid shell escaping issues with arbitrary issue body content.
1. **Create the Worktree** (updated) -- `workmux add BRANCH_NAME --open-if-exists -P PROMPT_FILE`
1. Report Success (updated) -- mention that issue context was injected

### 4. `plugins/create-worktree-from-issue/.claude-plugin/plugin.json`

Bump version from `1.0.0` to `1.1.0`.

### 5. `.claude-plugin/marketplace.json`

- Add `create-worktree` plugin entry (insert before `create-worktree-from-issue` alphabetically)
- Bump `create-worktree-from-issue` version to `1.1.0`
- Bump marketplace `metadata.version` to `1.2.0`

### 6. `CLAUDE.md`

Add `create-worktree/` to the structure diagram (before `create-worktree-from-issue/`).

### 7. `README.md`

- Add "Create Worktree" to the ToC skills line
- Add `/plugin install create-worktree@cboone/cboone-cc-plugins` to install commands
- Add "Create Worktree" skills section (before "Create Worktree from Issue")
- Update "Create Worktree from Issue" description to mention prompt injection

## Verification

- `workmux add --help` confirms `-p` and `-P` flags exist
- Create a test worktree via `/create-worktree` and verify the agent receives the prompt
- Create a test worktree from an issue via `/create-worktree-from-issue` and verify issue context appears in the new session
- Confirm `--open-if-exists` behavior: prompt only injected on initial creation (document this)
