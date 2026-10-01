# Branch Review: fix/display-skill-options

Base: main (merge base: 10fe5f67)
Commits: 5
Files changed: 91 (1 added, 90 modified, 0 deleted, 0 renamed)
Reviewed through: 468206bc

## Summary

The branch makes Claude Code show inline argument hints after a typed slash command (for example `/monitor-pr`) by adding `argument-hint` frontmatter to the 20 skills that accept arguments. The field was already on the rule 21 allowlist but unused. The branch also extends rule 21 of `bin/validate-plugins` so that a skill with an `## Options` section must declare a hint, documents the convention, updates the `create-plugin` guidance, patch-bumps the 21 touched plugins and regenerates the Codex and OpenCode mirrors.

## Changes by Area

### Skill frontmatter

One `argument-hint` line per skill, inserted after `description`, in the notation `<required>`, `[optional]`, `a|b`. Covers all 19 skills with `## Options` plus `review-plan` (`[path]`).

Files: `plugins/*/skills/*/SKILL.md` for address-issue, address-issue-in-worktree, address-review, commit, create-deferred-issues, create-worktree, lint-and-fix, merge-main, monitor-pr, pin-everything, rebase-onto-main, release, review-branch, review-colleague-pr, review-dependabot-config, review-plan, review-until-clean, set-up-review-config, suggest-next-issue, triage-dependabot-prs.

### Validation and tests

Rule 21 now tracks whether a non-empty `argument-hint` was seen and errors when a skill has `^## Options$` without one. A new `missing-argument-hint` fixture scenario strips `release`'s hint, and a scrut case asserts the error.

Files: `bin/validate-plugins`, `tests/fixtures/validate-plugin-fixture`, `tests/scrut/repo-tooling.md`.

### Documentation and authoring guidance

A new "Argument hints" subsection in the skill frontmatter section of the plugin development guide; `create-plugin`'s key points, checklist and `references/skill-md.md` now allow and describe the field.

Files: `docs/plugin-development.md`, `plugins/create-plugin/skills/create-plugin/SKILL.md`, `plugins/create-plugin/skills/create-plugin/references/skill-md.md`.

### Versions and generated mirrors

Patch bumps in each touched `.claude-plugin/plugin.json`; regenerated `dist/codex/` and `.agents/` output.

### Process docs

The plan, `docs/plans/todo/2026-10-01-add-skill-argument-hints.md`.

## File Inventory

- **New files (1)**: `docs/plans/todo/2026-10-01-add-skill-argument-hints.md`
- **Modified files (90)**: 21 skill or reference sources, 21 plugin manifests, their generated mirrors, `bin/validate-plugins`, the fixture, the scrut suite and `docs/plugin-development.md`
- **Deleted files**: none
- **Renamed files**: none

## Notable Changes

- **Merge gate tightened.** Rule 21 now fails CI for any future skill that adds an `## Options` section without a hint. This is intentional and every current skill satisfies it.
- No dependency, CI workflow or security-relevant changes.

## Plan Compliance

**Compliance verdict:** Good compliance. Every implementation item is done; the only remaining item is the manual check in a live Claude Code session, plus the `check-versions` run the plan schedules for before the PR.

**Overall progress:** 7/9 items done (78%), with the two outstanding items both verification steps.

### Done

1. **Add `argument-hint` to every skill that accepts arguments**: done for all 19 `## Options` skills plus `review-plan`. Hints were verified against each skill body, and the plan records where they differ from the proposed table.
1. **Scan skills without `## Options`**: done. `create-issue`, `pr` and `create-plugin` take no documented arguments; `review-plan` received `[path]`.
1. **Patch bumps**: done for all 21 touched plugins. None of them ships a `.codex-plugin/plugin.json` that needed mirroring; validation confirms manifests agree.
1. **Extend rule 21 with a passing and failing case**: done. The failing case is the new scenario; the passing case is the existing `valid` scenario, which now exercises 20 hinted skills.
1. **Document in `docs/plugin-development.md`**: done.
1. **Update `create-plugin` guidance and checklist**: done, including `references/skill-md.md`, which the plan did not name but which held the conflicting "exactly two fields" statement.
1. **Regenerate mirrors and commit separately**: done, in the planned commit order.

### Not started

1. **`check-versions` skill before the PR**: not yet run.
1. **Manual verification in Claude Code**: not yet done. Ghost-text display is the user-facing goal and is not covered by any automated test.

### Deviations

- **Hint content differs from the plan's table** for `create-deferred-issues` (no positional), `address-review` (path required), `address-issue-in-worktree` (accepts a description), `create-worktree` (two more flags), `review-colleague-pr` (`requirement-docs...`) and `suggest-next-issue` (`[filters...]`). Reasonable: the plan instructed verifying each against the skill body, and the plan file records the outcome.
- **`address-issue` groups `--dry-run|--no-approval` as alternatives** rather than listing them in Options order. Reasonable: the skill calls them opposite ends of the same gate.
- **Scope addition:** `references/skill-md.md` updated. Justified, as it otherwise contradicted the new guidance.

### Fidelity concerns

None of substance. The plan said to keep long hints short by listing frequently used flags only; `monitor-pr`, `create-worktree` and `review-until-clean` list every flag instead, producing long ghost text. This favors completeness, which matches what the user asked for.

## Code Quality Assessment

### Code quality

The validator change is small and follows rule 21's existing shape: a per-skill flag set inside the existing frontmatter loop and checked after it, with a comment explaining why. The fixture scenario mirrors its neighbors. Documentation is placed in the existing skill frontmatter section next to the allowlist table it relates to.

### Potential issues

1. **Rule 21 header comment is now incomplete** (`bin/validate-plugins`, the block starting at the `21. Skill frontmatter fields are on the allowlist` banner). It describes only the allowlist; the new Options check is explained only by the inline comment near the end of the loop. A reader scanning rule headers will miss it. Low severity.
1. **Empty-value detection handles only `""`.** A hint written as `argument-hint: ''` or as a block scalar whose first line is empty passes as non-empty. Low severity; no current skill does this, and the documented form is double-quoted.
1. **The Options check matches only the exact heading `## Options`.** A skill that documents arguments under another heading (as `review-plan` does in prose) is not required to have a hint. This is a deliberate, documented scope, not a bug, but the docs say "every skill that accepts arguments declares one" while the validator enforces a narrower condition.
1. **Fixture comment wording** ("release carries no extended frontmatter field of its own beyond argument-hint, so each scenario adds exactly the one it tests") is slightly awkward now that `missing-argument-hint` removes rather than adds a field. Cosmetic.

### Completeness

No TODOs, stubs or commented-out code. Tests accompany the validator change. The plan remains in `docs/plans/todo/`; move it to `docs/plans/done/` when the work is complete, per repository convention.

### Verdict

**Ready to merge after the two verification steps.** Run `check-versions` and confirm the ghost text appears in Claude Code for `/monitor-pr`.

**Strengths:** the root cause was identified precisely (an allowed but unused field); hints were checked against each skill's real argument handling rather than copied from the plan; the regression guard is enforced in CI with a targeted test; commits are small and ordered logically.

**Issues to address:**

1. Run the `check-versions` skill.
1. Manually confirm hint display in Claude Code.

**Suggestions:**

1. Mention the Options-section requirement in rule 21's header comment.
1. Treat `''` as empty in the hint check.
1. Reword the fixture comment for the removal scenario.
