# Markdown Style Guide

[Document structure](#document-structure) · [Headings](#headings) · [Paragraphs](#paragraphs) · [Line length](#line-length) · [Emphasis](#emphasis) · [Links](#links) · [Images](#images) · [Lists](#lists) · [Code](#code) · [Block quotes](#block-quotes) · [Tables](#tables) · [Horizontal rules](#horizontal-rules) · [HTML](#html) · [Whitespace](#whitespace) · [File naming](#file-naming) · [Accessibility](#accessibility)

---

## Document structure

### Single top-level heading

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

### Trailing newline

End every file with exactly one newline character. Most editors and linters enforce this.

---

## Headings

### ATX-style headings

Use ATX-style (`#`) headings. Never use Setext-style (underline) headings.

| Use           | Avoid                         |
| ------------- | ----------------------------- |
| `# Heading`   | `Heading`<br>`=======`        |
| `## Heading`  | `Heading`<br>`-------`        |

---

### Heading spacing

Include a space after the `#` characters.

| Use          | Avoid     |
| ------------ | --------- |
| `## Heading` | `##Heading` |

---

### Blank lines around headings

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

### Do not skip heading levels

Heading levels should increment by one. Do not skip from `##` to `####`.

| Use                              | Avoid                              |
| -------------------------------- | ---------------------------------- |
| `##` then `###` then `####`      | `##` then `####`                   |

---

### No trailing punctuation

Do not end headings with periods or colons. Question marks and exclamation marks are acceptable when they are part of the heading's meaning.

| Use                | Avoid                |
| ------------------ | -------------------- |
| `## Installation`  | `## Installation.`   |
| `## Installation`  | `## Installation:`   |
| `## Why Markdown?` | (acceptable)         |

---

### No inline code as full headings

Do not make an entire heading inline code. Use inline code only for identifiers within headings.

| Use                          | Avoid               |
| ---------------------------- | -------------------- |
| `## The \`config\` object`   | `` ## `config` ``    |

---

### Unique headings

Each heading within a document should be unique. Duplicate headings produce conflicting anchor links.

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

### No indented paragraphs

Do not indent the first line of a paragraph. Indented text can be interpreted as a code block.

| Use                | Avoid                    |
| ------------------ | ------------------------ |
| `Regular text.`    | `    Indented text.`     |

---

## Line length

### Wrap long lines

Wrap prose lines at a consistent length (80-100 characters) when the project enforces it. This improves readability in terminals and diff views.

---

### Sentence-per-line

In version-controlled documents, one sentence per line is an acceptable alternative. It produces cleaner diffs when sentences are added, removed, or reworded.

```markdown
<!-- Sentence per line -->
Markdown is a lightweight markup language.
It was created by John Gruber in 2004.
The goal was readability in plain text form.
```

---

### Do not break within a sentence

Whichever wrapping style is used, do not break in the middle of a sentence at arbitrary points. Break at sentence boundaries or at the line length limit.

---

## Emphasis

### Bold and italic markers

Use `**` for bold and `_` for italic. This convention avoids ambiguity with `*` and `__`.

| Use              | Avoid            |
| ---------------- | ---------------- |
| `**bold text**`  | `__bold text__`  |
| `_italic text_`  | `*italic text*`  |

---

### No emphasis in headings

Avoid emphasis markers inside headings. The heading level already provides visual distinction.

| Use             | Avoid               |
| --------------- | -------------------- |
| `## Overview`   | `## **Overview**`    |

---

### No empty emphasis

Do not use emphasis markers around whitespace or empty strings.

| Use            | Avoid  |
| -------------- | ------ |
| (omit)         | `** **` |
| (omit)         | `____`  |

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

### Meaningful link text

Use descriptive link text. Avoid "click here", "here", "this", or bare URLs as link text.

| Use                                             | Avoid                                        |
| ------------------------------------------------ | -------------------------------------------- |
| `See the [installation guide](url).`             | `Click [here](url) to install.`              |
| `Read the [API reference](url) for details.`     | `Details: [https://example.com/api](url)`     |

---

### Angle bracket autolinks

Use angle brackets for literal URLs that should be clickable.

| Use                          | Avoid                    |
| ---------------------------- | ------------------------ |
| `<https://example.com>`      | `https://example.com`    |

---

## Images

### Alt text

Always include descriptive alt text for images.

| Use                                    | Avoid                  |
| -------------------------------------- | ---------------------- |
| `![Diagram of auth flow](auth.png)`    | `![](auth.png)`        |
| `![Screenshot of dashboard](dash.png)` | `![image](dash.png)`   |

---

### Image links

To make an image clickable, wrap the image syntax in a link.

```markdown
[![Project logo](logo.png)](https://example.com)
```

---

## Lists

### Unordered list markers

Use `-` (hyphen) for unordered list items. Be consistent throughout the document.

| Use         | Avoid       |
| ----------- | ----------- |
| `- Item`    | `* Item`    |
| `- Item`    | `+ Item`    |

---

### Ordered list numbering

Use `1.` for every item in ordered lists. The renderer handles the numbering, and this avoids renumbering when items are added or removed.

```markdown
<!-- Use -->
1. First item
1. Second item
1. Third item
```

```markdown
<!-- Avoid: manual numbering -->
1. First item
2. Second item
3. Third item
```

---

### List indentation

Indent nested lists consistently, using the same number of spaces throughout the document (2 or 4 spaces).

```markdown
- Top level
  - Nested item
    - Deeply nested
```

---

### Blank lines around lists

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

Use `- [ ]` and `- [x]` for task lists. Keep a space inside the brackets for unchecked items.

```markdown
- [x] Write the introduction
- [ ] Add code examples
- [ ] Review and publish
```

---

## Code

### Inline code

Use backticks for inline code: commands, function names, variable names, file paths, and short expressions.

| Use                       | Avoid                  |
| ------------------------- | ---------------------- |
| `Run \`npm install\``     | `Run "npm install"`    |
| `The \`config\` object`   | `The config object`    |

---

### Fenced code blocks

Use triple-backtick fenced code blocks, not indented code blocks. Always specify a language identifier.

````markdown
<!-- Use -->
```python
def hello():
    print("Hello, world!")
```
````

````markdown
<!-- Avoid: indented code block, no language -->
    def hello():
        print("Hello, world!")
````

---

### Language identifiers

Always include a language identifier on fenced code blocks for syntax highlighting and tooling.

| Use               | Avoid    |
| ----------------- | -------- |
| ` ```javascript ` | ` ``` `  |
| ` ```bash `       | ` ``` `  |
| ` ```text `       | ` ``` `  |

Use `text` when no syntax highlighting applies.

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

### No code blocks inside headings

Do not place fenced code blocks inside headings.

---

## Block quotes

### Block quote markers

Use `>` followed by a space for block quotes.

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

### Table alignment

Use pipes and hyphens for tables. Align columns for readability in the source, but do not obsess over exact alignment when the table is maintained programmatically.

```markdown
| Name    | Type   | Default |
| ------- | ------ | ------- |
| timeout | number | 30      |
| retries | number | 3       |
```

---

### Header row

Always include a header row and separator row.

---

### Simple tables

Keep tables simple. If a table requires complex formatting or embedded code blocks, consider using a list or definition structure instead.

---

## Horizontal rules

### Horizontal rule syntax

Use `---` (three hyphens) for horizontal rules. Be consistent throughout the document.

| Use   | Avoid   |
| ----- | ------- |
| `---` | `***`   |
| `---` | `___`   |

---

### Blank lines around horizontal rules

Add a blank line before and after horizontal rules to prevent them from being interpreted as Setext heading markers.

---

## HTML

### Avoid raw HTML

Avoid inline HTML in Markdown files. Use Markdown syntax wherever possible.

| Use                   | Avoid                    |
| --------------------- | ------------------------ |
| `**bold**`            | `<strong>bold</strong>`  |
| `[link](url)`         | `<a href="url">link</a>` |

---

### Acceptable HTML

Some HTML is acceptable when Markdown has no equivalent: `<details>`, `<summary>`, `<kbd>`, `<br>`, `<sub>`, `<sup>`, and definition lists (`<dl>`, `<dt>`, `<dd>`).

---

## Whitespace

### No trailing whitespace

Remove trailing whitespace from all lines. Configure your editor to strip trailing whitespace on save.

Exception: In Markdown, two trailing spaces create a hard line break. Prefer a backslash (`\`) or a blank line instead, as trailing spaces are invisible and fragile.

| Use               | Avoid                         |
| ----------------- | ----------------------------- |
| `line one\`       | `line one  ` (two spaces)     |
| (blank line)      | `line one  ` (two spaces)     |

---

### No multiple consecutive blank lines

Use at most one blank line to separate elements.

---

### Consistent indentation

Use spaces, not tabs, for indentation in Markdown content. Match the project's indentation width (commonly 2 or 4 spaces).

---

## File naming

### Lowercase with hyphens

Name Markdown files in lowercase with hyphens as word separators.

| Use                      | Avoid                       |
| ------------------------ | --------------------------- |
| `getting-started.md`     | `Getting Started.md`        |
| `api-reference.md`       | `API_Reference.md`          |

Exception: conventional filenames like `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, and `LICENSE.md` remain uppercase.

---

### The `.md` extension

Use the `.md` extension, not `.markdown` or `.mdown`.

| Use              | Avoid                  |
| ---------------- | ---------------------- |
| `readme.md`      | `readme.markdown`      |
| `guide.md`       | `guide.mdown`          |

---

## Accessibility

### Descriptive link text

Screen readers often present links out of context. Write link text that makes sense in isolation.

| Use                                        | Avoid                            |
| ------------------------------------------ | -------------------------------- |
| `See the [style guide](url).`              | `[Click here](url) for style.`  |
| `Read [Effective Go](url) for guidance.`   | `Read about it [here](url).`    |

---

### Alt text for images

Write alt text that conveys the purpose of the image, not just its visual content. If the image is decorative, consider omitting it or using an empty alt attribute in HTML.

---

### Semantic structure

Use headings to create a navigable outline. Do not use headings solely for visual styling; do not use bold text as a substitute for headings.

---

## Sources

Compiled by [Christopher Boone](https://cboone.github.io). Based on some of each of the following:

- [Google Markdown Style Guide](https://google.github.io/styleguide/docguide/style.html)
- [Cirosantilli Markdown Style Guide](https://cirosantilli.com/markdown-style-guide)
- [markdownlint Rules](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md)
- [CommonMark Spec](https://spec.commonmark.org/)
