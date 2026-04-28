
# Cross-References in Pandoc Markdown

Comprehensive reference for cross-referencing sections, figures, equations, and tables in Pandoc Markdown. Covers native Pandoc heading IDs, raw LaTeX spans with cleveref, and the pandoc-crossref filter. Based on the Pandoc User's Guide and pandoc-crossref documentation.

## Section Labels (Native Pandoc)

Pandoc allows attaching identifiers to headings. These become `\label{}` commands in LaTeX output and `id` attributes in HTML output.

When the document title lives in YAML frontmatter, the first real body section starts at level 2.

### Explicit identifiers

```markdown
---
title: "Password Strength as Survival Analysis"
---

## Introduction {#sec:introduction}
## Background and Related Work {#sec:background}
## Formal Model {#sec:formal-model}
```

The identifier is placed in curly braces after the heading text. It must start with `#`.

### Auto-generated identifiers

When no explicit identifier is provided, Pandoc auto-generates one from the heading text by lowercasing, removing punctuation, and replacing spaces with hyphens.

```markdown
## Background and Related Work
<!-- auto-generates id: background-and-related-work -->
```

Auto-generated IDs are fragile: renaming the heading changes the ID and breaks all references to it. Prefer explicit IDs for any heading you plan to cross-reference.

### Unnumbered sections

Add the `.unnumbered` class to suppress the section number.

```markdown
## References {.unnumbered}
## Acknowledgments {.unnumbered}
```

In LaTeX output, this produces `\section*{References}`.

### Unlisted sections

Add the `.unlisted` class to exclude a section from the table of contents. This is often combined with `.unnumbered`.

```markdown
## Appendix Details {.unnumbered .unlisted}
```

## Raw LaTeX Spans (lightweight approach)

A lightweight pattern for LaTeX-only output targets is to write raw LaTeX inline spans for cross-references. This approach requires no extra filters and works with any LaTeX cross-reference package loaded in the preamble.

### Basic syntax

```markdown
As shown in `\cref{sec:introduction}`{=latex}, the framework consists of five spaces.
```

The backtick-delimited content is a raw LaTeX span. The `{=latex}` attribute tells Pandoc to pass the content through unchanged to the LaTeX output. In the generated `.tex`, this produces `\cref{sec:introduction}` exactly as written.

### Common cross-reference commands

```markdown
<!-- Section references -->
`\cref{sec:formal-model}`{=latex}         --> "Section 3" (lowercase)
`\Cref{sec:formal-model}`{=latex}         --> "Section 3" (capitalized, sentence start)

<!-- Equation references -->
`\eqref{eq:survival}`{=latex}             --> "(1)" (with parentheses)
`\cref{eq:survival}`{=latex}              --> "Equation 1"

<!-- Figure references -->
`\cref{fig:architecture}`{=latex}         --> "Figure 2"
`\Cref{fig:architecture}`{=latex}         --> "Figure 2" (capitalized)

<!-- Table references -->
`\cref{tbl:comparison}`{=latex}           --> "Table 1"

<!-- Theorem-like environments -->
`\cref{def:password-space}`{=latex}       --> "Definition 1"
`\cref{thm:survival}`{=latex}             --> "Theorem 2"
```

### Requirements

- The `+raw_attribute` Pandoc extension must be enabled (add it to the `-f` flag).
- The `cleveref` package must be loaded in the LaTeX preamble (typically via a project-wide `macros.tex` or directly in the template).
- Labels must exist in the generated `.tex` (from heading IDs, equation labels in raw LaTeX blocks, or figure/table captions).

### Advantages

- Zero extra dependencies beyond Pandoc itself.
- Works with any LaTeX cross-reference package (cleveref, hyperref, varioref).
- Full control over the exact LaTeX command produced.
- No filter ordering concerns.

### Limitations

- Raw LaTeX spans are invisible in non-LaTeX output (HTML, DOCX, EPUB). The reference simply disappears.
- Acceptable when LaTeX PDF is the only target format, which is the case for this project.

## pandoc-crossref Filter

pandoc-crossref is a Pandoc filter that provides format-independent cross-references using a Pandoc-native syntax. It works across all output formats.

### Installation

```bash
# macOS
brew install pandoc-crossref

# Invocation
pandoc --filter pandoc-crossref ...
```

The pandoc-crossref version must match your Pandoc version. Check compatibility before upgrading either tool.

### Figure references

```markdown
![This is the caption.](figures/architecture.pdf){#fig:architecture width=80%}

As shown in @fig:architecture, the system has three components.
```

The `{#fig:label}` attribute on the image creates the label. Reference it with `@fig:label` in the text.

### Equation references

```markdown
$$ E = mc^2 $$ {#eq:energy}

From @eq:energy, we can derive the relationship.
```

The `{#eq:label}` attribute follows the display math block. Note the space between `$$` and `{#eq:label}`.

### Table references

```markdown
| Column A | Column B |
| ---------- | ---------- |
| 1        | 2        |

: Comparison of approaches {#tbl:comparison}

The results in @tbl:comparison show improvement.
```

The label is placed in the caption line (prefixed with `:`).

### Section references

```markdown
## Formal Model {#sec:formal-model}

As described in @sec:formal-model, we define five spaces.
```

### Listing references

````markdown
```{#lst:example .python caption="Example code"}
def hello():
    print("Hello")
```

See @lst:example for the implementation.
````

### Multiple references

```markdown
[@fig:a; @fig:b; @fig:c]       --> "Figures 1-3" (compressed range)
[@eq:first; @eq:second]        --> "Equations 1, 2"
```

### Capitalized prefix

Use a capital letter at the start of the prefix for sentence beginnings.

```markdown
@fig:architecture shows...     --> "fig. 1 shows..."
@Fig:architecture shows...     --> "Figure 1 shows..."
```

### Subfigures

Use fenced divs to group subfigures under a parent label.

```markdown
::: {#fig:parent}

![Subfigure A caption](a.pdf){#fig:sub-a width=45%}
![Subfigure B caption](b.pdf){#fig:sub-b width=45%}

Parent figure caption.

:::
```

Reference the parent with `@fig:parent` or individual subfigures with `@fig:sub-a`.

### YAML configuration

pandoc-crossref supports extensive configuration through YAML frontmatter or a separate defaults file.

```yaml
---
chapters: false
numberSections: true
sectionsDepth: 3
figPrefix:
  - "Figure"
  - "Figures"
tblPrefix:
  - "Table"
  - "Tables"
eqnPrefix:
  - "Equation"
  - "Equations"
secPrefix:
  - "Section"
  - "Sections"
figureTitle: "Figure"
tableTitle: "Table"
listingTitle: "Listing"
---
```

### Filter ordering

When using pandoc-crossref with `--citeproc`, filter ordering is critical. Both use `[@...]` syntax, so pandoc-crossref must run first to consume its references before citeproc processes citations.

```bash
# Correct order
pandoc --filter pandoc-crossref --citeproc input.md -o output.pdf

# Wrong order (citeproc consumes cross-references as citations)
pandoc --citeproc --filter pandoc-crossref input.md -o output.pdf
```

With `--natbib`, this conflict does not arise because natbib processing happens later during the LaTeX compilation step, not during Pandoc's processing.

## Choosing an Approach

### Raw LaTeX spans

Best when:

- LaTeX PDF is the only output format.
- You want zero extra dependencies.
- You need specific LaTeX cross-reference commands (e.g., `\cref*`, `\vref`, `\nameref`).
- The LaTeX preamble already loads the required packages.

### pandoc-crossref

Best when:

- You need cross-references in multiple output formats (HTML, DOCX, EPUB, LaTeX).
- You prefer a cleaner, more Markdown-native syntax.
- You want automatic range compression (`Figures 1-3`).
- You want subfigure support without raw LaTeX.

### Comparison

| Feature               | Raw LaTeX spans              | pandoc-crossref         |
| --------------------- | ---------------------------- | ----------------------- |
| Dependencies          | None (Pandoc only)           | pandoc-crossref filter  |
| Output formats        | LaTeX only                   | All formats             |
| Syntax                | `` `\cref{label}`{=latex} `` | `@fig:label`            |
| LaTeX command control | Full                         | Limited (uses defaults) |
| Range compression     | Manual                       | Automatic               |
| Subfigures            | Raw LaTeX required           | Native div syntax       |
| Filter ordering       | No concerns                  | Must precede citeproc   |

### Choosing between the two

Prefer raw LaTeX spans with cleveref when the project's only output target is LaTeX PDF: it avoids an extra dependency and gives full control over the cross-reference commands. Prefer pandoc-crossref when you need multiple output formats (HTML, DOCX) or want automatic range compression and subfigure handling.

## Labels in Raw LaTeX Blocks

When placing labels inside raw LaTeX blocks (theorem environments, equations, etc.), use standard LaTeX `\label` commands, not Pandoc syntax.

```markdown
```{=latex}
\begin{definition}[Password Space]\label{def:password-space}
A \emph{password space} $\pspace$ is the set of all strings
accepted by the verification mechanism.
\end{definition}
```

Reference it from Markdown with:

```markdown
As defined in `\cref{def:password-space}`{=latex}, the password space...
```

The label is set inside the raw LaTeX block. The reference is a raw LaTeX inline span. Both resolve during LaTeX compilation.

## Common Mistakes

### Missing `=` in raw attribute

```markdown
Wrong: `\cref{sec:intro}`{latex}       (creates a code span with class "latex")
Right: `\cref{sec:intro}`{=latex}      (raw LaTeX span)
```

### Referencing auto-generated IDs

```markdown
Fragile:
## Background and Related Work
... see `\cref{background-and-related-work}`{=latex} ...

Stable:
## Background and Related Work {#sec:background}
... see `\cref{sec:background}`{=latex} ...
```

### Pandoc syntax inside raw LaTeX blocks

````markdown
Wrong (inside a raw LaTeX block):
```{=latex}
\begin{theorem}
See [@shannon1948] for details.          % Pandoc citation inside raw LaTeX
\end{theorem}
```

Right:

```{=latex}
\begin{theorem}
See \cite{shannon1948} for details.      % LaTeX citation inside raw LaTeX
\end{theorem}
```
````

Inside raw LaTeX blocks, Pandoc does not process any content. Use LaTeX commands directly.
