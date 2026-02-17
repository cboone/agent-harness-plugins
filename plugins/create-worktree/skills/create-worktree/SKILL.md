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

```
Work on: [user's task description]

Branch: [BRANCH_NAME]
```

Keep the prompt concise -- a few sentences at most. Use the user's own description of the task as the core content.

If the user provided only a branch name with no description, derive a human-readable description from the branch name (e.g., `feature/add-dark-mode` becomes "Work on: add dark mode").

### 3. Create the Worktree

**Important:** The `workmux add` command must be fully detached from the Claude Code process. `workmux` creates tmux windows and spawns new Claude sessions, which cannot initialize while the parent Claude Code process is alive. Background the command with `& disown` so it survives shell exit.

For simple prompts:

```bash
workmux add BRANCH_NAME --open-if-exists -p "PROMPT_TEXT" > /tmp/workmux-BRANCH_NAME.log 2>&1 & disown; sleep 8
```

Do not specify `--base`. Let workmux use its default. Only pass `--base BRANCH` if the user explicitly requests a specific base branch.

**Shell escaping:** If the prompt text contains characters that are difficult to escape inline (backticks, dollar signs, nested quotes), use the Write tool to create a temporary prompt file and pass it with `-P`. Using the Write tool avoids shell escaping issues entirely.

**Important:** Do not delete the prompt file immediately after launching. `workmux` runs asynchronously and may not read the file for several seconds. Wait and verify success before cleaning up.

After creating `/tmp/workmux-prompt-BRANCH_NAME.md` with the Write tool:

```bash
workmux add BRANCH_NAME --open-if-exists -P /tmp/workmux-prompt-BRANCH_NAME.md > /tmp/workmux-BRANCH_NAME.log 2>&1 & disown; sleep 8
```

After launching, use the Read tool to check `/tmp/workmux-BRANCH_NAME.log`, then verify:

```bash
git worktree list
```

If the log shows success and the worktree appears in the list, clean up:

```bash
rm -f /tmp/workmux-prompt-BRANCH_NAME.md /tmp/workmux-BRANCH_NAME.log
```

### 4. Report Success

After confirming the worktree exists in `git worktree list`, report:

- The branch name created
- The tmux window name (to help the user switch to it)
- A note that the task prompt was injected into the new session

## Error Handling

- If `workmux` is not installed, inform the user and suggest installing it
- If the branch already exists and `--open-if-exists` opens it, note that the prompt is only injected on initial creation
