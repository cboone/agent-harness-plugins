# Suggest Next Issue

Review open GitHub issues and recommend what to work on next with prioritized reasoning.

**Type:** Skill
**Trigger:** `/suggest-next-issue`
**Requires:** [`gh`](https://cli.github.com/)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Analyzes open issues in context (current branches, issue labels, assignments, recent work, project goals, and dependencies), excludes issues already marked in progress, then categorizes the remaining candidates as safe to parallelize, narrow scope, high impact, unblocks others, or overdue. Provides specific reasoning for each recommendation so you can make an informed decision.

It also reads the exclusive-resource claims recorded by [Create Worktree](../create-worktree/README.md) and [Address Issue in Worktree](../address-issue-in-worktree/README.md), so an issue whose verification needs a resource another worktree is holding is flagged rather than recommended blind. The summary ends with who holds what, which is the half of the picture the issue list cannot show.

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
    "allow": ["Bash(gh issue list *)", "Bash(gh api *)", "Bash(gh repo view *)", "Bash(gh pr list *)", "Bash(git worktree list*)", "Bash(git branch *)", "Bash(git -C * rev-parse *)"]
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

- [Address Issue in Worktree](../address-issue-in-worktree/README.md): start working on the suggested issue
- [Create Worktree](../create-worktree/README.md): claim, list, and release the exclusive resources this skill reports on
- [All plugins](../../README.md)
