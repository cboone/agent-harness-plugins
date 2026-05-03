# Address Review

Parse a review document for actionable feedback items, work through them systematically, and track resolution progress.

**Type:** Skill
**Trigger:** `/address-review <path>`

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Extracts items from checkboxes, bullets, numbered lists, and headings in a review document. Categorizes each item by type (code change, documentation, question, style), presents a summary for confirmation, then resolves items one by one. Commits fixes in logical groups by default, or per-item on request.

## Usage

```text
/address-review docs/reviews/my-review.md
/address-review docs/reviews/my-review.md --dry-run
/address-review docs/reviews/my-review.md --commit-per-item
/address-review docs/reviews/my-review.md --skip 2,5,8
```

| Option              | Description                                              |
| ------------------- | -------------------------------------------------------- |
| `--dry-run`         | Parse and list items without making changes              |
| `--commit-per-item` | Commit after each item instead of grouping related fixes |
| `--skip <numbers>`  | Skip specific item numbers (comma-separated)             |

## Examples

- "address review @docs/reviews/pr-feedback.md": works through all items
- "address the review --dry-run": previews items without making changes

## See Also

- [Resolve Copilot PR Feedback](../resolve-copilot-pr-feedback/README.md): resolve automated Copilot review comments
- [All plugins](../../../../README.md)
