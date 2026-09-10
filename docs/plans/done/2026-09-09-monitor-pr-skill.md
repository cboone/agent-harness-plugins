# Add a `monitor-pr` skill that tends a PR until it is ready to merge

## Context

The `pr` skill stops the moment the PR exists. Its step 9 prints the URL, the title, the commits, and the connected issues, and terminates. Its one CI-touching step (step 8) is explicitly one-shot and best-effort: `gh pr checks ... || true`, with the instruction "This step is best-effort and must never block the workflow."

Nothing downstream picks it up. A grep across `plugins/` for `gh run`, `gh pr checks`, `check-runs`, `--watch`, `sleep`, `poll`, `monitor`, `statusCheckRollup`, and `backoff` finds no polling, waiting, or looping anywhere in the repository. The only CI-state reads that exist are `pr` step 8 (one-shot, title-check only) and `suggest-next-issue` (one-shot, triage context).

`resolve-copilot-pr-feedback` has a matching gap on the review side. It is single-pass: fetch, process, verify, summarize, exit. It has no notion of "Copilot has not reviewed yet", so an empty `fetch` plus a clean `fetch-reviews` is reported as "No unresolved Copilot feedback" whether Copilot reviewed and found nothing or never ran at all. On an unreviewed PR it will post a no-op summary comment that reads as a clean bill of health.

So the loop between "PR created" and "PR ready to merge" is currently hand-driven: watch the checks yourself, notice when Copilot posts, run `/resolve-copilot-pr-feedback`, notice that the fix push invalidated Copilot's review, run it again, notice the branch went behind main, run `/merge-main`.

**Intended outcome:** `/monitor-pr` starts where `/pr` stops and tends the PR until its checks pass, Copilot has reviewed the current head with nothing open, and the PR is mergeable. It fixes what it can along the way, surfaces a compact status line on each tick, and pauses for genuine decisions rather than grinding through them.

## Design decisions

These were settled with the user before planning. They are load-bearing; do not quietly revisit them during implementation.

| Decision               | Choice                                                                                                                            |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Wait mechanism         | `ScheduleWakeup` where available, blocking `sleep` fallback elsewhere                                                             |
| Pacing                 | Adaptive by phase, no wall-clock cap, no give-up tick count                                                                       |
| Check failures         | Fix what it can; surface and pause for interesting questions or important decisions. Explicitly not a continue-at-all-costs skill |
| Branch sync            | Invoke `merge-main`                                                                                                               |
| Copilot pass criterion | Review `commit_id` equals current head SHA **and** `fetch` returns `[]` **and** `fetch-reviews` surfaces no unhandled findings    |
| Copilot re-review      | Wait passively first (auto-review is on in the user's repos), trigger manually only when it does not arrive                       |
| Merge-ready criterion  | Mergeable only: no conflicts, not behind base. `reviewDecision` is reported but never gates                                       |
| Terminal action        | Stop, report, then ask                                                                                                            |
| Reporting              | One-line tick, full report on state change                                                                                        |
| Category               | `ci-and-release`                                                                                                                  |

Two consequences worth stating plainly:

- **`reviewDecision` does not gate.** A human `CHANGES_REQUESTED` will not stop the skill from declaring the PR ready. The skill must still surface `reviewDecision` in every status line and in the terminal report, so an outstanding human objection is visible even though it is not blocking.
- **The mirrored copies are second-class.** `ScheduleWakeup` is Claude Code only and the build scripts mirror every plugin with no opt-out, so Codex CLI and OpenCode get the blocking-`sleep` path. It works, but it accumulates the whole watch in one turn's context.

## Approach

### 1. New plugin `plugins/monitor-pr/` at `1.0.0`

Skill-only, no bundled script, no `.codex-plugin/plugin.json` (validator rule 14 only fires for plugins with `hooks/hooks.json`). Layout:

```text
plugins/monitor-pr/
├── .claude-plugin/
│   └── plugin.json
├── README.md
└── skills/
    └── monitor-pr/
        └── SKILL.md
```

`plugin.json`, keys alphabetical with `version` last, matching `plugins/pr/.claude-plugin/plugin.json`:

```json
{
  "author": { "name": "Christopher Boone" },
  "description": "Monitor a pull request until its checks pass, Copilot signs off on the current head, and it is mergeable, fixing failures along the way.",
  "homepage": "https://github.com/cboone/agent-harness-plugins",
  "keywords": ["ci", "copilot", "github", "pull-requests", "workflow"],
  "license": "MIT",
  "name": "monitor-pr",
  "repository": "https://github.com/cboone/agent-harness-plugins",
  "skills": "./skills",
  "version": "1.0.0"
}
```

That description is 137 characters. See the Codex budget note under Verification before changing it.

### 2. `skills/monitor-pr/SKILL.md`

Frontmatter carries only `name` and `description`, as all 51 existing skills do, with `description` as a `>-` folded block hand-wrapped near 75 columns:

```yaml
---
name: monitor-pr
description: >-
  Monitor a pull request until its checks pass, Copilot has reviewed the
  current head with nothing left open, and it is mergeable, fixing failures
  and resolving Copilot feedback along the way. Use when the user says
  "monitor pr", "monitor the pr", "watch the pr", "keep an eye on the pr",
  "wait for ci", "wait for checks", "monitor pr 361", or any variant
  involving watching a pull request until it is ready to merge. Requires the
  gh CLI to be installed and authenticated.
---
```

Body follows house style: `# Monitor PR` H1, one-line purpose restatement, `## Options`, `## Workflow` with `### N.` H3 steps and `#### Na.` H4 sub-steps, `## Error Handling` last. All-`1.` lazy ordered lists. No em dashes; spaced `--` where a dash reads best.

`## Options`:

- **--interval `<duration>`**: Override adaptive pacing with a fixed wait (e.g. `--interval 10m`)
- **--no-fix**: Observe and report only; never push, never invoke a fixing skill

#### Step 1. Resolve the PR

Accept an optional PR number argument; otherwise derive from the current branch. One snapshot call:

```bash
gh pr view <number-or-omitted> --json number,url,headRefName,headRefOid,baseRefName,isDraft,state,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup
```

If the branch has no PR, report that and stop, pointing at `/pr`. Record `OWNER`, `REPO`, `PR_NUMBER`, and the head SHA; `resolve-copilot-pr-feedback` needs the first three and never documents how to derive them.

#### Step 2. Establish the wait mechanism

Try `ScheduleWakeup` first. If it is unavailable or rejected (see the uncertainty note below), fall back to a blocking `sleep` between inline polls, which is also the Codex CLI and OpenCode path. State which mechanism is in use on the first tick so the transcript is unambiguous.

Adaptive intervals by phase, overridable with `--interval`:

| Phase                                         | Wait             |
| --------------------------------------------- | ---------------- |
| Checks actively running                       | 2 to 5 minutes   |
| Awaiting a Copilot review at the current head | 5 to 10 minutes  |
| Checks queued, or nothing moving              | 20 to 30 minutes |

No wall-clock cap. The watch ends on a terminal state or an escalation, not a timer.

#### Step 3. Take a state snapshot

Re-run the step 1 `gh pr view` call, plus the Copilot review probe:

```bash
gh api --paginate "repos/OWNER/REPO/pulls/PR_NUMBER/reviews" \
  --jq '[.[] | select(.user.login == "copilot-pull-request-reviewer[bot]") | {id, commit_id, submitted_at, state}] | last'
```

`--paginate` is required, and the flag position matters for permission rules: a `Bash(gh api repos/*)` rule does not cover `gh api --paginate repos/*`. Reduce the snapshot to four axes:

- **checks**: `pass` / `fail` / `pending` / `none`, from `statusCheckRollup`
- **copilot**: `none` / `stale` (`commit_id != headRefOid`) / `at-head`
- **mergeability**: `mergeable` plus `mergeStateStatus`
- **pr state**: `OPEN` / `MERGED` / `CLOSED`, plus `isDraft`

#### Step 4. Classify and dispatch

Evaluate in this order and take the first match. Ordering matters: sync the branch before diagnosing check failures, because a stale branch is a common cause of them.

1. **PR is `MERGED` or `CLOSED`**: terminal. Report and stop.
1. **`mergeStateStatus` is `DIRTY`**: conflicts. Go to step 5a.
1. **`mergeStateStatus` is `BEHIND`**: go to step 5a.
1. **Any check failed**: go to step 5b.
1. **Checks pending or running**: wait.
1. **Checks pass, Copilot is `none` or `stale`**: go to step 5c.
1. **Copilot is `at-head` with open threads or unhandled findings**: go to step 5c.
1. **All four axes clean**: terminal. Go to step 6.

#### Step 5a. Sync the branch

Invoke `merge-main` via the Skill tool. Note that `merge-main` has no `Parent Continuation Contract` (unlike `lint-and-fix`) and will ask the user directly on uncommitted changes and on non-trivial conflicts. That is acceptable here: it matches "pause for important decisions". Supply a continuation block anyway for symmetry with how `pr` calls `lint-and-fix`, and treat any question it raises as an escalation. After a clean merge and push, resume at step 3.

#### Step 5b. Fix failing checks

1. Identify the failing job and pull its logs: `gh pr checks` for the rollup, then `gh run view <run-id> --log-failed`.
1. Classify and dispatch:
   - **Lint or format failure**: invoke `lint-and-fix --no-push` with a `Parent continuation:` block naming `monitor-pr` as caller and step 3 as the resume target, exactly as `pr` step 5 does. Branch on its structured `Lint status: <success|no-tools|failure>` output.
   - **Generated-tree drift**: run the repository's own build scripts (here, `bin/build-codex-marketplace` and `bin/build-opencode-mirror`) and commit the result.
   - **Test or build failure**: read the logs, diagnose, fix, commit, push.
1. Push, then resume at step 3. The head SHA has moved, so Copilot's prior review is now stale by construction.

**Escalation rules.** Stop the loop, report, and ask when any of these hold. This is the "not a continue-at-all-costs skill" clause and it must be written as a hard rule, not a suggestion:

- The correct fix is a judgment call about intended behavior rather than a mechanical repair.
- The same named check fails again after a fix attempt for it. Track attempts per check name.
- The fix would touch code outside what this branch already changes.
- The logs do not identify a cause.

#### Step 5c. Drive the Copilot cycle

1. **Copilot is `none` or `stale`**: wait. Auto-review on push is enabled in the user's repos, so the review normally arrives on its own.
1. **After two consecutive Copilot-phase ticks with no review at the current head**: trigger one manually. Prefer a mechanism that does not add PR comment noise, since `resolve-copilot-pr-feedback` opens with a `## PR Comments Prohibition (CRITICAL)` section. Candidates in preference order: the GraphQL `requestReviews` mutation with Copilot's bot node ID; `gh pr edit --add-reviewer`; a `gh pr comment` with an `@copilot review` mention as last resort. **Read that prohibition section before implementing this step** and reconcile the choice with it.
1. **Copilot is `at-head`**: invoke `resolve-copilot-pr-feedback` via the Skill tool with a `Parent continuation:` block. Consume its terminal status (`Completed` / `No unresolved Copilot feedback` / `Partial` / `Failed`). On `Partial` or `Failed`, escalate. On success, resume at step 3.
1. **Convergence guard**: count Copilot rounds. After three rounds that have not converged, stop and report rather than looping indefinitely.

   **Superseded during implementation.** This shipped as a plain round budget defaulting to 10, not a convergence judgment. Watching PR #379 take seven rounds to reach a clean review, with finding counts of 6, 1, 4, 1, 3, 2, 0, showed that Copilot swings between busy and quiet rounds over the same code, so the count carries no signal about whether the work is converging. The skill now keeps going while rounds produce valid defects and escalates only on findings that need the user. `--rounds <n|unlimited>` adjusts or removes the budget, and `--confirm-clean` requires two consecutive clean reviews rather than one.

Note the built-in reset: every push the skill makes invalidates Copilot's review, so the pass criterion is genuinely three-part and a fix always sends the loop back around.

#### Step 6. Terminal report, then ask

1. Stop the wakeup loop (`ScheduleWakeup({stop: true})` on the Claude Code path).
1. Print the full status table: every check with its state, the Copilot verdict with the SHA it was rendered against, `mergeable`, `mergeStateStatus`, and `reviewDecision` (labelled as informational, not blocking).
1. Ask the user what to do: merge now (squash, merge, or rebase), enable auto-merge via `gh pr merge --auto`, or leave it.

#### Step 7. Reporting format

Every tick prints one compact line, with `noop: true` on the wakeup so Claude Code collapses quiet ticks:

```text
▸ 361 · checks 4/5 · copilot stale · mergeable CLEAN · review NONE
```

Any state change prints the full table and passes `noop: false`. Escalations print what is blocking, what was tried, and the exact question, then stop. Tell the user that `/monitor-pr` resumes the watch.

#### `## Error Handling`

Bullet list of `- **<Condition>**: <what to do>` pairs, house style:

- **No PR for the current branch**: Report that and stop, pointing at `/pr`.
- **`gh` not available or not authenticated**: Report the error and stop.
- **PR is a draft**: Monitor normally, but report the draft state in every status line and do not offer to merge in step 6 without saying so.
- **`mergeable` is `UNKNOWN`**: GitHub is still computing it. Treat as pending and re-poll; do not report it as a failure.
- **`gh pr checks` exits non-zero**: Not an error. It exits non-zero when checks are failing _or_ still pending. Classify from the JSON, not the exit code.
- **No checks configured on the repository**: Not an error. Treat the checks axis as satisfied and say so explicitly in the report.
- **`merge-main` stops on conflicts it cannot resolve**: Escalate with the conflicted file list.
- **`resolve-copilot-pr-feedback` reports `Partial` or `Failed`**: Escalate with its failure details.

### 3. `plugins/monitor-pr/README.md`

Standard shape: `# Monitor PR`, the marketplace description verbatim as the opening paragraph, then the three-line header block, `## Installation`, `## What It Does`, `## Usage`, `## Recommended Permissions`, `## Examples`, `## See Also`.

Header block:

```markdown
**Type:** Skill
**Trigger:** `/monitor-pr [<pr-number>]`
**Requires:** [`gh`](https://cli.github.com/) (authenticated)
```

`## What It Does` must document the harness split honestly: `ScheduleWakeup` pacing on Claude Code, blocking `sleep` on Codex CLI and OpenCode, and that `/loop /monitor-pr` is the recommended Claude Code invocation. It must also state that `reviewDecision` is reported but does not gate the ready determination.

`## Recommended Permissions` as a copy-pasteable JSON block with a single-line `allow` array (Prettier `printWidth: 10000`), covering every command the skill actually runs:

```json
{
  "permissions": {
    "allow": ["Bash(gh pr view *)", "Bash(gh pr checks *)", "Bash(gh pr edit *)", "Bash(gh pr merge *)", "Bash(gh api --paginate repos/*/pulls/*/reviews*)", "Bash(gh api graphql *)", "Bash(gh run view *)", "Bash(gh run list *)", "Bash(git push*)"]
  }
}
```

`## See Also` links `../pr/README.md`, `../resolve-copilot-pr-feedback/README.md`, `../merge-main/README.md`, `../lint-and-fix/README.md`, and closes with `- [All plugins](../../README.md)`.

### 4. Repository bookkeeping

1. **`.claude-plugin/marketplace.json`**: add an entry in alphabetical position by name, between `merge-main` and `notify`. Ten required fields, `"category": "ci-and-release"`, `"source": "./plugins/monitor-pr"`, `"version": "1.0.0"`, `description` identical to `plugin.json`.
1. **Root `README.md`**: add a row to the `### CI and Release` table (`README.md:132-144`) in alphabetical position, between Add GoReleaser Homebrew and Optimize Runner Usage. Display name `Monitor PR`, trigger `` `/monitor-pr` ``, "What it does" the marketplace description verbatim. Add an `**External tools:**` bullet to that section's list (`README.md:146-151`), alphabetically after Add GoReleaser Homebrew: `- _Monitor PR:_ [`gh`](https://cli.github.com/) (required; the skill reads check, review, and merge state over the GitHub API)`. Prettier repads the columns on `make format`, so exact padding need not be hand-computed.
1. **Catalog state**: run `bin/compute-catalog-state` and write the result into `.claude-plugin/marketplace.json`. One new `1.0.0` plugin takes `catalog-M63-m93-p142-n51` to `catalog-M64-m93-p142-n52`. Do not hand-compute it; run the script.
1. **Mirrors**: run `bin/build-codex-marketplace` and `bin/build-opencode-mirror`, and commit `.agents/plugins/marketplace.json`, the new `dist/codex/plugins/monitor-pr/` tree, and the new `dist/opencode/skills/monitor-pr` symlink. CI's mirror check uses `git status --porcelain dist/ .agents/`, so a forgotten untracked symlink fails the build.

No scrut coverage and no `SCRUT_ENV` / `scrut-env` changes: this plugin bundles no script, so validator rule 18 does not apply.

## The one real uncertainty

`ScheduleWakeup` is documented as the mechanism for `/loop` dynamic mode ("Schedule when to resume work in /loop dynamic mode"). Whether it can be called from a skill invoked bare as `/monitor-pr`, rather than as `/loop /monitor-pr`, is not established by the tool documentation and needs a live check during implementation.

Design so this does not matter much: attempt `ScheduleWakeup`; if it is unavailable or rejected, fall back to the blocking-`sleep` path that Codex CLI and OpenCode use anyway. Document `/loop /monitor-pr` in the README as the recommended Claude Code invocation. Verify the bare `/monitor-pr` path against a real PR before considering the skill done, and record the actual behavior in the README rather than the assumed behavior.

**Resolved during implementation.** `ScheduleWakeup` works when called from a skill invoked outside `/loop`. It was exercised repeatedly against PR #379, both to schedule wakeups with a delay and prompt and to end the watch with `stop: true`, and it neither errored nor required loop mode. `/loop /monitor-pr` remains a reasonable invocation but is not a requirement, and the blocking-`sleep` fallback is needed only on harnesses with no scheduler at all.

## Out of scope

- **`merge-main` uses a bare `git stash`** (`plugins/merge-main/skills/merge-main/SKILL.md:55`), which collides with the shared stash stack across worktrees. Real, but a separate issue.
- **The misleading no-op comment in `resolve-copilot-pr-feedback`** when Copilot has not reviewed yet. `monitor-pr` routes around it by only invoking that skill once a review exists at the current head, but the underlying skill still cannot tell the two cases apart. Worth its own issue.
- **Auto-merge and merge execution** beyond offering them in step 6. The skill asks; it does not decide.
- **Requiring an `APPROVED` review decision.** Deliberately excluded per the merge-ready decision above.

## Verification

1. **Structural validation passes.**

   ```bash
   bin/validate-json
   bin/validate-plugins
   ```

   This covers all 18 rules, including name-to-directory agreement, the ten required marketplace fields, version agreement between `plugin.json` and the marketplace entry, alphabetical ordering, catalog state, and generated-tree freshness.

1. **The Codex description budget still fits.** Rule 17 caps the sum of all generated Codex skill descriptions at 12,000 characters, and the current total is 11,636, leaving 364. The generated Codex description is the _marketplace_ description, not the SKILL.md one. The proposed 137-character description takes the total to roughly 11,773. `bin/validate-plugins` enforces this; if it errors, shorten the description rather than raising `CODEX_SKILL_DESCRIPTION_BUDGET`.

1. **Lint and format pass.**

   ```bash
   make lint
   ```

1. **Mirrors regenerate to exactly what is committed.**

   ```bash
   bin/build-codex-marketplace
   bin/build-opencode-mirror
   git status --porcelain dist/ .agents/
   ```

   The final command must print nothing.

1. **Full gate.**

   ```bash
   make test-all
   ```

1. **Versions are consistent.** Invoke the repo-local `check-versions` skill, per the repository's rule that another branch may have already moved a version.

1. **End-to-end against a real PR.** On a live PR in this repository, with a deliberately broken lint rule pushed first:
   - `/monitor-pr` resolves the PR from the current branch and reports which wait mechanism it selected.
   - It detects the lint failure, invokes `lint-and-fix --no-push`, commits, pushes, and resumes.
   - Quiet ticks print the one-line form; the failure prints the full table.
   - It waits for Copilot's review at the new head rather than declaring victory on the stale one.
   - It invokes `resolve-copilot-pr-feedback` only after a review exists at the current head.
   - On reaching the clean state it stops the loop, prints the full table including the non-blocking `reviewDecision`, and asks how to proceed.
   - Force an escalation (a test failure with an ambiguous fix) and confirm the loop stops and asks rather than guessing.
