# Create Worktree

Create a git worktree, branch, and tmux window from an issue number or a task description, with a prompt injected using workmux.

**Type:** Skill
**Trigger:** `/create-worktree <issue-or-description>`

## Requirements

- [`workmux`](https://github.com/raine/workmux) 0.1.233 or newer, whenever a worktree is created, which is every use except `--list-resources` and `--release-resource`. Those two report on claims and stop, so they need only `jq`. `workmux add --dry-run` arrived in 0.1.220 and slash-separated generated names such as `fix/issue-123` stopped being flattened in 0.1.233; the branch naming here needs both. Verified against 0.1.261. Older versions degrade in two different ways rather than one: below 0.1.220 the dry run fails outright and the skill falls back to deriving the name from the issue title, while 0.1.220 through 0.1.232 generate a name successfully but flatten the prefix, so `fix/auth-timeout` silently becomes `fix-auth-timeout` and no fallback is triggered. Passing an explicit branch name skips naming altogether and works on any version.
- A naming command workmux can reach, unless you always pass an explicit branch name. `workmux add -A` uses `auto_name.command` if set, otherwise the configured agent's CLI, otherwise the [`llm`](https://llm.datasette.io/) CLI. With `agent: claude` that resolves to `claude --model haiku -p` and needs no extra setup. When none is reachable, the skill falls back to deriving a name from the issue title.
- [`gh`](https://cli.github.com/), authenticated, only when you pass an issue number.
- [`jq`](https://jqlang.org/), when you pass an issue number or use any of the resource options. The bundled `compose-issue-prompt` script parses the issue JSON with it, and `manage-resource-claims` reads and writes the claim file with it. Both exit if it is missing. A task description or an explicit branch name with no resource needs neither `gh` nor `jq`.

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

See the [marketplace install instructions](../../README.md#install).

## What It Does

Takes an issue number, a task description, or an explicit branch name.

Given an **issue number**, it fetches the issue and injects the title, labels, and body as the prompt. Given a **task description**, it injects the description. An explicit branch name is used as-is.

The branch name comes from workmux's own generator, which reads the prompt: the launcher runs `workmux add -A --dry-run`, which returns a name without creating anything. Whatever it returns is used as-is, with the issue number inserted after the type prefix so that `feature/make-things-better` for issue 387 becomes `feature/387-make-things-better`. A generator that returns a bare slug gets the number at the front, as `387-make-things-better`. Leading with the issue number is what lets the [PR](../pr/README.md) skill link the resulting pull request back to the issue.

Rerunning for the same issue reuses a local branch that already carries that number, so the same worktree reopens rather than a second one appearing under a differently worded name.

Either way, it creates the worktree via `workmux add` and stops. It does not start the work. To have the new session also plan the issue, use [Address Issue in Worktree](../address-issue-in-worktree/README.md).

### Exclusive resources

Some work cannot run in parallel across worktrees because it needs a resource only one worktree can hold: a DAW, a simulator, a device, a database, a port, a shared install location. `--resource <name>` records which worktree holds one, so the constraint is written down instead of remembered.

Claims live in the main worktree's `.claude/worktree-resources.local.json`, which every linked worktree resolves to the same path. Each claim records an id, the resource, worktree, branch, and a timestamp, plus the issue number when the worktree came from an issue. The id names one claim event, which is what `--take-over` carries: neither a path nor a timestamp identifies a claim, since a path can be reused and a timestamp has second resolution. The file is machine-local state and belongs in `.gitignore`; the skill offers to add the entry when it first creates the file.

Claiming a resource another worktree already holds reports the holder and asks rather than proceeding. Answering yes proceeds: the claim is advisory, and a user who wants to override always has a reason. What it will not do is take a resource over without asking, including in the window between the check and the write, where another worktree may have claimed it in the meantime.

A resource name is chosen per project and there is no registry, but it must contain no whitespace or control characters and must not begin with a hyphen, so that it survives the `key=value` listing and can be passed back as an argument. `logic`, `simulator`, and `port-5432` are all fine.

A claim whose worktree git no longer lists is stale. Stale claims are flagged by `--list-resources`, read as free when a new claim is checked, and replaced when one is recorded.

A worktree is identified by its git admin directory, which is what lets a claim survive `git worktree move` and a branch switch. git names that directory after the worktree's basename and reuses it for the next worktree with the same basename, so a claim whose worktree was removed and whose name has since been reused reports held rather than stale. `--release-resource` clears it; `prune` does not, because the claim does not read as stale. See [issue 424](https://github.com/cboone/agent-harness-plugins/issues/424).

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
| `--branch <name>`           | Use this exact branch name and skip generation                                       |
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

- "create worktree for issue 42": generates a name for the issue, inserts `42`, and injects the issue context
- "create worktree for adding dark mode": generates a name such as `feature/add-dark-mode`
- "spin up a worktree to fix the auth timeout": generates a name such as `fix/auth-timeout`
- "new worktree feature/refactor-config": uses the branch name as-is, with no generation step
- "create worktree for issue 42, it needs the DAW": claims `logic` for the new worktree, or reports which branch already holds it and asks
- "what's holding the simulator": lists every claim, flagging any whose worktree is gone
- "release the DAW": clears the `logic` claim without creating anything

## See Also

- [Address Issue in Worktree](../address-issue-in-worktree/README.md): the same worktree setup, plus the new session plans the issue and stops for approval
- [Address Issue](../address-issue/README.md): plan and address an issue in the current branch
- [All plugins](../../README.md)
