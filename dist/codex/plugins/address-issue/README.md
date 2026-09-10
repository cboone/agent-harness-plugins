# Address Issue

Fetch a GitHub issue, plan the work, stop for approval, then execute changes and commit with issue references.

**Type:** Skill
**Trigger:** `/address-issue <issue>`
**Requires:** [`gh`](https://cli.github.com/)

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Fetches a GitHub issue by number or search text, classifies it (bug fix, feature, documentation, refactor, or chore), extracts sub-tasks from task list checkboxes, plans the work and stops for your approval, then executes changes and commits with conventional commit messages that reference the issue number. Marks the issue "in progress" at the start and leaves that label in place until the related PR is merged or the user explicitly abandons the effort.

## Usage

```text
/address-issue #42
/address-issue the dark mode issue
/address-issue #42 --dry-run
/address-issue #42 --no-approval
/address-issue #42 --no-commit
/address-issue #42 --commit-per-change
```

| Option                | Description                                          |
| --------------------- | ---------------------------------------------------- |
| `--dry-run`           | Fetch, analyze, and plan without making changes      |
| `--no-approval`       | Skip the approval stop and go straight to execution  |
| `--no-commit`         | Make changes but do not commit them                  |
| `--commit-per-change` | Commit after each logical change instead of grouping |

## Recommended Permissions

This skill runs GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh issue view *)", "Bash(gh issue list *)", "Bash(gh issue edit *)", "Bash(gh label create *)"]
  }
}
```

## Examples

- "address issue #42": fetches the issue, presents a plan, waits for your approval, then makes changes and commits
- "fix issue #15": same workflow, triggered by a different phrase
- "address #88 --dry-run": shows the plan without making changes
- "address the login bug": searches for the issue by description

## See Also

- [Create Issue](../create-issue/README.md): create new GitHub issues
- [Address Issue in Worktree](../address-issue-in-worktree/README.md): run this skill in a new worktree instead of the current branch
- [Suggest Next Issue](../suggest-next-issue/README.md): find which issue to work on next
- [All plugins](../../../../README.md)
