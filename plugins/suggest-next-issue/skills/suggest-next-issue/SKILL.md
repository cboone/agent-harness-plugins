---
name: suggest-next-issue
description: >-
  Review all open GitHub issues in the current repository, analyze them in
  context (current branch state, recent work, project goals, dependencies), and
  recommend what to work on next with prioritized reasoning. Use when the user
  says "suggest next issue", "what should I work on next", "which issue should I
  tackle", "prioritize issues", "review open issues", "suggest an issue",
  "triage issues", or asks for help choosing between open issues. Also use
  when the user asks what can be worked on in parallel, or which issues avoid
  an exclusive resource another worktree is holding. Requires the gh CLI to be
  installed and authenticated.
---

# Suggest Next Issue

Analyze open GitHub issues and recommend what to work on next.

## Options

The user may provide these options inline:

- **label filter**: Focus on issues with a specific label (e.g., "suggest next bug" or "suggest next issue --label enhancement")
- **milestone filter**: Focus on issues in a specific milestone
- **limit**: Number of recommendations (default: 5)
- **include PRs**: Also consider open PRs needing attention (reviews, conflicts, CI failures)
- **--parallel-only**: Recommend only issues that can run beside the work already under way, excluding any whose verification needs an exclusive resource another worktree holds

## Workflow

### 1. Gather Context

Run these commands to build a complete picture:

```bash
# Open issues (with details for analysis)
gh issue list --state open --json number,title,labels,assignees,createdAt,updatedAt,comments,milestone,body --limit 100

# Recently closed issues (understand momentum)
gh issue list --state closed --json number,title,labels,closedAt --limit 10 --sort updated

# Current branches/worktrees (what's already in progress)
git worktree list
git branch --list --format='%(refname:short)'

# Current authenticated user (for assignment detection)
gh api user --jq '.login'

# Project context
gh repo view --json description,defaultBranchRef
```

If the user specified `--label` or `--milestone`, add the corresponding `--label` or `--milestone` flag to `gh issue list`.

If the user specified `--include-prs`:

```bash
gh pr list --state open --json number,title,labels,createdAt,updatedAt,isDraft,reviewDecision,statusCheckRollup
```

Also read the repo's README and any roadmap or project documentation to understand project goals.

**Read the exclusive-resource claims.** Some work cannot run in parallel because it needs a resource only one worktree can hold: a DAW, a simulator, a device, a database, a port, a shared install location. `create-worktree` and `address-issue-in-worktree` record those claims in the main worktree's `.claude/worktree-resources.local.json`. Resolve it from the first record of `git worktree list --porcelain`, whose `worktree` line is always the main worktree, and open the file with the Read tool:

```bash
git worktree list --porcelain
```

A missing file means no claims, which is the ordinary state and not an error. Each claim carries `resource`, `worktree`, `branch`, `claimed_at`, and an optional `issue`.

**Discount stale claims.** A claim whose `worktree` is absent from the `git worktree list` output already gathered above belongs to a worktree that has been removed. Treat it as free, and mention it so the user can clear it. Nothing that no longer exists should keep a resource reserved.

**Read the project's declared resources too.** Read whichever of `CLAUDE.md` and `AGENTS.md` exist in the repository root, and `copilot-instructions.md` under `.github/`. Any of them may be absent, which is normal, and `CLAUDE.md` is often a symlink to `AGENTS.md`, so read the target rather than treating it as a second source. Check any plan under `docs/plans/todo/` too. A heading containing "exclusive resource" names the project's resources and, usually, what kind of work needs each one. That list is what lets an issue be matched to a resource before anyone has claimed it.

### 2. Identify In-Progress Work

An issue is considered in progress if **any** of the following are true:

1. **Branch or worktree match**: A branch or worktree name contains the issue number (existing behavior)
1. **"in progress" label**: The issue has a label named "in progress" (case-insensitive match on the `labels` data already fetched in step 1)
1. **Assigned to current user**: The issue's `assignees` list (already fetched in step 1) includes the authenticated username from `gh api user`

Exclude in-progress issues from recommendations, but note them in the output as "already in progress" along with how each was detected (branch, label, assignment, or a combination).

A label-only match may mean local work is complete but the related PR is still waiting to merge. Keep excluding the issue in that state. Do not recommend it again only because no matching branch or worktree is visible.

### 3. Analyze Each Issue

Evaluate each open issue (that is not already in progress) on these signals:

| Signal                | Source                                                                 | Weight |
| --------------------- | ---------------------------------------------------------------------- | ------ |
| **Priority labels**   | Labels containing "bug", "critical", "urgent", "security"              | High   |
| **Dependencies**      | Issue body references to other issues (#N, "depends on", "blocked by") | High   |
| **Resource conflict** | Issue work or verification needs an exclusive resource already held    | High   |
| **Age**               | `createdAt` field                                                      | Medium |
| **Activity**          | Number of comments, `updatedAt` recency                                | Medium |
| **Effort**            | Issue body length/complexity, scope described                          | Low    |
| **Momentum fit**      | Similarity to recently closed issues                                   | Low    |

Dependency analysis: scan each issue body for references to other issues (`#N`, "depends on #N", "blocked by #N", "after #N"). Build a dependency graph to identify:

- Issues that **unblock** other open issues (high value)
- Issues that are **blocked** by other open issues (note the blocker)

Resource analysis: match each issue against the project's declared resources from step 1. An issue whose work or verification needs a resource a live claim holds is a poor next pick even when every other signal is strong, because starting it means either waiting or taking the resource away from work already under way. Say which resource and who holds it rather than silently ranking the issue down. Under `--parallel-only`, drop such issues from the recommendations entirely and list them separately.

This is advisory. An issue is never hidden outright unless `--parallel-only` was passed, because the user may well intend to finish the holding work first and start this next.

### 4. Generate Recommendations

Present the top N issues (default 5) organized by category:

**Categories** (use whichever apply, skip empty categories):

- **Safe to Parallelize**: Issues that need no resource a live claim holds, so they can start beside the work already under way
- **Narrow Scope**: Small, well-defined issues that touch few files and carry no open dependencies
- **High Impact**: Important features, critical bugs, or heavily requested items
- **Unblocks Others**: Issues that other open issues depend on
- **Overdue**: Old issues that have been neglected (use judgment based on repo's typical issue age)

Use **Safe to Parallelize** only when at least one resource is actually held. With nothing claimed, every issue qualifies and the category says nothing.

For each recommendation, include:

1. Issue number and title text (e.g., `#23 - Fix typo in help output`). Use the `title` field from the JSON, not the issue URL.
1. Labels and age
1. What it is: a brief summary of the issue (1-2 sentences distilled from the issue body, so the user understands the scope and substance without having to open the issue)
1. Why it's recommended (1-2 sentences with specific reasoning)
1. Suggested first steps or approach (1 sentence)
1. Blockers or considerations, if any, naming the resource and its holder when one applies

### 5. Summarize In-Progress Work

After recommendations, briefly list issues detected as in progress. For each, note how it was detected: branch/worktree, "in progress" label, assignment to current user, or a combination. This gives the user a complete picture of active work, including issues that may be waiting on PR merge after local implementation is done.

Then, when any resource is claimed, list who holds what: the resource, the branch, and whether the claim is stale. This is the half of the picture the issue list cannot show, and it is what answers "what can I work on in parallel" without the user having to remember the constraint. Skip the section entirely when nothing is claimed.

### 6. Offer to Start Work

End with an offer to create a worktree for the chosen issue via the `address-issue-in-worktree` skill. Example:

```text
Ready to start on one of these? Just say "start issue #N" or pick a number from the list.
```

## Example Output

```markdown
## Suggested Next Issues

### Safe to Parallelize

1. **#31 - Document the config schema** (documentation, 5 days old)
   Write reference docs for every key the config module accepts, with defaults and env overrides.
   Touches only `docs/`, so it needs nothing the `logic` claim is holding.
   Start: Read the config module's schema and mirror it.

### Narrow Scope

2. **#23 - Fix typo in help output** (bug, 2 days old)
   The `--version` flag prints "verison" instead of "version" in the CLI help text.
   Small fix, keeps the issue count tidy.
   Start: Check the help string in the CLI entry point.

### High Impact

3. **#18 - Add dark mode support** (enhancement, 12 days old, 4 comments)
   Add a system-preference-aware dark color scheme with a manual toggle in the settings panel.
   Most-requested feature. Pairs well with the theme work done in #15.
   Start: Add CSS variables for color scheme, then add a toggle component.

4. **#11 - Add manage-plan skill** (enhancement, 1 day old)
   Create a skill that can list, rename, archive, and delete saved plans from within a session.
   High-frequency workflow pattern from session analysis.
   Start: Review existing plan-related commands and design the skill interface.

### Unblocks Others

5. **#7 - Refactor config loading** (enhancement, 20 days old)
   Replace the ad-hoc JSON parsing with a centralized, schema-validated config module that supports defaults and env overrides.
   Issues #8 and #9 both depend on the new config system.
   Start: Extract config into a dedicated module with typed schema.

### Overdue

6. **#3 - Update installation docs** (documentation, 45 days old)
   The install guide still references the old `curl | bash` method; needs updating for the new package manager install flow.
   Open since v0.2. Quick update needed for current install process.
   Start: Compare current docs against actual install steps.

---

**Already in progress:**

- #14 -- feature/improve-notifications (branch)
- #16 -- fix/search-pagination (branch, assigned)
- #21 -- Add export feature (label: "in progress")
- #25 -- Fix auth timeout (assigned)

**Exclusive resources held:**

- `logic` -- feature/14-improve-notifications, claimed 2026-09-12T18:04:11Z
- `simulator` -- fix/99-old-thing (stale: that worktree no longer exists, clear it with `/create-worktree --release-resource simulator`)

#9 and #12 both need `logic` for verification, so they are better started once #14 is done.

Ready to start on one of these? Just say "start issue #N".
```

## Error Handling

- If `gh` is not authenticated, instruct the user to run `gh auth login`
- If no open issues exist, report that and suggest checking closed issues or creating new ones
- If all open issues are already in progress, report that and congratulate the user
- If the claim file is unreadable or malformed, say so and carry on without it. Resource awareness sharpens the recommendations; it is not a precondition for making them
- If `--parallel-only` leaves nothing to recommend, say which resources are held and which issues they hold back, rather than reporting an empty list
