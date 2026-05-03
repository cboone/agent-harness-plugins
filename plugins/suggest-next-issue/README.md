# Suggest Next Issue

Review all open GitHub issues and recommend what to work on next with prioritized reasoning.

**Type:** Skill
**Trigger:** `/suggest-next-issue`
**Requires:** [`gh`](https://cli.github.com/)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Analyzes open issues in context (current branches, recent work, project goals, and dependencies), then categorizes them as quick wins, high impact, unblocks others, or overdue. Provides specific reasoning for each recommendation so you can make an informed decision.

## Usage

```text
/suggest-next-issue
```

## Recommended Permissions

This skill runs GitHub CLI and git commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh issue list *)", "Bash(gh api *)", "Bash(gh repo view *)", "Bash(gh pr list *)", "Bash(git worktree list*)", "Bash(git branch *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "suggest next issue": analyzes all open issues and recommends priorities
- "what should I work on next": same behavior
- "triage issues": same behavior

## See Also

- [Create Worktree from Issue](../create-worktree-from-issue/README.md): start working on the suggested issue
- [All plugins](../../README.md)
