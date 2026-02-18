---
name: suggest-next-issue
description: >-
  Review all open GitHub issues in the current repository, analyze them in
  context (current branch state, recent work, project goals, dependencies), and
  recommend what to work on next with prioritized reasoning. Use when the user
  says "suggest next issue", "what should I work on next", "which issue should I
  tackle", "prioritize issues", "review open issues", "suggest an issue",
  "triage issues", or asks for help choosing between open issues. Requires the
  gh CLI to be installed and authenticated.
---

# Suggest Next Issue

Analyze open GitHub issues and recommend what to work on next.

## Options

The user may provide these options inline:

- **label filter**: Focus on issues with a specific label (e.g., "suggest next bug" or "suggest next issue --label enhancement")
- **milestone filter**: Focus on issues in a specific milestone
- **limit**: Number of recommendations (default: 5)
- **include PRs**: Also consider open PRs needing attention (reviews, conflicts, CI failures)

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

### 2. Identify In-Progress Work

An issue is considered in progress if **any** of the following are true:

1. **Branch or worktree match**: A branch or worktree name contains the issue number (existing behavior)
1. **"in progress" label**: The issue has a label named "in progress" (case-insensitive match on the `labels` data already fetched in step 1)
1. **Assigned to current user**: The issue's `assignees` list (already fetched in step 1) includes the authenticated username from `gh api user`

Exclude in-progress issues from recommendations, but note them in the output as "already in progress" along with how each was detected (branch, label, assignment, or a combination).

### 3. Analyze Each Issue

Evaluate each open issue (that is not already in progress) on these signals:

| Signal              | Source                                                                 | Weight |
| ------------------- | ---------------------------------------------------------------------- | ------ |
| **Priority labels** | Labels containing "bug", "critical", "urgent", "security"              | High   |
| **Dependencies**    | Issue body references to other issues (#N, "depends on", "blocked by") | High   |
| **Age**             | `createdAt` field                                                      | Medium |
| **Activity**        | Number of comments, `updatedAt` recency                                | Medium |
| **Effort**          | Issue body length/complexity, scope described                          | Low    |
| **Momentum fit**    | Similarity to recently closed issues                                   | Low    |

Dependency analysis: scan each issue body for references to other issues (`#N`, "depends on #N", "blocked by #N", "after #N"). Build a dependency graph to identify:

- Issues that **unblock** other open issues (high value)
- Issues that are **blocked** by other open issues (note the blocker)

### 4. Generate Recommendations

Present the top N issues (default 5) organized by category:

**Categories** (use whichever apply, skip empty categories):

- **Quick Wins**: Small, well-defined issues that can be resolved quickly
- **High Impact**: Important features, critical bugs, or heavily requested items
- **Unblocks Others**: Issues that other open issues depend on
- **Overdue**: Old issues that have been neglected (use judgment based on repo's typical issue age)

For each recommendation, include:

1. Issue number and title text (e.g., `#23 - Fix typo in help output`). Use the `title` field from the JSON, not the issue URL.
1. Labels and age
1. What it is: a brief summary of the issue (1-2 sentences distilled from the issue body, so the user understands the scope and substance without having to open the issue)
1. Why it's recommended (1-2 sentences with specific reasoning)
1. Suggested first steps or approach (1 sentence)
1. Blockers or considerations, if any

### 5. Summarize In-Progress Work

After recommendations, briefly list issues detected as in progress. For each, note how it was detected: branch/worktree, "in progress" label, assignment to current user, or a combination. This gives the user a complete picture of active work.

### 6. Offer to Start Work

End with an offer to create a worktree for the chosen issue via the `create-worktree-from-issue` skill. Example:

```text
Ready to start on one of these? Just say "start issue #N" or pick a number from the list.
```

## Example Output

```markdown
## Suggested Next Issues

### Quick Wins
1. **#23 - Fix typo in help output** (bug, 2 days old)
   The `--version` flag prints "verison" instead of "version" in the CLI help text.
   Small fix, keeps the issue count tidy.
   Start: Check the help string in the CLI entry point.

### High Impact
2. **#18 - Add dark mode support** (enhancement, 12 days old, 4 comments)
   Add a system-preference-aware dark color scheme with a manual toggle in the settings panel.
   Most-requested feature. Pairs well with the theme work done in #15.
   Start: Add CSS variables for color scheme, then add a toggle component.

3. **#11 - Add manage-plan skill** (enhancement, 1 day old)
   Create a skill that can list, rename, archive, and delete saved plans from within a session.
   High-frequency workflow pattern from session analysis.
   Start: Review existing plan-related commands and design the skill interface.

### Unblocks Others
4. **#7 - Refactor config loading** (enhancement, 20 days old)
   Replace the ad-hoc JSON parsing with a centralized, schema-validated config module that supports defaults and env overrides.
   Issues #8 and #9 both depend on the new config system.
   Start: Extract config into a dedicated module with typed schema.

### Overdue
5. **#3 - Update installation docs** (documentation, 45 days old)
   The install guide still references the old `curl | bash` method; needs updating for the new package manager install flow.
   Open since v0.2. Quick update needed for current install process.
   Start: Compare current docs against actual install steps.

---

**Already in progress:**
- #14 — feature/improve-notifications (branch)
- #16 — fix/search-pagination (branch, assigned)
- #21 — Add export feature (label: "in progress")
- #25 — Fix auth timeout (assigned)

Ready to start on one of these? Just say "start issue #N".
```

## Error Handling

- If `gh` is not authenticated, instruct the user to run `gh auth login`
- If no open issues exist, report that and suggest checking closed issues or creating new ones
- If all open issues are already in progress, report that and congratulate the user
