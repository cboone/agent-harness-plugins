# Restyle the Backlog Triage Board to Match the Bugs Board

Issue: #557

## Context

The `bugs` board (`plugins/publish-report-board/templates/bugs.html`, now on `main`) was redesigned on a Claude Design canvas: IBM Plex Sans and Mono, a graphite and orange light theme, a near-black dark theme, a masthead over a heavy rule, a count strip with one filled block, numbered rows instead of cards, a double rule labeled Report, and a 1200-pixel column. The `backlog-triage` board still has the Catamount look (Schibsted Grotesk, donkey ramp, slate badges, zebra rows, 1080 pixels), so the plugin's two boards no longer read as one system, and `design-conventions.md` has to carry a note that the bugs board departs from it.

The outcome: `backlog-triage.html` renders in the bugs board's look in both themes, keeps everything specific to a backlog (lane bars, capacity, serial and head lanes, the contention matrix, the blocked section), and `design-conventions.md` describes one shared look again. No data fields change, so `report-board` and its validation stay as they are.

## Decisions

- **Filled count block: Start now.** It is the count a reader acts on, as Critical is on the bugs board. It leads the strip; Open, Ready, Blocked, Lanes open and Branches at once follow as plain counts. Six columns at desktop, three at 860 pixels and below.
- **Section name stays "Start now"**, matching `startNow`. The time words are in its notes, so those drop "today": "Two branches to open.", "No branches picked.", "Nothing can start: every issue is blocked, queued behind another, or already in progress." The Lanes note drops "today" the same way.
- **Report divider** after Lanes: Start now and Lanes above it, the contention matrix and Blocked below it.
- **Shared code stays copied.** There is no build step, each template must stay one self-contained page, and the focus board (#558) is a third template still on its own branch. Extracting now would design a shared layer around two of three consumers. Instead, the copies get matching comments that name each other in both directions (today only `bugs.html` names its counterpart), and the extraction is offered as a follow-up issue once #558 lands.
- **Version:** a visual restyle with no new capability or data change, so a patch bump to `1.1.1`, confirmed with the check-versions skill before the PR.

## Changes

### 1. `plugins/publish-report-board/templates/backlog-triage.html`: styles

- Swap the Google Fonts link for the bugs board's IBM Plex link, and the header comment for one describing the new palette and what each accent means.
- Replace the token set with the bugs board's shared names and values (`--sans`, `--mono`, `--gutter`, `--ground`, `--ink`, `--body`, `--muted`, `--rule`, `--rule-soft`, `--link-rule`, `--focus`, `--aging`, `--stale`), plus backlog-only tokens in the same palette: `--primary` / `--on-primary` (the filled block, `#26292e` / `#ffb37a` light, `#8fb0ff` / `#0b1220` dark), `--accent` (`#a8430b` / `#f2b45a`, what is current: segments that can run now, contended cells, the In progress tag), `--bar-now`, `--bar-queued`, `--bar-edge`, `--bar-blocked`, `--hatch`, `--hit`, and `--chip-edge`. Light on `:root`, dark under `prefers-color-scheme` guarded by `:not([data-theme="light"])` and again under `[data-theme="dark"]`, as now.
- Base and layout from `bugs.html`: body type, `a` with the `--link-rule` underline, `.label`, `.num` in mono, `.board` at 1200 pixels with `gap: 56px`, `.section`, `.section-head`, `.section-title`, `.section-note`, `.ruled`, `.fold`, `.footer`.
- Backlog-specific pieces restyled rather than replaced:
  - Lane key badges become outlined mono tags; the capacity box loses its slate fill and becomes a large mono figure with a label, so the count strip keeps the only filled block.
  - Lane segments keep state in form: `now` solid accent, `queued` outlined with `--bar-edge`, `blocked` hatched over `--bar-blocked`.
  - Milestone chips become square outlined mono chips; `.chip--none` stays dashed. Soft ordering links (`.ref--soft`) keep the dashed underline.
  - The "In progress" tag uses the bugs board's `.tag` form in the accent color.
  - Lane item rows and blocked rows drop zebra fill for `--rule-soft` separators, matching the bugs board's report rows.
  - The contention matrix keeps its grid in `--rule`, with `--hit` cells and a `.table-wrap`-style scroll box.
- Breakpoints aligned with the bugs board's 860 pixels for the masthead, counts and Start now rows, keeping the backlog's 800-pixel lane-row stack and 720-pixel bar stack, and checking the matrix and lane bars at 390 pixels.

### 2. `backlog-triage.html`: markup in the script

- **Header** follows `bugs.html`: a `.masthead` with the eyebrow `Backlog triage · OWNER`, the repository name as the `h1`, and the `.when` column (sync time, `branch @ commit`, live age) over a 2-pixel ink rule; then the `.counts` strip with `.count--primary` for Start now; then the summary paragraph. The summary moves out of `main` into the header, as on the bugs board.
- **Start now rows** take the bugs board's `.urgent` shape: a zero-padded rank in the primary color, a line with the issue link, short title and any branch companions, the pick's `why` as the headline, and a side `dl.facts` with Lane (key and name), Milestone (chip, when the board has milestones) and Touches.
- **Lanes** keep `barRow`, `laneItem` and `laneBlock` and their logic untouched, changing only class names and wrappers. The capacity model, ranks and states stay byte for byte.
- **Report divider** `h("p", { class: "fold label", role: "separator" }, "Report")` between Lanes and the contention matrix.
- **Footer** takes the `.footer` style; its wording stays.
- Notes drop "today" as listed under Decisions.
- Comments on `h`, `prose`/`PROSE_REF`, `formatSync` and `refreshAge` name `bugs.html` as the counterpart, mirroring the comments already in `bugs.html`.

### 3. `plugins/publish-report-board/templates/bugs.html`

Comment-only: none needed if its counterpart comments still read correctly after the change; otherwise adjust wording so each pair names the other.

### 4. `plugins/publish-report-board/skills/publish-report-board/references/design-conventions.md`

- Opening paragraph: both templates embody the conventions; drop the sentence that the bugs board has a look of its own.
- Layout: describe the masthead, the count strip with one filled block for the count that matters most, the summary, numbered rows with the next action as headline and facts beside it, the Report double rule, and a 1200-pixel column.
- Add a short Type and palette rule: IBM Plex Sans for text and Plex Mono for numbers and labels; graphite and orange light theme, near-black dark theme with light blue and amber.
- Color: restate the accent rule in the new palette (the accent marks what is current or contended on a backlog board; the filled block marks the count that matters most), and keep blue reserved for focus, with the dark-theme exception for the filled block.
- Add neutral section names without time words.

### 5. `references/board-types/backlog-triage.md`

Update the "What the Page Draws" header row to name the filled Start now count and the summary, and note the Report divider above the contention matrix.

### 6. Version and mirrors

- `plugins/publish-report-board/.claude-plugin/plugin.json` to `1.1.1`; marketplace entries if they carry a version; run the check-versions skill.
- `make build` to regenerate mirrors, and commit any drift.

## Commits

Small Conventional Commits referencing #557, for example:

1. `docs: add plan for restyling the backlog triage board (#557)`
2. `feat: restyle the backlog triage board to match the bugs board (#557)`
3. `docs: describe one shared report board look (#557)`
4. `chore: bump publish-report-board to 1.1.1 (#557)`

## Verification

- Render both sample data files (`tests/data/report-board/backlog-triage.json` and `backlog-triage-next.json`) with `plugins/publish-report-board/scripts/report-board render`, wrap each in a doctype with `data-theme="light"` and `data-theme="dark"`, and take headless Chrome screenshots at 1440 and 390 pixels wide. Check: no horizontal page scroll at 390, the matrix scrolls in its own box, the lane bars and key fit, state reads as solid, outlined and hatched, the dashed no-milestone chip and soft links survive.
- Render the bugs sample beside it at the same widths to compare the two boards side by side.
- `make test-all`, including `tests/scrut/report-board.md` render and round-trip cases; observe the final result.
