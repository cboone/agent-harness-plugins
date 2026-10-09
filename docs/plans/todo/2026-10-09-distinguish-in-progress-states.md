# Distinguish In-Progress States on Report Boards

Related issues: #551, #548

## Context

Both report boards collapse very different kinds of work into one "in progress" state.

- **Backlog triage.** `inProgress` is a single free-text string: a branch, `PR #390`, or a phrase such as `the in progress label`. The template draws any value as the same "In progress" tag (`templates/backlog-triage.html`, `progressTag`), and every in-progress issue holds its serial or head lane's slot. The gather step fetches open pull requests with only `number,title,headRefName,closingIssuesReferences`, so the board cannot tell a six-week-old pushed branch from an approved, green pull request. The model derives the value by reading, which is how #551's inferred and carried-over statuses reached the page.
- **Bugs.** `bugs-gather` collects `isDraft`, `reviewDecision`, and the check rollup, and Ready to go splits into `ship`, `review`, `in-progress`, and `ready-to-fix`. But `review` mixes waiting on a reviewer, changes requested, and failing checks, and `in-progress` mixes a draft fix with a bare label or pipeline.
- **Assignment.** Both boards, following `suggest-next-issue`, treat assignment to the current user as in progress. Assignment says who owns an issue, not that work has started (#548). In the user's non-client repositories the user is assigned to and claims everything, so the explicit signal carries no information there.

The outcome: both boards share one progress model derived in code from gathered signals, render each stage distinctly with whose move it is and what to do next, flag stale and unhealthy work, and treat ownership as a separate, weak ranking factor called affinity.

## Decisions

- **Scope:** both boards, one shared vocabulary. The focus board (#558, `feature/focus-board`) adopts it when it lands; it is out of scope here.
- **Progress stages**, ordered, each backed by a named gathered signal:

  | Stage             | Signal                                                                              | Next move               |
  | ----------------- | ----------------------------------------------------------------------------------- | ----------------------- |
  | `started`         | A progress label or progress pipeline, with no branch or pull request               | Author                  |
  | `local-branch`    | A local branch or worktree naming the issue, not pushed                             | Author                  |
  | `pushed-branch`   | A remote branch naming the issue, no pull request                                   | Author                  |
  | `draft`           | An open draft pull request that closes the issue                                    | Author                  |
  | `awaiting-review` | An open pull request with review required and none given, checks passing or pending | Reviewer or CI          |
  | `needs-author`    | Changes requested, failing checks, or a merge conflict                              | Author                  |
  | `ready-to-merge`  | Approved or no review required, checks passing, mergeable                           | Author (merge)          |
  | `close-out`       | A pull request that closes the issue has merged, and the issue is open              | Author (close or split) |

  When several carriers exist, the furthest stage wins and the others are listed as extra carriers.

- **Next move** is `author`, `reviewer`, `ci`, or `nobody`. `nobody` is set when the stage's next move has seen no activity past the quiet threshold, so stuck work stands out.
- **Flags**, orthogonal to the stage:
  - `quiet` after 7 days and `stale` after 30 days with no commit, push, pull request update, or review event; both thresholds are configurable per board.
  - `behind` when the branch is behind the default branch, and `conflict` when GitHub reports it unmergeable.
  - `multiple` when an issue has more than one branch or pull request.
  - Local-only work carries the host that saw it, so a sync from another machine explains a difference.
- **Provenance (#551):** every stage names the signal that produced it, and is re-derived on each sync from that sync's gather. Previous board data never supplies a stage. Inferred statuses, such as a long-running routine, are recorded as blockers or left off.
- **Scheduling:** display plus flags. Every stage from `started` to `ready-to-merge` holds its lane slot as today; `quiet`, `stale`, and `ready-to-merge` are flagged in the lane so a held slot explains itself. `close-out` does not hold a slot.
- **Affinity** replaces assignment as a progress signal. It is a separate dimension saying how much an issue is already someone's:
  - Explicit: assigned, or claimed through a label or pipeline.
  - Implicit, for the current user: the issue's component overlaps components touched by the user's in-progress branches or pull requests; the user committed to those files or components recently; the user merged pull requests touching that area recently; or the user filed or commented on the issue.
  - Uniformity: when nearly every open issue shares the same explicit owner, the explicit signal is ignored for that repository and implicit affinity decides. This covers the user's non-client repositories without a per-repository switch, and keeps the signal in `swing-left` repositories, where assignment varies.
  - Effect: a small boost to picks and ranks for the current user, none for unowned issues, and a large penalty, never exclusion, for issues owned by someone else. Shown as context on every row: "affinity: you (recent commits in `bin/`)", "affinity: @someone (assigned)".
  - Affinity is a weak factor because issue state is not reliable. It never holds a slot and never marks progress.
- **Bugs board groups** map to the shared stages: Ready to go groups become `ready-to-merge`, `needs-author`, `awaiting-review`, `draft`, `pushed-branch`, `local-branch`, `started`, and `ready-to-fix`. Critical and High rows show the same stage tag and flags in place of the current one-line fix state.
- **Gathering:** a new deterministic `backlog-gather` script, modeled on `bugs-gather`, derives stages, flags, and affinity in code. Shared jq definitions for stages and flags are copied between the two gather scripts with comments naming each other, matching the template convention, until a shared layer is justified.
- **Page:** a header strip of per-stage counts linking to the rows; an In flight section grouping active work by stage, above Start now on the backlog board and above the tiers on the bugs board; stage-specific inline tags with a legend; and a short next action on each in-progress row ("merge it", "answer review", "fix checks", "resolve conflict", "resume or drop", "close or split").
- **Version:** new capability and a changed data contract, so a minor bump of `publish-report-board` to `1.2.0`, confirmed with the check-versions skill before the PR. If the `inProgress` string is removed rather than kept as an accepted legacy field, revisit whether that is a major change.

## Changes

### 1. Shared progress contract

- Define the `progress` object in `references/board-types/` prose and in `report-board` validation: `stage`, `carrier` (`{ "branch": ... }`, `{ "pr": N }`, `{ "label": ... }`, `{ "pipeline": ... }`), `signal` (provenance text), `since`, `lastActivity`, `nextMove`, `nextAction`, `flags`, and optional `host` and `extraCarriers`.
- Define the `affinity` object: `owner` (`you`, a login, or null), `kind` (`explicit` or `implicit`), `reasons`, and `ignoredExplicit` when uniformity applied.
- Add a shared reference, `references/progress-model.md`, owning the stage table, flags, thresholds, provenance rule, and affinity rules; both board-type references link to it.

### 2. `scripts/backlog-gather` (new)

- Gather open issues, open pull requests with `isDraft`, `reviewDecision`, `statusCheckRollup`, `mergeable`, `updatedAt`, and latest review times, remote and local branches with committer dates and ahead/behind counts against the default branch, worktrees, and the current user's recent commits and merged pull requests within a configurable window.
- Derive `progress` and `affinity` per issue; detect uniformity; write one normalized file the analysis reads. Fail rather than shrink the board on truncated lists, as `bugs-gather` does.
- Config keys: `progressLabels`, `progressPipelines`, `quietDays`, `staleDays`, `affinityDays`, `uniformityShare`.

### 3. `scripts/bugs-gather`

- Replace `progress_of` and `ready_group` with the shared stage derivation; add `mergeable`, branch, and activity data; add the flags and affinity.
- Map rank weights: an `affinity` weight group with small positive and large negative values, documented with the existing weights.

### 4. `scripts/report-board`

- Validate `progress` and `affinity` on both board types, replacing the `inProgress` text check and the `ready_groups` list.
- Update capacity and pick checks: `close-out` does not hold a slot; picks avoid issues owned by someone else unless the analysis gives a reason.
- `compare`: report stage moves ("draft to awaiting review"), flags raised and cleared, and affinity changes, replacing the current Started, Progress moved, and No longer in progress entries.

### 5. Templates

- `backlog-triage.html` and `bugs.html`: stage tags with distinct form and color in both themes, a legend, the header stage strip, the In flight section, next-action text, flag markers, and affinity context. Keep the existing shared look in `design-conventions.md`, extending its palette with stage colors that stay distinguishable in grayscale.
- The lane model reads `progress.stage` instead of `inProgress` truthiness.

### 6. References and skill prose

- `board-types/backlog-triage.md`: replace Analyze step 1 with a pointer to `backlog-gather` and `progress-model.md`; remove assignment as a progress signal; describe affinity in picks.
- `board-types/bugs.md`: new Ready to go groups, flags, and the affinity weight.
- `design-conventions.md`: stage colors and the In flight section.
- `SKILL.md` and the plugin README: mention the gather script and the new sections.

### 7. Tests

- New `tests/scrut/backlog-gather.md` with fixture stubs for each stage, each flag, uniformity, and implicit affinity.
- Extend `bugs-gather.md`, `report-board.md`, and `report-board-bugs.md` for the new fields, the regrouped Ready to go, and `compare` output.

## Open Questions

- Should `suggest-next-issue` adopt affinity and the same stage rules in this change, or in a follow-up that resolves #548 there?
- Does `uniformityShare` default to 0.9, and should it count only open issues, or include issues closed recently?
- Which recent-activity window should implicit affinity use by default: the same 30 days as `stale`, or longer?
- Should the In flight section replace the existing stage information in lanes and tiers, or sit beside it?
- Is a merged pull request with the progress label still present `close-out` or `started`? This plan proposes `close-out`, with the label noted as a cleanup.

## Verification

- `make test-all` passes, including the new and extended scrut suites.
- Publish sample boards for this repository and one `swing-left` repository, and confirm each stage, flag, and affinity value renders in both themes and at 390 pixels.
- Run `compare` across two syncs where a pull request moves from draft to review, and confirm the report names the move.
