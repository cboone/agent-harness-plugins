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

```bash
gh repo view --json nameWithOwner,url,defaultBranchRef
git fetch --quiet origin DEFAULT_BRANCH
git rev-parse origin/DEFAULT_BRANCH
gh issue list --state open --limit 500 --json number,title,body,labels,milestone,assignees
gh api 'repos/OWNER/REPO/milestones?state=open&per_page=100'
gh pr list --state open --json number,title,headRefName,closingIssuesReferences
git worktree list
git branch --list --format='%(refname:short)'
gh api user --jq '.login'
date -u +%Y-%m-%dT%H:%M:%SZ
```

Every open issue goes on the board. If the issue list returns exactly as many issues as `--limit` allows, raise the limit and run it again rather than working from a truncated backlog.

## Analyze

Work through these steps in order; each one uses the results of the one before.

### 1. Work in Progress

Detect it the way the `suggest-next-issue` skill does. An issue is in progress when a branch or worktree name contains its number, when it carries an "in progress" label, or when it is assigned to the current user. An open pull request that closes it also counts. Set `inProgress` to what carries the work, such as a branch name or `PR #390`.

### 2. Dependencies

Scan each body for references to other open issues, such as "blocked by #N", "depends on #N", "after #N", or "needs #N", and confirm that each is an ordering constraint rather than a passing mention. Record it as `waitingOn`, with `blockedBecause` saying what the blocker settles. Drop blockers that have closed: a closed blocker is no longer a reason.

### 3. Footprints and Contention

For each issue, work out what it will edit: plugins, packages, directories, or shared files, from the paths and names in its body. A component that two or more issues will edit is a claim, and each claim is a rebase waiting to happen.

List the claims under `contention.claims`, each naming the component and the issues that claim it, and set `contention.rowLabel` to what the components are, such as `Plugin` or `Package`. Leave out components only one issue claims, and files that nearly every change touches trivially, such as a changelog or a version tag; mention those in a lane note instead.

### 4. Lanes

Group the issues into lanes so that two issues in different lanes never edit the same component. Start from the claims: issues linked through shared components belong together. Every open issue goes in exactly one lane, including issues without a milestone and issues in progress, and validation rejects a board that leaves one out.

Give each lane a mode:

| Mode     | Meaning                                                 | Use when                                                                     |
| -------- | ------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `serial` | One branch at a time, in the listed order               | Every issue edits something another issue in the lane also edits             |
| `head`   | The first issue alone, then everything it frees at once | One issue settles something the rest read, and after it they are independent |
| `any`    | Every unblocked issue at once                           | Nothing in the lane shares a component                                       |

In a serial lane the listed order is the recommended sequence, with an issue already in progress first. In a head lane the head comes first. In an any-order lane the order is only for reading.

When two issues should ship on one branch, usually because neither makes sense without the other, set `sameBranchAs` on one of them to the other. Both must sit in the same lane, and the page draws them as one unit.

Give each lane a short `key` (`L1`, `L2`, and so on), a `name` a reader recognizes, `owns` listing what it edits, and a `note` saying why its order is what it is.

### 5. Start Now

Pick the branches to open today: at most one per serial or head lane, and never an issue that is blocked, in progress, or riding on another issue's branch. A serial or head lane whose single slot is held by an issue in progress gets no pick. Prefer issues that unblock others, carry the most risk while they stay open, or head a contended lane, and use the signals the `suggest-next-issue` skill weighs (priority labels, dependencies, age, activity) to break ties. Order the picks by value, and give each a `why` and a `touches` naming what it edits.

Staffing is a judgment, not a maximum. The header already shows how many branches could run at once; the picks say how many are worth running. When the two differ, say why in `notes.startNow`.

### 6. Prose

Write `summary`, each lane's `note`, each `blockedBecause`, and any section notes following `./references/design-conventions.md`.

## Data

### Top Level

| Field        | Required | Contents                                                                                                                            |
| ------------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `board`      | Yes      | `backlog-triage`                                                                                                                    |
| `title`      | Yes      | The board's name, identical across syncs                                                                                            |
| `repo`       | Yes      | `OWNER/NAME`                                                                                                                        |
| `repoUrl`    | No       | The repository URL, when it is not on github.com                                                                                    |
| `sync`       | Yes      | Sync metadata, as `./references/sync-metadata.md` describes                                                                         |
| `summary`    | Yes      | One or two sentences                                                                                                                |
| `milestones` | No       | `{ "title", "short" }` per milestone, in the order the contention matrix lists them; `short` labels the matrix column               |
| `issues`     | Yes      | Every open issue                                                                                                                    |
| `lanes`      | Yes      | Every lane                                                                                                                          |
| `startNow`   | Yes      | The picks, as a list that may be empty                                                                                              |
| `contention` | No       | `{ "rowLabel", "claims" }`; each claim is `{ "name", "issues", "query" }`, and `query` overrides the issue search its name links to |
| `notes`      | No       | Text for `startNow`, `blocked`, or `contention`, replacing the note the page would otherwise derive                                 |

### Issues

| Field            | Required         | Contents                                                                      |
| ---------------- | ---------------- | ----------------------------------------------------------------------------- |
| `number`         | Yes              | The issue number                                                              |
| `title`          | Yes              | The GitHub title, verbatim                                                    |
| `milestone`      | Yes              | The milestone title verbatim, or `null`                                       |
| `short`          | No               | A shorter title for the start and blocked lists, such as one without a prefix |
| `waitingOn`      | No               | The open issues this one waits on                                             |
| `blockedBecause` | With `waitingOn` | Why it cannot start yet                                                       |
| `sameBranchAs`   | No               | The issue whose branch this one ships on                                      |
| `inProgress`     | No               | The branch or pull request carrying the work                                  |

### Lanes and Picks

| Field                | Required | Contents                           |
| -------------------- | -------- | ---------------------------------- |
| `lanes[].key`        | Yes      | A short, unique key such as `L1`   |
| `lanes[].name`       | Yes      | A name a reader recognizes         |
| `lanes[].mode`       | Yes      | `serial`, `head`, or `any`         |
| `lanes[].issues`     | Yes      | The lane's issue numbers, in order |
| `lanes[].owns`       | No       | What the lane edits                |
| `lanes[].note`       | No       | Why the lane's order is what it is |
| `startNow[].issue`   | Yes      | The issue to start                 |
| `startNow[].why`     | Yes      | One or two sentences of reasons    |
| `startNow[].touches` | No       | What it edits                      |

## What the Page Draws

| Section           | Shows                                                               | Derived by the page                                                                                    |
| ----------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Header            | Repository, sync time, live age, and six counts                     | Open, ready (open minus blocked), blocked, lanes, branches at once, and picks                          |
| Summary           | `summary`                                                           | Nothing                                                                                                |
| Start now         | Each pick with its reasons, lane, footprint, and milestone          | The issues that share its branch                                                                       |
| Lanes             | A bar per lane with one segment per issue, then each lane in detail | Capacity from the mode; which segments can run now; "waits on", "unblocks", and "same branch as" links |
| Contention matrix | Claimed components down the side, milestones across                 | The columns, from the milestones of the claiming issues; the counts in the note                        |
| Blocked           | Each blocked issue, what it waits on, why, and which lanes free it  | The order, fewest blockers first; the freeing lanes                                                    |
| Footer            | The sync line and counts                                            | The milestone count                                                                                    |

Capacity follows the lane's mode: one branch at a time for a serial or head lane, and every unblocked issue at once for an any-order lane. A head lane also shows how many issues its head frees. "Branches at once" in the header is the sum across lanes.

## Validation

`report-board validate` rejects data that breaks any of these rules, and lists every problem at once:

- Every open issue sits in exactly one lane, and lanes list only issues on the board.
- `waitingOn` names only issues on the board, never the issue itself, and always comes with `blockedBecause`.
- `sameBranchAs` names an issue in the same lane that does not itself ship on another branch.
- A start pick is on the board, and is not blocked, not in progress, and not riding on another issue's branch.
- Required fields are present and well formed, issue numbers and lane keys are unique, and every `mode` is `serial`, `head`, or `any`.

## Example

The smallest useful board: one serial lane with a blocker, and one any-order lane holding an issue in progress.

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
    { "number": 101, "title": "parser: replace the tokenizer", "milestone": "Parser rewrite" },
    {
      "number": 102,
      "title": "parser: stream large inputs",
      "milestone": "Parser rewrite",
      "waitingOn": [101],
      "blockedBecause": "Streaming reads the token format that #101 replaces."
    },
    { "number": 106, "title": "ci: cache dependencies", "milestone": null, "inProgress": "feature/106-cache" }
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
  "contention": { "rowLabel": "Package", "claims": [{ "name": "parser", "issues": [101, 102] }] }
}
```
