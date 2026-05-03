
# Recommended LaTeX Packages

A curated guide to essential LaTeX packages for academic and technical documents. Each section covers what the package does, why it matters, key usage patterns, and common pitfalls. The final section provides load order guidance. Based on Nicholas Higham's recommended packages post, package documentation, and community best practices.

## mathtools

**Purpose**: Extends amsmath with additional features and fixes.

**Load instead of amsmath directly.** The mathtools package loads amsmath internally and patches several of its shortcomings.

```latex
\usepackage{mathtools}
```

### Key features

**DeclarePairedDelimiter**: Define delimiter pairs with automatic or manual sizing (see the math typesetting reference for full details):

```latex
\DeclarePairedDelimiter{\abs}{\lvert}{\rvert}
\DeclarePairedDelimiter{\norm}{\lVert}{\rVert}
\DeclarePairedDelimiter{\ceil}{\lceil}{\rceil}
\DeclarePairedDelimiter{\floor}{\lfloor}{\rfloor}

% Usage: \abs{x}, \abs[\big]{x}, \abs*{\frac{a}{b}}
```

**coloneqq**: Correct "defined as" symbol with proper spacing:

```latex
$f(x) \coloneqq x^2 + 1$
```

**shortintertext**: Less vertical space than `\intertext` in align environments:

```latex
\begin{align}
  a &= b + c \\
  \shortintertext{where}
  b &= d + e
\end{align}
```

**Starred matrix environments**: Alignment control in matrices:

```latex
\begin{bmatrix*}[r]
  -1 &  3 \\
   2 & -4
\end{bmatrix*}
```

**Other useful additions**:

- `\mathclap`, `\mathllap`, `\mathrlap`: zero-width math boxes for precise alignment
- `\cramped`: force cramped math style (smaller exponents)
- `\MoveEqLeft`: align first line of multi-line equation when `&` cannot appear at the start

## cleveref

**Purpose**: Intelligent cross-references that automatically include the reference type (e.g., "Theorem 1" instead of just "1").

**Must load after hyperref.**

```latex
\usepackage[noabbrev]{cleveref}
```

### Key commands

```latex
\cref{eq:energy}       % "equation (1)" or "eq. (1)"
\Cref{eq:energy}       % "Equation (1)" or "Eq. (1)" (sentence start)
\cref{thm:main}        % "theorem 1"
\Cref{thm:main}        % "Theorem 1"
\crefrange{eq:a}{eq:c} % "equations (1) to (3)"
```

### The noabbrev option

The `noabbrev` option spells out reference names in full ("equation" instead of "eq.", "theorem" instead of "thm."). This is generally preferred in formal writing.

### Multiple references

Cleveref handles multiple references intelligently:

```latex
\cref{eq:a,eq:b,eq:c}  % "equations (1), (2), and (3)"
\cref{thm:a,lem:b}     % "theorem 1 and lemma 2"
```

### Why use it

- Eliminates inconsistency (no more mixing "Eq." and "equation" and "Eqn.")
- Automatically adapts when a label's type changes (e.g., from lemma to theorem)
- Handles ranges and lists of references
- Supports all standard environments (equation, theorem, figure, table, section, etc.)

## hyperref

**Purpose**: Clickable cross-references, URLs, and PDF metadata.

**Load near-last** in the preamble (before cleveref, which must come after).

```latex
\usepackage[colorlinks]{hyperref}
\hypersetup{
  pdftitle  = {Your Paper Title},
  pdfauthor = {Your Name},
  linkcolor = blue,
  citecolor = blue,
  urlcolor  = blue,
}
```

### Key options

| Option        | Effect                                               |
| ------------- | ---------------------------------------------------- |
| `colorlinks`  | Color link text instead of drawing boxes around them |
| `hidelinks`   | No visible indication of links (for print)           |
| `bookmarks`   | Generate PDF bookmarks (default: true)               |
| `breaklinks`  | Allow links to break across lines                    |
| `pdfusetitle` | Use `\title` and `\author` for PDF metadata          |

### Common pitfalls

- Loading hyperref too early causes conflicts with many packages
- Some packages (notably, cleveref) must load after hyperref
- The `\url` command from hyperref can break at awkward places; use xurl for better behavior

## siunitx

**Purpose**: Typeset numbers, units, and quantities consistently.

```latex
\usepackage{siunitx}
```

### Key commands

```latex
% Quantities (number + unit)
\SI{9.81}{\metre\per\second\squared}   % 9.81 m/s^2
\SI{300}{\kilo\hertz}                   % 300 kHz
\SI{2.998e8}{\metre\per\second}         % 2.998 x 10^8 m/s

% Units alone
\si{\kilogram\metre\per\second\squared} % kg m/s^2
\si{\micro\second}                      % μs

% Numbers alone (with grouping, uncertainty)
\num{12345.678}                         % 12 345.678
\num{1.234(5)}                          % 1.234 ± 0.005
\num{1.2e3}                             % 1.2 x 10^3
```

### Table column type

The `S` column type aligns numbers on the decimal point. See the tables reference for examples.

```latex
\begin{tabular}{@{}l S[table-format=3.2]@{}}
  \toprule
  {Item}   & {Value} \\
  \midrule
  Alpha    & 12.34   \\
  Beta     & 1.2     \\
  Gamma    & 123.45  \\
  \bottomrule
\end{tabular}
```

### Configuration

Set global options in the preamble:

```latex
\sisetup{
  per-mode          = symbol,      % use / instead of negative exponents
  group-separator   = {\,},        % thin space for digit grouping
  detect-all,                      % match surrounding font
}
```

## booktabs

**Purpose**: Professional-quality table rules.

```latex
\usepackage{booktabs}
```

See the [tables reference](tables.md) for comprehensive coverage. In brief:

- `\toprule`, `\midrule`, `\bottomrule` for the three standard rules
- `\cmidrule(lr){m-n}` for partial rules
- `\addlinespace` for vertical grouping
- Never use vertical rules

## enumitem

**Purpose**: Customize list environments (itemize, enumerate, description).

```latex
\usepackage{enumitem}
```

### Key options

**nosep**: Remove all vertical spacing between items (useful for tight lists in two-column layouts):

```latex
\begin{itemize}[nosep]
  \item First item
  \item Second item
\end{itemize}
```

**wide**: Remove left indent so items align with the surrounding text:

```latex
\begin{enumerate}[wide]
  \item First item
  \item Second item
\end{enumerate}
```

**Custom labels**: Change the numbering or bullet style:

```latex
\begin{enumerate}[label=(\roman*)]
  \item First   % (i)
  \item Second  % (ii)
  \item Third   % (iii)
\end{enumerate}

\begin{enumerate}[label=\alph*)]
  \item First   % a)
  \item Second  % b)
\end{enumerate}
```

**leftmargin**: Control the indentation:

```latex
\begin{itemize}[leftmargin=*]  % minimal left margin
  \item Compact item
\end{itemize}
```

### Global settings

Set defaults for all lists in the preamble:

```latex
\setlist{nosep}                          % all lists: no extra spacing
\setlist[enumerate]{label=\arabic*.}     % all enumerate: "1.", "2.", etc.
```

## url and xurl

**Purpose**: Typeset URLs with intelligent line-breaking.

```latex
% Basic URL support
\usepackage{url}

% Better line-breaking (breaks at hyphens, slashes, etc.)
\usepackage{xurl}
```

The `xurl` package extends `url` with additional breakpoints. It should be loaded before `hyperref`:

```latex
\usepackage{xurl}
\usepackage[colorlinks]{hyperref}
```

### Usage

```latex
See \url{https://example.com/very/long/path/to/resource}.
```

With `hyperref` loaded, `\url` commands automatically become clickable links.

## upref

**Purpose**: Ensure cross-reference numbers are always upright, even in theorem environments that use italic text.

```latex
\usepackage{upref}
```

Without upref, a reference like `\ref{eq:foo}` inside an italic environment produces an italic number. With upref, reference numbers are always upright roman, which is correct typographic practice.

This is a small package with no options. Just load it.

## upquote

**Purpose**: Use straight quotes in verbatim environments instead of curly quotes.

```latex
\usepackage{upquote}
```

Without upquote, verbatim text shows curly quotes (' '), which is incorrect for code listings. With upquote, you get straight quotes (' "), matching what programmers expect.

Load it whenever your document contains code listings or verbatim text.

## fancyvrb

**Purpose**: Enhanced verbatim environments with line numbering, framing, font control, and more.

```latex
\usepackage{fancyvrb}
```

### Key features

```latex
% Verbatim with line numbers
\begin{Verbatim}[numbers=left]
def hello():
    print("world")
\end{Verbatim}

% Verbatim with a frame
\begin{Verbatim}[frame=single]
some code here
\end{Verbatim}

% Custom font size
\begin{Verbatim}[fontsize=\small]
smaller code
\end{Verbatim}

% Read from file
\VerbatimInput{code/example.py}
```

### Inline verbatim

Fancyvrb provides `\Verb` as an alternative to `\verb` that works in more contexts (including footnotes and moving arguments):

```latex
The command \Verb|git commit -m "msg"| creates a commit.
```

## microtype

**Purpose**: Subliminal improvements to typography through character protrusion (optical margin alignment) and font expansion (micro-adjustments to character widths for better justification).

```latex
\usepackage{microtype}
```

**Load early** in the preamble (after font packages).

### What it does

- **Character protrusion**: Small characters (hyphens, periods, commas) extend slightly into the margin, making the visual margin more even
- **Font expansion**: Characters are stretched or compressed by tiny amounts (1-2%) to reduce the number of hyphenations and improve line-breaking

### Configuration

The defaults work well for most documents. For fine-tuning:

```latex
\usepackage[
  protrusion = true,
  expansion  = true,
  tracking   = true,   % letter-spacing for small caps
  kerning    = true,
  spacing    = true,
]{microtype}
```

### Impact

The changes are subtle, as individual adjustments are imperceptible. The cumulative effect, however, is noticeable: fewer overfull boxes, fewer bad line breaks, and a more polished appearance. It is one of the simplest ways to improve document quality.

## bm

**Purpose**: Bold math symbols that respect italic and other math styles.

```latex
\usepackage{bm}
```

The `\bm` command produces bold italic math, which is the ISO 80000-2 standard for vectors. See the [ISO conventions reference](iso-conventions.md) for details.

```latex
$\bm{v} = v_1 \bm{e}_1 + v_2 \bm{e}_2 + v_3 \bm{e}_3$
```

### Why not mathbf?

`\mathbf` produces bold upright, which is correct for matrices but not for vectors. `\bm` produces bold italic, matching the ISO convention for vector quantities.

### Why not pmb?

`\pmb` (poor man's bold) fakes boldness by overprinting. The result is visually blurry. Always use `\bm` instead.

## subcaption

**Purpose**: Modern subfigure and subtable support.

```latex
\usepackage{subcaption}
```

**Use instead of** the legacy `subfigure` and `subfig` packages, both of which are unmaintained and have compatibility issues with modern LaTeX.

### Basic usage

```latex
\begin{figure}[tbp]
  \centering
  \begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\linewidth]{fig-a}
    \caption{First result}
    \label{fig:results-a}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\linewidth]{fig-b}
    \caption{Second result}
    \label{fig:results-b}
  \end{subfigure}
  \caption{Experimental results}
  \label{fig:results}
\end{figure}
```

This produces figures labeled (a) and (b), with an overall caption. References work at both levels:

```latex
\cref{fig:results}   % "figure 1"
\cref{fig:results-a} % "figure 1a"
```

### Subtables

The same pattern works for tables:

```latex
\begin{table}[tbp]
  \caption{Performance comparison}
  \label{tab:performance}
  \centering
  \begin{subtable}[b]{0.48\textwidth}
    \centering
    \caption{Dataset A}
    \label{tab:performance-a}
    \begin{tabular}{@{}lc@{}}
      \toprule
      Method & Score \\
      \midrule
      X      & 0.92  \\
      Y      & 0.87  \\
      \bottomrule
    \end{tabular}
  \end{subtable}
  \hfill
  \begin{subtable}[b]{0.48\textwidth}
    \centering
    \caption{Dataset B}
    \label{tab:performance-b}
    \begin{tabular}{@{}lc@{}}
      \toprule
      Method & Score \\
      \midrule
      X      & 0.89  \\
      Y      & 0.84  \\
      \bottomrule
    \end{tabular}
  \end{subtable}
\end{table}
```

## Load Order Summary

Package load order matters in LaTeX. Conflicts arise when packages redefine the same commands. The following order avoids the most common issues:

```latex
% 1. Document class
\documentclass{article}

% 2. Font and encoding (if needed)
\usepackage[T1]{fontenc}

% 3. Microtype (after fonts, before most other packages)
\usepackage{microtype}

% 4. Math packages
\usepackage{mathtools}   % loads amsmath
\usepackage{amssymb}
\usepackage{bm}

% 5. Tables and figures
\usepackage{booktabs}
\usepackage{siunitx}
\usepackage{graphicx}
\usepackage{subcaption}

% 6. Lists
\usepackage{enumitem}

% 7. Code and verbatim
\usepackage{fancyvrb}
\usepackage{upquote}

% 8. URL handling (before hyperref)
\usepackage{xurl}

% 9. Cross-references and linking
\usepackage{upref}
\usepackage[colorlinks]{hyperref}  % load near-last
\usepackage[noabbrev]{cleveref}    % must be after hyperref
```

### Critical ordering rules

1. **microtype** after font packages, before most others
2. **xurl** before hyperref
3. **hyperref** near-last (after almost everything else)
4. **cleveref** after hyperref (this is mandatory; cleveref patches hyperref internals)
5. **siunitx** before or after booktabs (no dependency), but before hyperref

### When in doubt

If you encounter a package conflict, the solution is almost always to move one of the two packages. Check the package documentation for load order requirements. The `hyperref` package is the most common source of ordering issues because it redefines many internal LaTeX commands.
