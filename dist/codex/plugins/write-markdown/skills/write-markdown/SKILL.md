---
name: write-markdown
description: >-
  Applies Markdown style conventions when creating or editing Markdown files.
---

# Markdown Style Guide

Apply the Markdown conventions from `./references/MARKDOWN.md` when creating or editing Markdown files. This guide targets GitHub Flavored Markdown (GFM) and aligns with markdownlint-cli2 rules.

## Common Mistakes

These two issues cause the most formatting churn and lint failures. Check every Markdown file for them.

### Tables: aligned pipes, from Prettier where it runs

A committed table has every pipe aligned, every cell padded to its column width, and delimiter hyphens filled to match. Who does the padding depends on the project.

```markdown
<!-- Committed form: pipes aligned, cells padded -->

| Name    | Type   | Default |
| ------- | ------ | ------- |
| timeout | number | 30      |
| retries | number | 3       |
```

```markdown
<!-- Ragged: fine as a draft only where Prettier will format it -->

| Name | Type | Default |
| --- | --- | --- |
| timeout | number | 30 |
| retries | number | 3 |
```

**Prettier formats Markdown here:** Prettier owns alignment. Write rows without padding, including rows added to an existing table, and run the project's format command (`yarn format`, `yarn lint:fix`, `make format`, or its equivalent). Do not hand-pad cells, and do not cite MD060 as the reason for alignment: projects that run Prettier typically disable it. Prettier formats Markdown when the project has a Prettier config (`.prettierrc*`, `prettier.config.*`, or a `prettier` key in `package.json`) or a format script that runs Prettier, and `.prettierignore` does not exclude the file.

**No Prettier:** nothing else aligns tables, so align them by hand, and do it before running `markdownlint-cli2 --fix`. MD060 has no fix toward the aligned style, and at its default settings it can compact a table that picked up a few unpadded rows, stripping the padding from the rows that were aligned. Procedure: write all rows, find the longest content per column, pad every cell to that width, fill delimiter hyphens to match, then verify all pipes line up.

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

- Align every pipe vertically and pad delimiter hyphens to match; where Prettier formats Markdown its format command does this, and elsewhere it is done by hand because markdownlint cannot
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

After creating or editing Markdown files, run the project's lint-fix and format commands to correct list numbering, spacing, and other formatting issues. This is a required final step, not optional.

Check `package.json` for project-specific scripts (e.g., `yarn lint:fix`, `yarn lint:md:fix`, `yarn format`, `npm run lint:fix`). Also check `Makefile` targets and scripts in `bin/`. Choose the order for each file using the Prettier detection above:

- **Prettier formats the file:** Run the linter in fix mode first and Prettier last, so Prettier has the final say on layout. Use the project's lint-fix and format commands when available. If either command is missing, invoke the corresponding installed tool directly: `markdownlint-cli2 --fix` for lint fixes, then `prettier --write` for formatting, passing the edited file paths. Prettier aligns the tables; no manual padding is needed, including when there is no project-specific lint script.
- **Prettier does not format the file:** Align tables by hand before running any command that invokes markdownlint's fix mode, including project-specific lint-fix scripts. Then run the project's lint-fix command, or invoke `markdownlint-cli2 --fix` directly on the edited files if no such command exists.
