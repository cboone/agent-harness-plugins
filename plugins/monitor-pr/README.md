# Monitor PR

Monitor a pull request until its checks pass, Copilot signs off on the current head, and it is mergeable, fixing failures along the way.

**Type:** Skill
**Trigger:** `/monitor-pr [<pr-number>]`
**Requires:** [`gh`](https://cli.github.com/) (authenticated)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Picks up where `pr` stops. The `pr` skill creates the pull request, prints the URL, and terminates; everything after that has traditionally been hand-driven. This skill takes over and tends the PR until it is ready to merge.

On each tick it takes one snapshot of the PR and reduces it to four axes: checks, Copilot, mergeability, and PR state. It then acts on the first problem it finds, in priority order:

1. **Branch is conflicted or behind the base**: invokes `merge-main`, since a stale branch is a common cause of check failures.
1. **A check failed**: pulls the failing job's logs and repairs it. Lint and format failures go to `lint-and-fix`; generated-tree drift is rebuilt with the repository's own build scripts; test and build failures are diagnosed from the logs.
1. **Copilot has not reviewed the current head**: waits. Copilot re-reviews automatically on push in most repository configurations. If no review arrives after two ticks, it requests one with `gh pr edit --add-reviewer "@copilot"`.
1. **Copilot reviewed the current head and left findings**: invokes `resolve-copilot-pr-feedback`.

Every push it makes invalidates Copilot's previous review, so the loop naturally goes back around after a fix. It stops when all four axes are clean at once, prints a full status table, and asks whether to merge, enable auto-merge, or leave it.

### It stops and asks

This is not a continue-at-all-costs skill. It halts the watch and puts the question to you when the fix is a judgment call about intended behavior, when the same check fails again after a fix attempt for it, when the fix would reach outside what the branch already changes, when the logs do not identify a cause, or when `merge-main` or `resolve-copilot-pr-feedback` reports something it could not finish.

### What counts as a Copilot sign-off

Copilot reviews are always `COMMENTED`, never `APPROVED`, so an approval state is never the pass signal. A sign-off means a Copilot review exists whose commit SHA equals the current head, the review-thread fetch returns nothing, and no review-body findings are left open. A review against an older SHA does not count.

### What does not gate

`reviewDecision` is reported in every status line but never blocks. A human `CHANGES_REQUESTED` will not stop this skill from declaring the PR ready, so that an outstanding human objection stays visible without stalling a watch on solo repositories that have no required reviewers.

### Pacing and harness support

Intervals adapt to the phase: shorter while checks are actively running, longer while waiting on Copilot, longest when nothing is moving. There is no wall-clock cap and no give-up count. The watch ends on a terminal state or an escalation, and you can interrupt it at any point.

On Claude Code the skill paces itself with the harness scheduler, which returns control between ticks and keeps the transcript small. `/loop /monitor-pr` is the recommended invocation there. Codex CLI and OpenCode have no scheduler, so the skill falls back to a blocking wait between polls inside a single turn. It works, but the whole watch accumulates in one turn's context.

Quiet ticks print a single line and are collapsed by the harness where it supports that. Only a real state change prints the full table.

## Usage

```text
/monitor-pr
/monitor-pr 361
/monitor-pr --interval 10m
/monitor-pr --no-fix
```

| Option           | Description                                                                     |
| ---------------- | ------------------------------------------------------------------------------- |
| `<pr-number>`    | Monitor a specific PR instead of the current branch's PR                        |
| `--interval <d>` | Override adaptive pacing with a fixed wait                                      |
| `--no-fix`       | Observe and report only: never push, invoke a fixing skill, or request a review |

## Recommended Permissions

This skill runs git and GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh pr view *)", "Bash(gh pr checks *)", "Bash(gh pr edit *)", "Bash(gh pr merge *)", "Bash(gh api --paginate --slurp repos/*/pulls/*/reviews*)", "Bash(gh run view *)", "Bash(gh run list *)", "Bash(git status*)", "Bash(git add *)", "Bash(git commit -S *)", "Bash(git push*)", "Bash(bin/build-codex-marketplace)", "Bash(bin/build-opencode-mirror)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

Two notes on these rules. **Flag position matters**: `Bash(gh api repos/*)` does not match `gh api --paginate --slurp repos/*`, because the flags come first, so the rule has to spell them out in order. **The repair paths need write rules**: step 6 stages, commits, and pushes fixes, and rebuilds generated trees, so `git add`, `git commit`, and the build scripts belong in the list alongside `git push`. The two `bin/build-*` entries are specific to this repository; substitute whatever build or codegen commands your own project's checks enforce.

## Examples

- "monitor the pr": resolves the current branch's PR and watches it until it is ready to merge
- "monitor pr 361": same behavior, against an explicit PR number
- "watch the pr": same behavior
- "keep an eye on the pr": same behavior
- "wait for ci": same behavior, though the watch still covers Copilot and mergeability rather than checks alone

## See Also

- [PR](../pr/README.md): create the pull request this skill then monitors
- [Resolve Copilot PR Feedback](../resolve-copilot-pr-feedback/README.md): the Copilot half of the loop, invoked once a review lands on the current head
- [Merge Main](../merge-main/README.md): invoked when the branch falls behind or conflicts with its base
- [Lint and Fix](../lint-and-fix/README.md): invoked to repair lint and format failures
- [All plugins](../../README.md)
