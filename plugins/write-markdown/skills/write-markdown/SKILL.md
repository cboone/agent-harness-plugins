---
name: write-markdown
description: >-
  Applies Markdown style conventions when creating or editing Markdown files.
  Use when: (1) creating new Markdown files, (2) editing existing .md files,
  or (3) reviewing Markdown for style and formatting issues.
---

# Markdown Style Guide

Apply the Markdown conventions from `./references/MARKDOWN.md` when creating or editing Markdown files. This guide targets GitHub Flavored Markdown (GFM) and aligns with markdownlint-cli2 rules.

## Key Conventions

Read `./references/MARKDOWN.md` for the complete guide. Summary:

### Document Structure

- One top-level heading (`# Title`) per document (MD025)
- Blank line before and after headings, lists, code blocks, and block quotes
- End files with a single trailing newline (MD047)

### Headings

- ATX-style headings (`#`) only, never Setext underlines (MD003)
- Do not skip heading levels (MD001)
- No trailing punctuation on headings (MD026)
- Sibling headings must be unique; same text is fine under different parents (MD024)

### Links and Images

- Inline links for one-off references: `[text](url)`
- Reference links for repeated URLs or long URLs: `[text][id]`
- Always include alt text on images (MD045)

### Lists

- Consistent markers: `-` for unordered (MD004), `1.` for all ordered items (MD029)
- Indent nested lists consistently
- Blank line before and after a list block (MD032)

### Tables

- Pad cells so pipe characters align vertically across all rows (MD060)
- Leading and trailing pipes on every row (MD055)
- Consistent column count across all rows (MD056)

### Code

- Fenced code blocks with language identifier: ` ```js ` (MD040)
- Backtick fences, not tilde fences (MD048)
- Inline code for identifiers, commands, and short expressions

### HTML

- Prefer Markdown syntax when an equivalent exists
- HTML is acceptable for features Markdown lacks (`<details>`, `<kbd>`, `<br>`, `<sub>`, `<sup>`, etc.)

## Validation

Whenever possible, validate Markdown before finishing. Prefer using a project-specific validation script, if available. Common locations include declarations in `package.json` and scripts stored in `bin/`. If those are not present, `markdownlint-cli2` is a commonly available linter for Markdown files.
