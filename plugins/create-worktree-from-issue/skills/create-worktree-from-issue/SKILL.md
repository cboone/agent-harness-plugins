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
gh issue list --search "USER_TEXT" --json number,title,labels --limit 10
```

If the search returns multiple results, present them to the user and ask which one to use. If it returns exactly one, confirm with the user before proceeding.

If no results, try broadening the search or ask the user to refine their query.

### 2. Determine the Base Branch

Determine the repo's default branch:

```bash
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
```

Use the repo's default branch (usually `main`) as the base. This is the safest default since the user is typically starting fresh work from a stable baseline, even if they happen to be on another branch when they invoke the skill.

### 3. Build the Branch Name

Construct a branch name in the format `TYPE/SLUG` where:

- **TYPE**: Derive from issue labels. Use `fix` for labels containing "bug" or "fix". Use `feature` for everything else (including when no labels match).
- **SLUG**: Slugify the issue title: lowercase, replace spaces and special characters with hyphens, collapse consecutive hyphens, trim leading/trailing hyphens, truncate to 50 characters at a word boundary.

Examples:

- Issue "Add dark mode support" with label "enhancement" -> `feature/add-dark-mode-support`
- Issue "Login fails with special chars" with label "bug" -> `fix/login-fails-with-special-chars`
- Issue "Update README" with no labels -> `feature/update-readme`

### 4. Confirm with the User

Before creating the worktree, confirm the plan:

- Issue: #NUMBER - TITLE
- Branch: `TYPE/SLUG`
- Base: DEFAULT_BRANCH (show explicitly so the user can verify or override)

Ask the user if this looks correct. Allow them to adjust the branch name or base branch.

### 5. Create the Worktree

```bash
workmux add BRANCH_NAME --base BASE_BRANCH
```

This creates:
- A new git branch
- A new worktree directory
- A new tmux window named after the worktree

### 6. Report Success

After `workmux add` completes, report:

- The issue number and title
- The branch name created
- The tmux window name (to help the user switch to it)
- Remind the user they can switch to the new window in tmux

## Error Handling

- If `gh` is not authenticated, instruct the user to run `gh auth login`
- If `workmux` is not installed, inform the user
- If the branch already exists, ask the user if they want to use `workmux add --open-if-exists` to open the existing worktree instead
- If the issue is closed, warn the user and ask if they want to proceed anyway
