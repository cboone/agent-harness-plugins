# Create Worktree

Create a git worktree, branch, and tmux window from an issue number or a task description, with a prompt injected using workmux.

**Type:** Skill
**Trigger:** `/create-worktree <issue-or-description>`

## Requirements

- [`workmux`](https://github.com/paiml/workmux), always.
- [`gh`](https://cli.github.com/), authenticated, only when you pass an issue number.
- [`jq`](https://jqlang.org/), when you pass an issue number or use any of the resource options. The bundled `compose-issue-prompt` script parses the issue JSON with it, and `manage-resource-claims` reads and writes the claim file with it. Both exit if it is missing. A task description or an explicit branch name with no resource needs neither `gh` nor `jq`.

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Takes an issue number, a task description, or an explicit branch name.

Given an **issue number**, it fetches the issue, derives a branch name of the form `feature/42-add-dark-mode-support` from the title and labels, and injects the issue title, labels, and body as the prompt. Leading with the issue number is what lets the [PR](../pr/README.md) skill link the resulting pull request back to the issue.

Given a **task description**, it derives a branch name such as `feature/add-dark-mode-support` or `fix/auth-timeout` and injects the description as the prompt. An explicit branch name is used as-is.

Either way, it creates the worktree via `workmux add` and stops. It does not start the work. To have the new session also plan the issue, use [Address Issue in Worktree](../address-issue-in-worktree/README.md).

### Exclusive resources

Some work cannot run in parallel across worktrees because it needs a resource only one worktree can hold: a DAW, a simulator, a device, a database, a port, a shared install location. `--resource <name>` records which worktree holds one, so the constraint is written down instead of remembered.

Claims live in the main worktree's `.claude/worktree-resources.local.json`, which every linked worktree resolves to the same path. Each claim records the resource, worktree, branch, issue, and a timestamp. The file is machine-local state and belongs in `.gitignore`; the skill offers to add the entry when it first creates the file.

Claiming a resource another worktree already holds reports the holder and asks rather than proceeding. It never refuses: the claim is advisory, and a user who wants to override always has a reason.

A claim whose worktree git no longer lists is stale. Stale claims are flagged by `--list-resources`, read as free when a new claim is checked, and replaced when one is recorded, so a worktree that has been removed never holds a resource forever.

Where a project declares its resources under an "exclusive resources" heading in `AGENTS.md`, `CLAUDE.md`, or a plan, the skill reads that list and matches a loose phrase against it, so "the DAW" resolves to `logic` without retyping. The name is a free string with no registry, so an undeclared one still works.

## Usage

```text
/create-worktree 42
/create-worktree add dark mode support
/create-worktree fix/my-branch-name
/create-worktree 42 --base develop
/create-worktree 42 --resource logic
/create-worktree --list-resources
/create-worktree --release-resource logic
```

| Option                      | Description                                                                          |
| --------------------------- | ------------------------------------------------------------------------------------ |
| `--issue <number>`          | Force issue lookup, for when a task description is itself a number                   |
| `--no-issue`                | Force description handling, even if the argument looks like an issue number          |
| `--base <branch>`           | Base the worktree on a specific branch instead of the repository's default           |
| `--resource <name>`         | Claim a named exclusive resource, reporting the holder first if one holds it already |
| `--release-resource <name>` | Release a claim and stop, creating nothing                                           |
| `--list-resources`          | Report every claim and stop, creating nothing                                        |

## Recommended Permissions

This skill runs workmux, git, and (for the issue path) GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh issue view *)", "Bash(gh repo view *)", "Bash(bash \"*/compose-issue-prompt\")", "Bash(bash \"*/compose-issue-prompt\" *)", "Bash(bash \"*/launch-workmux\" *)", "Bash(bash \"*/manage-resource-claims\" *)", "Bash(git remote show origin*)", "Bash(git worktree list*)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "create worktree for issue 42": creates `feature/42-<slug>` with the issue context injected
- "create worktree for adding dark mode": creates `feature/adding-dark-mode`
- "spin up a worktree to fix the auth timeout": creates `fix/auth-timeout`
- "new worktree feature/refactor-config": uses the branch name as-is
- "create worktree for issue 42, it needs the DAW": claims `logic` for the new worktree, or reports which branch already holds it and asks
- "what's holding the simulator": lists every claim, flagging any whose worktree is gone
- "release the DAW": clears the `logic` claim without creating anything

## See Also

- [Address Issue in Worktree](../address-issue-in-worktree/README.md): the same worktree setup, plus the new session plans the issue and stops for approval
- [Address Issue](../address-issue/README.md): plan and address an issue in the current branch
- [All plugins](../../../../README.md)
