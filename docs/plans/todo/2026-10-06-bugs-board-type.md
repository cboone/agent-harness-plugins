# Add a `bugs` Board Type to `publish-report-board`

## Context

`publish-report-board` ships `backlog-triage` on `main`, and a second type, `focus`, is under construction on `feature/focus-board` (no PR yet). Neither answers the question a bug list raises: which bugs are hurting people on production right now, what has to happen today, and how the rest should be triaged. This plan adds a third board type, `bugs`, for one repository at a time. Above the fold it is action oriented (act now, do today, ready to go); below it, it is a report (needs investigation, can wait, parked, recently fixed).

It follows the focus board's model wherever that fits: a deterministic gather and score script, a committed note that carries the user's judgments, a persistent cache so a re-sync in a new conversation stays cheap, a check-in with the user before publishing, signals with sources and ages, and validation rules that keep a stale board from publishing. It follows `backlog-triage` for identity: one repository, `repo` and `repoUrl`, `sync.branch` and `sync.commit`, and `#N` links. It departs from both where bugs differ: scope is every bug in the repository, whoever holds it, and model reading is the core of the analysis rather than a shortlist step, because severity and production status live in issue bodies.

Decisions confirmed by the user on 2026-10-06:

- Build independently from `main`, not stacked on `feature/focus-board`.
- One repository per board, for now. Every open bug in it, whoever holds it.
- Evidence comes from GitHub, ZenHub when configured, and model reading. Error trackers are out of scope for this version.
- A committed triage note with bug-specific verbs persists the user's judgments.

## Evidence Behind the Design

Gathered on 2026-10-06 against live Swing Left data.

- **Volume.** Open `bug`-labeled issues: `votefwd` 54, `frontend` 17, `SwingLeftPy` 21. The organization defines issue types Task, Bug and Feature, and `type:Bug` adds issues the label misses (`votefwd` 13, `frontend` 3, `SwingLeftPy` 4), so scope is the union of label and type. `votefwd` is the first target.
- **The tracker's severity signal is close to empty.** The only priority label in those repositories is `votefwd`'s `high-priority`. There are no severity, production or regression labels. Severity, environment and user impact must be read from bodies and comments, and the user's confirmed judgments must persist somewhere, which is the triage note's job.
- **Most bugs are found by code reading, not reported by users.** The fifteen newest `votefwd` bugs were all filed by `cboone` from audits, and bodies say so ("This is source verification, not a live production endpoint test"). Whether a bug is confirmed on production, reproduced, or inferred from source is therefore a first-class field; it is the main thing separating Act now from Needs investigation.
- **Impact ranges widely within one list.** The same week in `votefwd` holds "Pledging crashes the app instance" (core flow), "Banning an account does not stop it logging in" (access, security), and "check-cloud-run-config reports CPU drift" (internal tooling). Tiers must separate these without any label to lean on.

## First Live Gather

Run on 2026-10-06 against `swing-left/votefwd` at `develop` `8135b4cb`, with ZenHub, in 4.5 s (3.7 s without ZenHub).

- **Volume.** 64 open bugs: 51 by label alone, 10 by issue type alone, 3 by both. 7 closed in the last 7 days, 5 of them with a merged closing pull request, one closed as a duplicate.
- **ZenHub covers every bug**, in seven pipelines: New Issues 47, Must Do 6, In Progress 5, Product Backlog 2, Should Do 2, High Priority 1, Review/QA 1. Six are in the current sprint. "Must Do" and "Should Do" are pipelines the plan did not anticipate, and they are triage decisions someone already made.
- **GitHub carries no user-involvement signal here.** All 64 open bugs were filed by three maintainers (60 by `cboone`), none has a reaction, and no one outside the repository has commented. Reach and user involvement come from reading and from the triage note, as the plan expects; the gathered facts stay in the board for repositories where they fire.
- **Work in progress is common.** Eleven bugs carry an `in progress` label or sit in In Progress or Review/QA, and six have an open fix pull request (one with failing checks). The plan's tiers do not yet say how in-progress work shows.
- **The urgent label alone fills Now.** Four open bugs carry `high-priority` and one sits in High Priority, which under the drafted rule puts five bugs in Now before any reading, equal to the default `nowWarn`. Three of those are already in progress.

Confirmed by the user on 2026-10-06, after reviewing this gather:

- An urgent label or pipeline is a signal only. It adds rank weight and places nothing; reading and the triage note decide the tier.
- "Must Do" and "Should Do" pipelines add rank weight only.
- An in-progress bug stays in its tier with an "In progress" tag naming its pull request, label, or pipeline, so an urgent one's action becomes landing the fix. A non-urgent in-progress bug goes to Ready to go.
- Calibrate on a sample of about 15 varied bugs before assessing the rest.

Two adjustments from building the gatherer:

- ZenHub needs the repository's numeric ID, which the gatherer reads from the GitHub API, so the config does not carry it.
- `bugTypes` names GitHub issue types, searched with `type:`. ZenHub-only issue types cannot be found without enumerating the workspace, so they are out of scope.

## Sample Calibration

Fifteen `votefwd` bugs were assessed on 2026-10-06 by three parallel readers in about 39 s of wall-clock time, then placed by the drafted rules. Now held #4579 (every pledge crashes the instance and loses the COMMIT activity) and #4518 (241 banned accounts can still log in), which matched the user's reading. Today held five of the fifteen, which would extrapolate to about twenty, so the user tightened it.

Confirmed by the user on 2026-10-06, after reviewing the sample:

- A dated deadline is recorded as `deadline` and places a bug in Today only within `deadlineDays` (default 14); further out it adds rank weight and a dated chip. Undated time sensitivity, such as damage accruing with every event, still places it in Today.
- A security bug on a public surface goes to Now on code-reading evidence, because exposure does not wait for a confirmed exploit. Other high-impact bugs known only from source stay in Today with "confirm on production".
- A new assessment field, `mitigated`, marks a bug whose harm has been stopped while its fix remains. A mitigated bug skips Now and Today.
- Today needs a reach of `some` or more, or no workaround. A production bug that reaches few people who have a workaround goes to Ready to go, ranked high.

## Full Calibration

The remaining 49 bugs were assessed the same day by five parallel readers, each finishing in 64 to 81 s of wall-clock time. All 64 then placed as Now 5, Today 6, Ready 23, Investigate 15, and Later 15.

- **Now:** #4579 (pledge crash), #4034 and #4411 (unauthenticated API v2, and a letterBundles PATCH with no permission check), #4410 (opt-outs do not suppress adopted letters), #4518 (banned accounts can log in).
- **Today:** #4408 (relinquish erases bundle membership with no audit), #4327 (PDF workers exhaust their budget in zonal incidents), #4393 (refresh bounces users to /dashboard, in progress), and three to confirm on production: #4441, #4539, #4351.
- **Ready:** ten in progress, including both election-day bugs and #4386, due 2026-11-03; twelve ready to fix; #4554, mitigated.
- **Investigate:** mostly admin-tool bugs known only from source, plus three Must Do items: #3930, #3974, #4305.
- **Later:** internal tooling, tests, alerts, and deploy scripts.

The first full run exposed four rule problems, fixed before the user reviewed the result: "cause known" made Ready a catch-all of 34 that swallowed internal tooling; a deadline already past (#4320, 2026-08-31) still counted as due; `unknown` was read optimistically, as no workaround in Now and as wide reach in Today; and a suspected cause on a user-facing bug fell through to Later.

Confirmed by the user on 2026-10-06, after reviewing all 64:

- A `security` impact on an `internal` surface, such as #4575, a test break blocking a Dependabot fix for high-severity advisories, goes to Ready to go, never higher.
- Ready to go shows its top `readyLimit` (default 8) above the fold, and the full grouped list in the report.
- The overall shape matches the user's sense of the repository; the rules go into `bugs-gather score`.

## Naming and Settings

| Setting     | Value                                                                                                           |
| ----------- | --------------------------------------------------------------------------------------------------------------- |
| Board type  | `bugs`                                                                                                          |
| Template    | `${CLAUDE_PLUGIN_ROOT}/templates/bugs.html`                                                                     |
| Title       | `REPO bugs`, such as `votefwd bugs`                                                                             |
| Favicon     | 🐞                                                                                                              |
| Icon        | `bug`                                                                                                           |
| Description | `Bug board for OWNER/REPO: what to fix now, what to do today, and how the rest is triaged.`                     |
| Script      | `bugs-gather`, beside `report-board`, written `BUGS_GATHER` in the reference                                    |
| Config      | Optional, `${XDG_CONFIG_HOME:-$HOME/.config}/report-boards/bugs/REPO-PATH.json`                                 |
| Cache       | `${XDG_CACHE_HOME:-$HOME/.cache}/report-boards/bugs/REPO-PATH/`                                                 |
| Files       | `REPO-bugs.json`, `REPO-bugs.html`, working page `REPO-bugs.next.html`, under the skill's existing step 3 rules |

`REPO-PATH` is the host and path of `repoUrl`, as the skill's local fallback already keys boards, so two like-named repositories never share a config, cache or note.

## Scope

- Open issues in the repository that are bugs: GitHub issue type `Bug`, a label in `bugLabels` (default `["bug"]`), or an issue type named in `bugTypes` (default `["Bug"]`).
- Open pull requests that close any of those bugs, found through `closingIssuesReferences`, for Ready to go and the fix state on every row.
- Bugs closed within `recentDays` (default 7), with the pull request that closed them, for Recently fixed.

ZenHub containers (levels in `containerLevels`) are counted in Parked, never ranked.

## Assessment: What Reading Produces

Each bug gets one cached assessment, written by the model from the body and recent comments, keyed by `#N` and `updatedAt`. Fields are closed sets so `score` can compute on them and `validate` can check them:

| Field           | Values                                                                                                                     |
| --------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `environment`   | `production`, `staging`, `development`, `unknown`                                                                          |
| `evidence`      | `user-report`, `production-observed` (logs, monitoring, a maintainer saw it live), `reproduced`, `code-reading`, `unknown` |
| `surface`       | `public`, `signed-in`, `admin`, `internal`, `unknown`: who can see it, which is the visibility dimension                   |
| `impact`        | `security`, `data-loss`, `money`, `access`, `core-flow`, `degraded`, `cosmetic`, `internal`, `unknown`                     |
| `reach`         | `all`, `many`, `some`, `few`, `unknown`                                                                                    |
| `workaround`    | `none`, `exists`, `unknown`                                                                                                |
| `cause`         | `known`, `suspected`, `unknown`                                                                                            |
| `timeSensitive` | `true` when waiting makes it worse, such as a deadline, damage accruing in data, or reports increasing                     |
| `deadline`      | The date, `YYYY-MM-DD`, after which waiting makes it worse, such as an election day, or `null`                             |
| `mitigated`     | `true` when the harm has been stopped, such as by a configuration change, while the fix remains open                       |
| `gist`          | One sentence on what is wrong                                                                                              |
| `nextStep`      | One sentence on the next concrete action                                                                                   |
| `question`      | What has to be learned first, when anything above is `unknown`                                                             |

`money` covers donations, pledges and payments; `access` covers login, auth and account state. The gatherer adds the deterministic facts beside it: author association (outside reporters count as user involvement), distinct non-member commenters, reactions, `regressionLabels`, `urgentLabels`, ZenHub pipeline, sprint and blocking, age, recent activity, assignee, and fix pull request state (draft, checks, review decision).

## Tiers

`bugs-gather score` places every bug in exactly one tier with deterministic rules over the assessment, the gathered facts and the triage note. Triage entries win over assessment fields. Within a tier, bugs rank by a weighted urgency score (`weights`, defaults documented in the script) built from impact, reach, surface, user involvement, time sensitivity, regression and time open on production.

| Tier          | Rule                                                                                                                                                                                                                                                                                                                                                                                                                              | Above the fold   |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| `now`         | Unless snoozed or parked: an unexpired `escalate` entry; or, unless `mitigated`, production, `evidence` of `user-report`, `production-observed` or `reproduced`, a `surface` of `public` or `signed-in`, an impact of `security`, `data-loss`, `money`, `access` or `core-flow`, and a `workaround` of `none`; or `security` on a `public` surface in production or an unknown environment, on any evidence                       | Yes              |
| `today`       | Unless `mitigated`, any of: confirmed on production for `public` or `signed-in` users with a reach of `some`, `many` or `all`, or a `workaround` of `none`; a Now-level impact on those surfaces known only from source or not yet placed in an environment, with the action "confirm on production", unless its `deadline` lies beyond the window; undated `timeSensitive`; a `deadline` from today through `deadlineDays` ahead | Yes              |
| `ready`       | Not `now` or `today`, and any of: in progress; a fix pull request that is open and not a draft (grouped as "ship" when approved and green, otherwise "review" or "checks failing"); `mitigated`; `security` impact on an `internal` surface; or, on any surface but `internal`, `cause` `known` ("ready to fix"). The page shows the top `readyLimit` (default 8) above the fold and the rest in the report                       | Top `readyLimit` |
| `investigate` | Not internal, and any of `environment`, `surface`, `impact` or `cause` is `unknown`, or `cause` is `suspected`, or reproduction failed                                                                                                                                                                                                                                                                                            | No               |
| `later`       | Everything else, with a `reason`: internal (any bug on an `internal` surface that is not in progress), not production, cosmetic, or backlog                                                                                                                                                                                                                                                                                       | No               |
| `parked`      | Snoozed or parked by the note, a `parkLabels` label, or a container                                                                                                                                                                                                                                                                                                                                                               | No               |
| `fixed`       | Closed within `recentDays`; a production bug carries a "verify on production" tag                                                                                                                                                                                                                                                                                                                                                 | No               |

A `now` or `today` bug that also has a fix pull request stays in its tier and shows the pull request's state on its row: urgency wins over readiness. A snoozed or parked bug never reaches `now` or `today` unless a later `escalate` brings it back. Sections hold only what earns a place; an empty one shows its heading and one line.

## The Triage Note

Same file grammar, timestamp rules, ID rule, inclusive `until` dates in `timeZone`, and commit flow as the focus steering note: check for uncommitted changes the skill did not make and stop if there are any, `git add -- PATH`, `git commit -S -m MESSAGE -- PATH`, explicit `--git-dir` and `--work-tree` from `triageGit` when set, never push. Targets are `#N`. Verbs:

| Verb       | Effect                                                                                                                                                     | `until`  |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| `escalate` | Places the bug in Now                                                                                                                                      | Optional |
| `set`      | Overrides assessment fields, written `key=value` before the colon, such as `set #4579 environment=production evidence=user-report: two donors reported it` | Never    |
| `snooze`   | Keeps the bug in Parked through its date                                                                                                                   | Required |
| `park`     | Keeps the bug in Parked until the note changes, such as a won't-fix decision                                                                               | Never    |
| `context`  | Free text the analysis reads, such as "the send window opens 2026-10-14"; names no target                                                                  | Never    |

For `votefwd` the note is `~/Work/docs/bugs/votefwd.md`, committed to `sl-vf` the same way as the focus note.

## Repository Config

Optional. Without one, defaults apply and the first sync that needs a triage note asks the user for its path and writes the config with the Write tool. Fields: `timeZone`, `bugLabels`, `bugTypes`, `urgentLabels`, `urgentPipelines`, `regressionLabels`, `parkLabels`, `containerLevels`, `bots`, `recentDays`, `nowWarn` (a soft cap the page flags when exceeded, default 5), `readyLimit` (default 8), `deadlineDays` (default 14), `weights`, `triageNote`, `triageGit`, and `zenhub` (`workspace`, `tokenVariable`). Names shared with focus keep focus's meanings. Without `zenhub`, its fields are absent and the rules that use them never fire. The ZenHub token stays in its environment variable and reaches `curl` only through a mode-600 header file, as in focus.

`votefwd`'s first config: `bugLabels` `["bug"]`, `bugTypes` `["Bug"]`, `urgentLabels` `["high-priority"]`, `urgentPipelines` `["High Priority"]`, `timeZone` `America/New_York`, and the existing ZenHub workspace and token variable.

## Sync Flow

1. **Find the previous board** by exact title, as the skill already does.
2. **Gather.** `bugs-gather gather REPO_SPEC GATHER_JSON` resolves the repository, default branch and its commit, runs the open-bug, fix pull request and recently closed searches as parallel GraphQL calls, then one aliased ZenHub query for every bug, and writes one normalized file with a fingerprint per bug. It prints what moved since the cached gather: new bugs, closed bugs, new comments from other people, new reactions, fix pull request state changes.
3. **Assess what changed.** The model reads every bug whose assessment is missing or whose `updatedAt` differs from the cached one, and reuses the rest. A cold sync reads every bug, in parallel subagents that each return assessments in the fixed shape above, written to `ASSESS_JSON`.
4. **Score.** `bugs-gather score REPO_SPEC GATHER_JSON ASSESS_JSON SCORED_JSON` applies the note and the rules, and prints the proposed Now and Today lists, tier counts, tier moves, and every bug placed in Now or Today on an unconfirmed field.
5. **Check in.** Show that report, the triage entries and any expired ones, and ask, with a structured question tool when available: are the Now and Today calls right, and is anything confirmed on production, already fixed, or not worth fixing? Record answers as `escalate`, `set`, `snooze` or `park` entries, commit the note, and score again. Skip the questions when the invoking message already states the updates. When nothing moved and the user has nothing to add, say so and stop.
6. **Analyze.** For Now and Today, write `action` (the next concrete step, imperative) and `impact` (who is affected and how, one sentence). For Investigate, write `question`. Write `summary`: what to do first and the one constraint that shapes today.
7. **Write, validate, render, compare, publish**, as skill steps 6 to 9. Then `bugs-gather save REPO_SPEC GATHER_JSON ASSESS_JSON SCORED_JSON` updates the cache, only after publishing.

## Board Data

Top level: `board` (`bugs`), `title`, `repo`, `repoUrl`, `sync` (`at`, `branch`, `commit`, `timeZone`, `extra`), `summary`, `nowWarn`, `bugs`, `triage`, and section lists `now`, `today`, `ready`, `investigate`, `later`, `parked`, `fixed`.

- `bugs`: every bug in the gather, keyed by number, with `title`, `tier`, `state` (`open` or `closed`), `assessment`, the gathered facts the page draws, and `fix` (`{ "pr", "state" }`) when there is one.
- Section entries: `item`, `signals` (as in focus: `source` of `triage`, `zenhub`, `github` or `assessment`; `kind`; `text`; `at`; `entry` for triage signals), plus `action` and `impact` in `now` and `today`, `group` in `ready`, `question` in `investigate`, `reason` in `later` and `parked`.

## Page Layout

Follows `design-conventions.md`: tokens for both themes, a 1080-pixel column that reflows at phone width, state in form as well as color.

Above the fold, action oriented:

- **Header band**: repository, sync time and live age (amber after 4 hours, red after 12, checked against real use at delivery), and counts: Now, Today, Ready, Investigate, open bugs. A Now count above `nowWarn` carries a warning tag.
- **Summary.**
- **Act now**: one card per bug, ranked. The `action` is the largest text on the card, then `impact`, then evidence chips (environment, evidence, surface, reach, workaround) and the fix pull request's state. Now uses a new danger token with a solid left bar and a filled "Now" tag.
- **Today**: compact cards with `action`, `impact` and chips, amber with an outlined tag. A "confirm on production" bug carries a dashed "unconfirmed" chip.
- **Ready to go**: dense rows in three groups (ship, review or checks failing, ready to fix), each one click from its pull request or issue.

Below the fold, a report:

- **Needs investigation**: each bug with its `question` and what is unknown, ranked by the impact it would have if confirmed.
- **Can wait**: a table grouped by `reason`, with impact, environment, evidence, surface, age, and pipeline or sprint.
- **Recently fixed**: closed bugs with their closing pull request, and the "verify on production" tag where it applies.
- **Parked**, **Triage note** (expired entries struck through), and a **Footer** with the sync line and `sync.extra`.

Chips for unconfirmed fields are dashed, confirmed ones solid; a field set by the triage note carries a small note marker so the user sees which calls are theirs.

## `report-board` Changes

`main`'s `report-board` assumes one board type. Reproduce the focus branch's dispatch design rather than inventing a parallel one, using the same names, so whichever branch lands second merges by adding its type to each dispatch point:

- A `BOARD_TYPES` list, per-type validate filters, per-type compare filters, and `board_summary` branches (`bugs` prints "N now, M today, K open bugs").
- Top-level `issues` and `lanes` requirements become `backlog-triage` rules. `repo`, `repoUrl`, `sync.branch`, `sync.commit` and the identity guard stay as they are; `bugs` shares them with `backlog-triage`.
- `sync.timeZone` required for `bugs`, with the existing zone check.

`bugs` validation rules, every problem listed at once:

- Every bug sits in exactly one section; section lists name only bugs placed there; numbers are unique; `fixed` holds only closed bugs, every other section only open ones.
- Now and Today entries carry `action`, `impact` and at least one signal. A Now entry rests on an `escalate` signal, an urgent label or pipeline signal, or an assessment that meets the Now rule.
- Assessment fields use the closed sets above; an Investigate entry carries `question`.
- A `ready` "ship" or "review" entry names a fix pull request.
- A snoozed or parked bug is not in Now or Today unless a later `escalate` brings it back.
- Triage entries follow the grammar, IDs match, triage signals name unexpired entries, and no signal is later than `sync.at`.

`bugs` compare output: bugs that entered or left Now and Today, new and closed bugs, tier moves, and assessment changes that matter, such as an environment moving to `production`.

## Shared Code

`bugs-gather` needs pieces `focus-gather` also has: the mode-600 ZenHub header file, the aliased `issueByInfo` query with the `GithubIssueType` and `ZenhubIssueType` fragments, note parsing with offsets and inclusive local `until` dates, and atomic cache writes. Because the branches are independent, copy them from `feature/focus-board` with a comment naming the counterpart, as focus already does for template helpers. Template helpers (element builder, `#N` prose linker, sync-time formatting, live age) come from `backlog-triage.html` on `main`; signal chips come from `focus.html`. When the second of the two branches lands, file an issue to extract the shared pieces.

## Files

- New: `plugins/publish-report-board/scripts/bugs-gather` and `scripts/bugs-gather-queries/*.graphql`; `templates/bugs.html`; `skills/publish-report-board/references/board-types/bugs.md`.
- Changed: `scripts/report-board`; `SKILL.md` (board-type table, step 2 script location, step 5 check-in, step 10 report); `references/choosing-a-board.md` (`bugs` for a repository whose bug list needs triage by urgency, `backlog-triage` for drawing a backlog down), `design-conventions.md` (danger token for Now, signal chips), `sync-metadata.md` where it names types; plugin `README.md`; `.claude-plugin/plugin.json` to `1.1.0` with a `bugs` keyword; catalog and root README descriptions if the description changes, kept verbatim in sync.
- Tests: `tests/scrut/report-board.md` (dispatch, per-type requirements, every `bugs` rule accepting and rejecting, compare); new `tests/scrut/bugs-gather.md` with stubbed `gh` and `curl` (label and type union, fix pull request linking, recently closed, outside-reporter facts, ZenHub optional, note parsing and expiry across daylight-saving changes, every tier rule, urgency ordering, warm and cold cache, a repository with no bugs); `tests/data/bugs-gather/`, `tests/data/report-board/bugs.json`; a `tests/fixtures/curl-stub` and `gh-stub` additions; new paths in the Makefile `SCRUT_ENV` and CI `scrut-env`; `SCRUT_UNSET` clears the real ZenHub token variable.
- Regenerated: `dist/codex` and `.agents` mirrors through `make build`.
- This plan moves to `docs/plans/todo/2026-10-06-bugs-board-type.md`, committed before implementation starts.

## Delivery Order

1. Rename and commit this plan.
2. `report-board` dispatch on the focus model, with `backlog-triage` behavior unchanged and its scrut suite green.
3. `bugs-gather gather` against live `votefwd` data. Stop and review the volume and facts with the user.
4. A cold assessment of every `votefwd` bug, then `score`. Stop and calibrate the tier rules and weights with the user against the real Now and Today lists before building anything that depends on them; record the calibration decisions in this plan.
5. `bugs` validation and compare, with scrut tests.
6. Template and render; check by hand in headless Chrome at desktop and 390-pixel widths, in both themes, with a full Now list, an empty Now list, and an expired triage entry.
7. Skill, references, README, version, `make build`.
8. First real publish for `votefwd`, then a warm re-sync in a new conversation after a triage change, recording per-phase timings here as focus did.

Small signed Conventional Commits at each boundary; the plan is committed as it changes.

## Verification

- `make test-all` passes, with the final result observed.
- `report-board validate tests/data/report-board/bugs.json` passes, and each rejecting fixture fails with its named message.
- `render` then `extract` round-trips the sample board unchanged; `compare` against a modified copy reports the expected moves.
- The live `votefwd` publish validates, and the warm re-sync reuses cached assessments for unchanged bugs, which the recorded timings show.
- The `check-versions` skill passes before the PR.

## Out of Scope

- Several repositories on one board; a later version can widen scope to a client config, as focus does.
- Error trackers, logs, uptime and deploy state as sources; `production-observed` evidence comes from what issues and comments say.
- Writing back to GitHub or ZenHub, such as labels or pipelines.
- Bugs with no GitHub issue, and Slack or email reports.
