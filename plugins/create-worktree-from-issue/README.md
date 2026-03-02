# Create Worktree from Issue

Find a GitHub issue and create a dedicated worktree, branch, and tmux window for working on it.

**Type:** Skill
**Trigger:** `/create-worktree-from-issue`
**Requires:** [`gh`](https://cli.github.com/), [`workmux`](https://github.com/paiml/workmux)

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Create Worktree from Issue** from the available plugins.

## What It Does

Finds a GitHub issue by number or fuzzy text search, derives a branch name from the issue title and labels, self-assigns the issue, labels it "in progress", and creates a worktree via `workmux add` with the full issue context injected as a task prompt.

## Usage

```text
/create-worktree-from-issue 42
/create-worktree-from-issue the dark mode issue
```

Provide either an issue number or descriptive text to search for.

## Recommended Permissions

This skill runs GitHub CLI, workmux, and git commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": [
      "Bash(gh issue view *)",
      "Bash(gh issue list *)",
      "Bash(gh issue edit *)",
      "Bash(gh label create *)",
      "Bash(bash */launch-workmux *)",
      "Bash(git worktree list*)",
      "Bash(rm -f /tmp/workmux-prompt-*)"
    ]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "start issue #42": looks up issue 42 and creates a worktree for it
- "work on the dark mode issue": searches for a matching issue by title
- "create worktree for issue 15": same as providing the number directly

## See Also

- [Create Worktree](../create-worktree/README.md): create a worktree from a task description (not a GitHub issue)
- [Suggest Next Issue](../suggest-next-issue/README.md): get a recommendation for which issue to work on
- [All plugins](../../README.md)
