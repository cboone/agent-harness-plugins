# Address Issue in Worktree

Create a worktree, branch, and tmux window for a GitHub issue, then have the new session run address-issue to plan the work and stop for approval.

**Type:** Skill
**Trigger:** `/address-issue-in-worktree <issue>`
**Requires:** [`gh`](https://cli.github.com/), [`workmux`](https://github.com/paiml/workmux), [`jq`](https://jqlang.org/)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Finds a GitHub issue by number or fuzzy text search, derives a branch name from the issue title and labels, self-assigns the issue, labels it "in progress", and creates a worktree via `workmux add` with the full issue context injected as a prompt. The injected prompt ends with an instruction telling the new session to run `/address-issue <number>` first, so the work begins with a plan that stops for your approval.

The approval gate itself lives in [Address Issue](../address-issue/README.md). This skill creates the worktree and stops; the plan is produced and approved in the new session.

The "in progress" label is retained until the related PR is merged or the user explicitly abandons the effort.

## Usage

```text
/address-issue-in-worktree 42
/address-issue-in-worktree the dark mode issue
/address-issue-in-worktree 42 --no-approval
```

Provide either an issue number or descriptive text to search for.

| Option          | Description                                                                          |
| --------------- | ------------------------------------------------------------------------------------ |
| `--no-approval` | Pass `--no-approval` through, so the new session plans and executes without stopping |

## Recommended Permissions

This skill runs GitHub CLI, workmux, and git commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh issue view *)", "Bash(gh issue list *)", "Bash(gh issue edit *)", "Bash(gh label create *)", "Bash(bash \"*/compose-issue-prompt\")", "Bash(bash \"*/compose-issue-prompt\" *)", "Bash(bash \"*/launch-workmux\" *)", "Bash(git worktree list*)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "address issue #42 in a worktree": looks up issue 42, creates a worktree, and the new session plans it
- "start issue #42": same thing
- "work on the dark mode issue in a worktree": searches for a matching issue by title

## See Also

- [Address Issue](../address-issue/README.md): plan and address an issue in the current branch
- [Create Worktree](../create-worktree/README.md): create a worktree from an issue number or a task description, without chaining into address-issue
- [Suggest Next Issue](../suggest-next-issue/README.md): get a recommendation for which issue to work on
- [All plugins](../../README.md)
