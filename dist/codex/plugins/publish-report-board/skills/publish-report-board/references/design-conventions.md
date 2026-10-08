# Design Conventions

Boards read as one system because they share one set of design rules. The `backlog-triage` and `bugs` templates both embody these conventions, a new board type follows them, and the prose in the board data follows the writing rules at the end.

## Type and Palette

- **IBM Plex Sans for text and IBM Plex Mono for numbers and labels.** Count values, ranks, issue numbers in rows and tables, the sync line, column heads, and the eyebrow and divider labels are mono; headings, count labels, prose, and titles are sans.
- **Two themes.** The light theme is graphite and orange: a `#f1f1ef` ground, `#1b1c1e` ink, a `#26292e` filled block with `#ffb37a` text, and a `#a8430b` accent. The dark theme is near-black, `#121417`, with light blue `#8fb0ff` for the filled block and amber `#f2b45a` for the accent.

## Layout

- **Summary before detail.** A masthead carries an eyebrow label naming the board type and owner, the repository as a large heading, and the sync time, branch, commit, and live age on the right, over a heavy rule. A count strip follows, then one or two sentences of summary, then the sections, most actionable first. A reader who stops after the summary still knows what to do.
- **One filled block in the count strip**, for the count that matters most: Critical on a bugs board, Start now on a backlog board. The other counts stay plain beside it, except that a bugs board colors its High priority label with the accent.
- **Every section opens with a heading and a one-line note** that says what the section claims, not what it contains. Section names and notes are neutral, without dated time words such as "today" or "this week", which go stale between syncs; "Start now" names an action, not a date.
- **Rows, not cards.** What to act on is a list of numbered rows separated by rules, with the row's main claim as its headline and its supporting facts in a narrow column beside it: the next action on a bugs board, the reasons for the pick on a backlog board. On a bugs board, grouped lists such as Ready to go sit in columns.
- **A double rule labeled Report** divides what to act on from the reference material below it. The sections sit in a `main` landmark between the header, which holds the masthead, count strip, and summary, and the footer, and the divider carries its label for screen readers, since a separator's own text is not read.
- **One column of content**, at most 1200 pixels wide, that reflows into a single stack at phone width. Wide tables scroll inside their own container, so the page never scrolls sideways.

## Color

- **Semantic color stays separate from the accent.** The filled block and the ranks of the rows it counts share one color. The accent marks the second tier of attention: on a backlog board, what is current or contended, meaning the lane segments that can run now, the contention cells, and work in progress; on a bugs board, High priority, in outline. Milestone chip markers and other secondary marks stay neutral. Blue is reserved for focus, except in the dark theme, where the filled block takes the same light blue as the focus ring. Neither is decoration.
- **Both themes are defined as tokens.** Light values sit on `:root`; dark values sit under `prefers-color-scheme: dark` and again under `[data-theme="dark"]`, so an explicit choice wins in either direction. Components use tokens only, never a literal color that works in one theme. Tokens both templates use carry the same names and values. The filled block and the accent carry role names with the same values: `--primary` and `--accent` on a backlog board, `--critical` and `--high` on a bugs board.

## State in Form as Well as Color

Every state a reader acts on has a shape as well as a hue, so it survives a colorblind reader, a grayscale printout, and a glance:

- Lane segments that can run now are solid, queued ones are outlined, and blocked ones carry a hatch.
- An issue with no milestone gets a dashed chip.
- A soft ordering link, "better after" or "eases", gets a dashed underline; a hard one, "waits on" or "unblocks", keeps a solid one.
- An issue in progress carries an "In progress" tag that names its branch.
- Order is numbered only where it is real. Serial lanes number their steps; lanes with no order show a dot.
- On a bugs board, a Critical row has a filled tag and a High priority row an outlined one; a bug to confirm first carries a dashed tag; a fact nobody has confirmed is italic with a dashed underline, a fact the triage note set carries a dot, and an expired triage entry is struck through and tagged.

## Links

Every issue number, milestone, branch, and commit links to its source, including issue numbers written into prose, and the contention matrix links every component it lists. The footprint beside a lane or a pick stays prose, naming components the matrix links. The board summarizes; the reader acts in the source, so every row is one click away from it.

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
