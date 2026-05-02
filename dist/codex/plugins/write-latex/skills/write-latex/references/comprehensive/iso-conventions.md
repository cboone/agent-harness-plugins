
# ISO 80000-2 Mathematical Typesetting Conventions

Reference for the ISO 80000-2 standard governing the typesetting of mathematical symbols. This standard specifies when to use italic, upright, bold, and bold italic fonts in mathematical notation. Adopting it produces consistent, unambiguous documents and satisfies many journal style requirements. Based on the standard itself, Nicholas Higham's posts on ISO conventions, and the IEEE Math Typesetting Guide.

## Overview of ISO 80000-2

ISO 80000-2 (formerly ISO 31-11) is the international standard for mathematical notation. Its core principle is that font style carries semantic meaning:

- **Italic** denotes variables and quantities that can change.
- **Upright (roman)** denotes fixed entities: named functions, constants, units, labels, and descriptive subscripts.
- **Bold italic** denotes vector and tensor variables.
- **Bold upright** denotes fixed vector/matrix entities (less common; see below).

Most mathematics journals, IEEE, and many physics journals either require or recommend these conventions. Adopting them from the start avoids reformatting later.

## Variables: Italic

Variables are set in italic, which is the default for TeX math mode. This requires no special treatment. Single-letter variable names are conventional.

```latex
% Variables are italic by default
$x$, $y$, $z$, $t$, $n$, $k$
$f(x) = ax^2 + bx + c$
```

Multi-letter variable names should use `\mathit` to get proper italic kerning (rather than just typing letters in math mode, which treats each letter as a separate variable multiplied together):

```latex
% Wrong: interpreted as product of d, i, f, f
$diff = x - y$

% Correct: a single italic identifier
$\mathit{diff} = x - y$
```

In practice, prefer single-letter variables and use subscripts for disambiguation rather than multi-letter names.

## Constants: Upright Roman

Mathematical constants that have fixed, universal values are set in upright roman type. The three most important cases:

| Constant       | ISO rendering | LaTeX                                               |
| -------------- | ------------- | --------------------------------------------------- |
| Euler's number | e             | `\mathrm{e}`                                        |
| Imaginary unit | i             | `\mathrm{i}`                                        |
| Pi             | pi            | `\uppi` (with upgreek) or `\pi` (common compromise) |

### Macro definitions

Define macros in the preamble for consistency:

```latex
\newcommand{\eu}{\ensuremath{\mathrm{e}}}   % Euler's number
\newcommand{\iu}{\ensuremath{\mathrm{i}}}   % imaginary unit
```

The `\ensuremath` wrapper allows using the macro both in text mode and math mode.

Usage:

```latex
Euler's identity: $\eu^{\iu\pi} + 1 = 0$.

The complex number $z = a + b\iu$ has modulus $\lvert z \rvert$.
```

### Pi

The standard prescribes upright pi, but most mathematical typesetting uses italic pi out of long tradition. Both are acceptable. If you choose upright pi, the `upgreek` package provides `\uppi`:

```latex
\usepackage{upgreek}
% Then use \uppi in formulas
$A = \uppi r^2$
```

### Other upright items

Set these in upright roman as well:

- **Named functions**: `\sin`, `\cos`, `\log`, `\exp`, etc. (LaTeX does this automatically with the standard commands)
- **Units**: always upright. Use `siunitx` for proper typesetting: `\SI{9.81}{\metre\per\second\squared}`
- **Descriptive subscripts**: `E_{\mathrm{max}}`, `T_{\mathrm{eff}}`, `v_{\mathrm{rms}}`
- **Chemical elements and particles**: `\mathrm{H}_2\mathrm{O}`, `\mathrm{e}^-`
- **Abbreviations in subscripts**: `P_{\mathrm{in}}`, `P_{\mathrm{out}}`

## Differential Notation: Upright d

The differential operator d is a fixed symbol, not a variable, so ISO 80000-2 prescribes upright roman d. Define a macro:

```latex
\newcommand{\du}{\mathrm{d}}
```

### Spacing

Place a thin space (`\,`) between the integrand and the differential:

```latex
\[
  \int_0^\infty f(x)\,\du x
\]

\[
  \frac{\du f}{\du x} = \lim_{\Delta x \to 0}
    \frac{f(x + \Delta x) - f(x)}{\Delta x}
\]
```

### Partial derivatives

The partial derivative symbol `\partial` is traditionally italic in TeX. Some authors leave it italic; strict ISO compliance would make it upright, but the italic form is universally understood and widely accepted.

```latex
\[
  \frac{\partial f}{\partial x}
\]
```

### Multiple integrals

Maintain thin-space separation for each differential:

```latex
\[
  \iint_D f(x, y)\,\du x\,\du y
\]
```

## Vectors and Matrices

### Vectors: bold italic

ISO 80000-2 prescribes bold italic for vector quantities. Use the `bm` package:

```latex
\usepackage{bm}

% Vector variables
$\bm{v}$, $\bm{x}$, $\bm{F}$

% A vector equation
$\bm{F} = m\bm{a}$
```

`\bm` is preferred over `\boldsymbol` because it works correctly with more symbol types (including Greek letters). It is also preferred over `\mathbf`, which produces bold upright (appropriate for matrices, not vectors).

For a convenient shorthand, define:

```latex
\newcommand{\vect}[1]{\bm{#1}}
```

### Matrices: bold upright

Matrices (as fixed structural entities) are set in bold upright roman:

```latex
% Matrix names
$\mathbf{A}$, $\mathbf{B}$, $\mathbf{I}$ (identity matrix)

% A matrix equation
$\mathbf{A}\bm{x} = \bm{b}$
```

The distinction between `\mathbf` (bold upright, for matrices) and `\bm` (bold italic, for vectors) is the ISO-prescribed way to visually distinguish these entities.

### When to use which

| Entity                   | Font         | Command          |
| ------------------------ | ------------ | ---------------- |
| Scalar variable          | Italic       | `$x$`            |
| Vector variable          | Bold italic  | `$\bm{v}$`       |
| Matrix variable          | Bold upright | `$\mathbf{A}$`   |
| Unit vector              | Bold italic  | `$\bm{\hat{e}}$` |
| Named constant (scalar)  | Upright      | `$\mathrm{e}$`   |
| Named constant (vec/mat) | Bold upright | `$\mathbf{I}$`   |

### Package choice: bm vs manual

The `bm` package is the standard solution. It:

- Handles Greek letters, symbols, and accented characters
- Adapts to the surrounding math style (display, text, script)
- Is maintained and widely used

Avoid rolling your own bold-italic solution with `\pmb` (poor man's bold), which produces blurry output by overprinting.

## Functions: Roman Font

Named mathematical functions are always set in upright roman. LaTeX provides standard commands for common functions (`\sin`, `\cos`, `\log`, `\exp`, `\det`, `\dim`, `\lim`, `\max`, `\min`, `\sup`, `\inf`, `\gcd`, `\Pr`, `\ker`, `\hom`, `\deg`, `\arg`).

### Custom functions

For functions not in the standard set, use `\DeclareMathOperator` in the preamble:

```latex
\DeclareMathOperator{\Tr}{Tr}           % trace
\DeclareMathOperator{\rank}{rank}       % matrix rank
\DeclareMathOperator{\diag}{diag}       % diagonal matrix
\DeclareMathOperator{\sign}{sign}       % sign function
\DeclareMathOperator{\Var}{Var}         % variance
\DeclareMathOperator{\Cov}{Cov}         % covariance
\DeclareMathOperator*{\argmin}{arg\,min}  % with limits placement
\DeclareMathOperator*{\argmax}{arg\,max}
```

Never type function names as bare letters in math mode:

```latex
% Wrong: "log" in italic, bad spacing
$log(x)$

% Correct: upright, proper operator spacing
$\log(x)$
```

## Summary of Font Conventions

| Category               | Font         | Example                        |
| ---------------------- | ------------ | ------------------------------ |
| Variables              | Italic       | `$x$`, `$\alpha$`              |
| Named functions        | Upright      | `$\sin x$`, `$\log n$`         |
| Mathematical constants | Upright      | `$\mathrm{e}$`, `$\mathrm{i}$` |
| Descriptive subscripts | Upright      | `$E_{\mathrm{max}}$`           |
| Units                  | Upright      | `$\SI{5}{\kilogram}$`          |
| Differential d         | Upright      | `$\mathrm{d}x$`                |
| Vectors                | Bold italic  | `$\bm{v}$`                     |
| Matrices               | Bold upright | `$\mathbf{A}$`                 |
| Tensors                | Bold italic  | `$\bm{\sigma}$`                |

The key insight is that font style is not decoration; it is notation. A reader who sees an upright "e" knows it is Euler's number (2.71828...), not a variable. A reader who sees bold italic knows it is a vector, not a scalar. These distinctions reduce ambiguity and improve readability.
