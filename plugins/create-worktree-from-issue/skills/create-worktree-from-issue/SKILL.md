---
name: create-worktree-from-issue
description: >-
  Find a GitHub issue in the current repository and create a new git worktree,
  branch, and tmux window for working on it using workmux. Use when the user
  says "start issue", "work on issue", "create worktree from issue",
  "create worktree for issue", or references starting work on a GitHub issue
  by number (e.g., "#42") or by description (e.g., "the dark mode issue").
  Requires the gh CLI and workmux to be installed.
---

# Create Worktree from Issue

Find a GitHub issue and create a dedicated worktree + tmux window via `workmux add`.

## Workflow

### 1. Find the Issue

The user provides either an issue number or descriptive text.

**By number:**

```bash
gh issue view NUMBER --json number,title,labels,body,state
```

**By text (fuzzy search):**

```bash
gh issue list --search "USER_TEXT" --state all --json number,title,labels,state --limit 10
```

If the search returns exactly one result, proceed automatically with that issue without asking for additional confirmation.

If the search returns multiple results, present them to the user and ask which one to use.

If no results, try broadening the search or ask the user to refine their query.

### 2. Mark Issue In Progress

If the issue is open, signal that work is starting. Skip this step for closed issues.

**Self-assign:**

```bash
gh issue edit NUMBER --add-assignee @me
```

**Ensure the label exists, then add it:**

```bash
gh label create "in progress" --description "Work is actively being done" --color FBCA04 2>/dev/null
gh issue edit NUMBER --add-label "in progress"
```

The `gh label create` command is safe to run even if the label already exists — `2>/dev/null` suppresses the "already exists" error. This ensures the label is available before `gh issue edit --add-label` attempts to use it, since `gh` does **not** auto-create labels.

Self-assignment is idempotent — safe to re-run if the assignee already exists.

If any command fails, warn the user but continue with worktree creation. Status marking is best-effort and must never block the primary workflow.

### 3. Build the Branch Name

Construct a branch name in the format `TYPE/SLUG` where:

- **TYPE**: Derive from issue labels. Use `fix` for labels containing "bug" or "fix". Use `feature` for everything else (including when no labels match).
- **SLUG**: Slugify the issue title: lowercase, replace spaces and special characters with hyphens, collapse consecutive hyphens, trim leading/trailing hyphens, truncate to 50 characters at a word boundary.

Examples:

- Issue "Add dark mode support" with label "enhancement" -> `feature/add-dark-mode-support`
- Issue "Login fails with special chars" with label "bug" -> `fix/login-fails-with-special-chars`
- Issue "Update README" with no labels -> `feature/update-readme`

### 4. Compose the Issue Prompt

Build a prompt from the issue data retrieved in step 1. Format:

```
Work on issue #NUMBER: TITLE

Labels: LABEL1, LABEL2

BODY_CONTENT
```

- If the issue body exceeds approximately 2000 characters, truncate it at the nearest paragraph or sentence boundary and append: "(Issue body truncated. Run `gh issue view NUMBER` for full details.)"
- If the issue body is empty, omit it.
- If there are no labels, omit the labels line.

### 5. Create the Worktree

Use the Write tool to create a temporary prompt file at `/tmp/workmux-prompt-BRANCH_NAME.md` with the composed prompt from step 4. Using the Write tool avoids shell escaping issues with arbitrary issue body content.

**Important:** The `workmux add` command must be fully detached from the Claude Code process. `workmux` creates tmux windows and spawns new Claude sessions, which cannot initialize while the parent Claude Code process is alive. Background the command with `& disown` so it survives shell exit.

**Important:** Do not delete the prompt file immediately after launching. `workmux` runs asynchronously and may not read the file for several seconds. Wait and verify success before cleaning up.

```bash
workmux add BRANCH_NAME --open-if-exists -P /tmp/workmux-prompt-BRANCH_NAME.md > /tmp/workmux-BRANCH_NAME.log 2>&1 & disown; sleep 8
```

Do not specify a `--base` branch. Let `workmux` use its default.

After launching, use the Read tool to check `/tmp/workmux-BRANCH_NAME.log`, then verify:

```bash
git worktree list
```

If the log shows success and the worktree appears in the list, clean up:

```bash
rm -f /tmp/workmux-prompt-BRANCH_NAME.md /tmp/workmux-BRANCH_NAME.log
```

If the log shows an error (e.g., "Failed to read prompt file"), the prompt file may have been deleted too early or another issue occurred. Use the Read tool to check the log for details.

### 6. Report Success

After confirming the worktree exists in `git worktree list`, report:

- The issue number and title
- The branch name created
- The tmux window name (to help the user switch to it)
- A note that the issue context was injected into the new session
- Whether the issue was marked in progress (assigned and labeled), or if status marking was skipped/failed

## Error Handling

- If `gh` is not authenticated, instruct the user to run `gh auth login`
- If `workmux` is not installed, inform the user
- If the issue is closed, warn the user and ask if they want to proceed anyway
- If status marking fails (assignment or labeling), warn the user but continue with worktree creation — status marking is best-effort
