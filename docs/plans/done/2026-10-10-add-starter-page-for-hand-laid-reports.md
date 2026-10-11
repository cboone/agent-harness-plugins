# Add a starter page for hand-laid reports

## Context

Some reports fit neither board type: a cross-repository audit, a migration plan, an incident brief. They are asked for as a page anyway, and the ones laid out so far began by copying a template's stylesheet into a new file and adding page-specific rules after it. Those copies drift from the system as soon as `board.css` changes, and the skill gives no route for such a page: it says to answer in the terminal and never improvise a page outside the templates.

## Decisions

- **A static starter page ships beside the templates**, at `templates/starter/report.html`, outside the directory `render` lists board types from. It is the design system's board anatomy as plain HTML: masthead, count strip with a fact cell, summary, a lead section of ranked rows, a tier section, an aside, the Report divider, report rows, a reference table, and the footer. Its text is sample content that says what each part is for.
- **`report-board starter [--standalone] OUTPUT` writes it** with `board.css` inlined, using the same stylesheet checks as `render`. It refuses an existing OUTPUT, so it never writes over a page laid out by hand.
- **`board.css` gains the two pieces the conventions name and a hand-laid report needs:** the aside (`.aside`, `.aside-label`, `.aside-text`, `.aside--warn`) and the count-strip fact cell (`.count--fact`), with the design system's values. Charts stay out of scope.
- **A hand-laid report is a snapshot, not a board.** It carries no board data, so `extract`, `compare` and `validate` do not apply. It is edited by hand and republished to the same URL; its masthead and footer say when it was laid out and that it was laid out by hand.
- **The skill routes to it only on request.** A request for a board that no type fits is still answered in the terminal by default; when the user asks for a page, the skill starts from the starter rather than improvising one.

## Changes

1. `templates/board.css`: add the aside and the fact cell.
1. `templates/starter/report.html`: the starter page.
1. `scripts/report-board`: the `starter` command, its usage text, and its refusals.
1. `tests/scrut/report-board.md`: `starter` writes a page with the stylesheet inlined and no placeholder, `--standalone` writes a full document, and it refuses an existing output, extra operands, and a broken stylesheet.
1. `SKILL.md`, `design-conventions.md` and the plugin README: the hand-laid route, and the starter as its starting point.
1. Render the starter at desktop and phone widths in both themes and check it.
1. Run `make build`, `make test-all` and the check-versions skill. The branch already carries the 1.2.0 minor bump, which covers this capability.

## Out of scope

- Chart styles, which the conventions describe but no page shipped by the plugin draws yet.
- Migrating the existing hand-laid reports onto the starter.
