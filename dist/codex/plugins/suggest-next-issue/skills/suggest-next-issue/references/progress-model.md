# Progress Model

This model says how far along each open issue's work is, whose move comes next, and how much the issue is already someone's. The report boards and the `suggest-next-issue` skill share it, so an issue reads the same wherever it appears. The boards derive every value in code from the signals their gather scripts collect; a skill that applies the model by hand uses the same signals and rules.

`publish-report-board` holds the source of this file, and `make build` copies it into `suggest-next-issue`. Edit the source.

## Signals

Only these signals mark work, each gathered on the current sync. Nothing is carried over from an earlier sync, and nothing is inferred: a long-running routine, a time-gated task, or a plan to start soon is not progress. When something outside the repository gates an issue, record it as a blocker with its reason, or leave it out.

| Signal   | What counts                                                                                                                                                                                                                                                                                              |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Label    | A label in the progress labels, matched without regard to case. The default is `in progress`.                                                                                                                                                                                                            |
| Pipeline | A ZenHub pipeline in the progress pipelines, on a board that reads ZenHub. The default is `In Progress` and `Review/QA`.                                                                                                                                                                                 |
| Branch   | A local branch, a remote branch, or a worktree whose name contains the issue number as a whole number, such as `feature/412-tags` for #412 but not for #41. The default branch never counts.                                                                                                             |
| Open PR  | An open pull request that closes the issue, or whose head branch names it as a branch does.                                                                                                                                                                                                              |
| Merged   | A merged pull request in the same repository that closes the open issue, through a closing keyword or a manual link; or one that only mentions it, while a progress label or pipeline is still on the issue. A mention alone is not a signal: pull requests often name follow-up issues they leave open. |

Assignment is not a progress signal. It says who owns an issue, not that work has started; ownership is [affinity](#affinity).

## Stages

An issue with no signal has no stage and is not in progress. Otherwise its stage is the furthest one any of its signals reaches, in this order:

| Stage             | Reached by                                                                                     | Next move               | Next action                                                               |
| ----------------- | ---------------------------------------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------- |
| `started`         | A label or pipeline, with no branch or pull request                                            | Author                  | open a branch                                                             |
| `branch`          | A branch, with no open pull request                                                            | Author                  | push it, when the branch is local; otherwise open a pull request          |
| `draft`           | An open draft pull request                                                                     | Author                  | mark it ready for review                                                  |
| `awaiting-review` | An open pull request whose review is required and not given, or whose checks are still running | Reviewer, CI, or nobody | wait for review, request a review, or wait for checks                     |
| `needs-author`    | An open pull request with a merge conflict, changes requested, or failing checks               | Author                  | resolve the conflict, answer the review, or fix the checks, in that order |
| `ready-to-merge`  | An open pull request approved or needing no review, with checks passing or absent              | Author                  | merge it                                                                  |
| `close-out`       | A merged pull request, as Merged describes, on an issue still open                             | Author                  | close or split                                                            |

`close-out` outranks every other stage: an issue whose linked pull request merged is `close-out` even when a progress label, a branch, or another pull request remains, and those remain as extra carriers. A leftover progress label also raises the `leftover-label` flag, as a cleanup.

Among open pull requests, the one in the furthest stage carries the issue. A label or pipeline beside a branch or pull request never decides the stage; the branch or pull request does.

### Reading a Pull Request

Check these in order, and stop at the first that holds:

1. A draft is `draft`.
2. A conflict (`mergeable` is `CONFLICTING`), changes requested (`reviewDecision` is `CHANGES_REQUESTED`), or failing checks (the check rollup is `FAILURE` or `ERROR`) is `needs-author`.
3. A required review not yet given (`reviewDecision` is `REVIEW_REQUIRED`), or checks still running (`PENDING` or `EXPECTED`), is `awaiting-review`.
4. Anything else is `ready-to-merge`.

GitHub reports `mergeable` as `UNKNOWN` while it computes the answer. That counts as no conflict, and the signal says mergeability was unknown, so a sync neither waits on GitHub nor reports a conflict it has not seen.

### Next Move

The author moves next in every stage but `awaiting-review`. There the reviewer moves next when a review is required and at least one review is requested; `nobody` moves next when a review is required and none is requested, because the pull request cannot move until someone is asked; and CI moves next when no review is required and checks are running. Inactivity is not a next move: the `quiet` and `stale` flags report it.

## Flags

Flags describe the condition of the work, beside its stage.

| Flag             | Raised when                                                                                                                         |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `quiet`          | The last activity is more than the quiet days old, 7 by default                                                                     |
| `stale`          | The last activity is more than the stale days old, 30 by default. It replaces `quiet`, and the next action becomes "resume or drop" |
| `behind`         | The carrying branch is behind the default branch                                                                                    |
| `conflict`       | GitHub reports the carrying pull request as conflicting                                                                             |
| `multiple`       | More than one branch or open pull request carries the issue. A pull request and its own head branch count once.                     |
| `local`          | The carrying branch exists only on the machine that ran the gather, which the progress names as its host                            |
| `leftover-label` | A `close-out` issue still carries a progress label                                                                                  |

Last activity is the latest of the carrying branch's last commit, the carrying pull request's last update and last review, the merge time for `close-out`, and, for `started`, the issue's last update.

A local branch shares the `branch` stage with a pushed one because both answer how far along the work is, and whose move it is, the same way. Being unpushed is a condition of the branch: work that exists on one machine, and that a sync from another machine cannot see.

## Affinity

Affinity says how much an issue is already someone's. It is a weak ranking factor, because issue state is often out of date: it never marks progress, never holds a lane slot, and never excludes an issue.

| Kind     | Signal                                                                                                                                                                                                                       |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Explicit | An assignee. Or a claim label or claim pipeline, owned by the issue's assignees, or by no one known when it has none. Claim settings default to empty, and a label or pipeline cannot be both a claim and a progress signal. |
| Tier 1   | One of the issue's areas covers a file changed on the current user's open branches or pull requests                                                                                                                          |
| Tier 2   | One of the issue's areas covers a file in the current user's commits, or in pull requests the current user merged, within the work days, 30 by default                                                                       |
| Tier 3   | The current user filed the issue, or commented on it within the comment days, 90 by default                                                                                                                                  |

The tiers are implicit affinity, for the current user only, strongest first. An area is a named set of path patterns, such as `parser` covering `src/parser/**`, tagged on an issue by the analysis that reads it; an issue whose area cannot be told from reading it has no tier 1 or 2 affinity.

The owner is decided in this order, from the signals uniformity leaves: the current user when assigned; another person when assigned; the current user when an implicit tier says so; `unknown` when a claim with no assignee says so; and no one otherwise. An issue assigned to someone else stays theirs even when the current user has implicit affinity for it.

### Uniformity

Some repositories set a signal on almost every issue. In a repository with a single maintainer, that one person files, is assigned, and claims nearly everything, so those signals tell no issue apart. Each signal kind is therefore checked across the open issues: when one owner holds it on at least 90% of them, and there are at least five, the signal is ignored for the whole repository and the ignored kinds are named. The kinds are `assigned`, `claimed`, `filed`, `commented`, `active` (tier 1), and `recent` (tier 2).

### Effect

The current user's issues get a small boost, issues owned by someone else a large penalty, and unowned issues nothing. On a backlog board, a start pick owned by someone else needs a stated reason. On a bugs board, the weights add to the rank, 5 for the current user and -30 for someone else by default.

## Data Shapes

The boards carry these objects. A gather script writes them; the analysis never edits them.

`progress`, on an issue or bug, or null when it has no stage:

| Field           | Value                                                                                                                                                 |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `stage`         | One of the stages                                                                                                                                     |
| `carrier`       | What carries it, exactly one of `{ "pr": 412 }`, `{ "branch": "feature/412-tags" }`, `{ "label": "in progress" }`, or `{ "pipeline": "In Progress" }` |
| `signal`        | The gathered signal in words, such as `pull request #412, approved, checks passing`                                                                   |
| `lastActivity`  | An ISO 8601 time                                                                                                                                      |
| `since`         | An ISO 8601 time the stage is known to have begun, or null                                                                                            |
| `nextMove`      | `author`, `reviewer`, `ci`, or `nobody`                                                                                                               |
| `nextAction`    | The next action in words                                                                                                                              |
| `flags`         | A list of flags, empty when there are none                                                                                                            |
| `host`          | The machine that saw a `local` branch, or null                                                                                                        |
| `extraCarriers` | The other carriers, in the same form as `carrier`, empty when there are none                                                                          |

`affinity`, on every open issue or bug:

| Field     | Value                                                                                           |
| --------- | ----------------------------------------------------------------------------------------------- |
| `owner`   | `you`, another person's login, `unknown` for a claim with no known owner, or null               |
| `kind`    | `explicit`, `implicit`, or null when `owner` is null                                            |
| `tier`    | 1, 2, or 3 for implicit affinity, otherwise null                                                |
| `reasons` | The signals behind it in words, such as `assigned` or `commits in src/parser/** within 30 days` |

`areas`, at the top level of a board: a list of `{ "name", "paths" }`, where `paths` are glob patterns relative to the repository root. `*` matches within one path segment, `**` across segments, and a pattern ending in `/` covers everything below it. Each issue or bug lists the names of its areas in its own `areas` field.

`affinityIgnored`, at the top level of a board: the signal kinds uniformity dropped, empty when none were.
