# Branch Review: feature/350-create-deferred-issues-skill

Base: `main` (merge base: `340f3192`)
Commits: 5
Files changed: 21 (12 added, 9 modified, 0 deleted, 0 renamed)
Reviewed through: `5234d825`

Resolution status: R1, R2, and R3 addressed. See [Review resolution](#review-resolution) for the changes and scenario checks. The assessment below records the reviewed commit; it is not a reassessment of the corrected tree.

## Summary

This branch adds a skill that collects deferred concerns from the session, branch markers, PR discussions, and planning documents, then proposes and files an approved batch. It also updates `pr` to list newly filed follow-ups without closing them on merge. The plugin is registered and mirrored for Codex and OpenCode, but repository routing and revalidation after proposal edits need corrections before merging.

## Code Quality Assessment

**Verdict: needs changes.** The instructions are readable, well factored into references, and consistent with the repository's plugin conventions. Three P2 correctness issues affect the advertised multi-repository workflow.

### R1: Preserve the source repository when resolving issues and timelines

**P2.** `plugins/create-deferred-issues/skills/create-deferred-issues/SKILL.md:137-140` and `:212-215`.

The workflow explicitly allows discovering a PR in the fork's parent, but then confirms its closing issue numbers with `gh issue view <n> --repo <target>`, where the default target is origin. The timeline command likewise uses `<target>` for both source issues and the PR. For a PR in `upstream/project` closing its issue 42, with `me/project` as origin, these commands read `me/project#42` or fail instead of reading the source issue. That loses source deferrals and duplicate evidence, and a same-numbered issue in the fork can become an unrelated source.

Keep each source's repository and number together, preferably preserving its returned URL. Resolve closing references against their own repositories and query the PR timeline against `<pr-repo>`. Keep the filing target separate. Validate with a parent PR whose issue numbers differ in meaning from the fork's numbers.

### R2: Resolve candidate targets before searching for duplicates

**P2.** `plugins/create-deferred-issues/skills/create-deferred-issues/SKILL.md:221-229`.

Step 3 says to apply its rules in order, but its tracker search uses `<target>` before the next rule resolves each candidate's target. A concern explicitly assigned to another repository therefore reaches duplicate search with only the default target established. An existing issue in the destination can be missed, or a similarly titled issue in origin can incorrectly suppress the candidate. The no-origin path has the same ordering problem because the search has no resolved target at all.

Resolve candidate targets before target-dependent duplicate searches. Search each candidate's destination, retain source repositories separately for timeline reads, and mark unresolved targets as not checked until the user supplies one. Validate with a concern already tracked only in a second repository.

### R3: Repeat target-dependent checks after proposal edits

**P2.** `plugins/create-deferred-issues/skills/create-deferred-issues/SKILL.md:285-292`.

The proposal accepts target edits, including resolving an initially unresolved target, and explicitly says to file immediately when an edit also approves. It never routes the edited item back through repository metadata checks, duplicate search, label selection, or visibility assessment. For example, changing an item's destination from one owned repository to another and approving it can create a duplicate in the new destination or attempt a write to an archived repository, using checks made only for the old destination.

After an edit changes the destination or substantive concern, repeat the affected checks before filing and recompute third-party classification. Preserve item numbers; re-present the item if the checks materially change what was approved. Validate both edit-only and edit-plus-approval replies, including unresolved and archived targets.

### Strengths and limitations

- The proposal gate, fixed item numbers, sequential filing, partial-failure reporting, and retry lookup are explicit.
- Deferral examples distinguish pending work from rejected alternatives, resolved concerns, and marker illustrations.
- Follow-up exclusion is applied after all three PR issue-detection strategies, with qualified references supported in the PR body.
- No new executable helpers, dependencies, CI settings, or incomplete code stubs are introduced. The existing suite validates packaging and tooling; it does not execute the new conversational workflow.
- A useful nonblocking addition is a recorded scenario matrix covering cross-repository sources, retargeting, partial creation failures, and same-session PR composition.

## Changes by Area

- **Deferred-issue collection and filing:** five files under `plugins/create-deferred-issues/` define the manifest, README, skill, signal guide, and filing guide.
- **PR composition:** three files under `plugins/pr/` add follow-up exclusion and reporting and bump the version to `1.9.0`.
- **Catalog and distribution:** both marketplace files, the root README, eight Codex mirror files, and the OpenCode skill symlink register and distribute the feature.
- **Planning:** the dated plan records the workflow, safety constraints, integration, verification, and commit sequence.

## File Inventory

### Added: 12 files

- `plugins/create-deferred-issues/.claude-plugin/plugin.json`
- `plugins/create-deferred-issues/README.md`
- `plugins/create-deferred-issues/skills/create-deferred-issues/SKILL.md`
- `plugins/create-deferred-issues/skills/create-deferred-issues/references/batch-filing.md`
- `plugins/create-deferred-issues/skills/create-deferred-issues/references/deferral-signals.md`
- `dist/codex/plugins/create-deferred-issues/.claude-plugin/plugin.json`
- `dist/codex/plugins/create-deferred-issues/README.md`
- `dist/codex/plugins/create-deferred-issues/skills/create-deferred-issues/SKILL.md`
- `dist/codex/plugins/create-deferred-issues/skills/create-deferred-issues/references/batch-filing.md`
- `dist/codex/plugins/create-deferred-issues/skills/create-deferred-issues/references/deferral-signals.md`
- `dist/opencode/skills/create-deferred-issues` (symlink)
- `docs/plans/todo/2026-09-14-new-skill-create-deferred-issues.md`

### Modified: 9 files

- `.agents/plugins/marketplace.json`
- `.claude-plugin/marketplace.json`
- `README.md`
- `plugins/pr/.claude-plugin/plugin.json`
- `plugins/pr/README.md`
- `plugins/pr/skills/pr/SKILL.md`
- `dist/codex/plugins/pr/.claude-plugin/plugin.json`
- `dist/codex/plugins/pr/README.md`
- `dist/codex/plugins/pr/skills/pr/SKILL.md`

## Notable Changes

- GitHub writes are newly orchestrated through an approved batch. Repository identity, public/private source handling, and retry behavior are therefore functional requirements of the prompt.
- Version checks are clean: `create-deferred-issues` starts at `1.0.0`; `pr` advances from `1.8.5` to `1.9.0`, appropriate for the new capability.
- Catalog state changes from `catalog-M70-m107-p165-n57` to `catalog-M71-m108-p160-n58` after merging `main`. The computed value matches; plugin validation confirms catalog agreement and generated-tree freshness. The lower patch sum is expected when `pr` advances to a minor version with patch zero.

## Plan Compliance

Plan: `docs/plans/todo/2026-09-14-new-skill-create-deferred-issues.md`.

**Verdict: partial compliance.** All planned feature surfaces exist, but the repository-aware workflow has gaps and the planned full behavioral walkthrough is not established. Counting the plan's work in the 16 groups below, **12/16 are done (75%); 4 are partially done; none are wholly unstarted**. Subrequirements are included in their owning group.

### Plugin and workflow

1. **Done: manifest and activation.** Version, keywords, description surfaces, trigger phrases, and authenticated `gh` requirement are present.
1. **Done: options and continuation.** Both options, parent output fields, failure status, mandatory proposal gate, and user-directed continuation are specified.
1. **Partially done: context discovery.** Origin resolution, host handling, branch/base detection, PR lookup, source discovery, and label lookup exist. Source issue identity is lost for parent PRs (R1).
1. **Done: collection.** Session context, committed and uncommitted markers, untracked files, PR discussion, and changed plan/review documents are covered with the planned exclusions.
1. **Partially done: filtering and repository checks.** Deferral filtering, timeline matching, tracker search, target eligibility, and visibility rules exist. Target resolution follows duplicate search (R2), and source timeline routing is incorrect (R1).
1. **Partially done: proposal and edits.** Batch content, fixed numbering, drop/edit replies, dry-run, and third-party approval are present. Edited destinations do not repeat dependent checks (R3).
1. **Done: sequential filing and error handling.** Tmpfile mechanics, existing-label rules, body verification/recovery, retry checks, and partial-failure reporting follow the plan.
1. **Done: cross-reference and report.** Source body references, one summary comment, comment suppression, and parent/user reports are specified. Correct source identity depends on R1.
1. **Done: deferral reference.** Definitions, signal phrases, source shapes, exclusions, worked examples, and target signals are documented.
1. **Done: plugin README.** Installation, canonical description, behavior, options, requirements, permission block, examples, and related plugins are present.

### Integration and delivery

1. **Done: PR integration.** Detection exclusion, Follow-ups placement, commit-reference restriction, final report, README, and minor bump match the plan.
1. **Done: catalog and mirrors.** Alphabetical registration, category, root README row, tool requirement, catalog state, and generated distributions are present and validated.
1. **Done: cross-reference and writing constraints.** Plugin validation and lint pass. No missing referenced plugin was introduced.
1. **Done: commit organization.** The four planned commits occur in order, followed by a focused duplicate-matching fix.
1. **Done: plan artifact.** The dated plan is committed in the repository's conventional location. Remaining in `todo/` is appropriate while corrections remain.
1. **Partially done: verification.** See the checks below. The read-only current-branch probes do not establish the complete interactive dry-run or the fork/retargeting scenarios.

### Deviations and fidelity

The additional timeline-matching fix is justified: cross-references are only candidate evidence, not proof that all concerns are tracked. Discovering the PR before choosing its base is also reasonable and preserves the plan's intended branch scope. There are no unjustified feature additions or identified ordering violations in the commit sequence. R1 through R3 undermine the plan's repository-aware filing intent, including places where the plan itself specifies the same problematic ordering; faithfully copying that ordering does not establish correctness.

## Verification

- `make test-all`: lint and plugin validation passed. Scrut completed with 387/402 cases passing and 15 failing, all in `tests/scrut/launch-workmux.md`; Make exited 2. The suite is not green.
- The unchanged Git stub calls `/usr/bin/git` for branch-name validation. Directly running `/usr/bin/git check-ref-format --branch feature/42-new-work` reports an unaccepted Xcode license; the Git on PATH accepts the same name. This explains the branch-name validation failures. Other failures concern prompt-file and prompt-resend expectations; their causes were not established. The affected launcher scripts, fixture, and suite have no branch diff. No baseline rerun was performed, so the failures are not claimed to be proven baseline failures. Full output is in `/tmp/350-review-checks.log`.
- `git diff --check main...HEAD`: passed.
- `bin/compute-catalog-state`: returned the stored catalog value.
- Read-only GitHub probes: no open PR for this branch; source issue 350 and its timeline loaded successfully; labels loaded successfully. The timeline contains related proposals, confirming the need for concern-specific matching.
- Local marker scan and plan inventory inspected: changed marker text illustrates the skill's syntax rather than adding executable TODOs. The session available to this review contains no prior implementation conversation, so earlier deferrals cannot be reconstructed.
- No GitHub issue creation, comment posting, or interactive approval flow was executed. These findings are based on the committed prompt paths and concrete routing scenarios, not a claim of observing unintended GitHub writes.

At the initial review, this file was saved locally, formatted, linted, and left uncommitted; product files were not modified by the reviewer. An uncommitted title-quoting edit to `plugins/create-deferred-issues/skills/create-deferred-issues/references/batch-filing.md` appeared during that review and was left untouched; it is outside the reviewed committed diff. Validation ran in the shared working tree, not an isolated checkout of HEAD.

## Review resolution

The fixes preserve the separately committed title-quoting changes in `5cd9723a` and `0c77e190`.

- [x] **R1: source identity.** PRs and closing issues retain their full URLs, hosts, repositories, and numbers. Source issue reads and timeline reads use those identities; body references preserve them across destination edits. Bare references are interpreted in their source repository, and duplicate comparisons use repository plus number.
- [x] **R2: destination before search.** Target resolution and eligibility checks precede tracker searches. Searches and label lookup use each candidate's destination. Unresolved targets skip these calls and carry an explicit unchecked status until the user supplies a destination.
- [x] **R3: edited-item checks.** Destination or substantive concern edits repeat eligibility, third-party classification, labels, duplicate matching, and visibility checks. Only approval of the current checked proposal permits filing; material changes from checks require presenting the revision again, and item numbers stay fixed.
- [x] **Suggestion: scenario matrix.** The instruction-path walkthrough below covers routing, edits, failure handling, and PR composition.

### Scenario walkthrough

These are inspections of the revised prompt's prescribed behavior using sample inputs. They are not automated agent executions or live GitHub write tests. Source and destination names below are illustrative.

| Scenario                              | Sample input                                                                                                    | Result from following the revised instructions                                                                                                                            |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Parent PR source                      | Origin is `me/project`; PR `other/project#80` closes `other/project#42`; `me/project#42` is unrelated           | Read issue 42 in `other/project`; read PR timeline 80 and issue timeline 42 there; retain origin as the default filing destination; no comment on the parent              |
| Closing issue in a third repository   | The source PR closes `other/library#42` by full URL                                                             | Derive the issue's repository from that URL; read its body and timeline in `other/library`                                                                                |
| Destination-specific duplicate        | A concern targets `me/tools`; its existing issue is only in `me/tools`, not origin                              | Resolve `me/tools`, search there, and classify the matching concern as Already tracked                                                                                    |
| No origin                             | Session-only concern has no destination                                                                         | Skip destination metadata, labels, and search; propose as unresolved and unchecked; do not file                                                                           |
| Edit-only reply                       | `edit 2: use me/tools`                                                                                          | Recheck destination and concern, retain number 2, and present the revision for approval                                                                                   |
| Edit with approval, unchanged checks  | `edit 2: use me/tools; file 2`; destination is eligible, no duplicate, labels and disclosure remain appropriate | Complete all affected checks and file item 2 under that approval                                                                                                          |
| Edit to archived destination          | `edit 2: use me/archive; file 2`; metadata says archived                                                        | Move item 2 to Cannot file; do not attempt creation                                                                                                                       |
| Edit reveals a duplicate              | `edit 2: use me/tools; file 2`; destination search matches the concern                                          | Report item 2 as Already tracked; do not create another issue                                                                                                             |
| Resolving a target reveals new labels | Unresolved item 2 has no labels; the user supplies a target and approves; checking selects a type label         | Re-present the revised labeled item before filing because the check changed the approved proposal                                                                         |
| Private source to public destination  | Retargeting requires removing source links and paths from the body                                              | Recheck visibility, present the revised disclosure, and obtain approval for the changed proposal                                                                          |
| Third-party retargeting               | `edit 2: use other/tools; file all`                                                                             | Reclassify as third-party; whole-batch approval does not authorize filing item 2                                                                                          |
| Partial creation failure              | Items 1 and 3 succeed; item 2 fails                                                                             | Continue in order, report failure and successful URLs, and check newest destination issues before retrying item 2                                                         |
| Same-session PR                       | Newly filed `me/project#101` and `me/tools#7` are follow-ups; the branch addresses `me/project#350`             | The `pr` skill excludes follow-ups from closing candidates and lists them as `#101` and `me/tools#7` under Follow-ups; only the source issue remains eligible for closing |

All listed instruction paths reached the stated result on inspection. The full-suite failure recorded above remains a validation limitation; conversational checks do not substitute for a successful Scrut run.

### Resolution validation

- `make build`: passed; Codex and OpenCode mirrors regenerated.
- `make lint`: passed, including Markdown, Prettier, ShellCheck, shfmt, and actionlint. Markdown auto-fix and Prettier write ran on the changed source and review files before verification.
- `make validate`: passed, including JSON, plugin metadata, cross-references, and generated-tree freshness.
- The skill-creator validator, run through `uv` with PyYAML and a writable temporary cache: passed.
- `git diff --check` and staged whitespace check: passed.
- Version check: `create-deferred-issues` is new at `1.0.0`; `pr` advances from `1.8.5` to `1.9.0`; catalog state recomputes from `catalog-M70-m107-p165-n57` to `catalog-M71-m108-p160-n58`. No additional version bump is needed for corrections to the new plugin before its first release.
- Scrut was not rerun for these prompt-only fixes. Its earlier completed result remains 387 passing and 15 failing cases, with the limitations described in the original verification section. Neither launcher code nor its tests were changed.
- No live GitHub writes were made to test the workflow. The 13 recorded scenarios are instruction-path inspections.

### Resolution commits

- `b5f19835`: signed fix commit resolving R1, R2, and R3, including source documentation and Codex mirrors.
- This review document is committed separately with the resolution status, scenario matrix, and validation evidence, resolving the nonblocking documentation suggestion.

All four extracted review items are resolved; none were skipped. This records the fixes and their checks, not a claim that the outstanding full-suite failures have been repaired.
