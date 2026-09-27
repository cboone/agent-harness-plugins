# Add a `focus` Board Type to `publish-report-board`

## Summary

Add a second board type, `focus`, to the `publish-report-board` plugin. It answers a different question from `backlog-triage`: of everything in a multi-repository client workspace that touches the user, which few items matter now, and why. It is built for client work, where many stakeholders move priorities often and most of the tracker is not what matters in the moment.

The board combines three priority sources: the user's steering note, ZenHub state, and GitHub state. Operational signals such as production errors, CI health on the default branch, and deploy state are out of scope, as are Slack and email.

The first client is Swing Left: the `swing-left` organization's repositories and its ZenHub workspace. Nothing Swing Left specific is hard-coded; a per-client config file carries it.

The user returns to the same board many times a day, so a re-sync in a new conversation must be as cheap as one in the same conversation. Everything a later sync needs to answer "what moved?" and to skip re-reading unchanged items lives in a persistent per-client cache, not in the session's working files.

## Scope: Work That Is Definitively the User's

The board considers only items in the repositories the client config lists, and only items that name the user directly:

- Open issues assigned to the user.
- Open pull requests the user authored.
- Open pull requests that request the user's review by name, found with `user-review-requested:LOGIN`. Requests made to a team the user belongs to are out of scope.
- Open issues and pull requests in which another person mentions the user by login. An item the user wrote, or one already in scope through assignment, authorship or a review request, does not become an ask by mentioning the user.

Every search is built from `repo:ORG/NAME` qualifiers for the configured repositories, never from `org:`. That keeps archived repositories and repositories outside the ZenHub workspace out without a separate filter.

Unassigned issues, team review requests, issues in areas the user effectively owns but is not assigned to, repositories missing from the config, and ZenHub-only issues that have no GitHub counterpart are out of scope. Widening scope later is a config change plus new searches, not a redesign.

## Evidence Behind the Design

Gathered on 2026-09-25 against live Swing Left data.

- **Volume.** 466 open issues across 11 non-archived `swing-left` repositories. 75 are assigned to `cboone`, spread over five repositories: `votefwd` 33, `frontend` 26, `SwingLeftPy` 14, `templates` 1 and `swingleft-analytics` 1. Twenty of them are containers rather than work: 16 Epics and 4 Projects.
- **Containers are a ZenHub classification.** GitHub's issue `type` is empty on 38 of the 75. ZenHub's `issueType` carries the container types with a level: Project at level 2, Epic at level 3, and Sub-task at level 5. `issueType` is a union, so the query needs inline fragments on `GithubIssueType` and `ZenhubIssueType`; selecting `name` directly fails.
- **The tracker's priority signal is thin.** Of the 75 assigned issues, 23 sit in New Issues and 38 in Product Backlog. ZenHub's `priority` field is unset on every one. Sprint membership is set, and the current sprint (Sep 14 to Sep 28) held three of them when first counted and six on a recount the same day, which makes it the strongest ZenHub signal and one that moves within a day.
- **Pipelines are not a fixed list.** The live workspace has "High Priority" and "Blocked/On Hold" pipelines that the `manage-zenhub` board-data reference does not list. ZenHub pipeline state also lags GitHub: `SwingLeftPy#403` is closed on GitHub and still sits in In Progress.
- **Work arrives as new issues, not backlog drawdown.** This month's 51 merged PRs in `votefwd`, `frontend` and `SwingLeftPy` closed 37 issues. One of them, `SwingLeftPy#403`, was in the 2026-09-18 assigned inventory; the rest were filed and fixed within days. Nineteen PRs closed no issue.
- **Most review requests are not the user's, and archived repositories distort the counts.** `review-requested:cboone` across the organization matches 108 open PRs, 97 without archived repositories, and 74 of the 100 returned came from Dependabot. `user-review-requested:cboone` matches 13 across the organization, but 11 of those are 2022 Dependabot and `vf-bot` PRs in the archived `pairing-interview`; without archived repositories only 2 remain.
- **Mentions are mostly the user's own.** All four open items matching `mentions:cboone` were written by the user and are assigned to them. The search does not say who made the mention, so the gatherer reads the author of the mentioning body or comment.
- **Per-item model work is what scales linearly.** `backlog-triage` reads every issue body and places every issue in a lane. Gathering is cheap by comparison:
  - One aliased ZenHub `issueByInfo` query returned pipeline, sprint and priority for all 75 assigned issues in 0.9 s.
  - A single combined GitHub GraphQL query with five searches took 10.5 s and sits at GitHub's timeout; adding timeline fields made it fail with HTTP 502. The gatherer splits it into parallel calls.

## Board Shape

Sections, most actionable first. A section with nothing that earns a place shrinks to its heading and one line, as `backlog-triage` already does; the analysis never promotes an item just to fill a section.

| Section           | Holds                                                                                                                                                                                     |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Now               | The user's open PRs and in-progress work, with CI and review state and what each is waiting on                                                                                            |
| Focus             | At most `focusLimit` items (default 10), each with a "why now" naming the signals that put it there                                                                                       |
| Asks              | Review requests made to the user by name, and mentions from other people, that await the user; anything from a configured bot collapses into one counted line linking a search            |
| Waiting on others | The user's items held by someone else, naming what they wait on, including every item in a pipeline the config lists in `waitingPipelines`                                                |
| Rising            | A short list of items whose signals moved toward Focus without crossing into it                                                                                                           |
| Everything else   | Counts on the page: parked, containers (Initiative, Project, Epic), untriaged, snoozed, each linking a search. The data still lists every member, so validation can account for each item |

For Swing Left, `waitingPipelines` is `["Blocked/On Hold"]`. An item there shows in Waiting on others with its ZenHub blocking issues when it has any, and otherwise "on hold in ZenHub".

### Signals

Every item in Now, Focus, Asks and Rising carries one or more signals, each with a `source` (`steering`, `zenhub` or `github`), a `kind`, a short `text`, and the `at` time it was observed or set. A steering signal also carries `entry`, the ID of the steering entry it rests on. The page shows each signal's age, so a pick resting on a week-old reason reads differently from one resting on this morning's. A Focus pick must carry at least one signal; the validator enforces it.

Signals may name people by GitHub login as the source of a signal, such as "a review requested by `@erhowell`". Update `design-conventions.md` to allow that for this board type. The existing rule against writing about staff or staffing, meaning assigning people to work, still applies to `focus`.

Signal text and "why now" refer to items as `repo#N`, such as `votefwd#4034`, the same form the steering note uses. The page links that form within the board's organization.

### Horizon

Focus means what to work on today, with the current sprint and any steering entries as the wider context. The current sprint comes from the workspace's `activeSprint` on every sync, so a sprint rollover needs no config change.

## The Steering Note

The steering note is the user's input and a source of truth in its own right; the board renders it and never becomes it. It is a Markdown file whose entries are list items in a fixed grammar, readable by a person and parseable by the script:

```markdown
- 2026-09-25T14:10 pin votefwd#4034 until 2026-09-30: auth enforcement before the send window
- 2026-09-25T14:10 boost frontend#1780: the NGP sync is wanted this week
- 2026-09-24T09:00 snooze SwingLeftPy#217 until 2026-11-10: PG16 waits until after the election
- 2026-09-24T09:00 drop votefwd#4052: coverage work is parked this quarter
- 2026-09-23T16:30 context: PDF extraction is the current migration step
```

Verbs are `pin`, `boost`, `snooze`, `drop` and `context`. `pin` places an item in Focus; `boost` adds weight; `snooze` hides an item until a date; `drop` hides it until the note changes; `context` is free text the analysis reads when it writes "why now". Entries with `until` expire, and the check-in offers to remove expired ones. An entry's ID is its timestamp, verb and target together, which stay stable while the note is edited around them. The skill edits the note through the Write and Edit tools as the user directs; the page never edits it.

The note's path is set in the client config. For Swing Left it is `~/Work/docs/focus/swing-left.md`. `~/Work/docs/focus/` does not exist yet; the first sync that writes the note creates it.

The note is committed. For Swing Left it is tracked in `sl-vf`, a bare repository at `~/Work/sl-vf` whose worktree is `~/Work`. Its local `core.excludesfile`, `~/Work/.sl-vf.gitignore`, ignores everything by default and allowlists `docs/**`, so the note needs no force flag to be added. After the check-in changes the note, the skill commits only the note, GPG-signed, with a Conventional Commits message such as `docs: steer focus toward votefwd#4034`. The client config's `steeringGit` names how to reach the repository, because plain `git` fails in a worktree with no `.git` directory, so the skill passes `--git-dir` and `--work-tree` explicitly. The commit names the note as a pathspec (`git commit -S -- PATH`) rather than committing the index, because that worktree routinely holds other uncommitted changes. The skill never pushes; pushing stays with the user. When the note itself has uncommitted changes the skill did not make, it stops and asks rather than folding them into its commit.

## Client Config

One JSON file per client, at a path the user passes or the skill finds at `${XDG_CONFIG_HOME:-$HOME/.config}/report-boards/focus/CLIENT.json`:

| Field              | Contents                                                                                                                               |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| `client`           | A short name, used in the title (`swing-left focus`), the working file names, and the cache directory                                  |
| `login`            | The user's GitHub login                                                                                                                |
| `org`              | The GitHub organization the repositories belong to, used for links and `repo#N` references                                             |
| `repos`            | Repositories in scope, each with its name and GitHub numeric ID for ZenHub lookups. Searches cover these and nothing else              |
| `zenhub`           | Workspace ID, the token's environment variable name, a weight per pipeline, and `defaultWeight` for a pipeline the table does not list |
| `waitingPipelines` | Pipelines whose items belong in Waiting on others                                                                                      |
| `containerLevels`  | ZenHub issue-type levels that count as containers, default `[1, 2, 3]`                                                                 |
| `bots`             | Logins whose review requests and comments are counted but never surfaced as asks                                                       |
| `focusLimit`       | The Focus cap, default 10                                                                                                              |
| `steeringNote`     | Path to the steering note                                                                                                              |
| `steeringGit`      | `{ "gitDir", "workTree" }` for committing the note; omitted when the note sits in an ordinary repository or is not committed           |

The ZenHub token stays in its environment variable. The gatherer writes the authorization header to a mode-600 temporary file, passes it to `curl` with `-H @FILE`, and removes the file on exit, so the token never appears on a command line or in shell tracing. This works with the curl 8.7.1 that macOS ships.

## Persistent Cache

Each client has a cache directory at `${XDG_CACHE_HOME:-$HOME/.cache}/report-boards/focus/CLIENT/`, shared by every conversation and every harness:

- `gather.json`: the last complete gather, normalized, with a fingerprint per item covering GitHub state, `updatedAt`, pipeline, sprint, estimate, blocking counts, CI state on the user's PRs, and the latest comment from someone other than the user.
- `scored.json`: the last score output, so a later sync can say what entered or left the shortlist.
- `digests/`: one digest per item, keyed by `repo#N` and `updatedAt`.

The gatherer writes each file through a temporary file in the same directory and renames it into place, so an interrupted sync leaves the previous cache intact. When the cache is missing or unreadable, the sync is a cold one: it says so, reads every shortlisted item, and limits "what moved" to the board-level comparison `report-board compare` provides. The cache holds nothing the sources cannot rebuild, so deleting it costs one cold sync.

## Sync Flow

1. **Find the previous board** as the existing skill does, by exact title.
2. **Gather deterministically.** A new bundled script, `focus-gather`, runs the GitHub searches from the scope section as parallel GraphQL calls, then one aliased ZenHub query for every candidate plus the workspace's active sprint. Open or closed state always comes from GitHub; ZenHub supplies pipeline, sprint, estimate, blocking counts and issue type. It writes one normalized JSON file and compares it with the cached `gather.json`. Cost is a fixed number of calls, not one per issue.
3. **Score deterministically.** `focus-gather score` applies the steering note and the configured weights in `jq`, buckets every item, and writes a ranked shortlist of about 25 candidates with a per-signal breakdown. Containers, snoozed and dropped items leave the shortlist here.
4. **Check in with the user.** Before any model reading, show the current steering entries, expired entries, and what moved since the cached gather: new asks, pipeline and sprint changes, new comments from other people, CI state changes on the user's PRs. Then ask whether priorities changed, using a structured question tool when the session offers one, and otherwise numbered options in plain text, waiting for the reply. Record the answers as steering entries, commit the note as described above, and re-run the score, which runs in `jq` time. Skip the questions when the user already stated updates in the invoking message. If the host blocks the note write or the commit, stop before re-scoring and report the blocked command and the restriction.
5. **Read the shortlist only.** The model reads bodies and recent comments for shortlisted items whose `updatedAt` differs from their cached digest, and reuses cached digests for the rest. When more than a handful changed, read them in parallel with subagents, each returning a digest in a fixed shape.
6. **Write the board data**: Focus picks with "why now", Asks, Waiting, Rising, and the summary, then validate, render, compare and publish through the existing script and Artifact flow. Update the cache only after the board is published, so a sync that stops early leaves the previous cache as the baseline for the next one.

The cheap path, steps 2 and 3 against a warm cache, answers "has anything moved?" without model reading, in a new conversation as well as the same one. When nothing moved and the user has no steering updates, report that and leave the board as it is.

## Script Changes

`report-board` today assumes a single repository and one board type. It needs:

- **Board-type dispatch** in `validate`, `render`, `compare`, the identity guard, and `board_summary`, which today prints "N issues in M lanes" on every validate and render. `render` already picks its template by board type, and `extract` is type-agnostic.
- **Per-type top-level requirements.** `validate` requires `repo`, a non-empty `issues` list and a non-empty `lanes` list unconditionally today; those become `backlog-triage` rules.
- **Identity for a multi-repository board.** `focus` boards carry `scope` (`{ "org", "login", "client" }`) instead of `repo`, and the identity guard compares `title` and `scope`.
- **Sync metadata without a single commit.** `sync.at` stays required; `sync.branch` and `sync.commit` become per-board-type requirements. A `focus` board records the ZenHub workspace and the searched repositories in `sync.extra`, which stays a list of text.
- **`focus` board data** carries what validation checks, since `validate` sees only the data file:
  - `items`: every item in scope, keyed `repo#N`, with its section or `Everything else` bucket, including bucket members the page shows only as counts.
  - `steering`: a snapshot of the note's entries, each with its ID, `at`, verb, target, `until` and text.
  - Section lists that reference items by key, and signals as described above.
- **`focus` validation rules:**
  - Focus holds at most `focusLimit` items.
  - Every Focus item has at least one signal, and every signal's `at` is no later than `sync.at`.
  - Every open item assigned to the user appears in exactly one section or `Everything else` bucket.
  - No item appears in two sections.
  - A snoozed or dropped item never appears in Focus unless a later `pin` overrides it.
  - A steering signal's `entry` names an entry in `steering` that has not expired at `sync.at`.
- **`focus` compare output**: items that entered or left Focus, moved between sections, and new or resolved asks.

`focus-gather` is a new bundled script beside `report-board`, following `write-bash-scripts`, including its Bash 3.2 compatibility rules. Its GraphQL queries live in files next to it.

## Template

Add `templates/focus.html`, following `design-conventions.md`: tokens for both themes, a single 1080-pixel column that reflows at phone width, amber for Focus picks, and state carried in form as well as color. Signal chips show source and age; an aged signal gets a dashed outline, following the "state in form" rule. The header counts are Focus, Asks, Waiting, Rising and in scope, with a live sync age.

The page differs from `backlog-triage.html` in three places that cannot be copied:

- **Links.** `backlog-triage.html` links only `owner/repo#N` and bare `#N`, and builds every URL from one `repoUrl`. `focus.html` links `repo#N` within `scope.org`, and builds issue, pull request and search URLs per repository.
- **Age thresholds.** A board for today goes stale in hours, not days. The header age turns amber after 8 hours and red after 24, and signal chips compute their own ages against the same clock. Delivery step 5 checks these thresholds against real use.
- **Shared helpers.** There is no build step, so the element builder, the prose linker, sync-time formatting and the live age are copied from `backlog-triage.html`. Each copy carries a comment naming its counterpart, so a fix to one prompts a look at the other. Copy them after the head-lane capacity fix (`fix/head-lane-freed-count`) lands, so the copy starts from corrected code.

## Skill and Documentation

- Add `references/board-types/focus.md` covering gather, score, check-in, the persistent cache, analysis, data fields, what the page draws, validation, and a minimal example, parallel to `backlog-triage.md`.
- Update `SKILL.md`:
  - The board-type table, and the line saying only `backlog-triage` ships a template.
  - Step 3's naming, which becomes per board type. Working file names for `focus` are `CLIENT-focus.json` and `CLIENT-focus.html`, in a `focus/CLIENT` directory, and the local fallback keeps the board in the client's cache directory.
  - Step 4's local fallback, which finds a `focus` board by client rather than by `repoUrl`.
  - Step 5, which defers to the board type's reference for its check-in.
  - Step 8's identity-guard text, which names `scope` for a `focus` board.
  - Step 10's sync line, which reports the workspace and repositories for a `focus` board rather than a branch and commit.
- Update `sync-metadata.md` so `sync.branch` and `sync.commit` are per-board-type requirements.
- Update `design-conventions.md` with the narrow exception for naming logins as signal sources.
- Update `choosing-a-board.md` with when each type fits: `backlog-triage` for a repository whose backlog is the plan, `focus` for a workspace where attention is the constraint.
- Update the plugin README, the catalog description if it changes, and the recommended permissions for the new commands.
- Bump the plugin to the next minor version, from whatever the head-lane fix leaves it at; a new board type is a new capability.

## Tests

- Scrut coverage in `tests/scrut/report-board.md` for `focus` validation (each rule, accepting and rejecting), per-type top-level requirements, dispatch by board type including `board_summary`, identity comparison on `scope`, and `compare` output.
- Scrut coverage for `focus-gather` with stubbed `gh` and `curl`: parallel search assembly from `repo:` qualifiers, ZenHub lookup assembly including the issue-type fragments, bot filtering, mention filtering, steering parsing and expiry, container detection by level, the default pipeline weight, `waitingPipelines`, scoring order, warm and cold cache, and the empty-workspace case.
- `tests/fixtures` has a `gh` stub but no `curl` stub; add one. Register new paths in the Makefile's `SCRUT_ENV` and CI's `scrut-env`. Test configs name a test-only token variable with a sample value, and `SCRUT_UNSET` clears the real ZenHub token variable so no test can reach it.
- A template execution check if issue #403's approach for `backlog-triage` lands first; otherwise note the gap there.

## Delivery Order

1. The head-lane capacity fix to `backlog-triage.html` lands on `main` (`fix/head-lane-freed-count`).
2. `focus-gather` gather and score against live Swing Left data, run from the worktree. Stop and review the ranked shortlist with the user to calibrate weights before building anything that depends on them. The script and its tests land on the branch once calibrated.
3. Board data schema, `report-board` dispatch and `focus` validation, with scrut tests.
4. Template and render.
5. Skill, references and README.
6. A first real publish for Swing Left, then a re-sync in a new conversation after a steering change, recording timings for each phase and confirming the cache makes that re-sync cheap.

## Out of Scope

- Operational signals: production errors, CI health on default branches, deploy state.
- Slack, email and calendar as priority sources.
- ZenHub-only issues with no GitHub counterpart.
- Writing anything back to ZenHub or GitHub. Moving a pipeline or reassigning an issue stays with `manage-zenhub`.
- Porting to `cboone/board`. The gather and score split is designed so it can move to a server later.

## Decisions

Confirmed by the user on 2026-09-25:

- Priority sources are the user, through the steering note, plus ZenHub and GitHub.
- The skill checks in with the user about priority updates on every run.
- Sections hold only what earns a place; none is filled for its own sake.
- Focus is for today, with the current sprint as context.
- The steering note lives at `~/Work/docs/focus/swing-left.md` and is committed to `sl-vf`.
- Scope is work that is definitively the user's, as the scope section defines. Unassigned issues are out: 82 were filed in scope between 2026-09-18 and 2026-09-25, 53 of them in `votefwd`.
- Operational signals are out of scope.
- `focus` is a second board type in `publish-report-board`, published as a private Artifact.

Confirmed by the user on 2026-09-27, after a plan review:

- A re-sync in a new conversation must be cheap, because the user returns to the same boards repeatedly; the persistent cache provides it.
- Searches cover only the configured repositories, through `repo:` qualifiers.
- Items in the "Blocked/On Hold" pipeline go to Waiting on others. This is a first version, open to refinement.
- Asks surface mentions from other people only, excluding items the user wrote or already holds.
