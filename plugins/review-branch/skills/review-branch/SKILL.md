---
name: review-branch
description: >-
  Summarize all work done on the current branch compared to the base branch,
  grouping changes by area and highlighting notable modifications. Optionally
  compare progress against a plan document. Use when the user says
  "review branch", "review the work done on this branch",
  "summarize this branch", "where are we on this branch",
  "what's been done on this branch", "branch summary",
  "compare branch to plan", or any variant involving reviewing or
  summarizing the work on the current branch.
---

# Review Branch

Summarize all work done on the current branch, optionally comparing progress against a plan document.

## Options

The user may provide these options inline:

- **--plan `<path>`**: Path to a plan document to compare progress against
- **--since `<ref>`**: Use a specific tag, branch, or commit as the base reference instead of the default branch
- **--brief**: Output only a high-level summary without the detailed breakdown

## Workflow

### 1. Determine the Base Reference

Identify the base to diff against:

1. **If `--since <ref>` was specified**, use that ref as the base. Verify it exists:

```bash
git rev-parse --verify <ref>
```

1. **Otherwise**, detect the repository's default branch:

```bash
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
```

If `gh` is not available or the command fails, fall back to a purely local query of the remote HEAD ref:

```bash
git rev-parse --abbrev-ref origin/HEAD | sed 's@^origin/@@'
```

1. **Find the merge base** between the base reference and HEAD:

```bash
git merge-base <base-ref> HEAD
```

Use this merge base as the actual comparison point for all subsequent commands. This ensures the diff only includes changes made on this branch, not changes made on the base branch since diverging.

**If HEAD equals the merge base** (no commits on this branch), report that there are no changes to review and stop.

### 2. Gather Changes

Run these commands in parallel:

```bash
# Commit history on this branch
git log --oneline <merge-base>..HEAD

# File-level summary (insertions, deletions, renames)
git diff <merge-base>..HEAD --stat

# Full diff for detailed analysis
git diff <merge-base>..HEAD

# Current branch name
git branch --show-current
```

Also read the commit messages in detail to understand the intent behind each change:

```bash
git log <merge-base>..HEAD --format='%h %s%n%n%b' --no-merges
```

### 3. Summarize the Work

Analyze the full diff and commit history to produce a structured summary.

#### 3a. High-Level Summary

Write a 2-4 sentence overview of what this branch accomplishes. Focus on the purpose and outcome, not individual file changes.

#### 3b. Group Changes by Area

Organize all changes into logical groups based on what they affect. Use groups that fit the actual changes — common groupings include but are not limited to:

- API / endpoints
- UI / frontend
- Data models / schema
- Business logic
- Tests
- Configuration / build
- Documentation
- Dependencies

For each group, list:

- What changed and why (1-2 sentences)
- Files involved

Skip groups that have no changes. Name groups to match the project's domain (e.g., "Authentication" instead of "Business logic" when all changes relate to auth).

#### 3c. File Inventory

Provide counts and lists organized by change type:

- **New files**: Files added on this branch
- **Modified files**: Files changed on this branch
- **Deleted files**: Files removed on this branch
- **Renamed files**: Files moved or renamed on this branch

#### 3d. Notable Changes

Highlight anything that deserves special attention:

- New or changed dependencies (package.json, go.mod, Gemfile, requirements.txt, Cargo.toml, etc.)
- Configuration changes (CI/CD, linter configs, build configs)
- Schema or migration changes
- API changes (new endpoints, changed signatures, breaking changes)
- Security-relevant changes (auth, permissions, crypto, input validation)

If there are no notable changes worth highlighting, skip this section.

#### 3e. Brief Mode

If **--brief** was specified, output only the high-level summary (3a) and the file inventory counts (3c, counts only — not the full file lists). Skip sections 3b, 3d, and the plan comparison (step 4).

### 4. Compare Against Plan (if provided)

This step only runs if the user specified `--plan <path>` or if a plan was auto-detected.

#### 4a. Auto-Detection

If no `--plan` was specified, attempt to find a relevant plan:

1. Look for plan directories commonly used in projects:

```bash
# Check common plan directory locations
ls docs/plans/todo/ 2>/dev/null
ls docs/plans/in-progress/ 2>/dev/null
ls docs/plans/ 2>/dev/null
```

1. Search for plan files whose name matches the current branch name (with type prefixes and hyphens/underscores normalized). For example, branch `feature/add-dark-mode` would match a plan named `add-dark-mode.md`.

1. If exactly one plan matches, use it. If multiple plans match, list them and ask the user which to use. If no plans match, skip the plan comparison entirely.

#### 4b. Parse the Plan

Read the plan document and identify actionable items. Plans may use various formats:

- **Checkboxes**: `- [ ]` (incomplete) and `- [x]` (complete)
- **Numbered lists**: Sequential steps or phases
- **Headings as phases**: `## Phase 1`, `### Step 1`, etc.
- **Bullet points**: Unnumbered task lists

Extract every actionable item from the plan, preserving its hierarchy (phase/section grouping).

#### 4c. Match Work to Plan Items

For each plan item, determine its status based on the branch's changes:

- **Completed**: The diff clearly implements this item. Changes in the diff directly address the described work.
- **In progress**: Some related changes exist but the item is not fully implemented.
- **Not started**: No changes in the diff relate to this item.

Use the commit messages, file changes, and diff content to make these determinations. Be conservative — only mark an item as "Completed" when the evidence is clear.

#### 4d. Report Plan Progress

Present the comparison as a progress report:

1. **Overall progress**: A fraction and percentage (e.g., "7/12 items completed (58%)")
1. **Completed items**: List each with a brief note about which changes implement it
1. **In-progress items**: List each with what has been done and what remains
1. **Remaining items**: List items not yet started

If the plan uses phases or sections, preserve that grouping in the report.

### 5. Output the Review

Structure the final output with clear sections:

```markdown
## Branch Review: <branch-name>

Base: <base-ref> (merge base: <short-hash>)
Commits: <count>
Files changed: <count> (<added> added, <modified> modified, <deleted> deleted, <renamed> renamed)

### Summary

<high-level summary>

### Changes by Area

<grouped changes>

### File Inventory

<new/modified/deleted/renamed files>

### Notable Changes

<highlighted items>

### Plan Progress

<plan comparison, if applicable>
```

Adjust section headers and content to fit what is actually present. Omit empty sections.

## Error Handling

- **No commits on this branch**: Report that the branch has no changes compared to the base and stop.
- **Invalid --since ref**: If the specified ref does not exist, report the error and suggest checking the ref name.
- **Plan file not found**: If `--plan <path>` points to a non-existent file, report the error and continue with the review without plan comparison.
- **No gh CLI**: Fall back to `git remote show origin` for base branch detection. The review does not require `gh`.
- **Detached HEAD**: Use `HEAD` as the branch name and note that the review is running in detached HEAD state.
- **Large diffs**: If the diff is extremely large (thousands of lines), focus the summary on the stat output and commit messages rather than reading the entire diff line by line. Note that the detailed diff was too large for full analysis.
