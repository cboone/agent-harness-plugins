# Suggest Next Issue

Review all open GitHub issues and recommend what to work on next with prioritized reasoning.

**Type:** Skill
**Trigger:** `/suggest-next-issue`
**Requires:** [`gh`](https://cli.github.com/)

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Suggest Next Issue** from the available plugins.

## What It Does

Analyzes open issues in context (current branches, recent work, project goals, and dependencies), then categorizes them as quick wins, high impact, unblocks others, or overdue. Provides specific reasoning for each recommendation so you can make an informed decision.

## Usage

```text
/suggest-next-issue
```

## Examples

- "suggest next issue": analyzes all open issues and recommends priorities
- "what should I work on next": same behavior
- "triage issues": same behavior

## See Also

- [Create Worktree from Issue](../create-worktree-from-issue/README.md): start working on the suggested issue
- [All plugins](../../README.md)
