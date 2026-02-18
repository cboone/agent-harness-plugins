# Review Branch

Summarize all work done on the current branch compared to the base branch.

**Type:** Skill
**Trigger:** `/review-branch`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Review Branch** from the available plugins.

## What It Does

Groups changes by area/concern, lists new/modified/deleted files, and highlights notable changes (new dependencies, config changes, schema changes, API changes). Optionally compares progress against a plan document, reporting completed, in-progress, and remaining items with a completion percentage.

## Usage

```text
/review-branch
/review-branch --plan docs/plans/my-plan.md
/review-branch --since v1.2.0
/review-branch --brief
```

| Option          | Description                                       |
| --------------- | ------------------------------------------------- |
| `--plan <path>` | Compare progress against a plan document          |
| `--since <ref>` | Use a specific tag, branch, or commit as the base |
| `--brief`       | Output only a high-level summary                  |

## Examples

- "review branch": full summary of all changes
- "where are we on this branch": same as above
- "compare branch to plan": auto-detects a matching plan file

## See Also

- [PR](../pr/README.md): create a pull request after reviewing
- [All plugins](../../README.md)
