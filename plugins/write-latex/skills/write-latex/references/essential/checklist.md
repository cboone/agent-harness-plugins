# LaTeX Math Essential Checklist

Quick reference for reviews. For detailed guidance, see `../comprehensive/`.

## Display Math

- [ ] Use `\[...\]` or `equation` for single-line displays, never `$$...$$`
- [ ] Use `align` or `align*` for multi-line equations, never `eqnarray`
- [ ] No blank line before `\[` or `\begin{equation}` (creates spurious `\par`)
- [ ] Use `\eqref{label}` for equation references (auto-parenthesizes)
- [ ] Punctuate displayed equations as part of the sentence (comma, period, etc.)
- [ ] No colon before a displayed equation that completes the sentence
- [ ] Number only important equations; use `equation*` or `\notag` for the rest

## Math Environments

- [ ] `align` / `align*` for multi-line with alignment points
- [ ] `gather` / `gather*` for multi-line centered (no alignment)
- [ ] `multline` / `multline*` for a single long equation that must break
- [ ] `split` inside `equation` for a sub-aligned block with one number
- [ ] Starred variants suppress equation numbers; `\notag` on individual lines

## Operators and Functions

- [ ] Standard functions in roman: `\sin`, `\log`, `\max`, `\det`, `\lim`, etc.
- [ ] Custom operators via `\DeclareMathOperator{\tr}{tr}`, not `\mathrm{tr}`
- [ ] Limits placement: `\DeclareMathOperator*` for operators with limits below

## Delimiters

- [ ] `\langle` / `\rangle` for angle brackets, not `<` / `>`
- [ ] `\lvert` / `\rvert` for absolute value, not bare `|`
- [ ] `\lVert` / `\rVert` for norms, not `||`
- [ ] Prefer `\bigl`/`\bigr` (manual sizing) over `\left`/`\right` for spacing
- [ ] Use `\DeclarePairedDelimiter` from mathtools for consistent delimiters

## Fractions

- [ ] Inline: slashed form `a/b` or `\tfrac{a}{b}`, not full `\frac{a}{b}`
- [ ] Display: `\frac{a}{b}` or `\dfrac{a}{b}` as appropriate
- [ ] Never `\over` (plain TeX; breaks amsmath internals)

## Ellipsis

- [ ] `\dots` as the generic command (auto-detects placement)
- [ ] `\dotsc` after commas: $a_1, a_2, \dotsc, a_n$
- [ ] `\dotsb` between binary operators: $a_1 + a_2 + \dotsb + a_n$
- [ ] `\dotsm` for multiplication: $a_1 a_2 \dotsm a_n$
- [ ] `\dotsi` for integrals
- [ ] Never manually type `...` in math mode

## ISO 80000-2 (if adopted)

- [ ] Variables: italic (default math mode)
- [ ] Constants (e, i, pi): upright via `\mathrm` or custom macros
- [ ] Vectors: bold italic via `\bm{v}` or `\boldsymbol{v}`
- [ ] Matrices: bold upright via `\mathbf{A}`
- [ ] Differential d: upright `\mathrm{d}` or custom `\du` macro
- [ ] Define macros: `\newcommand{\eu}{\ensuremath{\mathrm{e}}}`

## Tables

- [ ] Use booktabs: `\toprule`, `\midrule`, `\bottomrule` (never `\hline`)
- [ ] No vertical rules
- [ ] `@{}` at left and right edges: `\begin{tabular}{@{}lcr@{}}`
- [ ] `\cmidrule(lr){m-n}` for partial rules with trimming
- [ ] Caption above table, `\label` immediately after `\caption`

## Bibliography

- [ ] Protect capitals: `title = "A {K}rylov Method for {MATLAB}"`
- [ ] Multi-word surnames: `author = "Van Loan, Charles F."`
- [ ] Always include `doi` field for entries that have one
- [ ] Use MathSciNet standard journal abbreviation strings
- [ ] `\usepackage{backref}` for "cited on page X" in bibliography

## Figures

- [ ] PDF or EPS for line art and diagrams (vector); PNG/JPG for photos only
- [ ] Caption below figures (above tables)
- [ ] `\label{fig:name}` immediately after `\caption`
- [ ] Float specifier `[tbp]`, never `[H]` alone
- [ ] Use `subcaption` package for subfigures (not `subfigure` or `subfig`)

## Packages

- [ ] Load `mathtools` (supersedes and extends amsmath)
- [ ] Load `hyperref` near-last; configure via `\hypersetup{}`
- [ ] Load `cleveref` after `hyperref`
- [ ] `microtype` for character protrusion and font expansion
- [ ] `siunitx` for quantities with units and `S` column type

## Cross-References

- [ ] Use `\cref{label}` mid-sentence, `\Cref{label}` at sentence start
- [ ] Consistent label prefixes: `fig:`, `eq:`, `sec:`, `thm:`, `tbl:`
- [ ] `\crefrange{eq:first}{eq:last}` for ranges
- [ ] Load cleveref with `noabbrev` option if full names preferred

## Macros

- [ ] `\newcommand` (not `\def`): warns on name collision
- [ ] Semantic names: `\realnumbers` not `\R` (unless project convention)
- [ ] `\xspace` at end of text macros for automatic trailing space
- [ ] Separate macros file (`macros.tex`) for larger projects
- [ ] Document macros with inline comments

## Common Mistakes

- [ ] No `\def` -- use `\newcommand` or `\renewcommand`
- [ ] No `\centerline` -- use `\centering` or `center` environment
- [ ] No `\over`, `\atop`, `\choose` -- use `\frac`, `\binom`
- [ ] No `\bf`, `\it`, `\rm` -- use `\textbf`, `\textit`, `\textrm`
- [ ] No `$$...$$` -- use `\[...\]`
- [ ] No `eqnarray` -- use `align`
- [ ] No excessive `\left`/`\right` -- use manual sizing or `\DeclarePairedDelimiter`
- [ ] No `*` for multiplication -- use juxtaposition, `\cdot`, or `\times`
