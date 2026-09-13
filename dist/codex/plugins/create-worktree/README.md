# Create Worktree

Create a git worktree, branch, and tmux window from an issue number or a task description, with a prompt injected using workmux.

**Type:** Skill
**Trigger:** `/create-worktree <issue-or-description>`

## Requirements

- [`workmux`](https://github.com/paiml/workmux), always.
- A naming command workmux can reach, unless you always pass an explicit branch name. `workmux add -A` uses `auto_name.command` if set, otherwise the configured agent's CLI, otherwise the [`llm`](https://llm.datasette.io/) CLI. With `agent: claude` that resolves to `claude --model haiku -p` and needs no extra setup. When none is reachable, the skill falls back to deriving a name from the issue title.
- [`gh`](https://cli.github.com/), authenticated, and [`jq`](https://jqlang.org/), both only when you pass an issue number. The bundled `compose-issue-prompt` script parses the issue JSON with `jq` and exits if it is missing. Task descriptions and explicit branch names need neither.

### Choosing the type prefix

The type prefix is whatever the generator returns, so it comes from your workmux naming prompt rather than from this skill. workmux's built-in prompt asks for bare kebab-case, which yields `387-make-things-better`. To get `feature/`, `fix/`, and `chore/` prefixes, ask for them in your global workmux config:

```yaml
auto_name:
  system_prompt: |
    Generate a concise git branch name based on the task description.

    Rules:
    - Use kebab-case (lowercase with hyphens)
    - Focus on the core task, not implementation details
    - Always use a feature-branch style prefix: feature/, fix/, chore/, or docs/
    - Use fix/ for a bug fix, feature/ for new work, chore/ for cleanup, docs/ for documentation

    Output ONLY the branch name, nothing else.
```

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Takes an issue number, a task description, or an explicit branch name.

Given an **issue number**, it fetches the issue and injects the title, labels, and body as the prompt. Given a **task description**, it injects the description. An explicit branch name is used as-is.

The branch name comes from workmux's own generator, which reads the prompt: the launcher runs `workmux add -A --dry-run`, which returns a name without creating anything. Whatever it returns is used as-is, with the issue number inserted after the type prefix so that `feature/make-things-better` for issue 387 becomes `feature/387-make-things-better`. A generator that returns a bare slug gets the number at the front, as `387-make-things-better`. Leading with the issue number is what lets the [PR](../pr/README.md) skill link the resulting pull request back to the issue.

Rerunning for the same issue reuses a local branch that already carries that number, so the same worktree reopens rather than a second one appearing under a differently worded name.

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
| `--base <branch>`  | Base the worktree on a specific branch instead of the repository's default  |

## Recommended Permissions

This skill runs workmux, git, and (for the issue path) GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh issue view *)", "Bash(gh repo view *)", "Bash(bash \"*/compose-issue-prompt\")", "Bash(bash \"*/compose-issue-prompt\" *)", "Bash(bash \"*/launch-workmux\" *)", "Bash(git remote show origin*)", "Bash(git worktree list*)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "create worktree for issue 42": generates a name for the issue, inserts `42`, and injects the issue context
- "create worktree for adding dark mode": generates a name such as `feature/add-dark-mode`
- "spin up a worktree to fix the auth timeout": generates a name such as `fix/auth-timeout`
- "new worktree feature/refactor-config": uses the branch name as-is, with no generation step

## See Also

- [Address Issue in Worktree](../address-issue-in-worktree/README.md): the same worktree setup, plus the new session plans the issue and stops for approval
- [Address Issue](../address-issue/README.md): plan and address an issue in the current branch
- [All plugins](../../../../README.md)
