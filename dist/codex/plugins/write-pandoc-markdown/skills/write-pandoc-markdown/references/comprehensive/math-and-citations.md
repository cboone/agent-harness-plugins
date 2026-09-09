# Math Delimiters and Citations in Pandoc Markdown

Comprehensive reference for inline and display math syntax, currency escaping, citation syntax, and the choice between `--natbib` and `--citeproc` processing modes. Based on the Pandoc User's Guide and BibTeX documentation.

## Inline Math

Use `$...$` for math within a sentence. Pandoc imposes stricter rules than LaTeX to avoid false positives from literal dollar signs in prose.

### Parsing rules

1. The opening `$` must have a non-space, non-newline character immediately to its right.
2. The closing `$` must have a non-space, non-newline character immediately to its left.
3. The closing `$` must not be immediately followed by a digit.

```markdown
Correct: The function $f(x) = x^2$ is continuous.
Correct: We define $n \ge 1$ as the iteration count.

Wrong:   The value $ x $ is positive.     (spaces around content)
Wrong:   The cost is $20,000$ per year.    (closing $ followed by digit)
```

### All standard LaTeX commands work inside delimiters

Pandoc does not interpret the contents of math delimiters. Everything between `$...$` passes through unchanged to the LaTeX processor. You can use `\frac`, `\sum`, `\mathbb`, custom macros, or any other LaTeX math command.

```markdown
The entropy is $H(\mathcal{P}) = -\sum_{i} p_i \log p_i$.
```

## Display Math

Use `$$...$$` for standalone equations. Display math must form its own paragraph: separate it from surrounding text with blank lines.

```markdown
The preceding paragraph ends here.

$$
H(\mathcal{P}) = -\sum_{i=1}^{n} p_i \log_2 p_i
$$

The following paragraph begins here.
```

### Rules for display math

1. The `$$...$$` block must be separated from surrounding text by blank lines (its own paragraph).
2. No blank lines are allowed between the opening `$$` and closing `$$`. A blank line inside the delimiters breaks the display math, causing Pandoc to interpret the content as two separate inline math expressions or plain text.
3. Content between the `$$` delimiters passes through unchanged to the LaTeX output.

### Opening and closing placement

Both styles work:

```markdown
<!-- Opening/closing on their own lines (preferred for readability) -->
$$
f(x) = \int_0^x g(t)\,\mathrm{d}t
$$

<!-- Opening/closing on the same lines as content -->
$$f(x) = \int_0^x g(t)\,\mathrm{d}t$$
```

### LaTeX note on `$$`

In pure LaTeX, `$$...$$` is discouraged in favor of `\[...\]` because the double-dollar syntax produces incorrect vertical spacing. In Pandoc Markdown, this concern does not apply: Pandoc converts `$$...$$` to `\[...\]` in the generated `.tex` file. Use `$$` in the Markdown source with confidence.

## The Currency Dollar Sign Problem

Pandoc uses `$` as a math delimiter. Currency amounts written with dollar signs risk accidental math parsing.

### Safe practice: always escape currency

```markdown
Correct: The breach cost \$438M in damages.
Correct: Users pay \$2.9M annually.
Correct: The budget is \$20,000 per quarter.

Wrong:   The breach cost $438M in damages.     (parsed as math)
Wrong:   Users pay $2.9M annually.              (parsed as math)
```

### Why `$20,000` usually survives

Pandoc's rule that the closing `$` cannot be followed by a digit means `$20,000` will not parse as math (the comma inside also helps). However, relying on this is fragile. A slight rewording like `$20,000-$30,000` could trigger unexpected math parsing. Escape all currency dollar signs to eliminate the risk entirely.

## Citation Syntax

Pandoc supports a rich citation syntax that works with both `--natbib` and `--citeproc` processing modes.

### Parenthetical citations

A citation key in square brackets produces a parenthetical citation.

```markdown
[@shannon1948]                  --> (Shannon, 1948)  or  [1]
[@shannon1948, p. 10]           --> (Shannon, 1948, p. 10)
[@shannon1948, pp. 10-15]       --> (Shannon, 1948, pp. 10-15)
[@shannon1948, Thm. 3.1]       --> (Shannon, 1948, Thm. 3.1)
```

With `--natbib`, `[@shannon1948]` becomes `\cite{shannon1948}` in the `.tex` output. With `--citeproc`, the citation is resolved inline using the specified CSL style.

### Textual citations (author in prose)

Use `@key` without brackets to place the author name in running text.

```markdown
@shannon1948 showed that entropy measures information content.
--> Shannon (1948) showed that entropy measures information content.
```

With `--natbib`, this becomes `\citet{shannon1948}`.

### Multiple citations

Separate multiple keys with semicolons inside a single bracket pair.

```markdown
[@shannon1948; @bonneau2012; @weir2009]
--> (Shannon, 1948; Bonneau, 2012; Weir et al., 2009)  or  [1, 5, 12]
```

With `--natbib`, this becomes `\cite{shannon1948,bonneau2012,weir2009}`.

### Suppress author

Use a minus sign before `@` to suppress the author name, showing only the year or number.

```markdown
Shannon [-@shannon1948] established the foundation.
--> Shannon (1948) established the foundation.
```

With `--natbib`, this becomes `\citeyear{shannon1948}`.

### Custom prefix text

Add text before the `@` inside the brackets.

```markdown
[See @shannon1948]              --> (See Shannon, 1948)
[cf. @shannon1948, p. 47]      --> (cf. Shannon, 1948, p. 47)
[e.g., @shannon1948; @weir2009] --> (e.g., Shannon, 1948; Weir et al., 2009)
```

### Locator terms

Pandoc recognizes standard locator terms that follow the citation key after a comma:

- `p.` / `pp.` (page/pages)
- `chap.` / `ch.` (chapter)
- `sec.` / `secs.` (section)
- `vol.` / `vols.` (volume)
- `Thm.` (theorem)
- `fig.` / `figs.` (figure)
- `eq.` / `eqs.` (equation)

```markdown
[@bonneau2012, sec. 4.2]
[@weir2009, fig. 3]
```

## natbib vs citeproc

Pandoc offers two mutually exclusive citation processing modes. You must choose one; using both simultaneously is an error.

### `--natbib` mode

Pandoc converts citation syntax to `\cite` family commands in the `.tex` output. BibTeX (or biber) resolves the references during the latexmk compilation step.

```text
[@key]      -->  \cite{key}
@key        -->  \citet{key}
[-@key]     -->  \citeyear{key}
```

**When to use:** When the target venue requires a specific `.bst` style file (IEEEtran, plain, acm, etc.). This is the standard approach for IEEE, ACM, and USENIX submissions.

**Requirements:**

- YAML frontmatter must include `bibliography:` (path to `.bib` file) and `bibliographystyle:` (e.g., `IEEEtran`).
- The `.bst` file must be accessible to BibTeX during compilation.
- latexmk handles the multiple compilation passes needed to resolve all references.

### `--citeproc` mode

Pandoc resolves all citations internally using CSL (Citation Style Language) files. The output contains fully formatted references, with no BibTeX step needed.

**When to use:** When producing format-independent output (HTML, DOCX, EPUB) or when you want Pandoc to handle everything without external tools. Also useful when a CSL style matches your target venue.

**Requirements:**

- YAML frontmatter must include `bibliography:` (path to `.bib`, `.json`, or `.yaml` file).
- Optionally specify `csl:` (path to `.csl` style file); defaults to Chicago author-date.

### Comparison

| Feature                | `--natbib`                      | `--citeproc`                     |
| ---------------------- | ------------------------------- | -------------------------------- |
| Output format          | LaTeX only                      | Any format                       |
| Style files            | `.bst` (BibTeX)                 | `.csl` (Citation Style Language) |
| Processing             | External (BibTeX/biber)         | Internal (Pandoc)                |
| Venue compatibility    | Excellent for IEEE, ACM, USENIX | Excellent for journals using CSL |
| Multi-pass compilation | Required (latexmk handles it)   | Not needed                       |

### Choosing a convention

Most CS conference venues (IEEE, ACM, USENIX) ship `.bst` style files and expect natbib-compatible bibliographies, so `--natbib` is the safer default for that audience. Journals with CSL styles or mixed-format output targets may prefer `--citeproc`. Pick one per project and declare the bibliography path in each paper's YAML frontmatter (`bibliography: path/to/refs.bib`).

## Common Mistakes

### Math delimiter spacing

```markdown
Wrong: $ f(x) = x^2 $        (spaces inside delimiters)
Right: $f(x) = x^2$           (no spaces inside delimiters)
```

### Unescaped currency

```markdown
Wrong: The cost was $2.5M.
Right: The cost was \$2.5M.
```

### Blank line in display math

```markdown
Wrong:
$$
x^2 + y^2 = z^2

\text{for integers } x, y, z
$$

Right:
$$
x^2 + y^2 = z^2
\text{ for integers } x, y, z
$$
```

### Missing semicolons in multiple citations

```markdown
Wrong: [@key1, @key2, @key3]        (commas between keys)
Right: [@key1; @key2; @key3]        (semicolons between keys)
```

### Mixing `--natbib` and `--citeproc`

These flags are mutually exclusive. Using both causes an error. Choose one and use it consistently for the entire document.
