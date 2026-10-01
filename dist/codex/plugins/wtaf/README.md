# WTAF

Summarize where the conversation, branch, and tasks stand and what comes next, with a thorough mode that also reads the history.

**Type:** Skill
**Trigger:** `/wtaf` (aliases: `/summary`, `/recap`, `/where-are-we`)
**Requires:** optional [`gh`](https://cli.github.com/) for pull request, issue, and CI state

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Restores your footing when you have lost the thread: after a long agent run, a new day, a compaction, truncated scrollback, a merge or deploy that happened elsewhere, or several worktrees running at once. It reads the conversation, the branch and worktree, the governing plan in `docs/plans/`, the pull request and linked issue, and the session's open tasks, then answers in one screen:

- a one-sentence verdict on where things stand;
- the goal of the work, as a story rather than a list;
- a short status table in the plan's own terms (phases, steps, milestones);
- what is waiting on you, and loose ends such as unpushed commits or items discussed but never filed;
- one to three next actions.

It verifies what you tell it ("1714 is merged") and what the conversation claims, and labels each important fact as measured now, from the conversation, or assumed. It adapts to the repository: team and client repositories get deploy state, approvals, and filed-versus-unfiled items; personal projects get roadmap progress, manual verification lists, and review rounds. It also handles one-off situations such as running outside a repository, a mid-rebase checkout, changes another agent made, or comparing two worktrees.

The skill is read-only. It never edits, commits, pushes, stashes, or posts anything; it offers next steps and waits.

## Usage

```text
/wtaf
/wtaf --thorough
/wtaf 4379
/wtaf this worktree versus ../other-worktree
/summary
/recap --thorough
/where-are-we
```

| Option       | Description                                                                                                                                                        |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `--fast`     | Default. Summarize from the current conversation and cheap local and GitHub reads                                                                                  |
| `--thorough` | Also read earlier sessions in this directory, the branch history against its plan, review threads and issue discussion, sibling worktrees, and health measured now |
| scope (text) | An issue or PR number, a plan, a phase or step, "cross-repo", or another worktree to compare against                                                               |

`/summary`, `/recap`, and `/where-are-we` are aliases that run `wtaf` with the same arguments. Only `wtaf` is selected automatically from natural phrasing; the aliases run when typed.

## Recommended Permissions

This skill runs read-only git and GitHub CLI commands. To allow them without prompts, add rules like these to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": [
      "Bash(git status*)",
      "Bash(git log *)",
      "Bash(git diff *)",
      "Bash(git rev-list *)",
      "Bash(git rev-parse *)",
      "Bash(git branch --show-current)",
      "Bash(git worktree list*)",
      "Bash(git stash list*)",
      "Bash(git remote -v*)",
      "Bash(git for-each-ref *)",
      "Bash(git merge-base *)",
      "Bash(git ls-remote *)",
      "Bash(git tag --sort*)",
      "Bash(git fetch --no-tags *)",
      "Bash(gh pr view *)",
      "Bash(gh pr list *)",
      "Bash(gh issue view *)",
      "Bash(gh repo view *)",
      "Bash(gh run list *)",
      "Bash(gh api --hostname *)",
      "Bash(ssh -G *)",
      "Bash(workmux list*)",
      "Bash(make help)"
    ]
  }
}
```

`gh api --hostname *` also matches write requests; the skill sends only GET requests and read-only GraphQL queries, but narrow that rule if you prefer prompts for it. The `awk` and `jq` filters the skill pipes output through are left out on purpose, because a broad rule for either allows arbitrary programs (`awk` can run commands through `system()`), so expect a prompt for those pipelines. Thorough mode also runs the project's own documented check command, such as `make test`, which these rules do not cover. If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "wtaf": a fast summary of where things stand
- "where do we stand?": same behavior
- "it's a new day, summarize where we are": same behavior, with remote state re-read since the last session
- "great, it's merged. what's next?": verifies the merge, then summarizes and suggests next steps
- "remind me what's left to verify": answers that first, then gives the summary in a line or two
- "I've lost track of this whole project, review everything and summarize the current state": `--thorough`
- "what is this worktree versus the one at ../other?": compares the two worktrees' branches, plans, and PRs

## See Also

- [Review Branch](../review-branch/README.md): review the code on the current branch rather than summarize its status
- [Suggest Next Issue](../suggest-next-issue/README.md): choose the next issue once the current work lands
- [Create Deferred Issues](../create-deferred-issues/README.md): file the items that exist only in the conversation
- [All plugins](../../../../README.md)
