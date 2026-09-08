# Raw LaTeX in Pandoc Markdown

Comprehensive reference for embedding raw LaTeX content in Pandoc Markdown documents. Covers fenced block syntax, inline raw spans, the `+raw_tex` extension, theorem environments, and common pitfalls. Based on the Pandoc User's Guide and R Markdown Cookbook.

## When to Use Raw LaTeX

Pandoc Markdown is expressive, but some LaTeX constructs have no Markdown equivalent. Use raw LaTeX for:

- **Theorem environments:** `\begin{definition}...\end{definition}`, `\begin{theorem}...\end{theorem}`, `\begin{proof}...\end{proof}`
- **Complex tables:** multi-row, multi-column, or heavily formatted tables that exceed Pandoc's pipe or grid table syntax
- **Package-specific commands:** TikZ figures, algorithm environments (`algorithmic`, `algorithm2e`), code listings (`lstlisting`), custom float types
- **Fine-grained formatting:** `\vspace`, `\pagebreak`, `\noindent`, column balancing (`\balance`), manual float placement overrides
- **Cross-references:** `\cref`, `\eqref`, `\nameref` (via raw inline spans)

Do not use raw LaTeX for things Pandoc handles natively (bold, italic, lists, basic tables, headings, citations). Unnecessary raw LaTeX reduces portability and makes the source harder to read.

## Fenced Block Syntax

The primary way to include raw LaTeX is with a fenced code block using the `{=latex}` attribute.

### Correct syntax

````markdown
```{=latex}
\begin{definition}[Password Space]\label{def:password-space}
A \emph{password space} $\pspace$ is the set of all strings
accepted by the verification mechanism.
\end{definition}
```
````

The `=` before `latex` is critical. It tells Pandoc that this is raw content in the LaTeX format, not a code block to be displayed.

### Wrong syntax (common mistakes)

````markdown
<!-- WRONG: creates a syntax-highlighted code block, not raw LaTeX -->

```{latex}
\begin{theorem}
...
\end{theorem}
```

<!-- WRONG: same problem, just a different syntax for code highlighting -->

```latex
\begin{theorem}
...
\end{theorem}
```

<!-- CORRECT: the equals sign makes it raw LaTeX -->

```{=latex}
\begin{theorem}
...
\end{theorem}
```
````

The difference is fundamental:

- ` ```{latex} ` and ` ```latex ` produce a `<pre><code class="latex">` block in HTML or a `\begin{Shaded}\begin{Highlighting}` block in LaTeX. The content is displayed as source code.
- ` ```{=latex} ` produces raw LaTeX that is compiled by the LaTeX engine. The content is executed, not displayed.

### Block placement

Raw LaTeX blocks must be separated from surrounding Markdown by blank lines, just like any other block element.

````markdown
The preceding paragraph ends here.

```{=latex}
\begin{theorem}\label{thm:main}
For all $x \in \pspace$, the survival function $S(x)$ is monotonically decreasing.
\end{theorem}
```

The following paragraph begins here.
````

## Inline Raw Spans

For single LaTeX commands within a paragraph, use inline raw spans.

### Syntax

```markdown
As shown in `\cref{sec:introduction}`{=latex}, the framework defines five spaces.
```

The backtick-delimited content is the raw LaTeX command. The `{=latex}` attribute tells Pandoc to pass it through unchanged.

### Common uses

```markdown
<!-- Cross-references -->

`\cref{sec:model}`{=latex}
`\Cref{fig:architecture}`{=latex}
`\eqref{eq:entropy}`{=latex}

<!-- Inline formatting -->

`\textsc{Small Caps Text}`{=latex}
`\textsuperscript{1}`{=latex}

<!-- Custom macros -->

`\pspace`{=latex}
`\aspace`{=latex}
```

### Requirements

The `+raw_attribute` Pandoc extension must be enabled. In the project Makefiles, this is included in the format specification:

```text
-f markdown+raw_tex+raw_attribute+fenced_divs+citations
```

## The `+raw_tex` Extension

The `+raw_tex` extension allows Pandoc to recognize raw LaTeX commands that appear directly in the Markdown source, outside any fenced block or inline span.

### How it works

With `+raw_tex` enabled, Pandoc passes through any LaTeX command it encounters (anything starting with `\` followed by a command name).

```markdown
<!-- With +raw_tex, this works without {=latex} fences -->

\begin{definition}
A password space is the set of all accepted strings.
\end{definition}

<!-- LaTeX commands in running text also pass through -->

This is \textbf{bold} via raw LaTeX.
```

### Comparison with `{=latex}` blocks

| Feature             | `+raw_tex` (unfenced)         | `{=latex}` blocks                               |
| ------------------- | ----------------------------- | ----------------------------------------------- |
| Explicitness        | Implicit; Pandoc guesses      | Explicit; clearly marked                        |
| Parsing reliability | Can be ambiguous              | Always reliable                                 |
| Readability         | Cleaner for simple commands   | More verbose                                    |
| Recommended for     | Simple commands, environments | Complex blocks, all cases where clarity matters |

### When `+raw_tex` can cause problems

Pandoc sometimes misinterprets LaTeX commands as text or vice versa. This is rare but possible when:

- A LaTeX command name collides with something Pandoc parses differently.
- A backslash appears in a context Pandoc interprets as an escape character.
- The command spans multiple lines in a way that confuses the Pandoc parser.

### Project convention

The project enables both extensions: `+raw_tex+raw_attribute`. For theorem environments and complex blocks, always use explicit `{=latex}` fences. For inline cross-references, use inline raw spans (`` `\cref{}`{=latex} ``). The `+raw_tex` extension provides a safety net for any raw LaTeX that might appear outside fenced blocks.

## Theorem Environments in Pandoc Markdown

Academic papers frequently need theorem, definition, lemma, and proof environments. These have no Pandoc Markdown equivalent and must use raw LaTeX blocks.

### Basic pattern

````markdown
```{=latex}
\begin{definition}[Password Space]\label{def:password-space}
A \emph{password space} $\pspace$ is the set of all strings
accepted by the verification mechanism.
\end{definition}
```
````

### Environment types

The available environments depend on what the LaTeX preamble defines. Typical definitions (often kept in a project-wide macros file such as `macros.tex`):

````markdown
```{=latex}
\begin{definition}[Name]\label{def:label}
Content with $math$ and \emph{emphasis}.
\end{definition}
```

```{=latex}
\begin{theorem}[Name]\label{thm:label}
Statement of the theorem.
\end{theorem}
```

```{=latex}
\begin{lemma}\label{lem:label}
Statement of the lemma.
\end{lemma}
```

```{=latex}
\begin{proposition}\label{prop:label}
Statement of the proposition.
\end{proposition}
```

```{=latex}
\begin{proof}
Proof content. Ends with a QED symbol automatically.
\end{proof}
```
````

### Content inside theorem environments

Inside a raw LaTeX block, use LaTeX syntax for everything. Pandoc does not process the content.

````markdown
```{=latex}
\begin{theorem}[Survival Bound]\label{thm:survival-bound}
For any password $x \in \pspace$ with probability $p_x$ under
distribution $\mathcal{D}$, the survival function satisfies
\begin{equation}\label{eq:survival}
  S(x) \ge 1 - \frac{G(p_x)}{|\aspace|}
\end{equation}
where $G(p_x)$ is the cumulative guessing count and $|\aspace|$
is the size of the attack space.
\end{theorem}
```
````

Key points:

- Use `\emph{}` instead of `*...*` for emphasis.
- Use `\cite{}` instead of `[@key]` for citations.
- Use `\ref{}` or `\cref{}` instead of Pandoc cross-references.
- Use `\textbf{}` instead of `**...**` for bold.
- Math delimiters (`$...$` and `\begin{equation}`) work normally because they are standard LaTeX.

## Complex Tables

When Pandoc's table syntax cannot express your table layout, use a raw LaTeX block.

````markdown
```{=latex}
\begin{table}[t]
\centering
\caption{Comparison of password strength metrics.}\label{tbl:metrics}
\begin{tabular}{lccr}
\toprule
Metric & Composability & Monotonicity & Computation \\
\midrule
Shannon entropy & No  & Yes & $O(n)$ \\
Min-entropy     & No  & Yes & $O(n)$ \\
Guessing curve  & Yes & Yes & $O(n \log n)$ \\
\bottomrule
\end{tabular}
\end{table}
```
````

For tables that Pandoc can handle (simple grids, pipes), prefer Pandoc syntax for readability and portability.

## TikZ Figures

TikZ diagrams must be placed in raw LaTeX blocks. A project-wide `tikz-styles.tex` typically holds shared style definitions (e.g. a colorblind-safe palette).

````markdown
```{=latex}
\begin{figure}[t]
\centering
\input{figures/architecture.tikz}
\caption{System architecture showing the five spaces.}\label{fig:architecture}
\end{figure}
```
````

For externally generated figures (PDF, PNG), prefer Pandoc's native image syntax:

```markdown
![System architecture showing the five spaces.](figures/architecture.pdf){width=\columnwidth}
```

## Caveats and Troubleshooting

### Raw LaTeX is invisible in non-LaTeX output

When converting to HTML, DOCX, or EPUB, raw LaTeX blocks and spans are silently dropped. The content simply vanishes. This is acceptable for projects that only produce LaTeX PDF, but it means the Markdown source is not truly format-independent.

### `\input` and `\include` commands

Pandoc does not follow `\input` or `\include` commands. If your raw LaTeX block uses `\input{file.tex}`, Pandoc passes the command through unchanged, and it resolves during LaTeX compilation. This works fine for the two-stage build pipeline, but:

- Pandoc cannot analyze or transform the included content.
- Errors in the included file will appear during the latexmk step, not the Pandoc step.

### Deeply nested raw blocks

Avoid placing raw LaTeX blocks inside other Pandoc constructs (blockquotes, list items, divs). The nesting can confuse the Pandoc parser, leading to unexpected output. If you need a theorem inside a list item, restructure the document to avoid the nesting.

### Mixing Pandoc and LaTeX syntax inside raw blocks

Inside a `{=latex}` block, everything is raw LaTeX. Pandoc syntax does not work.

````markdown
<!-- WRONG: Pandoc Markdown inside raw LaTeX -->

```{=latex}
\begin{theorem}
This uses **bold** and [@citation].
\end{theorem}
```

<!-- RIGHT: LaTeX syntax inside raw LaTeX -->

```{=latex}
\begin{theorem}
This uses \textbf{bold} and \cite{citation}.
\end{theorem}
```
````

### Blank lines inside raw LaTeX blocks

Blank lines inside a raw LaTeX block can sometimes cause Pandoc to split the block. While this is usually handled correctly with the `{=latex}` attribute, if you encounter unexpected behavior, remove unnecessary blank lines or use `%` comment lines as spacers.

````markdown
```{=latex}
\begin{proof}
First paragraph of the proof.
%
Second paragraph of the proof.
\end{proof}
```
````
