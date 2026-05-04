# Create Worktree

Create a new git worktree, branch, and tmux window with a task prompt injected into the new agent session.

**Type:** Skill
**Trigger:** `/create-worktree`
**Requires:** [`workmux`](https://github.com/paiml/workmux)

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Derives a branch name from your task description (e.g., `feature/add-dark-mode-support` or `fix/auth-timeout`), or accepts an explicit branch name. Creates the worktree via `workmux add` and injects a task prompt so the new agent session knows what to work on.

## Usage

```text
/create-worktree add dark mode support
/create-worktree fix/my-branch-name
```

Provide either a task description (branch name is derived automatically) or an explicit branch name.

## Recommended Permissions

This skill runs workmux and git commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(bash */launch-workmux *)", "Bash(git worktree list*)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "create worktree for adding dark mode": creates `feature/adding-dark-mode`
- "spin up a worktree to fix the auth timeout": creates `fix/auth-timeout`
- "new worktree feature/refactor-config": uses the branch name as-is

## See Also

- [Create Worktree from Issue](../create-worktree-from-issue/README.md): create a worktree tied to a GitHub issue
- [All plugins](../../../../README.md)
