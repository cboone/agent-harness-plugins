---
name: write-markdown
description: >-
  Applies Markdown style conventions when creating or editing Markdown files.
---

# Markdown Style Guide

Apply the Markdown conventions from `./references/MARKDOWN.md` when creating or editing Markdown files. This guide targets GitHub Flavored Markdown (GFM) and aligns with markdownlint-cli2 rules.

## Common Mistakes

These two issues cause the most lint failures. Check every Markdown file for them.

### Tables: align all pipes vertically

```markdown
<!-- Correct: pipes aligned, cells padded -->

| Name    | Type   | Default |
| ------- | ------ | ------- |
| timeout | number | 30      |
| retries | number | 3       |
```

```markdown
<!-- Wrong: ragged pipes, no padding -->

| Name    | Type   | Default |
| ------- | ------ | ------- |
| timeout | number | 30      |
| retries | number | 3       |
```

Procedure: write all rows, find the longest content per column, pad every cell to that width, fill delimiter hyphens to match, then verify all pipes line up.

### Code blocks: always include a language identifier

````markdown
<!-- Correct -->

```bash
echo "hello"
```
````

````markdown
<!-- Wrong: bare fence -->

```
echo "hello"
```
````

Use `text` when no syntax highlighting applies. Never leave the opening fence bare.

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

- Consistent markers: `-` for unordered (MD004); for ordered lists, use either `1.` for every item or sequential numbering (`1.`, `2.`, `3.`), but be consistent within each list (MD029)
- Indent nested lists consistently
- Blank line before and after a list block (MD032)

### Tables

- Pad every cell so all pipe characters align vertically; pad delimiter hyphens to match (MD060)
- Leading and trailing pipes on every row (MD055)
- Consistent column count across all rows (MD056)

### Code

- Fenced code blocks must have a language identifier, use `text` if none applies (MD040)
- Backtick fences, not tilde fences (MD048)
- Inline code for identifiers, commands, and short expressions

### HTML

- Prefer Markdown syntax when an equivalent exists
- HTML is acceptable for features Markdown lacks (`<details>`, `<kbd>`, `<br>`, `<sub>`, `<sup>`, etc.)

## Validation

After creating or editing Markdown files, run the project's lint-fix command to auto-correct table alignment, list numbering, and other formatting issues. This is a required final step, not optional.

Check `package.json` for project-specific scripts (e.g., `yarn lint:fix`, `yarn lint:md:fix`, `npm run lint:fix`). Also check `Makefile` targets and scripts in `bin/`. Run the linter in fix mode so it corrects what it can automatically.

If no project-specific lint script is available, use `markdownlint-cli2` directly as a fallback.
