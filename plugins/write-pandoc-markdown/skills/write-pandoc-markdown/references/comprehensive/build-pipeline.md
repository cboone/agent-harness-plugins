# The Pandoc-to-LaTeX Build Pipeline

Comprehensive reference for the two-stage build pipeline that converts Pandoc Markdown to venue-formatted PDFs. Covers the Pandoc conversion step, latexmk compilation, key flags, templates, Lua filters, and debugging techniques. Based on the Pandoc User's Guide.

## Two-Stage Build Overview

The pipeline has two distinct stages:

1. **Pandoc** converts `.md` to `.tex` using a venue-specific LaTeX template.
2. **latexmk** compiles `.tex` to `.pdf` via pdflatex and BibTeX (multiple passes as needed).

```text
main.md  --[Pandoc]--> main.tex  --[latexmk]--> main.pdf
```

### Why two stages?

A single-stage `pandoc -o main.pdf` pipeline exists (Pandoc can invoke a PDF engine directly), but the two-stage approach provides critical advantages:

- **Full LaTeX capabilities.** The generated `.tex` is a complete LaTeX document that uses venue-required class files (IEEEtran, usenix), BibTeX style files (.bst), and custom packages (cleveref, TikZ, booktabs).
- **BibTeX style compatibility.** Venues provide `.bst` files that format references to their specifications. The `--natbib` flag produces `\cite` commands that BibTeX processes with these style files.
- **Inspectable intermediate output.** The `.tex` file can be examined to diagnose formatting issues, verify that Pandoc conversions are correct, and manually adjust if needed.
- **Incremental compilation.** latexmk only recompiles when sources change, making rebuilds fast after small edits.

### The generated `.tex` is a build artifact

The `.tex` file is regenerated from the `.md` source on every build. It should be gitignored, not edited directly. Any changes to the paper go in the `.md` source.

## Stage 1: Pandoc Conversion

Pandoc reads the Markdown source, applies the template, and writes a `.tex` file.

### Key flags

#### `--template=path`

Specifies the LaTeX template that defines the document structure. The template contains Pandoc variable placeholders (`$title$`, `$body$`, etc.) that are filled from the YAML frontmatter and the converted Markdown body.

```bash
pandoc --template=templates/<venue>.latex -o main.tex main.md
```

#### `--natbib`

Converts Pandoc citation syntax to `\cite` family commands:

| Pandoc syntax | LaTeX output     |
| ------------- | ---------------- |
| `[@key]`      | `\cite{key}`     |
| `@key`        | `\citet{key}`    |
| `[-@key]`     | `\citeyear{key}` |
| `[@k1; @k2]`  | `\cite{k1,k2}`   |

The actual bibliography formatting is handled by BibTeX during the latexmk step, using the `.bst` style specified in `bibliographystyle:`.

#### `--wrap=none`

Prevents Pandoc from inserting line breaks in the generated `.tex`. This flag is critical: without it, Pandoc wraps lines at 72 characters by default (or the value set by `--columns`). Line breaks inside LaTeX commands or macro arguments can break compilation.

```bash
# CRITICAL: always use --wrap=none for LaTeX output
pandoc --wrap=none ...
```

For example, a long `\caption{}` that Pandoc wraps across lines may produce invalid LaTeX if the break falls in the wrong place.

#### `-f markdown+raw_tex+raw_attribute+fenced_divs+citations`

Specifies the input format with required Pandoc extensions:

| Extension        | Purpose                                               |
| ---------------- | ----------------------------------------------------- |
| `+raw_tex`       | Pass through raw LaTeX commands outside fenced blocks |
| `+raw_attribute` | Enable `{=latex}` on fenced blocks and inline spans   |
| `+fenced_divs`   | Allow `:::` div syntax for custom containers          |
| `+citations`     | Enable `[@key]` citation syntax                       |

#### `--syntax-highlighting=none`

Disables syntax highlighting for code blocks. When code blocks are present but highlighting is not needed (or when the venue template handles it differently), this avoids loading unnecessary LaTeX packages.

### Complete example

```bash
pandoc \
  --template=templates/<venue>.latex \
  --natbib \
  --syntax-highlighting=none \
  --wrap=none \
  -f markdown+raw_tex+raw_attribute+fenced_divs+citations \
  -o main.tex \
  main.md
```

## Stage 2: latexmk Compilation

latexmk manages the multi-pass compilation needed to resolve all cross-references, citations, and other LaTeX features that require iterative processing.

### Basic invocation

```bash
latexmk -pdf -silent -interaction=nonstopmode main
```

| Flag                       | Purpose                                      |
| -------------------------- | -------------------------------------------- |
| `-pdf`                     | Produce PDF via pdflatex                     |
| `-silent`                  | Suppress non-essential output                |
| `-interaction=nonstopmode` | Do not stop for errors (continue and report) |

### What latexmk does automatically

A typical LaTeX document with citations and cross-references requires:

1. `pdflatex main` (first pass: generates `.aux` with citation keys and labels)
2. `bibtex main` (processes `.aux` to generate `.bbl` with formatted references)
3. `pdflatex main` (second pass: incorporates `.bbl`, updates references)
4. `pdflatex main` (third pass: resolves all cross-references)

latexmk detects when additional passes are needed and runs them automatically. It also watches for dependency changes and skips unnecessary steps on subsequent builds.

### TEXINPUTS

The `TEXINPUTS` environment variable tells the LaTeX engine where to find input files (class files, style files, shared macros). In a multi-paper project with a shared directory:

```makefile
export TEXINPUTS := $(SHARED)/:$(TEXINPUTS)
```

This adds the shared directory to the search path, making `macros.tex`, `tikz-styles.tex`, and other shared resources available to all papers.

## Makefile Structure

Each paper typically has its own Makefile that orchestrates both stages.

### Full example

```makefile
MAIN = main
SHARED = ../shared
TEMPLATE = $(SHARED)/templates/ieee.latex
export TEXINPUTS := $(SHARED)/:$(TEXINPUTS)

PANDOC_FLAGS = \
    --template=$(TEMPLATE) \
    --natbib \
    --syntax-highlighting=none \
    --wrap=none \
    -f markdown+raw_tex+raw_attribute+fenced_divs+citations

all: $(MAIN).pdf

$(MAIN).tex: $(MAIN).md $(TEMPLATE) $(SHARED)/macros.tex $(SHARED)/tikz-styles.tex
    pandoc $(PANDOC_FLAGS) -o $@ $<

$(MAIN).pdf: $(MAIN).tex $(SHARED)/bibliography.bib
    latexmk -pdf -silent -interaction=nonstopmode $(MAIN)

figures:
    cd figures && uv run generate.py

clean:
    latexmk -C
    rm -f $(MAIN).tex $(MAIN).bbl $(MAIN).run.xml

.PHONY: all figures clean
```

Key details:

- The `.tex` target depends on the `.md` source, the template, and shared macros. Changing any of these triggers regeneration.
- The `.pdf` target depends on the `.tex` file and the bibliography. latexmk handles further dependencies internally.
- `clean` removes all build artifacts, including the generated `.tex`, `.bbl`, and latexmk's auxiliary files.
- `figures` generates paper figures by running Python scripts via `uv`.

## PDF Engine Selection

When using the two-stage pipeline, the PDF engine is configured in the latexmk step, not in Pandoc. However, understanding the options is useful for debugging and for alternative workflows.

### pdflatex

The default engine. Fast compilation, excellent package compatibility, limited Unicode support. Sufficient for English-language papers using standard LaTeX fonts.

```bash
latexmk -pdf main          # uses pdflatex
```

### xelatex

Full Unicode support and system font access. Use for papers requiring non-Latin scripts or specific fonts.

```bash
latexmk -xelatex main      # uses xelatex
```

### lualatex

Full Unicode support plus a Lua scripting engine. Use when packages require LuaTeX features.

```bash
latexmk -lualatex main     # uses lualatex
```

### Direct Pandoc-to-PDF (single stage)

For simpler documents that do not need BibTeX or venue class files, Pandoc can produce PDF directly:

```bash
pandoc -o main.pdf main.md                  # uses pdflatex by default
pandoc --pdf-engine=xelatex -o main.pdf main.md
pandoc --pdf-engine=lualatex -o main.pdf main.md
```

This approach does not support `--natbib` (which requires a BibTeX step). Use `--citeproc` instead for single-stage PDF generation.

## Templates

Templates define the LaTeX document structure with Pandoc variable placeholders.

### How templates work

A template is a LaTeX file with `$variable$` placeholders that Pandoc fills from the YAML frontmatter and the document body.

```latex
\documentclass[$for(classoption)$$classoption$$sep$,$endfor$]{IEEEtran}

\title{$title$}
\author{$author$}

\begin{document}
\maketitle

\begin{abstract}
$abstract$
\end{abstract}

$body$

\bibliographystyle{$bibliographystyle$}
\bibliography{$bibliography$}

\end{document}
```

### Key variables

| Variable              | Source                    | Description            |
| --------------------- | ------------------------- | ---------------------- |
| `$title$`             | YAML `title:`             | Paper title            |
| `$author$`            | YAML `author:`            | Author name(s)         |
| `$abstract$`          | YAML `abstract:`          | Abstract text          |
| `$body$`              | Markdown content          | Converted paper body   |
| `$bibliography$`      | YAML `bibliography:`      | Path to .bib file      |
| `$bibliographystyle$` | YAML `bibliographystyle:` | BibTeX style name      |
| `$header-includes$`   | YAML `header-includes:`   | Extra preamble content |

### Template conditionals and loops

Pandoc templates support conditionals and iteration:

```latex
$if(abstract)$
\begin{abstract}
$abstract$
\end{abstract}
$endif$

$for(header-includes)$
$header-includes$
$endfor$
```

### Custom variables

Any field in the YAML frontmatter becomes a template variable. Define custom fields as needed:

```yaml
---
shorttitle: "Password Security SoK"
venue: "IEEE S&P 2026"
---
```

Access them in the template with `$shorttitle$` and `$venue$`.

### Venue templates

Multi-paper projects typically keep one template per venue family in a shared templates directory. Common examples:

- `ieee.latex` for IEEEtran (IEEE S&P, IEEE TIT, IEEE Security & Privacy magazine)
- `usenix.latex` for USENIX papers (USENIX Security, SOUPS)
- `acm.latex` for ACM acmart papers (CCS, IMC, CPP)

## Lua Filters

Lua filters transform Pandoc's abstract syntax tree (AST) between the parsing step and the writing step. They are a powerful extension mechanism.

### Invocation

```bash
pandoc --lua-filter=my-filter.lua -o main.tex main.md
```

Multiple filters can be chained. They execute in the order specified.

### When to use Lua filters

- **Scholarly metadata extraction:** pull author affiliations into structured format
- **Diagram generation:** convert code blocks to rendered diagrams (Mermaid, PlantUML)
- **Custom transformations:** rewrite specific AST nodes (e.g., convert certain divs to LaTeX environments)
- **Format-specific tweaks:** adjust output for particular venues or formats

### Filter ordering

Filters run in the order specified on the command line. This matters when filters interact:

```bash
# pandoc-crossref must run before citeproc (both use [@...] syntax)
pandoc --filter pandoc-crossref --citeproc -o main.tex main.md

# Lua filters run in order
pandoc --lua-filter=first.lua --lua-filter=second.lua -o main.tex main.md
```

### Simple Lua filter example

A filter that converts all level-4 headings to bold paragraphs (useful for some venue formats):

```lua
function Header(el)
  if el.level == 4 then
    return pandoc.Para({pandoc.Strong(el.content)})
  end
end
```

## Debugging the Pipeline

### Examine the generated `.tex`

The most effective debugging technique is reading the generated `.tex` file. It shows exactly what Pandoc produced.

```bash
# Generate .tex without building PDF
pandoc $(PANDOC_FLAGS) -o main.tex main.md

# Inspect the output
less main.tex
```

### Common problems and solutions

#### Line breaks inside LaTeX commands

**Symptom:** LaTeX compilation error in a `\caption`, `\title`, or other command.
**Cause:** Missing `--wrap=none` flag. Pandoc wrapped a long line, breaking a LaTeX command across lines.
**Fix:** Add `--wrap=none` to the Pandoc flags.

#### Citations not resolving

**Symptom:** `[?]` appears in place of citation numbers.
**Cause:** BibTeX did not run, or the `.bib` file path is incorrect.
**Fix:** Check that `bibliography:` in the YAML frontmatter points to the correct `.bib` file (relative to the `.md` file). Ensure latexmk runs BibTeX (check the `.blg` file for errors).

#### Raw LaTeX appearing as source code

**Symptom:** LaTeX commands appear literally in the PDF instead of being executed.
**Cause:** Using ` ```{latex} ` or ` ```latex ` instead of ` ```{=latex} `.
**Fix:** Add the `=` sign: ` ```{=latex} `.

#### Missing extensions

**Symptom:** Citation syntax `[@key]` appears literally; raw LaTeX spans are not recognized.
**Cause:** The `-f` flag does not include the necessary extensions.
**Fix:** Ensure the format includes `+raw_tex+raw_attribute+citations`.

#### Template variable not rendering

**Symptom:** A YAML field value does not appear in the PDF.
**Cause:** The template does not reference the variable, or the variable name is misspelled.
**Fix:** Check the template source for `$variable_name$` and ensure the YAML field name matches exactly.

### Verbose output

Run Pandoc with `--verbose` for detailed processing information:

```bash
pandoc --verbose $(PANDOC_FLAGS) -o main.tex main.md 2>&1 | less
```

This shows which extensions are active, how citations are processed, and any warnings about unrecognized content.

### latexmk log files

latexmk produces several log files:

| File       | Contents                                             |
| ---------- | ---------------------------------------------------- |
| `main.log` | Full pdflatex output (warnings, errors, page counts) |
| `main.blg` | BibTeX log (citation resolution, missing entries)    |
| `main.aux` | Auxiliary data (labels, citation keys)               |

Check `main.blg` first for citation issues, then `main.log` for everything else.

## Build Workflow Summary

1. Edit `main.md` (Pandoc Markdown with YAML frontmatter).
2. Run `make` (or `make all`) in the paper directory.
3. Pandoc converts `main.md` to `main.tex` using the venue template.
4. latexmk compiles `main.tex` to `main.pdf`, running pdflatex and BibTeX as many times as needed.
5. If the build fails, examine `main.tex` (for Pandoc issues) or `main.log`/`main.blg` (for LaTeX/BibTeX issues).
6. The generated `main.tex` and all auxiliary files are gitignored. Only `main.md` is committed.
