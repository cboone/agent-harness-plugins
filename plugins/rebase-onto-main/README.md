# Rebase Onto Main

Fetch and rebase the current feature branch onto the repository's base branch.

**Type:** Skill
**Trigger:** `/rebase-onto-main`
**Requires:** [`gh`](https://cli.github.com/) (falls back to `git remote show origin` if unavailable)

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Rebase Onto Main** from the available plugins.

## What It Does

Automatically detects the default branch, handles uncommitted changes (stash, commit, or abort), resolves conflicts per replayed commit, and force-with-lease pushes after a successful rebase. Suggests running install commands when lockfiles change.

Unlike a merge, a rebase rewrites history: each commit on the feature branch is replayed on top of the base branch. Conflicts are resolved per commit, and any branch that has already been pushed requires a `--force-with-lease` push afterward. The skill never uses plain `--force`.

## Usage

```text
/rebase-onto-main
/rebase-onto-main --base develop
```

| Option            | Description                            |
| ----------------- | -------------------------------------- |
| `--base <branch>` | Override the auto-detected base branch |

## Recommended Permissions

This skill runs git and GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(git status*)", "Bash(git branch *)", "Bash(git fetch *)", "Bash(git rebase *)", "Bash(git commit *)", "Bash(git push*)", "Bash(git stash*)", "Bash(git log *)", "Bash(git diff*)", "Bash(git add *)", "Bash(git remote *)", "Bash(git rev-parse *)", "Bash(gh repo view *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "rebase onto main": fetches the default branch and rebases the current branch on top
- "rebase onto main --base develop": rebases onto `develop` instead
- "update branch via rebase": same as "rebase onto main"

## Force-Push Safety

After a rebase, the local branch's history diverges from any previously pushed copy. Pushing requires either:

- `git push --force-with-lease` (preferred, refuses to overwrite if the remote moved), or
- `git push -u origin HEAD` (only valid if the branch has no upstream yet).

The skill always uses `--force-with-lease` and never plain `--force`. The default branch is never force-pushed.

## See Also

- [Merge Main](../merge-main/README.md): merge the base branch into the current branch instead of rebasing
- [Review Branch](../review-branch/README.md): summarize what changed on the current branch
- [All plugins](../../README.md)
