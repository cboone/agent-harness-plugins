# Distinguish In-Progress States on Report Boards

Related issues: #551, #548

## Context

Both report boards collapse very different kinds of work into one "in progress" state.

- **Backlog triage.** `inProgress` is a single free-text string: a branch, `PR #390`, or a phrase such as `the in progress label`. The template draws any value as the same "In progress" tag (`templates/backlog-triage.html`, `progressTag`), and every in-progress issue holds its serial or head lane's slot. The gather step fetches open pull requests with only `number,title,headRefName,closingIssuesReferences`, so the board cannot tell a six-week-old pushed branch from an approved, green pull request. The model derives the value by reading, which is how #551's inferred and carried-over statuses reached the page.
- **Bugs.** `bugs-gather` collects `isDraft`, `reviewDecision`, and the check rollup, and Ready to go splits into `ship`, `review`, `in-progress`, and `ready-to-fix`. But `review` mixes waiting on a reviewer, changes requested, and failing checks, and `in-progress` mixes a draft fix with a bare label or pipeline.
- **Assignment.** Both boards, following `suggest-next-issue`, treat assignment to the current user as in progress. Assignment says who owns an issue, not that work has started (#548). In Chris's non-client repositories, Chris is assigned to and claims everything, so the explicit signal carries no information there.

The outcome: both boards share one progress model derived in code from gathered signals, render each stage distinctly with whose move it is and what to do next, flag stale and unhealthy work, and treat ownership as a separate, weak ranking factor called affinity.

## Decisions

- **Scope:** both boards and `suggest-next-issue`, one shared vocabulary. `suggest-next-issue` stops treating assignment as in progress, counts only the progress signals defined here, and weighs affinity the same way, which resolves #548. The focus board (#558, `feature/focus-board`) adopts it when it lands; it is out of scope here.
- **Progress stages**, ordered, each backed by a named gathered signal:

  | Stage             | Signal                                                                              | Next move               |
  | ----------------- | ----------------------------------------------------------------------------------- | ----------------------- |
  | `started`         | A progress label or progress pipeline, with no branch or pull request               | Author                  |
  | `branch`          | A local or remote branch, or a worktree, naming the issue, with no pull request     | Author                  |
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
  - `local` when a branch exists only on the machine that ran the gather. It names that host, so a sync from another machine explains a difference, and its next action is "push it". Local and pushed branches share one stage because they answer "how far along, and whose move" the same way; being unpushed is a condition of the branch, not a step of progress.
- **A merged pull request outranks a leftover label:** an open issue whose closing pull request merged is `close-out` even when a progress label is still present, and the label is noted as a cleanup.
- **Provenance (#551):** every stage names the signal that produced it, and is re-derived on each sync from that sync's gather. Previous board data never supplies a stage. Inferred statuses, such as a long-running routine, are recorded as blockers or left off.
- **Scheduling:** display plus flags. Every stage from `started` to `ready-to-merge` holds its lane slot as today; `quiet`, `stale`, and `ready-to-merge` are flagged in the lane so a held slot explains itself. `close-out` does not hold a slot.
- **Affinity** replaces assignment as a progress signal. It is a separate dimension saying how much an issue is already someone's:
  - Explicit: assigned, or claimed through a label or pipeline.
  - Implicit, for the current user, in three tiers, strongest first:
    1. Active work overlap: the issue's component overlaps components touched by the user's open branches or pull requests. No window, since an open branch is current by definition.
    2. Recent work in the area: the user committed to those files or components, or merged pull requests touching them, within 30 days (`affinityWorkDays`). The point is an area the user is in now; a longer window would mark most areas in a repository the user works in heavily.
    3. Discussion: the user filed the issue at any time, or commented on it within 90 days (`affinityCommentDays`).
  - Uniformity, applied to each signal separately: when one owner holds a signal on at least 90% of open issues (`uniformityShare`), and the repository has at least five open issues (`uniformityMinimum`), that signal is ignored for the repository. Only open issues count, since closed ones say nothing about the current backlog. This drops assignment, claims, and "filed it" in Chris's non-client repositories without a per-repository switch, keeps them in `swing-left` repositories, where they vary, and leaves whichever signals still tell issues apart.
  - Effect: a small boost to picks and ranks for the current user, none for unowned issues, and a large penalty, never exclusion, for issues owned by someone else. Shown as context on every row: "affinity: you (recent commits in `bin/`)", "affinity: @someone (assigned)".
  - Affinity is a weak factor because issue state is not reliable. It never holds a slot and never marks progress.
- **Bugs board groups** map to the shared stages: Ready to go groups become `ready-to-merge`, `needs-author`, `awaiting-review`, `draft`, `branch`, `started`, and `ready-to-fix`. Critical and High rows keep their tier, since urgency wins over readiness, and show the same stage tag and flags in place of the current one-line fix state.
- **Gathering:** a new deterministic `backlog-gather` script, modeled on `bugs-gather`, derives stages, flags, and affinity in code. Shared jq definitions for stages and flags are copied between the two gather scripts with comments naming each other, matching the template convention, until a shared layer is justified.
- **Page:** a header strip of per-stage counts, across every section, linking to the rows; stage-specific inline tags with a legend; and a short next action on each in-progress row ("merge it", "answer review", "fix checks", "resolve conflict", "push it", "resume or drop", "close or split").
- **In flight view, per board:**
  - Backlog triage gets an In flight section above Start now, listing all active work grouped by stage. Lanes keep each in-progress issue in place with a compact stage tag, because lane order and capacity depend on it, so the issue appears in both.
  - Bugs gets no separate section. Ready to go, regrouped by stage, is that view. In-flight bugs in Critical or High stay in their tier with the stage tag and are counted in the header strip.
- **Version:** new capability and a changed data contract, so a minor bump of `publish-report-board` to `1.2.0`, confirmed with the check-versions skill before the PR. If the `inProgress` string is removed rather than kept as an accepted legacy field, revisit whether that is a major change.

## Changes

### 1. Shared progress contract

- Define the `progress` object in `references/board-types/` prose and in `report-board` validation: `stage`, `carrier` (`{ "branch": ... }`, `{ "pr": N }`, `{ "label": ... }`, `{ "pipeline": ... }`), `signal` (provenance text), `since`, `lastActivity`, `nextMove`, `nextAction`, `flags`, and optional `host` (with the `local` flag) and `extraCarriers`.
- Define the `affinity` object: `owner` (`you`, a login, or null), `kind` (`explicit` or `implicit`), `tier` for implicit affinity, `reasons`, and `ignored`, listing the signals uniformity dropped for the repository.
- Add a shared reference, `references/progress-model.md`, owning the stage table, flags, thresholds, provenance rule, and affinity rules; both board-type references link to it.

### 2. `scripts/backlog-gather` (new)

- Gather open issues, open pull requests with `isDraft`, `reviewDecision`, `statusCheckRollup`, `mergeable`, `updatedAt`, and latest review times, remote and local branches with committer dates and ahead/behind counts against the default branch, worktrees, and the current user's recent commits and merged pull requests within a configurable window.
- Derive `progress` and `affinity` per issue; detect uniformity; write one normalized file the analysis reads. Fail rather than shrink the board on truncated lists, as `bugs-gather` does.
- Config keys: `progressLabels`, `progressPipelines`, `quietDays`, `staleDays`, `affinityWorkDays`, `affinityCommentDays`, `uniformityShare`, `uniformityMinimum`.

### 3. `scripts/bugs-gather`

- Replace `progress_of` and `ready_group` with the shared stage derivation; add `mergeable`, branch, and activity data; add the flags and affinity.
- Map rank weights: an `affinity` weight group with small positive and large negative values, documented with the existing weights.

### 4. `scripts/report-board`

- Validate `progress` and `affinity` on both board types, replacing the `inProgress` text check and the `ready_groups` list.
- Update capacity and pick checks: `close-out` does not hold a slot; picks avoid issues owned by someone else unless the analysis gives a reason.
- `compare`: report stage moves ("draft to awaiting review"), flags raised and cleared, and affinity changes, replacing the current Started, Progress moved, and No longer in progress entries.

### 5. Templates

- `backlog-triage.html` and `bugs.html`: stage tags with distinct form and color in both themes, a legend, the header stage strip, next-action text, flag markers, and affinity context.
- `backlog-triage.html` only: the In flight section above Start now. `bugs.html` regroups Ready to go by stage instead. Keep the existing shared look in `design-conventions.md`, extending its palette with stage colors that stay distinguishable in grayscale.
- The lane model reads `progress.stage` instead of `inProgress` truthiness.

### 6. References and skill prose

- `board-types/backlog-triage.md`: replace Analyze step 1 with a pointer to `backlog-gather` and `progress-model.md`; remove assignment as a progress signal; describe affinity in picks.
- `board-types/bugs.md`: new Ready to go groups, flags, and the affinity weight.
- `design-conventions.md`: stage colors, and the In flight section on the backlog board.
- `SKILL.md` and the plugin README: mention the gather script and the new sections.

### 7. `plugins/suggest-next-issue/skills/suggest-next-issue/SKILL.md`

- Replace step 2's signal list with the progress signals from `progress-model.md`: a branch or worktree naming the issue, a progress label, or an open pull request that closes it. Drop assignment as a signal.
- Add affinity as a ranking signal with the same weights in prose: a small boost for the current user, a large penalty for someone else, and the uniformity rule.
- List in-progress issues with their stage and next move, and `close-out` issues separately as cleanups.
- Bump `suggest-next-issue` as a minor change, since it changes what the skill recommends.

### 8. Tests

- New `tests/scrut/backlog-gather.md` with fixture stubs for each stage, each flag including `local`, uniformity per signal and below `uniformityMinimum`, and each implicit affinity tier.
- Extend `bugs-gather.md`, `report-board.md`, and `report-board-bugs.md` for the new fields, the regrouped Ready to go, and `compare` output.

## Verification

- `make test-all` passes, including the new and extended scrut suites.
- Publish sample boards for this repository and one `swing-left` repository, and confirm each stage, flag, and affinity value renders in both themes and at 390 pixels.
- Run `compare` across two syncs where a pull request moves from draft to review, and confirm the report names the move.
