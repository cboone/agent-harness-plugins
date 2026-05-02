# Commit

Smart, context-aware git commits with conventional commit messages and plan awareness.

**Type:** Skill
**Trigger:** `/commit`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Commit** from the available plugins.

## What It Does

Analyzes your diff to generate well-structured conventional commit messages that match your repository's existing style. Handles staged-only vs. all changes, supports commit-and-push workflows, and can detect plan files for separate commits.

## Usage

```text
/commit
/commit --push
/commit --staged
/commit --plan
/commit --all
```

| Option     | Description                                            |
| ---------- | ------------------------------------------------------ |
| `--push`   | Push to remote after committing                        |
| `--staged` | Commit only staged changes, ignoring unstaged changes  |
| `--plan`   | Commit only the plan file(s)                           |
| `--all`    | Stage and commit all changes including untracked files |

## Recommended Permissions

This skill runs git commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(git status*)", "Bash(git diff*)", "Bash(git log *)", "Bash(git add *)", "Bash(git commit *)", "Bash(git push*)", "Bash(git branch *)", "Bash(git mv *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "commit": stages and commits with an auto-generated message
- "commit and push": commits then pushes to remote
- "commit the plan, then the changes": creates two sequential commits
- "give the plan a meaningful name and commit": renames and commits the plan file

## See Also

- [PR](../pr/README.md): commit, push, and open a pull request in one step
- [All plugins](../../../../README.md)
