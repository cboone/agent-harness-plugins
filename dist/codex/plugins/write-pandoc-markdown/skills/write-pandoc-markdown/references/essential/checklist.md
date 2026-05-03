
# Pandoc Markdown Essential Checklist

Quick reference for reviews. For detailed guidance, see `../comprehensive/`.

## Math Delimiters

- [ ] Inline math: `$...$` with no space after opening `$` or before closing `$`
- [ ] Display math: `$$...$$` on its own paragraph (blank lines before and after)
- [ ] No blank lines inside `$$...$$` (breaks the display)
- [ ] Escape currency as `\$`: write `\$438M`, not `$438M`
- [ ] Closing `$` must not be immediately followed by a digit

## Citations

- [ ] Parenthetical: `[@key]` or `[@key, p. 10]`
- [ ] Textual (author in prose): `@key` without brackets
- [ ] Multiple: `[@key1; @key2; @key3]`
- [ ] Suppress author: `[-@key]`
- [ ] Custom prefix: `[See @key]` or `[See @key, Thm. 3.1]`
- [ ] Bibliography path in YAML frontmatter: `bibliography: path/to/file.bib`

## Cross-References

- [ ] Document title lives in YAML frontmatter, not as a body `#` heading
- [ ] First real section starts at `##`: `## Section Name {#sec:label}`
- [ ] Raw LaTeX spans: `` `\cref{sec:label}`{=latex} `` for cleveref references
- [ ] Equation references: `` `\eqref{eq:label}`{=latex} ``
- [ ] pandoc-crossref alternative: `@fig:label`, `@eq:label`, `@tbl:label`
- [ ] Unnumbered sections: `## References {.unnumbered}`

## Raw LaTeX Blocks

- [ ] Fenced syntax: `` ```{=latex} `` (critical: equals sign before `latex`)
- [ ] NOT `` ```{latex} `` or `` ```latex `` (these are code blocks, not raw LaTeX)
- [ ] Use for: theorem environments, complex tables, anything Pandoc cannot express
- [ ] Inline raw spans: `` `\command{arg}`{=latex} ``
- [ ] Raw LaTeX is ignored in non-LaTeX output (HTML, DOCX)

## YAML Frontmatter

- [ ] `title:` is required for project-authored documents
- [ ] `title:` in quotes if it contains colons
- [ ] `author:` as string or structured list
- [ ] `abstract: |` with pipe for multiline content
- [ ] `bibliography:` path to `.bib` file
- [ ] `bibliographystyle:` for `--natbib` builds (e.g., `IEEEtran`, `plain`)
- [ ] `classoption:` as YAML list for document class options

## Figures

- [ ] Syntax: `![Caption text](path/to/image.pdf){width=\columnwidth}`
- [ ] LaTeX attributes in braces: `{width=...}`, `{height=...}`
- [ ] Labeled figures: `![Caption](path){#fig:label}` (with pandoc-crossref)

## Paragraphs

- [ ] Unwrapped: one long line per paragraph (editor handles visual wrapping)
- [ ] Blank line between paragraphs
- [ ] Never hard-wrap within a paragraph

## Pandoc Extensions

- [ ] Enable: `markdown+raw_tex+raw_attribute+fenced_divs+citations`
- [ ] `+raw_tex` allows raw LaTeX outside fenced blocks
- [ ] `+raw_attribute` enables `{=latex}` attribute on fenced blocks and spans
- [ ] `+citations` enables `[@key]` citation syntax

## Build Pipeline

- [ ] `--natbib` converts `[@key]` to `\cite{key}` (for BibTeX style files)
- [ ] `--citeproc` processes citations with CSL styles (format-independent)
- [ ] `--natbib` and `--citeproc` are mutually exclusive
- [ ] `--wrap=none` prevents Pandoc from inserting line breaks in generated `.tex`
- [ ] `--template=path` for venue-specific LaTeX templates
- [ ] Two-stage: Pandoc produces `.tex`, then latexmk compiles to `.pdf`
