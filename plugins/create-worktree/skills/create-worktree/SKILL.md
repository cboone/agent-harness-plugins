---
name: create-worktree
description: >-
  Create a new git worktree, branch, and tmux window using workmux, from
  either a GitHub issue number or a task description, with a prompt injected
  into the new session. Use when the user says "create worktree", "new
  worktree", "start working on", "spin up a worktree", or asks to create a
  worktree for an issue number or a general task. Requires workmux, plus the
  gh CLI when given an issue number.
---

# Create Worktree

Create a dedicated worktree + tmux window via `workmux add`, with a prompt injected into the new agent session.

This skill creates the worktree and stops. It does not start the work. To have the new session also plan the issue, use `address-issue-in-worktree` instead.

## Options

The user may provide these options inline:

- **--issue `<number>`**: Force issue lookup, for when a task description is itself a number
- **--no-issue**: Force description handling, even if the argument looks like an issue number
- **--base `<branch>`**: Base the worktree on a specific branch instead of the repository's default branch

## Workflow

### 1. Classify the Argument

Decide what the user gave you, in this order:

1. **An issue number**: a bare integer or `#N` (e.g. `/create-worktree 42`, `/create-worktree #42`), or anything passed via `--issue N`
2. **An explicit branch name**: a string containing `/` that looks like `type/slug` (e.g. `/create-worktree feature/my-thing`) -- use as-is
3. **A task description**: anything else (e.g. `/create-worktree Fix a bug`)

`--no-issue` forces a bare integer down the description path.

If an issue number was given but `gh` is not installed or not authenticated, say so and ask whether to treat the argument as a task description instead. Do not silently fall back.

### 2. Determine the Branch Name

**From an issue number**, fetch the issue first:

```bash
gh issue view NUMBER --json number,title,labels,body,state
```

If the issue is closed, warn the user and ask whether to proceed.

Build the branch name as `TYPE/NUMBER-SLUG`:

- **TYPE**: `fix` if the labels contain "bug" or "fix", `feature` otherwise
- **SLUG**: slugify the issue title (see the rules below)

Leading with the issue number is what lets the `pr` skill link the resulting pull request back to the issue: its primary detection strategy reads `TYPE/N-description` straight out of the branch name. Without the number, `pr` falls back to searching GitHub by branch slug, which is slower and can match the wrong issue or none at all.

Examples:

- issue 42 "Add dark mode support" labeled `enhancement` -> `feature/42-add-dark-mode-support`
- issue 108 "Login fails with special chars" labeled `bug` -> `fix/108-login-fails-with-special-chars`
- issue 356 "chore: validate skill and path cross-references in bin/validate-plugins" labeled `maintenance` -> `feature/356-validate-skill-and-path-cross-references`
- issue 358 "lint-and-fix: consult project agent config before running a destructive auto-fix" labeled `bug` -> `fix/358-lint-and-fix-consult-project-agent-config`

**From a task description**, build `TYPE/SLUG`:

- **TYPE**: Use `fix` if the user mentions "fix", "bug", "patch", or similar. Use `feature` for everything else.
- **SLUG**: Slugify the description.

**Slugify rules**, applied in this order:

1. **Strip a leading conventional-commit prefix**, with or without a scope: `chore:`, `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `build:`, `ci:`, `perf:`, `style:`, and scoped forms such as `fix(auth):`. TYPE already carries that meaning, so leaving the prefix in produces contradictions like `feature/356-chore-validate-...`. A component name followed by a colon, such as `lint-and-fix:`, is not a conventional-commit type and stays.
1. Lowercase, replace spaces and special characters with hyphens, collapse consecutive hyphens, trim leading and trailing hyphens.
1. Truncate to 50 characters at a word boundary, never mid-word.
1. **Only if step 3 actually truncated**, drop the dangling fragment it left behind. Filler words are `a`, `an`, `and`, `as`, `at`, `before`, `but`, `by`, `for`, `from`, `in`, `into`, `of`, `on`, `or`, `the`, `to`, `when`, `while`, `with`, `without`. If either of the last two words is a filler word, cut from that filler word onward, and repeat. A branch ending in `-before`, `-in`, or `-in-bin` reads as if the name were cut off, because it was.

   The truncation guard matters: `Login fails with special chars` is under 50 characters, so nothing is dropped and `-with-special-chars` survives intact. Trimming unconditionally would mangle short titles that legitimately end in a prepositional phrase.

Examples:

- "create worktree for adding dark mode" -> `feature/adding-dark-mode`
- "spin up a worktree to fix the auth timeout" -> `fix/auth-timeout`
- "new worktree feature/refactor-config" -> `feature/refactor-config` (used as-is)

### 3. Compose the Prompt

**From an issue number**, pipe the `gh issue view` output through the bundled `compose-issue-prompt` script, which produces:

```text
Work on issue #NUMBER: TITLE

Labels: LABEL1, LABEL2

BODY_CONTENT
```

The script truncates a body longer than about 2000 characters at a paragraph or sentence boundary and appends a pointer to `gh issue view NUMBER`. Do not assemble this block by hand.

**From a task description**, build the prompt directly:

```text
Work on: [user's task description]

Branch: [BRANCH_NAME]
```

Keep the prompt concise -- a few sentences at most. Use the user's own description of the task as the core content.

If the user provided only a branch name with no description, derive a human-readable description from the branch name (e.g., `feature/add-dark-mode` becomes "Work on: add dark mode").

### 4. Create the Worktree

**Important:** The `workmux add` command must be fully detached from the Claude Code process. `workmux` creates tmux windows and spawns new Claude sessions, which cannot initialize while the parent Claude Code process is still running. The `launch-workmux` script handles backgrounding, detaching, waiting, and outputting the log.

**Template escaping:** `workmux` renders the prompt body through MiniJinja, so any literal `{{`, `{%`, or `{#` token in the task description (e.g. GitHub Actions `${{ inputs.x }}` expressions, Jinja/Liquid/Tera/Helm/Vue templates, Handlebars-style snippets) would otherwise be parsed as a template variable reference and rejected with `Template uses undefined variables`. The `launch-workmux` script reads the prompt from stdin, writes an escaped temporary prompt file for `workmux add -P`, and removes that temporary file after `workmux add` exits. Each escaped delimiter renders back to the literal characters, so the prompt stored at `<worktree>/.workmux/PROMPT-*.md` matches the original input.

**Invoking the scripts:** Both scripts ship with this plugin. Invoke them via `bash` followed by the quoted path:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/compose-issue-prompt"
bash "${CLAUDE_PLUGIN_ROOT}/scripts/launch-workmux"
```

These show the path form only. The runnable invocations, with their arguments, are further down.

Claude Code replaces the plugin-root placeholder with the installed plugin's absolute, version-correct directory before this file reaches you, so there is no search step and no need for a shell variable. Keeping `bash` as the command prefix keeps the command token stable across plugin versions, which is what permission allowlist rules match on.

**If the path was not substituted**, it still begins with `$` rather than `/`. Codex CLI substitutes the placeholder only in hook commands, and OpenCode does not substitute it at all. In that case locate the scripts with `**/create-worktree/**/scripts/compose-issue-prompt` and `**/create-worktree/**/scripts/launch-workmux`, prefer a match inside the harness's own installed-plugin directory, ignore any match under a `.bak` or other backup directory, confirm it with `test -x`, and use those absolute paths for the rest of the session.

In the examples below, `SCRIPTS_DIR/launch-workmux` is shorthand for the full **quoted path** shown above.

**Always pass `--base`.** `workmux`'s default base is the _current_ branch, not the repository's default branch, so running this skill from a feature branch silently stacks the new worktree on top of that branch and carries its commits along. Detect the default branch and pass it explicitly:

```bash
gh repo view --json defaultBranchRef -q '.defaultBranchRef.name'
```

**If `gh` is not available**, fall back to:

```bash
git remote show origin | grep 'HEAD branch' | sed 's/.*: //'
```

If the user passed `--base BRANCH`, use that instead. If both detection methods fail, tell the user which branch `workmux` would default to and ask before proceeding.

Then launch the worktree.

**From an issue number**, pipe the issue JSON through both scripts:

```bash
gh issue view NUMBER --json number,title,labels,body,state \
  | bash "SCRIPTS_DIR/compose-issue-prompt" \
  | bash "SCRIPTS_DIR/launch-workmux" "BRANCH_NAME" --base "BASE_BRANCH"
```

Do not pass `--chain-command` here. This skill creates the worktree and stops; `address-issue-in-worktree` is the skill that chains into `address-issue`.

This skill also does not self-assign the issue or label it "in progress". Creating a worktree is not a commitment to do the work, and the user may be setting up several at once. `address-issue-in-worktree` does claim the issue, because it starts the work.

**From a task description**, feed the prompt in directly:

```bash
bash "SCRIPTS_DIR/launch-workmux" "BRANCH_NAME" --base "BASE_BRANCH" <<'WORKMUX_PROMPT'
Work on: [user's task description]

Branch: [BRANCH_NAME]
WORKMUX_PROMPT
```

The script outputs the workmux log directly and cleans up its own log file. Verify success:

```bash
git worktree list
```

### 5. Report Success

After confirming the worktree exists in `git worktree list`, report:

- The branch name created
- The tmux window name (to help the user switch to it)
- A note that the prompt was injected into the new session
- For the issue path, the issue number and title

Then stop. Do not start the work.

## Error Handling

- If `workmux` is not installed, inform the user and suggest installing it
- If an issue number was given and `gh` is not installed or not authenticated, say so and ask whether to treat the argument as a task description
- If the issue is not found, report that and stop
- If the issue is closed, warn and ask before proceeding
- If the branch already exists and `--open-if-exists` opens it, note that the prompt is only injected on initial creation
