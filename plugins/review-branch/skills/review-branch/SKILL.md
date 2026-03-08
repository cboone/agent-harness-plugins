---
name: review-branch
description: >-
  Review and evaluate all work done on the current branch: summarize changes,
  rigorously assess plan compliance, and independently evaluate code quality.
  Use when the user says "review branch", "review the work done on this branch",
  "summarize this branch", "where are we on this branch",
  "what's been done on this branch", "branch summary",
  "compare branch to plan", "evaluate this branch", or any variant involving
  reviewing, summarizing, or evaluating the work on the current branch.
---

# Review Branch

Review and evaluate all work done on the current branch: summarize changes, assess plan compliance, and evaluate code quality on its own merits.

## Options

The user may provide these options inline:

- **--plan `<path>`**: Path to a plan document to compare progress against
- **--since `<ref>`**: Use a specific tag, branch, or commit as the base reference instead of the default branch
- **--brief**: Output only a high-level summary without the detailed breakdown
- **--no-save**: Skip saving the review to `docs/reviews/` (default: save after outputting)

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
git merge-base < base-ref > HEAD
```

Use this merge base as the actual comparison point for all subsequent commands. This ensures the diff only includes changes made on this branch, not changes made on the base branch since diverging.

**If HEAD equals the merge base** (no commits on this branch), report that there are no changes to review and stop.

### 2. Gather Changes

Run these commands in parallel:

```bash
# Commit history on this branch
git log --oneline < merge-base > ..HEAD

# File-level summary (insertions, deletions, renames)
git diff --stat < merge-base > ..HEAD

# Full diff for detailed analysis
git diff < merge-base > ..HEAD

# Current branch name
git branch --show-current

# Current HEAD commit (for "Reviewed through" metadata)
git rev-parse --short HEAD
```

Also read the commit messages in detail to understand the intent behind each change:

```bash
git log --format='%h %s%n%n%b' --no-merges < merge-base > ..HEAD
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

If **--brief** was specified, output only the high-level summary (3a) and the file inventory counts (3c, counts only, not the full file lists). Skip sections 3b and 3d. For plan compliance (step 4), include only the compliance verdict and overall progress fraction. For code quality (step 5), include only the assessment verdict. Skip the detailed breakdowns in both evaluation steps.

### 4. Evaluate Plan Compliance

This step runs when a plan is available (user-specified or auto-detected). Plan compliance is a rigorous evaluation, not a passive checklist. Scrutinize the implementation against the plan's intent, not just its task list.

#### 4a. Find the Plan

If the user specified `--plan <path>`, use that file. Otherwise, auto-detect:

1. Look for plan directories commonly used in projects:

```bash
# Check common plan directory locations
ls docs/plans/todo/ 2> /dev/null
ls docs/plans/in-progress/ 2> /dev/null
ls docs/plans/ 2> /dev/null
```

1. Search for plan files whose name matches the current branch name (with type prefixes and hyphens/underscores normalized). For example, branch `feature/add-dark-mode` would match a plan named `add-dark-mode.md`.

1. If exactly one plan matches, use it. If multiple plans match, list them and ask the user which to use. If no plans match, skip the plan evaluation entirely.

#### 4b. Parse the Plan

Read the plan document and extract every actionable item, preserving hierarchy (phase/section grouping). Plans may use:

- **Checkboxes**: `- [ ]` (incomplete) and `- [x]` (complete)
- **Numbered lists**: Sequential steps or phases
- **Headings as phases**: `## Phase 1`, `### Step 1`, etc.
- **Bullet points**: Unnumbered task lists

Also identify the plan's stated goals, constraints, design decisions, and any specified approaches or technologies. These contextual elements are as important as the task list items when evaluating compliance.

#### 4c. Match Work to Plan Items

For each plan item, determine its status based on the branch's changes:

- **Done**: The diff clearly and fully implements this item. Changes directly address the described work with no gaps.
- **Partially done**: Some related changes exist but the item is not fully implemented. Note specifically what is missing.
- **Not started**: No changes in the diff relate to this item.

**Be strict.** Only mark an item as "Done" when the implementation is thorough and complete. If an item asks for error handling and the code adds only the happy path, that is "Partially done," not "Done." If the plan says to add tests and there are no tests, it is "Not started" regardless of how complete the feature code is.

#### 4d. Identify Deviations

Look for discrepancies between the plan and the actual implementation:

- **Approach deviations**: The plan specified one approach but the implementation uses a different one (e.g., plan says "use a map" but code uses a slice; plan says "add a middleware" but code modifies the handler directly).
- **Scope additions**: Work done on the branch that the plan does not mention. This is not necessarily bad, but it must be called out explicitly. Was this extra work justified, or is it scope creep?
- **Scope omissions**: Plan items that appear to have been intentionally skipped, not just "not yet started." Look for evidence that the implementer chose to skip something.
- **Ordering violations**: If the plan specifies an order of operations and the implementation did things in a different sequence, note whether this matters.

#### 4e. Assess Implementation Fidelity

Go beyond "was it done?" to ask "was it done well relative to what the plan intended?"

For each item marked "Done" or "Partially done":

- Does the implementation match the spirit of the plan, or only the letter?
- If the plan described a specific design, does the code follow that design?
- If the plan mentioned quality expectations (e.g., "robust error handling," "comprehensive tests"), does the implementation meet those expectations?
- Are there shortcuts or simplifications that undermine the plan's intent?

#### 4f. Report Plan Compliance

Present a thorough compliance report:

1. **Compliance verdict**: A clear, direct assessment. Is the branch in good compliance with the plan, partial compliance, or poor compliance? Do not hedge. Be specific about why.
1. **Overall progress**: A fraction and percentage (e.g., "7/12 items done (58%)")
1. **Done items**: List each with a brief note about which changes implement it, and any caveats about implementation quality
1. **Partially done items**: List each with what has been done and what specifically remains
1. **Not started items**: List items not yet started
1. **Deviations**: List every deviation found in 4d, with an assessment of whether each deviation is reasonable or problematic
1. **Fidelity concerns**: List any concerns from 4e where the implementation does not match the plan's intent

If the plan uses phases or sections, preserve that grouping in the report.

### 5. Assess Code Quality

This step always runs, regardless of whether a plan exists. Evaluate the branch's changes on their own merits, independent of any plan. Read the diff critically, as a reviewer would.

#### 5a. Code Quality

Examine the diff for:

- **Readability**: Is the code clear and understandable? Are names descriptive? Is the logic easy to follow?
- **Maintainability**: Will this code be easy to modify in the future? Are there hard-coded values, magic numbers, or tightly coupled components that will cause problems later?
- **Patterns and consistency**: Does the new code follow the same patterns as the surrounding codebase? Are there inconsistencies in style, naming, or structure compared to the existing code?
- **Duplication**: Is there meaningful code duplication that should be addressed?

#### 5b. Potential Issues

Look actively for problems:

- **Bugs**: Logic errors, off-by-one errors, nil/null pointer risks, race conditions, resource leaks
- **Edge cases**: Unhandled boundary conditions, empty inputs, error paths
- **Error handling**: Are errors handled appropriately? Are there silent failures, swallowed errors, or overly broad catch blocks?
- **Security**: Input validation gaps, injection risks, authentication/authorization issues, secrets in code
- **Performance**: Obvious performance problems such as unnecessary allocations, N+1 queries, unbounded growth, or missing pagination

Do not invent hypothetical problems. Flag only issues that are visible in the diff or strongly implied by it.

#### 5c. Completeness

Assess whether the work on this branch feels finished:

- Are there TODO, FIXME, HACK, or XXX comments in the new code?
- Are there stub implementations, placeholder values, or commented-out code?
- If new features were added, are there corresponding tests?
- If APIs were changed, is documentation updated?
- Are there loose ends visible in the diff: partial implementations, unfinished refactors, half-migrated patterns?

#### 5d. Assessment Verdict

Provide a clear, direct overall assessment of the code quality. Do not just list observations: synthesize them into a verdict.

1. **Overall quality**: Is this code ready to merge, or does it need more work? Be direct.
1. **Strengths**: What is done well? Be specific.
1. **Issues to address**: What needs to be fixed or improved before merging? Prioritize by severity.
1. **Suggestions**: Optional improvements that are not blocking but would make the code better.

### 6. Output the Review

Structure the final output with clear sections:

```markdown
## Branch Review: <branch-name>

Base: <base-ref> (merge base: <merge-base-short-hash>)
Commits: <count>
Files changed: <count> (<added> added, <modified> modified, <deleted> deleted, <renamed> renamed)
Reviewed through: <head-short-hash>

### Summary

<high-level summary>

### Changes by Area

<grouped changes>

### File Inventory

<new/modified/deleted/renamed files>

### Notable Changes

<highlighted items>

### Plan Compliance

<plan evaluation, if applicable>

### Code Quality Assessment

<independent code evaluation>
```

Adjust section headers and content to fit what is actually present. Omit empty sections. The **Plan Compliance** and **Code Quality Assessment** sections are the most important outputs of this review: make them thorough, specific, and direct.

### 7. Save the Review

Save the review output to a file for future reference and use with the `address-review` skill. **Skip this step if `--no-save` was specified.**

#### 7a. Determine the Filename

Build the filename from today's date and the current branch name:

1. **Get today's date**:

```bash
date +%Y-%m-%d
```

1. **Get the branch name** (already available from step 2):

Use the branch name obtained from `git branch --show-current` in step 2. If in detached HEAD state, use `HEAD` as the branch name.

1. **Sanitize the branch name** for use as a filename:

- Replace `/` and any other characters that are unsafe in filenames (spaces, colons, backslashes) with `-`
- Collapse consecutive hyphens into a single hyphen
- Remove leading and trailing hyphens
- If the result is empty after these steps, fall back to `branch` as the name

The resulting filename format is `YYYY-MM-DD-sanitized-branch-name.md`. For example:

- Branch `feature/store-reviews` on 2026-03-08 produces `2026-03-08-feature-store-reviews.md`
- Branch `fix/auth-bug` on 2026-03-08 produces `2026-03-08-fix-auth-bug.md`
- Detached HEAD on 2026-03-08 produces `2026-03-08-HEAD.md`
- A branch that sanitizes to empty on 2026-03-08 produces `2026-03-08-branch.md`

#### 7b. Create the Directory

```bash
mkdir -p docs/reviews
```

#### 7c. Write the File

Use the **Write** tool to save the full review output (the same markdown content displayed in step 6) to `docs/reviews/<filename>`.

If a file with the same name already exists, overwrite it. A review of the same branch on the same day is a re-review, and the latest version should replace the earlier one.

#### 7d. Report the Saved Path

After saving, report the file path to the user:

```text
Review saved to docs/reviews/<filename>
```

Include a hint about the address-review skill:

```text
To address the items in this review, run: /address-review docs/reviews/<filename>
```

## Error Handling

- **No commits on this branch**: Report that the branch has no changes compared to the base and stop.
- **Invalid --since ref**: If the specified ref does not exist, report the error and suggest checking the ref name.
- **Plan file not found**: If `--plan <path>` points to a non-existent file, report the error and continue with the review without plan comparison.
- **No gh CLI**: Fall back to `git remote show origin` for base branch detection. The review does not require `gh`.
- **Detached HEAD**: Use `HEAD` as the branch name and note that the review is running in detached HEAD state.
- **Save failure**: If the review file cannot be written (e.g., read-only filesystem, permissions issue), report the error but do not fail the entire review. The terminal output is already complete.
- **Large diffs**: If the diff is extremely large (thousands of lines), focus the summary on the stat output and commit messages rather than reading the entire diff line by line. Note that the detailed diff was too large for full analysis.
