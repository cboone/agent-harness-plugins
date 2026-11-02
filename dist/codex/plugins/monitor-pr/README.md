# Monitor Pr

Monitor a pull request until its checks pass, Copilot signs off on the current head, and it is mergeable, fixing failures along the way, then offer the merge and sync the main worktree once it lands; resolve Copilot feedback on demand.

**Type:** Skills

See the [installation instructions](../../../../README.md#install).

## monitor-pr:monitor

Monitor a pull request until its checks pass, Copilot signs off on the current head, and it is mergeable, fixing failures along the way, then offer the merge and sync the main worktree once it lands.

**Type:** Skill
**Trigger:** `/monitor-pr:monitor [<pr-number>]`
**Requires:** [`gh`](https://cli.github.com/) (authenticated), [`jq`](https://jqlang.org/)

### Installation

See the [marketplace install instructions](../../../../README.md#install).

### What It Does

Picks up where `pr` stops. The `pr` skill creates the pull request, prints the URL, and terminates; everything after that has traditionally been hand-driven. This skill takes over and tends the PR until it is ready to merge, and then through the merge.

On each tick it takes one snapshot of the PR and reduces it to four axes: checks, Copilot, mergeability, and PR state. It then acts on the first problem it finds, in priority order. On a PR Dependabot authored, the skill never pushes, so each of these follows [Dependabot PRs](#dependabot-prs) instead:

1. **Branch is conflicted or behind the base**: invokes `sync-with-main:merge`, since a stale branch is a common cause of check failures.
1. **A check failed**: pulls the failing job's logs and repairs it. Lint and format failures go to `lint-and-fix`; generated-tree drift is rebuilt with the repository's own build scripts; test and build failures are diagnosed from the logs.
1. **Copilot reviewed the current head**: invokes `monitor-pr:resolve-copilot-feedback` once for that review. The first time a current-head review appears, the watch reads its complete body and classifies it as a review, one of Copilot's error or excluded-files notices, or unclear. It reads the whole body rather than a prefix, because the text saying Copilot did not review can sit anywhere in it. A notice is never a clean review: the watch requests one retry for it and escalates if Copilot answers with another notice. An unclear body escalates. A review goes to the resolver, which reads every concern the body states, whatever its layout, so a new Copilot layout cannot stop the watch. If the resolver finds the review was actually a notice, the watch takes the notice path. Every tick also runs a read-only probe, using the same bundled script the resolver reads with, for open Copilot threads and for Copilot feedback anywhere neither threads nor review bodies reach, such as a comment on the PR itself. This one does not wait for in-flight checks. The fixes land whatever the checks go on to do, so there is no reason to serialize the Copilot cycle behind a check run the skill cannot influence.
1. **Copilot has not reviewed the current head**: waits, once the checks are passing. Copilot re-reviews automatically on push in most repository configurations. If no review arrives after two quiet ticks, it requests one with `gh pr edit --add-reviewer "@copilot"`. Asking for a review is the one Copilot action that waits on checks, because any push throws the result away.

Every push it makes invalidates Copilot's previous review, so the loop naturally goes back around after a fix. It stops repairing when all four axes are clean at once, prints a full status table, and moves on to [the merge](#the-merge). When Copilot asked for human review of a change without naming a defect, the report says "Ready, with N advisory requests for human review" and quotes each one, since those requests never block the watch.

#### It stops and asks

This is not a continue-at-all-costs skill. It halts the watch and puts the question to you when the fix is a judgment call about intended behavior, when the same check fails again after a fix attempt for it, when the fix would reach outside what the branch already changes, when the logs do not identify a cause, when `sync-with-main:merge` or `monitor-pr:resolve-copilot-feedback` reports something it could not finish, when the resolver reports a [sibling chain](#monitor-prresolve-copilot-feedback) (it quotes the chain and its design option and asks whether to adopt it or patch the instance), when GitHub refuses the merge for a reason other than a new push or no merge method is left, when a change is requested while an approval is awaited, when the merge watch can no longer read the PR, or when Copilot feedback comes back reportedly resolved while the same review still reads as unresolved. That last one covers both forms Copilot's feedback takes. An inline thread clears when it is resolved, but a finding filed in a review body has no thread and the body is immutable, so it stays visible in that review permanently. The resolver records it as handled in a summary row that links back to the exact review and includes the fixing commit or no-change rationale; monitor reports that summary link instead of implying that the original review body changed.

#### What counts as a Copilot sign-off

Copilot reviews are always `COMMENTED`, never `APPROVED`, so an approval state is never the pass signal. A sign-off means a Copilot review exists whose commit SHA equals the current head, the watch read it as a review rather than a notice, the resolver processed it to `Completed` or `No unresolved Copilot feedback` and listed it as read, and the review-thread fetch returns nothing. A review against an older SHA does not count.

The probe commands run in the snapshot step, before anything is dispatched, from a copy of `resolve-copilot-threads` this plugin ships, so the watch and the resolver always read the same review data. The full read that classifies a review happens once per review, not on every tick. One consequence is worth knowing: review bodies are immutable, so a finding the resolver has already handled keeps appearing in that review for the life of the PR. What clears it is the record of having processed that review, not a later fetch, and the watch does not wait for a body that cannot change.

Copilot's output varies between runs over identical code, so a review that surfaces nothing is not proof that there was nothing to surface. `--confirm-clean` requires two consecutive clean reviews instead of one: the first clean review does not end the watch, a second is requested explicitly (a re-review of unchanged code has to be asked for, since nothing triggers it), and only two in a row against the same head satisfy the Copilot axis. Any push resets the pair, and if the confirming review turns something up, the count starts over after it is fixed.

#### How long it runs

The Copilot round budget defaults to 10. On reaching it the skill stops and asks whether to continue and for how many more rounds; `--rounds <n>` sets a different budget and `--rounds unlimited` removes the question entirely, committing to run until the PR is genuinely clean.

The budget bounds an unattended watch. It is not a judgment about whether the work is going well, and the skill does not read the finding counts as a trend. Copilot swings between busy and quiet rounds over the same code, so a rising count does not mean divergence, and four rounds is often not enough to finish. A watch still turning up real defects at round 8 is working, not thrashing. What ends a watch early is a finding that needs your judgment, not an unflattering shape in the numbers.

Late rounds triage instead of blocking. From the Copilot round after `--triage-after`, 5 by default, only High findings drive fixes. Medium and Low findings are deferred: the resolver resolves their threads with a deferral reply and lists them, and at readiness, at an escalation, or after the merge if someone else merges first, the watch proposes them as one batch of follow-up issues through [Create Deferred Issues](../create-deferred-issues/README.md), so you approve the whole batch once. Rounds are counted across the PR, including reviews from before the watch began. `--triage-after never` keeps every finding blocking.

#### The merge

At readiness the skill offers one merge, not a menu. It reads the merge methods the repository settings allow and narrows them by the base branch's rulesets, since a ruleset can allow only squash, or require a linear history, on a repository whose settings also allow merge commits. Where a merge queue applies, the offer names the queue. If one method is left, it offers that one. Otherwise it uses an allowed method the repository's agent config or the harness's memory names, and failing both it proposes a merge commit, or the first allowed method when merge commits are not allowed, asks once, and saves the answer as a per-repository memory note where the harness has durable memory. A read it cannot make, such as merge settings hidden from an account without admin access, is reported as unknown rather than taken as permission.

Before offering, it starts a background watch on the PR, so the offer and the watch never wait on each other: whoever merges the PR, from wherever, the session finds out. The question is asked in plain text rather than through a blocking prompt so that the watch can wake the session while the question is open. The merge is pinned to the head that was declared ready, and a push after readiness sends the PR back through the repair loop rather than letting an unchecked head merge. Merging leaves the head branch in place, since a worktree usually has it checked out, and a merge GitHub queues or turns into auto-merge keeps the watch running until it lands. On a foreground path, where no watch can run beside an open question, it makes the offer and ends with a checkpoint; the next `/monitor-pr:monitor` picks up a merge made in the meantime.

Some repositories need an approving review first. The skill treats a PR that way when a base-branch ruleset requires approvals, when `reviewDecision` is `REVIEW_REQUIRED`, or when your own or the project's agent instructions say the repository's PRs need approval before merge. That last source covers repositories GitHub does not protect, and it keeps any organization-specific policy in your configuration rather than in the skill. The watch then reports "Ready, awaiting approval", offers the merge once approval arrives and a fresh snapshot is still clean, and escalates on a change request.

Once the PR merges, the skill fetches the base branch from the remote that names the PR's repository, which in a fork is not `origin`, and fast-forwards the worktree that has it checked out, usually the main worktree, or the branch ref when none does. It confirms the merge commit arrived before calling the branch synced, and it reports git's refusal rather than stashing, resetting, or forcing when local changes or a diverged branch are in the way. It then messages the other agent sessions working in the repository's worktrees with the PR, the merge commit, and the sync result. On Claude Code it finds those sessions by matching each `ListAgents` session's tmux pane against the panes inside the repository's worktrees, and sends with `SendMessage`. The message is informational; each session decides whether to merge the base branch. A PR closed without merging gets neither step.

#### Dependabot PRs

Dependabot owns its branches. Once anyone else pushes to one, Dependabot stops rebasing it, and a later `@dependabot recreate` throws the push away. So on a PR authored by Dependabot the skill never pushes:

- A conflicted or out-of-date branch gets a `@dependabot rebase` comment, once per head, instead of `sync-with-main:merge`.
- A failing check is diagnosed but not repaired, and the watch stops there. A failure caused by a secret that Dependabot runs cannot read is reported as an environment problem, pointing at [Review Dependabot Config](../dependabot/README.md#dependabotreview-config). Anything else points at [Triage Dependabot PRs](../dependabot/README.md#dependabottriage-prs).
- The Copilot axis counts as clean unless a Copilot review of the current head states a concern, leaves an open thread, or reads as unclear, or the audit reports Copilot feedback outside threads and review bodies, any of which escalates. With no resolver to run, the watch reads the review body in full itself; the probe and that read are reads, so the Dependabot path sees what Copilot found without running a skill that would push. The skill never requests or waits for a review, since every rebase leaves any earlier review behind.

#### What does not gate

`reviewDecision` is reported in every status line but never blocks readiness. A human `CHANGES_REQUESTED` will not stop this skill from declaring the PR ready, so that an outstanding human objection stays visible without stalling a watch on solo repositories that have no required reviewers. When the repository or your instructions require an approval, it does hold back the merge offer; see [the merge](#the-merge).

#### Pacing and harness support

Intervals adapt to the phase: shorter while checks are actively running, longer while waiting on Copilot, longest when nothing is moving. Copilot rounds bound the repair loop; each background change watch also has a 24-hour lifetime. The repair loop ends at readiness, an escalation, an exhausted round budget, or a background-watch expiry; after readiness, the merge watch ends at the merge, a close, an escalation, or after 24 hours with the PR still open. You can interrupt either at any point.

On Claude Code, run `/monitor-pr:monitor` once. A background `merge-flow watch-changes` command polls internally and resumes the conversation when checks complete or fail, a Copilot review arrives at the head, the head changes, the PR merges or closes, or known mergeability changes. Unchanged polls stay silent. The task ID and baseline are retained in watch state. Existing quiet-tick decisions use a bounded poll count; failed reads and the 24-hour lifetime are bounded by the same loop as the merge watch. When background completion is unavailable, `ScheduleWakeup`, conversation-resume tasks and bounded foreground polling remain fallbacks.

On Codex surfaces that offer scheduled tasks, the skill schedules the next tick in the current conversation, cancels that task once the watch reaches a terminal state or needs a decision, and at readiness replaces it with a task that watches for the merge. This is the preferred Codex path because every scheduled run is an actual continuation, not a request for the agent to remember to continue after replying.

Codex CLI does not expose that scheduler. It runs a foreground poll loop instead: after each wait, the same active turn takes a new snapshot and dispatches it. This loop also applies when task creation fails on a scheduled surface. The default `--ticks 3` ends each foreground invocation with a resumable checkpoint, never a readiness claim. Run the reported command in the same conversation to restore options, counters, and action guards; to resume elsewhere, paste the complete checkpoint before the command and verify the repository and branch. Only the per-invocation tick count resets. See [Checkpoint and Resume](skills/monitor/references/checkpoint.md). Use `--ticks unlimited` only when keeping the foreground session active is appropriate.

On fallback paths, quiet ticks print a single line and are collapsed by the harness where it supports that. Only a real state change prints the full table.

### Usage

```text
/monitor-pr:monitor
/monitor-pr:monitor 361
/monitor-pr:monitor --interval 10m
/monitor-pr:monitor --ticks 5
/monitor-pr:monitor --rounds unlimited
/monitor-pr:monitor --triage-after 3
/monitor-pr:monitor --confirm-clean
/monitor-pr:monitor --no-fix
```

| Option                      | Description                                                                                        |
| --------------------------- | -------------------------------------------------------------------------------------------------- |
| `<pr-number>`               | Monitor a specific PR instead of the current branch's PR                                           |
| `--interval <d>`            | Override adaptive pacing with a fixed wait                                                         |
| `--ticks <n\|unlimited>`    | Bound all foreground paths, including scheduler fallbacks; the default is 3                        |
| `--rounds <n\|unlimited>`   | Change the Copilot round budget from its default of 10; `unlimited` commits to running until clean |
| `--triage-after <n\|never>` | Defer Medium and Low Copilot findings to follow-up issues from round `n + 1`; the default is 5     |
| `--confirm-clean`           | Require two consecutive clean Copilot reviews rather than one                                      |
| `--no-fix`                  | Observe and report only: never push, invoke a fixing skill, request a review, or merge             |

### Recommended Permissions

This skill runs git and GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh pr view *)", "Bash(gh pr checks *)", "Bash(gh pr edit *)", "Bash(gh pr comment *)", "Bash(gh pr merge *)", "Bash(gh api --paginate --slurp repos/*/pulls/*/reviews*)", "Bash(gh run view *)", "Bash(gh run list *)", "Bash(bash \"*/resolve-copilot-threads\" *)", "Bash(bash \"*/merge-flow\" *)", "Bash(gh pr ready *)", "Bash(jq *)", "Bash(sleep *)", "Bash(git status*)", "Bash(git add *)", "Bash(git commit *)", "Bash(git push*)", "Bash(make build)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

Four notes on these rules. **The script rules are deliberately path-agnostic**: the installed plugin directory carries a version in its path, so matching on the trailing script name keeps the rules working across upgrades, and the `resolve-copilot-threads` entry covers this plugin's copy and `monitor-pr:resolve-copilot-feedback`'s alike. The `merge-flow` entry covers every GitHub read, git fetch, fast-forward, and tmux listing the script makes; the skill's own `gh pr view` and `gh pr merge` calls fall under their rules. **Flag position matters**: `Bash(gh api repos/*)` does not match `gh api --paginate --slurp repos/*`, because the flags come first, so the rule has to spell them out in order. **The repair paths need write rules**: step 6 stages, commits, and pushes fixes, and rebuilds generated trees, so `git add`, `git commit`, and the build command belong in the list alongside `git push`. The `make build` entry is specific to this repository; substitute whatever build or codegen commands your own project's checks enforce. **`sleep` is only needed on a foreground path**: it pauses an active Codex CLI tick. It cannot revive a watch after the agent has returned a response.

### Examples

- "monitor the pr": resolves the current branch's PR, watches it until it is ready to merge, and then through the merge
- "monitor pr 361": same behavior, against an explicit PR number
- "watch the pr": same behavior
- "keep an eye on the pr": same behavior
- "wait for ci": same behavior, though the watch still covers Copilot and mergeability rather than checks alone

### See Also

- [PR](../pr/README.md): create the pull request this skill then monitors
- [Resolve Copilot PR Feedback](#monitor-prresolve-copilot-feedback): the Copilot half of the loop, invoked once a review lands on the current head
- [Merge Main](../sync-with-main/README.md#sync-with-mainmerge): invoked when the branch falls behind or conflicts with its base
- [Lint and Fix](../lint-and-fix/README.md): invoked to repair lint and format failures
- [Create Deferred Issues](../create-deferred-issues/README.md): files the follow-up issues for findings deferred in late rounds
- [Triage Dependabot PRs](../dependabot/README.md#dependabottriage-prs): decide what to do with a Dependabot PR before watching it
- [All plugins](../../../../README.md)

## monitor-pr:resolve-copilot-feedback

Process and resolve GitHub Copilot automated PR review comments.

**Type:** Skill
**Trigger:** `/monitor-pr:resolve-copilot-feedback`

Every thread resolution records a GitHub reason: fixed concerns (including earlier fixes) and outdated concerns are **Addressed** (`ADDRESSED`); valid concerns deferred, out of scope or deliberately declined, and unchanged nitpicks, are **Won't fix** (`WONT_FIX`); factually wrong concerns are **Incorrect** (`INVALID`), with an explanatory reply. Pending decisions remain open. Recovery after an existing reply uses the same mapping. The summary records each touched thread's reason, or intended reason if resolution failed. Review-body findings have no thread to resolve.

The bundled helper accepts `resolve THREAD_ID --reason REASON` and `reply-and-resolve THREAD_ID --reason REASON --body-file TMPFILE`. GitHub's GraphQL `resolveReviewThread` mutation accepts `resolutionReason: PullRequestReviewThreadResolutionReason` in its input. Callers outside the skill can omit `--reason` to retain reason-free resolution.
**Requires:** [`gh`](https://cli.github.com/) (authenticated), and the [Review Anti-Patterns](../review-anti-patterns/README.md) and [Lint and Fix](../lint-and-fix/README.md) skills

### Installation

See the [marketplace install instructions](../../../../README.md#install).

### What It Does

Fetches unresolved Copilot review threads via GraphQL, categorizes them (nitpick, outdated, incorrect, valid, deferred, advisory, or no concern for review text that states nothing to act on), resolves threads, and updates Copilot instruction files under `.github/` when Copilot feedback is incorrect. Also fetches Copilot's **review bodies**, where Copilot states findings without opening a thread: in its lead paragraph, in lists of open or previously missed findings, in file-summary tables, and wherever it puts them next. Those findings have no thread to reply to or resolve, so a thread-only query cannot see them.

The skill reads each review body as text rather than parsing its layout. Copilot reshapes that layout often, and the text always says what it found, so the bundled script returns each body raw and complete, with the review comment ids it links to, and the skill lists every concern the review states. Each concern is settled as a restatement of a thread or an earlier disposition, a new finding, an advisory request for human review, which the summary quotes at the top, or nothing of concern. A new layout therefore costs nothing: there is no parser to fall behind. Copilot's error and excluded-files notices are recognized by reading them, never read as clean reviews, and named in the summary so `monitor-pr:monitor` can request a fresh review.

An audit counts every Copilot review, review comment and pull request comment, and lists any feedback the fetches cannot reach. It never reports "no unresolved Copilot feedback" without having run all three checks. Because Copilot re-emits the same body finding in every later review, the skill reads back its own prior summary comments. Each records the ids of the reviews it read, so a later run reads every review no completed run settled, plus the newest review of the current head, whenever those reviews arrived. It carries forward anything an earlier run left pending or failed, and verifies each finding against the current code before acting, so already-handled findings are noted rather than re-fixed. Each disposition links its exact source review in the single final summary comment; fixed dispositions name their commit, while no-change dispositions state their evidence or rationale.

Valid findings are fixed as a class: the skill names the general problem behind the finding, finds every instance across the branch, its parallel paths, mirror copies and callers, and fixes them together. A sibling of a finding already fixed on the pull request is not patched again. The skill leaves its thread open when it has one, names the chain in its summary with a design option that would close the class, such as an allowlist, a structural parser or an explicit threat model, and ends `Partial` so you choose. In late rounds, a caller such as `monitor-pr:monitor` can pass `DEFER_SEVERITIES=Medium,Low`. Findings at those severities are not fixed: their threads are resolved with a deferral reply, and the summary lists them under `### Deferred to follow-up` for the caller to file as one batch.

Before pushing, the fixes are reviewed with the [Review Anti-Patterns](../review-anti-patterns/README.md) skill, in a read-only subagent where the session has one, and its Important findings are fixed or declined with a recorded rationale. A consistency sweep then corrects every document, comment, help text and pull request body that the fixes made wrong, and lint runs. A closing review covers everything committed after the first review, and nothing is pushed while a workflow failure or an Important finding stands. Thread timing and recovery follow [the resolver's step 4](skills/resolve-copilot-feedback/SKILL.md#4-handle-each-category). The pull request body is updated only after the push.

After reaching a terminal workflow state, posts a required final summary comment to the PR for every outcome, including no unresolved feedback, non-code-change resolutions, code-change resolutions, partial processing, and failures when PR context and GitHub authentication are available. If the summary cannot be posted, the workflow reports that incomplete state and preserves the intended summary for retry instead of claiming success. No-op runs reuse an existing same-head no-op summary instead of adding duplicate comments. Helps you quickly triage automated suggestions after opening a PR.

### Usage

```text
/monitor-pr:resolve-copilot-feedback
```

### Recommended Permissions

This skill runs custom scripts and git commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(bash \"*/resolve-copilot-threads\" *)", "Bash(git push*)", "Bash(gh api --paginate repos/*/issues/*/comments*)", "Bash(mktemp -u \"${TMPDIR:-/tmp}/copilot-reply-*\")", "Bash(rm -f *copilot-reply-*)", "Bash(gh pr comment *)", "Bash(gh pr view *)", "Bash(gh pr edit *)", "Bash(mktemp -u \"${TMPDIR:-/tmp}/copilot-body-*\")", "Bash(rm -f *copilot-body-*)", "Bash(git rev-parse HEAD)", "Bash(git status --porcelain)", "Bash(git diff *)", "Bash(mktemp -u \"${TMPDIR:-/tmp}/copilot-summary-*\")", "Bash(rm -f *copilot-summary-*)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

### Examples

- "resolve copilot feedback": fetches and processes Copilot review comments
- "check copilot review": same behavior
- "handle copilot comments": same behavior

### See Also

- [Address Review](../address-review/README.md): work through a human-written review document
- [PR](../pr/README.md): create the PR that Copilot will review
- [All plugins](../../../../README.md)

Resolver summaries lead with a verdict and linked findings grouped by outcome, with bookkeeping and the full findings table in collapsed details. Every completed thread gets a reply leading with its decision, linking fixing commits, conventions or tracked follow-ups where applicable.

## Codex invocation

At every entry, `merge-flow prepare` resolves active restrictions once into watch state before an axis is read. Triage, probes, classification, actions and resumed events consult that same policy; `merge-flow dispatch` selects from its permitted candidates. A paused triage count is recorded as paused without reading bodies or inventing a count. Blocked actions appear as would-do lines. With no permitted action or running permitted check, the watch cancels its scheduler and returns a policy-limited `Status: unavailable` report. Bundled script calls carry `--watch-state` so their reads and mutations consult the same policy before authentication or API work.

Invoke `$monitor-pr:monitor` or `$monitor-pr:resolve-copilot-feedback` in the conversation, or select the skill from `/skills`. Natural-language requests use the same workflow. Parent calls load the advertised skill location and pass their continuation block; they do not execute a dollar mention as a tool. Host restrictions still govern every step.
