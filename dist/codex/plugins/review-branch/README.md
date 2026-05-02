# Review Branch

Review and evaluate all work done on the current branch compared to the base branch.

**Type:** Skill
**Trigger:** `/review-branch`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Review Branch** from the available plugins.

## What It Does

Summarizes changes by area/concern, lists new/modified/deleted files, and highlights notable changes. By default, saves the review to `docs/reviews/` with a datestamp-prefixed filename (e.g., `2026-03-08-feature-store-reviews.md`) for use with the [Address Review](../address-review/README.md) skill (saving can be skipped with `--no-save`). Then goes further with two evaluations:

- **Plan compliance**: When a plan document is available (auto-detected or specified), rigorously evaluates whether the implementation matches the plan's intent. Checks for deviations, scope additions and omissions, and assesses implementation fidelity, not just task completion.
- **Code quality assessment**: Always runs, regardless of whether a plan exists. Examines the diff for readability, maintainability, potential bugs, edge cases, error handling, security issues, and completeness. Delivers a direct verdict on merge readiness.

## Usage

```text
/review-branch
/review-branch --plan docs/plans/my-plan.md
/review-branch --since v1.2.0
/review-branch --brief
/review-branch --no-save
```

| Option          | Description                                       |
| --------------- | ------------------------------------------------- |
| `--plan <path>` | Compare progress against a plan document          |
| `--since <ref>` | Use a specific tag, branch, or commit as the base |
| `--brief`       | Output only a high-level summary                  |
| `--no-save`     | Skip saving the review to `docs/reviews/`         |

## Examples

- "review branch": full summary of all changes
- "where are we on this branch": same as above
- "compare branch to plan": auto-detects a matching plan file

## See Also

- [Address Review](../address-review/README.md): work through review feedback items
- [PR](../pr/README.md): create a pull request after reviewing
- [All plugins](../../../../README.md)
