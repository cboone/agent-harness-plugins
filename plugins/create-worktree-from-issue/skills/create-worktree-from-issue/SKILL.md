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

### 2. Build the Branch Name

Construct a branch name in the format `TYPE/SLUG` where:

- **TYPE**: Derive from issue labels. Use `fix` for labels containing "bug" or "fix". Use `feature` for everything else (including when no labels match).
- **SLUG**: Slugify the issue title: lowercase, replace spaces and special characters with hyphens, collapse consecutive hyphens, trim leading/trailing hyphens, truncate to 50 characters at a word boundary.

Examples:

- Issue "Add dark mode support" with label "enhancement" -> `feature/add-dark-mode-support`
- Issue "Login fails with special chars" with label "bug" -> `fix/login-fails-with-special-chars`
- Issue "Update README" with no labels -> `feature/update-readme`

### 3. Compose the Issue Prompt

Build a prompt from the issue data retrieved in step 1. Format:

```
Work on issue #NUMBER: TITLE

Labels: LABEL1, LABEL2

BODY_CONTENT
```

- If the issue body exceeds approximately 2000 characters, truncate it at the nearest paragraph or sentence boundary and append: "(Issue body truncated. Run `gh issue view NUMBER` for full details.)"
- If the issue body is empty, omit it.
- If there are no labels, omit the labels line.

### 4. Create the Worktree

Write the prompt to a temporary file and pass it via `-P` to avoid shell escaping issues with arbitrary issue body content.

**Important:** The `workmux add` command must run outside the sandbox (use `dangerouslyDisableSandbox: true` on the Bash tool call). It interacts with tmux to create windows and sessions, which hangs indefinitely inside the sandbox.

```bash
PROMPT_FILE=$(mktemp)
cat > "$PROMPT_FILE" << 'PROMPT'
[composed prompt from step 3]
PROMPT
workmux add BRANCH_NAME --open-if-exists -P "$PROMPT_FILE"
rm "$PROMPT_FILE"
```

Do not specify a `--base` branch. Let `workmux` use its default.

### 5. Report Success

After `workmux add` completes, report:

- The issue number and title
- The branch name created
- The tmux window name (to help the user switch to it)
- A note that the issue context was injected into the new session

## Error Handling

- If `gh` is not authenticated, instruct the user to run `gh auth login`
- If `workmux` is not installed, inform the user
- If the issue is closed, warn the user and ask if they want to proceed anyway
