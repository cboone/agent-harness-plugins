---
name: publish-report-board
description: >-
  Publish a recurring analysis, starting with backlog triage, as a live report
  board with a stable URL, and re-sync it in place as the source data changes.
---

# Publish Report Board

Publish an analysis as a report board, and re-sync it in place when its source data changes.

A report board is an analysis with three properties that terminal output serves badly: it is re-run against source data that keeps changing, it is scanned for what to do next rather than read top to bottom, and it stays open as a working surface. Each board type is a fixed page template plus a reference describing the data it needs and how to derive it.

**A board renders the source of truth and never becomes one.** GitHub, or whatever else a board reads, stays authoritative, and every sync re-derives the board from it. The page holds nothing a later sync would contradict: no checkboxes, no editable status, no runtime state, and no page that saves its own versions, which would also conflict with every republish.

## Board Types

| Board type       | Answers                                                           | Reference                                    |
| ---------------- | ----------------------------------------------------------------- | -------------------------------------------- |
| `backlog-triage` | What to start next, what can run in parallel, and what is blocked | `./references/board-types/backlog-triage.md` |

Only `backlog-triage` ships a template. When the user wants a board for another kind of analysis, such as CI health or release readiness, say that no template exists for it yet and deliver the analysis in the terminal. Do not improvise a page outside the templates: boards read as one system because they share one design, described in `./references/design-conventions.md`.

## Workflow

### 1. Decide Whether a Board Is Warranted

Read `./references/choosing-a-board.md`. A one-time answer belongs in the terminal; say so in one sentence and answer there.

### 2. Locate the Script

The `report-board` script ships with this plugin. It validates board data, renders it into the template, reads it back out of a published page, and compares two syncs. Invoke it via `bash` followed by the quoted path:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/report-board"
```

Claude Code replaces the plugin-root placeholder with the installed plugin's absolute, version-correct directory before this file reaches you, so there is no search step and no need for a shell variable. Keeping `bash` as the command prefix keeps the command token stable across plugin versions, which is what permission allowlist rules match on.

**If the path was not substituted**, it still begins with `$` rather than `/`. Codex CLI substitutes the placeholder only in hook commands, and OpenCode does not substitute it at all. In that case locate the script with `**/publish-report-board/**/scripts/report-board`, prefer a match inside the harness's own installed-plugin directory, ignore any match under a `.bak` or other backup directory, confirm it with `test -x`, and use that absolute path for the rest of the session. The script finds its templates relative to its own location, so run it from where it is installed rather than from a copy.

In the commands below, `REPORT_BOARD` is shorthand for that full **quoted path**.

### 3. Choose Where the Board Lives

Name the data file `REPO-BOARD.json` and the board `REPO-BOARD.html`, where `REPO` is the repository name without its owner and `BOARD` is the board type: `agent-harness-plugins-backlog-triage.json` and `agent-harness-plugins-backlog-triage.html`. Those two names are fixed rather than illustrative, and the same names are used wherever the files live. The local fallback has no Artifact to recover a board from and finds the previous one by this name alone, so a session that invents its own name reads a re-sync as a first publish: it reports no changes and leaves the earlier board sitting beside the new one.

`REPO-BOARD.html` names the published board, not every page this sync renders. Without the Artifact tool the two are separate files: step 7 renders a working page that step 8 is still free to reject, and step 9 renders the board itself once the checks have passed. Give that working page any other name in the same directory, such as `REPO-BOARD.next.html`, and leave `REPO-BOARD.html` alone until step 9. The fixed name governs discovery, which is what the rule above protects; it does not mean a sync may write only one file.

- **With the Artifact tool** (Claude Code): keep both files in the session scratchpad directory when the system prompt lists one, and otherwise in a directory from `mktemp -d`. The published Artifact is the board; the local files are this conversation's working copies.
- **Without the Artifact tool** (Codex CLI, OpenCode): keep both files in `${XDG_CACHE_HOME:-$HOME/.cache}/report-boards/REPO-PATH/`, creating it if needed. `REPO-PATH` is the host and path of `repoUrl` together, such as `git.example.com/enterprise/owner/name`, or `github.com/OWNER/REPO` when the board carries none. The whole address is the key because a host alone is not unique: two repositories can share an owner and a name under different path prefixes on one host. The rendered `REPO-BOARD.html` there is the board, and the next session finds it at that exact path.

### 4. Find the Previous Board

Establish whether this is a first publish or a re-sync before gathering anything. `./references/artifact-mechanics.md` covers each case, and each one has a silent failure mode.

- **Published earlier in this conversation**: the working `.json` holds the previous data; copy it to `PREVIOUS_JSON`. If the working files are gone, as they are once a session restart clears the scratchpad, recover the data from the published board the way the next case does.
- **Published in an earlier conversation**: use the URL the user gives, or find it with the Artifact `list` action by the board's exact title, which has to match exactly one entry. Boards for like-named repositories share a title, so where several match, confirm a candidate's `repo` from its extracted data before publishing over it, as `./references/artifact-mechanics.md` describes. Read the artifact, save the HTML it returns, and recover the data the page was built from:

  ```bash
  bash REPORT_BOARD extract PAGE_HTML > PREVIOUS_JSON
  ```

- **Local fallback**: the previous board is `REPO-BOARD.html` in that directory; `extract` it to `PREVIOUS_JSON` the same way. Look for that name rather than for whatever HTML the directory happens to hold, and treat its absence as a first publish rather than reaching for a near match.
- **Nothing found**: this is a first publish.

Keep `PREVIOUS_JSON` apart from the working files, as `REPO-BOARD.previous.json`. Steps 6 and 7 overwrite the working files with this sync, so a comparison against them finds nothing to report.

On a re-sync, the previous data is a draft, not a source. Its lanes and reasons are a starting point; GitHub decides what is true now.

### 5. Gather and Analyze

Follow the board type's reference for the commands to run and the analysis to perform. Record the sync metadata as you gather: `./references/sync-metadata.md` lists what every board must state.

### 6. Write and Validate the Board Data

Write the data as JSON to the working `.json` path with the Write tool, then validate it:

```bash
bash REPORT_BOARD validate DATA_JSON
```

Fix every problem it lists, then validate again. The rules catch a stale board: an open issue left out of every lane, a blocking issue that has since closed, a start pick that is already in progress. They check pull request, branch, and cross-repository references only for their shape, so confirm those are still open while gathering. Resolve each by placing or correcting the item, never by deleting an open issue from the data.

### 7. Render

Render to a working path, never straight onto a board that is already published:

```bash
bash REPORT_BOARD render DATA_JSON PAGE_HTML
```

Add `--standalone` when there is no Artifact tool. It writes a complete HTML document that opens straight from disk; the default output is a fragment, because the Artifact tool supplies its own document skeleton.

Without the Artifact tool, make `PAGE_HTML` the working page from step 3, `REPO-BOARD.next.html` beside the data file, rather than the board itself. Rendering onto the board would publish it here, before step 8 has compared anything, so a sync that step 8 tells you to abandon would already have replaced what was there. Step 9 renders onto `REPO-BOARD.html` once the checks have passed.

Never edit the rendered page. Change the data and render again.

### 8. Compare With the Previous Sync

Skip this step on a first publish. On a re-sync:

```bash
bash REPORT_BOARD compare PREVIOUS_JSON DATA_JSON
```

`PREVIOUS_JSON` is the copy step 4 saved, never a working file this sync has already overwritten. Keep the output: it is the change report, and a sync that silently overwrites the board is indistinguishable from one that did nothing.

Stop before publishing if the report carries a `Changed board identity` line naming `title`, `repo`, or `repoUrl`. A later conversation finds this board by its exact title, so a rebuilt title leaves the old board stranded and publishes a second one beside it, with nothing on either page saying so. The local fallback finds the board by the host and path of `repoUrl` as well, so a move between hosts, or to a different path prefix on one host, reads as a first publish and strands the board at the old path. These fields change only when the repository itself has been renamed or moved; confirm that is what happened, and move the old board to the new path, before going on.

### 9. Publish

**With the Artifact tool**, publish the rendered page as `./references/artifact-mechanics.md` describes: the same file path within a conversation, the board's URL from a later one, and the favicon and icon only on the first publish. Never pass `force`, and never declare runtime capabilities.

**Without it**, publishing is a second render, this time onto the board path itself. It comes last, after step 8, so that a re-sync which has to stop stops with the published board untouched.

Skip the freshness check on a first publish, since step 4 found no board and there is nothing to extract. Otherwise extract the board at its path once more and confirm it still holds the data step 4 recovered. A difference means another session published while this one was gathering, so begin again from that newer board rather than writing over it. Then run `render` again, giving it the board path as its output, and give the user that path.

Render onto the board rather than moving the file step 7 produced. `render` replaces a page in place: it writes through a temporary file in the board's own directory and gives it the mode the board already has, so a board written under a strict umask is not widened by a later session running under a looser one. Moving a file carries the mode of the file being moved, which would lose that.

This is weaker than what the Artifact tool does, and it is worth knowing by how much. That tool refuses a publish outright to a page that changed since this conversation read it. Nothing on disk refuses anything, and this check does not hold the file between confirming it and writing over it, so two sessions can still interleave. It catches the ordinary case and turns a silent overwrite into a stop. `./references/artifact-mechanics.md` states what it leaves uncovered.

### 10. Report

Tell the user:

1. The board's URL, or the absolute path of the local file, which opens in any browser.
2. The sync line: when, against which branch, and at which commit.
3. On a re-sync, the `compare` output under a "Changes since the last sync" heading, unedited.
4. The board's summary.
5. When the board is shared by link, that link viewers keep seeing the pinned version until the user moves the pin, as `./references/artifact-mechanics.md` describes.

Then stop. Publishing a board does not start work on anything it recommends.

## Error Handling

- If `gh` is not authenticated, tell the user to run `gh auth login` and stop; a board built from partial data is worse than none.
- If `jq` is missing, `report-board` exits with status 2 and says so. Tell the user to install it.
- If validation fails after an honest attempt to place every item, show the user the remaining problems rather than publishing a board that breaks its own rules.
- If a publish is refused because the page changed since this conversation read it, read it again, rebuild from what comes back, and publish again.
- If no board type fits the request, say so and answer in the terminal.
