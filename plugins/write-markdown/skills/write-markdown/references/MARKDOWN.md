# Markdown Style Guide

[Document structure](#document-structure) · [Headings](#headings) · [Paragraphs](#paragraphs) · [Emphasis](#emphasis) · [Links](#links) · [Images](#images) · [Lists](#lists) · [Code](#code) · [Block quotes](#block-quotes) · [Tables](#tables) · [Horizontal rules](#horizontal-rules) · [HTML](#html) · [Whitespace](#whitespace) · [File naming](#file-naming) · [Accessibility](#accessibility)

This guide targets GitHub Flavored Markdown (GFM) and aligns with markdownlint-cli2 rules. Rule IDs (MD001, MD003, etc.) are noted for cross-reference with markdownlint configuration.

---

## Document structure

### Single top-level heading (MD025)

Use exactly one `#` heading per document. It serves as the document title.

```markdown
<!-- Use -->

# Project README

## Installation

## Usage
```

```markdown
<!-- Avoid: multiple top-level headings -->

# Project README

# Installation

# Usage
```

When using YAML front matter with a `title` field (e.g., in Hugo or Jekyll), the front matter title can satisfy this rule. Configure MD041 with `front_matter_title` accordingly.

---

### Front matter

When using YAML front matter, place it at the very top of the file before any content.

```markdown
---
title: My Document
date: 2025-01-15
---

# My Document
```

---

### Trailing newline (MD047)

End every file with exactly one newline character. Most editors and linters enforce this.

---

## Headings

### ATX-style headings (MD003)

Use ATX-style (`#`) headings. Never use Setext-style (underline) headings.

| Use          | Avoid                  |
| ------------ | ---------------------- |
| `# Heading`  | `Heading`<br>`=======` |
| `## Heading` | `Heading`<br>`-------` |

---

### Heading spacing (MD018, MD019)

Include exactly one space after the `#` characters.

| Use          | Avoid       |
| ------------ | ----------- |
| `## Heading` | `##Heading` |

---

### Blank lines around headings (MD022)

Add a blank line before and after every heading.

```markdown
<!-- Use -->

Some paragraph text.

## Next Section

More text here.
```

```markdown
<!-- Avoid -->

Some paragraph text.

## Next Section

More text here.
```

---

### Do not skip heading levels (MD001)

Heading levels should increment by one. Do not skip from `##` to `####`.

| Use                         | Avoid            |
| --------------------------- | ---------------- |
| `##` then `###` then `####` | `##` then `####` |

---

### No trailing punctuation (MD026)

Do not end headings with periods or colons. Question marks and exclamation marks are acceptable when they are part of the heading's meaning.

| Use                | Avoid              |
| ------------------ | ------------------ |
| `## Installation`  | `## Installation.` |
| `## Installation`  | `## Installation:` |
| `## Why Markdown?` | (acceptable)       |

---

### No inline code as full headings

Do not make an entire heading inline code. Use inline code only for identifiers within headings.

| Use                        | Avoid             |
| -------------------------- | ----------------- |
| `## The \`config\` object` | `` ## `config` `` |

---

### Sibling heading uniqueness (MD024)

Headings should be unique among their siblings (headings at the same level under the same parent). The same heading text may appear in different sections.

```markdown
<!-- Acceptable: same heading text under different parents -->

## Setup

### Prerequisites

## Deployment

### Prerequisites
```

```markdown
<!-- Avoid: duplicate siblings under the same parent -->

## Setup

### Step One

### Step One
```

---

## Paragraphs

### Blank lines between paragraphs

Separate paragraphs with a single blank line.

```markdown
<!-- Use -->

First paragraph.

Second paragraph.
```

```markdown
<!-- Avoid -->

First paragraph.
Second paragraph.
```

---

### No indented paragraphs (MD023)

Do not indent the first line of a paragraph. Indented text can be interpreted as a code block.

| Use             | Avoid            |
| --------------- | ---------------- |
| `Regular text.` | `Indented text.` |

---

## Emphasis

### Bold and italic markers (MD049, MD050)

Use `**` for bold and `_` for italic. This convention avoids ambiguity with `*` and `__`.

| Use             | Avoid           |
| --------------- | --------------- |
| `**bold text**` | `__bold text__` |
| `_italic text_` | `*italic text*` |

---

### No emphasis in headings (MD036)

Avoid emphasis markers inside headings. The heading level already provides visual distinction. Do not use bold text as a substitute for headings.

| Use           | Avoid             |
| ------------- | ----------------- |
| `## Overview` | `## **Overview**` |

---

### No empty emphasis (MD037)

Do not use emphasis markers around whitespace or empty strings.

| Use    | Avoid   |
| ------ | ------- |
| (omit) | `** **` |
| (omit) | `____`  |

---

## Links

### Inline links

Use inline links for one-off references.

```markdown
See the [installation guide](https://example.com/install) for details.
```

---

### Reference links

Use reference-style links when the same URL appears multiple times or when the URL is long enough to hurt readability.

```markdown
Read the [contributing guide][contributing] before opening a PR.
See the [contributing guide][contributing] for branch naming.

[contributing]: https://example.com/contributing
```

---

### Reference link placement

Place reference link definitions at the end of the document or at the end of the section where they are used.

---

### Defined reference links (MD052, MD053)

Every reference link must have a corresponding definition, and every definition should be used. Unused definitions are dead weight; undefined references break links silently.

---

### Meaningful link text

Use descriptive link text. Avoid "click here", "here", "this", or bare URLs as link text.

| Use                                          | Avoid                                     |
| -------------------------------------------- | ----------------------------------------- |
| `See the [installation guide](url).`         | `Click [here](url) to install.`           |
| `Read the [API reference](url) for details.` | `Details: [https://example.com/api](url)` |

---

### No empty links (MD042)

Every link must have both a URL and link text.

---

## Images

### Alt text (MD045)

Always include descriptive alt text for images.

| Use                                    | Avoid                |
| -------------------------------------- | -------------------- |
| `![Diagram of auth flow](auth.png)`    | `![](auth.png)`      |
| `![Screenshot of dashboard](dash.png)` | `![image](dash.png)` |

---

### Image links

To make an image clickable, wrap the image syntax in a link.

```markdown
[![Project logo](logo.png)](https://example.com)
```

---

## Lists

### Unordered list markers (MD004)

Use `-` (hyphen) for unordered list items. Be consistent throughout the document.

| Use      | Avoid    |
| -------- | -------- |
| `- Item` | `* Item` |
| `- Item` | `+ Item` |

---

### Ordered list numbering (MD029)

Either numbering style is acceptable for ordered lists: repeating `1.` for every item, or sequential numbering (`1.`, `2.`, `3.`). Be consistent within each list.

```markdown
<!-- Both are acceptable -->

1. First item
1. Second item
1. Third item

1. First item
2. Second item
3. Third item
```

Do not mix styles within a single list.

---

### List indentation (MD005, MD007)

Indent nested lists consistently, using the same number of spaces throughout the document (2 or 4 spaces).

```markdown
- Top level
  - Nested item
    - Deeply nested
```

---

### Blank lines around lists (MD032)

Add a blank line before and after a list block.

```markdown
<!-- Use -->

Introductory text.

- First item
- Second item

Following paragraph.
```

```markdown
<!-- Avoid -->

Introductory text.

- First item
- Second item
  Following paragraph.
```

---

### Blank lines in loose lists

When list items contain multiple paragraphs or complex content, add blank lines between items (loose list style).

```markdown
- First item with a longer explanation.

  Continuation of the first item.

- Second item with its own explanation.
```

---

### Task lists

Use `- [ ]` and `- [x]` for task lists. Keep a space inside the brackets for unchecked items. This is a GFM extension.

```markdown
- [x] Write the introduction
- [ ] Add code examples
- [ ] Review and publish
```

---

## Code

### Inline code (MD038)

Use backticks for inline code: commands, function names, variable names, file paths, and short expressions. Do not pad with spaces inside the backticks.

| Use                     | Avoid               |
| ----------------------- | ------------------- |
| `Run \`npm install\``   | `Run "npm install"` |
| `The \`config\` object` | `The config object` |

---

### Fenced code blocks (MD046, MD031)

Use triple-backtick fenced code blocks, not indented code blocks. Surround them with blank lines. Always specify a language identifier.

````markdown
<!-- Use -->

```python
def hello():
    print("Hello, world!")
```
````

```markdown
<!-- Avoid: indented code block, no language -->

    def hello():
        print("Hello, world!")
```

---

### Language identifiers (MD040)

Every fenced code block must include a language identifier. Never leave the opening fence bare.

| Use               | Avoid   |
| ----------------- | ------- |
| ` ```javascript ` | ` ``` ` |
| ` ```bash `       | ` ``` ` |
| ` ```text `       | ` ``` ` |

Use `text` when no syntax highlighting applies.

Common language identifiers: `bash`, `console`, `css`, `diff`, `go`, `html`, `javascript`, `json`, `jsonc`, `markdown`, `python`, `text`, `toml`, `typescript`, `yaml`.

---

### Code fence style (MD048)

Use backtick fences (` ``` `), not tilde fences (`~~~`). Be consistent throughout the document.

---

### Code block context

When showing terminal commands, distinguish between the command and its output. Use `bash` or `console` for commands and consider separating output into its own block.

````markdown
```bash
npm test
```

```text
All tests passed.
```
````

---

## Block quotes

### Block quote markers (MD027)

Use `>` followed by a single space for block quotes.

```markdown
> This is a block quote.
> It can span multiple lines.
```

---

### Blank lines around block quotes

Add a blank line before and after block quotes.

---

### Nested block quotes

Nest block quotes with additional `>` markers. Limit nesting depth to maintain readability.

```markdown
> First level.
>
> > Nested quote.
```

---

## Tables

### Table syntax (MD055, MD056, MD058)

Use pipes and hyphens for tables. Surround tables with blank lines. Ensure consistent column counts across rows.

```markdown
| Name    | Type   | Default |
| ------- | ------ | ------- |
| timeout | number | 30      |
| retries | number | 3       |
```

---

### Table column alignment

Committed tables are aligned: pipe characters line up vertically across all rows, each cell is padded to the width of its column's longest content, and the delimiter row's hyphens fill the column width. This is Prettier's table formatting, and it is also the layout markdownlint's MD060 rule accepts as its `aligned` style.

```markdown
<!-- Committed form: aligned columns -->

| Name    | Type   | Default |
| ------- | ------ | ------- |
| timeout | number | 30      |
| retries | number | 3       |
```

```markdown
<!-- Ragged: a draft Prettier will align, not a committed form -->

| Name | Type | Default |
| --- | --- | --- |
| timeout | number | 30 |
| retries | number | 3 |
```

Determine ownership for each edited file. Verify that Prettier is available as a project dependency or a global tool. Its settings may live in `.prettierrc*`, `prettier.config.*`, or a `prettier` key in `package.json`; config presence alone does not prove that formatting runs. If project format commands exist, inspect their paths, globs, working directory, and options: a command restricted to JavaScript or other non-Markdown files does not own Markdown alignment. If no format command exists, configured and available Prettier can format the file directly through the project's package manager. In either case, honor the chosen command's effective ignore files: `.gitignore` and `.prettierignore` by default, or the files specified by `--ignore-path`.

**Where Prettier formats the file, Prettier owns alignment.** Write rows without padding and let Prettier align them. Appending a row with longer content re-pads the entire column, and Prettier does that in one pass, so do not pad by hand. Projects in this position typically set `MD060: false`: markdownlint has no fix toward the aligned style, and its default `any` style reports, and fixes, against whichever style the table most closely matches. Do not cite MD060 as the reason a table is aligned. If MD060 is enabled or its setting is unknown, run Prettier on the edited files before any lint-fix script so an alignment error cannot stop a chained formatter step. Then run lint fixes and finish with Prettier. With MD060 disabled, only the final Prettier pass is needed. Use project scripts when available and a package-manager runner such as `npm exec --`, `yarn exec`, `pnpm exec`, or `bun run` for installed CLI tools when a script is missing; a required initial formatter pass must run Prettier without a preceding linter.

**Where Prettier does not format the file, align tables by hand.** This includes files excluded from an otherwise configured Prettier command. With MD060 at its default settings, `markdownlint-cli2 --fix` leaves a table closest to the aligned style unchanged, and rewrites a table closest to the compact style toward compact. An aligned table with a few longer rows appended falls in the second group, so `--fix` strips the padding from the rows that were already aligned. Align before running the fix, including project-specific lint-fix scripts. To align a table:

1. Write all rows with their content
1. Find the longest content in each column (including header text)
1. Pad every cell to match the longest content's width with trailing spaces
1. Fill delimiter row hyphens to match the column width
1. Verify all pipes are in the same column positions across every row

A hand-aligned table is already in the layout Prettier produces, so adding Prettier to the project later leaves it unchanged.

---

### Header row

Always include a header row and separator row.

---

### Simple tables

Keep tables simple. If a table requires complex formatting or embedded code blocks, consider using a list or definition structure instead.

Tables are a GFM extension.

---

## Horizontal rules

### Horizontal rule syntax (MD035)

Use `---` (three hyphens) for horizontal rules. Be consistent throughout the document.

| Use   | Avoid |
| ----- | ----- |
| `---` | `***` |
| `---` | `___` |

---

### Blank lines around horizontal rules

Add a blank line before and after horizontal rules to prevent them from being interpreted as Setext heading markers.

---

## HTML

### Prefer Markdown syntax

When Markdown has equivalent syntax, prefer it over HTML.

| Use           | Avoid                    |
| ------------- | ------------------------ |
| `**bold**`    | `<strong>bold</strong>`  |
| `[link](url)` | `<a href="url">link</a>` |

---

### HTML for features Markdown lacks

HTML is acceptable and often necessary when Markdown has no equivalent. Common uses include:

- `<details>` and `<summary>` for collapsible sections
- `<kbd>` for keyboard shortcuts
- `<br>` for line breaks (especially in table cells and ToC formatting)
- `<sub>` and `<sup>` for subscript and superscript
- `<dl>`, `<dt>`, `<dd>` for definition lists
- `<picture>` and `<source>` for responsive images

Projects that use HTML in Markdown should disable MD033 in their markdownlint configuration.

---

## Whitespace

### No trailing whitespace (MD009)

Remove trailing whitespace from all lines. Configure your editor to strip trailing whitespace on save.

Exception: In Markdown, two trailing spaces create a hard line break. Prefer a backslash (`\`) or a blank line instead, as trailing spaces are invisible and fragile.

| Use          | Avoid                   |
| ------------ | ----------------------- |
| `line one\`  | `line one` (two spaces) |
| (blank line) | `line one` (two spaces) |

---

### No hard tabs (MD010)

Use spaces, not tabs, for indentation in Markdown content. Match the project's indentation width (commonly 2 or 4 spaces).

---

### No multiple consecutive blank lines (MD012)

Use at most one blank line to separate elements.

---

## File naming

### Lowercase with hyphens

Name Markdown files in lowercase with hyphens as word separators.

| Use                  | Avoid                |
| -------------------- | -------------------- |
| `getting-started.md` | `Getting Started.md` |
| `api-reference.md`   | `API_Reference.md`   |

Exception: conventional filenames like `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, and `LICENSE.md` remain uppercase.

---

### The `.md` extension

Use the `.md` extension, not `.markdown` or `.mdown`.

| Use         | Avoid             |
| ----------- | ----------------- |
| `readme.md` | `readme.markdown` |
| `guide.md`  | `guide.mdown`     |

---

## Accessibility

### Descriptive link text

Screen readers often present links out of context. Write link text that makes sense in isolation.

| Use                                      | Avoid                          |
| ---------------------------------------- | ------------------------------ |
| `See the [style guide](url).`            | `[Click here](url) for style.` |
| `Read [Effective Go](url) for guidance.` | `Read about it [here](url).`   |

---

### Alt text for images

Write alt text that conveys the purpose of the image, not just its visual content. If the image is decorative, consider omitting it or using an empty alt attribute in HTML.

---

### Semantic structure

Use headings to create a navigable outline. Do not use headings solely for visual styling; do not use bold text as a substitute for headings.

---

## Sources

Compiled by [Christopher Boone](https://cboone.github.io). Based on:

- [markdownlint rules](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md) via [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2)
- [Prettier Markdown support](https://prettier.io/blog/2017/11/07/1.8.0.html) (table alignment, prose wrapping)
- [GitHub Flavored Markdown Spec](https://github.github.com/gfm/)
