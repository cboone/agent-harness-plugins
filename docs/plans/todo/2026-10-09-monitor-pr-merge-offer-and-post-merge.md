# Monitor PR: merge offer, merge watch, and post-merge sync

## Context

`monitor-pr` currently ends at a ready PR by asking "squash, merge, or rebase, auto-merge, or leave it". That has three problems. It offers methods the repository may forbid. It re-asks a question whose answer is usually fixed per repository. And nothing happens after the merge, so sibling worktree sessions and the main worktree's `main` drift until someone notices.

Intended outcome:

1. At readiness, offer **one** merge method: the one the repository actually permits, preferring a merge commit.
1. Without blocking that offer, watch the PR in the background until it merges, whoever merges it.
1. On merge, fast-forward the base branch in the main worktree and notify the other agent sessions working in the repository's worktrees.
1. On repositories that require approval, wait for approval first, then offer the merge and keep watching.

The public skill stays generic. Swing Left specifics live only in Chris's global instructions.

Findings that shape the design (checked 2026-10-09):

- `swing-left/frontend` repo settings allow merge commits and squash, but its `main` ruleset allows only `squash` and requires 1 approval. Repo settings alone pick the wrong method, so merge methods must come from `gh api repos/O/R/rules/branches/BASE` (`pull_request` rule `parameters.allowed_merge_methods`, `required_approving_review_count`) intersected with the repo's `allow_*` settings, plus classic branch protection where present.
- `swing-left/gt-analytics-dashboard` has no rules, so detection alone misses some client repos. An instruction-level policy covers them.
- `~/.claude/CLAUDE.md` is 8,190 of 8,192 bytes, so adding the policy means trimming existing wording.
- `ListAgents` shows each peer's tmux pane (`%470`) but not its cwd. `tmux list-panes -a -F '#{pane_id} #{pane_current_path}'` maps panes to directories, which can then be matched against `git worktree list --porcelain`.

## Decisions (from interview)

- **Approval policy**: detect from rulesets and branch protection, and also honor any instruction in the user's or project's agent config saying the repository's PRs need approval before merge. Add those words to the existing client-repos line in the global `CLAUDE.md`.
- **Merge method memory**: derive the allowed methods from GitHub on every run. When exactly one is allowed, use it without asking about the method. When several are allowed, use the method named by the repository's agent config or the harness's durable memory. Otherwise default to a merge commit, confirm it once, and save a per-repository note in harness memory (Claude Code memory; skip where the harness has none and say so).
- **After approval**: offer the merge like any other repo, with the background watch still running.
- **Notification**: harness peer messaging (Claude Code `ListAgents` and `SendMessage`) to sessions whose pane cwd is inside any of the repository's worktrees, excluding this session. The message is informational: PR number and URL, merge commit SHA, base branch, and whether the main worktree was fast-forwarded. Recipients decide whether to merge main.

## Changes

### `plugins/monitor-pr/skills/monitor-pr/SKILL.md`

Replace step 8's merge question and add new steps. Keep step numbering stable for existing cross-references where possible by inserting the new material as sub-steps of step 8 (8a to 8e) rather than renumbering 9.

1. **Step 1 snapshot**: no change to the `gh pr view` fields, which already carry `reviewDecision` and `baseRefName`. Add `mergeCommit` only to the merge-watch probe below.
1. **New "Merge policy" section** (referenced from step 8), run once per watch and recorded in watch state:
   - Allowed methods: `gh api repos/OWNER/REPO --jq '{allow_merge_commit,allow_squash_merge,allow_rebase_merge}'` intersected with every `pull_request` rule's `allowed_merge_methods` from `gh api repos/OWNER/REPO/rules/branches/BASE`. A failed rules read is not "no rules": report it and fall back to asking with all repo-allowed methods.
   - Method choice order: only one allowed → that one; repo agent config names one; harness memory note for `OWNER/REPO`; else `merge` if allowed, then confirm once and record the note. Never list all methods by default.
   - Approval required when any of: a `pull_request` rule with `required_approving_review_count` above 0, classic branch protection with required reviews, `reviewDecision` of `REVIEW_REQUIRED`, or an instruction in the loaded user or project agent config saying this repository's PRs need approval before merge. The skill names which source applied.
1. **Step 8 rewrite (Terminal report, then merge)**:
   - 8a. Print the existing report (unchanged content, including `BLOCKED`, draft and advisory-request caveats).
   - 8b. **Approval gate**: when approval is required and `reviewDecision` is not `APPROVED`, report "Ready, awaiting approval", start the merge watch (8c) in approval-waiting mode, and do not offer the merge yet. `CHANGES_REQUESTED` escalates per step 9. A push during the wait sends the watch back to step 3, since rulesets may dismiss stale approvals.
   - 8c. **Merge watch**, started before the merge offer so it never waits on the user. Claude Code: a `Bash` `run_in_background` loop polling `gh pr view N --repo O/R --json state,reviewDecision,mergeCommit` every 60 seconds, exiting on `MERGED`, `CLOSED`, or (approval-waiting mode) a `reviewDecision` change. The harness re-invokes the session when it exits. Codex: a scheduled task with the same exit conditions. Foreground fallback: say plainly that the watch cannot run alongside the question, ask first, then poll under the existing `--ticks` rules. Record the watcher ID in watch state and stop it on any terminal path.
   - 8d. **Merge offer**: one question naming the chosen method, for example "Merge #361 with a merge commit?". End the turn with the question in plain text rather than a blocking question tool, so a merge by someone else can wake the session. On yes, run `gh pr merge N --repo O/R --<method>` without `--delete-branch` (the head branch is usually checked out in a worktree). Do not offer auto-merge unless checks are still pending at that moment.
   - 8e. **Post-merge**, triggered only by observing `state: MERGED`, whichever path observed it, once per merge commit SHA:
     1. Fast-forward the base branch in the main worktree (first entry of `git worktree list --porcelain`): `git -C MAIN fetch origin BASE`, then `git -C MAIN merge --ff-only origin/BASE` when `BASE` is checked out there, or `git -C MAIN fetch origin BASE:BASE` when it is not. Never stash, reset or force. Report a refusal (dirty files in the way, diverged base) instead of working around it.
     1. Notify peers: list sessions, map each pane to its cwd, keep those inside any worktree path of this repository, exclude this session, and send the informational message. On harnesses without peer messaging, report that no sessions were notified.
     1. Print a final line with the merge SHA, the fast-forward result and the sessions notified, then stop the watch.
   - `CLOSED` without merge: report and stop, with no sync or notification.
1. **Steps 4, 9, Reporting Format, Error Handling**: route the "all four axes clean" terminal through step 8's new flow; stop the merge watch on escalation; add status line forms `awaiting approval` and `watching for merge`; add error entries for a failed rules read, a refused fast-forward and an unreachable peer.
1. **Dependabot section**: unchanged behavior except that 8e also applies after a Dependabot merge.
1. **`--no-fix`**: report what 8c to 8e would do and perform none of them, consistent with "observe and report only".

### `plugins/monitor-pr/skills/monitor-pr/references/checkpoint.md`

Add fields: merge policy (allowed methods, chosen method and its source, approval requirement and its source), merge-watch mode and watcher ID, and the post-merge guard (merge SHA processed).

### `plugins/monitor-pr/README.md`, `.claude-plugin/marketplace.json`, root `README.md`

Describe the merge offer, approval wait, merge watch, and post-merge sync. Update the catalog description to mention offering the merge and syncing after it, and copy it verbatim into both READMEs. Keep the `install` anchor link.

### `plugins/monitor-pr/.claude-plugin/plugin.json`

Bump `2.0.0` → `2.1.0` (new capability; existing options unchanged).

### Outside this repository

- `~/.claude/CLAUDE.md` (claudefiles bare repo, per `~/.claude/claude-dotfiles-data/.claude/CLAUDE.md`): extend the client-repos line with "their PRs need approval before merge", trimming other wording so the file stays within 8 KiB. Commit signed through the claudefiles repo.
- Update the existing `merge-commits-only` memory note so its "How to apply" points at the skill's rules-aware method detection.

## Housekeeping

- Rename this plan to `docs/plans/todo/2026-10-09-monitor-pr-merge-offer-and-post-merge.md` and commit it first.
- Empty sibling branches `feature/decrease-copilot-rounds` and `feature/add-pr-monitoring-options` may also touch `monitor-pr`; check them for new commits before opening the PR and merge main as needed.
- Use `write-markdown` before editing Markdown. Small signed Conventional Commits at logical boundaries.

## Verification

1. `make build`, `make lint`, `make validate`, `make test-scrut`, then the `check-versions` skill.
1. Dry-run the policy commands against real repos and confirm the chosen method: `cboone/agent-harness-plugins` → merge commit, no approval; `swing-left/frontend` → squash, approval via ruleset; `swing-left/gt-analytics-dashboard` → approval via the global instruction, method per memory or merge commit.
1. Confirm the pane-to-worktree mapping: run `ListAgents` and `tmux list-panes -a -F '#{pane_id} #{pane_current_path}'` and check that the matched set covers sessions in `agent-harness-plugins__worktrees/*` and nothing else.
1. End to end on this PR: let `monitor-pr` reach readiness, confirm it offers only a merge commit with the background watch running, merge from the GitHub UI instead, and confirm the session wakes, fast-forwards `main` in `/Users/ctm/Development/agent-harness-plugins`, and notifies sibling sessions.
