# Suggest Next Issue

Recommend the next open GitHub issue in a focused terminal answer, with reasoning, progress signals and resource constraints.

**Type:** Skill
**Trigger:** `/suggest-next-issue`
**Requires:** [`gh`](https://cli.github.com/)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Analyzes open issues in context (current branches, pull requests, issue labels, assignments, recent work, project goals, and dependencies), excludes issues already in progress, reports how far along each one is and whose move comes next, weighs assignments and recent work in an area as a weak ownership signal, then categorizes the remaining candidates as safe to parallelize, narrow scope, high impact, unblocks others, or overdue. Provides specific reasoning for each recommendation so you can make an informed decision.

It also reads the exclusive-resource claims recorded by [Create Worktree](../workmux/README.md) and [Address Issue in Worktree](../workmux/README.md), so an issue whose verification needs a resource another worktree is holding is flagged rather than recommended blind. The summary ends with who holds what, which is the half of the picture the issue list cannot show.

## Usage

```text
/suggest-next-issue
/suggest-next-issue --parallel-only
```

| Option            | Description                                                                            |
| ----------------- | -------------------------------------------------------------------------------------- |
| `--parallel-only` | Recommend only issues that need no exclusive resource another worktree currently holds |

## Recommended Permissions

This skill runs GitHub CLI and git commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh issue list *)", "Bash(gh api *)", "Bash(gh repo view *)", "Bash(gh pr list *)", "Bash(git worktree list*)", "Bash(git branch *)", "Bash(git -C * rev-parse *)", "Bash(git config user.email)", "Bash(git log *)", "Bash(git diff --name-only *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "suggest next issue": analyzes all open issues and recommends priorities
- "what should I work on next": same behavior
- "triage issues": same behavior
- "what can I work on in parallel": recommends only issues that need no held resource, and names who holds the rest

## See Also

- [Address Issue in Worktree](../workmux/README.md): start working on the suggested issue
- [Create Worktree](../workmux/README.md): claim, list, and release the exclusive resources this skill reports on
- [All plugins](../../README.md)
