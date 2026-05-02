---
name: create-worktree
description: >-
  Create a new git worktree, branch, and tmux window using workmux, with a
  task prompt injected into the new session. Use when the user says "create
  worktree", "new worktree", "start working on", "spin up a worktree", or
  asks to create a worktree for a general task (not tied to a specific GitHub
  issue -- use create-worktree-from-issue for that). Requires workmux to be
  installed.
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

**Template escaping:** `workmux` renders the prompt body through MiniJinja, so any literal `{{`, `{%`, or `{#` token in the task description (e.g. GitHub Actions `${{ inputs.x }}` expressions, Jinja/Liquid/Tera/Helm/Vue templates, Handlebars-style snippets) would otherwise be parsed as a template variable reference and rejected with `Template uses undefined variables`. The `launch-workmux` script rewrites the prompt file in place before invoking `workmux add`, replacing each delimiter with a `{{ "..." }}` expression that renders back to the literal characters. The rewrite happens atomically (write to a sibling temp file, then `mv` over the original), so `workmux` always sees a complete file. The rendered prompt stored at `<worktree>/.workmux/PROMPT-*.md` matches the original input verbatim, so the new agent session sees the prompt unchanged. Because the script edits the file you wrote in-place, after this point the prompt file on disk contains the escaped form (not the original) until you delete it in cleanup.

**Locating the script:** At the start of your session, locate the script by searching for `**/create-worktree/scripts/launch-workmux`. Note the absolute path and use it with `bash` as the command prefix in all subsequent invocations. Do not use a shell variable, since shell state does not persist between commands.

In the example below, `SCRIPTS_DIR/launch-workmux` is a placeholder for the script's **quoted absolute path** (e.g., `"/absolute/path/to/plugins/create-worktree/scripts/launch-workmux"`). Always invoke via `bash` followed by the quoted path. This ensures the command token is `bash`, which matches stable allowlist patterns regardless of the plugin's installed path or version.

First, use the Write tool to create a temporary prompt file at `/tmp/workmux-prompt-BRANCH_NAME.md` with the composed prompt from step 2. Using the Write tool avoids shell escaping issues with special characters in the prompt text.

**Important:** Do not delete the prompt file immediately after launching. `workmux` runs asynchronously and may not read the file for several seconds. Wait and verify success before cleaning up.

Do not specify `--base`. Let workmux use its default. Only pass `--base BRANCH` if the user explicitly requests a specific base branch.

Then launch the worktree:

```bash
bash "SCRIPTS_DIR/launch-workmux" "BRANCH_NAME" "/tmp/workmux-prompt-BRANCH_NAME.md"
```

If the user requested a specific base branch:

```bash
bash "SCRIPTS_DIR/launch-workmux" "BRANCH_NAME" "/tmp/workmux-prompt-BRANCH_NAME.md" --base "BASE_BRANCH"
```

The script outputs the workmux log directly and cleans up its own log file. Verify success:

```bash
git worktree list
```

If the log shows success and the worktree appears in the list, clean up the prompt file:

```bash
rm -f /tmp/workmux-prompt-BRANCH_NAME.md
```

### 4. Report Success

After confirming the worktree exists in `git worktree list`, report:

- The branch name created
- The tmux window name (to help the user switch to it)
- A note that the task prompt was injected into the new session

## Error Handling

- If `workmux` is not installed, inform the user and suggest installing it
- If the branch already exists and `--open-if-exists` opens it, note that the prompt is only injected on initial creation
