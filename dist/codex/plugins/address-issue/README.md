# Address Issue

Fetch a GitHub issue, analyze it, plan and execute the work in the current branch, and commit with issue references.

**Type:** Skill
**Trigger:** `/address-issue`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Address Issue** from the available plugins.

## What It Does

Fetches a GitHub issue by number or search text, classifies it (bug fix, feature, documentation, refactor, or chore), extracts sub-tasks from task list checkboxes, plans the work, executes changes, and commits with conventional commit messages that reference the issue number. Marks the issue "in progress" at the start and removes the label when done.

## Usage

```text
/address-issue #42
/address-issue the dark mode issue
/address-issue #42 --dry-run
/address-issue #42 --no-commit
/address-issue #42 --commit-per-change
```

| Option                | Description                                          |
| --------------------- | ---------------------------------------------------- |
| `--dry-run`           | Fetch, analyze, and plan without making changes      |
| `--no-commit`         | Make changes but do not commit them                  |
| `--commit-per-change` | Commit after each logical change instead of grouping |

## Recommended Permissions

Allow these `gh` commands so the skill can run without repeated permission prompts:

- `gh issue view *`
- `gh issue list *`
- `gh issue edit *`
- `gh label create *`

## Examples

- "address issue #42": fetches the issue, plans the work, makes changes, and commits
- "fix issue #15": same workflow, triggered by a different phrase
- "address #88 --dry-run": shows the plan without making changes
- "address the login bug": searches for the issue by description

## See Also

- [Create Issue](../create-issue/README.md): create new GitHub issues
- [Create Worktree from Issue](../create-worktree-from-issue/README.md): start an issue in a new worktree instead of the current branch
- [Suggest Next Issue](../suggest-next-issue/README.md): find which issue to work on next
- [All plugins](../../../../README.md)
