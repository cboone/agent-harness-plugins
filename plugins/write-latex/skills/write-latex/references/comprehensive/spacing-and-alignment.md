
# Spacing and Alignment in LaTeX Equations

## Standard Math Spaces

LaTeX provides six built-in spacing commands for fine-tuning mathematical expressions.
The fundamental unit is the *mu* (math unit): 1 mu = 1/18 em at the current math font size.

| Command   | Width  | Usage                                          |
|-----------|--------|-------------------------------------------------|
| `\,`      |  3 mu  | Thin space; most common fine-tuning space       |
| `\:`      |  4 mu  | Medium space; rarely needed                     |
| `\;`      |  5 mu  | Thick space; between adjacent display formulas  |
| `\!`      | -3 mu  | Negative thin space; for pulling symbols closer |
| `\quad`   | 18 mu  | 1 em; standard separator in display math        |
| `\qquad`  | 36 mu  | 2 em; large separator between formulas          |

In running text, `\quad` and `\qquad` serve as logical separators between conditions or between a formula and its qualifier:

```latex
f(x) = x^2, \qquad x \in \mathbb{R}.
```

## Common Spacing Patterns

### Integrals: Thin Space Before the Differential

Always insert `\,` before the upright differential to visually separate the integrand from the `d`:

```latex
% Good
\int_0^1 f(x) \, \mathrm{d}x

% Bad: no space before d
\int_0^1 f(x)\mathrm{d}x
```

For multiple integrals, the thin space applies before each differential:

```latex
\iint_D f(x,y) \, \mathrm{d}x \, \mathrm{d}y
```

### Set Notation: `\mid` vs `|`

Use `\mid` (or `\mathrel{|}`) for the "such that" bar in set-builder notation.
The bare `|` is an ordinary symbol with no surrounding space; `\mid` is a relation with proper padding:

```latex
% Good: \mid gives correct relation spacing
\{ x \in \mathbb{R} \mid x > 0 \}

% Bad: | has no relational spacing
\{ x \in \mathbb{R} | x > 0 \}
```

For conditioning in probability, the same rule applies:

```latex
P(A \mid B) = \frac{P(B \mid A) \, P(A)}{P(B)}
```

### Thin Space in Set Braces

When using the full set-builder notation with `\{` and `\}`, add thin spaces inside the braces for readability:

```latex
\{\, x \in \mathbb{R} \mid x > 0 \,\}
```

### Function Application

No space between function name and parenthesized argument is the default and correct:

```latex
% Correct: no space
\sin(x), \quad \log(n), \quad f(x)
```

## Knuth's @ Active Character Technique

In *Digital Typography*, Knuth describes making `@` an active character that inserts 1 mu of space.
This allows extremely fine adjustments:

```latex
% In the preamble (book-length projects only):
\mathcode`@="8000
{\catcode`@=\active \gdef@{\mkern1mu}}

% Usage:
\sqrt{@\log n}    % tiny nudge inside the radical
```

**When to use:** Only in book-length projects or final polish of critical displays. For papers and theses, the standard spacing commands suffice. Do not reach for this technique in everyday work.

## Phantom Commands

Phantom commands create invisible boxes with the dimensions of their argument.
They are essential for aligning content across separate equations.

| Command      | Width | Height | Depth |
|-------------|-------|--------|-------|
| `\phantom`   | Yes   | Yes    | Yes   |
| `\hphantom`  | Yes   | No     | No    |
| `\vphantom`  | No    | Yes    | Yes   |

### Vertical Alignment with `\vphantom`

Use `\vphantom` to equalize the height of delimiters across aligned equations when the content differs in height:

```latex
\begin{align}
  a &= \left( \vphantom{\frac{1}{2}} x + y \right) \\
  b &= \left( \frac{1}{2} + z \right)
\end{align}
```

Without the `\vphantom`, the parentheses in the first line would be shorter than in the second, creating a visual mismatch.

### Horizontal Alignment with `\hphantom`

Use `\hphantom` to reserve horizontal space without rendering content:

```latex
\begin{align}
  x &= a + b + c \\
    &= \hphantom{a + {}} d + e
\end{align}
```

This aligns `d` directly under `b` by inserting invisible space the width of `a +`.

## Intertext: Text Between Aligned Equations

### `\intertext` (amsmath)

Inserts a line of text between rows of an `align` environment without breaking the alignment:

```latex
\begin{align}
  a &= b + c \label{eq:first} \\
  \intertext{Substituting equation~\eqref{eq:first} into the result,}
  d &= e + f \label{eq:second}
\end{align}
```

`\intertext` adds full paragraph spacing above and below the text.

### `\shortintertext` (mathtools)

When the text is short (a few words), `\intertext` adds too much vertical space.
The mathtools package provides `\shortintertext` with tighter spacing:

```latex
\usepackage{mathtools}  % in preamble

\begin{align}
  a &= b + c \\
  \shortintertext{where}
  b &= x^2.
\end{align}
```

**Rule of thumb:** Use `\shortintertext` for single words or short phrases ("where", "and so", "since").
Use `\intertext` for full sentences.

## Manual Line Breaking in Aligned Environments

### Adjusting Vertical Space with `\\[length]`

The `\\` command in `align` accepts an optional length for vertical adjustment:

```latex
\begin{align}
  a &= b + c \\[6pt]   % extra space before next line
  d &= e + f \\[-3pt]   % tighter space before next line
  g &= h + i
\end{align}
```

Common uses:

- Add space after a line containing tall symbols (`\sum`, `\frac`) to avoid crowding
- Reduce space between closely related lines for visual grouping
- Separate logical groups of equations without starting a new environment

### Breaking Long Equations

For a single equation that is too long for one line, use `multline` (amsmath):

```latex
\begin{multline}
  f(x) = a_0 + a_1 x + a_2 x^2 + a_3 x^3 \\
       + a_4 x^4 + a_5 x^5 + a_6 x^6
\end{multline}
```

The first line is flush left, the last line flush right, and middle lines are centered.
For an aligned multi-line equation with a single equation number, use `split` inside `equation`:

```latex
\begin{equation}
\begin{split}
  f(x) &= a_0 + a_1 x + a_2 x^2 \\
       &\quad + a_3 x^3 + a_4 x^4
\end{split}
\end{equation}
```

## No Blank Lines Before Display Math

Never leave a blank line immediately before `\[`, `\begin{equation}`, or any display math environment.
A blank line in LaTeX is equivalent to `\par`, which ends the current paragraph and introduces vertical spacing before the display.

```latex
% WRONG: blank line creates a \par, adding unwanted vertical space
Consider the function

\[
  f(x) = x^2.
\]

% CORRECT: display math continues the paragraph
Consider the function
\[
  f(x) = x^2.
\]
```

The visual difference is subtle in some document classes but pronounced in others.
The blank line inserts `\parskip` plus `\abovedisplayskip`, creating a gap that is visibly larger than intended.

**The same rule applies after display math.** Do not leave a blank line between the closing `\]` and the next sentence if the sentence continues the same paragraph.

## Sources

- Downes, M. and Beeton, B. *Short Math Guide for LaTeX*. AMS, 2017.
- Higham, N. J. "Typesetting Mathematics According to the ISO Standard." Blog post, 2020.
- Knuth, D. E. *Digital Typography*. Chapter on fine-tuning mathematical spacing.
- Wright, J. *mathtools* package documentation. CTAN.
