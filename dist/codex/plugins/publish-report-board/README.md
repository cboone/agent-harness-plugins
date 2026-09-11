# Publish Report Board

Publish a recurring analysis, starting with backlog triage, as a live report board with a stable URL, and re-sync it in place as the source data changes.

**Type:** Skill
**Trigger:** `/publish-report-board`
**Requires:** [`jq`](https://jqlang.org/), plus an authenticated [`gh`](https://cli.github.com/) for the backlog board

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Some analyses are re-run against data that keeps changing, scanned for what to do next, and kept open for days. Terminal output serves them badly: it disappears with the session, and the next session derives everything again. This skill publishes such an analysis as a report board, a private Artifact page with a stable URL, and re-syncs that page in place as the data moves.

A board renders the source of truth and never becomes one. GitHub stays authoritative, every sync re-derives the board from it, and the page holds nothing a later sync would contradict: no checkboxes, no editable status, no saved state.

Each sync:

1. Finds the previous board, whether it was published in this conversation or an earlier one, so the same URL updates instead of a second board appearing.
2. Gathers the source data and writes the board's analysis as JSON.
3. Validates it with the bundled `report-board` script, which rejects a board that leaves an open issue out of every lane, cites a blocker that has closed, or recommends starting work already in progress.
4. Renders it into the board type's page template.
5. On a re-sync, compares it with the previous board and reports what changed.
6. Publishes it, then reports the URL, the revision it was synced against, and the changes.

## Board Types

| Board type       | Answers                                                           |
| ---------------- | ----------------------------------------------------------------- |
| `backlog-triage` | What to start next, what can run in parallel, and what is blocked |

The backlog board opens with the sync time and six counts, then the issues to start now and why, the lanes of issues that can run in parallel with each lane's capacity and order, a contention matrix of components claimed by more than one issue, and the blocked issues with what frees each one. A blocker can be another issue, a pull request, a branch that has to merge, or an issue in another repository, and a softer "better after" relation keeps an issue out of the picks without blocking it. The board follows the viewer's light or dark theme and reflows to phone width.

Other board types, such as CI health or release readiness, do not have templates yet. Asked for one, the skill says so and answers in the terminal.

## Harness Support

Claude Code publishes boards with its Artifact tool. Codex CLI and OpenCode have no equivalent, so there the skill renders a complete standalone HTML file to `${XDG_CACHE_HOME:-~/.cache}/report-boards/OWNER/REPO/` and reports its path. The file opens in any browser, and the next sync compares against it before rendering over it.

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

## Recommended Permissions

This skill runs GitHub CLI, git, and bundled-script commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": [
      "Bash(bash \"*/report-board\" *)",
      "Bash(gh repo view *)",
      "Bash(gh issue list *)",
      "Bash(gh pr list *)",
      "Bash(gh api 'repos/*/milestones?state=open*')",
      "Bash(gh api user *)",
      "Bash(git fetch *)",
      "Bash(git rev-parse *)",
      "Bash(git worktree list*)",
      "Bash(git branch --list*)",
      "Bash(git branch --remotes *)",
      "Bash(date -u *)",
      "Bash(readlink /etc/localtime)",
      "Bash(mktemp -d*)"
    ]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## See Also

- [Suggest Next Issue](../suggest-next-issue/README.md): rank open issues and recommend what to work on next, in the terminal
- [All plugins](../../../../README.md)
