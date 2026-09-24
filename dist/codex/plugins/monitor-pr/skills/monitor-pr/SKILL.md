---
name: monitor-pr
description: >-
  Watch a PR until checks pass, Copilot feedback is resolved, and it is
  mergeable, fixing failures. Use for "monitor the pr" or "wait for ci".
---

# Monitor PR

<!-- The bin/ and docs/ paths below name files in this repository, not in a project a skill runs against. -->
<!-- validate-plugins: repository-paths -->

Watch a pull request until it is ready to merge, fixing what can be fixed and pausing for what cannot.

This skill starts where `pr` stops. It is not a passive observer: it repairs failing checks, syncs a stale branch, and drives Copilot feedback to resolution. It is also not a continue-at-all-costs skill. When a decision is genuinely the user's, it stops and asks.

## Options

The user may provide these options inline:

- **`<pr-number>`**: Monitor a specific PR instead of the current branch's PR (e.g., `/monitor-pr 361`)
- **--interval `<duration>`**: Override adaptive pacing with a fixed wait (e.g., `--interval 10m`)
- **--ticks `<n|unlimited>`**: Limit foreground polling, including scheduler fallbacks, to `n` ticks before producing a resumable checkpoint. The default is 3; `unlimited` keeps the foreground turn active until a terminal condition or escalation
- **--rounds `<n|unlimited>`**: Change the Copilot round budget from its default of 10. `--rounds unlimited` commits to running until the PR is genuinely clean, however many rounds that takes, and never pauses to ask for more
- **--confirm-clean**: Require two consecutive clean Copilot reviews rather than one. After the first clean review, request another explicitly and wait for it
- **--no-fix**: Observe and report only. Never push, never invoke a fixing skill, never request a review

## Ready Criteria

The watch ends when all four axes are clean at the same time. Partial greenness is not readiness.

| Axis         | Clean when                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Checks       | Every check in `statusCheckRollup` has concluded successfully, or the repository has no checks configured                                                                                                                                                                                                                                                                                                                                                               |
| Copilot      | A Copilot review exists whose commit SHA equals the current head, and the step 3 feedback probe reports no open threads, no format drift, and either no review-body findings or only findings step 7b has already cleared, per the rules below. Under `--confirm-clean`, two consecutive such reviews against that same head. On a Dependabot PR, clean unless the probe reports findings or drift against a current-head review, per [Dependabot PRs](#dependabot-prs) |
| Mergeability | `mergeable` is `MERGEABLE` and `mergeStateStatus` is neither `DIRTY` nor `BEHIND`. `BLOCKED` counts as clean but must be reported, per the rule below                                                                                                                                                                                                                                                                                                                   |
| PR state     | `OPEN` and not merged or closed                                                                                                                                                                                                                                                                                                                                                                                                                                         |

Five rules that follow from this and are easy to get wrong:

- **A review-body finding the resolver has already handled still shows in the probe, and the axis is still clean.** Review bodies are immutable, so `fetch-reviews` reports that finding against that review for as long as the review exists; it never goes to zero the way an open thread does. What clears it is step 7b's record of having processed that review `id`, not a later probe. Waiting for the count to drop would hold a finished PR open forever.
- **A review processed with any other outcome never becomes clean, and never waits.** Only `Completed` and `No unresolved Copilot feedback` clear a review's findings. A `Partial` or `Failed` outcome leaves the axis dirty, while the once-per-review `id` guard in step 4 stops the review from being sent to step 7b again, so no later tick can change anything. Escalate per step 9 instead of falling through to the wait branch. This matters on a resumed watch: the original outcome already escalated and ended the watch, and the checkpoint restores the guard, so the wait branch is exactly where such a review would otherwise land.
- **A Copilot review against an older SHA does not count.** Copilot reviews are pinned to the commit they ran against, so every push this skill makes invalidates the previous review by construction. A fix always sends the loop back around.
- **`reviewDecision` does not gate.** A human `CHANGES_REQUESTED` will not stop this skill from declaring the PR ready. Report `reviewDecision` in every status line and in the terminal report so an outstanding human objection stays visible, but never wait on it.
- **`BLOCKED` does not gate either, but it must be reported.** Requiring `mergeStateStatus` to be `CLEAN` would be the stricter reading of "ready to merge", and it is deliberately not what this skill does: on a repository whose branch protection requires an approving review, nothing the skill can do will ever satisfy it, so the watch would run until its round budget expired and then report failure on a PR that is finished. Treat `BLOCKED` as ready-with-a-caveat instead. **A terminal report that omits an active `BLOCKED` state is wrong**, because it tells the user the PR is ready to merge when GitHub will refuse the merge. Name the state and say what is unsatisfied.

## Dependabot PRs

A PR whose `author.login` in the step 1 snapshot is `app/dependabot` belongs to Dependabot, and Dependabot owns its branch. Once anyone else pushes to that branch, Dependabot stops rebasing it, and a later `@dependabot recreate` discards the push. So on a Dependabot PR this skill never pushes, and four steps change:

- **Step 5, syncing the branch**: do not invoke `merge-main`. Ask Dependabot instead, once per head SHA:

  ```bash
  gh pr comment PR_NUMBER --repo OWNER/REPO --body "@dependabot rebase"
  ```

  Then wait for the head SHA to change, and resume at step 3. The request works even on a PR whose automatic rebases Dependabot disabled after 30 days. If Dependabot replies that it will not rebase, usually because someone else pushed to the branch, escalate per step 9: `@dependabot recreate` would rebuild the PR but discards those commits, so that is the user's decision.

- **Step 6, failing checks**: diagnose as in step 6a, but do not repair. A failure caused by a secret the Dependabot run cannot read (`Input required and not supplied: token`, an empty cloud credential, a refused OIDC exchange) says nothing about the update: escalate per step 9, reporting it as an environment problem and pointing the user at the `review-dependabot-config` skill. Escalate any other failure per step 9 too, pointing at the `triage-dependabot-prs` skill, which decides whether the update needs work, a migration, or an ignore. Either way the watch stops, because no further tick can change a failure this skill may not repair.
- **Step 7, the Copilot cycle**: automatic Copilot review does not reliably run on Dependabot PRs, so never request one, and never wait for one. A missing review, or a review against an older head (which every `@dependabot rebase` produces), leaves the Copilot axis not applicable: report it as `n/a (Dependabot)` and treat the axis as clean. Only a Copilot review at the current head matters, and the step 3 feedback probe is what decides whether it did anything. Run the probe here exactly as anywhere else: both of its commands are reads, so nothing about this path pushes. When it reports open threads, review-body findings, or format drift, report the thread locations and finding count, or the drift with the review URL, and escalate rather than invoking `resolve-copilot-pr-feedback`, whose fixes would be pushes. When it reports none of the three, the review is clean and the axis is clean.
- **Step 8, the terminal report**: say the PR is a Dependabot PR, and merge only with a method the repository allows, as for any other PR.

Under `--no-fix`, report the rebase request that would have been posted instead of posting it.

## Skill dependencies

- **Required:** `lint-and-fix`, `merge-main`, `resolve-copilot-pr-feedback`
- **Optional:** None

## Workflow

### 1. Resolve the PR

If the user supplied a PR number, use it. Otherwise derive the PR from the current branch. Take the opening snapshot with one call:

```bash
gh pr view <number-or-omitted> --json number,url,author,headRefName,headRefOid,baseRefName,isDraft,state,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup
```

Record `OWNER`, `REPO`, and `PR_NUMBER`. The `resolve-copilot-pr-feedback` skill needs all three and does not document how to derive them, so pass them explicitly when invoking it.

If this conversation contains a foreground checkpoint for that same repository and PR, treat the invocation as a continuation: restore its options and watch state using [Checkpoint and Resume](./references/checkpoint.md) before dispatching the opening snapshot. Resume at step 3 with fresh GitHub state. Do not initialize a new watch or reset its action guards merely because the user reran the command.

Also record whether `author.login` is `app/dependabot`, which switches on the rules in [Dependabot PRs](#dependabot-prs).

**If the branch has no PR**, report that and stop, pointing the user at `/pr`.

### 2. Establish the Wait Mechanism

Choose exactly one mechanism and name it on the first tick:

1. **Claude Code**: Prefer `ScheduleWakeup`, which returns control between ticks and keeps the transcript small. Select this mechanism only when the tool is available and accepts the wakeup.
1. **Codex with scheduled tasks**: Create a task that resumes this conversation after the selected interval. Select this mechanism only after successful task creation, and retain its task ID for updates and cancellation. Its prompt must say to resume this `monitor-pr` watch at step 3, retain the recorded PR identity, options, counters, and action guards, and stop the task on a terminal report or escalation. Use the watch-state fields in [Checkpoint and Resume](./references/checkpoint.md). On each nonterminal tick, schedule or update the next wakeup using the selected interval. A scheduled task is a new tick, not a delayed final response.
1. **Foreground, including Codex CLI, OpenCode, and scheduler fallbacks**: When no scheduler is available, or scheduling is rejected or fails, announce the fallback and run a foreground polling loop. If replacing an existing scheduled watch, cancel its pending task or wakeup first; if cancellation fails, escalate rather than start a second loop. A blocking `sleep` by itself is not a continuation mechanism: after every sleep, take the step 3 snapshot and dispatch it in the same active turn. Do not print a terminal response merely because a tick is waiting. Stop only on a terminal condition, an escalation, or the `--ticks` foreground limit.

The default `--ticks 3` bounds every foreground loop, including scheduler fallbacks. Count one tick for each step 3 snapshot and its step 4 dispatch, including the opening snapshot. Finish the dispatch before applying the limit; readiness and escalation take precedence over a checkpoint. At the limit, checkpoint before the next wait, following [Checkpoint and Resume](./references/checkpoint.md): include the PR URL, current head SHA, all four axes, complete watch state, selected interval, and the exact `/monitor-pr` invocation with the original options. Report a **resumable checkpoint**, not a readiness verdict. `--ticks unlimited` removes this foreground limit, but the user may still interrupt the active session. Never claim that a blocking wait will resume after the agent has returned a final response.

Adaptive intervals by phase, unless `--interval` overrides them:

| Phase                                         | Wait             |
| --------------------------------------------- | ---------------- |
| Checks actively running                       | 2 to 5 minutes   |
| Awaiting a Copilot review at the current head | 5 to 10 minutes  |
| Checks queued, or nothing moving              | 20 to 30 minutes |

When more than one row applies, take the shorter wait. The step 4 fallthrough can reach a tick with checks still running and a Copilot review outstanding at once, and the shorter interval is the one that governs.

On scheduler-backed surfaces there is no wall-clock cap or tick limit. The only budget is on Copilot rounds, per step 7c, and it counts completed reviews rather than elapsed time or poll count. On every foreground path, `--ticks` additionally bounds an individual invocation. The user can interrupt at any point.

### 3. Take a State Snapshot

Re-run the `gh pr view` call from step 1, and probe Copilot's latest review:

```bash
gh api --paginate --slurp repos/OWNER/REPO/pulls/PR_NUMBER/reviews |
  jq '[.[][] | select((.user.login? // "") as $login | ["copilot-pull-request-reviewer", "copilot-pull-request-reviewer[bot]", "copilot", "github-copilot[bot]"] | any(. == $login))] | last | {id, commit_id, submitted_at, state}'
```

Three details in that command are load-bearing:

- **`--slurp`, and no `--jq`.** Without `--slurp`, `--paginate` emits one JSON array per page and `gh` applies `--jq` to each page separately, so a filter like `[...] | last` returns the last match _per page_ rather than the last overall. On a PR with enough reviews to paginate, that silently reads the wrong review and the skill compares the wrong SHA against the head. `--slurp` collects the pages into an array of arrays, which `.[][]` then flattens. `gh` rejects `--slurp` together with `--jq` (`the --slurp option is not supported with --jq or --template`), so the filtering has to move to a standalone `jq` after a pipe.
- **Every Copilot login, not just one.** REST reports the account as `copilot-pull-request-reviewer[bot]` while GraphQL reports it as `copilot-pull-request-reviewer`, and `copilot` and `github-copilot[bot]` also appear. Matching a single login makes a real review invisible, which reads as "Copilot has not reviewed yet" and sends the skill into a pointless wait and then an escalation. This is the same login set that `resolve-copilot-pr-feedback` matches on, tested the same way: bind the login, then `any(. == $login)` over an explicit array. `IN(...)` would also work on any jq since 1.5, but the array form is the pattern already established in this repository, and `.user.login? // ""` keeps a review with no author from breaking the comparison.
- **Flag position, and no quotes around the endpoint.** `--paginate` and `--slurp` come before the path, so a `Bash(gh api repos/*)` rule does not match `gh api --paginate repos/*`; the rule has to spell the flags out in order. Leave the endpoint unquoted as shown: the recommended allow rule matches an unquoted path, and a quoted one begins with `"` where the pattern expects `r`, so it fails to match and prompts. Nothing in the endpoint needs quoting, since owner, repo, and PR number contain no shell metacharacters. The trailing `|` ends the line without a continuation backslash, which keeps the command intact when copied.

Copilot's review `state` is always `COMMENTED`, never `APPROVED`, so never treat an approval state as the pass signal.

`id` is the review's stable key. The feedback probe below reads it, and step 7b's once-per-review guard records it. `commit_id` cannot stand in for it, because `--confirm-clean` produces two reviews against the same head and only the `id` tells them apart.

#### The Copilot feedback probe

The metadata above says a review exists and which commit it ran against. It says nothing about what the review found, and the step 4 Copilot condition is entirely about what it found. Probe that directly, using the same script `resolve-copilot-pr-feedback` classifies with, so the two skills never disagree about what counts as clean.

This plugin ships its own copy of that script. Invoke it via `bash` followed by the quoted path:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/resolve-copilot-threads" fetch OWNER REPO PR_NUMBER |
  jq -c '{openThreads: length, locations: [.[].location]}'
```

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/resolve-copilot-threads" fetch-reviews OWNER REPO PR_NUMBER |
  jq -c --argjson review_id REVIEW_ID '
    [.[] | select(.id == $review_id)] | last
    | {id, url, hasFormatDrift, findings: (.findings | length)}'
```

Claude Code replaces the plugin-root placeholder with the installed plugin's absolute, version-correct directory before this file reaches you. **If the path was not substituted**, it still begins with `$` rather than `/`; Codex CLI substitutes it only in hook commands, and OpenCode does not substitute it at all. In that case locate the script with `**/monitor-pr/**/scripts/resolve-copilot-threads`, prefer a match inside the harness's own installed-plugin directory, ignore any match under a `.bak` or other backup directory, confirm it with `test -x`, and use that absolute path for the rest of the session.

Seven points govern how the probe is run and read:

- **A failed probe is not a clean probe, and it does not announce itself in the exit status.** Both commands write a diagnostic to stderr and exit nonzero, but the pipeline reports `jq`'s status, and `jq` over empty input emits nothing and exits `0`. So an authentication failure, a rate limit, or a wrong repository shows up as empty output beside the helper's error message, not as a zero count and not as a failing command. Read empty output as "this tick observed nothing", never as "no open threads" or "no findings": leave the Copilot axis unresolved, let the tick fall through to the wait, and probe again next tick. Prefixing the command with `set -o pipefail` makes the status carry the failure, at the cost of the recommended `Bash(bash "*/resolve-copilot-threads" *)` allow rule no longer matching, since the command would then begin with `set`.

- **Both commands are read-only.** `fetch` is a GraphQL query and `fetch-reviews` is a REST read; neither writes to the PR. So the probe runs unchanged on a Dependabot PR and under `--no-fix`, which is what lets those paths observe findings and drift without invoking a skill that pushes.
- **Run it only when the metadata probe's `commit_id` equals `headRefOid`.** A stale review sends the tick to step 7a whatever the probe would say, so running it there spends two calls on an answer nothing reads. Nothing is lost by the gate: `fetch` reports every unresolved Copilot thread on the PR, whatever review opened it, so threads left over from an earlier review are still counted the moment a current-head review appears.
- **Project the fields shown, never the raw result.** `fetch-reviews` returns every Copilot review on the PR with its complete `reviewBody`, and a watch takes this snapshot on every tick.
- **Select the review by `id`, not by head SHA.** Under `--confirm-clean` two reviews share one head, and only the newest one's body is the current verdict. `--argjson` is required because REST reports `id` as a number.
- **An all-null result is not a failure, and it is not a match either.** `fetch-reviews` skips a review whose body is empty, so a review the metadata probe found can be absent from its output. jq builds the object anyway, and the filter then answers `{"id":null,"url":null,"hasFormatDrift":null,"findings":0}`: `.findings | length` over an absent review is `0`, not an error. Read a null `id` as "this review carried no body", which means no review-body findings and no format drift, and keep the thread count from `fetch`. A null `hasFormatDrift` is the absence of an answer, never `false` on its own merits, so never report it as a review that parsed cleanly.
- **`fetch-reviews` reads the reviews endpoint the metadata probe already read.** That repetition is deliberate: each command stays standalone and copy-pasteable, and the second read only happens on ticks where a current-head review exists.

The probe answers exactly three questions, and step 4 asks no more of it than these: are there open Copilot threads, does the current-head review body carry findings, and does `hasFormatDrift` report that its layout could not be parsed. Whether a finding is real, already handled, or needs no code change is `resolve-copilot-pr-feedback`'s judgment, not this skill's.

Reduce the snapshot to the four axes in [Ready Criteria](#ready-criteria).

### 4. Classify and Dispatch

Evaluate in this order and take the first match. Every condition below is work the skill can do now. Waiting is not, so it sits at the end as the fallthrough rather than in the middle of the list: a pending check is nothing the skill can act on, and it must never displace a condition that is.

Two orderings are deliberate:

- **Sync the branch before diagnosing check failures**, because a stale branch is a common cause of them.
- **Act on Copilot findings without waiting for in-flight checks**, because that work is durable: the fixes land whatever the checks go on to do. Requesting a review is perishable by comparison, so both request paths keep a passing-checks precondition. Every push invalidates a review rendered against the old head, which makes a review requested mid-check one that a check fix would throw away, and it spends a round against the step 7c budget either way.

1. **PR is `MERGED` or `CLOSED`**: terminal. Report and stop.
1. **`mergeStateStatus` is `DIRTY`**: conflicts with the base branch. Go to step 5.
1. **`mergeStateStatus` is `BEHIND`**: go to step 5.
1. **`mergeStateStatus` is `BLOCKED`**: do not treat this as a blocker and do not wait on it, but record it. It means a branch protection rule is unsatisfied, most often a required approving review. Continue evaluating the remaining conditions, and carry the `BLOCKED` state into every status line and into the terminal report per step 8.
1. **Any check concluded with a failure**: go to step 6.
1. **Copilot reviewed the current head, the step 3 feedback probe reported open threads, review-body findings, or format drift, and step 7b has not already been invoked for that review `id`**: go to step 7b. Checks still running do not hold this back. Drift is routed here rather than left to the wait below, because it is not clean and no later tick changes an immutable review body; the resolver reads the raw body and reports the drift as a failure. The `id` clause is step 7b's own once-per-review guard, lifted into the condition that reads it: a review body is immutable, so a finding the resolver has already recorded as handled still appears in the probe on every later tick, and without the guard here it would re-dispatch forever.
1. **Copilot reviewed the current head, step 7b already processed that review, and either its outcome was not `Completed` or `No unresolved Copilot feedback`, or the probe still reports open threads or format drift against it**: escalate per step 9. Both shapes are terminal for that review. A non-clearing outcome never satisfies the axis, and a clearing outcome that leaves threads or drift behind is the case step 7b calls out as unable to change on its own. The `id` guard in the condition above will not send the review to step 7b a second time, and no later tick alters an immutable review, so without this condition the tick falls through to the wait below and the watch never ends. **State the two disqualifying signals rather than a summary of them.** A phrasing such as "this tick has no new input" is true of a cleanly resolved review as well, and this condition sits above the terminal one, so that reading escalates every finished PR instead of merging it. Neither a clean processed review nor a review whose only remaining signal is a review-body finding belongs here: the first satisfies the Copilot axis, and the second is cleared by step 7b's record rather than by a later probe, per the Ready Criteria rules.
1. **Checks pass and Copilot is missing or stale**: go to step 7a.
1. **Checks pass, Copilot reviewed the current head cleanly, `--confirm-clean` is set, and this is the first such review**: go to step 7d to request and await the confirming review.
1. **All four axes clean**: terminal. Go to step 8.
1. **Nothing above matched**: wait, then return to step 3. Checks pending or running with nothing else to act on is the usual case.

Under `--no-fix`, replace steps 5, 6, and 7 with a report of what would have been done, then continue waiting. The step 3 feedback probe still runs: it writes nothing, and without it the report would not be able to say what Copilot actually found.

On a Dependabot PR, steps 5 to 8 follow [Dependabot PRs](#dependabot-prs). Of the four Copilot conditions above, only the first applies, and it leads to an escalation rather than step 7b; the other three never match, the second of them because step 7b is never invoked there to record an outcome. The step 3 probe is what makes that first condition observable there, and it is read-only, so the Dependabot path judges the review without invoking anything that pushes.

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
resolve-copilot-pr-feedback OWNER=<owner> REPO=<repo> PR_NUMBER=<number>

Parent continuation:
- Caller: monitor-pr
- Resume target: Step 3, take a fresh state snapshot.
- On Completed or No unresolved Copilot feedback: Return the final summary comment URL and any originating review URLs, then continue immediately to Step 3 without asking the user for confirmation.
- On Partial or Failed: Stop the watch and escalate per Step 9.
```

Pass the `OWNER`, `REPO`, and `PR_NUMBER` recorded in step 1. That skill's script calls require all three and it does not document how to derive them, so supplying them here saves it from re-deriving them or asking the user.

Only invoke it once a review exists at the current head. Invoking it earlier makes it report `No unresolved Copilot feedback` and post a no-op summary comment, which reads as a clean bill of health for code Copilot never saw.

**Invoke it at most once per review.** Record the review `id` each invocation is made against, taken from the step 3 probe, together with the status it reported. **Do not key this on the head SHA.** Step 7d deliberately requests a second review against the same head, so a SHA key conflates two distinct reviews: it would either suppress the confirming review's findings as already processed or escalate it as a repeat when it is genuinely new. The `id` is the only field that separates them. That record is also what the Copilot axis reads: a review-body finding is cleared by having processed its review, not by a later probe.

**Escalate when a source that should have cleared did not.** After a `Completed` or `No unresolved Copilot feedback` report for a review `id`, escalate per step 9 when the next snapshot's probe still reports open threads, or still reports format drift against that same review. Nothing further will change on its own in either case: a second invocation has no new input to work from, and the step 7c budget will not stop the cycle because it counts completed reviews rather than invocations. A new review or a push is what makes another invocation meaningful.

**Review-body findings are the exception, and getting this backwards is the trap.** An open thread clears when it is resolved, so a repeat there means something genuinely failed. A review-body finding has no thread to resolve and review bodies are immutable, so it stays visible in that review permanently, and the step 3 probe will keep reporting it on every tick for the life of the PR. `resolve-copilot-pr-feedback` records it as handled in a linked summary row and reads that record back on its next run; that record, plus this step's own processed-review record, is the disposition. Escalating on a finding count that cannot fall would turn every noted or previously handled review-body finding into a false escalation on a PR that is finished. Retain the final summary comment URL and the originating review URL for terminal or escalation reporting.

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

1. Wait for a review newer than the recorded one, then run the step 3 feedback probe against its `id` and judge it by the same standard: no open threads, no format drift, and no review-body findings.
1. **Two consecutive clean reviews against the same head SHA** satisfy the Copilot axis. Report both, with their timestamps, so the terminal report shows the confirmation actually happened.
1. **If the probe reports anything against the confirming review**, step 4 sends it to step 7b under its own `id`, and the resolver's status decides what it was. `No unresolved Copilot feedback` means every finding in that body was already recorded against an earlier review, so nothing new surfaced and the pair still completes. `Completed` means the confirmation earned its keep: handle it per step 7b, and reset the count, so the next clean review is again only the first of two.

Any push resets the confirmation, whatever its source. Both clean reviews must be against the current head, so a fix, a merge from step 5, or a commit someone else pushes all send the count back to zero.

Each review in a confirmation pair counts as its own round against the step 7c budget.

### 8. Terminal Report, Then Ask

1. Stop the wait loop. On the `ScheduleWakeup` path, that means `ScheduleWakeup({stop: true})`; on the scheduled-task path, stop the task that resumes this conversation.
1. Print the full status table: every check with its state, the Copilot verdict with the SHA it was rendered against, `mergeable`, `mergeStateStatus`, and `reviewDecision` labelled as informational.
1. If review-body findings were processed or previously handled during this watch, include the resolver's final summary comment URL and each originating Copilot review URL. State whether each finding was actionable, previously handled, or required no code change; do not make the user search unrelated PR comments for the disposition.
1. **If `mergeStateStatus` is `BLOCKED`, say so before offering to merge.** State that GitHub will refuse the merge until the branch protection requirement is met, and name it if `reviewDecision` identifies it (a required approving review being the usual case). Offering a merge without that caveat presents a PR as ready when it is not yet mergeable.
1. Ask the user how to proceed: merge now (squash, merge, or rebase), enable auto-merge with `gh pr merge --auto`, or leave it as is.

Do not merge without asking, and do not enable auto-merge without asking.

### 9. Escalate

When an escalation rule fires, stop the wait loop, including any scheduled task that resumes this conversation, and report:

1. What is blocking, in one sentence.
1. What was already tried, including any commits pushed during this watch.
1. The specific question the user needs to answer.

Then tell the user that `/monitor-pr` resumes the watch once they have decided.

## Reporting Format

Every tick prints one compact line. On the `ScheduleWakeup` path, pass `noop: true` on a tick where nothing changed, so quiet ticks collapse in the user's terminal. On a scheduled task, report only a material state change; otherwise use the task's quiet-result mechanism if it has one.

```text
▸ 361 · checks 4/5 · copilot stale · mergeable CLEAN · review NONE · round 3/10
```

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
- **`resolve-copilot-pr-feedback` reports `Completed` or `No unresolved Copilot feedback` but the next probe still reports open threads or format drift against that review**: Escalate per step 9. Those are the two signals that should have cleared and did not, so nothing further changes on its own. **A review-body finding is not one of them.** It stays in the immutable body for the life of the PR, and step 7b's processed-review record is what clears it, so escalating there would stop a PR that is finished. Include the resolver summary and originating review links so the reported disposition is visible beside the immutable finding. Do not invoke the skill again against the same review; step 4's once-per-review `id` guard already prevents it.
- **Copilot never reviews despite an explicit request**: Escalate. Copilot review may be disabled for the repository, in which case the user must decide whether to proceed without it.
- **Push rejected because the remote moved**: Someone else pushed to the branch. Re-poll, sync per step 5, and retry once. If it is rejected again, escalate.
- **Dependabot does not act on a rebase request**: After two quiet ticks with the head SHA unchanged and no reply from Dependabot on the PR, escalate. Do not post the request again for the same head.
