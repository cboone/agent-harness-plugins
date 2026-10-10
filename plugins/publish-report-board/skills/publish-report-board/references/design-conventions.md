# Design Conventions

Boards read as one system because they share one set of design rules. The `backlog-triage` and `bugs` templates both embody these conventions and share one stylesheet, `templates/board.css`, which `report-board render` writes into every page. A new board type follows these conventions and draws from that stylesheet rather than carrying styles of its own, and the prose in the board data follows the writing rules at the end. A report laid out by hand starts from `templates/starter/report.html`, which `report-board starter` writes with the stylesheet inlined, and follows the same rules. Where a rule below names something neither board template draws yet, such as a chart, an aside, or a fact cell, it fixes how a new board type or a hand-laid report draws it, so the system stays one system as it grows.

## Principles

- **Summary before detail.** The masthead, count strip, and summary answer "what do I do next". A reader who stops there still knows.
- **Rows, not cards.** Content is numbered rows between rules. Nothing sits in a filled box except the one filled count, the lead tier's tags, the fix line, and contended matrix cells.
- **One filled block.** One color fills one count-strip cell and carries through to the ranks and tags of the rows it counts. The accent marks the second tier. Everything else is ink, body, or muted.
- **State in form as well as color.** Every state a reader acts on has a shape, and color only reinforces it.
- **The board summarizes; the reader acts in the source.** Every reference links to where it lives.

## Tokens

Both themes are defined as tokens. Light values sit on `:root`; dark values sit under `prefers-color-scheme: dark` on `:root:not([data-theme="light"])`, and again on `:root[data-theme="dark"]`, so an explicit choice wins in either direction. Components use tokens only, never a literal color that works in one theme. The tokens are defined once, in the shared stylesheet.

| Token                   | Light                | Dark                 | Role                                                             |
| ----------------------- | -------------------- | -------------------- | ---------------------------------------------------------------- |
| `--ground`              | `#f1f1ef`            | `#121417`            | Page background                                                  |
| `--ink`                 | `#1b1c1e`            | `#e9ecf0`            | Headings, headlines, figures, heavy rules                        |
| `--body`                | `#36383c`            | `#c6cbd3`            | Secondary prose                                                  |
| `--muted`               | `#5d6066`            | `#9aa1ad`            | Labels, column heads, notes, the sync line                       |
| `--rule`                | `#d6d6d2`            | `#2c3138`            | Row separators and grids                                         |
| `--rule-soft`           | `#e4e4e0`            | `#22262c`            | Separators between rows of one list or table                     |
| `--primary`             | `#26292e`            | `#8fb0ff`            | The filled count, and the ranks and tags of the rows it counts   |
| `--on-primary`          | `#ffb37a`            | `#0b1220`            | Text on `--primary`                                              |
| `--accent`              | `#a8430b`            | `#f2b45a`            | The second tier: what is current, contended, or needs a decision |
| `--fix`, `--fix-ground` | `#2f5f28`, `#e3ebdf` | `#a6d492`, `#1c2819` | A change exists that resolves the item                           |
| `--aging`               | `#a8430b`            | `#f2b45a`            | The sync line once a board nears stale; the accent's value       |
| `--stale`               | `#b42318`            | `#ff8a80`            | Time has run out: a sync too old to trust, an overdue date       |
| `--link-rule`           | 45% muted            | 45% muted            | The underline a link rests on                                    |
| `--focus`               | `#2563eb`            | `#8fb0ff`            | The keyboard focus ring, and nothing else                        |
| `--bar-now`             | `#a8430b`            | `#f2b45a`            | A lane segment that can run now; the accent's value              |
| `--bar-edge`            | `#5d6066`            | `#9aa1ad`            | The outline of a queued segment; the muted value                 |
| `--bar-blocked`         | `#e4e4e0`            | `#22262c`            | The ground under a blocked segment's hatch; the soft rule value  |
| `--hatch`               | 28% ink              | 26% ink              | The 135-degree stripe of a waiting or unfinished shape           |
| `--hit`                 | `#f6e2d3`            | `#2b2418`            | Ground of a contended matrix cell                                |

Every board names the filled block `--primary` and the accent `--accent`, whatever the lead tier is called on the page, such as Critical or Start now. Blue is reserved for focus, except in the dark theme, where the filled block takes the same light blue as the focus ring.

Every text pair a board sets, and the focus ring against the ground, passes 4.5:1 in both themes. The tightest are the focus ring on `--ground` and `--accent` text on `--hit`, both in the light theme. Check a new pairing before using it.

Never add a series hue or another semantic color. `--aging` and the `--bar-*` tokens name roles for colors already in the palette, not new hues. Red (`--stale`) and green (`--fix`) already carry fixed meanings and always appear with words.

## Type

- **IBM Plex Sans for text and IBM Plex Mono for numbers and labels.** Count values, ranks, issue numbers in rows and tables, the sync line, column heads, and the eyebrow and divider labels are mono; headings, count labels, prose, and titles are sans. Digits that align are set in mono, whose figures are all one width.
- **Sizes step down by importance.** The repository heading is fluid from 40 to 64 pixels and the summary from 19 to 23, at most 62 characters wide. Section titles are 28 pixels for the lead section, in the filled block's color, 24 for the others above the divider, and 20 below it. A ranked row's headline is 21 pixels and its detail 16; a second-tier row's are 17 and 15, under a 22-pixel rank. Body text is 15, supporting lines 14 and 13. Mono figures are 40 pixels in the count strip, 24 for a fact cell, and 30 for a lead rank, zero-padded. Below 480 pixels the count figures, ranks, and headlines step down: 32, 22, and 18.
- **Sentence case** for titles and section names. Uppercase appears only in mono labels, column heads, tags, and count labels, which the styles set, with letter-spacing between 0.05em and 0.1em.

## Layout

- **Summary before detail.** A masthead carries an eyebrow label naming the board type and owner, the repository as a large heading, and the sync time, branch, commit, and live age on the right, over a heavy rule. A count strip follows, then one or two sentences of summary, then the sections, most actionable first.
- **One filled block in the count strip**, for the count that matters most: Critical on a bugs board, Start now on a backlog board. The other counts stay plain beside it; at most one more colors its label with the accent, as High priority does on a bugs board. A total that frames the others, such as Open bugs, can be muted. Do not color several figures by meaning.
- **A count-strip cell can hold a fact instead of a count**, such as a date, a ratio, or a state word, set smaller than a count. A fact cell is never filled.
- **Every section opens with a heading and a one-line note** that says what the section claims, not what it contains. Section names and notes are neutral, without dated time words such as "today" or "this week", which go stale between syncs; "Start now" names an action, not a date.
- **Rows, not cards.** What to act on is a list of numbered rows separated by rules, with the row's main claim as its headline and its supporting facts in a narrow column beside it: the next action on a bugs board, the reasons for the pick on a backlog board. On a bugs board, grouped lists such as Ready to go sit in columns.
- **A double rule labeled Report** divides what to act on from the reference material below it. The sections sit in a `main` landmark between the header, which holds the masthead, count strip, and summary, and the footer, and the divider carries its label for screen readers, since a separator's own text is not read. A narrative report where nothing ranks, such as an incident brief, drops the filled block and the divider and keeps the rest.
- **One column of content**, at most 1200 pixels wide with a side gutter of `clamp(16px, 4vw, 48px)`, that reflows to narrower grids at tablet and phone widths: rows stack their side columns beneath them, and the count strip wraps to three columns. Wide tables scroll inside their own container, so the page never scrolls sideways.
- **Square everything.** No rounded corners, no drop shadows, and no gradients except the hatch. An inset edge, such as the outline of a queued segment, is an inset `box-shadow` with no blur and no offset, which draws as a stroke inside the shape's own box.

## State in Form as Well as Color

Every state a reader acts on has a shape as well as a hue, so it survives a colorblind reader, a grayscale printout, and a glance. A shape keeps its meaning on every board type: reuse one of these before inventing another, and never reuse one for a different state.

| Shape                          | Means                                                        |
| ------------------------------ | ------------------------------------------------------------ |
| Filled with `--primary`        | The lead tier: the filled count, a Critical or Start now tag |
| Outlined in `--accent`         | The second tier: a High priority or In progress tag          |
| Solid `--accent`               | Can run now: a lane segment ready to start                   |
| Outlined in `--bar-edge`       | Queued or planned: will happen, not started                  |
| Hatched                        | Waiting on something, or not yet final                       |
| Dashed                         | Not settled: nothing exists yet, or nobody has confirmed     |
| Hollow `--accent` marker       | A gap, or a decision needed (no template draws it yet)       |
| Italic with a dashed underline | A fact nobody has confirmed                                  |
| Struck through with a tag      | Expired                                                      |
| Dashed underline on a link     | A soft ordering, such as "better after" or "eases"           |

The templates apply it this way:

- Lane segments that can run now are solid, queued ones are outlined, and blocked ones carry a hatch.
- An issue with no milestone gets a dashed chip.
- A soft ordering link gets a dashed underline; a hard one, "waits on" or "unblocks", keeps a solid one.
- An issue in progress carries an "In progress" tag that names its branch.
- Order is numbered only where it is real. Serial lanes number their steps; lanes with no order show a dot.
- On a bugs board, a Critical row has a filled tag and a High priority row an outlined one; a bug to confirm first carries a dashed tag; a fact nobody has confirmed is italic with a dashed underline, a fact the triage note set carries a dot, and an expired triage entry is struck through and tagged.

Show a key wherever three or more states appear together. Never use soft colored pills for state.

## Notes and Charts

- **A note is a ruled row, not a callout.** A method, a source, or a caveat sits between an ink rule above and a hairline below, under a mono label such as Method or Not yet known, with no fill and no colored side border. A caveat that changes how the reader should act turns its rule and label `--stale` and says so in words. At most one per section, after the section head.
- **Charts draw in ink.** Columns and bars are `--ink`, with gridlines in `--rule-soft`, a `--muted` baseline, and mono labels in `--muted`. Mark only the one value the board is about in `--accent`. A partial period, such as an incomplete week, is hatched with an ink outline. Where the data source changes, draw a dashed seam and name both sides.
- **Every chart states its scale and carries its values.** A caption names the unit and what a gridline or a full bar is, the SVG's title or the figure's label restates every value, and a `details` disclosure below holds the raw table. Bars that show magnitude and segments that show state are different encodings; never mix them in one figure.

## Links and Interaction

Every issue number, milestone, branch, and commit links to its source, including issue numbers written into prose, and the contention matrix links every component it lists. The footprint beside a lane or a pick stays prose, naming components the matrix links. The board summarizes; the reader acts in the source, so every row is one click away from it.

- Links rest on a `--link-rule` underline, muted at 45 percent opacity, that turns `currentColor` on hover. The link text keeps its color.
- Focus is always visible: a 2-pixel `--focus` outline offset by 2 pixels.
- Boards are read, not operated. The only control a board adds is a native `details` disclosure, and nothing moves beyond the browser's own disclosure.
- No icons, logos, or emoji. The masthead heading is the board's identity, and state is carried by shapes, not pictograms.

## Writing the Board Data

The template renders the prose fields as written, so they carry the board's voice.

- **`summary`**: one or two sentences that answer "what do I start next" and name the one constraint that shapes the answer.
- **`why`**, for each start pick: one or two sentences with concrete references, such as what the issue frees or what it collides with. Never restate the title.
- **Lane notes**: what is true of the group, usually why its order is what it is.
- **`blockedBecause`**: why the issue cannot start yet, in terms of what its blocker settles.
- **`action`**, for each Critical and High priority bug: the next concrete step, imperative, naming what to change or check. Never restate the title.
- **`impact`**, for each Critical and High priority bug: who is affected and how, in one sentence, with the numbers the issue gives.
- **`question`**, for each bug to investigate: the one thing to learn first, as a question.
- Write issue numbers as `#123`, or `OWNER/REPO#123` for another repository; the page links each one.
- Write about branches and work to start, never about staff or staffing. A board's reader is usually a single maintainer, not a team with people to assign.
- No em dashes, no time or effort estimates, and neutral technical terms throughout.
