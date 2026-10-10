# Write the design system into the design conventions

## Context

The Report Boards design system, built from the `bugs` and `backlog-triage` templates and the hand-laid reports, settled decisions that `design-conventions.md` does not yet record: a token vocabulary with role names, a fixed meaning for each state shape, notes as asides rather than callouts, count strip cells that hold a fact rather than a count, how charts are drawn, and what a board may make interactive. A session building or extending a board reads only the repository, so those decisions belong in the plugin's reference.

## Decisions

- `design-conventions.md` stays the single design reference. It gains the decisions above and keeps describing the two shipped templates accurately; the templates themselves do not change here.
- Role names stay as the templates use them. The reference lists one vocabulary and notes the `bugs` board names (`critical`, `on-critical`, `high`) as aliases, so nothing claims a class or token the templates do not define.
- The shapes table is normative for every board type: a shape keeps its meaning wherever it appears, and a new board type reuses an existing shape before inventing one.
- The design system artifact is private, so the reference does not link to it.

## Changes

1. Rewrite `plugins/publish-report-board/skills/publish-report-board/references/design-conventions.md`: tokens and roles, type scale, layout skeleton, the shapes table, notes, count strip fact cells, charts, links and interaction, then the existing writing rules.
1. Bump `publish-report-board` from 1.1.1 to 1.1.2: a reference change with no new behavior.
1. Run `make build`, `make test-all` and the check-versions skill.

## Out of scope

- Moving both templates onto shared class names and one stylesheet.
- Restyling the focus board on `feature/focus-board`.
