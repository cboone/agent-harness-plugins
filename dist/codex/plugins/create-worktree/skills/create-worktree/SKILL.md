---
name: create-worktree
description: >-
  Create a git worktree, branch, and tmux window with a task prompt using
  workmux.
---

# Create Worktree

Create a dedicated worktree + tmux window via `workmux add`, with a task prompt injected into the new agent session.

## Workflow

### 1. Determine the Branch Name

The user provides either:

- **An explicit branch name** (e.g., "create worktree feature/my-thing") -- use as-is
- **A task description** (e.g., "create a worktree for adding dark mode") -- construct a branch name using the `TYPE/SLUG` format

**Branch naming rules (`TYPE/SLUG`):**

- **TYPE**: Use `fix` if the user mentions "fix", "bug", "patch", or similar. Use `feature` for everything else.
- **SLUG**: Slugify the description: lowercase, replace spaces and special characters with hyphens, collapse consecutive hyphens, trim leading/trailing hyphens, truncate to 50 characters at a word boundary.

Examples:

- "create worktree for adding dark mode" -> `feature/adding-dark-mode`
- "spin up a worktree to fix the auth timeout" -> `fix/auth-timeout`
- "new worktree feature/refactor-config" -> `feature/refactor-config` (used as-is)

### 2. Compose the Task Prompt

Build a prompt string that gives the new agent context about its task:

```text
Work on: [user's task description]

Branch: [BRANCH_NAME]
```

Keep the prompt concise -- a few sentences at most. Use the user's own description of the task as the core content.

If the user provided only a branch name with no description, derive a human-readable description from the branch name (e.g., `feature/add-dark-mode` becomes "Work on: add dark mode").

### 3. Create the Worktree

**Important:** The `workmux add` command must be fully detached from the Claude Code process. `workmux` creates tmux windows and spawns new Claude sessions, which cannot initialize while the parent Claude Code process is alive. The `launch-workmux` script handles backgrounding, detaching, waiting, and outputting the log.

**Template escaping:** `workmux` renders the prompt body through MiniJinja, so any literal `{{`, `{%`, or `{#` token in the task description (e.g. GitHub Actions `${{ inputs.x }}` expressions, Jinja/Liquid/Tera/Helm/Vue templates, Handlebars-style snippets) would otherwise be parsed as a template variable reference and rejected with `Template uses undefined variables`. The `launch-workmux` script reads the prompt from stdin, writes an escaped temporary prompt file for `workmux add -P`, and removes that temporary file after `workmux add` exits. Each escaped delimiter renders back to the literal characters, so the prompt stored at `<worktree>/.workmux/PROMPT-*.md` matches the original input.

**Locating the script:** At the start of your session, locate the script by searching for `**/create-worktree/scripts/launch-workmux`. Note the absolute path and use it with `bash` as the command prefix in all subsequent invocations. Do not use a shell variable, since shell state does not persist between commands.

In the example below, `SCRIPTS_DIR/launch-workmux` is a placeholder for the script's **quoted absolute path** (e.g., `"/absolute/path/to/plugins/create-worktree/scripts/launch-workmux"`). Always invoke via `bash` followed by the quoted path. This ensures the command token is `bash`, which matches stable allowlist patterns regardless of the plugin's installed path or version.

Do not specify `--base`. Let workmux use its default. Only pass `--base BRANCH` if the user explicitly requests a specific base branch.

Then launch the worktree:

```bash
bash "SCRIPTS_DIR/launch-workmux" "BRANCH_NAME" <<'WORKMUX_PROMPT'
Work on: [user's task description]

Branch: [BRANCH_NAME]
WORKMUX_PROMPT
```

If the user requested a specific base branch:

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

### 4. Report Success

After confirming the worktree exists in `git worktree list`, report:

- The branch name created
- The tmux window name (to help the user switch to it)
- A note that the task prompt was injected into the new session

## Error Handling

- If `workmux` is not installed, inform the user and suggest installing it
- If the branch already exists and `--open-if-exists` opens it, note that the prompt is only injected on initial creation
