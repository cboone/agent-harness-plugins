
# Math Typesetting in LaTeX

Comprehensive reference for mathematical typesetting covering display and inline math, environments, numbering, operators, delimiters, fractions, ellipsis, and subscripts/superscripts. Based on the AMS Short Math Guide, IEEE Math Typesetting Guide, Evan Chen's style guide, and Herbert Voss's Mathmode document.

## Display vs Inline Math

### Inline math

Use `$...$` for math that flows within a sentence. Keep inline expressions short and simple.

```latex
The function $f(x) = x^2$ is continuous on $\mathbb{R}$.
```

### Display math

Use `\[...\]` for standalone equations that do not need a number. Never use `$$...$$` for display math. The double-dollar syntax is a plain TeX holdover that produces incorrect vertical spacing and interacts badly with fleqn mode.

```latex
% Correct
\[
  f(x) = \int_0^x g(t)\,\mathrm{d}t
\]

% Wrong: never use $$
$$f(x) = \int_0^x g(t)\,\mathrm{d}t$$
```

### When to break out of inline

Move an expression to display mode when it:

- Contains fractions (use slashed form `a/b` if staying inline)
- Contains sums or integrals with limits
- Is long enough to crowd the surrounding text
- Needs its own equation number

### Line break placement in formulas

When breaking a long equation across lines, the placement of the break differs between display and inline contexts:

- **Display mode:** Break *before* the relation or binary operator, so the operator starts the new line and signals continuation. This is the standard convention in `split` and `align` environments (the `&` goes before `=`).
- **Inline text:** If a formula must break within running text, the break goes *after* the operator. The operator stays with the left fragment to signal that more is coming.

```latex
% Display: break BEFORE the equals sign
\begin{equation}
\begin{split}
  f(x) &= a_0 + a_1 x + a_2 x^2 \\
       &= g(x) + h(x)
\end{split}
\end{equation}
```

## Core Environments

Load `mathtools` (which loads `amsmath` automatically) to access all of these environments.

### equation

A single numbered equation. Use the starred variant `equation*` when no number is needed (equivalent to `\[...\]`).

```latex
\begin{equation}
  E = mc^2
  \label{eq:energy}
\end{equation}
```

### align

Multiple equations aligned at a common point (typically `&` before `=`). Each line gets its own number unless suppressed.

```latex
\begin{align}
  f(x) &= x^2 + 2x + 1 \label{eq:f} \\
  g(x) &= x^3 - 1       \label{eq:g}
\end{align}
```

Use `align*` when no line needs a number. Use `\notag` on individual lines to suppress their numbers while keeping others.

### gather

Multiple equations centered, with no alignment point. Each line is numbered.

```latex
\begin{gather}
  x + y = 1 \\
  x - y = 3
\end{gather}
```

### multline

A single long equation broken across lines. The first line is left-aligned, the last is right-aligned, and middle lines are centered. Only one equation number (on the last line by default).

```latex
\begin{multline}
  p(x) = x^8 + x^7 + x^6 + x^5 \\
       + x^4 + x^3 + x^2 + x + 1
\end{multline}
```

### split

A sub-environment used inside `equation` (or similar) when you need alignment within a single equation number.

```latex
\begin{equation}
  \begin{split}
    H(X \mid Y) &= -\sum_{y} p(y) \sum_{x} p(x \mid y) \log p(x \mid y) \\
                &= -\sum_{x,y} p(x,y) \log p(x \mid y)
  \end{split}
  \label{eq:conditional-entropy}
\end{equation}
```

### aligned and gathered

These are analogous to `align` and `gather` but are sub-environments that fit inside an outer environment or inside `\[...\]`. They do not produce equation numbers on their own.

```latex
\[
  \left\{
  \begin{aligned}
    x + y &= 1 \\
    x - y &= 3
  \end{aligned}
  \right.
\]
```

### When to use each

| Goal                                       | Environment          |
| ------------------------------------------ | -------------------- |
| Single numbered equation                   | `equation`           |
| Single unnumbered equation                 | `equation*` or `\[`  |
| Multiple aligned equations, each numbered  | `align`              |
| Multiple aligned equations, none numbered  | `align*`             |
| Multiple centered equations, each numbered | `gather`             |
| Multiple centered equations, none numbered | `gather*`            |
| One long equation split across lines       | `multline`           |
| Aligned lines sharing one number           | `equation` + `split` |
| Alignment as a sub-expression              | `aligned`            |
| Centering as a sub-expression              | `gathered`           |

### notag vs nonumber

Both suppress the equation number on a single line. Prefer `\notag` (the amsmath name) over `\nonumber` (the plain LaTeX name). They are functionally identical, but `\notag` is the recommended form in the AMS documentation.

```latex
\begin{align}
  a &= b + c \notag \\
  d &= e + f \label{eq:second-line}
\end{align}
```

## Equation Numbering and References

### label and eqref

Place `\label` immediately after (or on the same line as) the equation it labels. Reference equations with `\eqref`, which automatically wraps the number in parentheses.

```latex
\begin{equation}
  a^2 + b^2 = c^2
  \label{eq:pythagoras}
\end{equation}

By \eqref{eq:pythagoras}, we have\dots
```

This produces "By (1), we have..." with the number hyperlinked (when using hyperref).

### tag and tag\*

Override the automatic number with a custom label. `\tag` wraps the label in parentheses; `\tag*` prints it without parentheses.

```latex
\begin{equation}
  E = mc^2 \tag{Einstein}
\end{equation}

\begin{equation}
  F = ma \tag*{N2}
\end{equation}
```

## Operators

### Standard operators

LaTeX provides these as commands so they appear in upright roman: `\sin`, `\cos`, `\tan`, `\log`, `\ln`, `\exp`, `\det`, `\dim`, `\ker`, `\lim`, `\max`, `\min`, `\sup`, `\inf`, `\gcd`, `\Pr`, `\arg`, `\deg`, `\hom`.

Always use the command form; never type the name directly in math italic:

```latex
% Correct
$\log n$

% Wrong: "log" appears in italic
$log n$
```

### DeclareMathOperator

Define custom operators in the preamble. They render in upright roman with correct spacing.

```latex
\DeclareMathOperator{\Tr}{Tr}
\DeclareMathOperator{\rank}{rank}
\DeclareMathOperator{\diag}{diag}
```

The starred variant `\DeclareMathOperator*` places subscripts and superscripts as limits (below and above in display mode):

```latex
\DeclareMathOperator*{\argmin}{arg\,min}
\DeclareMathOperator*{\argmax}{arg\,max}
```

```latex
% In display mode, "x" appears below "arg min"
\[
  \hat{\theta} = \argmin_{x \in \mathcal{X}} L(x)
\]
```

### operatorname

For one-off operators that do not justify a preamble declaration:

```latex
$\operatorname{softmax}(z_i)$
```

The starred variant `\operatorname*` gives limit placement.

## Delimiters

### Named delimiters

Use named commands for delimiters that have no direct keyboard equivalent:

| Delimiter      | Left command | Right command |
| -------------- | ------------ | ------------- |
| Angle brackets | `\langle`    | `\rangle`     |
| Absolute value | `\lvert`     | `\rvert`      |
| Norm           | `\lVert`     | `\rVert`      |
| Floor          | `\lfloor`    | `\rfloor`     |
| Ceiling        | `\lceil`     | `\rceil`      |

Never use `<` and `>` for angle brackets; they produce relation symbols with wrong spacing.

### Manual sizing vs left/right

Prefer manual sizing commands over `\left`/`\right`. The `\left`/`\right` pair:

- Adds an extra `\mathinner` atom, producing incorrect horizontal spacing
- Cannot break across lines
- Sometimes chooses a size that is too large or too small

The manual sizing commands from smallest to largest:

| Left     | Right    | Size    |
| -------- | -------- | ------- |
| `\bigl`  | `\bigr`  | Small   |
| `\Bigl`  | `\Bigr`  | Medium  |
| `\biggl` | `\biggr` | Large   |
| `\Biggl` | `\Biggr` | Largest |

There are also middle variants (`\bigm`, `\Bigm`, etc.) for delimiters that act as binary relations (like `\mid` in set-builder notation).

```latex
% Good: manual sizing, correct spacing
\[
  P\bigl(X \in A \bigm| Y = y\bigr)
\]

% Acceptable but often problematic
\[
  P\left(X \in A \;\middle|\; Y = y\right)
\]
```

### DeclarePairedDelimiter (mathtools)

Define delimiter pairs once and get automatic or manual sizing:

```latex
\DeclarePairedDelimiter{\abs}{\lvert}{\rvert}
\DeclarePairedDelimiter{\norm}{\lVert}{\rVert}
\DeclarePairedDelimiter{\ceil}{\lceil}{\rceil}
\DeclarePairedDelimiter{\floor}{\lfloor}{\rfloor}
\DeclarePairedDelimiter{\inner}{\langle}{\rangle}
```

Usage:

```latex
% Unstarred: no auto-sizing (plain delimiters)
$\abs{x}$

% Starred: \left/\right auto-sizing
$\abs*{\frac{a}{b}}$

% Manual sizing via optional argument (recommended)
$\abs[\big]{x}$
$\norm[\Big]{\sum_i x_i}$
```

The optional-argument form is the best approach: it avoids the spacing issues of `\left`/`\right` while still scaling the delimiters.

## Fractions

### frac, dfrac, tfrac

- `\frac{a}{b}`: adapts to context (display-size in display mode, text-size in inline mode)
- `\dfrac{a}{b}`: forces display-size. Use in display mode when `\frac` looks too small inside an outer fraction or matrix.
- `\tfrac{a}{b}`: forces text-size. Use in display mode when a fraction should remain compact.

### Inline conventions

In inline text, prefer the slashed form or `\tfrac` to avoid expanding the line height:

```latex
% Good: slashed form in inline text
The ratio $a/b$ satisfies $a/b > 1$.

% Also acceptable
The ratio $\tfrac{a}{b}$ satisfies\dots

% Bad: full-size fraction disrupts line spacing
The ratio $\frac{a}{b}$ satisfies\dots
```

**Never use stacked fractions inside exponents or subscripts.** Stacking in these positions produces tiny, nearly unreadable numerals. Always use the slashed form:

```latex
% WRONG: stacked fraction in exponent creates tiny numbers
$e^{\frac{n(n+1)(2n+1)}{3}}$

% CORRECT: slashed form is readable
$e^{n(n+1)(2n+1)/3}$
```

This is one of the most common typographic errors mathematicians make when they control their own typesetting.

### cfrac

For continued fractions, use `\cfrac` (not nested `\frac` calls), which provides correct vertical centering:

```latex
\[
  \cfrac{1}{1 + \cfrac{1}{1 + \cfrac{1}{1 + \cdots}}}
\]
```

## Ellipsis

### Automatic detection with dots

The `\dots` command from amsmath examines the next token and chooses the correct ellipsis style automatically. Use it as your default.

```latex
$a_1, a_2, \dots, a_n$        % detects comma: baseline dots
$a_1 + a_2 + \dots + a_n$     % detects +: centered dots
```

### Explicit variants

When `\dots` cannot determine the context (or when you want to be explicit), use the semantic variants:

| Command  | Usage                              | Placement |
| -------- | ---------------------------------- | --------- |
| `\dotsc` | After commas                       | Baseline  |
| `\dotsb` | Between binary operators/relations | Centered  |
| `\dotsm` | Between multiplication signs       | Centered  |
| `\dotsi` | Between integrals                  | Centered  |

```latex
$a_1, a_2, \dotsc, a_n$
$a_1 + a_2 + \dotsb + a_n$
$A_1 A_2 \dotsm A_n$
$\int_{a_1}^{b_1} \int_{a_2}^{b_2} \dotsi \int_{a_n}^{b_n}$
```

Never use `\ldots` or `\cdots` directly; the semantic commands are clearer and more portable.

## Subscripts and Superscripts

### Readability

Keep subscript/superscript nesting shallow. Two levels is the practical maximum. If you need more, introduce intermediate notation or a separate definition.

```latex
% Acceptable: two levels
$x_{i_k}$

% Too deep: hard to read, hard to typeset well
$x_{i_{j_k}}$

% Better: define intermediate notation
Let $m = i_j$.  Then $x_{m_k}$\dots
```

### substack

For multi-line subscripts on sums or products, use `\substack` (from amsmath):

```latex
\[
  \sum_{\substack{0 \le i \le m \\ 0 \le j \le n}} a_{ij}
\]
```

### Spacing and grouping

- Always brace multi-character subscripts and superscripts: `x_{ij}`, not `x_ij`.
- For a subscript that is a word or abbreviation, use `\mathrm`: `E_{\mathrm{max}}`, not `E_{max}` (which renders as the product of italic m, a, x).
- Place limits on large operators (sums, products, integrals) using `_` and `^`; they appear below/above in display mode and to the side in inline mode by default.

## Mathtools Enhancements

The `mathtools` package extends amsmath with several useful features beyond `\DeclarePairedDelimiter` (covered above).

### coloneqq

The correct symbol for "is defined as" with proper spacing:

```latex
$f(x) \coloneqq x^2 + 1$
```

This is preferred over `\mathrel{:=}` or `:=` because it produces a vertically centered colon with correct relation spacing.

### prescript

Place superscripts and subscripts to the left of a symbol:

```latex
\[
  \prescript{14}{6}{\mathbf{C}}
\]
```

### shortintertext

A variant of `\intertext` with less vertical space. Use it inside `align` environments when you need a short text annotation between lines:

```latex
\begin{align}
  a &= b + c \\
  \shortintertext{where}
  b &= d + e
\end{align}
```

### Starred matrix environments

Mathtools provides `bmatrix*`, `pmatrix*`, etc., with an optional alignment argument:

```latex
\[
  \begin{bmatrix*}[r]
    -1 &  2 \\
     3 & -4
  \end{bmatrix*}
\]
```

The `[r]` aligns entries to the right, which is useful for matrices with mixed positive and negative entries.
