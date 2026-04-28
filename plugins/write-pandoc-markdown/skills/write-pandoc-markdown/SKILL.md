---
name: write-pandoc-markdown
description: >-
  Pandoc-flavored Markdown conventions for academic papers with LaTeX output.
  Use when: (1) writing or editing .md files that use Pandoc extensions (math
  delimiters, citations, raw LaTeX blocks), (2) configuring YAML frontmatter
  for academic papers, (3) using Pandoc citation syntax, (4) embedding raw
  LaTeX in Markdown, or (5) working with the Pandoc-to-LaTeX build pipeline.
  This skill is distinct from write-markdown, which covers GFM and markdownlint
  rules.
---

# Write Pandoc Markdown

Apply the Pandoc Markdown conventions from the reference files below when
creating or editing academic papers authored in Pandoc-flavored Markdown.

This skill covers Pandoc extensions and the Markdown-to-LaTeX pipeline. For
GFM formatting and markdownlint rules, see the `write-markdown` skill instead.

Document titles belong in YAML frontmatter (`title:`), not as a body `#`
heading. The frontmatter title is the implicit H1, so the first real body
section starts at `##`.

## Core Principles

1. **Plain text sustainability** -- Markdown source should remain readable and
   editable decades from now, independent of any tool
1. **Separation of content and formatting** -- write content in Markdown; let
   the template and build pipeline handle visual presentation
1. **Pandoc syntax over raw LaTeX when possible** -- use `[@key]` for
   citations, `$...$` for math, Markdown headings for sections; fall back to
   raw LaTeX only for constructs Pandoc cannot express
1. **Format-independent content** -- raw LaTeX blocks are invisible in HTML and
   DOCX output; prefer Pandoc-native syntax for maximum portability

## Workflow

1. Review against the essential checklist:
   `./references/essential/checklist.md`
1. For specific questions, consult the comprehensive references below

## Reference Navigation

**Quick reviews (default):**

- `references/essential/checklist.md` -- condensed, actionable rules

**Deep dives by topic:**

- `references/comprehensive/math-and-citations.md` -- math delimiter rules,
  currency escaping, citation syntax, natbib vs citeproc
- `references/comprehensive/cross-references.md` -- raw LaTeX spans,
  pandoc-crossref, section labels, filter ordering
- `references/comprehensive/raw-latex-blocks.md` -- when to use raw LaTeX,
  fenced block syntax, inline raw spans, theorem environments
- `references/comprehensive/yaml-frontmatter.md` -- academic metadata fields,
  template variables, header includes, field escaping
- `references/comprehensive/build-pipeline.md` -- two-stage build, Pandoc
  flags, PDF engines, Lua filters

## Sources

- MacFarlane, J. *Pandoc User's Guide*. pandoc.org.
- Yakimova, N. *pandoc-crossref*. GitHub.
- Drescher, D. and Gessler, A. *Pandoc Scholar*.
- Programming Historian. "Sustainable Authorship in Plain Text Using Pandoc
  and Markdown."
