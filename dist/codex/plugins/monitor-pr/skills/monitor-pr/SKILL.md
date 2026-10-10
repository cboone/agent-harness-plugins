---
name: monitor-pr
description: >-
  Watch a PR until checks pass, Copilot feedback is resolved, and it is
  mergeable, fixing failures, then offer the merge; on a Dependabot PR, never
  push: request a rebase. Use for "monitor the pr", "watch the pr", or "wait
  for ci".
argument-hint: "[pr-number] [--interval <duration>] [--ticks <n|unlimited>] [--rounds <n|unlimited>] [--confirm-clean] [--no-fix]"
---

# Monitor PR

<!-- The bin/ and docs/ paths below name files in this repository, not in a project a skill runs against. -->
<!-- validate-plugins: repository-paths -->

Watch a pull request until it is ready to merge, fixing what can be fixed and pausing for what cannot, then offer the merge and bring the base branch and the repository's other sessions up to date once it lands.

This skill starts where `pr` stops. It is not a passive observer: it repairs failing checks, syncs a stale branch, and drives Copilot feedback to resolution. It is also not a continue-at-all-costs skill. When a decision is genuinely the user's, it stops and asks.

## Options

The user may provide these options inline:

- **`<pr-number>`**: Monitor a specific PR instead of the current branch's PR (e.g., `/monitor-pr 361`)
- **--interval `<duration>`**: Override adaptive pacing with a fixed wait (e.g., `--interval 10m`)
- **--ticks `<n|unlimited>`**: Limit foreground polling, including scheduler fallbacks, to `n` ticks before producing a resumable checkpoint. The default is 3; `unlimited` keeps the foreground turn active until a terminal condition or escalation
- **--rounds `<n|unlimited>`**: Change the Copilot round budget from its default of 10. `--rounds unlimited` commits to running until the PR is genuinely clean, however many rounds that takes, and never pauses to ask for more
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

- **Step 5, syncing the branch**: do not invoke `merge-main`. Ask Dependabot instead, once per head SHA:

  ```bash
  gh pr comment PR_NUMBER --repo OWNER/REPO --body "@dependabot rebase"
  ```

  Then wait for the head SHA to change, and resume at step 3. The request works even on a PR whose automatic rebases Dependabot disabled after 30 days. If Dependabot replies that it will not rebase, usually because someone else pushed to the branch, escalate per step 9: `@dependabot recreate` would rebuild the PR but discards those commits, so that is the user's decision.

- **Step 6, failing checks**: diagnose as in step 6a, but do not repair. A failure caused by a secret the Dependabot run cannot read (`Input required and not supplied: token`, an empty cloud credential, a refused OIDC exchange) says nothing about the update: escalate per step 9, reporting it as an environment problem and pointing the user at the `review-dependabot-config` skill. Escalate any other failure per step 9 too, pointing at the `triage-dependabot-prs` skill, which decides whether the update needs work, a migration, or an ignore. Either way the watch stops, because no further tick can change a failure this skill may not repair.
- **Step 7, the Copilot cycle**: automatic Copilot review does not reliably run on Dependabot PRs, so never request one, and never wait for one. A missing review, a review against an older head (which every `@dependabot rebase` produces), or a current-head review classified `notice` leaves the Copilot axis not applicable: report it as `n/a (Dependabot)` and treat the axis as clean. A notice belongs with the missing review because it is one: Copilot reviewed nothing at that head, and since this path never requests a review, no retry can replace it, so holding the axis open would wait forever. Only a Copilot review at the current head matters. Run the step 3 feedback probe and classification here exactly as anywhere else: they are reads, so nothing about this path pushes. Because this path never invokes `resolve-copilot-pr-feedback`, whose fixes would be pushes, read the classified body in full yourself and list every concern it states, wherever it states it. When the probe reports open threads or audit items, the body states any concern, or the classification is `unclear`, report the thread locations, the concerns quoted with the review URL, or the audit item links, and escalate. When none of these holds, the review is clean and the axis is clean.
- **Step 8, the terminal report**: say the PR is a Dependabot PR. The merge policy, merge offer, and post-merge steps apply as for any other PR.

Under `--no-fix`, report the rebase request that would have been posted instead of posting it.

## Skill dependencies

- **Required:** `lint-and-fix`, `merge-main`, `resolve-copilot-pr-feedback`
- **Optional:** None

## Workflow

### 1. Resolve the PR

If the user supplied a PR number, use it. Otherwise derive the PR from the current branch. Take the opening snapshot with one call:

```bash
gh pr view <number-or-omitted> --json number,url,author,headRefName,headRefOid,baseRefName,isDraft,state,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup,mergeCommit
```

Record `OWNER`, `REPO`, and `PR_NUMBER`. The `resolve-copilot-pr-feedback` skill needs all three and does not document how to derive them, so pass them explicitly when invoking it.

If this conversation contains a foreground checkpoint for that same repository and PR, treat the invocation as a continuation: restore its options and watch state using [Checkpoint and Resume](./references/checkpoint.md) before dispatching the opening snapshot. Resume at step 3 with fresh GitHub state. Do not initialize a new watch or reset its action guards merely because the user reran the command.

Also record whether `author.login` is `app/dependabot`, which switches on the rules in [Dependabot PRs](#dependabot-prs).

**If the branch has no PR**, report that and stop, pointing the user at `/pr`.

### 2. Establish the Wait Mechanism

Choose exactly one mechanism and name it on the first tick:

1. **Claude Code**: Prefer `ScheduleWakeup`, which returns control between ticks and keeps the transcript small. Select this mechanism only when the tool is available and accepts the wakeup.
1. **Codex with scheduled tasks**: Create a task that resumes this conversation after the selected interval. Select this mechanism only after successful task creation, and retain its task ID for updates and cancellation. Its prompt must say to resume this `monitor-pr` watch at step 3, retain the recorded PR identity, options, counters, and action guards, and stop the task on escalation, on a terminal report, or at readiness, where step 8c replaces it. Use the watch-state fields in [Checkpoint and Resume](./references/checkpoint.md). On each nonterminal tick, schedule or update the next wakeup using the selected interval. A scheduled task is a new tick, not a delayed final response.
1. **Foreground, including Codex CLI, OpenCode, and scheduler fallbacks**: When no scheduler is available, or scheduling is rejected or fails, announce the fallback and run a foreground polling loop. If replacing an existing scheduled watch, cancel its pending task or wakeup first; if cancellation fails, escalate rather than start a second loop. A blocking `sleep` by itself is not a continuation mechanism: after every sleep, take the step 3 snapshot and dispatch it in the same active turn. Do not print a terminal response merely because a tick is waiting. Stop only on a terminal condition, an escalation, or the `--ticks` foreground limit.

The default `--ticks 3` bounds every foreground loop, including scheduler fallbacks. Count one tick for each step 3 snapshot and its step 4 dispatch, including the opening snapshot. Finish the dispatch before applying the limit; escalation and the step 8 transition at readiness take precedence over a checkpoint. At the limit, checkpoint before the next wait, following [Checkpoint and Resume](./references/checkpoint.md): include the PR URL, current head SHA, all four axes, complete watch state, selected interval, and the exact `/monitor-pr` invocation with the original options. Report a **resumable checkpoint**, not a readiness verdict. `--ticks unlimited` removes this foreground limit, but the user may still interrupt the active session. Never claim that a blocking wait will resume after the agent has returned a final response.

Adaptive intervals by phase, unless `--interval` overrides them:

| Phase                                         | Wait             |
| --------------------------------------------- | ---------------- |
| Checks actively running                       | 2 to 5 minutes   |
| Awaiting a Copilot review at the current head | 5 to 10 minutes  |
| Checks queued, or nothing moving              | 20 to 30 minutes |

When more than one row applies, take the shorter wait. The step 4 fallthrough can reach a tick with checks still running and a Copilot review outstanding at once, and the shorter interval is the one that governs.

During the repair loop on scheduler-backed surfaces there is no wall-clock cap or tick limit. The only budget is on Copilot rounds, per step 7c, and it counts completed reviews rather than elapsed time or poll count. On every foreground path, `--ticks` additionally bounds an individual invocation. After readiness, the step 8c merge watch has its own lifetime of 24 hours. The user can interrupt at any point.

### 3. Take a State Snapshot

Re-run the `gh pr view` call from step 1, and probe Copilot's latest review:

```bash
gh api --paginate --slurp repos/OWNER/REPO/pulls/PR_NUMBER/reviews |
  jq '[.[][] | select((.user.login? // "") as $login | ($login | type) == "string" and (["copilot-pull-request-reviewer", "copilot-pull-request-reviewer[bot]", "copilot", "github-copilot[bot]"] | any(. == ($login | ascii_downcase))))] | last | {id, commit_id, submitted_at, state}'
```

Three details in that command are load-bearing:

- **`--slurp`, and no `--jq`.** Without `--slurp`, `--paginate` emits one JSON array per page and `gh` applies `--jq` to each page separately, so a filter like `[...] | last` returns the last match _per page_ rather than the last overall. On a PR with enough reviews to paginate, that silently reads the wrong review and the skill compares the wrong SHA against the head. `--slurp` collects the pages into an array of arrays, which `.[][]` then flattens. `gh` rejects `--slurp` together with `--jq` (`the --slurp option is not supported with --jq or --template`), so the filtering has to move to a standalone `jq` after a pipe.
- **Every Copilot login, not just one.** REST reports the account as `copilot-pull-request-reviewer[bot]` while GraphQL reports it as `copilot-pull-request-reviewer`, and `copilot` and `github-copilot[bot]` also appear. Matching a single login makes a real review invisible, which reads as "Copilot has not reviewed yet" and sends the skill into a pointless wait and then an escalation. This is the same login set that `resolve-copilot-pr-feedback` matches on, tested the same way: bind the login, lowercase it, then `any(. == ...)` over an explicit array, so `Copilot` matches as it does in `fetch-reviews` and the two never disagree about which review is newest. `.user.login? // ""` and the string check keep a review with no author, or a malformed one, from breaking the comparison.
- **Flag position, and no quotes around the endpoint.** `--paginate` and `--slurp` come before the path, so a `Bash(gh api repos/*)` rule does not match `gh api --paginate repos/*`; the rule has to spell the flags out in order. Leave the endpoint unquoted as shown: the recommended allow rule matches an unquoted path, and a quoted one begins with `"` where the pattern expects `r`, so it fails to match and prompts. Nothing in the endpoint needs quoting, since owner, repo, and PR number contain no shell metacharacters. The trailing `|` ends the line without a continuation backslash, which keeps the command intact when copied.

Copilot's review `state` is always `COMMENTED`, never `APPROVED`, so never treat an approval state as the pass signal.

`id` is the review's stable key. The feedback probe below reads it, and step 7b's once-per-review guard records it. `commit_id` cannot stand in for it, because `--confirm-clean` produces two reviews against the same head and only the `id` tells them apart.

#### The Copilot feedback probe

The metadata above says a review exists and which commit it ran against. It says nothing about what the review found. Probe what is open directly, using the same script `resolve-copilot-pr-feedback` reads with, so the two skills always see the same review data.

This plugin ships its own copy of that script. Invoke it via `bash` followed by the quoted path:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/resolve-copilot-threads" fetch OWNER REPO PR_NUMBER |
  jq -c '{openThreads: length, locations: [.[].location]}'
```

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/resolve-copilot-threads" fetch-reviews OWNER REPO PR_NUMBER |
  jq -c --argjson review_id REVIEW_ID '
    [.[] | select(.id == $review_id)] | last
    | {id, url, commitId}'
```

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/resolve-copilot-threads" audit OWNER REPO PR_NUMBER |
  jq -c '{audited: true, items: [(.uncovered // error("no uncovered"))[] | "\(.surface):\(.id)"]}'
```

Claude Code replaces the plugin-root placeholder with the installed plugin's absolute, version-correct directory before this file reaches you. **If the path was not substituted**, it still begins with `$` rather than `/`; Codex CLI substitutes it only in hook commands, and OpenCode does not substitute it at all. In that case locate the script with `**/monitor-pr/**/scripts/resolve-copilot-threads`, prefer a match inside the harness's own installed-plugin directory, ignore any match under a `.bak` or other backup directory, confirm it with `test -x`, and use that absolute path for the rest of the session.

Eight points govern how the probe is run and read:

- **A failed probe is not a clean probe, and it does not announce itself in the exit status.** Each command writes a diagnostic to stderr and exits nonzero, but the pipeline reports `jq`'s status, and `jq` over empty input emits nothing and exits `0`. So an authentication failure, a rate limit, or a wrong repository shows up as empty output beside the helper's error message, not as a zero count and not as a failing command. Read empty output as "this tick observed nothing", never as "no open threads": leave the Copilot axis unresolved, let the tick fall through to the wait, and probe again next tick. Prefixing the command with `set -o pipefail` makes the status carry the failure, at the cost of the recommended `Bash(bash "*/resolve-copilot-threads" *)` allow rule no longer matching, since the command would then begin with `set`.

- **All three commands are read-only.** `fetch` is a GraphQL query, `fetch-reviews` is a REST read, and `audit` is three REST reads and a GraphQL query; none writes to the PR. So the probe runs unchanged on a Dependabot PR and under `--no-fix`, which is what lets those paths observe Copilot's feedback without invoking a skill that pushes.
- **The audit sees what the other two cannot.** It reports Copilot feedback outside any Copilot thread or review body, in `uncovered`: a Copilot reply inside an unresolved thread someone else opened, a review comment no thread holds, a comment on the PR itself, or a review whose body is not a string. Without it, that feedback would leave the Copilot axis clean while it sat unread. The list is PR-wide and persists like a review body, so the probe projects it as `items`, which is what step 7b records as processed. Each item names its surface (`review-comment:ID`, `issue-comment:ID`, or `review:ID` for a review whose body is not a string), because ids from different GitHub tables can coincide. An absent `audited` field is a failed audit, never an empty one: the filter emits nothing when `audit` fails or when its output lacks the list. After two consecutive ticks with a failed audit, escalate per step 9, quoting the stderr, rather than probing forever.
- **Run it only when the metadata probe's `commit_id` equals `headRefOid`.** A stale review sends the tick to step 7a whatever the probe would say, so running it there spends the whole probe on an answer nothing reads. Nothing is lost by the gate: `fetch` reports every unresolved Copilot thread on the PR, whatever review opened it, so threads left over from an earlier review are still counted the moment a current-head review appears.
- **Project the fields shown on every tick, never the raw result.** `fetch-reviews` returns every Copilot review on the PR with its complete body, and a watch takes this snapshot on every tick. The body is read once per review, by the classification below.
- **Select the review by `id`, not by head SHA.** Under `--confirm-clean` two reviews share one head, and only the newest one's body is the current verdict. `--argjson` is required because REST reports `id` as a number.
- **An all-null result is not a failure, and it is not a match either.** `fetch-reviews` leaves out a review whose body is not a string, so a review the metadata probe found can be absent from its output. jq builds the object anyway, and the filter then answers `{"id":null,"url":null,"commitId":null}`. A null `id` means `fetch-reviews` did not return the review the metadata probe found. That has several causes: a body skipped because it is not a string (the command then prints `Warning: skipping review ID: its body is not a string.` on stderr), or a wrong `REVIEW_ID`. None of them is a clean review, so never satisfy the Copilot axis on a null `id`. Keep the thread count from `fetch`, re-probe on the next tick, and if the `id` is still null after two ticks, escalate per step 9, quoting any skip warning.
- **`fetch-reviews` reads the reviews endpoint the metadata probe already read.** That repetition is deliberate: each command stays standalone and copy-pasteable, and the second read only happens on ticks where a current-head review exists.

#### Classifying a Copilot review

The first time a current-head review `id` appears, read its **complete** body before recording anything about it:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/resolve-copilot-threads" fetch-reviews OWNER REPO PR_NUMBER |
  jq -c --argjson review_id REVIEW_ID '[.[] | select(.id == $review_id)] | last | {id, body}'
```

**A failed read is not a body.** No output at all means the fetch failed, and it prints its cause on stderr; `{"id":null,"body":null}` means the result did not carry that review. Neither is a body to classify: record nothing for that `id`, let the tick fall through to the wait, and read again next tick. Count consecutive failed reads for the `id` in the watch state, and after two, escalate per step 9 quoting the stderr. Only a non-null `id` with a `body` is read and classified. An empty `body` states nothing, and any findings that review has are threads, so it is a `review`.

Never truncate the body or read only its start. Copilot can place the text that says it did not review anywhere in the body, and a prefix discards exactly the evidence the classification needs. A review body is immutable, so one full read per review `id` is enough. Record one classification per `id` in the watch state:

- **`review`**: Copilot reviewed the head. Step 4 dispatches it to step 7b.
- **`notice`**: the body says Copilot did not review the head, for example because it hit an error or because every changed file was excluded. Step 4's notice condition handles it.
- **`unclear`**: the body neither plainly reports a review nor plainly says no review happened. Never treat it as a review, never let it satisfy the Copilot axis, and never count it toward `--confirm-clean`. Escalate per step 9 with the review link and a short quote of what made it ambiguous, so the user decides.

The resolver reads the same body in full during its own run, which makes it a second check. If its summary for a review this skill classified as `review` has a failure row naming that review as a Copilot notice, reclassify that `id` as `notice` and take step 4's notice condition instead of escalating the resolver's outcome. A misreading in either skill therefore cannot turn a notice into a clean axis.

The probe and the classification answer exactly four questions, and step 4 asks no more of them than these: is the current-head review a review, a notice, or unclear, are there open Copilot threads, has step 7b processed this review `id` and with what outcome, and does the audit report Copilot feedback the other two cannot reach. What a review body says, whether a finding is real, already handled, or needs no code change, is `resolve-copilot-pr-feedback`'s judgment, not this skill's, except on the Dependabot path, where no resolver runs.

Reduce the snapshot to the four axes in [Ready Criteria](#ready-criteria).

### 4. Classify and Dispatch

Evaluate in this order and take the first match. Every condition below is work the skill can do now. Waiting is not, so it sits at the end as the fallthrough rather than in the middle of the list: a pending check is nothing the skill can act on, and it must never displace a condition that is.

Two orderings are deliberate:

- **Sync the branch before diagnosing check failures**, because a stale branch is a common cause of them.
- **Act on Copilot findings without waiting for in-flight checks**, because that work is durable: the fixes land whatever the checks go on to do. Requesting a review is perishable by comparison, so both request paths keep a passing-checks precondition. Every push invalidates a review rendered against the old head, which makes a review requested mid-check one that a check fix would throw away, and it spends a round against the step 7c budget either way.

1. **PR is `MERGED`**: go to step 8f with `mergeCommit.oid` from the snapshot, whoever merged it and whether or not the watch reached step 8; the step 8f guard makes a merge already handled a no-op. A merge seen before readiness is reported as such. A snapshot with no merge commit yet is re-read on the next tick rather than sent to step 8f.
1. **PR is `CLOSED`**: terminal. Report that it was closed without merging, and stop.
1. **`mergeStateStatus` is `DIRTY`**: conflicts with the base branch. Go to step 5.
1. **`mergeStateStatus` is `BEHIND`**: go to step 5.
1. **`mergeStateStatus` is `BLOCKED`**: do not treat this as a blocker and do not wait on it, but record it. It means a branch protection rule is unsatisfied, most often a required approving review. Continue evaluating the remaining conditions, and carry the `BLOCKED` state into every status line and into the terminal report per step 8.
1. **Any check concluded with a failure**: go to step 6.
1. **Copilot's newest review against the current head has not been classified yet**: if the probe returned its `id`, read it in full and classify it now, per [classifying a Copilot review](#classifying-a-copilot-review); if the read succeeds, record the classification and evaluate this list again from the top. If the probe returned a null `id`, or the read fails, record nothing, count it, and go straight to the wait at the end of this list: no later Copilot condition may act on an unclassified review. A null probe `id` escalates under the probe's own two-tick rule, and a failed read under the classification section's.
1. **Copilot's newest review against the current head is classified `unclear`**: escalate per step 9 with the review link and a short quote of what made it ambiguous. Never route it to step 7b, and never treat it as clean.
1. **Copilot's newest review against the current head is classified `notice`**: Copilot did not review this head. If no retry has been recorded for that notice's review `id`, request a review once as in step 7a, when checks pass, and record the `id`; this retry is keyed on the notice, so it does not spend the once-per-head request step 7a guards. If a retry is already recorded and the newest review is still that notice after two further ticks, or the review the retry produced is another notice, escalate per step 9 with the notice text. Never route a notice to step 7b, and never treat it as clean.
1. **Copilot reviewed the current head, and the audit failed on this tick and on the one before it**: escalate per step 9, quoting the audit's stderr. A failed audit is one whose projection has no `audited` field. Count consecutive failed-audit ticks in the watch state, and reset the count on any tick whose audit succeeds. A single failure falls through to the conditions below with the audit treated as unresolved, so it can neither dispatch audit items nor let the Copilot axis read as clean; the next tick probes again.
1. **Copilot reviewed the current head, its newest review there is classified `review`, and either step 7b has not already been invoked for that review `id`, or the audit reported an item that no step 7b invocation has recorded at the current head**: go to step 7b. Every current-head review classified `review` goes to the resolver once, whatever its body says: only a full read can tell whether it states a concern, and that read is the resolver's job. Audit items are PR-wide, so a new one dispatches even against a review `id` already processed, and one recorded at the current head does not dispatch again. Checks still running do not hold this back. The `id` clause is step 7b's own once-per-review guard, lifted into the condition that reads it: a review body is immutable, so without the guard every later tick would dispatch the same review again.
1. **Copilot reviewed the current head, step 7b already processed that review, and either its outcome was not `Completed` or `No unresolved Copilot feedback`, or the probe still reports open threads**: escalate per step 9, unless the outcome's failure row names that review as a Copilot notice, in which case reclassify it as `notice` per [classifying a Copilot review](#classifying-a-copilot-review) and evaluate this list again. Both shapes are terminal for that review. A non-clearing outcome never satisfies the axis, and a clearing outcome that leaves threads behind is the case step 7b calls out as unable to change on its own. The `id` guard in the condition above will not send the review to step 7b a second time, and no later tick alters an immutable review, so without this condition the tick falls through to the wait below and the watch never ends. **State the two disqualifying signals rather than a summary of them.** A phrasing such as "this tick has no new input" is true of a cleanly resolved review as well, and this condition sits above the terminal one, so that reading escalates every finished PR instead of merging it. A clean processed review does not belong here: it satisfies the Copilot axis, and its review-body findings are cleared by step 7b's record rather than by a later probe, per the Ready Criteria rules.
1. **Checks pass and Copilot is missing or stale**: go to step 7a.
1. **Checks pass, Copilot reviewed the current head cleanly, `--confirm-clean` is set, and this is the first such review**: go to step 7d to request and await the confirming review.
1. **All four axes clean**: terminal. Go to step 8.
1. **Nothing above matched**: wait, then return to step 3. Checks pending or running with nothing else to act on is the usual case.

Under `--no-fix`, replace steps 5, 6, and 7 with a report of what would have been done, then continue waiting. The step 3 feedback probe still runs: it writes nothing, and without it the report would not be able to say what Copilot actually found.

On a Dependabot PR, steps 5 to 8 follow [Dependabot PRs](#dependabot-prs), and the Copilot conditions above change as that section describes. The classification and `unclear` conditions apply unchanged. A `notice` makes the Copilot axis `n/a (Dependabot)` instead of requesting a retry, and so does a missing or stale review, so the missing-or-stale condition never requests a review either. The audit-failure condition applies unchanged. In place of the dispatch condition, read the classified `review` body in full yourself and escalate if it states any concern, or if the probe reports open threads or audit items. The processed-review condition never matches, because step 7b is never invoked there to record an outcome, and neither does the `--confirm-clean` condition, because no review is ever requested. The probe and the classification read are read-only, so the Dependabot path judges the review without invoking anything that pushes.

### 5. Sync the Branch

Invoke the `merge-main` skill:

```text
merge-main

Parent continuation:
- Caller: monitor-pr
- Resume target: Step 3, take a fresh state snapshot.
- On clean merge and push: Continue immediately to Step 3 without asking the user for confirmation.
- On conflicts requiring a decision, or on any question raised: Stop the watch and escalate per Step 9.
```

`merge-main` has no parent continuation contract of its own and will ask the user directly about uncommitted changes and non-trivial conflicts. That is acceptable here: a question it raises is exactly the kind of decision this skill is supposed to surface rather than guess at. Treat any such question as an escalation.

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
  - Caller: monitor-pr
  - Resume target: Step 6c, push the fix, then Step 3, take a fresh state snapshot.
  - On lint success: Continue immediately to Step 6c without asking the user for confirmation.
  - On lint failure or skipped required lint work: Stop the watch and escalate per Step 9.
  ```

  Branch on its structured `Lint status: <success|no-tools|failure>` output.

- **Generated-tree drift**: run the repository's own build scripts and commit the result. In this repository that is `bin/build-codex-marketplace` and `bin/build-opencode-mirror`.
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

This is the correct mechanism. Do **not** request a review by posting an `@copilot` mention with `gh pr comment`: that adds PR comment noise, and `resolve-copilot-pr-feedback` treats writing PR comments as forbidden outside its own single summary. Request the review at most once per head SHA. If none arrives after a further two ticks, escalate per step 9.

The run check is what separates "Copilot has not started" from "Copilot is mid-review", which the review list alone cannot distinguish: both look like an absent review. Without it, a slow review gets a redundant request, and a review that was never triggered waits out the same two ticks as one that is already running.

#### 7b. Reviewed at the Current Head

Invoke the `resolve-copilot-pr-feedback` skill:

```text
resolve-copilot-pr-feedback OWNER=<owner> REPO=<repo> PR_NUMBER=<number> REVIEW_ID=<review id>

Parent continuation:
- Caller: monitor-pr
- Resume target: Step 3, take a fresh state snapshot.
- On Completed or No unresolved Copilot feedback: Return the final summary comment URL, its Reviews read line and any originating review URLs, then continue immediately to Step 3 without asking the user for confirmation.
- On Partial or Failed: Stop the watch and escalate per Step 9, unless a failure row names REVIEW_ID as a Copilot notice; then reclassify it as a notice per Step 3 and continue at Step 4.
```

Pass the `OWNER`, `REPO`, and `PR_NUMBER` recorded in step 1. That skill's script calls require all three and it does not document how to derive them, so supplying them here saves it from re-deriving them or asking the user. Pass `REVIEW_ID`, the review this dispatch is for: the resolver must read it and list it under `Reviews read`. **A clearing outcome whose `Reviews read` line does not list `REVIEW_ID` does not clear that review.** Treat it like a `Partial` outcome and escalate per step 9, because nothing shows the review was read.

Only invoke it once a review exists at the current head. Invoking it earlier makes it report `No unresolved Copilot feedback` and post a no-op summary comment, which reads as a clean bill of health for code Copilot never saw.

**Invoke it at most once per review.** Record the review `id` each invocation is made against, taken from the step 3 probe, together with the status it reported, the audit `items` at the time, and the head SHA. The resolver runs its own audit and handles those items, so a `Completed` or `No unresolved Copilot feedback` outcome clears them the way it clears review-body findings. An item recorded under any other outcome stays uncleared. **Audit items clear only at the head they were recorded against.** Copilot repeats a review-body finding in each new review until the code changes, so each new head gets it checked again; an audit item is never repeated, and a push can undo the change that settled it. After any push, every audit item dispatches again with the first review at the new head, and the resolver checks it against the current code, so one that still holds costs a `Previously handled` row rather than a new fix. **Do not key this on the head SHA.** Step 7d deliberately requests a second review against the same head, so a SHA key conflates two distinct reviews: it would either suppress the confirming review's findings as already processed or escalate it as a repeat when it is genuinely new. The `id` is the only field that separates them. That record is also what the Copilot axis reads: a review-body finding is cleared by having processed its review, not by a later probe.

**Escalate when a source that should have cleared did not.** After a `Completed` or `No unresolved Copilot feedback` report for a review `id`, escalate per step 9 when the next snapshot's probe still reports open threads. Nothing further will change on its own: a second invocation has no new input to work from, and the step 7c budget will not stop the cycle because it counts completed reviews rather than invocations. A new review or a push is what makes another invocation meaningful.

**Review-body findings are the exception, and getting this backwards is the trap.** An open thread clears when it is resolved, so a repeat there means something genuinely failed. A review-body finding has no thread to resolve and review bodies are immutable, so it stays in that review permanently, for the life of the PR. `resolve-copilot-pr-feedback` records it as handled in a linked summary row and reads that record back on its next run; that record, plus this step's own processed-review record, is the disposition. Escalating on a body that cannot change would turn every noted or previously handled review-body finding into a false escalation on a PR that is finished. Retain the final summary comment URL and the originating review URL for terminal or escalation reporting.

#### 7c. Round Budget

Count Copilot rounds for this watch. The default budget is **10**. On reaching it, stop and report per step 9, then ask whether to continue and for how many more rounds.

This is a budget, not a verdict about progress. **Do not treat the shape of the finding counts as a signal.** Copilot swings: a round with many findings is regularly followed by a quiet one and then a busy one again, and the count going up does not mean the work is diverging. Four rounds is often not enough to finish, so a watch that is still finding real defects at round 6 or 8 is behaving normally, not thrashing.

What matters is whether the findings are real. Keep going while each round produces valid, fixable defects, and escalate early per step 9 only when a round produces something that needs the user's judgment, per the escalation rules in step 6d. The budget exists to bound an unattended watch, not to second-guess a productive one.

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

Readiness ends the repair loop, not the watch. From here the skill reports, settles the merge policy, waits for any required approval, offers the merge, and handles the merge whoever performs it.

The merge steps call a second script this plugin ships, the same way as the probe:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/merge-flow" policy OWNER REPO BASE
```

If the plugin-root path was not substituted, locate `**/monitor-pr/**/scripts/merge-flow` exactly as the probe section describes for its script. Every `merge-flow` command prints one JSON value and reports a failed GitHub or git read inside it, including a response it cannot parse, so read the output, not the exit status. A nonzero exit means it printed no JSON: a usage error, `sync` or `panes` run outside a git repository, or `panes` unable to use tmux. **Treat any run that prints no JSON as a failed read**, quoting its stderr: `policy` then knows neither source, a `watch` escalates per step 9, `sync` has not synced, and `panes` could not enumerate peers. This includes a background watch that was stopped before it printed.

#### 8a. Report

1. Stop the wait loop. On the `ScheduleWakeup` path, that means `ScheduleWakeup({stop: true})`; on the scheduled-task path, stop the task that resumes this conversation. Step 8c replaces it with a merge watch.
1. Record `READY_HEAD`, the `headRefOid` readiness was declared on. Every later step compares against it.
1. Print the full status table: every check with its state, the Copilot verdict with the SHA it was rendered against, `mergeable`, `mergeStateStatus`, and `reviewDecision` labelled as informational.
1. If review-body findings were processed or previously handled during this watch, include the resolver's final summary comment URL and each originating Copilot review URL. State whether each finding was actionable, previously handled, or required no code change; do not make the user search unrelated PR comments for the disposition.
1. **If the resolver's summary for the current head lists `Requests for human review`, lead with them.** Write "Ready, with N advisory requests for human review" in place of a bare "Ready", and quote each request with its review link. Copilot raises these on changes it judges sensitive, and they never block the watch, so this report is the place they reach the user before a merge.
1. **If `mergeStateStatus` is `BLOCKED`, say so before offering to merge.** State that GitHub will refuse the merge until the branch protection requirement is met, and name it if `reviewDecision` identifies it (a required approving review being the usual case). Offering a merge without that caveat presents a PR as ready when it is not yet mergeable.
1. If the PR is a draft, say so; step 8e offers to mark it ready, since GitHub refuses to merge a draft.

#### 8b. Settle the Merge Policy

Do this once per watch, record the result in the watch state, and reuse it on resume. It decides which merge method to offer and whether the PR needs an approval first. Run `merge-flow policy OWNER REPO BASE` as shown above. Its fields:

- **`allowed`**: the merge methods the repository settings allow, intersected with every base-branch rule that limits methods, in the names `gh pr merge` takes (`merge`, `squash`, `rebase`). **The rulesets can narrow what the settings allow**: a repository can allow merge commits and squash while its base-branch ruleset allows only squash, or requires a linear history, which rules merge commits out; offering a merge commit there produces a merge GitHub refuses. `null` means no source supplied a method list, usually settings hidden from an account without admin access on a branch whose rules do not limit methods. It is unknown, not empty.
- **`mergeQueue`**: `true` when a merge queue applies to the base branch. The queue then merges the PR with its own method, so name the queue in the offer rather than a method, and expect step 8e's still-`OPEN` outcome.
- **`approvals`**: the highest approving-review count a base-branch rule requires, or `null` when the rules could not be read.
- **`settingsNote`** and **`rulesNote`**: why a source is missing, for example that the settings are hidden from an account without admin access, or that the base branch was not found. Quote a note in the report whenever its source is `null`.

Choose the method in this order, and name the source in the report:

1. `allowed` holds exactly one method: use it.
1. The repository's agent config names a method in `allowed`: use it.
1. The harness's durable memory holds a merge-method note for `OWNER/REPO` that names a method in `allowed`: use it.
1. Otherwise propose `merge` if `allowed` includes it, else the first method in `allowed`, and ask the user to confirm it once as part of the merge offer. Record the answer in the harness's durable memory as a per-repository note, such as a Claude Code project memory, so the next watch does not ask again. On a harness without durable memory, say that the choice was not recorded.

A method named by the agent config or a memory note that `allowed` excludes is reported as excluded, not used. When `allowed` is `null`, the named methods cannot be checked: use them in the same order, say that GitHub may refuse them, and with neither available propose `merge`. When `allowed` is an empty list, no method is left: escalate per step 9 with the `settings` and `rules` lists. Never list every method by default. The offer names one.

The PR **requires approval** before merge when any of these holds, and the report names which:

- A base-branch rule requires approving reviews (`approvals` above 0).
- `reviewDecision` is `REVIEW_REQUIRED`, which is how classic branch protection reports a required review.
- The user's or the project's loaded agent instructions say that this repository's PRs need approval before merge. Such a policy may cover repositories GitHub does not protect, so honor it even when both readings above say no approval is required.

When `approvals` is `null` and neither of the other sources applies, the requirement is unknown: say so in the merge offer, quoting `rulesNote`, rather than presenting the PR as needing no approval.

Then, when the PR requires approval and `reviewDecision` is not `APPROVED`, go to step 8d. Otherwise start the merge watch per step 8c and go to step 8e.

#### 8c. Start the Merge Watch

Start a background watch on the PR **before** making the merge offer, so that it does not wait on the user's answer and the offer does not wait on it. The PR can be merged by anyone, from anywhere; the watch is how the skill learns of it. Run one watch at a time: stop the previous one before starting another.

On Claude Code, run the watch with the `Bash` tool's `run_in_background` option. The harness re-invokes the session when it exits:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/merge-flow" watch OWNER REPO PR_NUMBER READY_HEAD
```

During an approval wait, step 8d adds `--awaited DECISION`, the `reviewDecision` it is waiting to change, with `NONE` standing for an empty decision. The watch polls every 60 seconds. After each failed read it waits the interval times the failure count, at most 15 minutes, and after 8 consecutive failures it exits with a `failed` event. It exits with `expired` after 24 hours, and prints one JSON line when it exits. Record its task ID in the watch state.

On Codex with scheduled tasks, create a task that resumes this conversation at the 2-to-5-minute interval. On each tick it runs one read, `gh pr view PR_NUMBER --repo OWNER/REPO --json state,reviewDecision,headRefOid,mergeCommit`, and applies the same events the script reports: `merged` only once `mergeCommit` is set, `closed`, `head` when `headRefOid` differs from `READY_HEAD`, and `decision` when an awaited `reviewDecision` changed. It also counts consecutive failed reads and reports `failed` after 8, and reports `expired` 24 hours after the watch started; record the start time and the failure count in the watch state so the bounds hold across ticks. On any event, stop the task and handle the event below.

On the foreground path, a harness with neither a background task nor a scheduled task, no watch can run alongside an open question. Claude Code always has the background task, even when `ScheduleWakeup` was unavailable, so this path is for the others. Make the offer per step 8e, or during an approval wait report "Ready, awaiting approval" per step 8d, then end the turn with a resumable checkpoint carrying the step 8 fields, per [Checkpoint and Resume](./references/checkpoint.md). Say that a merge made elsewhere is picked up when `/monitor-pr` next runs, since step 4 sends a merged PR to step 8f.

Handle the watch's `event`:

- **`merged`**: go to step 8f with its `mergeCommit`. When `mergeCommit` is `null`, GitHub reported the merge without naming its commit: report its `error`, skip the sync, which needs the commit, and still notify the other sessions that the PR merged.
- **`closed`**: report that the PR was closed without merging, and stop. Do not sync or notify.
- **`head`**: a push arrived after readiness, so the readiness verdict no longer holds. Keep the merge policy, clear the offer and the approval wait, re-establish the step 2 wait mechanism, and resume at step 3. A push resets an approval as far as this skill is concerned, whatever GitHub's dismissal rules do.
- **`decision`**: go to step 8d's change rules.
- **`failed`**: escalate per step 9, quoting its `error`.
- **`expired`**: the watch outlived its 24-hour lifetime with the PR still open. Report that, and that `/monitor-pr` starts a new watch, and stop.

#### 8d. Wait for Approval

If `reviewDecision` is already `CHANGES_REQUESTED`, escalate per step 9 now, quoting the review. Otherwise report "Ready, awaiting approval" with the source step 8b named, and start the step 8c watch with `--awaited` set to the current `reviewDecision`. Do not offer the merge yet, and request reviewers only if the user asks.

When the watch reports a `decision` event:

- **`APPROVED`**: take a fresh step 3 snapshot. If all four axes are still clean at `READY_HEAD`, restart the watch without `--awaited` and go to step 8e; otherwise re-establish the step 2 wait mechanism and dispatch the snapshot per step 4.
- **`CHANGES_REQUESTED`**: escalate per step 9, quoting the review.
- **Anything else**, such as a decision cleared back to `NONE`: restart the watch with `--awaited` set to the new decision.

#### 8e. Offer the Merge

Ask one question naming the chosen method, for example "Merge #361 with a merge commit?". Add the one-time method confirmation when step 8b proposed the method, the unknown-approval caveat when step 8b reported one, and, on a draft, the offer to mark it ready with `gh pr ready PR_NUMBER --repo OWNER/REPO` first. Record that the offer was made at `READY_HEAD`, and do not ask again for that head.

**Ask in plain text and end the turn**, rather than through a blocking question tool. The merge watch can re-invoke the session only while the session is idle, so a blocking question would hold back a merge someone else made.

On a yes, merge with the chosen method, pinned to the head readiness was declared on, and without `--delete-branch`, since the head branch is usually checked out in a worktree that deleting it would strand:

```bash
gh pr merge PR_NUMBER --repo OWNER/REPO --merge --match-head-commit READY_HEAD
```

Replace `--merge` with `--squash` or `--rebase` as chosen, or leave the method out when `mergeQueue` is `true`, since the queue sets it. Then read the result with `gh pr view PR_NUMBER --repo OWNER/REPO --json state,mergeCommit`:

- **`MERGED` with a `mergeCommit`**: stop the background watch, and go to step 8f. If the watch reports the same merge later, the step 8f guard makes that report a no-op.
- **Still `OPEN`**: GitHub queued the merge, or enabled auto-merge because a requirement is still pending; `gh pr merge` says which. Report it, record the phase as `merge requested`, and leave the watch running: its `merged` event drives step 8f.
- **The merge was refused**: when the refusal is that the head no longer matches `READY_HEAD`, handle it as a `head` event. Otherwise escalate per step 9 with GitHub's message.

On a no, leave the watch running and say so: a merge made later still triggers step 8f.

#### 8f. After the Merge

Run this once per merge commit SHA, whichever path observed the merge, and record the SHA in the watch state. Never run it with an empty SHA: a `MERGED` state without a merge commit is re-read, never recorded.

1. **Fast-forward the base branch.** From this repository's worktree, run:

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/scripts/merge-flow" sync OWNER REPO BASE MERGE_SHA
   ```

   It fetches `BASE` from the remote whose URL names `OWNER/REPO`, which in a fork is not `origin`, checks that the fetched branch contains the merge, and fast-forwards whichever worktree has `BASE` checked out, usually the main worktree, or the branch ref when none does. It never stashes, resets, or force-updates a local branch. `synced` is `true` only when the local `BASE` contains the merge. When it is `false`, report its `reason` as written and leave the worktrees as they are.

1. **Notify the other sessions working in this repository.** On Claude Code, list the tmux panes inside this repository's worktrees:

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/scripts/merge-flow" panes
   ```

   It prints a JSON array of `{pane, path, worktree}`, matching each pane's directory to a worktree by whole path component, so a sibling directory such as `repo-old` never matches `repo`. Then list sessions with `ListAgents`: each row ends with its tmux location, such as `tmux plugins:@89.%206`, whose last part is the pane ID. Keep the sessions whose pane ID is in the array, and leave out this session. Send each one a message with `SendMessage`: the PR number and URL, the merge commit SHA, the base branch, and the `sync` result. Keep it informational: each recipient decides whether to merge the base branch into its own work.

   Report three outcomes apart: sessions notified, by name; no peer sessions found; and peers that could not be enumerated, because `panes` failed, the harness has no session listing or messaging, or a session shows no tmux pane. Name any session whose message failed, and continue with the rest.

1. **Print the final line**, with the merge SHA, the sync result, and the sessions notified, then end the watch, stopping any background watch still running.

Under `--no-fix`, steps 8b to 8f report what they would do, the method and the approval requirement included, and do none of it: no merge watch, no merge, no sync, and no messages.

### 9. Escalate

When an escalation rule fires, stop the wait loop, including any scheduled task that resumes this conversation and any step 8c merge watch, and report:

1. What is blocking, in one sentence.
1. What was already tried, including any commits pushed during this watch.
1. The specific question the user needs to answer.

Then tell the user that `/monitor-pr` resumes the watch once they have decided.

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
- **`mergeable` is `UNKNOWN`**: GitHub is still computing it. Treat as pending and re-poll. Do not report it as a failure.
- **`gh pr checks` exits non-zero**: Not an error. It exits non-zero for pending checks as well as failing ones. Classify from the JSON.
- **No checks configured on the repository**: Not an error. Treat the checks axis as clean and say so explicitly in the report.
- **`merge-main` stops on conflicts it cannot resolve**: Escalate with the conflicted file list.
- **`resolve-copilot-pr-feedback` reports `Partial` or `Failed`**: Escalate with its failure details, final summary comment URL if one was posted, and any originating review URLs.
- **`resolve-copilot-pr-feedback` reports `Completed` or `No unresolved Copilot feedback` but the next probe still reports open threads**: Escalate per step 9. Open threads should have cleared and did not, so nothing further changes on its own. **A review-body finding is not such a signal.** It stays in the immutable body for the life of the PR, and step 7b's processed-review record is what clears it, so escalating there would stop a PR that is finished. Include the resolver summary and originating review links so the reported disposition is visible beside the immutable finding. Do not invoke the skill again against the same review; step 4's once-per-review `id` guard already prevents it.
- **Copilot never reviews despite an explicit request**: Escalate. Copilot review may be disabled for the repository, in which case the user must decide whether to proceed without it.
- **Copilot answers a retry with another notice**: Escalate with the notice text. An `error` notice that repeats points at Copilot itself; a `no-files` notice means every changed file is excluded from review, which only the user can decide to accept.
- **Push rejected because the remote moved**: Someone else pushed to the branch. Re-poll, sync per step 5, and retry once. If it is rejected again, escalate.
- **`merge-flow` prints no JSON**: Treat it as a failed read, per the step 8 introduction, and quote its stderr.
- **A `merge-flow policy` source is `null`**: Report its note. Never read an unknown source as permissive: unknown methods are not an empty list, and an unread ruleset is not a ruleset that requires no approval.
- **`merge-flow sync` reports `synced: false`**: Report its `reason` as written and leave the worktrees untouched. Never stash, reset, or force past it; the merge itself stands, and the peer messages say the base branch was not synced.
- **`gh pr merge` exits 0 but the PR is still open**: The merge was queued or auto-merge was enabled. Keep the merge watch running and let its `merged` event drive step 8f.
- **A peer session cannot be messaged**: Name it, and continue with the rest. The merge and the sync do not depend on it.
- **Dependabot does not act on a rebase request**: After two quiet ticks with the head SHA unchanged and no reply from Dependabot on the PR, escalate. Do not post the request again for the same head.
