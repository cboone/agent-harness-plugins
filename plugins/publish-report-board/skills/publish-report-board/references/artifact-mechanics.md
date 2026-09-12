# Artifact Mechanics

The Artifact tool publishes a local HTML file as a private page on claude.ai, with a URL the user can keep. Most of what can go wrong here is silent: the wrong call does not fail, it creates a second board or leaves the first one stale, and nobody notices until someone acts on it.

## First Publish

Publish the rendered page with these parameters:

| Parameter     | Value                                            |
| ------------- | ------------------------------------------------ |
| `file_path`   | The rendered page in the working directory       |
| `favicon`     | The board type's emoji, from its reference       |
| `icon`        | The board type's icon word, from its reference   |
| `description` | One sentence naming the board and the repository |

Do not pass `url` on a first publish. The page's name comes from the `<title>` the template writes from the data's `title` field. Keep that title identical across syncs, because it is how a later conversation finds the board.

Give the user the URL the tool returns.

## Re-sync in the Same Conversation

Render to the same path and publish the same `file_path` again. The same path keeps the same URL. Rendering to a different path silently creates a second board with its own URL, and the first one stops updating with no sign on the page that it has.

Pass the board's `url` as well. It does no harm within the conversation, and it keeps the update on the same board if the session has restarted since the first publish. If the tool then refuses because this conversation has no record of the board, read it first, as the next section describes.

Omit `favicon` and `icon`. The board keeps the ones it has, and a changed favicon makes it read as a different page.

## Re-sync From a Later Conversation

A later conversation has no record of the path it published from, so a plain publish creates a new board instead of updating the old one.

1. **Get the URL.** Use the one the user gives. Otherwise run the `list` action and take the entry whose title matches the board's title exactly. Recovering a URL is a lookup, never a guess: if no title matches, say so and ask whether to publish a new board. Require exactly one match rather than taking the first. A title carries no owner, so two repositories of the same name produce the same title; when several entries match, `read` each candidate, `extract` its board data, and keep the one whose `repo` and `board` are this board's. If none is, or more than one is, ask instead of publishing over a board that belongs to something else. Publishing to the wrong URL succeeds silently, so this is the step that has to be certain.
2. **Read the board** with the `read` action and that URL. It returns the page's HTML, and saves a large page to a local file. The tool refuses a publish to an artifact the current conversation has not read, so this step is required.
3. **Recover the previous data** from that HTML with `report-board extract`. Use it as the draft for this sync and as `PREVIOUS` for `report-board compare`.
4. **Publish** the new render with `file_path` and with `url` set to the board's URL. Later republishes in the same conversation then use the same `file_path` and the same `url`.

## Shared Boards

A board the user has shared by link carries a share pin, and the `read` and publish results say which version link viewers see. A republish does not move that pin: the owner sees the new version, while everyone holding the link keeps seeing the pinned one. When the tool reports a pin, tell the user after every republish that link viewers still see the earlier version until the pin is moved from the page's share menu. Never report a re-sync as reaching everyone when the tool says it has not.

## Conflicts

If a publish is refused because the page changed since this conversation read it, read it again, rebuild from what comes back, and publish again. Never pass `force`. It discards whatever version is newer than yours, and a board has no legitimate reason to overwrite a version nobody here has seen.

## Runtime Capabilities

Never declare `capabilities` on a board, and omit the field on every republish so nothing changes. A board holds no state of its own. Anything a later sync would contradict, such as a ticked checkbox or an edited status, does not belong on the page, and a page that saved its own versions would conflict with every republish.

## Without the Artifact Tool

Codex CLI and OpenCode have no Artifact tool. There the board is the standalone HTML file at `${XDG_CACHE_HOME:-$HOME/.cache}/report-boards/HOST/OWNER/REPO/REPO-BOARD.html`, where `HOST` is the host of `repoUrl` or `github.com` when the board carries none, under the name the skill gives every working file:

1. Render with `--standalone` to that path, creating the directory if it does not exist.
2. Give the user the absolute path; the file opens in any browser.
3. On the next sync, look for the previous board at that exact path, run `report-board compare` against it, and render over it only afterwards.
4. Immediately before that render, extract the board at that path again and confirm it still holds the data this sync started from. A difference means another session published while this one was gathering, so begin again from the newer board instead of overwriting it.

The name is what makes this work. Nothing else on disk identifies a board, so a session that renders to a name of its own reads a re-sync as a first publish: it compares against nothing, reports no changes, and leaves the earlier board beside the new one.

That last step narrows a gap rather than closing it, and it is worth being plain about which. Two sessions re-syncing one board on the same machine can still interleave between the check and the write, because nothing here holds a lock across gathering and rendering, and bash has no primitive for one that works the same way on every platform this skill runs on. The Artifact tool refuses a publish to a page that changed since the conversation read it, and the local fallback has no equivalent to lean on. The check is a deliberate stand-in: it catches the ordinary case, where one session finishes while another is still gathering, and it turns a silent stale overwrite into a sync that stops and starts again from what is actually on disk.

Everything else in the skill is unchanged.
