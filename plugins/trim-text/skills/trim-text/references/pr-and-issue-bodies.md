# Profile: PR and issue bodies

Applies to pull request descriptions and issue bodies, whether published or drafted by another skill.

## What leads

**For a PR, the change this PR makes, as the net diff shows it.** Not the commits in order, not how the work went, and not the files touched. **For an issue, the problem or the request**, in terms of what someone sees.

Lead with one or two sentences a reviewer could stop after. Then the details a reviewer needs, grouped by change rather than by file or by the order the work happened. Each thing is said once.

## Don't over-trim

Lean means no padding, not no reasoning. Keep what makes the change reviewable:

- why the obvious fix was wrong
- what is deliberately unchanged
- a behavior change, a risk, or a deploy step
- known limits
- verification a reviewer cannot see for themselves, such as a rehearsal against staging
- a test step someone still has to run, as an unchecked item, so the gap stays visible

## Cut these, in addition to the shared list

| Cut                                                                | Instead                                                                          |
| ------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| A description of the commits or the branch history                 | The net change. A commit that reverted an earlier one leaves nothing to describe |
| Restating the title, the diff, or what CI reports                  | Delete it. "Renames the test file" is visible in the diff                        |
| A file-by-file inventory                                           | A few bullets grouped by change                                                  |
| The investigation story: "How this surfaced", "found by…"          | The finding, stated once                                                         |
| Out-of-scope findings written up as prose                          | Links to filed issues, under the section the repository uses for follow-ups      |
| The author's doubts, notes on what was left alone, reviewer to-dos | Delete; these belong in the hand-off message to the person who asked             |
| Session leakage: "the user", "has been asked", "as discussed"      | The fact, without the conversation around it                                     |
| A restatement of a committed plan, or an audit against it          | A link to the plan as the source of truth                                        |
| Test-plan boilerplate: checked lint, type check, suite counts      | Delete; CI reports these. Keep unchecked steps and evidence CI cannot show       |
| Noise about unrelated tests or flaky runs                          | Delete, or a link to the issue that tracks the flake                             |
| Template sections answered "No" with a justification               | Remove the section where the template allows it                                  |
| Comments about the description's own revisions                     | Delete                                                                           |
| Citation chains: "reference [39] cited therein, which is…"         | The citation that matters                                                        |
| Counts that change with every commit: test counts, file counts     | A description: "adds scrut coverage for the bundled script"                      |

Under a parent continuation, keep every unchecked checklist item, including a reviewer to-do, and flag it instead of deleting it: the calling skill rejects a body that loses one.

Bold used for emphasis or as bullet lead-ins goes too, unless the repository's own template uses it.

## Stays true

A body is written once, but merges and review fixes keep changing what it should say. Check every claim against the current diff, not the draft's memory of it: a removed input still listed, a release target that moved, or a behavior a later commit reverted. A claim the diff no longer supports is a rewrite or a delete, even when it is short; under a parent continuation, flag it with the correction instead (see "Preserve meaning" in the skill).

## Preserve

- Section headings the repository's template or the calling skill requires, including `## Summary`, `## Test plan`, `## Closes`, `## Related issues`, and `## Follow-ups`
- Closing keywords, issue and PR references, and their exact targets
- Checklist state: never check or uncheck an item
- Trailers, session lines, and anything the repository's instructions require in a body
- Mentions, links, images, and code blocks

## Verify

Compare the final body with the original under "Preserve meaning", and confirm every issue reference and closing keyword is unchanged. For a published body, read it back after the write and confirm it matches the body written, as step 4 of the skill describes.

## Worked examples

From real PR and issue edits. `…` marks a truncated original, and each Before quotes the text as written at the time. Rows marked _anonymized_ come from client work, with names, products, and numbers replaced; the writing failure is unchanged.

| Failure                                          | Before                                                                                                                                                                                              | After                                                                                                                                                                         |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Describes the commits, not the net diff          | `Restore ToC format to match CLAUDE.md conventions (\| separators, _italic_ subcategory labels, no trailing colons)`, when a later commit had reverted the change it restored                       | deleted: with the change reverted, the commit left nothing to describe                                                                                                        |
| Counts that drift                                | `adds 58 scrut cases`; `lint, validation, and 138 scrut cases, 58 of them for report-board`                                                                                                         | `adds scrut coverage for the bundled script`; `lint, validation, and the full scrut suite`                                                                                    |
| Stale claim                                      | `Intended as a **minor** release (v3.3.0).`                                                                                                                                                         | `Targets v4.0.0.`                                                                                                                                                             |
| Unrelated test noise                             | `The first full test run passed 401 of 402 Scrut cases. … returned empty output. An isolated rerun passed … unchanged by this PR…`                                                                  | deleted                                                                                                                                                                       |
| Session leakage                                  | `The user corrected the initial absence report: they had searched the effects menu.`                                                                                                                | `The initial absence report came from an effects-menu search.`                                                                                                                |
| Duplicates the plan                              | A ten-step `## Workflow` and a `### Lenses` table restating the plan                                                                                                                                | `The implementation plan is the source of truth for the workflow, the lenses, … This issue carries the case for the work, the settled decisions, and the definition of done.` |
| Citation chain                                   | `(Theorem 2 of [@zhangyeung1998], originally proved in reference [39] cited therein, which is [@zhangyeung1997])`                                                                                   | `(Theorem 2 of [@zhangyeung1998], originally proved in [@zhangyeung1997])`                                                                                                    |
| Investigation story, _anonymized_                | `## How this surfaced … After re-running it green, the deploy step reported SUCCESS … That is what led here.`                                                                                       | `There was a bug in the deploy script that prevented new revisions from getting automatically promoted on staging. Now there isn't.`                                          |
| Justifying the finding, _anonymized_             | `found by rehearsing the runbook against staging rather than by reading the code. Every defect here made the tooling look like it was working.`                                                     | `Rehearsing the fix on staging revealed some needed changes.`                                                                                                                 |
| File-by-file inventory, _anonymized_             | A 19-row `\| File \| What \|` table, such as `scripts/setup-test-db.sh \| Changed: loads the new … CI fixture`                                                                                      | Six bullets grouped by change, such as `Tests: database-backed handler tests, mapper tests, and payload fixtures`                                                             |
| Test-plan boilerplate, _anonymized_              | `[x] npm run lint -- --max-warnings 0 passes. [x] Unit suite passes (496 tests)… [x] Planted defects…`                                                                                              | the lint and unit-suite items deleted, since CI reports them; `[x] Planted defects…` kept, as evidence CI cannot show                                                         |
| Author's doubt and reviewer to-dos, _anonymized_ | `## Note … I left the table alone, since I don't know whether that policy is finished…`; `[ ] Reviewer: confirm the new required flag is acceptable friction`                                       | deleted; raised in the hand-off message instead                                                                                                                               |
| Parked findings, _anonymized_                    | `## Out of scope, noted for follow-up: BUILD_ID is not exported into the deploy step's container… the promote script is hardcoded to one service…`                                                  | deleted from the body; listed in the hand-off message to be filed as issues                                                                                                   |
| Buried lead, arguing a decision, _anonymized_    | `Staff asked to remove the word … The first instance was fixed in an earlier PR. This is the second instance…`; `Added a comment saying so, to keep the branch from being "simplified" away later.` | `The dashboard buttons name the wrong campaign type for the active campaign.`; the second sentence deleted                                                                    |

The "stale claim" row is a rewrite rather than a cut: the short version was wrong, and staying true outranks staying short.
