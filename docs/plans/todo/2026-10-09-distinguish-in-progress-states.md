# Distinguish In-Progress States on Report Boards

Related issues: #551, #548

## Context

Both report boards collapse very different kinds of work into one "in progress" state.

- **Backlog triage.** `inProgress` is a single free-text string: a branch, `PR #390`, or a phrase such as `the in progress label`. The template draws any value as the same "In progress" tag (`templates/backlog-triage.html`, `progressTag`), and every in-progress issue holds its serial or head lane's slot. The gather step fetches open pull requests with only `number,title,headRefName,closingIssuesReferences`, so the board cannot tell a six-week-old pushed branch from an approved, green pull request. The model derives the value by reading, which is how #551's inferred and carried-over statuses reached the page.
- **Bugs.** `bugs-gather` collects `isDraft`, `reviewDecision`, and the check rollup, and Ready to go splits into `ship`, `review`, `in-progress`, and `ready-to-fix`. But `review` mixes waiting on a reviewer, changes requested, and failing checks, and `in-progress` mixes a draft fix with a bare label or pipeline.
- **Assignment.** The backlog triage board, following `suggest-next-issue`, treats assignment to the current user as in progress. The bugs board gathers assignees (`bugs-gather`, `assignees`) but does not use them for progress or rank. Assignment says who owns an issue, not that work has started (#548). In single-maintainer repositories, where one person is assigned to and claims every issue, the explicit signal carries no information.

The outcome: both boards share one progress model derived in code from gathered signals, render each stage distinctly with whose move it is and what to do next, flag stale and unhealthy work, and treat ownership as a separate, weak ranking factor called affinity.

## Decisions

- **Scope:** both boards and `suggest-next-issue`, one shared vocabulary. `suggest-next-issue` stops treating assignment as in progress, counts only the progress signals defined here, and weighs affinity the same way, which resolves #548. The focus board (#558, `feature/focus-board`) adopts it when it lands; it is out of scope here.
- **Progress stages**, ordered, each backed by a named gathered signal:

  | Stage             | Signal                                                                                                                             | Next move               |
  | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
  | `started`         | A progress label or progress pipeline, with no branch or pull request; with either, the branch or pull request decides the stage   | Author                  |
  | `branch`          | A local or remote branch, or a worktree, that names the issue and carries work, with no pull request                               | Author                  |
  | `draft`           | An open draft pull request that closes the issue or whose branch names it                                                          | Author                  |
  | `awaiting-review` | An open pull request whose required review is not given, or whose checks are still running                                         | Reviewer, CI, or nobody |
  | `needs-author`    | Changes requested, failing checks, or a merge conflict                                                                             | Author                  |
  | `ready-to-merge`  | Approved or no review required, checks passing, mergeable                                                                          | Author (merge)          |
  | `close-out`       | A merged pull request in the same repository closes the open issue, or only mentions it while a progress label or pipeline remains | Author (close or split) |

  When several carriers exist, the furthest stage wins and the others are listed as extra carriers.

- **Close-out data:** GitHub closes an issue when a pull request with a closing keyword merges into the default branch, so `close-out` mostly comes from merges into another branch and from pull requests that only mention the issue, as in #551. Both gather scripts read each open issue's closing references, which include manual links, and its timeline `CrossReferencedEvent` items, and keep the merged pull requests in the same repository. A closing reference, or a cross-reference with a closing keyword, is a `close-out` carrier; a mention counts only while a progress label or pipeline is still on the issue, because pull requests often name follow-up issues they leave open, which on this repository marked a third of the open issues before the rule required the label. Connect events are not read, since a manual link that was removed leaves the closing references.
- **Mergeability:** GitHub returns `mergeable: UNKNOWN` while it computes the result. `UNKNOWN` counts as no conflict, the stage comes from review and checks, and the signal text says mergeability was unknown, so a sync never waits on GitHub or reports a conflict it has not seen.

- **Next move** is `author`, `reviewer`, `ci`, or `nobody`. `nobody` means the stage waits on a reviewer and no review is requested from anyone, so the pull request cannot move until someone is asked. Inactivity is the `quiet` and `stale` flags' job, so the two never say the same thing.
- **Flags**, orthogonal to the stage:
  - `quiet` after 7 days and `stale` after 30 days with no commit, pull request update, review, merge, or, for a label or pipeline alone, issue update or pipeline move; both thresholds are configurable per board.
  - `behind` when the branch is behind the default branch, and `conflict` when GitHub reports it unmergeable.
  - `multiple` when more than one branch or open pull request carries an issue short of `close-out`, counting a pull request and its own head branch once.
  - `local` when a branch exists only on the machine that ran the gather. It names that host, so a sync from another machine explains a difference, and its next action is "push it". Local and pushed branches share one stage because they answer "how far along, and whose move" the same way; being unpushed is a condition of the branch, not a step of progress.
- **A merged pull request outranks a leftover label:** an open issue with a merged pull request that counts, as the `close-out` row says, is `close-out` even when a progress label is still present, and the label is noted as a cleanup.
- **Provenance (#551):** every stage names the signal that produced it, and is re-derived on each sync from that sync's gather. Previous board data never supplies a stage. Inferred statuses, such as a long-running routine, are recorded as blockers or left off.
- **Scheduling:** display plus flags. Every stage from `started` to `ready-to-merge` holds its lane slot as today; `quiet`, `stale`, and `ready-to-merge` are flagged in the lane so a held slot explains itself. `close-out` does not hold a slot.
- **Affinity** replaces assignment as a progress signal. It is a separate dimension saying how much an issue is already someone's:
  - Explicit: assigned, or claimed through a label in `claimLabels` or a ZenHub pipeline in `claimPipelines`. Both default to empty; pipelines apply only to the bugs board, which reads ZenHub. A claim is owned by the issue's assignees, and by an `unknown` owner when it has none. Claim settings are separate from `progressLabels` and `progressPipelines`, and a label or pipeline in both lists is a configuration error, so a progress label marks work started without also counting as ownership.
  - Implicit, for the current user, in three tiers, strongest first:
    1. Active work overlap: the paths of the issue's areas overlap files changed on the user's open branches or pull requests. No window, since an open branch is current by definition.
    2. Recent work in the area: the user committed to those paths, or merged pull requests touching them, within 30 days (`affinityWorkDays`). The point is an area the user is in now; a longer window would mark most areas in a repository the user works in heavily.
    3. Discussion: the user filed the issue at any time, or commented on it within 90 days (`affinityCommentDays`).
  - Uniformity, applied to each signal separately: when one owner holds a signal on at least 90% of open issues (`uniformityShare`), and the repository has at least five open issues (`uniformityMinimum`), that signal is ignored for the repository. Only open issues count, since closed ones say nothing about the current backlog. This drops assignment, claims, and "filed it" in single-maintainer repositories without a per-repository switch, keeps them in repositories with several people, where they vary, and leaves whichever signals still tell issues apart.
  - Effect: a small boost to picks and ranks for the current user, none for unowned issues, and a large penalty, never exclusion, for issues owned by someone else. Shown as context on every row: "affinity: you (bin changed in commit 1a2b3c4 within 30 days)", "affinity: @someone (assigned)".
  - Affinity is a weak factor because issue state is not reliable. It never holds a slot and never marks progress.
- **Bugs board groups** map to the shared stages: Ready to go groups become `ready-to-merge`, `needs-author`, `awaiting-review`, `draft`, `branch`, `started`, `close-out`, and `ready-to-fix`. Critical and High rows keep their tier, since urgency wins over readiness, and show the same stage tag and flags in place of the current one-line fix state.
- **Areas, tagged by the analysis and matched in code:** the user's side of tiers 1 and 2 (changed files, commits, merged pull requests) is gathered in code, but only reading an issue says what part of the code it concerns. So the analysis tags each open issue or bug with one or more areas, and a deterministic step matches paths afterward:
  - An area is `{ "name", "paths" }`, with `paths` as glob patterns relative to the repository root, such as `{ "name": "parser", "paths": ["src/parser/**"] }`. Board data carries the area list, and each issue or bug lists area names. An issue whose area cannot be told from reading it gets none, and gets no tier 1 or 2 affinity.
  - Backlog triage: the analysis writes areas in the same pass that reads issues for lanes, and `contention.claims` is derived from them, as the areas two or more issues share, rather than written separately. A `backlog-gather finish` step reads the gather and the analysis data and writes each issue's `progress` and `affinity`, the derived claims, and `schemaVersion`, so every tier names the commit, branch, or pull request behind it.
  - Bugs: each assessment carries its areas as `{ "name", "paths" }`, saved in the cache with it, so an unchanged bug is not read again. `bugs-gather score` refuses an area that two bugs give different paths, matches paths, and computes affinity alongside the rank.
- **Gathering:** a new deterministic `backlog-gather` script, modeled on `bugs-gather`, derives stages and flags in code, and gathers the user's side of affinity; tiers 1 and 2 are computed after the analysis tags areas. Both gather scripts read one shared file of jq definitions, `scripts/progress.jq`, for the branch-name rule, pull request stages, branch joining, merged links, the progress derivation, area matching, uniformity, and the owner order, so the two boards cannot drift apart; each script only turns what it gathered into the shapes those definitions take.
- **Page:** a header strip of per-stage counts, across every section, linking to the rows; stage-specific inline tags, keyed by the header stage strip; and a short next action on each in-progress row ("merge it", "answer review", "fix checks", "resolve conflict", "push it", "resume or drop", "close or split").
- **In flight view, per board:**
  - Backlog triage gets an In flight section above Start now, listing all active work grouped by stage. Lanes keep each in-progress issue in place with a compact stage tag, because lane order and capacity depend on it, so the issue appears in both.
  - Bugs gets no separate section. Ready to go, regrouped by stage, is that view. In-flight bugs in Critical or High stay in their tier with the stage tag and are counted in the header strip.
- **Boards published before the change:** `inProgress` and the old Ready to go groups are removed, not kept as legacy fields. Board data gains `schemaVersion: 2`, and data without it is version 1. `compare` reads an older previous board without validating it as the current version, compares everything outside the progress model as it does now (opened, closed, lanes, tiers, picks), and prints one line saying the progress model changed and stage changes start with the next sync, in place of a Started, No longer in progress, or regrouped entry for every issue. Mapping old values to stages was rejected: `PR #390` and the old `review` and `in-progress` groups each cover several stages, so a mapping would report moves that did not happen.
- **Version:** `publish-report-board` to `1.3.0`, a minor bump over `1.2.0`, the shared design system. A board published by an earlier version still extracts and compares, and the data each sync writes is produced fresh, so no stored input stops working. `suggest-next-issue` takes a minor bump too. Confirm both with the check-versions skill before the PR.
- **One progress model for `suggest-next-issue`:** a skill can read only files its own plugin ships (`docs/plugin-development.md`, Review checklists), so `suggest-next-issue` cannot link to `publish-report-board`'s reference. `references/progress-model.md` in `publish-report-board` is the source of truth, and `make build` copies it byte for byte into `suggest-next-issue`'s `references/`, as `bin/build-review-checklists` does for review checklists. The model file is written for both consumers: stages, flags, provenance, and affinity, with board scheduling left to the board-type references.

## Changes

### 1. Shared progress contract

- Define the `progress` object in `references/board-types/` prose and in `report-board` validation: `stage`, `carrier` (`{ "branch": ... }`, `{ "pr": N }`, `{ "label": ... }`, `{ "pipeline": ... }`), `signal` (provenance text), `since`, `lastActivity`, `nextMove`, `nextAction`, `flags`, and optional `host` (with the `local` flag) and `extraCarriers`.
- Define the `affinity` object: `owner` (`you`, a login, `unknown`, or null), `kind` (`explicit` or `implicit`), `tier` for implicit affinity, and `reasons`; and a top-level `affinityIgnored`, listing the signal kinds uniformity dropped for the repository.
- Add `schemaVersion: 2` to both board types' data.
- Add a shared reference, `references/progress-model.md`, owning the stage table, flags, thresholds, provenance rule, and affinity rules; both board-type references link to it, and the build copies it to `suggest-next-issue`.

### 2. `scripts/backlog-gather` (new)

- Gather open issues, open pull requests with `isDraft`, `reviewDecision`, `statusCheckRollup`, `mergeable`, `updatedAt`, and latest review times, remote and local branches with committer dates and ahead/behind counts against the default branch, worktrees, each open issue's timeline cross-references to merged pull requests, and the current user's recent commits and merged pull requests within a configurable window.
- Derive `progress` and the explicit and tier 3 affinity signals per issue; detect uniformity; gather the user's changed files on open branches and pull requests, and the paths of the user's commits and merged pull requests within `affinityWorkDays`; write one normalized file the analysis reads.
- Add a `finish` subcommand that reads the gather and the analysis data, matches area paths against the gathered files, and writes the final `progress` and `affinity` per issue, the derived claims, and `schemaVersion`, refusing an area with no paths, an issue naming an undefined area, a derived field the analysis wrote itself, or an issue set that differs from the gather. The gather stops rather than shrink the board when the open issues, open pull requests, or merged search come back incomplete, and warns, then goes on, when GitHub cuts one issue's labels, assignees, linked pull requests, cross-references, or comments short, as `bugs-gather` does.
- Config keys: `progressLabels`, `claimLabels`, `quietDays`, `staleDays`, `affinityWorkDays`, `affinityCommentDays`, `uniformityShare`, `uniformityMinimum`.

### 3. `scripts/bugs-gather`

- Replace `progress_of` and `ready_group` with the shared stage derivation; add `mergeable`, review requests, timeline cross-references to merged pull requests, branch, and activity data; add the flags; add `claimLabels` and `claimPipelines` to the config keys; gather the user's changed and recently committed paths.
- Assessments gain an `areas` list of `{ "name", "paths" }`, cached with them. `score` refuses an area that two bugs give different paths, matches paths, and computes affinity.
- Map rank weights: an `affinity` weight group with small positive and large negative values, documented with the existing weights.

### 4. `scripts/report-board`

- Validate `progress` and `affinity` on both board types, replacing the `inProgress` text check and the `ready_groups` list.
- Update capacity and pick checks: `close-out` does not hold a slot; a pick owned by someone else needs a `despiteOwner` reason.
- `compare`: report stage moves ("draft to awaiting review"), flags raised and cleared, and affinity changes, replacing the current Started, Progress moved, and No longer in progress entries. When the previous board has no `schemaVersion`, skip the progress entries and print the one-line model-change notice instead.
- Validate that no label or pipeline is in both a progress list and a claim list.

### 5. Templates

- `backlog-triage.html` and `bugs.html`: stage tags with distinct form and color in both themes, the header stage strip that keys them, next-action text, flag markers, and affinity context.
- `backlog-triage.html` only: the In flight section above Start now. `bugs.html` regroups Ready to go by stage instead. Keep the existing shared look in `design-conventions.md`, extending its palette with stage colors that stay distinguishable in grayscale.
- The lane model reads `progress.stage` instead of `inProgress` truthiness. The templates have no execution coverage (#403), so the lane and capacity changes rest on the manual checks under Verification; #403 stays the follow-up for automated coverage.

### 6. References and skill prose

- `board-types/backlog-triage.md`: replace Analyze step 1 with a pointer to `backlog-gather` and `progress-model.md`; remove assignment as a progress signal; add area tagging, derive the contention claims from areas, run `backlog-gather finish` after the analysis, and describe affinity in picks.
- `board-types/bugs.md`: new Ready to go groups, flags, the `areas` field in the assessment shape the subagents return, and the affinity weight.
- `design-conventions.md`: stage colors, and the In flight section on the backlog board.
- `SKILL.md` and the plugin README: mention the gather script and the new sections.

### 7. `plugins/suggest-next-issue/skills/suggest-next-issue/SKILL.md`

- Replace step 2's signal list with a pointer to its own `./references/progress-model.md`, the build's copy, and summarize the signals there: a branch or worktree naming the issue and carrying work, a progress label, an open pull request that closes it or whose branch names it, or a merged pull request that closes an open issue, or mentions it while a progress label remains (`close-out`). Drop assignment as a signal. Update `board-types/backlog-triage.md`, which today tells the board to detect progress the way `suggest-next-issue` does, to point at the model instead.
- Add affinity as a ranking signal with the same weights in prose: a small boost for the current user, a large penalty for someone else, and the uniformity rule.
- List in-progress issues with their stage and next move, and `close-out` issues separately as cleanups.
- Bump `suggest-next-issue` as a minor change, since it changes what the skill recommends.

### 8. Build and validation tooling

- Add `bin/build-shared-references`, run by `make build`, which copies `plugins/publish-report-board/skills/publish-report-board/references/progress-model.md` to `plugins/suggest-next-issue/skills/suggest-next-issue/references/progress-model.md`.
- Add rule 22 to `bin/validate-plugins`: fail when the copy is missing or differs from its source.
- Add the copy to the root `CLAUDE.md`'s never-hand-edit list, the `## Code Review Rules` paths not to review, and `bin/AGENTS.md` and `docs/plugin-development.md` beside the review-checklist copies.
- Run `make build` and commit the regenerated `dist/codex/` and `dist/opencode/` mirrors for both plugins, and `.agents/plugins/marketplace.json` if the build changes it.

### 9. Tests

- New `tests/scrut/backlog-gather.md` with fixture stubs for each stage, each flag including `local`, uniformity per signal and below `uniformityMinimum`, each implicit affinity tier, an issue with no areas, `finish` refusing an undefined area, `close-out` from a referencing pull request merged into a non-default branch, `mergeable: UNKNOWN`, `nobody` with no review requested, and a progress label beside a pull request.
- Extend `bugs-gather.md`, `report-board.md`, and `report-board-bugs.md` for the new fields, assessments with areas, claims derived from areas, the regrouped Ready to go, a label in both progress and claim lists refused, `compare` output, and `compare` against a version 1 previous board printing only the model-change notice for progress.
- New `tests/scrut/progress-model.md` covering `scripts/progress.jq` case by case, including the cases where signals compete.
- Extend `tests/scrut/` coverage of `bin/validate-plugins` for rule 22: a missing copy and a stale copy each fail.

## Verification

- `make build` leaves no diff, and `make test-all` passes, including the new and extended scrut suites.
- Publish sample boards for this repository and one repository with several people, and confirm each stage, flag, and affinity value renders in both themes and at 390 pixels.
- Run `compare` across two syncs where a pull request moves from draft to review, and confirm the report names the move.
- Re-sync a board published by `1.1.1` and confirm the change report carries the model-change notice and no per-issue progress entries.
