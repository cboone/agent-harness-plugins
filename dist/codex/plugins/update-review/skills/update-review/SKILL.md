---
name: update-review
description: >-
  Find the latest branch review, assess commits made since, and update the
  review document with a synthesized reassessment.
---

# Update Review

Find the latest saved review for the current branch, identify commits made since that review, and produce a unified updated document that synthesizes the original assessment with new work.

## Options

The user may provide these options inline:

- **--review `<path>`**: Path to a specific review document to update (overrides auto-detection)
- **--plan `<path>`**: Path to a plan document to compare progress against
- **--brief**: Output only a high-level summary without the detailed breakdown

## Workflow

### 1. Find the Review Document

If the user specified `--review <path>`, use that file. Otherwise, auto-detect:

1. **Get the current branch name**:

```bash
git branch --show-current
```

If this command returns an empty string (detached HEAD), treat the branch name as `HEAD` before sanitizing.

1. **Sanitize the branch name** for filename matching:

- Replace `/` and any other characters that are unsafe in filenames (spaces, colons, backslashes) with `-`
- Collapse consecutive hyphens into a single hyphen
- Remove leading and trailing hyphens
- If the result is empty after these steps, fall back to `HEAD` as the name

1. **Search for matching review files**:

```bash
ls docs/reviews/*-<sanitized-branch-name>.md 2>/dev/null
```

1. **Select the review file**:

- If exactly one file matches, use it
- If multiple files match, sort by filename (date prefix) and:
  - If the matching files have different date prefixes, use the most recent (highest date prefix)
  - If multiple files share the same date prefix, list them and ask the user which one to update
- If no files match, report that no review was found for this branch and suggest running `/review-branch` first, then stop

### 2. Parse the Existing Review

Read the review document and extract metadata from the header block:

- **Base**: The base ref and merge base hash from the `Base:` line
- **Commits**: The count of previously reviewed commits from the `Commits:` line
- **Files changed**: The file change counts from the `Files changed:` line
- **Reviewed through**: The commit hash from the `Reviewed through:` line

Also read all section content (Summary, Changes by Area, File Inventory, Notable Changes, Plan Compliance, Code Quality Assessment) to use as context when synthesizing the update.

**Legacy fallback**: If the document does not contain a `Reviewed through:` line (generated before this metadata was added), infer the last reviewed commit:

1. Extract the merge base hash from the `Base:` line
1. Extract the commit count from the `Commits:` line
1. Find the Nth commit on the branch:

```bash
git log --oneline --reverse <merge-base>..HEAD | sed -n '<count>p' | awk '{print $1}'
```

Report a warning that the review document uses a legacy format and will be upgraded with a `Reviewed through:` line in the updated output.

### 3. Gather New Changes

1. **Verify the "Reviewed through" commit** still exists on the current branch:

```bash
git rev-parse --verify <reviewed-through-hash>
git merge-base --is-ancestor <reviewed-through-hash> HEAD
```

If the hash is not found or is not an ancestor of HEAD (due to rebase or force-push), report the issue and suggest running a fresh `/review-branch` instead. Stop.

1. **Check for new commits**:

```bash
git log --oneline <reviewed-through-hash>..HEAD
```

If there are no new commits (HEAD equals the "Reviewed through" hash), report that the review is already current and stop.

1. **Gather the delta** (new changes since last review). Run these in parallel:

```bash
# New commits since last review
git log --oneline <reviewed-through-hash>..HEAD

# Delta diff stats
git diff --stat <reviewed-through-hash>..HEAD

# Delta full diff
git diff <reviewed-through-hash>..HEAD

# New commit messages in detail
git log --format='%h %s%n%n%b' --no-merges <reviewed-through-hash>..HEAD
```

1. **Gather the full picture** (for the unified review). Run these in parallel:

```bash
# Recalculate merge base (may have changed if base branch advanced)
git merge-base <base-ref> HEAD

# Full commit history from merge base
git log --oneline <merge-base>..HEAD

# Full diff stats from merge base
git diff --stat <merge-base>..HEAD

# Full diff from merge base
git diff <merge-base>..HEAD

# Current HEAD hash
git rev-parse --short HEAD

# Today's date for the Updated: metadata line
date +%Y-%m-%d
```

### 4. Assess the Delta

Analyze the new commits in the context of the existing review. For each section of the review, determine what has changed:

#### 4a. Summary

Does the branch's overall purpose or narrative change with the new work? Update the summary to cover all work, noting significant new directions.

#### 4b. Changes by Area

What new areas are affected? Do existing areas have additional changes? Merge new area information into the existing groupings.

#### 4c. File Inventory

Recalculate the complete file inventory from the merge base to HEAD. Note which files are newly added, modified, or deleted since the last review.

#### 4d. Notable Changes

Are there new notable changes (dependencies, configs, APIs, security) since the last review?

#### 4e. Plan Compliance

If a plan is available, re-evaluate all plan items from scratch against the full diff (merge base to HEAD). Items that were "Partially done" or "Not started" in the previous review may have progressed. Note the progression explicitly.

**Plan detection**: If the user specified `--plan <path>`, use that file. Otherwise, auto-detect:

1. Look for plan files in common plan directories (`docs/plans/todo/`, `docs/plans/in-progress/`, `docs/plans/`)
1. Search for plan files whose name matches the current branch name (with type prefixes and hyphens/underscores normalized). For example, branch `feature/add-dark-mode` would match a plan named `add-dark-mode.md`.
1. If exactly one plan matches, use it. If multiple plans match, list them and ask the user which to use. If no plans match, skip plan evaluation entirely.

#### 4f. Code Quality Assessment

Evaluate the full diff (merge base to HEAD) but pay special attention to the delta. Note:

- Issues from the prior review that have been addressed
- New issues introduced since the prior review
- Overall trajectory: is the code quality improving, stable, or regressing?

#### 4g. Brief Mode

If **--brief** was specified, output only the high-level summary (4a) and file inventory counts. For plan compliance, include only the compliance verdict and overall progress fraction. For code quality, include only the assessment verdict. Skip the detailed breakdowns.

### 5. Synthesize the Updated Review

Produce a single unified document that replaces the old review. Use the same format as the review-branch output template, with additional metadata:

```markdown
## Branch Review: <branch-name>

Base: <base-ref> (merge base: <merge-base-short-hash>)
Commits: <new-total-count>
Files changed: <new-total-count> (<added> added, <modified> modified, <deleted> deleted, <renamed> renamed)
Reviewed through: <head-short-hash>
Updated: <today's date> (previous: <original-review-date or "unknown">)

### Summary

<unified summary covering all work, noting what changed since last review>

### Changes by Area

<all areas, with new changes since last review integrated>

### File Inventory

<complete file inventory from merge base to HEAD>

### Notable Changes

<all notable changes>

### Plan Compliance

<full re-evaluation against plan, noting progress since last review>

### Code Quality Assessment

<unified assessment highlighting:

- issues from prior review that have been addressed
- new issues introduced since prior review
- overall trajectory>

### Changes Since Last Review

<concise summary of what the new commits added, changed, or fixed>
```

The `Updated:` metadata line records the update date and links back to the original review date (extracted from the original filename's date prefix). If the filename does not start with a `YYYY-MM-DD-` prefix (e.g., when using `--review` with a custom path), use `"unknown"` as the previous date value.

The `Changes Since Last Review` section provides a quick-reference delta so the reader can see what is new without reading the entire document. This section is specific to updated reviews and does not appear in fresh review-branch output.

Adjust section headers and content to fit what is actually present. Omit empty sections. The **Plan Compliance** and **Code Quality Assessment** sections are the most important outputs of this review: make them thorough, specific, and direct.

### 6. Write the Updated Review

Overwrite the existing review file at its original path. Do not change the filename (the original date prefix is preserved).

Report the update to the user, using the actual path of the review file (the resolved `--review` path or the auto-detected path):

```text
Review updated: <review-path>
Previous review covered N commits through <old-hash>
Updated review covers M commits through <new-hash> (K new commits)
```

Include a hint about the address-review skill:

```text
To address the items in this review, run: /address-review <review-path>
```

## Error Handling

- **No review found**: Report that no review document was found for the current branch in `docs/reviews/` and suggest running `/review-branch` first.
- **"Reviewed through" hash not found**: If the commit hash recorded in the review no longer exists on the branch (due to force-push, rebase, or history rewrite), report the issue and suggest running a fresh `/review-branch`.
- **No new commits**: If HEAD equals the "Reviewed through" hash, report that the review is already current and stop.
- **Legacy format (no "Reviewed through" line)**: Fall back to inferring the last reviewed commit from the commit count and merge base. Warn about the legacy format and include the `Reviewed through:` line in the updated output.
- **Multiple review files, same date**: If multiple review files match the branch name pattern within the same date, list them and ask the user which to update.
- **Save failure**: If the review file cannot be written (e.g., read-only filesystem, permissions issue), report the error but do not fail the entire review. The terminal output is already complete.
- **Detached HEAD**: Use `HEAD` as the branch name and note that the review is running in detached HEAD state.
- **Large diffs**: If the delta diff is extremely large (thousands of lines), focus on the stat output and commit messages rather than reading the entire diff line by line. Note that the detailed diff was too large for full analysis.
