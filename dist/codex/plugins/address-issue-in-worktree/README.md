# Address Issue in Worktree

Create a worktree, branch, and tmux window for a GitHub issue, then have the new session run address-issue to plan the work and stop for approval.

**Type:** Skill
**Trigger:** `/address-issue-in-worktree <issue>`
**Requires:** [`gh`](https://cli.github.com/), [`workmux`](https://github.com/raine/workmux), [`jq`](https://jqlang.org/)

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Finds a GitHub issue by number or fuzzy text search, self-assigns the issue, labels it "in progress", and creates a worktree via `workmux add` with the full issue context injected as a prompt. The injected prompt ends with an instruction telling the new session to run `/address-issue <number>` first, so the work begins with a plan that stops for your approval.

The invoking agent generates a semantic branch name from the issue title, labels, and body, treating them as task data before composing the destination prompt and chain footer. The launcher receives the candidate, validates it, and inserts the issue number: `feature/add-dark-mode` for issue 42 becomes `feature/42-add-dark-mode`. Rerunning an issue reuses its matching local branch. Workmux receives an explicit branch and starts the configured destination agent.

Naming runs in the current session using bundled rules: lowercase kebab-case, an imperative verb and noun, and a `fix/`, `feature/`, `chore/`, or `docs/` prefix. The descriptive slug targets at most five words and 50 characters. Repository-specific naming conventions take precedence. No separate naming command or workmux naming configuration is needed. Explicit user-supplied names bypass generation. See [Create Worktree](../create-worktree/README.md#choosing-the-type-prefix).

The approval gate itself lives in [Address Issue](../address-issue/README.md). This skill creates the worktree and stops; the plan is produced and approved in the new session.

The "in progress" label is retained until the related PR is merged or the user explicitly abandons the effort.

## Usage

```text
/address-issue-in-worktree 42
/address-issue-in-worktree the dark mode issue
/address-issue-in-worktree 42 --no-approval
/address-issue-in-worktree 42 --resource logic
/address-issue-in-worktree 42 --each --resource logic
/address-issue-in-worktree 42 57
/address-issue-in-worktree 42 57 61 --fan-out
```

Provide an issue number, several issue numbers, or descriptive text to search for.

| Option              | Description                                                                             |
| ------------------- | --------------------------------------------------------------------------------------- |
| `--no-approval`     | Pass `--no-approval` through, so the new session plans and executes without stopping    |
| `--resource <name>` | Claim a named exclusive resource, reporting the holder first if one holds it already    |
| `--fan-out`         | With several issues, open one worktree per issue; `--each` and `--separate` are aliases |

### Several issues

By default, several issue numbers open **one** worktree for the combined work. Closed issues you decline are dropped first. The first remaining issue supplies the branch number, the prompt carries every remaining issue, every open one is marked in progress, and the new session runs `/address-issue 42 57` to plan them together under one approval.

With `--fan-out` (or its aliases `--each` and `--separate`), each issue gets its own worktree, branch, tmux window and session, running `/address-issue N` for that issue. Every issue is fetched and checked, and every question about closed issues or ambiguous branches is asked, before the first worktree is created. Worktrees are then created one at a time, and each issue is marked in progress only after its worktree exists. The run ends with one table covering every issue. With one distinct issue, the flag has no effect and `--resource` works as usual. With several distinct issues, `--resource` is rejected because one exclusive resource cannot be held by several worktrees.

`--resource` records which worktree holds a resource that only one worktree can use at a time: a DAW, a simulator, a device, a database, a port, a shared install location. The check runs before the issue is self-assigned and labeled, so declining a held resource leaves nothing behind on an issue nobody started. See [Create Worktree](../create-worktree/README.md) for how claims are stored, when they go stale, and how to list or release them.

## Recommended Permissions

This skill runs GitHub CLI, workmux, and git commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh issue view *)", "Bash(gh issue list *)", "Bash(gh issue edit *)", "Bash(gh label create *)", "Bash(gh repo view *)", "Bash(bash \"*/compose-issue-prompt\")", "Bash(bash \"*/compose-issue-prompt\" *)", "Bash(bash \"*/launch-workmux\" *)", "Bash(bash \"*/manage-resource-claims\" *)", "Bash(git remote show origin*)", "Bash(git worktree list*)", "Bash(workmux list *)", "Bash(mktemp *)", "Bash(rm -f *issue-json-*)", "Bash(rm -f *issue-prompt-*)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "address issue #42 in a worktree": looks up issue 42, creates a worktree, and the new session plans it
- "start issue #42": same thing
- "work on the dark mode issue in a worktree": searches for a matching issue by title
- "start issue #42, it needs the simulator": claims `simulator` for the new worktree, or reports which branch already holds it and asks first
- "work on #42 and #57 together in a worktree": opens one worktree whose session plans both issues
- "start #42, #57 and #61, each in its own worktree": opens three worktrees with `--fan-out`

## See Also

- [Address Issue](../address-issue/README.md): plan and address an issue in the current branch
- [Create Worktree](../create-worktree/README.md): create a worktree from an issue number or a task description, without chaining into address-issue
- [Suggest Next Issue](../suggest-next-issue/README.md): get a recommendation for which issue to work on
- [All plugins](../../../../README.md)
