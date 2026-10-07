---
applyTo: "plugins/publish-report-board/**,tests/scrut/report-board*.md,tests/scrut/bugs-gather.md"
---

# Report board review instructions

For repo-wide conventions, see [copilot-instructions.md](../copilot-instructions.md) and `AGENTS.md` at the repository root.

- **`bugs-gather score` places bugs in tiers; `report-board validate` checks a board's consistency.** Placement depends on config the board data does not carry, such as `deadlineDays`, progress and park labels, and when triage entries expire against the sync time, so `report-board` cannot recompute tiers from the board alone. It checks the rules it can check from the board: that each section agrees with `bug.tier`, that a Critical entry has an escalate call or an assessment that earns Critical, and that signals and triage calls are consistent. Do not ask `report-board` to rerun the scoring rules.
- **`scripts/bugs-gather-queries/zenhub.graphql` is deliberately left open.** Its last line closes `workspace`, not the query; `gather_zenhub` appends one aliased `issueByInfo` field per bug and then the closing `}`. Do not flag the file as unbalanced on its own.
