# YAML Frontmatter for Academic Papers

Comprehensive reference for configuring Pandoc documents through YAML metadata blocks. Covers standard academic fields, template variables, header includes, escaping rules, and multi-block metadata. Based on the Pandoc User's Guide.

## Basic Structure

YAML frontmatter is placed at the very beginning of the Markdown file, enclosed between `---` delimiters.

```yaml
---
title: "My Paper Title"
author: Author Name
bibliography: refs.bib
---
```

In this repository the frontmatter title is the document title. Do not repeat it as a body `# Title` heading. The first real body section should start at `##`.

### Delimiter rules

- The opening `---` must be the first line of the file (no blank lines or content before it).
- The opening `---` must NOT be followed by a blank line; the first field must appear on the next line.
- The metadata block ends with `---` or `...` on its own line.
- Everything between the delimiters is YAML, parsed according to standard YAML 1.1 rules.

## Standard Academic Fields

### title

The paper title. Quotes are required if the title contains a colon, because YAML interprets bare colons as key-value separators.

```yaml
title: Simple Title Without Colons
title: "Title With a Colon: The Subtitle"
title: "SoK: Password Security from Entropy to Survival Analysis"
```

Project convention:

```markdown
---
title: "SoK: Password Security from Entropy to Survival Analysis"
---

## Introduction
```

Do not write both `title:` in frontmatter and a duplicate body `# SoK: ...` heading.

### author

A single author as a string:

```yaml
author: Author Name
```

Multiple authors as a list of strings:

```yaml
author:
  - Alice Smith
  - Bob Jones
  - Carol White
```

Structured author data with affiliations:

```yaml
author:
  - name: Alice Smith
    affiliation: University of Example
    email: alice@example.edu
  - name: Bob Jones
    affiliation: Institute of Research
    email: bob@research.org
```

The template determines how structured author data is rendered. Simple templates may only use the `name` field; venue-specific templates often use `affiliation` and `email` as well.

### abstract

Use the YAML pipe (`|`) for multiline content. The pipe preserves newlines, which Pandoc then interprets as Markdown.

```yaml
abstract: |
  This paper presents a formal framework for password security
  that models the interaction of five mathematical spaces and
  four agents. We prove that traditional entropy-based metrics
  are insufficient for capturing real-world attack dynamics.

  Our framework introduces survival analysis as the unifying
  formalism, connecting guessing curves, KDF cost, and attacker
  economics into a single coherent model.
```

Each blank line within the pipe block starts a new paragraph. The content after the pipe is indented (typically two spaces). Pandoc interprets the abstract content as Markdown, so you can use inline math (`$...$`), emphasis (`*...*`), and other Markdown formatting.

### bibliography

Path to the BibTeX (`.bib`) file, relative to the Markdown source file.

```yaml
bibliography: refs.bib
bibliography: ../shared/bibliography.bib
bibliography: /absolute/path/to/refs.bib
```

Multiple bibliography files:

```yaml
bibliography:
  - main-refs.bib
  - additional-refs.bib
```

### bibliographystyle

The BibTeX style file name (without `.bst` extension). Used only with `--natbib`.

```yaml
bibliographystyle: IEEEtran
bibliographystyle: plain
bibliographystyle: acm
bibliographystyle: unsrt
```

This field has no effect when using `--citeproc`. For citeproc, use `csl:` instead.

### classoption

A YAML list of document class options passed to `\documentclass[options]{class}`.

```yaml
classoption:
  - conference
  - letterpaper
  - twocolumn
```

Or as an inline YAML list:

```yaml
classoption: [conference, letterpaper, twocolumn]
```

These become the optional argument to `\documentclass` in the generated `.tex` file.

### keywords

A YAML list of keywords for the paper.

```yaml
keywords:
  - password security
  - entropy
  - survival analysis
  - guessing curves
```

### nocite

Force-cite entries that are not cited in the text but should appear in the bibliography. Use the pipe for multiline content.

```yaml
nocite: |
  @shannon1948
  @bonneau2012
```

To cite all entries in the bibliography file:

```yaml
nocite: |
  @*
```

### date

The document date. If omitted, many templates leave the date blank.

```yaml
date: "2025-01-15"
date: "January 2025"
```

## Template Variables

These variables control the generated LaTeX document structure. Their availability depends on the template being used. The following are supported by Pandoc's default LaTeX template and most custom templates.

### documentclass

The LaTeX document class.

```yaml
documentclass: article
documentclass: report
documentclass: book
documentclass: IEEEtran
```

For venue-specific templates, the document class is typically hardcoded in the template, so this field is not needed.

### fontsize

Base font size for the document.

```yaml
fontsize: 10pt
fontsize: 11pt
fontsize: 12pt
```

### geometry

Page geometry settings, passed to the `geometry` LaTeX package.

```yaml
geometry: margin=1in
geometry:
  - top=1in
  - bottom=1in
  - left=0.75in
  - right=0.75in
```

### linestretch

Line spacing multiplier, passed to the `setspace` package.

```yaml
linestretch: 1.0    # single spacing
linestretch: 1.5    # one-and-a-half spacing
linestretch: 2.0    # double spacing
```

### pagestyle

Page header/footer style.

```yaml
pagestyle: plain      # page numbers only
pagestyle: empty      # no headers or footers
pagestyle: headings   # section titles in headers
```

### numbersections

Whether to number sections.

```yaml
numbersections: true
numbersections: false
```

### colorlinks

Whether hyperlinks should be colored (requires hyperref).

```yaml
colorlinks: true
linkcolor: blue
citecolor: green
urlcolor: cyan
```

### lang

Document language, used for hyphenation and localization.

```yaml
lang: en-US
lang: pt-BR
```

## Header Includes

The `header-includes` field injects raw LaTeX into the document preamble. Use it for loading packages, defining macros, or setting up environments that are not handled by the template.

```yaml
header-includes:
  - \usepackage{tikz}
  - \usepackage{booktabs}
  - \usepackage{algorithmic}
  - \newcommand{\pspace}{\mathcal{P}}
  - \DeclareMathOperator{\argmax}{arg\,max}
```

Each list item is a string containing a LaTeX command. These are placed in the preamble after the template's own package loads.

### When to use header-includes vs. shared macros

- Use `header-includes` for paper-specific packages or macros that only one paper needs.
- Use a shared macro file (e.g. a project-wide `macros.tex`) for notation and packages used across every paper in a multi-paper project. The template `\input`s the shared file.

### Multi-line header-includes

For longer preamble additions, use the pipe syntax:

```yaml
header-includes: |
  \usepackage{tikz}
  \usetikzlibrary{arrows,positioning}
  \tikzset{
    block/.style={rectangle, draw, minimum width=2cm}
  }
```

## Field Escaping and YAML Gotchas

### Strings with colons need quotes

YAML interprets `key: value` syntax anywhere it finds a colon followed by a space. Titles, descriptions, and other text fields that contain colons must be quoted.

```yaml
# WRONG: YAML parse error
title: SoK: Password Security Analysis

# RIGHT: quoted string
title: "SoK: Password Security Analysis"
```

### Pipe (`|`) for multiline fields

The pipe character preserves newlines. Use it for abstracts, long descriptions, and any field that spans multiple lines.

```yaml
abstract: |
  First paragraph of the abstract.

  Second paragraph of the abstract.
```

The content must be indented relative to the field name.

### YAML booleans and numbers

Field values that look like YAML booleans or numbers are parsed as such, not as strings. This rarely matters for Pandoc metadata but can cause surprises.

```yaml
# These are parsed as booleans, not strings
yes: true
no: false
on: true
off: false

# These are parsed as numbers, not strings
version: 15
threshold: 3.14
```

If you need them as strings, quote them:

```yaml
version: "15"
answer: "yes"
```

### Fields ending with underscore

Field names ending with an underscore are ignored by Pandoc. This is useful for storing metadata that should not affect the output.

```yaml
internal_notes_: "This is a draft; do not distribute."
```

### All string scalar values are Markdown

Pandoc interprets all string values in the frontmatter as Markdown. This means you can use inline formatting:

```yaml
title: "A *Novel* Approach to Password Security"
# The word "Novel" will be italicized in the output
```

This also means you must escape characters that have special Markdown meaning if you want them literal.

## Multiple Metadata Blocks

A Pandoc document may contain more than one YAML metadata block. Later blocks override earlier ones for fields with the same name; fields from earlier blocks are preserved if not overridden.

```yaml
---
title: "My Paper"
author: Alice
---
Some content...
---
date: "2025-01-15"
keywords:
  - security
  - passwords
---
More content...
```

This is occasionally useful for setting metadata that depends on the document content, but most papers use a single frontmatter block at the top.

## Example Frontmatter (complete)

A complete example for an IEEE conference paper in a multi-paper project that keeps its bibliography in a shared directory:

```yaml
---
title: "SoK: An Example Systematization Title"
author: Author Name
abstract: |
  TODO: Abstract.
bibliography: ../shared/bibliography.bib
bibliographystyle: IEEEtran
classoption:
  - conference
nocite: |
  @some_key
---
```

Key points about this example:

- The title is quoted because it contains a colon.
- The bibliography path is relative to the Markdown file; `../shared/bibliography.bib` is the convention when sibling papers share a `shared/` directory.
- `bibliographystyle: IEEEtran` pairs with the `--natbib` flag in the Makefile.
- `classoption: [conference]` is passed to `\documentclass[conference]{IEEEtran}` via the template.
- `nocite` forces the referenced entry into the bibliography even if it is not cited in the text.

## Frontmatter for Different Venues

### IEEE (IEEEtran class)

```yaml
---
title: "Paper Title"
author: Author Name
abstract: |
  Abstract text.
bibliography: ../shared/bibliography.bib
bibliographystyle: IEEEtran
classoption:
  - conference
---
```

### USENIX

```yaml
---
title: "Paper Title"
author: Author Name
abstract: |
  Abstract text.
bibliography: ../shared/bibliography.bib
bibliographystyle: plain
classoption:
  - letterpaper
  - twocolumn
  - 10pt
---
```

### ACM (acmart class)

```yaml
---
title: "Paper Title"
author:
  - name: Author Name
    affiliation: University
    email: author@example.edu
abstract: |
  Abstract text.
bibliography: refs.bib
bibliographystyle: ACM-Reference-Format
classoption:
  - sigconf
---
```

The exact fields required depend on the venue template. Always check the template source for the variables it expects.
