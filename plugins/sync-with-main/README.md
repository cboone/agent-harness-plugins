# Sync With Main

Merge or rebase the base branch into the current branch, resolve conflicts, and push using the selected workflow.

**Type:** Skills

See the [installation instructions](../../README.md#install).

## sync-with-main:merge

Fetch and merge the base branch into the current feature branch with automatic conflict resolution.

**Type:** Skill
**Trigger:** `/sync-with-main:merge`
**Requires:** [`gh`](https://cli.github.com/) (falls back to `git remote show origin` if unavailable)

### Installation

See the [marketplace install instructions](../../README.md#install).

### What It Does

Automatically detects the default branch, handles uncommitted changes (stash, commit, or abort), resolves merge conflicts, and pushes after a successful merge. Suggests running install commands when lockfiles change.

### Usage

```text
/sync-with-main:merge
/sync-with-main:merge --base develop
```

| Option            | Description                            |
| ----------------- | -------------------------------------- |
| `--base <branch>` | Override the auto-detected base branch |

### Recommended Permissions

This skill runs git and GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(git status*)", "Bash(git branch *)", "Bash(git fetch *)", "Bash(git merge *)", "Bash(git commit *)", "Bash(git push*)", "Bash(git stash*)", "Bash(git log *)", "Bash(git diff*)", "Bash(git add *)", "Bash(git remote *)", "Bash(gh repo view *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

### Examples

- "merge main": fetches and merges the default branch
- "merge main --base develop": merges the `develop` branch instead
- "sync with main": same as "merge main"

### See Also

- [Review Branch](../review-branch/README.md): summarize what changed on the current branch
- [All plugins](../../README.md)

## sync-with-main:rebase

Fetch and rebase the current feature branch onto the base branch with automatic conflict resolution and force-with-lease push.

**Type:** Skill
**Trigger:** `/sync-with-main:rebase`
**Requires:** [`gh`](https://cli.github.com/) (falls back to `git remote show origin` if unavailable)

### Installation

See the [marketplace install instructions](../../README.md#install).

### What It Does

Automatically detects the default branch, handles uncommitted changes (stash, commit, or abort), resolves conflicts per replayed commit, and pushes after a successful rebase (using `--force-with-lease` only when the rebase rewrote history). Suggests running install commands when lockfiles change.

Unlike a merge, a rebase rewrites history: each commit on the feature branch is replayed on top of the base branch. Conflicts are resolved per commit, and any branch that has already been pushed requires a `--force-with-lease` push afterward. The skill never uses plain `--force`.

### Usage

```text
/sync-with-main:rebase
/sync-with-main:rebase --base develop
```

| Option            | Description                            |
| ----------------- | -------------------------------------- |
| `--base <branch>` | Override the auto-detected base branch |

### Recommended Permissions

This skill runs git and GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(git status*)", "Bash(git branch *)", "Bash(git fetch *)", "Bash(git rebase *)", "Bash(git commit *)", "Bash(git push*)", "Bash(git stash*)", "Bash(git log *)", "Bash(git diff*)", "Bash(git add *)", "Bash(git remote *)", "Bash(git rev-parse *)", "Bash(git merge-base *)", "Bash(gh repo view *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

### Examples

- "rebase onto main": fetches the default branch and rebases the current branch on top
- "rebase onto main --base develop": rebases onto `develop` instead
- "update branch via rebase": same as "rebase onto main"

### Force-Push Safety

After a rebase, the local branch's history may diverge from any previously pushed copy. The skill picks the push command based on whether the rebase actually rewrote history:

- **History rewritten** (commits replayed onto a new base): `git push --force-with-lease`, which refuses to overwrite the remote if someone else has pushed in the meantime.
- **No-op or fast-forward only** (HEAD unchanged after rebase): a plain `git push`, since nothing was rewritten.
- **No upstream yet** (fresh branch never pushed): `git push -u origin HEAD`, no force needed.

The skill never uses plain `--force`, and never force-pushes the default branch.

### See Also

- [Merge Main](../sync-with-main/README.md): merge the base branch into the current branch instead of rebasing
- [Review Branch](../review-branch/README.md): summarize what changed on the current branch
- [All plugins](../../README.md)
