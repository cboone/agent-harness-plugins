---
name: address-review
description: >-
  Work through the actionable items in a review document and track their
  resolution. Use for "address the review" or "address @docs/reviews/...".
argument-hint: "<review-path> [--dry-run] [--skip <numbers>] [--commit-per-item]"
---

# Address Review

Parse a review document, extract actionable items, and work through them systematically.

## Options

The user may provide these options inline:

- **--dry-run**: Parse and list items without making changes
- **--skip \<numbers>**: Skip specific item numbers (comma-separated, e.g., `--skip 2,5,8`)
- **--commit-per-item**: Commit after each item instead of grouping related fixes

## Capabilities and authority

Use the tools this session actually offers. For a question, use a structured question tool when available in the active mode; otherwise present numbered choices and wait. In a noninteractive run, report the unresolved question and preserved state instead of choosing an answer. Tool names such as Write, Read, Glob and AskUserQuestion below are examples: perform the same file or question operation with the host's supported mechanism. Write a body file completely before issuing the command that reads it; never batch those dependent operations.

Prior user authorization carries through the workflow; add no confirmation merely because the harness differs. Host approvals, active Plan or read-only mode, writable roots and network policy still apply. Stop before a prohibited write or any step dependent on a blocked operation, preserve state, and report the exact command and restriction. Never bypass controls or claim an unrun step completed. Separate completed, skipped, blocked and failed work in the result. For invocation hints, render the named skill with the running harness's form: slash invocation in Claude Code, dollar mention or the skills selector in Codex. A mention is not a tool call; load composed skills from their advertised locations.

## Parent Continuation Contract

Honor a supplied parent continuation block and its resume target. On success, return control to the parent without asking whether to continue. When a decision has no supplied answer, do not ask independently or guess: return `Status: needs-decision`, the question, available choices and preserved state. The parent asks or stops, then invokes this skill with an answer. For an in-progress merge or rebase, list conflicts and the applicable abort command; do not abort or discard work merely to return a result.

Return `Status: <success|no-op|failure|unavailable|needs-decision>`, `Outputs`, `Unresolved or skipped` and `Caller resume target`. A no-op is successful only when no required work was skipped. Preserve any domain-specific status lines below. A host block or failed required check is failure, a missing required skill is unavailable, and unresolved choices are needs-decision. Standalone invocations retain their existing questions and reporting.

## Workflow

### 1. Identify the Review Document

The user provides a path to a review document, typically as an `@`-reference or a file path argument. `docs/reviews/` is the canonical location, and it is where the `review-branch` skill saves its output. Older projects may keep them in `docs/plans/reviews/`; any markdown file the user references works too.

Read the file. If the path does not exist, report that and stop.

### 2. Parse Actionable Items

Extract every actionable item from the review document. Items may appear as:

- **Checkboxes**: `- [ ] Fix the error handling in auth.go`
- **Unchecked bullets**: `- Fix the error handling in auth.go`
- **Numbered lists**: `1. Fix the error handling in auth.go`
- **Headings followed by description**: A heading that names an issue, with explanatory text below
- **Inline code references**: Items that reference specific files, functions, or line numbers

For each extracted item, record:

| Field          | Description                                               |
| -------------- | --------------------------------------------------------- |
| **Number**     | Sequential index (1, 2, 3, ...)                           |
| **Summary**    | One-line description of the item                          |
| **Type**       | `code-change`, `documentation`, `question`, or `style`    |
| **File hints** | Any file paths, function names, or line numbers mentioned |
| **Context**    | The full original text from the review document           |

**Type classification rules:**

- **code-change**: Mentions fixing, adding, removing, or refactoring code; references specific files or functions
- **documentation**: Mentions README, docs, comments, docstrings, or documentation files
- **question**: Phrased as a question or asks for clarification; contains "should we", "consider whether", "why", etc.
- **style**: Mentions formatting, naming, whitespace, linting, or cosmetic changes

When in doubt, classify as `code-change`.

### 3. Present the Item List

Display a numbered summary of all extracted items:

```text
## Review Items (N total)

| # | Type | Summary | File hints |
|---|------|---------|------------|
| 1 | code-change | Fix error handling in auth.go | auth.go:42 |
| 2 | documentation | Update README install section | README.md |
| 3 | question | Should we support Windows paths? | - |
| 4 | style | Rename helper to follow convention | utils/helper.go |
```

**If `--dry-run` was specified**: Stop here after displaying the table. Do not make any changes.

Ask the user to confirm the list. The user may:

- **Confirm**: Proceed with all items
- **Skip items**: Specify item numbers to skip (e.g., "skip 3 and 5")
- **Reorder**: Specify a preferred order (e.g., "do 4 first, then 1, 2")

Merge any `--skip` numbers from the command line with any skips the user specifies interactively.

### 4. Work Through Items Systematically

Process each item in order (or user-specified order). For each item:

#### 4a. Announce the Item

```text
### Addressing item N of M: <summary>
Type: <type> | Files: <file hints>
```

#### 4b. Locate the Relevant Code

Use the file hints from the review item to find the relevant code:

1. If the item references specific files or line numbers, read those files directly
1. If the item references function or variable names, search the codebase for them
1. If the item is vague, search for keywords from the item's context

#### 4c. Make the Changes

- For **code-change** items: Edit the relevant files to address the feedback
- For **documentation** items: Update the referenced documentation
- For **style** items: Apply the formatting or naming changes
- For **question** items: Research the answer, then either:
  - Make a change if the answer is clear and actionable
  - Flag it for the user with your findings and recommendation, then move on

#### 4d. Mark the Item as Resolved

After addressing an item, report:

```text
Item N: Resolved - <brief description of what was done>
```

If the item cannot be resolved (ambiguous, requires external input, or references code that does not exist):

```text
Item N: Skipped - <reason>
```

#### 4e. Commit If Applicable

**If `--commit-per-item` was specified**: Commit the changes for this item immediately before moving to the next. Use a conventional commit message referencing the review:

```text
fix: <description of the change>
```

### 5. Commit in Logical Groups

**If `--commit-per-item` was NOT specified** (the default behavior):

After all items are addressed, group the changes into the smallest logical commits that are appropriate. Each commit should represent a single coherent change:

1. **Group by relatedness**: Changes to the same file or feature area go together
1. **Separate concerns**: Code changes, documentation updates, and style fixes get separate commits when they are independent
1. **Keep commits atomic**: Each commit should be a self-contained, reviewable unit
1. **Prefer smaller over larger**: When in doubt, split into more commits rather than fewer. A bug fix mixed with an unrelated refactor should be two commits, not one

For each commit group, generate a conventional commit message:

```text
fix: address review feedback for <area>

Resolves items N, M from <review-file-name>.
```

### 6. Report Completion

After all items are processed, display a summary:

```text
## Review Resolution Summary

**Source**: <review file path>
**Total items**: N
**Resolved**: X
**Skipped**: Y

| # | Type | Summary | Status | Commit |
|---|------|---------|--------|--------|
| 1 | code-change | Fix error handling in auth.go | Resolved | abc1234 |
| 2 | documentation | Update README install section | Resolved | def5678 |
| 3 | question | Should we support Windows paths? | Skipped (needs discussion) | - |
| 4 | style | Rename helper to follow convention | Resolved | abc1234 |
```

If any items were skipped, list them with explanations at the end:

```text
### Items Needing Discussion

- **#3**: Should we support Windows paths? - This is an open design question.
  Recommendation: <your recommendation based on codebase analysis>
```

## Review Document Format

This skill handles various markdown formats commonly used in review documents. The expected structure is flexible, but works best with:

```markdown
# Review: <title>

## Section Name (optional)

- [ ] First actionable item
- [ ] Second actionable item with reference to `src/file.go:42`
- A bullet without checkbox is also treated as actionable
- [x] Already-completed items are skipped

### Subsection (optional)

1. Numbered items work too
2. Another numbered item

> Quoted text is treated as context, not as an actionable item

General prose paragraphs are treated as context for the items that follow them,
not as actionable items themselves.
```

**Skipped patterns** (not treated as actionable items):

- Already-checked checkboxes: `- [x] Done item`
- Block quotes: `> This is context`
- Prose paragraphs without list markers or headings
- Code blocks (treated as context for adjacent items)
- Metadata lines (dates, authors, labels)

## Error Handling

- **File not found**: Report that the review document does not exist and stop
- **No actionable items**: Report that no items were found, show what was parsed, and suggest the document may not follow a recognizable format
- **Ambiguous items**: Flag them for the user rather than guessing
- **File referenced in item does not exist**: Skip the item with an explanation
- **Merge conflicts during commits**: Stop and report the conflict; do not force through
