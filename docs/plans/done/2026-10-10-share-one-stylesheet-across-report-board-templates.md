# Share one stylesheet across report board templates

## Context

`bugs.html` and `backlog-triage.html` each carry a full copy of the board styles, kept in step by a comment asking that both change together. The copies have already drifted: the facts row gap, the 480px breakpoint (backlog only), the default tag color, the count strip's column count and wrapping border, and the section note width. The two boards also name the same components differently (`.urgent-*` and `.start-*` for ranked rows, `--critical` and `--primary` for the filled block). The design conventions now describe one vocabulary; the templates should use it.

## Decisions

- **One stylesheet, inlined at render.** `templates/board.css` holds every board style. Each template keeps an empty `<style>` element with a `/* __BOARD_STYLES__ */` placeholder, and `report-board render` puts the stylesheet there, so a published page stays one self-contained file. The Artifact tool serves a single page, so a linked stylesheet is not an option.
- **The stylesheet is trusted template input.** It is inserted before the title and data placeholders are split, and `render` refuses a stylesheet that is missing or that carries either placeholder, and a template without the styles placeholder.
- **One vocabulary**, from the design system:
  - Tokens: `--primary`, `--on-primary` and `--accent` on both boards; `--critical`, `--on-critical` and `--high` go.
  - Ranked rows: `.rank-row`, `.rank`, `.rank-main`, `.rank-line`, `.rank-headline`, `.rank-detail`, `.rank-with` and `.rank-side`, with `.rank-row--tier` for second-tier rows, replacing `.urgent-*` and `.start-*`. The backlog side column becomes a `.rank-side` wrapper around its facts list, as on the bugs board.
  - Sections: `section--lead`, `section--tier`, `section--accent` and `section--report`. Bugs `critical` becomes `lead`, `high` becomes `accent`, `ready` becomes `tier`; backlog `lanes` becomes `tier`.
  - Counts and tags: `.count--primary`, `.count--accent`, `.tag--primary`, `.tag--accent`.
  - Tables and notes: `.ref-table` and `.ref-group` replace `.lower-table` and `.lower-group`; `.note-log`, `.note-entry`, `.note-entry--expired`, `.note-text` and `.note-empty` replace `.triage-*`; `.dep--soft` replaces `.ref--soft`.
- **Drift resolves toward the more recent backlog restyle:** facts row gap 6px, the 480px breakpoint on both boards, section notes at most 88ch, the repository heading wrapping anywhere, and the third count dropping its border when the strip wraps. The count strip sizes its columns from its cells, so neither board states a count. `.tag` takes no default color; each tag names its own.
- **No other visual change.** Both boards are rendered from the scrut sample data before and after, at desktop and phone widths in both themes, and the screenshots compared. Only the drift listed above may differ.
- **Board data and validation are unchanged**, so published boards re-sync without migration.

## Changes

1. Add `templates/board.css`: the merged, renamed rules, with a header comment on the system and the token rules.
1. Replace each template's style block with the placeholder, and rename the classes its script emits.
1. `scripts/report-board`: insert the stylesheet in `render`, with the refusals above.
1. `tests/scrut/report-board.md`: render inlines the stylesheet and leaves no styles placeholder; render refuses a template without the placeholder and a stylesheet carrying a data or title placeholder; the existing copied-template testcase supplies a stylesheet.
1. `design-conventions.md`: drop the bugs-board aliases, and point at `board.css` as the single source of the styles.
1. Bump `publish-report-board` to 1.2.0: `render` gains a shared stylesheet, which a copied template now needs.
1. Run `make build`, `make test-all` and the check-versions skill.

## Out of scope

- Restyling the focus board on `feature/focus-board`, which will need rebasing onto these names.
- Components the design system adds that neither template draws yet.
