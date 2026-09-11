# Branch Review: feature/365-add-issue-report

Base: `origin/main` (merge base: `6761dc22`)
Commits: 11
Files changed: 30 (24 added, 6 modified, 0 deleted, 0 renamed), 12 of them generated mirror copies
Reviewed through: `2f5dc7b4`

## Summary

This branch adds the `publish-report-board` skill plugin for issue #365. A report board is an analysis published as a private Artifact with a stable URL and re-synced in place as its source data changes. The Catamount backlog report from Claude Design is implemented as the first board type, and a bundled `report-board` script validates board data, renders it into a self-contained page template, reads it back out of a published page, and compares two syncs.

The plugin is registered in the catalog, documented, mirrored to Codex CLI and OpenCode, and covered by 55 scrut cases. The review found correctness bugs in the script and the page, plus layout, accessibility, and documentation gaps; all of them are fixed in the last three commits.

## Changes by Area

### Skill and References

The skill body sets out a ten-step workflow: decide whether a board is warranted, locate the script, choose where the board lives, find the previous board, gather and analyze, validate, render, compare, publish, and report. The references cover when a board earns its cost, Artifact republishing and URL recovery, the sync metadata every board states, the shared design conventions, and the backlog-triage board type in full.

- `plugins/publish-report-board/skills/publish-report-board/SKILL.md`
- `plugins/publish-report-board/skills/publish-report-board/references/choosing-a-board.md`
- `plugins/publish-report-board/skills/publish-report-board/references/artifact-mechanics.md`
- `plugins/publish-report-board/skills/publish-report-board/references/sync-metadata.md`
- `plugins/publish-report-board/skills/publish-report-board/references/design-conventions.md`
- `plugins/publish-report-board/skills/publish-report-board/references/board-types/backlog-triage.md`

### Page Template

The Catamount design as a page drawn from embedded JSON. It defines light and dark themes as tokens, reflows to phone width, and builds every element through DOM text nodes and attributes. The page derives lane capacity, bar states, counts, and the "unblocks" and "eases" links from the data. It supports blocker references (pull requests, branches, other repositories, any URL), a soft "better after" relation, repositories without milestones, one-line empty states, and a live sync age that turns amber after a day and red after three.

- `plugins/publish-report-board/templates/backlog-triage.html`

### report-board Script

Four subcommands. `validate` enforces the rules every board relies on, most importantly that every open issue sits in exactly one lane. `render` fills the template, escaping the title and every `<` in the payload. `extract` reads the data back out of a page, including one wrapped in a host's document skeleton. `compare` produces the change report for a re-sync.

- `plugins/publish-report-board/scripts/report-board`

### Tests

55 scrut cases cover validation messages, rendering and escaping, standalone output, the extract round trip, the change report, file-handling edge cases, and usage errors.

- `tests/scrut/report-board.md`
- `tests/data/report-board/backlog-triage.json`
- `tests/data/report-board/backlog-triage-next.json`

### Catalog, CI, and Agent Config

The plugin enters the marketplace at 1.0.0 under `writing`, moving the catalog tag to `catalog-M66-m92-p154-n53`. The root README gains a Writing row and an external-tools note. The `Makefile` and `ci.yml` register the scrut environment, and `AGENTS.md` documents the plugin-root `templates/` directory and drops a slug-link count that had drifted.

- `.claude-plugin/marketplace.json`
- `README.md`
- `Makefile`
- `.github/workflows/ci.yml`
- `AGENTS.md`
- `plugins/publish-report-board/.claude-plugin/plugin.json`
- `plugins/publish-report-board/README.md`

### Generated Mirrors

Rebuilt with `bin/build-codex-marketplace` and `bin/build-opencode-mirror`; `bin/validate-plugins` confirms they match the source.

- `.agents/plugins/marketplace.json`
- `dist/codex/plugins/publish-report-board/`
- `dist/opencode/skills/publish-report-board`

## File Inventory

- **New files**: 24, of which 13 are source and 11 are generated mirror copies.
- **Modified files**: 6: `.claude-plugin/marketplace.json`, `.github/workflows/ci.yml`, `AGENTS.md`, `Makefile`, `README.md`, and the generated `.agents/plugins/marketplace.json`.
- **Deleted files**: none.
- **Renamed files**: none.

## Notable Changes

- **A new plugin layout.** `publish-report-board` is the first plugin with a plugin-root `templates/` directory. Its script finds the templates relative to its own resolved location, which works in all three harnesses.
- **A harness-specific capability.** Publishing uses Claude Code's Artifact tool. Codex CLI and OpenCode fall back to a standalone HTML file at a stable cache path, and the plugin README records that decision.
- **CI configuration.** Two scrut environment variables are added to the reusable scrut workflow's `scrut-env` list and to the `Makefile`.
- **Security-relevant handling.** Issue titles and notes come from GitHub and reach the page only as text. Every link starts from a validated `https://` address, and the render step escapes `<` so no string can close the data element.

## Plan Compliance

No plan file exists for this branch, so the review measures it against issue #365, whose definition of done and scope sections serve as the plan.

**Compliance verdict: good.** Every definition-of-done item is complete, every section of "What the skill covers" is implemented, and the one reduction in scope, shipping a single board type, was agreed at the start.

**Overall progress: 7/7 definition-of-done items done (100%).**

### Definition of Done

1. **Done.** `plugins/publish-report-board/` exists with `.claude-plugin/plugin.json` at `1.0.0`.
1. **Done.** It is registered in `.claude-plugin/marketplace.json`, alphabetically, under `writing`.
1. **Done.** It has a per-plugin `README.md`.
1. **Done.** The root README's Writing table has a row that uses the marketplace description verbatim.
1. **Done.** The harness-portability question is resolved, as a local HTML fallback, and the README records it.
1. **Done.** Both mirrors are regenerated and committed.
1. **Done.** `metadata.version` is recomputed and matches `bin/compute-catalog-state`.

### What the Skill Covers

1. **Deciding a board is warranted.** Done, in `choosing-a-board.md`.
1. **Naming the source of truth.** Done: the skill states that a board renders the source of truth and never becomes one, and forbids runtime state.
1. **Sync metadata.** Done: the data requires it, the header and footer show it, and a live age flags stale boards.
1. **Artifact mechanics.** Done: same-path republishing, URL recovery with `list` and `read`, conflicts, share pins, and recovery after a session restart.
1. **The re-sync procedure.** Done: `extract` recovers the previous data and `compare` reports what changed.
1. **Design conventions.** Done, in `design-conventions.md` and embodied in the template.

### Deviations

- **Scope reduction: one board type instead of four.** The issue proposed references for backlog triage, CI health, release readiness, and verification gaps. Only backlog triage ships, as agreed when the work began, and the skill says plainly that other board types are not built. No follow-up issues are filed yet.
- **Scope additions.** The Catamount template, the `extract` and `compare` subcommands, blocker references, the "better after" relation, the milestone-free layout, and the sync-age thresholds all go beyond the issue text. Each came from an explicit request during the work, and each serves the issue's own goals of trustworthy re-syncs and scannable boards.

### Fidelity Concerns

None outstanding. The issue asks that a re-sync report what changed rather than overwrite silently; before the review, `compare` missed blockers, soft links, or in-progress work that changed while staying set, and it now reports all three.

## Code Quality Assessment

**Overall quality: ready to merge.** The review found real defects, several of them in exactly the silent-failure class the issue warns about, and every one is fixed and covered by a test where a test can reach it.

### Strengths

- **Validation guards against a stale board.** Requiring every open issue in exactly one lane catches a re-sync that forgot a new issue. Rejecting closed blockers, in-progress picks, and better-after picks catches the other common drifts.
- **Data and presentation are separate.** The agent writes only JSON. The page derives everything else, so capacities and counts cannot disagree with the lanes they summarize.
- **Untrusted text is handled safely.** Nothing from the data reaches the page as markup.
- **Validation messages name the problem.** Each one says what is wrong and how to fix it, and malformed data of every shape probed produces messages rather than tool errors.

### Issues Found and Fixed

Two independent reviewers examined the script and the template, alongside a documentation pass and edge-case probes.

**Script** (`79cfd742`):

1. An empty file, or two boards back to back, validated as fine.
1. An output path naming a directory was silently written into, under a temporary name.
1. A start pick whose `waitingOn` was not a list crashed `jq`.
1. `compare` ignored blockers, better-after targets, and in-progress work that changed while staying set.
1. A better-after link between issues on the same branch was accepted.
1. `extract` was quadratic: 27 s on a 500 KB page, now 0.04 s.
1. Rendered pages were created readable by their owner alone.
1. Blocking loops went undetected.
1. Nits: duplicate issues within a lane or a claim, a path starting with a dash, a symlinked script, and a new in-progress issue reported twice.

**Page** (`2f5dc7b4`):

1. A sync time no calendar has, such as `24:30`, or an unparsable repository address, blanked the page.
1. An empty Start now could claim that everything was in progress when it was not.
1. Plurals such as "directorys".
1. `#12` in `owner/repo#12` linked to this repository's issue 12.
1. A branch name containing `#` broke its link.
1. The capacity unit overflowed its box, and lane rows were too narrow between 721 and 800 pixels.
1. Tabular figures spaced out the colon in the sync time.
1. Lane names were not headings, blocked cells had no labels for screen readers, and queued bar segments differed from runnable ones only in fill.

**Documentation** (`4ff72784`): recovery when a session restart clears the working files, passing the URL on every republish, gathering unmerged remote branches, a stale table of what the page draws, and README coverage of the new features.

### Accepted Risks

- Better-after loop detection is roughly cubic on long chains: an 800-issue chain takes 14 seconds to validate. Real boards have a handful of such links.
- The page needs JavaScript. A `<noscript>` message says so.
- `compare` does not validate its inputs. It tolerates fields of the wrong type instead, so a board written by an older version still compares.

### Suggestions

- File follow-up issues for the remaining board types, so the scope reduction is tracked.
- Run the `check-versions` skill immediately before opening the pull request, in case `main` moves.

## Verification

- `make lint`: markdownlint, Prettier, shellcheck, shfmt, and actionlint are clean.
- `make validate`: every JSON file and plugin rule passes.
- `make test-scrut`: 135 cases across 6 suites pass, 55 of them in `tests/scrut/report-board.md`.
- Both preview boards validate, render, and are published on the final template.
