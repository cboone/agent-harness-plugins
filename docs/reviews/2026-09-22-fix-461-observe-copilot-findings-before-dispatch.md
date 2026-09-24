# Branch Review: fix/461-observe-copilot-findings-before-dispatch

Base: `main` (merge base: `ba8fd093`)
Commits: 3
Files changed: 17 (3 added, 14 modified, 0 deleted, 0 renamed)
Reviewed through: `563a5d78`

## Summary

Closes the observability gap in `monitor-pr` step 4: the dispatch condition named open threads, review-body findings, and format drift, but the step 3 snapshot returned only review metadata, so none of the three was actually observable. The branch bundles a byte-identical copy of `resolve-copilot-threads` in `monitor-pr` and runs its read-only `fetch` and `fetch-reviews` commands in step 3, then rewrites the step 4 condition, the Ready Criteria Copilot row, the Dependabot rules, the step 7b guard and escalation rule, and the step 7d `--confirm-clean` standard against what the probe reports.

## Changes by Area

**Copilot observability (the substance).** `plugins/monitor-pr/skills/monitor-pr/SKILL.md` gains a `#### The Copilot feedback probe` subsection under step 3 with two commands and six governing points, gated on the newest review matching `headRefOid`. Step 4's Copilot condition now cites the probe and carries the once-per-review `id` guard. A fourth Ready Criteria rule explains why an already-handled review-body finding still leaves the axis clean.

**Escalation semantics.** Step 7b's single paragraph splits into two: one that escalates when open threads or format drift survive a clearing report, and one that explicitly exempts review-body findings. This is the load-bearing change in the branch.

**Bundled helper.** `plugins/monitor-pr/scripts/resolve-copilot-threads`, 725 lines, byte-identical to the resolver's copy.

**Resume state.** `references/checkpoint.md` records the probe result in the Snapshot row, and Resume Procedure step 5 is corrected so a steady review-body finding count is not treated as an escalation.

**Repository docs and wiring.** `plugins/AGENTS.md`, `docs/plugin-development.md`, `Makefile`, `.github/workflows/ci.yml`, version 1.5.0, regenerated `dist/codex/`.

**Tests.** One `cmp` byte-identity testcase in `repo-tooling.md`; two `parse-reviews` testcases in `resolve-copilot-threads.md` that run the shipped copy.

## File Inventory

**New (3):** `plugins/monitor-pr/scripts/resolve-copilot-threads`, `dist/codex/plugins/monitor-pr/scripts/resolve-copilot-threads`, `docs/plans/done/2026-09-21-observe-copilot-findings-before-dispatch.md`

**Modified (14):** `plugins/monitor-pr/` (SKILL.md, checkpoint.md, README.md, plugin.json), `plugins/AGENTS.md`, `docs/plugin-development.md`, `Makefile`, `.github/workflows/ci.yml`, `tests/scrut/` (2), `dist/codex/plugins/monitor-pr/` (4)

## Notable Changes

- **New CI environment entry**: `MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN` added to both `SCRUT_ENV` and `scrut-env`. Both were updated together, which is the trap `plugins/AGENTS.md` warns about.
- **New permission surface**: `Bash(bash \"*/resolve-copilot-threads\" *)` added to the recommended allowlist. It is path-agnostic and already covers the resolver's copy, so users who have that rule need no change.
- **Version**: 1.5.0, minor, correct for a new capability. `resolve-copilot-pr-feedback` is untouched and correctly does not move.

## Plan Compliance

Plan: `docs/plans/done/2026-09-21-observe-copilot-findings-before-dispatch.md`

**Verdict: good compliance on the implementation, incomplete on verification.** Every planned change landed, two justified scope additions were made, and one plan verification step was silently substituted rather than performed. The plan also had a blind spot that the implementation inherited.

**Overall progress: 8/8 change items done (100%); 4/6 verification items done, 1 partial, 1 not done (75%).**

### Done

| Plan item                                                 | Implemented by                                       | Caveat                                                              |
| --------------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------- |
| 1. Bundle the script                                      | `plugins/monitor-pr/scripts/resolve-copilot-threads` | Byte-identity confirmed by `cmp` and a planted defect               |
| 2. SKILL.md step 3 probe                                  | `#### The Copilot feedback probe`                    | All six documented points present; one is inaccurate, see finding 3 |
| 2. Step 4 condition, Dependabot sentence, `--no-fix` note | Step 4 list and trailing paragraphs                  | Matches plan                                                        |
| 2. Ready Criteria row                                     | Copilot row                                          | Matches plan intent                                                 |
| 2. Step 7b guard and escalation, step 7d                  | 7b split into two paragraphs; 7d item 5 rewritten    | Matches plan                                                        |
| 3. `checkpoint.md` Snapshot row                           | Snapshot row                                         | Matches plan                                                        |
| 4. README, 5. version, 6. repository docs                 | As planned                                           | See deviation 2 and finding 1                                       |
| 7. Tests and wiring, 8. Regenerate                        | As planned                                           | Matches plan                                                        |

### Deviations

1. **Scope addition, justified:** the fourth Ready Criteria rule was not in the plan. Without it the Copilot row's "already returned `Completed`" clause has no explanation, so this earns its place.
1. **Scope addition, necessary:** `checkpoint.md` Resume Procedure step 5 was edited beyond the plan. The old text said to escalate when "findings remain against an already processed review", which directly contradicts the new step 7b rule. Leaving it would have shipped two rules in conflict. This should have been in the plan.
1. **Verification substitution, not disclosed at the time:** plan verification item 5 said to run the probe commands by hand against a real PR with a current-head Copilot review. That was not done. The jq filters were exercised against fixtures through `parse-reviews` instead, which does not test `fetch`, `fetch-reviews`, pagination, or the `gh` invocation. The substitute is weaker than what the plan called for, and the completion report did not say so.
1. **Verification item 2 is partial:** a single clean `make test-all` was never observed. The one full run had a testcase time out under contention from three concurrent scrut runs; the affected file was re-run to 43/43 separately. The conclusion is sound, but it was assembled from two runs rather than one.

### Plan blind spot

The plan listed `plugins/AGENTS.md` and `docs/plugin-development.md` as the documentation to update and did not consider the root `README.md`. That omission propagated straight into the implementation. See finding 1.

## Code Quality Assessment

**Overall: not ready to merge.** The core design is sound and the prose is up to the standard of the surrounding file, but there is one documentation defect that makes a harness-compatibility claim false and one reachable state where the watch waits forever. Both are small edits.

### Strengths

- **The design choice is right and is defended in the text.** Sharing the parser instead of restating its clean-or-drift rules is the decision that makes this fix durable, and both `docs/plugin-development.md` and the new `repo-tooling.md` section say why, in the "failing loud beats failing quiet" register the rest of the repository uses.
- **The escalation carve-out is the non-obvious part and it is correct.** Making the findings condition observable would otherwise have converted every noted review-body finding into a false escalation, because review bodies are immutable and the count never falls. Splitting 7b into "escalate when a source that should have cleared did not" and "review-body findings are the exception" gets this right and explains the trap.
- **The `cmp` guard was defect-tested, not assumed.** A planted byte made it fail, and the file was restored.

### Issues to address

#### P1 — 1. The root README's known-limitations lists are now wrong

Both `### Codex CLI known limitations` and `### OpenCode known limitations` in the root `README.md` enumerate the skills whose bundled script paths arrive unsubstituted: `/address-issue-in-worktree`, `/create-worktree`, `/publish-report-board`, and `/resolve-copilot-pr-feedback`. `monitor-pr` is now a fifth and appears in neither.

This is not cosmetic: the lists are the repository's statement about what works on which harness, `monitor-pr` previously needed no script at all, and nothing machine-checks these lists. Add `monitor-pr` to both.

Consider also whether `plugins/monitor-pr/README.md` should link to `#using-with-opencode` now that the limitation applies to it. The repository's rule is to link "when relevant", though `resolve-copilot-pr-feedback`'s README does not link there either, so following suit is defensible.

#### P1 — 2. A review processed with `Partial` or `Failed` can livelock a resumed watch

Step 4's new `id` clause prevents re-dispatch, and the Ready Criteria row clears a review-body finding only on `Completed` or `No unresolved Copilot feedback`. So for a review whose unfinished work is review-body findings only:

- step 4 condition 6 does not match (`id` already invoked)
- conditions 7 and 8 do not match
- condition 9 does not match (Copilot axis not clean)
- condition 10 waits, every tick, forever

`checkpoint.md` Resume Procedure step 5 escalates only on open threads or drift, and 7b's new escalation rule covers only `Completed` and `No unresolved Copilot feedback`. The immediate `Partial` escalates through 7b's continuation contract and stops the watch, so this needs a resume to reach, but resuming after an escalation is the documented flow ("`/monitor-pr` resumes the watch once they have decided").

One sentence fixes it, for example in the Ready Criteria rules: a review already processed with an outcome other than `Completed` or `No unresolved Copilot feedback` never becomes clean and never re-dispatches, so escalate per step 9 rather than waiting.

This is a sharpened pre-existing ambiguity rather than a fresh regression, but this change is precisely about making these transitions well-defined, so it belongs here.

#### P2 — 3. The "A `null` result is not a failure" bullet describes an output shape the command does not produce

The documented filter ends `[.[] | select(.id == $review_id)] | last | {id, url, hasFormatDrift, findings: (.findings | length)}`. On no match, jq's object construction over `null` yields:

```json
{ "id": null, "url": null, "hasFormatDrift": null, "findings": 0 }
```

Verified against `tests/data/copilot-reviews/format-d-drift.json`. An agent told to expect `null` may read this object as a match and treat `hasFormatDrift: null` as a value rather than an absence. Either describe the real shape, or make the filter emit a literal `null` or an explicit sentinel. This file documents exact output shapes elsewhere, so the imprecision stands out.

#### P2 — 4. The two step 3 filters have no test

The new testcases pin `parse-reviews` output, which the resolver's own tests already covered in substance. What is new and untested is the selection-and-projection filter the SKILL tells the agent to run, which is exactly where finding 3 lives. A testcase piping a fixture through `parse-reviews` into that filter, with both a matching and a non-matching `review_id`, would have caught it and would pin the shape against future parser changes.

### Suggestions (non-blocking)

- `plugins/AGENTS.md` now reads "...must stay byte-identical, as must `resolve-copilot-threads` in ... Update both copies and their scrut coverage together." After a sentence naming two distinct pairs, "both copies" is ambiguous. "Update each pair together" reads cleaner.
- The Ready Criteria Copilot cell ends "...or only findings step 7b has already returned `Completed` or `No unresolved Copilot feedback` for", which is a long cell closing on a stranded preposition. The fourth rule below the table already carries the explanation, so the cell could say "or only findings already processed per step 7b" and let the rule do the work.
- No TODO, FIXME, stub, or commented-out content in the diff. Commit messages are Conventional, signed, and reference `(#461)`.
