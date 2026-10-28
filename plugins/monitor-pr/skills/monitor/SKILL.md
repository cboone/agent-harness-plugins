---
name: monitor
description: >-
  Watch a PR until checks pass, Copilot feedback is resolved, and it is
  mergeable, fixing failures, then offer the merge; on a Dependabot PR, never
  push: request a rebase. Use for "monitor the pr", "watch the pr", or "wait
  for ci".
argument-hint: "[pr-number] [--interval <duration>] [--ticks <n|unlimited>] [--rounds <n|unlimited>] [--triage-after <n|never>] [--confirm-clean] [--no-fix]"
---

# Monitor PR

<!-- The bin/ and docs/ paths below name files in this repository, not in a project a skill runs against. -->
<!-- validate-plugins: repository-paths -->

Watch a pull request until it is ready to merge, fixing what can be fixed and pausing for what cannot, then offer the merge and bring the base branch and the repository's other sessions up to date once it lands.

This skill starts where `pr` stops. It is not a passive observer: it repairs failing checks, syncs a stale branch, and drives Copilot feedback to resolution. It is also not a continue-at-all-costs skill. When a decision is genuinely the user's, it stops and asks.

Execution begins at step 1 policy preparation before any axis read, classification or action. This applies to every section and example, including Dependabot overrides, error handling, restored phases and callback events. Those sections describe candidate behavior; the one prepared policy governs entry to all of it.

## Options

The user may provide these options inline:

- **`<pr-number>`**: Monitor a specific PR instead of the current branch's PR (e.g., `/monitor-pr:monitor 361`)
- **--interval `<duration>`**: Override adaptive pacing with a fixed wait (e.g., `--interval 10m`)
- **--ticks `<n|unlimited>`**: Limit foreground polling, including scheduler fallbacks, to `n` ticks before producing a resumable checkpoint. The default is 3; `unlimited` keeps the foreground turn active until a terminal condition or escalation
- **--rounds `<n|unlimited>`**: Change the Copilot round budget from its default of 10. `--rounds unlimited` commits to running until the PR is genuinely clean, however many rounds that takes, and never pauses to ask for more
- **--triage-after `<n|never>`**: From Copilot round `n + 1`, defer Medium and Low findings to follow-up issues instead of fixing them, per step 7c. The default is 5; `never` lets every finding block
- **--confirm-clean**: Require two consecutive clean Copilot reviews rather than one. After the first clean review, request another explicitly and wait for it
- **--no-fix**: Observe and report only. Never push, never invoke a fixing skill, never request a review, and never merge or act on a merge

## Ready Criteria

The repair loop ends when all four axes are clean at the same time, and step 8 takes over. Partial greenness is not readiness.

| Axis         | Clean when                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Checks       | Every check in `statusCheckRollup` has concluded successfully, or the repository has no checks configured                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Copilot      | A Copilot review exists whose commit SHA equals the current head and whose recorded classification is `review`, step 7b processed that review `id` with a `Completed` or `No unresolved Copilot feedback` outcome whose summary lists that `id` under `Reviews read`, the step 3 feedback probe reports no open threads, and an audit that ran on this tick (`audited: true`) reports only items step 7b has processed under a clearing outcome at the current head, per the rules below. Under `--confirm-clean`, two consecutive such reviews against that same head. On a Dependabot PR, clean when there is no current-head review or it is classified `notice`, or when it is classified `review`, its body states no concern, and the probe reports no open threads or audit items; an unclassified or `unclear` review is never clean, per [Dependabot PRs](#dependabot-prs) |
| Mergeability | `mergeable` is `MERGEABLE` and `mergeStateStatus` is neither `DIRTY` nor `BEHIND`. `BLOCKED` counts as clean but must be reported, per the rule below                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| PR state     | `OPEN` and not merged or closed                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |

Six rules that follow from this and are easy to get wrong:

- **A review-body finding the resolver has already handled stays in the review body, and the axis is still clean.** Review bodies are immutable, so the finding is there for as long as the review exists; it never goes away the way an open thread does. What clears it is step 7b's record of having processed that review `id`, not a later read of the body. Waiting for the body to change would hold a finished PR open forever. Audit items behave the same way: a Copilot comment on the PR stays there, and step 7b's record of its id under a `Completed` or `No unresolved Copilot feedback` outcome is what clears it.
- **A review processed with any other outcome never becomes clean, and never waits.** Only `Completed` and `No unresolved Copilot feedback` clear a review's findings. A `Partial` or `Failed` outcome leaves the axis dirty, while the once-per-review `id` guard in step 4 stops the review from being sent to step 7b again, so no later tick can change anything. Escalate per step 9 instead of falling through to the wait branch. This matters on a resumed watch: the original outcome already escalated and ended the watch, and the checkpoint restores the guard, so the wait branch is exactly where such a review would otherwise land.
- **A Copilot review against an older SHA does not count.** Copilot reviews are pinned to the commit they ran against, so every push this skill makes invalidates the previous review by construction. A fix always sends the loop back around.
- **A Copilot notice is not a review.** Copilot posts "encountered an error and was unable to review this pull request", and a report that every changed file was excluded, through the review API. Each is pinned to the head like a review and carries no verdict and no findings, which is exactly what a clean review looks like. Reading the whole body, once per review `id`, tells them apart, as [classifying a review](#classifying-a-copilot-review) describes. A review classified `notice` or `unclear` never satisfies the Copilot axis, and never counts toward `--confirm-clean`.
- **`reviewDecision` does not gate readiness.** A human `CHANGES_REQUESTED` will not stop this skill from declaring the PR ready. Report `reviewDecision` in every status line and in the terminal report so an outstanding human objection stays visible. It matters only after readiness: step 8b uses it, with the rulesets and agent instructions, to decide whether the merge offer waits for an approval.
- **`BLOCKED` does not gate either, but it must be reported.** Requiring `mergeStateStatus` to be `CLEAN` would be the stricter reading of "ready to merge", and it is deliberately not what this skill does: on a repository whose branch protection requires an approving review, nothing the skill can do will ever satisfy it, so the watch would run until its round budget expired and then report failure on a PR that is finished. Treat `BLOCKED` as ready-with-a-caveat instead. **A terminal report that omits an active `BLOCKED` state is wrong**, because it tells the user the PR is ready to merge when GitHub will refuse the merge. Name the state and say what is unsatisfied.

## Dependabot PRs

A PR whose `author.login` in the step 1 snapshot is `app/dependabot` belongs to Dependabot, and Dependabot owns its branch. Once anyone else pushes to that branch, Dependabot stops rebasing it, and a later `@dependabot recreate` discards the push. So on a Dependabot PR this skill never pushes, and four steps change:

- **Step 5, syncing the branch**: do not invoke `sync-with-main:merge`. Ask Dependabot instead, once per head SHA:

  ```bash
  gh pr comment PR_NUMBER --repo OWNER/REPO --body "@dependabot rebase"
  ```

  Then wait for the head SHA to change, and resume at step 3. The request works even on a PR whose automatic rebases Dependabot disabled after 30 days. If Dependabot replies that it will not rebase, usually because someone else pushed to the branch, escalate per step 9: `@dependabot recreate` would rebuild the PR but discards those commits, so that is the user's decision.

- **Step 6, failing checks**: diagnose as in step 6a, but do not repair. A failure caused by a secret the Dependabot run cannot read (`Input required and not supplied: token`, an empty cloud credential, a refused OIDC exchange) says nothing about the update: escalate per step 9, reporting it as an environment problem and pointing the user at the `dependabot:review-config` skill. Escalate any other failure per step 9 too, pointing at the `dependabot:triage-prs` skill, which decides whether the update needs work, a migration, or an ignore. Either way the watch stops, because no further tick can change a failure this skill may not repair.
- **Step 7, the Copilot cycle**: automatic Copilot review does not reliably run on Dependabot PRs, so never request one, and never wait for one. A missing review, a review against an older head (which every `@dependabot rebase` produces), or a current-head review classified `notice` leaves the Copilot axis not applicable: report it as `n/a (Dependabot)` and treat the axis as clean. A notice belongs with the missing review because it is one: Copilot reviewed nothing at that head, and since this path never requests a review, no retry can replace it, so holding the axis open would wait forever. Only a Copilot review at the current head matters. Run the step 3 feedback probe and classification here exactly as anywhere else: they are reads, so nothing about this path pushes. Because this path never invokes `monitor-pr:resolve-copilot-feedback`, whose fixes would be pushes, read the classified body in full yourself and list every concern it states, wherever it states it. When the probe reports open threads or audit items, the body states any concern, or the classification is `unclear`, report the thread locations, the concerns quoted with the review URL, or the audit item links, and escalate. When none of these holds, the review is clean and the axis is clean.
- **Step 8, the terminal report**: say the PR is a Dependabot PR. The merge policy, merge offer, and post-merge steps apply as for any other PR.

The stored sync gate also applies to a Dependabot rebase request; blocked requests produce would-do reports.

## Skill dependencies

- **Required:** `lint-and-fix`, `sync-with-main:merge`, `monitor-pr:resolve-copilot-feedback`
- **Optional:** `create-deferred-issues`

## Capabilities and authority

Use the tools this session actually offers. For a question, use a structured question tool when available in the active mode; otherwise present numbered choices and wait. In a noninteractive run, report the unresolved question and preserved state instead of choosing an answer. Tool names such as Write, Read, Glob and AskUserQuestion below are examples: perform the same file or question operation with the host's supported mechanism. Write a body file completely before issuing the command that reads it; never batch those dependent operations.

Prior user authorization carries through the workflow; add no confirmation merely because the harness differs. Host approvals, active Plan or read-only mode, writable roots and network policy still apply. Stop before a prohibited write or any step dependent on a blocked operation, preserve state, and report the exact command and restriction. Never bypass controls or claim an unrun step completed. Separate completed, skipped, blocked and failed work in the result. For invocation hints, render the named skill with the running harness's form: slash invocation in Claude Code, dollar mention or the skills selector in Codex. A mention is not a tool call; load composed skills from their advertised locations.

## Parent Continuation Contract

Honor a supplied parent continuation block and its resume target. On success, return control to the parent without asking whether to continue. When a decision has no supplied answer, do not ask independently or guess: return `Status: needs-decision`, the question, available choices and preserved state. The parent asks or stops, then invokes this skill with an answer. For an in-progress merge or rebase, list conflicts and the applicable abort command; do not abort or discard work merely to return a result.

Return `Status: <success|no-op|failure|unavailable|needs-decision>`, `Outputs`, `Unresolved or skipped` and `Caller resume target`. A no-op is successful only when no required work was skipped. Preserve any domain-specific status lines below. A host block or failed required check is failure, a missing required skill is unavailable, and unresolved choices are needs-decision. Standalone invocations retain their existing questions and reporting.

## Workflow

### 1. Resolve the PR

#### Resolve policy before any axis work

Every entry starts here: a new invocation, scheduler wake, changed option, restored checkpoint or merge-watch event. Restore options and metadata without reading review bodies, retain all action guards, then resolve the active restrictions **once** for this entry through `merge-flow prepare`. Do not resume directly at an axis read or merge phase. If restrictions change during the entry, return here before further work.

Claude Code replaces the plugin-root placeholder with the installed plugin's absolute, version-correct directory before this file reaches you. If the plugin-root placeholder was not substituted, use the physical location of this loaded skill, never a cache-wide search. Expand any advertised skill-root alias first and set `skill_file` to that absolute `SKILL.md` path. Resolve symlinks before moving up from `skills/NAME/` to the plugin root:

```bash
# package-relative-helper
resolved_skill="$(realpath -- "${skill_file}")" || exit 1
plugin_root="$(cd -- "$(dirname -- "${resolved_skill}")/../.." && pwd -P)" || exit 1
helper="${plugin_root}/scripts/resolve-copilot-threads"
test -x "${helper}" || exit 1
policy_helper="${plugin_root}/scripts/merge-flow"
test -x "${policy_helper}" || exit 1
```

Use the resulting quoted absolute helper path for this session. If path resolution or the executable check fails, stop and report the unavailable helper; do not select another installed version. When `realpath` is unavailable, the host's file tools may resolve the same symlink chain explicitly; if they cannot, report the limitation.

Write raw watch metadata with a `restrictions` object containing current `noFix` and `copilotPaused` booleans plus a `blockedActions` array for additional host or workflow restrictions. These values come from current instructions and effective options, never cached permission values. Also carry `triageAfter` (a nonnegative integer or `"never"`) and `earlierReviewCount` (the known count or null, never an invented zero). Resolve and store the returned `policy` in watch state before any axis read:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/merge-flow" prepare < RAW_STATE_JSON > WATCH_STATE_JSON
```

`RAW_STATE_JSON` and `WATCH_STATE_JSON` are paths to non-secret state files written with the host's permitted file tools. A blocked write, unavailable helper or invalid policy stops before axis work. Policy preparation and validation are pure local operations. A permitted gate means the restrictions do not prohibit an action; it does not grant missing user approval.

Every entry point below consults this **same** resolved policy, using `merge-flow gate ACTION < WATCH_STATE_JSON`. Continue only when its JSON `allowed` field is true; false or a failed/malformed result is never permission. Record blocked work as would-do data. Policy-limited termination and scheduler cancellation remain as step 4 defines. Do not reinterpret raw flags or hand-edit the stored permissions.

| Entry                                                                          | Gate                                              |
| ------------------------------------------------------------------------------ | ------------------------------------------------- |
| PR/check/run metadata and logs                                                 | `read-axis`                                       |
| Review bodies, thread data, audits and stored body reads                       | `read-review`                                     |
| Numeric earlier-review counting                                                | `triage-review`, through the triage command below |
| Review classification/reclassification, including cached bodies and Dependabot | `classify-review`                                 |
| Sync child or Dependabot rebase request; repairs/publication                   | `sync`; `repair`                                  |
| Resolver child and feedback mutations                                          | `process-review`                                  |
| Review requests, waiting, confirming                                           | `request-review`, `wait-review`, `confirm-review` |
| Readiness policy, offers, ready/merge calls and merge watches                  | `merge`                                           |
| Post-merge work, base sync and peer messages                                   | `post-merge`, with `sync`/`notify` prerequisites  |
| Deferred-issue batch or its approval handoff                                   | `file-deferred`, preserving mandatory approval    |
| Reporting and permitted non-review escalation                                  | `report`, `escalate`                              |

The feedback helper also consults `classify-review` because its filters inspect review/comment content. All monitor invocations of bundled scripts must carry `--watch-state WATCH_STATE_JSON` before their command. The scripts enforce the shared gate before dependency/auth checks, API/body reads, writes or mutations. The resolver child receives `WATCH_STATE_FILE` with this same path and carries it into its helper calls. Never omit the state to obtain standalone behavior during a watch. Only pure `prepare`, `gate`, `triage`, `lifecycle`, `dispatch` and `observation-kinds` read their state from stdin instead.

#### Resolve the opening snapshot

Require `read-axis` before the following metadata-only lookup. A review metadata projection may expose identity, URL, SHA and state, but not body text when `read-review` is blocked.

If the user supplied a PR number, use it. Otherwise derive the PR from the current branch. Take the opening snapshot with one call:

```bash
gh pr view <number-or-omitted> --json number,url,author,headRefName,headRefOid,baseRefName,isDraft,state,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup,mergeCommit
```

If the opening or later PR metadata read fails, submit `{name:"snapshot",pending:true,diagnostic:"<actual stderr>"}` to `merge-flow dispatch` with the prepared policy before lifecycle resolution. This registry kind is terminal: the common handler returns immediate `Status: failure`, names the failed read and supplies no lifecycle, route or wait. Stop and cancel scheduling. Never reuse stale metadata or invent OPEN. Without that explicit failed-read observation, missing or invalid lifecycle remains an input error.

Store the fresh metadata object as `snapshot` in watch state, then run `merge-flow lifecycle` once for that snapshot before any candidate collection, triage or feedback probe. Retain the returned `lifecycle` for the tick. A MERGED result proceeds only to post-merge candidate handling; CLOSED proceeds with no work. Neither enters OPEN-only triage, body probes, repairs or review handling. A terminal event is not downgraded to OPEN by a stale metadata read.

Record `OWNER`, `REPO`, and `PR_NUMBER`. The `monitor-pr:resolve-copilot-feedback` skill needs all three and does not document how to derive them, so pass them explicitly when invoking it.

If this conversation contains a foreground checkpoint for that same repository and PR, treat the invocation as a continuation: restore its options and watch state using [Checkpoint and Resume](./references/checkpoint.md) before dispatching the opening snapshot. Resolve the policy above first, then resume at step 3 with fresh GitHub state. Do not initialize a new watch or reset its action guards merely because the user reran the command.

Also record whether `author.login` is `app/dependabot`, which switches on the rules in [Dependabot PRs](#dependabot-prs).

**If the branch has no PR**, report that and stop, pointing the user at `/pr`.

Before numeric triage counting, run `merge-flow triage < WATCH_STATE_JSON`. A `paused` result records triage as paused, leaves an unknown count unknown, and performs no body read, classification or counting. An `unavailable` result likewise skips the work with its restriction reported. A `not-needed` result reuses existing metadata. Only `needsRead: true` permits the batch: consult `read-review` and `classify-review`, fetch earlier reviews with the guarded helper, classify them and record the count/ids. This includes a resume changing `--triage-after` from `never` to a number. Do not infer zero from a blocked batch.

Before scheduling, syncing or repairing, unless `--no-fix` or the Dependabot path excludes those actions, confirm that the `lint-and-fix`, `sync-with-main:merge` and `monitor-pr:resolve-copilot-feedback` skills are available in the advertised list. Accept bare or plugin-qualified identities only when they identify the intended skill unambiguously. If a required skill is missing, stop with `Status: unavailable`, name it and its install command (`/plugin install PLUGIN@agent-harness-plugins` or `codex plugin add PLUGIN@agent-harness-plugins`). Mention `--no-fix` as an available mode, but never switch to it silently.

The prepared policy represents higher-priority review pauses. When review gates return paused, report any metadata-observed arrival and mark the axis `paused by policy`, not clean. A skipped triage/probe/classification is intentional policy state, not a failed or empty review.

For paths that can fix: Confirm that the `lint-and-fix` skill is available. Confirm that the `sync-with-main:merge` skill is available. Confirm that the `monitor-pr:resolve-copilot-feedback` skill is available. These checks share the exclusions and missing-skill stop above.

### 2. Establish the Wait Mechanism

Prepare the mechanism choice here, but do not arm a scheduler or start a wait until step 4's shared dispatch filter permits work or waiting. The acceptance checks below apply when dispatch permits arming. A policy-limited terminal result cancels any restored scheduler instead.

Choose exactly one mechanism and name it on the first tick:

1. **Accepted wake-up tool**: Prefer `ScheduleWakeup`, which returns control between ticks and keeps the transcript small. Select this mechanism only when the tool is available and accepts the wakeup.
1. **Conversation-resume scheduler**: Create a task that resumes this conversation after the selected interval. Select this mechanism only after successful task creation, and retain its task ID for updates and cancellation. Its prompt must say to enter step 1 policy preparation with the retained watch state, then resume this `monitor-pr:monitor` watch at step 3, retain the recorded PR identity, options, counters, and action guards, and stop the task on escalation, on a terminal report, or at readiness, where step 8c replaces it. Use the watch-state fields in [Checkpoint and Resume](./references/checkpoint.md). On each nonterminal tick, schedule or update the next wakeup using the selected interval. A scheduled task is a new tick, not a delayed final response.
1. **Interruptible foreground polling**: When no scheduler is available, or scheduling is rejected or fails, announce the fallback and run a foreground polling loop. If replacing an existing scheduled watch, cancel its pending task or wakeup first; if cancellation fails, escalate rather than start a second loop. A blocking `sleep` by itself is not a continuation mechanism: after every sleep, take the step 3 snapshot and dispatch it in the same active turn. Do not print a terminal response merely because a tick is waiting. Stop only on a terminal condition, an escalation, or the `--ticks` foreground limit.

The default `--ticks 3` bounds every foreground loop, including scheduler fallbacks. Count one tick for each step 3 snapshot and its step 4 dispatch, including the opening snapshot. Finish the dispatch before applying the limit; escalation and the step 8 transition at readiness take precedence over a checkpoint. At the limit, checkpoint before the next wait, following [Checkpoint and Resume](./references/checkpoint.md): include the PR URL, current head SHA, all four axes, complete watch state, selected interval, and the exact `/monitor-pr:monitor` invocation with the original options. Report a **resumable checkpoint**, not a readiness verdict. `--ticks unlimited` removes this foreground limit, but the user may still interrupt the active session. Never claim that a blocking wait will resume after the agent has returned a final response.

Use an interruptible wait when offered. Otherwise bound each shell wait by the observed host command timeout, retain the running command handle and resume dispatch in the same turn. Never infer a scheduler or command timeout from the harness name.

Adaptive intervals by phase, unless `--interval` overrides them:

| Phase                                         | Wait             |
| --------------------------------------------- | ---------------- |
| Checks actively running                       | 2 to 5 minutes   |
| Awaiting a Copilot review at the current head | 5 to 10 minutes  |
| Checks queued, or nothing moving              | 20 to 30 minutes |

When more than one row applies, take the shorter wait. The step 4 fallthrough can reach a tick with checks still running and a Copilot review outstanding at once, and the shorter interval is the one that governs.

During the repair loop on scheduler-backed surfaces there is no wall-clock cap or tick limit. The only budget is on Copilot rounds, per step 7c, and it counts completed reviews rather than elapsed time or poll count. On every foreground path, `--ticks` additionally bounds an individual invocation. After readiness, the step 8c merge watch has its own lifetime of 24 hours. The user can interrupt at any point.

### 3. Take a State Snapshot

On the first tick, reuse step 1's opening metadata and lifecycle. On later ticks, consult `read-axis` before re-running the metadata-only `gh pr view` call and latest-review projection. Consult `read-review` before any feedback/body probe and `classify-review` before entering classification below. A blocked probe is recorded as paused/unavailable, without incrementing failure counters, inventing an empty result or entering a review route. These gates also apply to cached bodies and Dependabot observations.

After each fresh metadata read, store `snapshot`, run `merge-flow lifecycle` once and retain its result. Terminal lifecycles skip all OPEN-only observations below and proceed to step 4. Rebuild observation outcomes from this tick, never cached results.

The latest-review command projects metadata only:

```bash
gh api --paginate --slurp repos/OWNER/REPO/pulls/PR_NUMBER/reviews |
  jq '[.[][] | select((.user.login? // "") as $login | ($login | type) == "string" and (["copilot-pull-request-reviewer", "copilot-pull-request-reviewer[bot]", "copilot", "github-copilot[bot]"] | any(. == ($login | ascii_downcase))))] | last | {id, url: .html_url, commit_id, submitted_at, state}'
```

Three details in that command are load-bearing:

- **`--slurp`, and no `--jq`.** Without `--slurp`, `--paginate` emits one JSON array per page and `gh` applies `--jq` to each page separately, so a filter like `[...] | last` returns the last match _per page_ rather than the last overall. On a PR with enough reviews to paginate, that silently reads the wrong review and the skill compares the wrong SHA against the head. `--slurp` collects the pages into an array of arrays, which `.[][]` then flattens. `gh` rejects `--slurp` together with `--jq` (`the --slurp option is not supported with --jq or --template`), so the filtering has to move to a standalone `jq` after a pipe.
- **Every Copilot login, not just one.** REST reports the account as `copilot-pull-request-reviewer[bot]` while GraphQL reports it as `copilot-pull-request-reviewer`, and `copilot` and `github-copilot[bot]` also appear. Matching a single login makes a real review invisible, which reads as "Copilot has not reviewed yet" and sends the skill into a pointless wait and then an escalation. This is the same login set that `monitor-pr:resolve-copilot-feedback` matches on, tested the same way: bind the login, lowercase it, then `any(. == ...)` over an explicit array, so `Copilot` matches as it does in `fetch-reviews` and the two never disagree about which review is newest. `.user.login? // ""` and the string check keep a review with no author, or a malformed one, from breaking the comparison.
- **Flag position, and no quotes around the endpoint.** `--paginate` and `--slurp` come before the path, so a `Bash(gh api repos/*)` rule does not match `gh api --paginate repos/*`; the rule has to spell the flags out in order. Leave the endpoint unquoted as shown: the recommended allow rule matches an unquoted path, and a quoted one begins with `"` where the pattern expects `r`, so it fails to match and prompts. Nothing in the endpoint needs quoting, since owner, repo, and PR number contain no shell metacharacters. The trailing `|` ends the line without a continuation backslash, which keeps the command intact when copied.

Copilot's review `state` is always `COMMENTED`, never `APPROVED`, so never treat an approval state as the pass signal.

`id` is the review's stable key. The feedback probe below reads it, and step 7b's once-per-review guard records it. `commit_id` cannot stand in for it, because `--confirm-clean` produces two reviews against the same head and only the `id` tells them apart.

#### The Copilot feedback probe

The metadata above says a review exists and which commit it ran against. It says nothing about what the review found. Probe what is open directly, using the same script `monitor-pr:resolve-copilot-feedback` reads with, so the two skills always see the same review data.

This plugin ships its own copy of that script. Invoke it via `bash` followed by the quoted path:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/resolve-copilot-threads" --watch-state WATCH_STATE_JSON fetch OWNER REPO PR_NUMBER |
  jq -c '{openThreads: length, locations: [.[].location]}'
```

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/resolve-copilot-threads" --watch-state WATCH_STATE_JSON fetch-reviews OWNER REPO PR_NUMBER |
  jq -c --argjson review_id REVIEW_ID '
    [.[] | select(.id == $review_id)] | last
    | {id, url, commitId}'
```

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/resolve-copilot-threads" --watch-state WATCH_STATE_JSON audit OWNER REPO PR_NUMBER |
  jq -c '{audited: true, items: [(.uncovered // error("no uncovered"))[] | "\(.surface):\(.id)"]}'
```

Eight points govern how the probe is run and read:

- **A failed probe is not a clean probe, and it does not announce itself in the exit status.** Each command writes a diagnostic to stderr and exits nonzero, but the pipeline reports `jq`'s status, and `jq` over empty input emits nothing and exits `0`. So an authentication failure, a rate limit, or a wrong repository shows up as empty output beside the helper's error message, not as a zero count and not as a failing command. Read empty output as "this tick observed nothing", never as "no open threads": leave the Copilot axis unresolved and submit the appropriate pending observation with stderr to the common handling below. Prefixing the command with `set -o pipefail` makes the status carry the failure, at the cost of the recommended `Bash(bash "*/resolve-copilot-threads" *)` allow rule no longer matching, since the command would then begin with `set`.

- **Read-only is not unrestricted.** These three commands require the stored `read-review` permission, even on a Dependabot PR or under `--no-fix`. If permitted, they observe feedback without a fixing child; if blocked, record the skipped probe without reading bodies.
- **The audit sees what the other two cannot.** It reports Copilot feedback outside any Copilot thread or review body, in `uncovered`: a Copilot reply inside an unresolved thread someone else opened, a review comment no thread holds, a comment on the PR itself, or a review whose body is not a string. Without it, that feedback would leave the Copilot axis clean while it sat unread. The list is PR-wide and persists like a review body, so the probe projects it as `items`, which is what step 7b records as processed. Each item names its surface (`review-comment:ID`, `issue-comment:ID`, or `review:ID` for a review whose body is not a string), because ids from different GitHub tables can coincide. An absent `audited` field is a failed audit, never an empty one: the filter emits nothing when `audit` fails or when its output lacks the list. Submit the audit outcome and stderr to merge-flow's observation handling below. The helper alone advances or resets its two-tick counter and returns terminal diagnostics at the bound.
- **Run it only when the metadata probe's `commit_id` equals `headRefOid`.** A stale review sends the tick to step 7a whatever the probe would say, so running it there spends the whole probe on an answer nothing reads. Nothing is lost by the gate: `fetch` reports every unresolved Copilot thread on the PR, whatever review opened it, so threads left over from an earlier review are still counted the moment a current-head review appears.
- **Project the fields shown on every tick, never the raw result.** `fetch-reviews` returns every Copilot review on the PR with its complete body, and a watch takes this snapshot on every tick. The body is read once per review, by the classification below.
- **Select the review by `id`, not by head SHA.** Under `--confirm-clean` two reviews share one head, and only the newest one's body is the current verdict. `--argjson` is required because REST reports `id` as a number.
- **An all-null result is not a failure, and it is not a match either.** `fetch-reviews` leaves out a review whose body is not a string, so a review the metadata probe found can be absent from its output. jq builds the object anyway, and the filter then answers `{"id":null,"url":null,"commitId":null}`. A null `id` means `fetch-reviews` did not return the review the metadata probe found. That has several causes: a body skipped because it is not a string (the command then prints `Warning: skipping review ID: its body is not a string.` on stderr), or a wrong `REVIEW_ID`. None of them is a clean review, so never satisfy the Copilot axis on a null `id`. Keep the thread count from `fetch` and submit pending `review-id` with any skip warning to the common handling below; no independent counter or escalation applies.
- **`fetch-reviews` reads the reviews endpoint the metadata probe already read.** That repetition is deliberate: each command stays standalone and copy-pasteable, and the second read only happens on ticks where a current-head review exists.

#### Classifying a Copilot review

Consult the stored `classify-review` permission before any classification or reclassification, and `read-review` before obtaining or reading a body, even from a cache. Do not execute this section during a blocked triage or probe.

The first time a current-head review `id` appears, read its **complete** body before recording anything about it:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/resolve-copilot-threads" --watch-state WATCH_STATE_JSON fetch-reviews OWNER REPO PR_NUMBER |
  jq -c --argjson review_id REVIEW_ID '[.[] | select(.id == $review_id)] | last | {id, body}'
```

**A failed read is not a body.** No output at all means the fetch failed, and it prints its cause on stderr; `{"id":null,"body":null}` means the result did not carry that review. Neither is a body to classify: record no classification for that `id` and submit pending `review-body` with stderr to the common handling below. No independent per-id counter, wait or escalation applies. Only a non-null `id` with a `body` is read and classified. An empty `body` states nothing, and any findings that review has are threads, so it is a `review`.

Never truncate the body or read only its start. Copilot can place the text that says it did not review anywhere in the body, and a prefix discards exactly the evidence the classification needs. A review body is immutable, so one full read per review `id` is enough. Record one classification per `id` in the watch state:

- **`review`**: Copilot reviewed the head. Step 4 dispatches it to step 7b.
- **`notice`**: the body says Copilot did not review the head, for example because it hit an error or because every changed file was excluded. Step 4's notice condition handles it.
- **`unclear`**: the body neither plainly reports a review nor plainly says no review happened. Never treat it as a review, never let it satisfy the Copilot axis, and never count it toward `--confirm-clean`. Escalate per step 9 with the review link and a short quote of what made it ambiguous, so the user decides.

The resolver reads the same body in full during its own run, which makes it a second check. If its summary for a review this skill classified as `review` has a `Still open` entry naming that review as a Copilot notice, reclassify that `id` as `notice` and take step 4's notice condition instead of escalating the resolver's outcome. A misreading in either skill therefore cannot turn a notice into a clean axis.

The probe and the classification answer exactly four questions, and step 4 asks no more of them than these: is the current-head review a review, a notice, or unclear, are there open Copilot threads, has step 7b processed this review `id` and with what outcome, and does the audit report Copilot feedback the other two cannot reach. What a review body says, whether a finding is real, already handled, or needs no code change, is `monitor-pr:resolve-copilot-feedback`'s judgment, not this skill's, except on the Dependabot path, where no resolver runs.

Reduce the snapshot to the four axes in [Ready Criteria](#ready-criteria).

### 4. Classify and Dispatch

Use the lifecycle already computed once from this tick's snapshot before collecting candidates. MERGED admits only an unhandled post-merge candidate; CLOSED admits no work. For OPEN, collect matching conditions in the order below without routing them. The shared eligibility predicate checks every candidate against that lifecycle and the prepared policy; OPEN-only actions cannot survive a terminal state. A forbidden action becomes a `Would do` line in the report, never a route and never work to wait for. Route only the first remaining permitted action. If none remains, wait only for a running permitted check. Otherwise end with the policy-limited terminal report: `Status: unavailable`, every would-do line and remaining axis, the named parent resume target when supplied, and the scheduler cancellation outcome. Cancel the selected scheduler before returning; if cancellation fails, report that failure. Never offer a merge or start a merge watch from this terminal result. Do not invent pending work from a forbidden review request, repair, sync or merge.

Use the existing `merge-flow dispatch` helper to apply this rule. Resolve `merge-flow` from the same physical loaded-package root as the other bundled helper, confirm it is executable, and pass one JSON snapshot on stdin. The helper only selects and reports; it performs no GitHub or git operation. A missing helper, invalid snapshot or failed command stops dispatch and is reported, never replaced by the old first-match behavior.

Start from watch state containing the fresh `snapshot` and helper-computed `lifecycle`; append candidate fields, leaving `policy` unchanged. For example:

```bash
jq '.+{candidates:[{action:"repair",detail:"fix the failed check"}],runningPermittedCheck:false}' WATCH_STATE_JSON |
  bash "${CLAUDE_PLUGIN_ROOT}/scripts/merge-flow" dispatch
```

Pass the unchanged step 1 `policy` object. Only re-entering step 1 can replace permissions after an option or policy change. Use `sync` for DIRTY/BEHIND, `repair` for failed checks, `classify-review` for a new unclassified review, `process-review` for feedback/audit/unclear-review handling, `request-review` or `wait-review` for step 7a, `confirm-review` for step 7d, `merge` for readiness, `post-merge` for step 8f. For CLOSED, supply no candidates and report the closed state when dispatch returns its terminal result. A note-only BLOCKED state is reported but is not a route. `escalate` is available for a permitted non-review escalation. No unconditional wait candidate is allowed. `runningPermittedCheck` is true only when an actual check that policy permits observing remains running; a forbidden action never sets it.

Write the snapshot with the host's file tool, or provide it through supported stdin transport, without interpolating review text into shell code. For a file transport, invoke the resolved helper as follows; `SNAPSHOT_FILE` is the completed JSON file's path:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/merge-flow" dispatch < SNAPSHOT_FILE
```

If the placeholder is literal, substitute the quoted physical loaded-package helper path already resolved above.

Print every returned `wouldDo` item as data. Persist the helper's returned `observationFailures` unchanged before continuing; no skill-side code increments or resets these counters. If `route` is non-null, perform that selected action only, following its existing step, then take a new snapshot. A route with `retry: true` selects the next snapshot after the normal interruptible wait; do not add another standalone read before that snapshot. If `wait` is true, use the selected interruptible wait and resume at step 3. If `terminal` is true, include every returned diagnostic, preserve the returned status (`failure` for the terminal snapshot kind), and perform the terminal report and cancellation above. Do not subsequently apply raw condition priority or the old report-and-continue rule. Read-only snapshot/probe observations remain permitted under `--no-fix`; their results do not authorize a fixing or review-request route.

#### Permitted pending observations

The closed registry returned by `merge-flow observation-kinds < WATCH_STATE_JSON` is the only kind-to-permission/diagnostic mapping. Supply `{name, pending, diagnostic}` for every applicable read attempted this tick:

| Kind              | Read outcome                                                                                  |
| ----------------- | --------------------------------------------------------------------------------------------- |
| `snapshot`        | Failed opening or later PR metadata, terminal before lifecycle as above                       |
| `review-metadata` | Latest-review API or metadata projection failed; a successful no-review result is not pending |
| `triage`          | Earlier-review batch/count read failed; leave the count unknown                               |
| `threads`         | Thread fetch or projection failed or emitted no result                                        |
| `review-id`       | Review identity fetch/projection failed or selected `id` is null                              |
| `review-body`     | Full classification-body fetch failed or selected identity/body is absent                     |
| `audit`           | Audit failed or lacks its required result fields                                              |
| `mergeability`    | Mergeability remains unknown                                                                  |

The registry maps `snapshot`, `review-metadata` and `mergeability` to `read-axis`, and other kinds to `read-review`. Existing triage/classification gates remain required; a retry never grants them. For each fresh OPEN snapshot, submit all applicable successful or pending outcomes through the same handler. A successful/known observation has `pending: false`. Preserve the actual diagnostic, including audit stderr. A forbidden observation is a would-do item, never a reason to wait and never an attempted read. No duplicate name is allowed within one tick.

Pass the previous `observationFailures` returned by `merge-flow` back unchanged on the next dispatch, including resume. Only this helper owns these counters: it advances permitted pending work and resets it on permitted success. Every retryable registry kind shares the same two-tick bound; terminal `snapshot` never retries. The first pending outcome produces an explicit read retry even with no running CI check; the second ends `Status: unavailable` with a diagnostic naming the observation. Stop the scheduler at this result rather than escalating as if policy allowed unlimited retries. Terminal PR lifecycles ignore old observations and cannot wait on running checks. Restore counters from checkpoints; a missing resumed counter is reported rather than silently reset.

`merge-flow lifecycle < SNAPSHOT_STATE_JSON > TICK_STATE_JSON` computes state before candidate collection. These are distinct input/output files; update the watch-state path to the completed result. Dispatch verifies that lifecycle still matches the snapshot. Treat a missing or invalid lifecycle as an input failure, not OPEN.

Two orderings are deliberate:

- **Sync the branch before diagnosing check failures**, because a stale branch is a common cause of them.
- **Act on Copilot findings without waiting for in-flight checks**, because that work is durable: the fixes land whatever the checks go on to do. Requesting a review is perishable by comparison, so both request paths keep a passing-checks precondition. Every push invalidates a review rendered against the old head, which makes a review requested mid-check one that a check fix would throw away, and it spends a round against the step 7c budget either way.

1. **PR is `MERGED`**: go to step 8f with `mergeCommit.oid` from the snapshot, whoever merged it and whether or not the watch reached step 8; the step 8f guard makes a merge already handled a no-op. A merge seen before readiness is reported as such. When the snapshot has no merge commit yet, run the step 8c watch with the current `headRefOid` instead and handle its `merged` event; on the foreground path, run it in the foreground, since no question is open.
1. **PR is `CLOSED`**: provide no work candidates. Report the closed state with the helper's terminal result and cancel scheduled work.
1. **`mergeStateStatus` is `DIRTY`**: conflicts with the base branch. Go to step 5.
1. **`mergeStateStatus` is `BEHIND`**: go to step 5.
1. **`mergeStateStatus` is `BLOCKED`**: do not treat this as a blocker and do not wait on it, but record it. It means a branch protection rule is unsatisfied, most often a required approving review. Continue evaluating the remaining conditions, and carry the `BLOCKED` state into every status line and into the terminal report per step 8.
1. **Any check concluded with a failure**: go to step 6.
1. **Copilot's newest review against the current head has not been classified yet**: if the probe returned its `id`, read it in full and classify it now, per [classifying a Copilot review](#classifying-a-copilot-review); if the read succeeds, record the classification and evaluate this list again from the top. If the probe returned a null `id`, or the read fails, record no classification and submit the appropriate `review-id` or `review-body` outcome to the common handler. No later Copilot condition may act on an unclassified review; no separate counter or wait applies.
1. **Copilot's newest review against the current head is classified `unclear`**: escalate per step 9 with the review link and a short quote of what made it ambiguous. Never route it to step 7b, and never treat it as clean.
1. **Copilot's newest review against the current head is classified `notice`**: Copilot did not review this head. If no retry has been recorded for that notice's review `id`, request a review once as in step 7a, when checks pass, and record the `id`; this retry is keyed on the notice, so it does not spend the once-per-head request step 7a guards. If a retry is already recorded and the newest review is still that notice after two further ticks, or the review the retry produced is another notice, escalate per step 9 with the notice text. Never route a notice to step 7b, and never treat it as clean.
1. **An OPEN observation is pending or has succeeded**: supply its current outcome to the helper-owned observation handling above. Do not add an independent audit counter, retry loop or escalation route.
1. **Copilot reviewed the current head, its newest review there is classified `review`, and either step 7b has not already been invoked for that review `id`, or the audit reported an item that no step 7b invocation has recorded at the current head**: go to step 7b. Every current-head review classified `review` goes to the resolver once, whatever its body says: only a full read can tell whether it states a concern, and that read is the resolver's job. Audit items are PR-wide, so a new one dispatches even against a review `id` already processed, and one recorded at the current head does not dispatch again. Checks still running do not hold this back. The `id` clause is step 7b's own once-per-review guard, lifted into the condition that reads it: a review body is immutable, so without the guard every later tick would dispatch the same review again.
1. **Copilot reviewed the current head, step 7b already processed that review, and either its outcome was not `Completed` or `No unresolved Copilot feedback`, or the probe still reports open threads**: escalate per step 9, unless the outcome's `Still open` entry names that review as a Copilot notice, in which case reclassify it as `notice` per [classifying a Copilot review](#classifying-a-copilot-review) and evaluate this list again. Both shapes are terminal for that review. A non-clearing outcome never satisfies the axis, and a clearing outcome that leaves threads behind is the case step 7b calls out as unable to change on its own. The `id` guard in the condition above will not send the review to step 7b a second time, and no later tick alters an immutable review, so without this condition the tick falls through to the wait below and the watch never ends. **State the two disqualifying signals rather than a summary of them.** A phrasing such as "this tick has no new input" is true of a cleanly resolved review as well, and this condition sits above the terminal one, so that reading escalates every finished PR instead of merging it. A clean processed review does not belong here: it satisfies the Copilot axis, and its review-body findings are cleared by step 7b's record rather than by a later probe, per the Ready Criteria rules.
1. **Checks pass and Copilot is missing or stale**: go to step 7a.
1. **Checks pass, Copilot reviewed the current head cleanly, `--confirm-clean` is set, and this is the first such review**: go to step 7d to request and await the confirming review.
1. **All four axes clean**: terminal. Go to step 8.
1. **No action condition matched**: supply no route candidate. The shared dispatch filter alone decides whether a running permitted check justifies waiting or the watch must terminate.

The list above supplies candidates only. Restriction filtering and terminal reporting always use the shared rule before any step is entered, including under `--no-fix`.

On a Dependabot PR, steps 5 to 8 follow [Dependabot PRs](#dependabot-prs), and the Copilot conditions above change as that section describes. The classification and `unclear` conditions apply unchanged. A `notice` makes the Copilot axis `n/a (Dependabot)` instead of requesting a retry, and so does a missing or stale review, so the missing-or-stale condition never requests a review either. The audit-failure condition applies unchanged. In place of the dispatch condition, read the classified `review` body in full yourself and escalate if it states any concern, or if the probe reports open threads or audit items. The processed-review condition never matches, because step 7b is never invoked there to record an outcome, and neither does the `--confirm-clean` condition, because no review is ever requested. The probe and the classification read are read-only, so the Dependabot path judges the review without invoking anything that pushes.

### 5. Sync the Branch

Invoke the `sync-with-main:merge` skill:

```text
sync-with-main:merge

Parent continuation:
- Caller: monitor-pr:monitor
- Resume target: Step 3, take a fresh state snapshot.
- On needs-decision: escalate with the question and preserved state, returning it to this skill's parent when supplied.
- On clean merge and push: Continue immediately to Step 3 without asking the user for confirmation.
- On conflicts requiring a decision, or on any question raised: Stop the watch and escalate per Step 9.
```

Treat `needs-decision` from `sync-with-main:merge` as an escalation. Under a parent, return the question and preserved state; standalone, ask through the available question mechanism.

After a clean merge and push, resume at step 3. The head SHA has moved, so Copilot's prior review is now stale.

### 6. Fix Failing Checks

#### 6a. Identify the Failure

```bash
gh pr checks PR_NUMBER --json name,state,link,description,workflow
```

`gh pr checks` exits non-zero when checks are failing **or** still pending, so the exit code is not a reliable signal. Classify from the JSON.

To read the failing job's output, resolve the run id first. A check's `link` has the shape `https://github.com/OWNER/REPO/actions/runs/<run-id>/job/<job-id>`, so the run id is the segment **after `/runs/`**, not the trailing segment, which is the job id. Several checks usually share one run id, because they are jobs within the same run. Either read it from that URL, or query the branch directly:

```bash
gh run list --branch <branch> --limit 5 --json databaseId,conclusion,workflowName \
  --jq '[.[] | select(.conclusion == "failure")][0].databaseId'
gh run view <run-id> --log-failed
```

**A failing check under-reports.** Jobs stop at the first failing step, so later steps in the same job never run and their violations never surface. Treat the log as a lower bound: after repairing what it names, re-run the project's full check locally before pushing, or expect a second failure for something the first log never mentioned.

#### 6b. Repair by Category

- **Lint or format failure**: invoke the `lint-and-fix` skill with `--no-push`:

  ```text
  lint-and-fix --no-push

  Parent continuation:
  - Caller: monitor-pr:monitor
  - Resume target: Step 6c, push the fix, then Step 3, take a fresh state snapshot.
  - On lint success: Continue immediately to Step 6c without asking the user for confirmation.
  - On lint failure or skipped required lint work: Stop the watch and escalate per Step 9.
  - On needs-decision: escalate with the question and preserved state before pushing.
  ```

  Branch on its structured `Lint status: <success|no-tools|failure>` output.

- **Generated-tree drift**: run the repository's own build scripts and commit the result. In this repository that is `make build`.
- **Test or build failure**: read the logs, diagnose the cause, fix it, and commit.

Two ways this step goes wrong in practice:

- **A repair can cause the next failure.** Editing a source file that a generated tree mirrors leaves that tree stale, so a lint fix turns into a generated-tree drift failure on the following run. After repairing anything under a mirrored path, rebuild the generated trees in the same commit rather than waiting for CI to catch it.
- **A chained auto-fix stops at the first unfixable error.** Where a project's fix target chains tools (`markdownlint --fix` then `prettier --write`, say), a violation that has no auto-fix exits non-zero and the later tools never run, so the pass repairs nothing and hides everything downstream of it. Resolve the unfixable violation by hand, then run the fix target again so the remaining tools get their turn.

#### 6c. Push and Resume

Push the fix, then resume at step 3.

#### 6d. Escalation Rules

Stop the watch, report, and ask when any of these hold. These are hard rules, not suggestions:

- The correct fix is a judgment call about intended behavior rather than a mechanical repair.
- The same named check fails again after a fix attempt for it. Track attempts per check name across ticks.
- The fix would touch code outside what this branch already changes.
- The logs do not identify a cause.

### 7. Drive the Copilot Cycle

#### 7a. No Review, or a Stale One

Wait and return to step 3. Copilot re-reviews automatically on push in most repository configurations, so the review usually arrives without prompting.

Before deciding whether to request one, check whether Copilot is already working. Its review runs as a workflow named `Copilot`, so an in-progress run against the current head means a review is coming and requesting another would only duplicate it:

```bash
gh run list --branch <branch> --workflow Copilot --limit 10 --json headSha,status 2> /dev/null |
  jq -r --arg head <head-sha> 'first(.[] | select(.headSha == $head) | .status)'
```

That command answers with exactly one line, or none. Three details make it so:

- **`--workflow Copilot`, not a client-side name filter.** `--limit` applies to runs across every workflow on the branch, so on a repository with several workflows the Copilot run for the current head can fall outside the window and look like no run at all, which then triggers a redundant review request. Narrowing server-side makes the limit count Copilot runs alone.
- **Filter on the head SHA**, using the `headRefOid` from the step 3 snapshot. A completed run for a superseded commit otherwise reads as though it belonged to the current head, which is precisely the distinction this check exists to draw.
- **`first(...)`, because a SHA can have several runs.** A re-run adds another Copilot run for the same commit, and a bare `select` emits one line per match, so the reader gets `completed` and `in_progress` together with no way to tell which governs. `gh run list` returns newest-first, so the first match is the current one. `first` over an empty stream emits nothing and still exits 0.

Empty output means no run for this head. The discarded stderr matters for that: on a repository where Copilot review is not enabled there is no `Copilot` workflow at all, and `gh` then exits non-zero with `could not find any workflows named Copilot`. That is the no-run case, not a failure, so let it read as empty rather than treating it as an error.

Classify each Copilot-phase tick as **working** or **quiet**, and count only the quiet ones:

- **A run against the current head is `in_progress` or `queued`**: working. Copilot is mid-review, so keep waiting however many ticks it takes, and reset the quiet count to zero.
- **A run against the current head `completed`, but no review is visible yet**: quiet. The run finishing and the review appearing are not simultaneous, so one quiet tick here is normal.
- **No run against the current head at all**: quiet. Nothing was triggered.

Both quiet cases are counted the same way and lead to the same remedy, because in both of them nothing further is coming on its own.

**After two consecutive quiet ticks**, request a review explicitly:

```bash
gh pr edit PR_NUMBER --add-reviewer "@copilot"
```

This is the correct mechanism. Do **not** request a review by posting an `@copilot` mention with `gh pr comment`: that adds PR comment noise, and `monitor-pr:resolve-copilot-feedback` treats writing PR comments as forbidden outside its own single summary. Request the review at most once per head SHA. If none arrives after a further two ticks, escalate per step 9.

The run check is what separates "Copilot has not started" from "Copilot is mid-review", which the review list alone cannot distinguish: both look like an absent review. Without it, a slow review gets a redundant request, and a review that was never triggered waits out the same two ticks as one that is already running.

#### 7b. Reviewed at the Current Head

Invoke the `monitor-pr:resolve-copilot-feedback` skill:

```text
monitor-pr:resolve-copilot-feedback OWNER=<owner> REPO=<repo> PR_NUMBER=<number> REVIEW_ID=<review id> WATCH_STATE_FILE=<same watch state path> [DEFER_SEVERITIES=Medium,Low]

Parent continuation:
- Caller: monitor-pr:monitor
- Resume target: Step 3, take a fresh state snapshot.
- On Completed or No unresolved Copilot feedback: Return the final summary comment URL, its Reviews read line and any originating review URLs, then continue immediately to Step 3 without asking the user for confirmation.
- On Partial or Failed: Stop the watch and escalate per Step 9, unless a `Still open` entry names REVIEW_ID as a Copilot notice; then reclassify it as a notice per Step 3 and continue at Step 4.
- On needs-decision: escalate with the question and preserved state, returning it to this skill's parent when supplied.
```

Pass `DEFER_SEVERITIES=Medium,Low` when the review's triage round, per step 7c, is above `--triage-after`. Leave it out when `create-deferred-issues` is not installed, so every finding keeps blocking, and say so once with its install command.

**A `Partial` with a `### Sibling chain` section is a design question, not a failure.** Escalate per step 9, quoting that section, and ask whether to adopt its design option or patch the sibling. Once the answer is carried out and pushed, the next review goes to the resolver as usual, and it settles the sibling against the new code.

Pass the `OWNER`, `REPO`, and `PR_NUMBER` recorded in step 1. That skill's script calls require all three and it does not document how to derive them, so supplying them here saves it from re-deriving them or asking the user. Pass `REVIEW_ID`, the review this dispatch is for: the resolver must read it and list it under `Reviews read`. **A clearing outcome whose `Reviews read` line does not list `REVIEW_ID` does not clear that review.** Treat it like a `Partial` outcome and escalate per step 9, because nothing shows the review was read.

Only invoke it once a review exists at the current head. Invoking it earlier makes it report `No unresolved Copilot feedback` and post a no-op summary comment, which reads as a clean bill of health for code Copilot never saw.

**Invoke it at most once per review.** Record the review `id` each invocation is made against, taken from the step 3 probe, together with the status it reported, the audit `items` at the time, and the head SHA. The resolver runs its own audit and handles those items, so a `Completed` or `No unresolved Copilot feedback` outcome clears them the way it clears review-body findings. An item recorded under any other outcome stays uncleared. **Audit items clear only at the head they were recorded against.** Copilot repeats a review-body finding in each new review until the code changes, so each new head gets it checked again; an audit item is never repeated, and a push can undo the change that settled it. After any push, every audit item dispatches again with the first review at the new head, and the resolver checks it against the current code, so one that still holds costs a `Previously handled` row rather than a new fix. **Do not key this on the head SHA.** Step 7d deliberately requests a second review against the same head, so a SHA key conflates two distinct reviews: it would either suppress the confirming review's findings as already processed or escalate it as a repeat when it is genuinely new. The `id` is the only field that separates them. That record is also what the Copilot axis reads: a review-body finding is cleared by having processed its review, not by a later probe.

**Escalate when a source that should have cleared did not.** After a `Completed` or `No unresolved Copilot feedback` report for a review `id`, escalate per step 9 when the next snapshot's probe still reports open threads. Nothing further will change on its own: a second invocation has no new input to work from, and the step 7c budget will not stop the cycle because it counts completed reviews rather than invocations. A new review or a push is what makes another invocation meaningful.

**Review-body findings are the exception, and getting this backwards is the trap.** An open thread clears when it is resolved, so a repeat there means something genuinely failed. A review-body finding has no thread to resolve and review bodies are immutable, so it stays in that review permanently, for the life of the PR. `monitor-pr:resolve-copilot-feedback` records it as handled in a linked summary row and reads that record back on its next run; that record, plus this step's own processed-review record, is the disposition. Escalating on a body that cannot change would turn every noted or previously handled review-body finding into a false escalation on a PR that is finished. Retain the final summary comment URL and the originating review URL for terminal or escalation reporting.

#### 7c. Round Budget

Count Copilot rounds for this watch. The default budget is **10**. On reaching it, stop and report per step 9, then ask whether to continue and for how many more rounds.

This is a budget, not a verdict about progress. **Do not treat the shape of the finding counts as a signal.** Copilot swings: a round with many findings is regularly followed by a quiet one and then a busy one again, and the count going up does not mean the work is diverging. Four rounds is often not enough to finish, so a watch that is still finding real defects at round 6 or 8 is behaving normally, not thrashing.

What matters is whether the findings are real. Keep going while each round produces valid, fixable defects, and escalate early per step 9 only when a round produces something that needs the user's judgment, per the escalation rules in step 6d. The budget exists to bound an unattended watch, not to second-guess a productive one.

**Late rounds triage instead of blocking.** `--triage-after <n>`, 5 by default, sets the last round in which every finding blocks. A review's triage round is this watch's round count plus the earlier reviews step 1 counted. From round `n + 1`, step 7b asks the resolver to defer Medium and Low findings, in lines this PR changed and in unchanged code alike, and only High findings still drive fixes. A finding without a severity label still blocks. `--triage-after never` passes no deferral at any round. Deferred rounds still count toward the round budget.

`--rounds <n>` sets a different budget. `--rounds unlimited` removes it: the watch then runs until the PR is genuinely clean and never pauses to ask for more rounds, though every other escalation rule still applies.

#### 7d. Confirming a Clean Review

A single clean review is the default finish. It is also the weakest link in the ready criteria, because Copilot's output varies between runs over identical code: a review that surfaces nothing is not proof that there is nothing to surface.

Under **--confirm-clean**, require two consecutive clean reviews instead:

1. The first clean review at the current head does **not** end the watch. Record it, along with the head SHA it was rendered against.
1. Request another review explicitly, exactly as in step 7a:

   ```bash
   gh pr edit PR_NUMBER --add-reviewer "@copilot"
   ```

   This is a re-review of unchanged code, so the request is what produces it. Waiting will not.

1. Wait for a review newer than the recorded one, then run the step 3 feedback probe against its `id` and judge it by the same standard: classified `review` rather than `notice` or `unclear`, no open threads, and processed by step 7b with a `Completed` or `No unresolved Copilot feedback` outcome. A notice does not complete or reset the pair; step 4's notice condition handles it.
1. **Two consecutive clean reviews against the same head SHA** satisfy the Copilot axis. Report both, with their timestamps, so the terminal report shows the confirmation actually happened.
1. **Step 4 sends the confirming review to step 7b under its own `id`**, like every current-head review, and the resolver's status decides what it was. `No unresolved Copilot feedback` means the body stated nothing new, only findings already recorded against an earlier review or text of no concern, so the pair still completes. `Completed` with a pushed commit means the confirmation earned its keep: handle it per step 7b, and reset the count, so the next clean review is again only the first of two. `Completed` with nothing pushed, which is what a confirming review usually produces when the resolver settles every concern in it as restated or of no concern, changed nothing, so the pair still completes. Resetting on it would request reviews until the round budget ran out.

Any push resets the confirmation, whatever its source. Both clean reviews must be against the current head, so a fix, a merge from step 5, or a commit someone else pushes all send the count back to zero.

Each review in a confirmation pair counts as its own round against the step 7c budget.

### 8. Terminal Report, Then Merge

Under a parent continuation block, stop scheduled repair work, print the readiness report from step 8a and return `Status: success` to the named resume target before steps 8b through 8f. Merge policy and any merge decision belong to the parent. Do not create a merge watch, offer a merge or merge on the parent's behalf.

Readiness ends the repair loop, not the watch. From here the skill reports, settles the merge policy, waits for any required approval, offers the merge, and handles the merge whoever performs it.

The merge steps call a second script this plugin ships, the same way as the probe:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/merge-flow" --watch-state WATCH_STATE_JSON policy OWNER REPO BASE
```

If the plugin-root path was not substituted, use `${plugin_root}/scripts/merge-flow` from the same resolved loaded-package root as the probe, and confirm it is executable before invoking it. Every `merge-flow` command prints one JSON value and reports a failed GitHub or git read inside it, including a response it cannot parse, so read the output, not the exit status. A nonzero exit means it printed no JSON: a usage error, `sync` or `panes` run outside a git repository, or `panes` unable to use tmux. **Treat any run that prints no JSON as a failed read**, quoting its stderr: `policy` then knows neither source, a `watch` escalates per step 9, `sync` has not synced, and `panes` could not enumerate peers. This includes a background watch that was stopped before it printed.

#### 8a. Report

The deferred-issue batch below is shared by readiness and step 9 escalation. When this monitor has a parent and a batch needs user approval, return `Status: needs-decision` with the proposed concerns, resolver summary URL, destination constraints and preserved watch state **before** invoking the child. The parent can invoke `create-deferred-issues` in its own user-facing context, obtain the child's mandatory proposal approval and resume the monitor with the recorded outcome. Never turn a continuation block or a monitor readiness result into filing approval. This return takes precedence over step 8's success return. In a standalone monitor, preserve the child's explicit approval exception and its existing continuation.

1. Stop the wait loop. On the `ScheduleWakeup` path, that means `ScheduleWakeup({stop: true})`; on the scheduled-task path, stop the task that resumes this conversation. Step 8c replaces it with a merge watch.
1. Record `READY_HEAD`, the `headRefOid` readiness was declared on. Every later step compares against it.
1. Print the full status table: every check with its state, the Copilot verdict with the SHA it was rendered against, `mergeable`, `mergeStateStatus`, and `reviewDecision` labelled as informational.
1. If review-body findings were processed or previously handled during this watch, include the resolver's final summary comment URL and each originating Copilot review URL. State whether each finding was actionable, previously handled, or required no code change; do not make the user search unrelated PR comments for the disposition.
1. **If the resolver's summary for the current head lists `Needs human review`, lead with them.** Write "Ready, with N advisory requests for human review" in place of a bare "Ready", and quote each request with its review link. Copilot raises these on changes it judges sensitive, and they never block the watch, so this report is the place they reach the user before a merge.
1. **If `mergeStateStatus` is `BLOCKED`, say so before offering to merge.** State that GitHub will refuse the merge until the branch protection requirement is met, and name it if `reviewDecision` identifies it (a required approving review being the usual case). Offering a merge without that caveat presents a PR as ready when it is not yet mergeable.
1. If the PR is a draft, say so; step 8e offers to mark it ready, since GitHub refuses to merge a draft.
1. **File the deferred findings as one batch.** When any resolver summary on the PR lists findings under `### Deferred to follow-up`, invoke the `create-deferred-issues` skill once, before step 8b. It collects them from those summaries and drops any already tracked, so its proposal is the single approval for the watch's follow-up issues:

   ```text
   create-deferred-issues

   Include the findings listed under `### Deferred to follow-up` in the resolver summary comments (starting with `<!-- copilot-feedback-summary -->`, or the legacy `## Copilot Feedback Summary` heading) on <PR URL>, which may already be merged.

   Parent continuation:
   - Caller: monitor-pr
   - Resume target: the step that ran the batch: step 8b, step 8f, or the step 9 report.
   - On `filed`, `none found` or `none approved`: Report the outcome and continue at the resume target.
   - On any other outcome, including `none fileable` and `failure`: Report the findings left unfiled with their source links. From step 8b or step 8f, escalate per Step 9 instead of continuing, without running the batch again there; from step 9, continue the report.
   ```

   Append the outcome to the report. Only those three outcomes continue: every deferred finding is then filed, already tracked, or declined by the user, whose decision is its disposition and stays recorded in the resolver's summary comment. Under `--no-fix`, list the findings the batch would propose instead of invoking it.

#### 8b. Settle the Merge Policy

Do this once per watch, record the result in the watch state, and reuse it on resume. It decides which merge method to offer and whether the PR needs an approval first. Run `merge-flow policy OWNER REPO BASE` as shown above. Its fields:

- **`allowed`**: the merge methods the repository settings allow, intersected with every base-branch rule that limits methods, in the names `gh pr merge` takes (`merge`, `squash`, `rebase`). **The rulesets can narrow what the settings allow**: a repository can allow merge commits and squash while its base-branch ruleset allows only squash, or requires a linear history, which rules merge commits out; offering a merge commit there produces a merge GitHub refuses. `null` means a source could not be read, usually settings hidden from an account without admin access, so a method GitHub refuses could still be in the list. It is unknown, not empty.
- **`candidates`**: the same intersection over whichever sources were read, or `null` when none of them lists methods. Use it only while `allowed` is `null`.
- **`mergeQueue`**: `true` when a merge queue applies to the base branch. The queue then merges the PR with its own method, so name the queue in the offer rather than a method, and expect step 8e's still-`OPEN` outcome.
- **`approvals`**: the highest approving-review count a base-branch rule requires, or `null` when the rules could not be read.
- **`settingsNote`** and **`rulesNote`**: why a source is missing. Quote a note in the report whenever its source is `null`.

Choose the method in this order, and name the source in the report:

1. `allowed` holds exactly one method: use it.
1. The repository's agent config names a method in `allowed`: use it.
1. The harness's durable memory holds a merge-method note for `OWNER/REPO` that names a method in `allowed`: use it.
1. Otherwise propose `merge` if `allowed` includes it, else the first method in `allowed`, and ask the user to confirm it once as part of the merge offer. Record the answer in the harness's durable memory as a per-repository note, such as a Claude Code project memory, so the next watch does not ask again. On a harness without durable memory, say that the choice was not recorded.

A method named by the agent config or a memory note that `allowed` excludes is reported as excluded, not used. When `allowed` is `null`, nothing is verified, so never take the first rule's shortcut and always confirm the method with the user: check named methods against `candidates` instead, propose from `candidates`, or `merge` when it is also `null`, and say that GitHub may refuse the method. When `allowed` is an empty list, no method is left: escalate per step 9 with the `settings` and `rules` lists. Never list every method by default. The offer names one.

The PR **requires approval** before merge when any of these holds, and the report names which:

- A base-branch rule requires approving reviews (`approvals` above 0).
- `reviewDecision` is `REVIEW_REQUIRED`, which is how classic branch protection reports a required review.
- The user's or the project's loaded agent instructions say that this repository's PRs need approval before merge. Such a policy may cover repositories GitHub does not protect, so honor it even when both readings above say no approval is required.

When `approvals` is `null` and neither of the other sources applies, the requirement is unknown: say so in the merge offer, quoting `rulesNote`, rather than presenting the PR as needing no approval.

Then, when the PR requires approval and `reviewDecision` is not `APPROVED`, go to step 8d. Otherwise start the merge watch per step 8c and go to step 8e.

#### 8c. Start the Merge Watch

Start a background watch on the PR **before** making the merge offer, so that it does not wait on the user's answer and the offer does not wait on it. The PR can be merged by anyone, from anywhere; the watch is how the skill learns of it. Run one watch at a time: stop the previous one before starting another.

When a background-command capability can notify this conversation on completion, run the watch through it, for example a tool's `run_in_background` option:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/merge-flow" --watch-state WATCH_STATE_JSON watch OWNER REPO PR_NUMBER READY_HEAD
```

During an approval wait, step 8d adds `--awaited DECISION`, the `reviewDecision` it is waiting to change, with `NONE` standing for an empty decision. The watch prints one JSON line when it exits, and bounds itself: `merge-flow --help` lists its interval, failure limit, and lifetime. Record its task ID in the watch state.

When an accepted scheduler can resume this conversation, create a task at the 2-to-5-minute interval. Each tick first enters step 1 policy preparation and checks the stored merge permission, then runs the same watch for a single read, passing back the counts the previous tick returned and the Unix time of the first tick:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/merge-flow" --watch-state WATCH_STATE_JSON watch OWNER REPO PR_NUMBER READY_HEAD --once --failures F --merged-reads M --started T
```

A `pending` event carries `failures` and `mergedReads` for the next tick; record them, with `T`, in the watch state. Any other event stops the task and is handled below.

When neither capability can run a watch alongside an open question, make the permitted offer per step 8e, or during an approval wait report "Ready, awaiting approval" per step 8d, then end the turn with a resumable checkpoint carrying the step 8 fields, per [Checkpoint and Resume](./references/checkpoint.md). Say that a merge made elsewhere is observed on the next invocation, when the same restriction-filtered dispatcher decides whether post-merge work is permitted.

Treat delivery of a watch event as a new entry: resolve policy at step 1 before refreshing the snapshot and pass the applicable merge/post-merge candidates through the shared dispatcher before acting. A blocked action contributes a would-do line, even if an earlier tick permitted the watch. Handle the permitted watch's `event`:

- **`merged`**: go to step 8f with its `mergeCommit`. When `mergeCommit` is `null`, GitHub reported the merge without naming its commit: report its `error`. When the event carries an `error` and a `mergeCommit`, the PR merged at a head other than `READY_HEAD`, so commits this watch never checked landed: lead the final report with that `error`, and still run step 8f, since the merge stands.
- **`closed`**: report that the PR was closed without merging, and stop. Do not sync or notify.
- **`head`**: a push arrived after readiness, so the readiness verdict no longer holds. Keep the merge policy, clear the offer and the approval wait, re-establish the step 2 wait mechanism, and resume at step 3. A push resets an approval as far as this skill is concerned, whatever GitHub's dismissal rules do.
- **`decision`**: go to step 8d's change rules.
- **`failed`**: escalate per step 9, quoting its `error`.
- **`expired`**: the watch outlived its 24-hour lifetime with the PR still open. Report that, and that `/monitor-pr:monitor` starts a new watch, and stop.

#### 8d. Wait for Approval

If `reviewDecision` is already `CHANGES_REQUESTED`, escalate per step 9 now, quoting the review. Otherwise report "Ready, awaiting approval" with the source step 8b named, and start the step 8c watch with `--awaited` set to the current `reviewDecision`. Do not offer the merge yet, and request reviewers only if the user asks.

When the watch reports a `decision` event:

- **`APPROVED`**: take a fresh step 3 snapshot. If all four axes are still clean at `READY_HEAD`, restart the watch without `--awaited` and go to step 8e; otherwise re-establish the step 2 wait mechanism and dispatch the snapshot per step 4.
- **`CHANGES_REQUESTED`**: escalate per step 9, quoting the review.
- **Anything else**, such as a decision cleared back to `NONE`: restart the watch with `--awaited` set to the new decision.

#### 8e. Offer the Merge

Ask one question naming the chosen method, for example "Merge #361 with a merge commit?". Add the one-time method confirmation when step 8b proposed the method, the unknown-approval caveat when step 8b reported one, and, on a draft, the offer to mark it ready with `gh pr ready PR_NUMBER --repo OWNER/REPO` first. Set the phase to `offered`; only a `head` event, which clears the phase, allows another offer.

**Ask in plain text and end the turn**, rather than through a blocking question tool. The merge watch can re-invoke the session only while the session is idle, so a blocking question would hold back a merge someone else made.

On a yes, merge with the chosen method, pinned to the head readiness was declared on, and without `--delete-branch`, since the head branch is usually checked out in a worktree that deleting it would strand:

```bash
gh pr merge PR_NUMBER --repo OWNER/REPO --merge --match-head-commit READY_HEAD
```

Replace `--merge` with `--squash` or `--rebase` as chosen, or leave the method out when `mergeQueue` is `true`, since the queue sets it.

- **`gh pr merge` succeeds**: report what it said, merged, queued, or auto-merge enabled, and set the phase to `merge requested`. The watch already running reports the merge, and its `merged` event drives step 8f; a queued merge or auto-merge simply takes longer. On the foreground path, where no watch runs, make one `--once` read: `merged` goes to step 8f, and `pending` ends the turn with a checkpoint.
- **The merge was refused**: when the refusal is that the head no longer matches `READY_HEAD`, handle it as a `head` event. Otherwise escalate per step 9 with GitHub's message.

On a no, leave the watch running and say so: a merge made later still triggers step 8f.

#### 8f. After the Merge

Run this once per PR, whichever path observed the merge, and record that it ran in the watch state. When the watch never reached step 8a, run its deferred-issue batch first, resuming here. A `merged` event with a null `mergeCommit` skips the sync, which needs the commit, and runs only the notification.

1. **Fast-forward the base branch.** From this repository's worktree, run:

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/scripts/merge-flow" --watch-state WATCH_STATE_JSON sync OWNER REPO BASE MERGE_SHA
   ```

   It fetches `BASE` from the PR's repository, even in a fork, and fast-forwards whichever worktree has it checked out, usually the main worktree. `synced` is `true` only when the local `BASE` contains the merge. When it is `false`, report its `reason` as written and leave the worktrees as they are: never stash, reset, or force past it.

1. **Notify the other sessions working in this repository.** On Claude Code, list the tmux panes inside this repository's worktrees:

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/scripts/merge-flow" --watch-state WATCH_STATE_JSON panes
   ```

   It prints a JSON array of `{pane, worktree}`. Then list sessions with `ListAgents`: each row ends with its tmux location, such as `tmux plugins:@89.%206`, whose last part is the pane ID. Keep the sessions whose pane ID is in the array, and leave out this session. Send each one a message with `SendMessage`: the PR number and URL, the merge commit SHA, the base branch, and the `sync` result. Keep it informational: each recipient decides whether to merge the base branch into its own work.

   Report three outcomes apart: sessions notified, by name; no peer sessions found; and peers that could not be enumerated, because `panes` failed, the harness has no session listing or messaging, or a session shows no tmux pane. Name any session whose message failed, and continue with the rest.

1. **Print the final line**, with the merge SHA, the sync result, and the sessions notified, then end the watch, stopping any background watch still running.

Steps 8a through 8f remain subject to the shared restriction filter before entry, including when a checkpoint restores a merge phase. A blocked merge or post-merge action contributes a would-do report, not a route, watch, sync or message.

### 9. Escalate

When an escalation rule fires, stop the wait loop, including any scheduled task that resumes this conversation and any step 8c merge watch, and report:

1. What is blocking, in one sentence.
1. What was already tried, including any commits pushed during this watch.
1. Any findings deferred under `--triage-after`, after running step 8a's deferred-issue batch for them, resuming at this report, since the resolver has already resolved their threads.
1. The specific question the user needs to answer.

Then tell the user that `/monitor-pr:monitor` resumes the watch once they have decided.

## Reporting Format

Every tick prints one compact line. On the `ScheduleWakeup` path, pass `noop: true` on a tick where nothing changed, so quiet ticks collapse in the user's terminal. On a scheduled task, report only a material state change; otherwise use the task's quiet-result mechanism if it has one.

```text
▸ 361 · checks 4/5 · copilot stale · mergeable CLEAN · review NONE · round 3/10
```

After readiness, the line names the step 8 phase instead of the round, for example `▸ 361 · ready · awaiting approval (REVIEW_REQUIRED)` or `▸ 361 · ready · watching for merge · offered: merge commit`.

Carry the round counter once any Copilot round has run, so the remaining budget stays visible without having to count back through the transcript. Show `round 3/unlimited` under `--rounds unlimited`, and mark a pending confirmation as `round 3/10 (confirming 1/2)` under `--confirm-clean`.

Any state change prints the full table and passes `noop: false`:

```text
## PR 361 -- state changed

| Check          | State   |
| -------------- | ------- |
| Lint           | pass    |
| Validate       | pass    |
| Scrut tests    | FAIL    |

Copilot: stale (reviewed 1c62d4d, head is 072d742)
Mergeable: MERGEABLE (CLEAN) | Review decision: NONE (informational)

→ Fetching logs for Scrut tests
```

The terminal report uses the same table plus the readiness verdict for all four axes.

## Error Handling

- **No PR for the current branch**: Report that and stop, pointing the user at `/pr`.
- **`gh` not available or not authenticated**: Report the error and stop.
- **PR is a draft**: Monitor normally, but report the draft state in every status line, and say so explicitly before offering to merge in step 8.
- **`mergeable` is `UNKNOWN`**: submit a pending mergeability observation with its diagnostic. Only the helper-owned two-tick retry path may re-poll; at the bound report policy-unavailable with that diagnostic, rather than an unbounded wait or a false clean result.
- **`gh pr checks` exits non-zero**: Not an error. It exits non-zero for pending checks as well as failing ones. Classify from the JSON.
- **No checks configured on the repository**: Not an error. Treat the checks axis as clean and say so explicitly in the report.
- **`sync-with-main:merge` stops on conflicts it cannot resolve**: Escalate with the conflicted file list.
- **`monitor-pr:resolve-copilot-feedback` reports `Partial` or `Failed`**: Escalate with its failure details, final summary comment URL if one was posted, and any originating review URLs.
- **`monitor-pr:resolve-copilot-feedback` reports `Completed` or `No unresolved Copilot feedback` but the next probe still reports open threads**: Escalate per step 9. Open threads should have cleared and did not, so nothing further changes on its own. **A review-body finding is not such a signal.** It stays in the immutable body for the life of the PR, and step 7b's processed-review record is what clears it, so escalating there would stop a PR that is finished. Include the resolver summary and originating review links so the reported disposition is visible beside the immutable finding. Do not invoke the skill again against the same review; step 4's once-per-review `id` guard already prevents it.
- **Copilot never reviews despite an explicit request**: Escalate. Copilot review may be disabled for the repository, in which case the user must decide whether to proceed without it.
- **Copilot answers a retry with another notice**: Escalate with the notice text. An `error` notice that repeats points at Copilot itself; a `no-files` notice means every changed file is excluded from review, which only the user can decide to accept.
- **Push rejected because the remote moved**: Someone else pushed to the branch. Re-poll, sync per step 5, and retry once. If it is rejected again, escalate.
- **`merge-flow` reports a failure**: Handle each field as step 8 describes, quoting its note, `error`, or `reason`. Never read an unknown source as permissive: unknown methods are not an empty list, and an unread ruleset is not a ruleset that requires no approval.
- **Dependabot does not act on a rebase request**: After two quiet ticks with the head SHA unchanged and no reply from Dependabot on the PR, escalate. Do not post the request again for the same head.
