# Bugs Board

A bugs board answers what to do about one repository's open bugs: which ones are hurting people on production and need action now, which need doing or confirming today, which are ready to land or fix, and how the rest are triaged. It puts action first and report second: above the fold, a card per urgent bug with its next action; below it, what needs investigating, what can wait, what was recently fixed, and what is parked.

Trackers rarely say how bad a bug is. Severity labels go unused, and many bugs are found by reading code rather than reported by users, so whether a bug is on production, who it reaches, and how it is known must be read from its body and comments. That reading is the core of the analysis, and the persistent cache keeps it from being repeated: a later sync, in any conversation, reads only the bugs that changed.

It draws on three sources: GitHub, ZenHub when the repository has a workspace, and the user's triage note. Error trackers, logs, and deploy state are out of scope; a bug seen on production counts as seen when its issue or a comment says so.

| Setting     | Value                                                                                       |
| ----------- | ------------------------------------------------------------------------------------------- |
| Board type  | `bugs`                                                                                      |
| Template    | `${CLAUDE_PLUGIN_ROOT}/templates/bugs.html`                                                 |
| Title       | `REPO bugs`, such as `votefwd bugs`                                                         |
| Favicon     | 🐞                                                                                          |
| Icon        | `bug`                                                                                       |
| Description | `Bug board for OWNER/REPO: what to fix now, what to do today, and how the rest is triaged.` |
| Script      | `bugs-gather`, beside `report-board`, invoked the same way and written `BUGS_GATHER`        |

## Scope

Open issues in the repository that are bugs: those carrying a label in `bugLabels`, or an issue type in `bugTypes`. The pull requests that close them come along, for their draft, check, and review state, and so do bugs closed within `recentDays`, for Recently fixed. ZenHub containers are counted as parked, never ranked.

## Repository Config

Optional. Pass `bugs-gather` the repository as `OWNER/NAME`, and it reads a config, when one exists, from `${XDG_CONFIG_HOME:-$HOME/.config}/report-boards/bugs/github.com/OWNER/NAME.json`; or pass the path of a config file whose `repo` names the repository. Without a config, the defaults below apply and there is no triage note. Before the first check-in that records an entry, ask the user where the note should live, and write the config with the Write tool.

| Field               | Default                                 | Contents                                                                                                                              |
| ------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `repo`              | The argument                            | `OWNER/NAME`; required in a config passed by path                                                                                     |
| `timeZone`          | `UTC`                                   | An IANA zone; triage `until` dates and assessment deadlines count in its local days                                                   |
| `bugLabels`         | `["bug"]`                               | Labels that mark a bug; a bug needs any one of them                                                                                   |
| `bugTypes`          | `["Bug"]`                               | GitHub issue types that mark a bug                                                                                                    |
| `urgentLabels`      | `[]`                                    | Labels that add rank weight, such as `high-priority`; they place nothing                                                              |
| `urgentPipelines`   | `[]`                                    | ZenHub pipelines that add the same weight                                                                                             |
| `regressionLabels`  | `["regression"]`                        | Labels that mark a regression, which adds weight                                                                                      |
| `parkLabels`        | `["wontfix", "won't fix", "duplicate"]` | Labels that park a bug                                                                                                                |
| `progressLabels`    | `["in progress"]`                       | Labels that mark work in progress                                                                                                     |
| `progressPipelines` | `["In Progress", "Review/QA"]`          | ZenHub pipelines that mark work in progress                                                                                           |
| `containerLevels`   | `[1, 2, 3]`                             | ZenHub issue-type levels that count as containers                                                                                     |
| `bots`              | `[]`                                    | Logins whose comments never count as people; logins ending in `[bot]` never do either                                                 |
| `recentDays`        | `7`                                     | How far back Recently fixed reaches                                                                                                   |
| `nowWarn`           | `5`                                     | A Now count above this carries a warning on the page                                                                                  |
| `readyLimit`        | `8`                                     | How many Ready to go rows sit above the fold; the rest go to the report                                                               |
| `deadlineDays`      | `14`                                    | How close an assessment deadline must be to place a bug in Today                                                                      |
| `weights`           | Documented in `bugs-gather`             | Rank weights, grouped as the defaults are; a config overrides any one, such as `{"pipelines": {"Must Do": 10}}`                       |
| `zenhub`            | None                                    | `workspace` (the ID) and `tokenVariable` (the name of the environment variable holding the token); without it, ZenHub is never called |
| `triageNote`        | None                                    | The path to the triage note; a leading `~/` means the home directory                                                                  |
| `triageGit`         | None                                    | `{ "gitDir", "workTree" }` when the note is committed to a repository with no `.git` directory in its worktree                        |

The ZenHub token stays in its environment variable. `bugs-gather` writes the authorization header to a file only its owner can read, so the token never reaches a command line.

## The Triage Note

The note is the user's input and a source of truth of its own; the board renders it and never becomes it. It is Markdown whose list items are entries in a fixed grammar. Other lines are prose and are ignored.

```markdown
- 2026-10-14T09:00-04:00 escalate #4579: every pledge since the deploy has failed
- 2026-10-14T09:05-04:00 set #4441 environment=production evidence=user-report: a partner reported the missing campaign
- 2026-10-14T09:10-04:00 snooze #4061 until 2026-11-10: PDF size waits until after the election
- 2026-10-14T09:10-04:00 park #4199: the workflow is being replaced
- 2026-10-13T08:00-04:00 context: the send window opens 2026-10-20
```

| Verb       | Effect                                                                                                                                                        | `until`  |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| `escalate` | Places the bug in Now                                                                                                                                         | Optional |
| `set`      | Overrides assessment fields, written `key=value` before the colon; the keys are the assessment fields below, and `timeSensitive`, `mitigated`, and `deadline` | Never    |
| `snooze`   | Parks the bug through its date                                                                                                                                | Required |
| `park`     | Parks the bug until the note changes, such as a decision not to fix it                                                                                        | Never    |
| `context`  | Free text the analysis reads when it writes actions and the summary; it names no bug                                                                          | Never    |

Every timestamp carries an explicit offset. An `until` date is inclusive in the config's `timeZone`: the entry expires at the start of the following local day. Among a bug's `escalate`, `snooze`, and `park` entries still in force, the latest decides. A `set` entry wins over the assessment for the fields it names, and the page marks each one, so the user sees which calls are theirs. An entry's ID is its timestamp, verb, and target, such as `2026-10-14T09:00-04:00 escalate #4579`, or its timestamp and `context`.

## Sync

### 1. Gather

```bash
bash BUGS_GATHER gather REPO GATHER_JSON
```

It runs the open and recently closed searches, by label and by issue type, in parallel, reads the ZenHub state of every open bug and the workspace's active sprint in one aliased query, and writes one normalized file. Then it prints what moved since the cached gather, or says the sync is a cold one. An archived repository stops the gather.

### 2. Read What Changed

```bash
bash BUGS_GATHER reuse REPO GATHER_JSON ASSESSMENTS_JSON
```

It writes to `ASSESSMENTS_JSON` the cached assessments whose bug has not changed since it was read, and lists the open bugs that need reading. Read each one's body and every comment, read-only, and add its assessment to the list in `ASSESSMENTS_JSON` with the Write tool. When more than a handful need reading, read them in parallel with subagents, about ten bugs each, giving each the instructions below and the exact shape to return.

#### Assessment

Judge from what the issue and its comments say, never from a bug's plausibility; an unknown is information the board shows. Use `unknown` whenever the issue does not say.

| Field           | Values                                                                                                                                                                                                                                                                       |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `number`        | The issue number                                                                                                                                                                                                                                                             |
| `updatedAt`     | The issue's `updatedAt`, exactly as GitHub returns it; `score` refuses an assessment of an older version                                                                                                                                                                     |
| `environment`   | Where it is known to occur: `production` only when the issue says it happens, or would happen, on the live service with the deployed code; `staging`; `development` for local, CI, and tests; `unknown`                                                                      |
| `evidence`      | How it is known, the strongest that applies: `user-report` (a real user or support contact), `production-observed` (logs, alerts, or a maintainer saw it live), `reproduced`, `code-reading` (found by reading source), `unknown`                                            |
| `surface`       | Who would see it: `public` (anyone, signed out), `signed-in` (ordinary signed-in users), `admin` (staff tools), `internal` (only maintainers: CI, tests, logs, ops scripts, alerts), `unknown`                                                                               |
| `impact`        | The worst consequence: `security`, `data-loss` (lost, corrupted, or persistently wrong data), `money` (donations, pledges, payments), `access` (login, sign-out, or wrongly allowed in), `core-flow` (a main user task fails), `degraded`, `cosmetic`, `internal`, `unknown` |
| `reach`         | How many of the affected surface's users hit it: `all`, `many`, `some`, `few`, `unknown`                                                                                                                                                                                     |
| `workaround`    | `none`, `exists` (the issue names one, or users can retry or take another path), `unknown`                                                                                                                                                                                   |
| `cause`         | `known` (the issue names the faulty code or condition), `suspected`, `unknown`                                                                                                                                                                                               |
| `timeSensitive` | `true` only when waiting makes it worse: a dated deadline, damage accruing with every event, or reports increasing                                                                                                                                                           |
| `deadline`      | The date, `YYYY-MM-DD`, after which waiting makes it worse, such as an election day, or `null`                                                                                                                                                                               |
| `mitigated`     | `true` when the harm has already been stopped, such as by a configuration change, while the code fix remains open                                                                                                                                                            |
| `reproduced`    | `true` or `false` when the issue reports an attempt to reproduce it, otherwise `null`                                                                                                                                                                                        |
| `gist`          | One sentence on what is wrong                                                                                                                                                                                                                                                |
| `nextStep`      | One sentence on the next concrete action, imperative                                                                                                                                                                                                                         |
| `question`      | When any of `environment`, `surface`, `impact`, or `cause` is `unknown`, or `cause` is `suspected`, the most useful thing to learn first, as a question; otherwise `null`                                                                                                    |

### 3. Score

```bash
bash BUGS_GATHER score REPO GATHER_JSON ASSESSMENTS_JSON SCORED_JSON
```

It refuses assessments that miss an open bug, describe an older version of one, or fall outside the closed sets, and lists every problem at once. Otherwise it applies the triage note, places every open bug in one tier, ranks each tier by a weighted urgency score, and prints the report the check-in shows: the triage entries and any expired or malformed ones, Now and Today with why each is there, the top of Ready to go, the report counts, and on a warm cache what entered or left Now and Today.

| Tier            | Rule, applied in this order                                                                                                                                                                                                                                                                                                                                                                          |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `now`, `parked` | The latest `escalate`, `snooze`, or `park` entry in force decides first: `escalate` places Now, and the other two place Parked. Then a `parkLabels` label or a container places Parked                                                                                                                                                                                                               |
| `now`           | Unless `mitigated`: confirmed on production (evidence of `user-report`, `production-observed`, or `reproduced`) for `public` or `signed-in` users, with a `security`, `data-loss`, `money`, `access`, or `core-flow` impact and no workaround; or a `security` impact on a `public` surface in production or an unknown environment, on evidence from reading code or stronger                       |
| `today`         | Unless `mitigated`: confirmed on production for `public` or `signed-in` users reaching `some` or more, or with no workaround; a Now-level impact on those surfaces known only from source or not yet placed in an environment, with evidence other than `unknown`, to confirm on production, unless its deadline lies beyond the window; undated `timeSensitive`; a `deadline` within `deadlineDays` |
| `ready`         | In progress, through a fix pull request, a progress label, or a progress pipeline; `mitigated`; a `security` impact on an `internal` surface                                                                                                                                                                                                                                                         |
| `later`         | An `internal` surface, or a `cosmetic` impact                                                                                                                                                                                                                                                                                                                                                        |
| `investigate`   | Any of `environment`, `surface`, `impact`, or `cause` is `unknown`; `cause` is `suspected`; or reproduction failed                                                                                                                                                                                                                                                                                   |
| `ready`         | Everything else: the cause is known, so the bug is ready to fix                                                                                                                                                                                                                                                                                                                                      |
| `fixed`         | Closed within `recentDays`; one that was on production carries a reminder to verify the fix there                                                                                                                                                                                                                                                                                                    |

Urgency labels, urgent pipelines, sprints, regressions, outside reporters, and reactions add rank weight but place nothing. A bug in Now or Today keeps its tier when it also has a fix pull request, and shows the pull request's state: urgency wins over readiness. Ready to go groups its bugs as `ship` (an open, ready, approved, and green fix), `review` (any other open, ready fix), `in-progress`, and `ready-to-fix`.

### 4. Check In

Show the user the score report. Offer to remove expired entries and report any malformed ones. Then ask, with a structured question tool when the session offers one, and otherwise as numbered options in plain text: are the Now and Today calls right, and is any bug confirmed on production, already fixed, or not worth fixing? Wait for the answer. Skip the questions when the invoking message already states the calls.

When nothing moved, no bug needed reading, and the user has nothing to add, say so and stop: the board is current, and a republish would only move its sync time.

Record each answer as a triage entry, with the current time and its offset from `date +%Y-%m-%dT%H:%M%z`, written as `-04:00` rather than `-0400`. Edit the note with the Write or Edit tool, creating its directory on first use, then commit it:

1. Before editing, check that the note has no changes the user has not committed, in the worktree or the index. With `triageGit`, pass `--git-dir` and `--work-tree` to every git command, because plain `git` fails in a worktree with no `.git` directory. If there are such changes, stop rather than fold them into this commit.
2. Stage the note by its exact path: `git add -- PATH`.
3. Commit only that path, signed, naming the change: `git commit -S -m "docs: escalate votefwd#4579 on the bug board" -- PATH`. The pathspec keeps any other staged work out of the commit.
4. Never push; pushing stays with the user.

If the host blocks the edit or the commit, stop before scoring again and report the blocked command and the restriction. Otherwise run `score` again, which takes a fraction of a second, and use its output from here on. The new entries are later than the gather, so the score counts the note as of its own time, which becomes the board's `sync.at`.

### 5. Draft and Write the Prose

```bash
bash BUGS_GATHER draft REPO GATHER_JSON SCORED_JSON DATA_JSON
```

It writes board data with every placement, signal, fact, and link already filled in from the score. Write the prose into it with the Write or Edit tool:

- **`summary`**: one or two sentences naming what to do first and the one constraint that shapes today.
- **`action`**, for each Now and Today entry: the next concrete step, imperative, such as "Roll back the 2026-10-05 deploy, or ship the `.first()` fix with a stubbed SES test." It starts as the assessment's next step; sharpen it with the triage `context` entries and what the other bugs say.
- **`impact`**, for each Now and Today entry: who is affected and how, in one sentence, with numbers when the issue has them.
- **`question`**, for each Investigate entry: it starts as the assessment's question; keep it or sharpen it.

No section is filled for its own sake. A section with nothing that earns a place draws its heading and one line.

### 6. Validate, Render, Compare, Publish

Follow the skill's steps 6 to 9. After the board is published, and only then, save the cache:

```bash
bash BUGS_GATHER save REPO GATHER_JSON ASSESSMENTS_JSON SCORED_JSON
```

A sync that stops early leaves the previous cache as the baseline for the next one.

## Cache

Each repository has a cache at `${XDG_CACHE_HOME:-$HOME/.cache}/report-boards/bugs/github.com/OWNER/NAME/`, shared by every conversation and every harness. It holds the last published gather, its assessments, and its score. Each file is replaced in one step, so an interrupted save leaves the previous one intact. When the cache is missing or unreadable, the sync is a cold one: it says so, and every open bug needs reading. Deleting the cache costs one cold sync and nothing else.

## Data

`bugs-gather draft` writes every field below; the analysis writes only the prose.

### Top Level

| Field        | Required | Contents                                                                                                       |
| ------------ | -------- | -------------------------------------------------------------------------------------------------------------- |
| `board`      | Yes      | `bugs`                                                                                                         |
| `title`      | Yes      | The board's name, identical across syncs                                                                       |
| `repo`       | Yes      | `OWNER/NAME`                                                                                                   |
| `repoUrl`    | Yes      | The repository's address                                                                                       |
| `sync`       | Yes      | `at` is the score's time, `branch` and `commit` the default branch and its tip, `timeZone` the config's        |
| `summary`    | Yes      | One or two sentences                                                                                           |
| `nowWarn`    | Yes      | The config's Now warning count                                                                                 |
| `readyLimit` | Yes      | The config's Ready to go cap above the fold                                                                    |
| `triage`     | Yes      | The note's entries, empty when there are none                                                                  |
| `bugs`       | Yes      | Every bug in the gather, open and recently closed, each with its `tier`                                        |
| Sections     | Yes      | `now`, `today`, `ready`, `investigate`, `later`, `parked`, and `fixed`, each a list of entries, possibly empty |

### Section Entries

| Field      | Required                          | Contents                                              |
| ---------- | --------------------------------- | ----------------------------------------------------- |
| `item`     | Yes                               | The bug's number; its `tier` must name this list      |
| `action`   | In `now` and `today`              | The next concrete step                                |
| `impact`   | In `now` and `today`              | Who is affected and how                               |
| `signals`  | At least one in `now` and `today` | As the score lists them                               |
| `group`    | In `ready`                        | `ship`, `review`, `in-progress`, or `ready-to-fix`    |
| `question` | In `investigate`                  | What to learn first                                   |
| `reason`   | In `later` and `parked`           | Why it waits                                          |
| `verify`   | Optional in `fixed`               | `true` to remind the reader to check it on production |

Write bug numbers in prose as `#123`; the page links them.

## What the Page Draws

| Section             | Shows                                                                                                                          |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Header              | The repository, the sync time and live age, and the Now, Today, Ready, Investigate, and open counts; Now warns above `nowWarn` |
| Summary             | `summary`                                                                                                                      |
| Act now             | A card per bug: the action as the largest text, the impact, why it is there, its facts, its fix, and its signals               |
| Today               | The same card, smaller, with an "Unconfirmed" tag on a bug to confirm on production                                            |
| Ready to go         | The top `readyLimit` bugs in their groups, each with its next step, fix state, and facts                                       |
| Needs investigation | Below the Report divider: each bug, what is unknown, and its question                                                          |
| More ready to go    | The rest of Ready to go                                                                                                        |
| Can wait            | A table grouped by reason, with impact, environment, evidence, age, and pipeline                                               |
| Recently fixed      | Each closed bug, why it closed, what fixed it, and a "Verify on production" tag where it applies                               |
| Parked              | Each bug and why                                                                                                               |
| Triage note         | The note's entries, with expired ones struck through                                                                           |
| Footer              | The sync line, the counts, and `sync.extra`                                                                                    |

A fact nobody has confirmed, such as an unknown field or evidence from reading code, is a dashed chip; a fact the triage note set carries a dot. A signal older than a week has a dashed outline. The header age turns amber after 4 hours and red after 12, because a bug board for today goes stale in hours.

## Validation

`report-board validate` rejects data that breaks any of these rules, and lists every problem at once:

- Every bug sits in exactly one section, the one its `tier` names; closed bugs sit in `fixed`, and open ones never do.
- Now and Today entries carry an action, an impact, and at least one signal, and no signal is later than `sync.at`.
- A Now entry rests on an `escalate` entry or on an assessment that earns Now by the rule above.
- A snoozed or parked bug is not in Now or Today unless a later `escalate` brings it back.
- A triage signal names an entry in `triage` that has not expired by `sync.at`, counted in local days of `sync.timeZone`.
- Open bugs carry assessments in the closed sets; triage entries follow the note grammar, and each ID matches its entry.
- Ready entries name a group, and `ship` and `review` entries a fix pull request; Investigate entries carry a question; Later and Parked entries a reason.
- `sync.timeZone` is set and is a zone the time zone database has.
