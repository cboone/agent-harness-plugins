# PR

Commit all changes, push to remote, and create a GitHub pull request in one automated step.

**Type:** Skill
**Trigger:** `/pr`
**Requires:** [`gh`](https://cli.github.com/)

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **PR** from the available plugins.

## What It Does

Stages everything, generates a conventional commit message from the diff, pushes the branch, and opens a PR with an auto-generated title and summary. Detects connected GitHub issues from branch names and commit messages, and adds closing references automatically. Handles branches with no upstream, skips the commit step when the working tree is clean, and detects when a PR already exists.

## Usage

```text
/pr
```

No options. The skill makes opinionated decisions at every step with no prompts.

## Recommended Permissions

This skill runs git and GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": [
      "Bash(git status*)",
      "Bash(git diff*)",
      "Bash(git log *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git push*)",
      "Bash(git branch *)",
      "Bash(git rev-parse *)",
      "Bash(git remote *)",
      "Bash(git mv *)",
      "Bash(gh repo view *)",
      "Bash(gh issue view *)",
      "Bash(gh issue list *)",
      "Bash(gh pr create *)",
      "Bash(gh pr view *)",
      "Bash(mktemp /tmp/pr-body-*)",
      "Bash(rm -f /tmp/pr-body-*)"
    ]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "pr": commits, pushes, and creates a pull request
- "create a pr": same behavior
- "push and create pr": same behavior

## See Also

- [Commit](../commit/README.md): commit without creating a PR
- [Review Branch](../review-branch/README.md): summarize branch work before opening a PR
- [All plugins](../../README.md)
