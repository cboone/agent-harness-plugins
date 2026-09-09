# Common LaTeX Mistakes and Their Fixes

Each section presents a wrong/right pair with an explanation of why the wrong form causes problems.

## Display Math: `$$...$$` vs `\[...\]`

```latex
% WRONG: plain TeX display math
$$f(x) = x^2$$

% RIGHT: LaTeX display math
\[
  f(x) = x^2
\]
```

**Why it matters:** `$$...$$` is a plain TeX command that LaTeX inherited but never endorsed.
It produces incorrect vertical spacing because it does not account for the `\abovedisplayskip` and `\belowdisplayskip` lengths that LaTeX uses to adjust spacing based on context (for example, whether the preceding text line is short enough that the display could be raised).
It also interacts poorly with `fleqn` (flush-left equations) and cannot be detected by tools that check for proper LaTeX environments.

## Multi-line Equations: `eqnarray` vs `align`

```latex
% WRONG: eqnarray has incorrect spacing
\begin{eqnarray}
  a &=& b + c \\
  d &=& e + f
\end{eqnarray}

% RIGHT: align with correct spacing
\begin{align}
  a &= b + c \\
  d &= e + f
\end{align}
```

**Why it matters:** The `eqnarray` environment uses `\arraycolsep` spacing around the `=` sign, producing spaces that are too wide. Compare the space around `=` in `eqnarray` (default `\arraycolsep` is 5pt on each side, totaling 10pt) with `align` (which uses the correct `\thickmuskip` of about 5mu).
Additionally, `eqnarray` allows equations to overflow into the margin and overlap with equation numbers.
The `align` family from amsmath handles spacing, numbering, and overflow correctly.

## Centering: `\centerline` vs `\centering`

```latex
% WRONG: plain TeX command
\centerline{Some text or figure}

% RIGHT: LaTeX command
{\centering Some text or figure\par}

% RIGHT: LaTeX environment
\begin{center}
  Some text or figure
\end{center}
```

**Why it matters:** `\centerline` is a plain TeX command that does not respect LaTeX's list and minipage environments.
It can produce unexpected results inside `itemize`, `enumerate`, or `minipage`.
Inside a `figure` or `table` float, use `\centering` (without the `center` environment, which adds extra vertical space).

## Defining Commands: `\def` vs `\newcommand`

```latex
% WRONG: \def silently overwrites existing commands
\def\epsilon{\varepsilon}

% RIGHT: \newcommand errors on collision
\newcommand{\eps}{\varepsilon}

% RIGHT: \renewcommand when intentionally overriding
\renewcommand{\epsilon}{\varepsilon}
```

**Why it matters:** `\def` is a TeX primitive that performs no safety checks.
If you write `\def\bar{...}`, you silently destroy the existing `\bar` command with no warning.
`\newcommand` raises an error if the command name is already defined, alerting you to the conflict.
Use `\renewcommand` only when you deliberately intend to override an existing command and understand the consequences.

## Fractions: `\over` vs `\frac`

```latex
% WRONG: plain TeX infix notation
{a + b \over c + d}

% RIGHT: LaTeX \frac command
\frac{a + b}{c + d}
```

**Why it matters:** `\over` is an infix command from plain TeX that conflicts with amsmath's internal fraction handling.
When amsmath is loaded, `\over` triggers warnings and may produce incorrect output.
The `\frac` command (and its variants `\dfrac`, `\tfrac`, `\cfrac`) is the correct LaTeX interface.
The same applies to `\atop` (use nothing or `\genfrac`) and `\choose` (use `\binom`).

## Font Commands: `\bf`/`\it`/`\rm` vs `\textbf`/`\textit`/`\textrm`

```latex
% WRONG: old two-letter commands
{\bf bold text}
{\it italic text}

% RIGHT: NFSS-aware commands
\textbf{bold text}
\textit{italic text}
```

**Why it matters:** The two-letter font commands (`\bf`, `\it`, `\rm`, `\sl`, `\sc`, `\tt`, `\sf`) predate LaTeX2e's New Font Selection Scheme (NFSS).
They do not nest: `{\bf\it text}` does not produce bold italic; it just produces italic.
The modern commands (`\textbf`, `\textit`, etc.) compose correctly: `\textbf{\textit{text}}` produces bold italic.
In math mode, use `\mathbf`, `\mathrm`, `\mathit`, `\mathsf`, `\mathtt`, or `\boldsymbol`/`\bm`.

## Angle Brackets: `<`/`>` vs `\langle`/`\rangle`

```latex
% WRONG: relation symbols with wrong spacing
$<v, w>$

% RIGHT: delimiter symbols
$\langle v, w \rangle$
```

**Why it matters:** In math mode, `<` and `>` are classified as relation symbols (like `=` or `\leq`).
LaTeX inserts `\thickmuskip` (5mu) on each side, producing wider spacing than a delimiter should have.
`\langle` and `\rangle` are classified as opening and closing delimiters, respectively, with correct spacing.
The visual difference: `< v, w >` has noticeable gaps; `\langle v, w \rangle` looks tight and correct.

## Absolute Value: `|` vs `\lvert`/`\rvert`

```latex
% WRONG: ordinary symbol with ambiguous spacing
$|x|$

% RIGHT: paired delimiters with correct spacing
$\lvert x \rvert$

% BEST: mathtools paired delimiter
\DeclarePairedDelimiter{\abs}{\lvert}{\rvert}
$\abs{x}$       % auto-sized: \abs*{x}
```

**Why it matters:** The bare `|` character is classified as an ordinary symbol (class 0) in TeX's math spacing.
This means TeX does not know whether a given `|` is an opening or closing delimiter, so it cannot insert the correct spacing.
Consider: `|{-}x|` may produce different spacing than `\lvert{-}x\rvert`.
Using `\lvert`/`\rvert` (from amsmath) or a `\DeclarePairedDelimiter` macro gives correct delimiter spacing in all contexts.
The same issue applies to norms: use `\lVert`/`\rVert` instead of `||`.

## Ellipsis: Manual `...` vs `\dots` Family

```latex
% WRONG: three periods
$a_1, a_2, ... , a_n$

% RIGHT: semantic ellipsis
$a_1, a_2, \dotsc, a_n$    % dots with commas
$a_1 + a_2 + \dotsb + a_n$ % dots with binary operators
$a_1 a_2 \dotsm a_n$       % dots with multiplication
```

**Why it matters:** Manually typed periods produce dots at the baseline with incorrect inter-dot spacing.
The `\dots` family from amsmath places dots at the correct vertical position (low for commas, centered for binary operators) and with proper spacing.
The generic `\dots` command auto-detects placement based on the following token, but the explicit variants (`\dotsc`, `\dotsb`, `\dotsm`, `\dotsi`) are more reliable and self-documenting.

## Limits: `\limits` Abuse

```latex
% WRONG: forcing limits on a non-operator
\max\limits_{x \in S}   % \max already handles limits
f\limits_n               % f is not an operator

% RIGHT: use \DeclareMathOperator for custom operators
\DeclareMathOperator*{\argmax}{arg\,max}
$\argmax_{x \in S} f(x)$

% RIGHT: subscripts on ordinary symbols
$f_n(x)$
```

**Why it matters:** The `\limits` command is designed for large operators like `\sum`, `\prod`, and `\int` (and their custom equivalents defined with `\DeclareMathOperator*`).
Applying it to non-operator symbols disrupts TeX's spacing algorithms and produces results that look wrong at different font sizes.
For custom operators that should have limits placed below (in display mode), use `\DeclareMathOperator*`.

## Package Choice: amsmath vs mathtools

```latex
% SUBOPTIMAL: loading amsmath directly
\usepackage{amsmath}

% BETTER: mathtools loads and extends amsmath
\usepackage{mathtools}
```

**Why it matters:** The mathtools package is a strict superset of amsmath.
It loads amsmath internally and then fixes several documented bugs (for example, incorrect spacing in certain `gather` environments) while adding useful features: `\DeclarePairedDelimiter`, `\shortintertext`, `\coloneqq`, and more.
There is no downside to loading mathtools instead of amsmath, and it saves you from needing to work around known amsmath issues.

## Float Placement: `[H]` vs `[tbp]`

```latex
% WRONG: forces float to exact position
\begin{figure}[H]
  \includegraphics{plot.pdf}
  \caption{A plot.}
\end{figure}

% RIGHT: let LaTeX find the best position
\begin{figure}[tbp]
  \includegraphics{plot.pdf}
  \caption{A plot.}
\end{figure}
```

**Why it matters:** The `[H]` specifier (from the float package) forces the float to appear at the exact location in the source.
This prevents LaTeX from optimizing page layout, often causing large blank spaces, page breaks in awkward places, or floats that push text to the next page.
The `[tbp]` specifier tells LaTeX it may place the float at the top, bottom, or on a dedicated float page, allowing the algorithm to produce a balanced layout.
If you find yourself wanting `[H]`, that usually indicates the text needs restructuring: add a forward reference ("as shown in Figure~\ref{fig:plot}") and let the float go where LaTeX places it.

## Subfigure Packages: `subfigure`/`subfig` vs `subcaption`

```latex
% WRONG: legacy packages
\usepackage{subfigure}  % obsolete since 2005
\usepackage{subfig}     % unmaintained, conflicts with hyperref

% RIGHT: modern subcaption package
\usepackage{subcaption}

\begin{figure}[tbp]
  \begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\textwidth]{plot-a.pdf}
    \caption{First result.}
    \label{fig:result-a}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\textwidth]{plot-b.pdf}
    \caption{Second result.}
    \label{fig:result-b}
  \end{subfigure}
  \caption{Combined results showing both analyses.}
  \label{fig:results}
\end{figure}
```

**Why it matters:** The `subfigure` package has been obsolete since 2005 and conflicts with many modern packages.
The `subfig` package was its replacement but is itself unmaintained and has known conflicts with `hyperref` and `tocloft`.
The `subcaption` package is actively maintained, integrates with the standard `caption` package, and works correctly with `hyperref` and `cleveref`.

## Multiplication: Juxtaposition, Not Asterisk

```latex
% WRONG: asterisk for multiplication
$a * b$

% RIGHT: juxtaposition or explicit operator
$ab$, \quad $a \cdot b$, \quad $a \times b$
```

**Why it matters:** In mathematical typesetting, multiplication is denoted by juxtaposition ($ab$), a centered dot ($a \cdot b$), or a cross ($a \times b$). The asterisk `*` is a programming convention, not a mathematical one. In mathematics, `*` already has established meanings (convolution, dual space, conjugate, Kleene star) and should not be repurposed for ordinary multiplication.

## Sources

- Ensenbach, M. et al. _l2tabu: A List of Don'ts in LaTeX_. CTAN.
- Chen, E. _LaTeX Style Guide_. web.evanchen.cc.
- Higham, N. J. "Top Tips for New LaTeX Users." Blog post.
- Mittelbach, F. and Fischer, U. _The LaTeX Companion_. 3rd ed., 2024.
- Wright, J. _mathtools_ package documentation. CTAN.
