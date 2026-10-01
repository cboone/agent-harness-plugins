# Branch Review: feature/add-confirm-clean-option-to-review-until-clean-skill

Base: main (merge base: 10fe5f67)
Commits: 4
Files changed: 12 (2 added, 10 modified, 0 deleted, 0 renamed)
Reviewed through: d7ac389f

## Summary

The branch adds an opt-in `--confirm-clean` option to the `review-until-clean` skill. When the option is set, the first clean round no longer ends the run: a second review over the same snapshot has to come back clean too. A single clean round stays the default. The option mirrors `monitor-pr`'s option of the same name, with one deliberate difference: the confirming round can run past `--max-rounds`. The plugin is bumped to 1.1.0, the Codex mirror is regenerated, and the branch includes the plan and a clean `review-until-clean` ledger.

## Changes by Area

### Skill behavior

`SKILL.md` adds the option, the confirming-round branch in step 8, the round-limit exception in step 10, the confirmation report in step 11, a confirmed-run example and an error-handling entry. `references/stop-rules.md` gains a "Confirming a clean result" section and updates the convergence and "What a clean result does not mean" sections to match. `references/ledger.md` gains a `Confirmation:` header line, a heading for the confirming round and a result sentence that names both rounds.

- `plugins/review-until-clean/skills/review-until-clean/SKILL.md`
- `plugins/review-until-clean/skills/review-until-clean/references/stop-rules.md`
- `plugins/review-until-clean/skills/review-until-clean/references/ledger.md`

### User documentation

The README adds the usage line, the options table row, an explanatory paragraph and an example.

- `plugins/review-until-clean/README.md`

### Versioning and generated mirrors

The plugin version moves from 1.0.0 to 1.1.0, a minor bump for a new capability. `make build` regenerated the Codex mirror.

- `plugins/review-until-clean/.claude-plugin/plugin.json`
- `dist/codex/plugins/review-until-clean/**` (5 files)

### Process documents

- `docs/plans/todo/2026-10-01-add-confirm-clean-to-review-until-clean.md`
- `docs/reviews/2026-10-01-feature-add-confirm-clean-option-to-review-until-clean-skill-until-clean.md`

## File Inventory

- **New (2):** the plan and the `review-until-clean` ledger above.
- **Modified (10):** the 5 source files under `plugins/review-until-clean/` and their 5 mirrors under `dist/codex/`.
- **Deleted / renamed:** none.

## Plan Compliance

**Verdict: good compliance, with one implementation defect against the plan's own semantics.** Every planned change landed. The round-budget rule, however, is written two incompatible ways across the files (see Fidelity concerns).

**Progress: 6/6 change items done (100%); 2/3 verification items done.**

Done:

1. `SKILL.md` updates: the option, step 8 branch, step 10 exemption, step 11 report, example output and error-handling entry. All present.
1. `stop-rules.md`: a new section covering the reasoning, the pair rule, the reset rule, the budget exemption, how terminal statuses apply and `--report-only`; the Convergence and "What a clean result does not mean" sections are adjusted.
1. `ledger.md`: the `Confirmation:` header, the confirming-round heading and the result wording.
1. README: usage line, table row, paragraph and example.
1. Version bumped to 1.1.0, and no `.codex-plugin` manifest exists to mirror it.
1. `make build` run and the mirrors committed.

Verification:

- `make build` and `make test-all` were run: done, with 637/637 scrut cases passing.
- The `check-versions` skill was run: done, with no issues.
- The planned end-to-end read of the default, confirmed and reset paths in `SKILL.md` is only partly done. Doing it would have exposed the budget inconsistency below.

**Deviations:**

- **Scope addition:** a `review-until-clean` ledger is committed. Committing process documents is the repository convention, so this is reasonable.
- **Deliberate divergence from `monitor-pr`:** `monitor-pr` counts each review in a confirmation pair as its own round, while this branch exempts the confirming round. The user chose this during planning, so it is reasonable.

**Fidelity concerns:**

- The plan says the confirming round "always runs, even when the first clean round used the last of `--max-rounds`". The files implement two different rules for how it is counted (Issue 1).

## Code Quality Assessment

**Overall: nearly ready to merge.** One issue needs fixing first: an ambiguity in the stopping rules that changes when a run ends.

**Strengths:**

- The reasoning for the option is stated once, the same way in each file, using the wording `monitor-pr` already established.
- Edge cases are covered: a reset when the snapshot moves, carried declines during confirmation, a failed confirming round, `--report-only`, and partial-scope coverage.
- The default behavior is unchanged in every file, since each new sentence is conditional on `--confirm-clean`.
- The tables are aligned, the mirrors are regenerated, and the version bump is the correct size.

**Issues to address:**

- [ ] **Issue 1 (Important): contradictory rules for counting the confirming round against `--max-rounds`.**
  - **The conflict.** The Convergence bullet in `references/stop-rules.md` says a confirming round "does not count against" the round limit, which means it never uses up any of the budget. `SKILL.md` step 10 says it is an "exception to that cap" only when "the first clean round used the last round". The `SKILL.md` example shows the confirming round as `Round 3 of 3`, which means it does use a slot when one is free.
  - **A case where they disagree.** With `--max-rounds 3`: round 1 has findings and they are fixed, round 2 is clean, and round 3, the confirming round, finds something. Under the stop-rules wording, only 2 rounds have been counted, so the loop fixes and goes on to a fourth round. Under `SKILL.md` and the example, no rounds remain and the run ends `stopped`. The same uncertainty affects the ledger's `Rounds: <n> of <max>` line.
  - **Fix.** Pick one rule and state it identically in all three places. The rule most consistent with the plan and the example: "The confirming round uses a round from the budget when one is left. When the first clean round used the last one, the confirming round runs anyway as one extra round, and it never earns another fix pass."

**Suggestions:**

- [ ] **Suggestion 1 (Nit): two notations for the confirming round.** `ledger.md` writes its heading as `## Round 3 (confirming round 2)`, while the `SKILL.md` example writes `Round 3 of 3 (confirming 2/2)`. Both work, but using the same "confirming 2/2" form in both would let a reader match ledger sections to terminal output at a glance.
- [ ] **Suggestion 2 (Nit): status for a `--report-only` run whose confirming round finds something.** The stop rules say such a run ends `stopped` when no rounds remain. `--report-only` never has fix rounds anyway, so it is unclear whether the status should be `stopped` or simply the round's findings, as a plain `--report-only` run would report today. The statuses for `--report-only` were already loosely defined before this branch, so this is optional.
