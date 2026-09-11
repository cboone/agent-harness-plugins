---
name: monitor-pr
description: >-
  Monitor a pull request until its checks pass, Copilot has reviewed the
  current head with nothing left open, and it is mergeable, fixing failures
  and resolving Copilot feedback along the way. Use when the user says
  "monitor pr", "monitor the pr", "watch the pr", "keep an eye on the pr",
  "wait for ci", "wait for checks", "monitor pr 361", or any variant
  involving watching a pull request until it is ready to merge. Requires the
  gh CLI to be installed and authenticated, and jq.
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
- **--rounds `<n|unlimited>`**: Change the Copilot round budget from its default of 10. `--rounds unlimited` commits to running until the PR is genuinely clean, however many rounds that takes, and never pauses to ask for more
- **--confirm-clean**: Require two consecutive clean Copilot reviews rather than one. After the first clean review, request another explicitly and wait for it
- **--no-fix**: Observe and report only. Never push, never invoke a fixing skill, never request a review

## Ready Criteria

The watch ends when all four axes are clean at the same time. Partial greenness is not readiness.

| Axis         | Clean when                                                                                                                                                                                                    |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Checks       | Every check in `statusCheckRollup` has concluded successfully, or the repository has no checks configured                                                                                                     |
| Copilot      | A Copilot review exists whose commit SHA equals the current head, `fetch` returns `[]`, and `fetch-reviews` has no open finding. Under `--confirm-clean`, two consecutive such reviews against that same head |
| Mergeability | `mergeable` is `MERGEABLE` and `mergeStateStatus` is neither `DIRTY` nor `BEHIND`. `BLOCKED` counts as clean but must be reported, per the rule below                                                         |
| PR state     | `OPEN` and not merged or closed                                                                                                                                                                               |

Three rules that follow from this and are easy to get wrong:

- **A Copilot review against an older SHA does not count.** Copilot reviews are pinned to the commit they ran against, so every push this skill makes invalidates the previous review by construction. A fix always sends the loop back around.
- **`reviewDecision` does not gate.** A human `CHANGES_REQUESTED` will not stop this skill from declaring the PR ready. Report `reviewDecision` in every status line and in the terminal report so an outstanding human objection stays visible, but never wait on it.
- **`BLOCKED` does not gate either, but it must be reported.** Requiring `mergeStateStatus` to be `CLEAN` would be the stricter reading of "ready to merge", and it is deliberately not what this skill does: on a repository whose branch protection requires an approving review, nothing the skill can do will ever satisfy it, so the watch would run until its round budget expired and then report failure on a PR that is finished. Treat `BLOCKED` as ready-with-a-caveat instead. **A terminal report that omits an active `BLOCKED` state is wrong**, because it tells the user the PR is ready to merge when GitHub will refuse the merge. Name the state and say what is unsatisfied.

## Workflow

### 1. Resolve the PR

If the user supplied a PR number, use it. Otherwise derive the PR from the current branch. Take the opening snapshot with one call:

```bash
gh pr view <number-or-omitted> --json number,url,headRefName,headRefOid,baseRefName,isDraft,state,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup
```

Record `OWNER`, `REPO`, and `PR_NUMBER`. The `resolve-copilot-pr-feedback` skill needs all three and does not document how to derive them, so pass them explicitly when invoking it.

**If the branch has no PR**, report that and stop, pointing the user at `/pr`.

### 2. Establish the Wait Mechanism

Prefer `ScheduleWakeup`, which returns control between ticks and keeps the transcript small. If it is unavailable or rejected, fall back to a blocking `sleep` between inline polls. That fallback is also the Codex CLI and OpenCode path, since neither harness has a scheduler.

State which mechanism is in use on the first tick, so the transcript is unambiguous about how the watch is being paced.

Adaptive intervals by phase, unless `--interval` overrides them:

| Phase                                         | Wait             |
| --------------------------------------------- | ---------------- |
| Checks actively running                       | 2 to 5 minutes   |
| Awaiting a Copilot review at the current head | 5 to 10 minutes  |
| Checks queued, or nothing moving              | 20 to 30 minutes |

When more than one row applies, take the shorter wait. The step 4 fallthrough can reach a tick with checks still running and a Copilot review outstanding at once, and the shorter interval is the one that governs.

There is no wall-clock cap and no limit on ticks: waiting is free, so a watch may tick as many times as it needs to. The only budget is on Copilot rounds, per step 7c, and it counts completed reviews rather than elapsed time or poll count. The watch ends on a terminal state, an escalation, or an exhausted round budget, never on a timer. The user can interrupt at any point.

### 3. Take a State Snapshot

Re-run the `gh pr view` call from step 1, and probe Copilot's latest review:

```bash
gh api --paginate --slurp repos/OWNER/REPO/pulls/PR_NUMBER/reviews |
  jq '[.[][] | select((.user.login? // "") as $login | ["copilot-pull-request-reviewer", "copilot-pull-request-reviewer[bot]", "copilot", "github-copilot[bot]"] | any(. == $login))] | last | {commit_id, submitted_at, state}'
```

Three details in that command are load-bearing:

- **`--slurp`, and no `--jq`.** Without `--slurp`, `--paginate` emits one JSON array per page and `gh` applies `--jq` to each page separately, so a filter like `[...] | last` returns the last match _per page_ rather than the last overall. On a PR with enough reviews to paginate, that silently reads the wrong review and the skill compares the wrong SHA against the head. `--slurp` collects the pages into an array of arrays, which `.[][]` then flattens. `gh` rejects `--slurp` together with `--jq` (`the --slurp option is not supported with --jq or --template`), so the filtering has to move to a standalone `jq` after a pipe.
- **Every Copilot login, not just one.** REST reports the account as `copilot-pull-request-reviewer[bot]` while GraphQL reports it as `copilot-pull-request-reviewer`, and `copilot` and `github-copilot[bot]` also appear. Matching a single login makes a real review invisible, which reads as "Copilot has not reviewed yet" and sends the skill into a pointless wait and then an escalation. This is the same login set that `resolve-copilot-pr-feedback` matches on, tested the same way: bind the login, then `any(. == $login)` over an explicit array. `IN(...)` would also work on any jq since 1.5, but the array form is the pattern already established in this repository, and `.user.login? // ""` keeps a review with no author from breaking the comparison.
- **Flag position, and no quotes around the endpoint.** `--paginate` and `--slurp` come before the path, so a `Bash(gh api repos/*)` rule does not match `gh api --paginate repos/*`; the rule has to spell the flags out in order. Leave the endpoint unquoted as shown: the recommended allow rule matches an unquoted path, and a quoted one begins with `"` where the pattern expects `r`, so it fails to match and prompts. Nothing in the endpoint needs quoting, since owner, repo, and PR number contain no shell metacharacters. The trailing `|` ends the line without a continuation backslash, which keeps the command intact when copied.

Copilot's review `state` is always `COMMENTED`, never `APPROVED`, so never treat an approval state as the pass signal.

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
1. **Copilot reviewed the current head with open threads or findings**: go to step 7b. Checks still running do not hold this back.
1. **Checks pass and Copilot is missing or stale**: go to step 7a.
1. **Checks pass, Copilot reviewed the current head cleanly, `--confirm-clean` is set, and this is the first such review**: go to step 7d to request and await the confirming review.
1. **All four axes clean**: terminal. Go to step 8.
1. **Nothing above matched**: wait, then return to step 3. Checks pending or running with nothing else to act on is the usual case.

Under `--no-fix`, replace steps 5, 6, and 7 with a report of what would have been done, then continue waiting.

### 5. Sync the Branch

Invoke the `merge-main` skill using the Skill tool:

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

- **Lint or format failure**: invoke the `lint-and-fix` skill using the Skill tool with `--no-push`:

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

Invoke the `resolve-copilot-pr-feedback` skill using the Skill tool:

```text
resolve-copilot-pr-feedback OWNER=<owner> REPO=<repo> PR_NUMBER=<number>

Parent continuation:
- Caller: monitor-pr
- Resume target: Step 3, take a fresh state snapshot.
- On Completed or No unresolved Copilot feedback: Continue immediately to Step 3 without asking the user for confirmation.
- On Partial or Failed: Stop the watch and escalate per Step 9.
```

Pass the `OWNER`, `REPO`, and `PR_NUMBER` recorded in step 1. That skill's script calls require all three and it does not document how to derive them, so supplying them here saves it from re-deriving them or asking the user.

Only invoke it once a review exists at the current head. Invoking it earlier makes it report `No unresolved Copilot feedback` and post a no-op summary comment, which reads as a clean bill of health for code Copilot never saw.

**Invoke it at most once per review.** Record the review each invocation is made against, by id or by the head SHA it was rendered against. If it reports `Completed` or `No unresolved Copilot feedback` and the next snapshot still matches step 4's findings condition against that same review, nothing further will change on its own: a second invocation has no new input to work from, and the step 7c budget will not stop the cycle because it counts completed reviews rather than invocations. Escalate per step 9 instead. A new review or a push is what makes another invocation meaningful.

**Both feedback sources count here, and the review body is the one that traps.** An open thread at least clears when it is resolved, so a repeat there means something genuinely failed. A review-body finding has no thread to resolve and review bodies are immutable, so it stays visible in that review permanently: `resolve-copilot-pr-feedback` records it as handled in its own summary comment and reads that record back on its next run. A guard keyed on open threads alone would never fire in precisely the case that loops.

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

1. Wait for a review newer than the recorded one, then judge it by the same standard: no open threads, and no review-body findings that are not already recorded in a prior summary comment.
1. **Two consecutive clean reviews against the same head SHA** satisfy the Copilot axis. Report both, with their timestamps, so the terminal report shows the confirmation actually happened.
1. **If the second review surfaces anything real**, the confirmation earned its keep. Handle it per step 7b, and reset the count: the next clean review is again only the first of two.

Any push resets the confirmation, whatever its source. Both clean reviews must be against the current head, so a fix, a merge from step 5, or a commit someone else pushes all send the count back to zero.

Each review in a confirmation pair counts as its own round against the step 7c budget.

### 8. Terminal Report, Then Ask

1. Stop the wait loop. On the `ScheduleWakeup` path, that means `ScheduleWakeup({stop: true})`.
1. Print the full status table: every check with its state, the Copilot verdict with the SHA it was rendered against, `mergeable`, `mergeStateStatus`, and `reviewDecision` labelled as informational.
1. **If `mergeStateStatus` is `BLOCKED`, say so before offering to merge.** State that GitHub will refuse the merge until the branch protection requirement is met, and name it if `reviewDecision` identifies it (a required approving review being the usual case). Offering a merge without that caveat presents a PR as ready when it is not yet mergeable.
1. Ask the user how to proceed: merge now (squash, merge, or rebase), enable auto-merge with `gh pr merge --auto`, or leave it as is.

Do not merge without asking, and do not enable auto-merge without asking.

### 9. Escalate

When an escalation rule fires, stop the wait loop and report:

1. What is blocking, in one sentence.
1. What was already tried, including any commits pushed during this watch.
1. The specific question the user needs to answer.

Then tell the user that `/monitor-pr` resumes the watch once they have decided.

## Reporting Format

Every tick prints one compact line. On the `ScheduleWakeup` path, pass `noop: true` on a tick where nothing changed, so quiet ticks collapse in the user's terminal:

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
- **`resolve-copilot-pr-feedback` reports `Partial` or `Failed`**: Escalate with its failure details.
- **`resolve-copilot-pr-feedback` reports `Completed` or `No unresolved Copilot feedback` but step 4's findings condition still matches the same review**: Escalate per step 9. This covers an open thread and a review-body finding alike, and the body case is the one that cannot clear on its own. Do not invoke the skill again against the same review, per step 7b.
- **Copilot never reviews despite an explicit request**: Escalate. Copilot review may be disabled for the repository, in which case the user must decide whether to proceed without it.
- **Push rejected because the remote moved**: Someone else pushed to the branch. Re-poll, sync per step 5, and retry once. If it is rejected again, escalate.
