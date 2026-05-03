# Update Review

Find the latest branch review, assess commits made since, and update the review document in place with a synthesized reassessment.

**Type:** Skill
**Trigger:** `/update-review`

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Finds the most recent review for the current branch in `docs/reviews/`, identifies commits made since that review was written, and produces an updated review that synthesizes the original assessment with a reassessment of the new work. Overwrites the review file in place, preserving the original date prefix.

Plan compliance is recalculated from scratch to capture progress. Code quality assessment highlights what changed since the last review, noting which prior issues were addressed, any new issues, and the overall quality trajectory.

## Usage

```text
/update-review
/update-review --review docs/reviews/2026-03-08-feature-my-branch.md
/update-review --plan docs/plans/my-plan.md
/update-review --brief
```

| Option            | Description                                                 |
| ----------------- | ----------------------------------------------------------- |
| `--review <path>` | Path to a specific review document to update                |
| `--plan <path>`   | Compare progress against a plan document                    |
| `--brief`         | Output only a high-level summary without detailed breakdown |

## Examples

- "update review": finds and updates the latest review for this branch
- "refresh the review": same as above
- "update the review --plan docs/plans/my-plan.md": updates with plan compliance
- "re-review the branch": updates the existing review with new commits

## See Also

- [Review Branch](../review-branch/README.md): create an initial branch review
- [Address Review](../address-review/README.md): work through review feedback items
- [All plugins](../../../../README.md)
