# Publish Report Board

Publish a recurring analysis, such as backlog triage or bug triage, as a live report board with a stable URL, and re-sync it in place as the source data changes.

**Type:** Skill
**Trigger:** `/publish-report-board`
**Requires:** [`jq`](https://jqlang.org/) and an authenticated [`gh`](https://cli.github.com/); the bugs board also uses `curl` and a ZenHub API token when its repository has a ZenHub workspace

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Some analyses are re-run against data that keeps changing, scanned for what to do next, and kept open for days. Terminal output serves them badly: it disappears with the session, and the next session derives everything again. This skill publishes such an analysis as a report board, a private Artifact page with a stable URL, and re-syncs that page in place as the data moves.

A board renders the source of truth and never becomes one. GitHub stays authoritative, every sync re-derives the board from it, and the page holds nothing a later sync would contradict: no checkboxes, no editable status, no saved state.

Each sync:

1. Finds the previous board, whether it was published in this conversation or an earlier one, so the same URL updates instead of a second board appearing.
2. Gathers the source data and writes the board's analysis as JSON.
3. Validates it with the bundled `report-board` script, which rejects a board that leaves an open issue out of every lane, waits on an issue that has closed, recommends starting work already in progress, or marks a bug Critical on a triage call that has expired.
4. Renders it into the board type's page template.
5. On a re-sync, compares it with the previous board and reports what changed.
6. Publishes it, then reports the URL, the revision it was synced against, and the changes.

## Board Types

| Board type       | Answers                                                                                          |
| ---------------- | ------------------------------------------------------------------------------------------------ |
| `backlog-triage` | What to start next, what can run in parallel, and what is blocked                                |
| `bugs`           | Which of a repository's bugs are critical, which are high priority, and how the rest are triaged |

The backlog board opens with the sync time and six counts, then the issues to start now and why, the lanes of issues that can run in parallel with each lane's capacity and order, a contention matrix of components claimed by more than one issue, and the blocked issues with what frees each one. A blocker can be another issue, a pull request, a branch that has to merge, or an issue in another repository, and a softer "better after" relation keeps an issue out of the picks without blocking it. The board follows the viewer's light or dark theme and reflows to phone width.

The bugs board is action first and report second. Above the fold, a row for each critical bug, hurting people on production or open to anyone, and each high priority one, getting worse or still to confirm, leads with the next action and says who is affected; the bugs ready to land or fix follow. Below it sit the bugs that need investigating, a table of lower priority bugs, what was fixed, what is parked, and your triage note. Most of what makes a bug urgent, such as whether it is on production, who it reaches, and how it is known, lives in issue bodies rather than labels, so each sync reads the bugs that changed and caches what it learned; a bundled `bugs-gather` script gathers, scores, and caches deterministically. A committed triage note records your calls, such as escalating a bug or confirming it on production, and every sync applies them before its own rules.

Other board types, such as CI health or release readiness, do not have templates yet. Asked for one, the skill says so and answers in the terminal. Asked for a page anyway, such as an audit or a migration plan, it lays out a hand-laid report from a starter page in the same design: a one-time snapshot that carries no board data and is revised by hand rather than re-synced.

## Harness Support

Claude Code publishes boards with its Artifact tool. Codex CLI and OpenCode have no equivalent, so there the skill renders a complete standalone HTML file under `${XDG_CACHE_HOME:-$HOME/.cache}/report-boards/`, in a directory named for the host and path of the board's `repoUrl`, and reports its path. Keying on the whole address keeps same-named repositories apart across hosts and across path prefixes on one host. The file opens in any browser, and the next sync compares against it before rendering over it.

The plugin therefore ships unchanged to all three harnesses: only the publish step differs, and the skill chooses it by whether the Artifact tool is present.

## Usage

```text
/publish-report-board
/publish-report-board re-sync the backlog board
```

## The report-board Script

The skill drives the bundled script; you can also run it directly.

| Command                                        | What it does                                              |
| ---------------------------------------------- | --------------------------------------------------------- |
| `report-board validate DATA`                   | Checks board data against the rules every board relies on |
| `report-board render [--standalone] DATA PAGE` | Writes the data into its board type's template            |
| `report-board extract PAGE`                    | Prints the data a rendered page was built from            |
| `report-board compare PREVIOUS CURRENT`        | Reports what changed between two syncs                    |
| `report-board starter [--standalone] PAGE`     | Writes a starter page for a report laid out by hand       |

The bugs board adds `bugs-gather`, beside it:

| Command                                            | What it does                                                                                       |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `bugs-gather gather REPO GATHER`                   | Gathers open and recently closed bugs, their fixes, and their ZenHub state, and reports what moved |
| `bugs-gather reuse REPO GATHER ASSESSMENTS`        | Keeps the cached assessments that still match their bugs and lists the bugs to read                |
| `bugs-gather score REPO GATHER ASSESSMENTS SCORED` | Applies the triage note and the tier rules and prints the check-in report                          |
| `bugs-gather draft REPO GATHER SCORED DATA`        | Builds board data from a score, leaving the prose to write                                         |
| `bugs-gather save REPO GATHER ASSESSMENTS SCORED`  | Stores the cache the next sync starts from                                                         |

## Recommended Permissions

This skill runs GitHub CLI, git, and bundled-script commands that trigger permission prompts. Committing a bugs board's triage note runs a signed `git commit` on the note alone, which these rules leave to a prompt on purpose. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": [
      "Bash(bash \"*/report-board\" *)",
      "Bash(bash \"*/bugs-gather\" *)",
      "Bash(test -x *)",
      "Bash(gh repo view *)",
      "Bash(gh issue list *)",
      "Bash(gh pr list *)",
      "Bash(gh api --paginate --slurp 'repos/*/*/milestones?state=open*')",
      "Bash(gh api user *)",
      "Bash(jq *)",
      "Bash(cp *)",
      "Bash(git fetch *)",
      "Bash(git rev-parse *)",
      "Bash(git worktree list*)",
      "Bash(git branch --list*)",
      "Bash(git branch --remotes *)",
      "Bash(date -u *)",
      "Bash(readlink /etc/localtime)",
      "Bash(mkdir -p *report-boards/*)",
      "Bash(gh issue view *)",
      "Bash(mktemp -d*)"
    ]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## See Also

- [Suggest Next Issue](../suggest-next-issue/README.md): rank open issues and recommend what to work on next, in the terminal
- [All plugins](../../../../README.md)
