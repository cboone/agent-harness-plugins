# Mention connected issues in PR descriptions

## Context

Branches created by `create-worktree-from-issue` use a `TYPE/SLUG` format (e.g., `feature/add-dark-mode-support`) with **no issue number** embedded. The current PR skill only references issues when the branch name contains an explicit pattern like `fix/issue-42`. This means PRs created from issue-derived branches almost never link back to their source issues, and those issues never auto-close on merge.

This enhancement adds a multi-strategy issue detection step to the PR skill so that connected issues are always discovered and mentioned with GitHub closing keywords (`Closes #N` / `Fixes #N`).

## Files to modify

| File | Change |
|------|--------|
| `plugins/pr/skills/pr/SKILL.md` | Add issue detection step, update PR body template, update commit/report steps, add error handling |
| `plugins/pr/.claude-plugin/plugin.json` | Bump version `1.0.1` → `1.1.0` |
| `.claude-plugin/marketplace.json` | Mirror version bump for PR plugin entry |

## Plan

### 1. Add step "1b. Detect Connected Issues" within Gather Context

Insert a new sub-step after the existing context-gathering commands (after line 56) that runs three strategies in sequence:

**Strategy 1 — Issue numbers in the branch name:**
Parse the current branch name for issue numbers in patterns like:
- `TYPE/N-description` (e.g., `fix/42-login-bug` → #42)
- `TYPE/description-N` (e.g., `feature/login-bug-42` → #42)
- `TYPE/issue-N-description` (e.g., `fix/issue-42` → #42)
- `N-description` (e.g., `42-add-login` → #42)

Verify each candidate with `gh issue view NUMBER --json number,title,state`.

**Strategy 2 — Issue references in commit messages:**
Scan `git log <base-branch>..HEAD` output (already gathered) for `#N` references. Verify each with `gh issue view`.

**Strategy 3 — GitHub issue search by branch slug (only if strategies 1 and 2 found nothing):**
Extract the slug after the first `/`, convert hyphens to spaces, and search:

```bash
gh issue list --search "KEYWORDS" --state open --json number,title --limit 5
```

- **1 result** → include it
- **Multiple results** → include only if one title, when slugified, closely matches the branch slug
- **0 results** → skip

Merge all results into a deduplicated list.

### 2. Update Step 3 (Commit Changes)

Replace the existing branch-name-only issue reference instruction (line 74) with a broader one that references all issues detected in step 1b.

### 3. Update Step 5 (PR Body) with a `## Closes` section

Add a conditional `## Closes` section at the end of the PR body template, after `## Test plan`:

```markdown
## Closes

Closes #18
```

- `fix/*` branches use `Fixes #N`
- All other branches use `Closes #N`
- If no issues were detected, omit the section entirely

Update the `gh pr create` example to show the section.

### 4. Update Step 6 (Report Results)

Add connected issues and closing keywords to the post-creation report.

### 5. Add error handling

- Issue detection failures (network, auth) → skip silently; never block PR creation
- Already-closed issues → still include (creates cross-reference; GitHub handles gracefully)

### 6. Bump versions

- `plugins/pr/.claude-plugin/plugin.json`: `1.0.1` → `1.1.0` (new capability)
- `.claude-plugin/marketplace.json` PR entry: `1.0.1` → `1.1.0`
- No marketplace metadata version bump (no plugin added or removed)

## Verification

1. Test with a branch containing an issue number (e.g., `fix/42-something`) — should detect #42 from branch name
2. Test with a branch created via `create-worktree-from-issue` (e.g., `feature/add-dark-mode-support`) — should find the issue via slug search
3. Test with a branch that has `#N` references in commit messages — should detect from commits
4. Test with a branch that has no connected issues — should produce a PR body with no `## Closes` section
5. Verify `plugin.json` and `marketplace.json` versions match at `1.1.0`
