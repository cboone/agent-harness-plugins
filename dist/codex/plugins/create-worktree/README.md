# Create Worktree

Create a git worktree, branch, and tmux window from an issue number or a task description, with a prompt injected using workmux.

**Type:** Skill
**Trigger:** `/create-worktree <issue-or-description>`

## Requirements

- [`workmux`](https://github.com/paiml/workmux), always.
- [`gh`](https://cli.github.com/), authenticated, only when you pass an issue number. Task descriptions and explicit branch names need no GitHub access.

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Takes an issue number, a task description, or an explicit branch name.

Given an **issue number**, it fetches the issue, derives a branch name of the form `feature/42-add-dark-mode-support` from the title and labels, and injects the issue title, labels, and body as the prompt. Leading with the issue number is what lets the [PR](../pr/README.md) skill link the resulting pull request back to the issue.

Given a **task description**, it derives a branch name such as `feature/add-dark-mode-support` or `fix/auth-timeout` and injects the description as the prompt. An explicit branch name is used as-is.

Either way, it creates the worktree via `workmux add` and stops. It does not start the work. To have the new session also plan the issue, use [Address Issue in Worktree](../address-issue-in-worktree/README.md).

## Usage

```text
/create-worktree 42
/create-worktree add dark mode support
/create-worktree fix/my-branch-name
/create-worktree 42 --base develop
```

| Option             | Description                                                                 |
| ------------------ | --------------------------------------------------------------------------- |
| `--issue <number>` | Force issue lookup, for when a task description is itself a number          |
| `--no-issue`       | Force description handling, even if the argument looks like an issue number |
| `--base <branch>`  | Base the worktree on a specific branch instead of the workmux default       |

## Recommended Permissions

This skill runs workmux, git, and (for the issue path) GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh issue view *)", "Bash(bash \"*/compose-issue-prompt\")", "Bash(bash \"*/compose-issue-prompt\" *)", "Bash(bash \"*/launch-workmux\" *)", "Bash(git worktree list*)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "create worktree for issue 42": creates `feature/42-<slug>` with the issue context injected
- "create worktree for adding dark mode": creates `feature/adding-dark-mode`
- "spin up a worktree to fix the auth timeout": creates `fix/auth-timeout`
- "new worktree feature/refactor-config": uses the branch name as-is

## See Also

- [Address Issue in Worktree](../address-issue-in-worktree/README.md): the same worktree setup, plus the new session plans the issue and stops for approval
- [Address Issue](../address-issue/README.md): plan and address an issue in the current branch
- [All plugins](../../../../README.md)
