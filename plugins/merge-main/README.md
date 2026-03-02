# Merge Main

Fetch and merge the repository's base branch into the current feature branch.

**Type:** Skill
**Trigger:** `/merge-main`
**Requires:** [`gh`](https://cli.github.com/) (falls back to `git remote show origin` if unavailable)

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Merge Main** from the available plugins.

## What It Does

Automatically detects the default branch, handles uncommitted changes (stash, commit, or abort), resolves merge conflicts, and pushes after a successful merge. Suggests running install commands when lockfiles change.

## Usage

```text
/merge-main
/merge-main --base develop
```

| Option            | Description                            |
| ----------------- | -------------------------------------- |
| `--base <branch>` | Override the auto-detected base branch |

## Recommended Permissions

This skill runs git and GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(git status*)", "Bash(git branch *)", "Bash(git fetch *)", "Bash(git merge *)", "Bash(git commit *)", "Bash(git push*)", "Bash(git stash*)", "Bash(git log *)", "Bash(git diff*)", "Bash(git add *)", "Bash(git remote *)", "Bash(gh repo view *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "merge main": fetches and merges the default branch
- "merge main --base develop": merges the `develop` branch instead
- "sync with main": same as "merge main"

## See Also

- [Review Branch](../review-branch/README.md): summarize what changed on the current branch
- [All plugins](../../README.md)
