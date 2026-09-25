# Add a `focus` Board Type to `publish-report-board`

## Summary

Add a second board type, `focus`, to the `publish-report-board` plugin. It answers a different question from `backlog-triage`: of everything in a multi-repository client workspace that touches the user, which few items matter now, and why. It is built for client work, where many stakeholders move priorities often and most of the tracker is not what matters in the moment.

The board combines three priority sources: the user's steering note, ZenHub state, and GitHub state. Operational signals such as production errors, CI health on the default branch, and deploy state are out of scope, as are Slack and email.

The first client is Swing Left: the `swing-left` organization's repositories and its ZenHub workspace. Nothing Swing Left specific is hard-coded; a per-client config file carries it.

## Scope: Work That Is Definitively the User's

The board considers only items that name the user directly:

- Open issues assigned to the user.
- Open pull requests the user authored.
- Open pull requests that request the user's review by name, found with `user-review-requested:LOGIN`. Requests made to a team the user belongs to are out of scope.
- Open issues and pull requests that mention the user by login.

Unassigned issues, team review requests, and issues in areas the user effectively owns but is not assigned to are out of scope. Widening scope later is a config change plus new searches, not a redesign.

## Evidence Behind the Design

Gathered on 2026-09-25 against live Swing Left data.

- **Volume.** About 460 open issues across six `swing-left` repositories; 73 assigned to `cboone`, of which more than 20 are Projects and Epics rather than work.
- **The tracker's priority signal is thin.** Of the 73 assigned issues, 21 sit in New Issues and 38 in Product Backlog. ZenHub's `priority` field is unset on every one. Sprint membership is set, and the current sprint (Sep 14 - Sep 28) holds three of them, which makes it the strongest ZenHub signal.
- **Work arrives as new issues, not backlog drawdown.** This month's 51 merged PRs in `votefwd`, `frontend` and `SwingLeftPy` closed 37 issues. One of them, `SwingLeftPy#403`, was in the 2026-09-18 assigned inventory; the rest were filed and fixed within days. Nineteen PRs closed no issue.
- **Most review requests are not the user's.** 108 open PRs match `review-requested:cboone`, which includes team requests; of the first 50 returned, 32 came from Dependabot and 2 from release automation. Only 2 match `user-review-requested:cboone`, the requests made to the user by name.
- **Per-item model work is what scales linearly.** `backlog-triage` reads every issue body and places every issue in a lane. Gathering is cheap by comparison:
  - One aliased ZenHub `issueByInfo` query returned pipeline, sprint, estimate and blocking counts for all 73 assigned issues in 0.8 s.
  - A single combined GitHub GraphQL query with five searches took 10.5 s and sits at GitHub's timeout; adding timeline fields made it fail with HTTP 502. The gatherer splits it into parallel calls.

## Board Shape

Sections, most actionable first. A section with nothing that earns a place shrinks to its heading and one line, as `backlog-triage` already does; the analysis never promotes an item just to fill a section.

| Section           | Holds                                                                                                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Now               | The user's open PRs and in-progress work, with CI and review state and what each is waiting on                                                                           |
| Focus             | At most `focusLimit` items (default 10), each with a "why now" naming the signals that put it there                                                                      |
| Asks              | Review requests made to the user by name, and mentions from people, that await the user; anything from a configured bot collapses into one counted line linking a search |
| Waiting on others | The user's items held by someone else, naming what they wait on                                                                                                          |
| Rising            | A short list of items whose signals moved toward Focus without crossing into it                                                                                          |
| Everything else   | Counts only: parked, containers (Initiative, Project, Epic), untriaged, snoozed, each linking a search                                                                   |

### Signals

Every item in Now, Focus, Asks and Rising carries one or more signals, each with a `source` (`steering`, `zenhub` or `github`), a `kind`, a short `text`, and the `at` time it was observed or set. The page shows each signal's age, so a pick resting on a week-old reason reads differently from one resting on this morning's. A Focus pick must carry at least one signal; the validator enforces it.

Signals may name people by GitHub login, such as "a review requested by `@erhowell`". This relaxes the design conventions' rule against writing about staff for this board type only; update `design-conventions.md` to say so.

### Horizon

Focus means what to work on today, with the current sprint and any steering entries as the wider context.

## The Steering Note

The steering note is the user's input and a source of truth in its own right; the board renders it and never becomes it. It is a Markdown file whose entries are list items in a fixed grammar, readable by a person and parseable by the script:

```markdown
- 2026-09-25T14:10 pin votefwd#4034 until 2026-09-30: auth enforcement before the send window
- 2026-09-25T14:10 boost frontend#1780: the NGP sync is wanted this week
- 2026-09-24T09:00 snooze SwingLeftPy#217 until 2026-11-10: PG16 waits until after the election
- 2026-09-24T09:00 drop votefwd#4052: coverage work is parked this quarter
- 2026-09-23T16:30 context: PDF extraction is the current migration step
```

Verbs are `pin`, `boost`, `snooze`, `drop` and `context`. `pin` places an item in Focus; `boost` adds weight; `snooze` hides an item until a date; `drop` hides it until the note changes; `context` is free text the analysis reads when it writes "why now". Entries with `until` expire, and the check-in offers to remove expired ones. The skill edits the note through the Write and Edit tools as the user directs; the page never edits it.

The note's path is set in the client config. For Swing Left it is `~/Work/docs/focus/swing-left.md`, tracked in the `sl-vf` bare repository, whose ignore rules already include `docs/`.

The note is committed. After the check-in changes it, the skill commits only the note, GPG-signed, with a Conventional Commits message such as `docs: steer focus toward votefwd#4034`. The client config's `steeringGit` names how to reach the repository, because `sl-vf` is a bare repository whose worktree has no `.git` directory: plain `git` fails there, so the skill passes `--git-dir` and `--work-tree` explicitly. The skill never pushes; pushing stays with the user. When the note has uncommitted changes the skill did not make, it stops and asks rather than folding them into its commit.

## Client Config

One JSON file per client, at a path the user passes or the skill finds at `${XDG_CONFIG_HOME:-$HOME/.config}/report-boards/focus/CLIENT.json`:

| Field          | Contents                                                                                                                     |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `client`       | A short name, used in the title (`swing-left focus`) and the working file names                                              |
| `login`        | The user's GitHub login                                                                                                      |
| `org`          | The GitHub organization searched                                                                                             |
| `repos`        | Repositories in scope, each with its GitHub numeric ID for ZenHub lookups                                                    |
| `zenhub`       | Workspace ID, the token's environment variable name, and a weight per pipeline                                               |
| `bots`         | Logins whose review requests and comments are counted but never surfaced as asks                                             |
| `focusLimit`   | The Focus cap, default 10                                                                                                    |
| `steeringNote` | Path to the steering note                                                                                                    |
| `steeringGit`  | `{ "gitDir", "workTree" }` for committing the note; omitted when the note sits in an ordinary repository or is not committed |

The ZenHub token stays in its environment variable. The gatherer writes the authorization header to a mode-600 temporary file and passes it to `curl` with `-H @FILE`, so the token never appears on a command line or in shell tracing.

## Sync Flow

1. **Find the previous board** as the existing skill does, by exact title.
2. **Gather deterministically.** A new bundled script, `focus-gather`, runs the GitHub searches as parallel GraphQL calls (the four searches in the scope section above), then one aliased ZenHub query for every candidate plus the current sprint. It writes one normalized JSON file. Cost is a fixed number of calls, not one per issue.
3. **Score deterministically.** `focus-gather score` applies the steering note and the configured weights in `jq`, buckets every item, and writes a ranked shortlist of about 25 candidates with a per-signal breakdown. Containers, snoozed and dropped items leave the shortlist here.
4. **Check in with the user.** Before any model reading, show the current steering entries, expired entries, and what moved since the last sync: new asks, pipeline and sprint changes, new comments from other people, CI state changes on the user's PRs. Then ask with `AskUserQuestion` whether priorities changed. Record the answers as steering entries, commit the note as described above, and re-run the score, which runs in `jq` time. Skip the questions when the user already stated updates in the invoking message.
5. **Read the shortlist only.** The model reads bodies and recent comments for shortlisted items whose `updatedAt` differs from the cached digest, and reuses cached digests for the rest. Digests live beside the working board files, keyed by item and `updatedAt`. When more than a handful changed, read them in parallel with subagents, each returning a digest in a fixed shape.
6. **Write the board data**: Focus picks with "why now", Asks, Waiting, Rising, and the summary, then validate, render, compare and publish through the existing script and Artifact flow.

The cheap path, steps 2 and 3 plus the comparison with the previous sync, is enough to answer "has anything moved?" without model reading. When nothing moved and the user has no steering updates, report that and leave the board as it is.

## Script Changes

`report-board` today assumes a single repository and one board type. It needs:

- **Board-type dispatch** in `validate`, `render`, `compare`, and the identity guard. `extract` is already type-agnostic.
- **Identity for a multi-repository board.** `focus` boards carry `scope` (`{ "org", "login", "client" }`) instead of `repo`, and the identity guard compares `title` and `scope`.
- **Sync metadata without a single commit.** `sync.at` stays required; `sync.branch` and `sync.commit` become per-board-type requirements. A `focus` board records the ZenHub workspace and the searched repositories in `sync.extra`.
- **`focus` validation rules:**
  - Focus holds at most `focusLimit` items.
  - Every Focus item has at least one signal, and every signal's `at` is no later than `sync.at`.
  - Every open item assigned to the user appears in exactly one section or `Everything else` bucket.
  - No item appears in two sections.
  - A snoozed or dropped item never appears in Focus unless a later `pin` overrides it.
  - A steering signal cites an entry that has not expired.
- **`focus` compare output**: items that entered or left Focus, moved between sections, and new or resolved asks.

`focus-gather` is a new bundled script beside `report-board`, following `write-bash-scripts`, including its Bash 3.2 compatibility rules. Its GraphQL queries live in files next to it.

## Template

Add `templates/focus.html`, following `design-conventions.md`: tokens for both themes, a single 1080-pixel column that reflows at phone width, amber for Focus picks, and state carried in form as well as color. Signal chips show source and age; an aged signal gets a dashed outline, following the "state in form" rule. The header counts are Focus, Asks, Waiting, Rising and in scope, with the live sync age the existing template already computes.

## Skill and Documentation

- Add `references/board-types/focus.md` covering gather, score, check-in, analysis, data fields, what the page draws, validation, and a minimal example, parallel to `backlog-triage.md`.
- Update `SKILL.md`'s board-type table and workflow so step 5 defers to the board type's reference for its check-in, and so the "one repository" wording in steps 3 and 4 becomes per-board-type naming. Working file names for `focus` are `CLIENT-focus.json` and `CLIENT-focus.html`, in a `focus/CLIENT` directory.
- Update `choosing-a-board.md` with when each type fits: `backlog-triage` for a repository whose backlog is the plan, `focus` for a workspace where attention is the constraint.
- Update the plugin README, the catalog description if it changes, and the recommended permissions for the new commands.
- Bump the plugin to `1.1.0`; a new board type is a new capability.

## Tests

- Scrut coverage in `tests/scrut/report-board.md` for `focus` validation (each rule, accepting and rejecting), dispatch by board type, identity comparison on `scope`, and `compare` output.
- Scrut coverage for `focus-gather` with stubbed `gh` and `curl` fixtures: parallel search assembly, ZenHub lookup assembly, bot filtering, steering parsing and expiry, scoring order, and the empty-workspace case. Register new paths in the Makefile's `SCRUT_ENV` and CI's `scrut-env`.
- A template execution check if issue #403's approach for `backlog-triage` lands first; otherwise note the gap there.

## Delivery Order

1. `focus-gather` gather and score against live Swing Left data, run from the worktree. Stop and review the ranked shortlist with the user to calibrate weights before building anything that depends on them.
2. Board data schema, `report-board` dispatch and `focus` validation, with scrut tests.
3. Template and render.
4. Skill, references and README.
5. A first real publish for Swing Left, then a re-sync after a steering change, recording timings for each phase.

## Out of Scope

- Operational signals: production errors, CI health on default branches, deploy state.
- Slack, email and calendar as priority sources.
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
