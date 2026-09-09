# Create Issue

Create GitHub issues using tmpfiles to avoid permission prompts from large multiline Bash arguments.

**Type:** Skill
**Trigger:** `/create-issue`

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Creates GitHub issues by writing the issue body to a temporary file and passing it to `gh issue create --body-file`, instead of inlining large multiline strings as Bash arguments. This keeps the Bash command short and avoids triggering Claude Code's permission prompts for complex commands. Supports labels, assignees, milestones, projects, and cross-repo issue creation.

## Requirements

- [`gh`](https://cli.github.com/). Install via Homebrew: `brew install gh`

## Usage

Ask Claude to create an issue:

- "Create an issue for adding dark mode support"
- "File a bug report about the login timeout"
- "Open an issue on org/repo for the missing docs"

Or invoke directly with `/create-issue`.

## Recommended Permissions

This skill runs GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh issue create *)", "Bash(gh issue view *)", "Bash(gh issue edit *)", "Bash(mktemp -u /tmp/gh-issue-body-*)", "Bash(rm -f /tmp/gh-issue-body-*)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## See Also

- [Create Worktree from Issue](../create-worktree-from-issue/README.md): Start working on an existing issue in an isolated worktree
- [Suggest Next Issue](../suggest-next-issue/README.md): Get recommendations on which issue to tackle next
- [All plugins](../../../../README.md)
