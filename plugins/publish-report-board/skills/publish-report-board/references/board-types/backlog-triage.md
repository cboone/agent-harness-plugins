# Backlog Triage Board

A backlog triage board answers three questions about a repository's open issues: what to start now, what can run in parallel, and what is blocked and by what. It suits a backlog worked by several branches or sessions at once, where the binding constraint is less what matters most than what can proceed without colliding.

| Setting     | Value                                                                                    |
| ----------- | ---------------------------------------------------------------------------------------- |
| Board type  | `backlog-triage`                                                                         |
| Template    | `${CLAUDE_PLUGIN_ROOT}/templates/backlog-triage.html`                                    |
| Title       | `REPO backlog`, such as `agent-harness-plugins backlog`                                  |
| Favicon     | 🗂️                                                                                       |
| Icon        | `board`                                                                                  |
| Description | `Backlog triage for OWNER/REPO: what to start, the lanes, contention, and blocked work.` |

## Gather

Run these from a checkout of the repository:

```bash
git fetch --quiet --prune origin
bash BACKLOG_GATHER gather OWNER/REPO GATHER_JSON
gh api --paginate --slurp 'repos/OWNER/REPO/milestones?state=open&per_page=100' | jq 'add'
date -u +%Y-%m-%dT%H:%M:%SZ
```

`BACKLOG_GATHER` is `backlog-gather`, found beside `report-board` the way the skill finds it. The fetch takes every branch and prunes the deleted ones, so the gather sees work pushed from another machine or session. The gather then reads, in one file:

- every open issue, with its body, labels, milestone, assignees, author, and comments;
- each issue's `progress`, derived from its branches, worktrees, open and merged pull requests, and progress labels, as `./references/progress-model.md` describes;
- what affinity needs: assignments, claim labels, who filed or commented, and the files on the current user's open branches and pull requests and in their recent commits and merged pull requests;
- the default branch, its commit, the current user, and this machine's name.

It stops rather than shrink the board when GitHub cuts a list short, and prints a summary of the stages and flags it found. The milestones call is paginated because GitHub caps a page at 100 and returns only the first one otherwise, so `--slurp` gathers the pages and `add` flattens them into a single list.

Unmerged branches are also what a branch blocker points at: a branch holding unmerged work with no pull request is often the reason an issue cannot finish. The gather reports remote branches carrying their remote, as `origin/feature`. Record a branch blocker as the branch alone, `feature`, because the page builds a compare link from it and `origin/feature` names no branch on GitHub.

Optional settings live in `${XDG_CONFIG_HOME:-$HOME/.config}/report-boards/backlog-triage/github.com/OWNER/NAME.json`:

| Setting               | Default           | Meaning                                                                                |
| --------------------- | ----------------- | -------------------------------------------------------------------------------------- |
| `progressLabels`      | `["in progress"]` | Labels that mark work started                                                          |
| `claimLabels`         | `[]`              | Labels that claim an issue for its assignees; a label cannot be in both lists          |
| `quietDays`           | `7`               | Days without activity before work is flagged `quiet`                                   |
| `staleDays`           | `30`              | Days without activity before work is flagged `stale`; more than `quietDays`            |
| `affinityWorkDays`    | `30`              | How far back the current user's commits and merged pull requests count toward affinity |
| `affinityCommentDays` | `90`              | How far back the current user's comments count toward affinity                         |
| `uniformityShare`     | `0.9`             | The share of open issues one owner may hold a signal on before that signal is ignored  |
| `uniformityMinimum`   | `5`               | The fewest open issues for which uniformity applies                                    |

## Analyze

Work through these steps in order; each one uses the results of the one before.

### 1. Work in Progress

The gather has already decided it. Read each issue's `progress` from the gather to know what is in progress, at which stage, and whose move it is, and never write or change it: a status no gathered signal supports, such as a long-running routine or a plan to start soon, is not progress. When something outside the repository gates such an issue, record it as a blocker in the next step; otherwise leave it out. An issue in `close-out` has merged work and is still open, so it holds no lane slot and is a cleanup rather than a candidate to start.

### 2. Dependencies

Scan each body for references to other open issues, such as "blocked by #N", "depends on #N", "after #N", or "needs #N", and confirm that each is an ordering constraint rather than a passing mention. Record it as `waitingOn`, with `blockedBecause` saying what the blocker settles.

An issue can also wait on something that is not an open issue on this board: a pull request, a branch that has to merge, an issue in another repository, or anything else with a URL. Record each as a reference, as [References](#references) describes, rather than in a lane note, so the board counts the issue as blocked and links to what it waits on. Drop blockers that have closed or merged: a finished blocker is no longer a reason.

Some constraints are soft: an issue could start now, but starting it before another open issue lands would repeat work or force a rebase. Record those in `after` rather than `waitingOn`. It takes the same forms, so the thing to wait for can also be a pull request, a branch, or another repository's issue. The board shows the relation, counts the issue as queued rather than blocked, and never picks it to start now. Within a serial lane the listed order already says this, so `after` earns its place mostly across lanes.

### 3. Areas and Contention

For each issue, work out what it will edit: plugins, packages, directories, or shared files, from the paths and names in its body. Record each component as an area in the top-level `areas` list, with a `name` and the `paths` it covers as glob patterns relative to the repository root, such as `{ "name": "parser", "paths": ["src/parser/**"] }`, and list the names of an issue's areas in its own `areas` field. Leave an issue without areas when its body does not say what it edits, and leave out files that nearly every change touches trivially, such as a changelog or a version tag; mention those in a lane note instead.

An area that two or more issues list is a claim, and each claim is a rebase waiting to happen. `backlog-gather finish` derives `contention.claims` from the areas, so do not write the claims yourself; set `contention.rowLabel` to what the components are, such as `Plugin` or `Package`, and give an area a `query` to override the issue search its claim links to. The areas also decide part of each issue's affinity: an area covering files the current user is changing or recently changed marks the issue as theirs.

### 4. Lanes

Group the issues into lanes so that two issues in different lanes never edit the same component. Start from the claims: issues linked through shared components belong together. Every open issue goes in exactly one lane, including issues without a milestone and issues in progress, and validation rejects a board that leaves one out.

Give each lane a mode:

| Mode     | Meaning                                                                  | Use when                                                                     |
| -------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| `serial` | One branch at a time: the first issue in the listed order that can start | Every issue edits something another issue in the lane also edits             |
| `head`   | The first issue alone, then everything it frees at once                  | One issue settles something the rest read, and after it they are independent |
| `any`    | Every issue that can start at once, so blocked and queued work waits     | Nothing in the lane shares a component                                       |

In a serial lane the listed order is the recommended sequence, with an issue already in progress first; an issue that cannot start yet is passed over for the next one that can. In a head lane the head comes first, and while it cannot start, nothing else in the lane does. In either, work already in progress holds the lane's single slot, including work on an issue riding another's branch. When more than one branch in such a lane is already in progress, the page shows each one running, so the overlap stays visible. In an any-order lane the order is only for reading.

When two issues should ship on one branch, usually because neither makes sense without the other, set `sameBranchAs` on one of them to the other. Both must sit in the same lane, and the page draws them as one unit.

Give each lane a short `key` (`L1`, `L2`, and so on), a `name` a reader recognizes, `owns` listing what it edits, and a `note` saying why its order is what it is.

### 5. Start Now

Pick the branches to open today: at most one per serial or head lane, and never an issue that is blocked, in progress, in `close-out`, better after another open issue, or riding on another issue's branch. A serial or head lane whose single slot is held by an issue in progress gets no pick, and otherwise its pick is the issue the page runs there: a head lane's head, or a serial lane's first issue that can start. Prefer issues that unblock others, carry the most risk while they stay open, or head a contended lane, and use the signals the `suggest-next-issue` skill weighs to break ties: priority labels, dependencies, age from `createdAt`, recent activity from `updatedAt`, and affinity, which favors the current user's issues a little and counts heavily against issues someone else owns. Order the picks by value, and give each a `why` and a `touches` naming what it edits. A pick owned by someone else needs `despiteOwner`, saying why it is worth starting anyway.

How many branches to start is a judgment, not a maximum. The header already shows how many could run at once; the picks say how many are worth starting. When the two differ, say why in `notes.startNow`.

### 6. Prose

Write `summary`, each lane's `note`, each `blockedBecause`, and any section notes following `./references/design-conventions.md`.

### 7. Finish

Write the analysis to `ANALYSIS_JSON`, then let the gather add what it derived:

```bash
bash BACKLOG_GATHER finish GATHER_JSON ANALYSIS_JSON DATA_JSON
```

It adds each issue's `progress` and `affinity`, the claims derived from the areas, `affinityIgnored`, and `schemaVersion`. It refuses analysis data that writes any of those itself, names an area it does not define, or covers a different set of open issues than the gather, and lists every problem at once. `DATA_JSON` is what the skill validates and renders.

## Data

### Top Level

| Field             | Required | Contents                                                                                                                   |
| ----------------- | -------- | -------------------------------------------------------------------------------------------------------------------------- |
| `board`           | Yes      | `backlog-triage`                                                                                                           |
| `schemaVersion`   | Finish   | `2`                                                                                                                        |
| `title`           | Yes      | The board's name, identical across syncs                                                                                   |
| `repo`            | Yes      | `OWNER/NAME`                                                                                                               |
| `repoUrl`         | No       | The repository URL, when it is not on github.com, with no query or fragment                                                |
| `sync`            | Yes      | Sync metadata, as `./references/sync-metadata.md` describes                                                                |
| `summary`         | Yes      | One or two sentences                                                                                                       |
| `milestones`      | No       | `{ "title", "short" }` per milestone, in the order the contention matrix lists them; `short` labels the matrix column      |
| `issues`          | Yes      | Every open issue                                                                                                           |
| `lanes`           | Yes      | Every lane                                                                                                                 |
| `startNow`        | Yes      | The picks, as a list that may be empty                                                                                     |
| `areas`           | No       | `{ "name", "paths", "query" }` per area, as [Areas and Contention](#3-areas-and-contention) describes; `query` is optional |
| `contention`      | No       | `{ "rowLabel", "claims" }`; finish derives each claim, `{ "name", "issues", "query" }`, from the areas                     |
| `affinityIgnored` | Finish   | The signal kinds uniformity dropped, as `./references/progress-model.md` describes                                         |
| `notes`           | No       | Text for `startNow`, `blocked`, or `contention`, replacing the note the page would otherwise derive                        |

Rows marked Finish are written by `backlog-gather finish`, never by the analysis; the progress and affinity shapes are in `./references/progress-model.md`.

### Issues

| Field            | Required         | Contents                                                                                         |
| ---------------- | ---------------- | ------------------------------------------------------------------------------------------------ |
| `number`         | Yes              | The issue number                                                                                 |
| `title`          | Yes              | The GitHub title, verbatim                                                                       |
| `milestone`      | Yes              | The milestone title verbatim, or `null`                                                          |
| `short`          | No               | A shorter title for the start and blocked lists, such as one without a prefix                    |
| `waitingOn`      | No               | What this one waits on: issue numbers on this board, or [references](#references)                |
| `blockedBecause` | With `waitingOn` | Why it cannot start yet                                                                          |
| `sameBranchAs`   | No               | The issue whose branch this one ships on                                                         |
| `after`          | No               | What this one is better started after: issue numbers on this board, or [references](#references) |
| `areas`          | No               | The names of the areas this issue edits                                                          |
| `progress`       | Finish           | The issue's stage, carrier, flags, and next move, or `null`                                      |
| `affinity`       | Finish           | Who the issue already belongs to, and why                                                        |

### References

Each `waitingOn` or `after` entry is an open issue number on this board, or an object naming exactly one of these:

| Form                                       | Waits on                                       | Links to                                   |
| ------------------------------------------ | ---------------------------------------------- | ------------------------------------------ |
| `{ "pr": 390 }`                            | A pull request in this repository              | The pull request                           |
| `{ "branch": "fix/remove-floating-tags" }` | A branch in this repository that has to merge  | The branch compared with the synced branch |
| `{ "ref": "OWNER/REPO#17" }`               | An issue or pull request in another repository | That issue or pull request                 |
| `{ "url": "https://…", "label": "…" }`     | Anything else                                  | The URL, under the label                   |

Any form may add a `title`, which the Blocked section shows beside the link, and a `url` reference carries its required `label` as well. That section's "Freed from" column names the lane for an issue on the board, and the kind of reference otherwise. In `after`, the same forms name what an issue is better started after, and its lane row links each one.

### Lanes and Picks

| Field                     | Required      | Contents                                |
| ------------------------- | ------------- | --------------------------------------- |
| `lanes[].key`             | Yes           | A short, unique key such as `L1`        |
| `lanes[].name`            | Yes           | A name a reader recognizes              |
| `lanes[].mode`            | Yes           | `serial`, `head`, or `any`              |
| `lanes[].issues`          | Yes           | The lane's issue numbers, in order      |
| `lanes[].owns`            | No            | What the lane edits                     |
| `lanes[].note`            | No            | Why the lane's order is what it is      |
| `startNow[].issue`        | Yes           | The issue to start                      |
| `startNow[].why`          | Yes           | One or two sentences of reasons         |
| `startNow[].touches`      | No            | What it edits                           |
| `startNow[].despiteOwner` | With an owner | Why to start an issue someone else owns |

## What the Page Draws

| Section           | Shows                                                                         | Derived by the page                                                                                                                                   |
| ----------------- | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Header            | Repository, sync time, live age, six counts, the stage strip, and the summary | Picks, as the filled block; ready (open minus blocked), blocked, lanes, branches at once, and open; a count per stage                                 |
| In flight         | Every issue with progress, grouped by stage                                   | The order of stages; each row's carrier link, next action, flags, and activity age                                                                    |
| Start now         | Each pick with its reasons, lane, footprint, milestone, and owner             | The issues that share its branch                                                                                                                      |
| Lanes             | A bar per lane with one segment per issue, then each lane in detail           | Capacity from the mode; which segments can run now; stage tags and flags; "waits on", "unblocks", "better after", "eases", and "same branch as" links |
| Contention matrix | Claimed components down the side, milestones across                           | The columns, from the milestones of the claiming issues; the counts in the note                                                                       |
| Blocked           | Each blocked issue, what it waits on, why, and what frees it                  | The order, fewest blockers first; the freeing lane, or the kind of reference                                                                          |
| Footer            | The sync line and counts                                                      | The milestone count, and any signal kinds uniformity ignored                                                                                          |

In flight, Start now, and Lanes sit above a double rule labeled Report; the contention matrix and Blocked sit below it, as reference material.

Capacity follows the lane's mode: one branch at a time for a serial or head lane, and every unblocked issue at once for an any-order lane. A serial lane runs its first issue that can start, and a head lane only its head, so a head that cannot start holds its whole lane at zero. A head lane also shows how many issues its head frees. It shows that count while the head is running, whether the head is the pick or its branch is already in progress, and zero when the head is not running at all. What it counts is every issue in the lane that the head releases, and the lane itself is what holds the rest back until the head lands: an issue with no blockers of its own is therefore counted, while one that also waits on something outside the head's branch is not, because the head landing does not free it. A branch already in progress beside the head is running now rather than waiting on the head, so it is not counted. A rider kept back by a blocker of its own frees nothing either. "Branches at once" in the header is the sum across lanes. A branch carrying an issue that is better after another open issue counts as queued rather than runnable, so it adds nothing to capacity until its target lands, unless its work has already started.

When no open issue has a milestone, the page drops the milestone column and chips, heads the contention matrix's single column "Claimed by", and says so in the footer rather than counting zero milestones.

When nothing is blocked, the Blocked section shrinks to its heading and the words "Nothing is blocked." An empty `startNow` shrinks the Start now section the same way, to a line saying whether anything could have started. `notes.blocked` and `notes.startNow` replace either line when set.

## Validation

`report-board validate` rejects data that breaks any of these rules, and lists every problem at once:

- Every open issue sits in exactly one lane, and lanes list only issues on the board.
- `waitingOn` lists open issues on the board, never the issue itself, or well-formed references, and always comes with `blockedBecause`.
- `after` lists open issues on the board or well-formed references, never the issue itself, never an issue it already waits on or shares a branch with, and never forms a loop.
- `sameBranchAs` names an issue in the same lane that does not itself ship on another branch.
- A start pick is on the board, and is not blocked, not in progress (counting work on an issue riding its branch), not better after another open issue, and not riding on another issue's branch; nothing riding on its own branch is better after another open issue either. A pick owned by someone else carries `despiteOwner`.
- `schemaVersion` is 2. Each issue's `progress` and `affinity` take the shapes in `./references/progress-model.md`, every area an issue names is defined, and the claims are the ones the areas derive.
- A serial or head lane gets at most one pick, none while work in progress holds its slot, and only the issue the page runs there: a head lane's head, or a serial lane's first issue that can start.
- `sync.at` falls on a real calendar date, `sync.commit` is a full SHA, and `sync.timeZone`, when set, is a zone the time zone database has, wherever one is installed.
- Required fields are present and well formed, including each issue's `milestone`, which is `null` when it has none. Issue numbers, lane keys, and claim names are unique, and every `mode` is `serial`, `head`, or `any`.

## Example

The smallest useful analysis: one serial lane with a blocker, and one any-order lane holding an issue the gather found in progress. `backlog-gather finish` adds `progress`, `affinity`, the claims, `affinityIgnored`, and `schemaVersion`.

```json
{
  "board": "backlog-triage",
  "title": "widgets backlog",
  "repo": "example/widgets",
  "sync": {
    "at": "2026-09-01T13:30:00Z",
    "timeZone": "America/New_York",
    "branch": "main",
    "commit": "0123456789abcdef0123456789abcdef01234567",
    "openPullRequests": 1
  },
  "summary": "Two lanes can run at once. The tokenizer rewrite gates the parser lane, so start there.",
  "issues": [
    { "number": 101, "title": "parser: replace the tokenizer", "milestone": "Parser rewrite", "areas": ["parser"] },
    {
      "number": 102,
      "title": "parser: stream large inputs",
      "milestone": "Parser rewrite",
      "areas": ["parser"],
      "waitingOn": [101],
      "blockedBecause": "Streaming reads the token format that #101 replaces."
    },
    { "number": 106, "title": "ci: cache dependencies", "milestone": null, "areas": ["ci"] }
  ],
  "startNow": [{ "issue": 101, "why": "Frees #102, and nothing outside the parser touches it.", "touches": "parser" }],
  "lanes": [
    {
      "key": "L1",
      "name": "Parser core",
      "owns": "parser",
      "mode": "serial",
      "note": "Both issues edit the tokenizer.",
      "issues": [101, 102]
    },
    { "key": "L2", "name": "Standalone", "mode": "any", "issues": [106] }
  ],
  "areas": [
    { "name": "parser", "paths": ["src/parser/**"] },
    { "name": "ci", "paths": [".github/workflows/"] }
  ],
  "contention": { "rowLabel": "Package" }
}
```
