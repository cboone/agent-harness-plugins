# Merge Main

Fetch and merge the repository's base branch into the current feature branch.

**Type:** Skill
**Trigger:** `/merge-main`
**Requires:** [`gh`](https://cli.github.com/) (falls back to `git remote show origin` if unavailable)

## What It Does

Automatically detects the default branch, handles uncommitted changes (stash, commit, or abort), resolves merge conflicts, and pushes after a successful merge. Suggests running install commands when lockfiles change.

## Usage

```text
/merge-main
/merge-main --base develop
```

| Option | Description |
| ------------------- | ----------------------------------------------- |
| `--base <branch>` | Override the auto-detected base branch |

## Examples

- "merge main" — fetches and merges the default branch
- "merge main --base develop" — merges the `develop` branch instead
- "sync with main" — same as "merge main"

## See Also

- [Review Branch](../review-branch/README.md) — summarize what changed on the current branch
- [All plugins](../../README.md)
