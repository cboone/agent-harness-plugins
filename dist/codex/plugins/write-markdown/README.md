# Write Markdown

Markdown style conventions targeting GitHub Flavored Markdown (GFM), aligned with markdownlint-cli2 rules.

**Type:** Skill
**Trigger:** `/write-markdown` (also activates automatically)

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Provides Markdown formatting conventions for document structure, headings, links, lists, tables, code blocks, and HTML usage. Activates automatically when creating, editing, or reviewing Markdown files, ensuring consistent formatting across the project.

Includes a reference guide covering all conventions with markdownlint rule identifiers.

## Usage

```text
/write-markdown
```

The skill also activates automatically when Claude Code detects Markdown file work.

## Examples

- Creating a new `.md` file: the style guide activates automatically
- "review this Markdown for formatting": activates automatically
- "/write-markdown": loads the full style guide explicitly

## See Also

- [Lint and Fix](../lint-and-fix/README.md): run markdownlint and other formatters
- [All plugins](../../../../README.md)
