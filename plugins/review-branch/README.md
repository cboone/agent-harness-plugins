# Review Branch

Review and evaluate all work done on the current branch: summarize changes, assess plan compliance, and evaluate code quality.

**Type:** Skill
**Trigger:** `/review-branch`

## Installation

See the [marketplace install instructions](../../README.md#install).

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

## Recommended Permissions

This skill runs git and GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(git branch *)", "Bash(git diff*)", "Bash(git log *)", "Bash(git merge-base *)", "Bash(git rev-parse *)", "Bash(gh repo view *)", "Bash(mkdir -p docs/reviews)"]
  }
}
```

## See Also

- [Address Review](../address-review/README.md): work through review feedback items
- [PR](../pr/README.md): create a pull request after reviewing
- [All plugins](../../README.md)
