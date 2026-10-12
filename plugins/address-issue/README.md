# Address Issue

Fetch a GitHub issue, plan the work, stop for approval, then execute changes and commit with issue references.

**Type:** Skill
**Trigger:** `/address-issue <issue>`
**Requires:** [`gh`](https://cli.github.com/)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Fetches a GitHub issue by number or search text, classifies it (bug fix, feature, documentation, refactor, or chore), extracts sub-tasks from task list checkboxes, plans the work and stops for your approval, then executes changes and commits with conventional commit messages that reference the issue number. Marks the issue "in progress" at the start and leaves that label in place until the related PR is merged or the user explicitly abandons the effort.

## Usage

Plans propose separate PRs for independent areas and isolate sanitizers, parsers, validators and security boundaries with their required tests, consumers and documentation. Input-check designs prefer exact-format allowlists or structural parsing over blocklists or regexes patched one input form at a time, using the [Review Anti-patterns](../review-anti-patterns/README.md) checklist as a reference.

```text
/address-issue #42
/address-issue the dark mode issue
/address-issue #42 --dry-run
/address-issue #42 --no-approval
/address-issue #42 --no-commit
/address-issue #42 --commit-per-change
/address-issue 42 57
```

Several issue numbers share one plan with one approval stop. Every issue is fetched and checked, you choose whether to keep each closed one, and every open issue that remains is marked in progress. The plan may propose separate PRs and identifies the changes for the current branch; other PRs remain planned follow-ups. Commits reference every issue they address. The options apply to that one plan.

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

- [Create Issue](../use-git/README.md#create-issue): create new GitHub issues
- [Address Issue in Worktree](../workmux/README.md#workmuxstart-issue): run this skill in a new worktree instead of the current branch
- [Suggest Next Issue](../suggest-next-issue/README.md): find which issue to work on next
- [All plugins](../../README.md)
