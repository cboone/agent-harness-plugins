# Design Conventions

Boards read as one system because they share one set of design rules. The `backlog-triage` template embodies these conventions, a new board type follows them, and the prose in the board data follows the writing rules at the end. The `bugs` board follows the same rules in a look of its own: IBM Plex Sans and Mono, a 1200-pixel column, and a graphite and orange light theme with a near-black dark theme.

## Layout

- **Summary before detail.** A header band carries the repository, the sync time, and a row of counts. One or two sentences of summary follow, then the sections, most actionable first. A reader who stops after the summary still knows what to do.
- **Every section opens with a heading and a one-line note** that says what the section claims, not what it contains.
- **One column of content**, at most 1080 pixels wide, that reflows into a single stack at phone width. Wide tables scroll inside their own container, so the page never scrolls sideways.

## Color

- **Semantic color stays separate from the accent.** Amber marks what is current or contended: the start picks, the lane segments that can run now, the contention cells. On a bugs board, the Critical count and tags are the one filled block, and High priority is the accent color in outline. Blue is reserved for interaction: hover, press, and focus, except in the bugs board's dark theme, where Critical takes the same light blue as the board's focus ring. Neither is decoration.
- **Both themes are defined as tokens.** Light values sit on `:root`; dark values sit under `prefers-color-scheme: dark` and again under `[data-theme="dark"]`, so an explicit choice wins in either direction. Components use tokens only, never a literal color that works in one theme.

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
