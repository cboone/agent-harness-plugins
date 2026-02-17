---
name: write-markdown
description: >-
  Applies Markdown style conventions when creating or editing Markdown files.
  Use when: (1) creating new Markdown files, (2) editing existing .md files,
  or (3) reviewing Markdown for style and formatting issues.
---

# Markdown Style Guide

Apply the Markdown conventions from `./references/MARKDOWN.md` when creating or editing Markdown files.

## Key Conventions

Read `./references/MARKDOWN.md` for the complete guide. Summary:

### Document Structure

- One top-level heading (`# Title`) per document
- Blank line before and after headings, lists, code blocks, and block quotes
- End files with a single trailing newline

### Headings

- ATX-style headings (`#`) only, never Setext (underlines)
- Do not skip heading levels (e.g., `##` to `####`)
- No trailing punctuation on headings

### Links and Images

- Inline links for one-off references: `[text](url)`
- Reference links for repeated URLs or long URLs: `[text][id]`
- Always include alt text on images

### Lists

- Consistent markers: `-` for unordered, `1.` for all ordered items
- Indent nested lists by 2 or 4 spaces, consistently
- Blank line before and after a list block

### Code

- Fenced code blocks with language identifier: ` ```js `
- Inline code for identifiers, commands, and short expressions

### Line Length

- Wrap prose at a reasonable length (80-100 characters) when the project enforces it
- One sentence per line is an acceptable alternative in version-controlled documents

## Validation

Whenever possible, validate Markdown before finishing. Prefer using a project-specific validation script, if available. Common locations include declarations in `package.json` and scripts stored in `bin/`. If those are not present, `markdownlint` is a commonly available linter for Markdown files.
