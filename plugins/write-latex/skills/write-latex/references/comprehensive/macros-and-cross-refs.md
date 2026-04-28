
# Macro Design and Cross-References

## Part 1: Macro Design

### Basic Syntax

```latex
\newcommand{\name}[n]{definition}
```

- `\name` is the command name (must begin with `\`).
- `[n]` is the number of parameters (0 to 9). Omit the brackets for zero parameters.
- `{definition}` is the replacement text. Use `#1`, `#2`, ..., `#9` for parameters.

```latex
% Zero parameters
\newcommand{\realnumbers}{\mathbb{R}}

% One parameter
\newcommand{\norm}[1]{\lVert #1 \rVert}

% Two parameters
\newcommand{\innerprod}[2]{\langle #1, #2 \rangle}
```

### Semantic Names

Choose macro names that describe the *concept*, not the *appearance*.
This makes the source readable and allows you to change the presentation later without rewriting every usage.

```latex
% GOOD: semantic names
\newcommand{\realnumbers}{\mathbb{R}}
\newcommand{\integers}{\mathbb{Z}}
\newcommand{\expectedvalue}[1]{\mathbb{E}\!\left[#1\right]}
\newcommand{\probability}[1]{\Pr\!\left(#1\right)}
\newcommand{\transpose}{\mathsf{T}}

% ACCEPTABLE: short names when a project convention is established
% (document the convention in a macros file header comment)
\newcommand{\R}{\mathbb{R}}
\newcommand{\Z}{\mathbb{Z}}
\newcommand{\E}[1]{\mathbb{E}\!\left[#1\right]}
```

The key principle: if a reviewer asks you to change how real numbers are typeset (from `\mathbb{R}` to `\mathbf{R}`, say), you edit one line instead of hundreds.

### The `\xspace` Package

Text-mode macros that expand to words need trailing space handling.
Without `\xspace`, the macro swallows any space after it:

```latex
\usepackage{xspace}

% Without \xspace: "LaTeX is great" becomes "LaTeXis great"
\newcommand{\latex}{LaTeX}     % bad: \latex is great -> LaTeXis great

% With \xspace: automatic space insertion
\newcommand{\latex}{\LaTeX\xspace}  % good: \latex is great -> LaTeX is great
```

`\xspace` inspects the next token: if it is a letter or space, it inserts a space; if it is punctuation (comma, period, closing brace), it does not.

**Note:** `\xspace` is only for text-mode macros. Math-mode macros do not need it because TeX handles spacing in math mode through its atom classification system.

### `\providecommand`

Use `\providecommand` when you want to define a macro only if it does not already exist.
This avoids errors when loading files that may define the same macro:

```latex
% Define only if not already defined
\providecommand{\eps}{\varepsilon}
```

This is useful in shared macro files that multiple documents `\input`.
If the main document already defines `\eps`, the `\providecommand` is silently ignored.

### `\renewcommand`

Use `\renewcommand` when you intentionally want to override an existing command:

```latex
% Override LaTeX's default epsilon with the curly variant
\renewcommand{\epsilon}{\varepsilon}

% Override the default QED symbol
\renewcommand{\qedsymbol}{$\blacksquare$}
```

`\renewcommand` raises an error if the command does *not* already exist, which is the opposite of `\newcommand`.
This safety check ensures you are actually overriding something.

### Separate Macros File

For projects with more than a handful of macros, collect them in a dedicated file:

```latex
% In macros.tex:
% === Number sets ===
\newcommand{\realnumbers}{\mathbb{R}}
\newcommand{\naturals}{\mathbb{N}}
\newcommand{\integers}{\mathbb{Z}}

% === Operators ===
\DeclareMathOperator{\tr}{tr}
\DeclareMathOperator*{\argmin}{arg\,min}
\DeclareMathOperator*{\argmax}{arg\,max}

% === Delimiters ===
\DeclarePairedDelimiter{\abs}{\lvert}{\rvert}
\DeclarePairedDelimiter{\norm}{\lVert}{\rVert}
\DeclarePairedDelimiter{\ceil}{\lceil}{\rceil}
\DeclarePairedDelimiter{\floor}{\lfloor}{\rfloor}

% In the main document preamble:
\input{macros}
```

### Documenting Macros

Add comments explaining the purpose, parameters, and expected context of each macro:

```latex
% Entropy of a random variable.
% #1: the random variable (e.g., X, Y)
% Usage: $\entropy{X}$ produces H(X)
\newcommand{\entropy}[1]{H\!\left(#1\right)}

% Conditional entropy.
% #1: target variable, #2: conditioning variable
% Usage: $\condentropy{X}{Y}$ produces H(X | Y)
\newcommand{\condentropy}[2]{H\!\left(#1 \mid #2\right)}
```

This is especially important in multi-author projects where not everyone is familiar with every macro.

### The `\ensuremath` Wrapper

`\ensuremath` allows a math-mode macro to be used safely in text mode:

```latex
\newcommand{\realnumbers}{\ensuremath{\mathbb{R}}}

% Now works in both contexts:
The set of real numbers \realnumbers{} is uncountable.  % text mode
Let $x \in \realnumbers$.                               % math mode
```

Without `\ensuremath`, using `\realnumbers` outside of math mode produces an error.
Use this for macros that might appear in headings, captions, or running text.

**Caveat:** `\ensuremath` adds a small overhead. For macros that are only ever used in math mode, it is unnecessary.

## Part 2: Cross-References with cleveref

The `cleveref` package automates reference formatting.
Instead of manually writing "Theorem 2.1", you write `\cref{thm:main}` and cleveref determines the type and number automatically.

### Loading cleveref

cleveref must be loaded **after** hyperref (if hyperref is used), because cleveref patches hyperref's reference mechanism:

```latex
% Correct load order
\usepackage{hyperref}
\usepackage{cleveref}

% With full names instead of abbreviations
\usepackage[noabbrev]{cleveref}
```

The `noabbrev` option produces "Theorem" instead of "Thm.", "equation" instead of "eq.", and so on.

### Basic Usage: `\cref` and `\Cref`

```latex
% Mid-sentence (lowercase type name)
As shown in \cref{thm:main}, the bound is tight.
% Output: "As shown in theorem 1, the bound is tight."

% Sentence start (capitalized type name)
\Cref{thm:main} establishes the upper bound.
% Output: "Theorem 1 establishes the upper bound."
```

**Rule:** Use `\cref` for mid-sentence references and `\Cref` at the start of a sentence. Never start a sentence with `\cref` (lowercase).

### Ranges with `\crefrange`

```latex
\crefrange{eq:first}{eq:last}
% Output: "equations (1) to (5)" or "eqs. (1) to (5)"

\Crefrange{fig:a}{fig:d}
% Output: "Figures 1a to 1d"
```

### Multiple References

cleveref automatically sorts, compresses, and groups multiple references:

```latex
\cref{eq:a,eq:b,eq:c,eq:d}
% Output: "eqs. (1) to (4)" if contiguous

\cref{eq:a,eq:c,thm:main}
% Output: "eqs. (1) and (3) and theorem 1"

\cref{fig:a,fig:b,fig:c}
% Output: "figures 1a to 1c"
```

### Consistent Label Prefixes

Adopt a consistent naming scheme for labels across the entire document.
cleveref uses these to determine the reference type, but consistent prefixes also make the source readable:

| Prefix  | Environment          | Example              |
|---------|---------------------|----------------------|
| `fig:`  | figure               | `\label{fig:arch}`   |
| `tbl:`  | table                | `\label{tbl:results}`|
| `eq:`   | equation, align      | `\label{eq:loss}`    |
| `sec:`  | section              | `\label{sec:method}` |
| `thm:`  | theorem              | `\label{thm:main}`   |
| `lem:`  | lemma                | `\label{lem:bound}`  |
| `def:`  | definition           | `\label{def:space}`  |
| `cor:`  | corollary            | `\label{cor:tight}`  |
| `rem:`  | remark               | `\label{rem:note}`   |
| `alg:`  | algorithm            | `\label{alg:train}`  |
| `lst:`  | listing              | `\label{lst:code}`   |
| `app:`  | appendix section     | `\label{app:proofs}` |

### Equation References: `\cref` vs `\eqref`

For equations specifically, both `\cref` and `\eqref` work:

```latex
\cref{eq:main}     % Output: "eq. (1)" or "equation (1)"
\eqref{eq:main}    % Output: "(1)" -- just the number in parentheses
```

Use `\cref` when you want the type name ("equation (1)").
Use `\eqref` when the context makes the type obvious and you just need the number.

### Unbreakable Spaces and cleveref

With `\ref`, you must manually insert an unbreakable space to prevent a line break between the type name and the number:

```latex
% Without cleveref: manual ~ required
Theorem~\ref{thm:main}
Figure~\ref{fig:arch}
Section~\ref{sec:method}
```

With `\cref`, unbreakable spaces are inserted automatically.
You do not need to add `~` when using `\cref` or `\Cref`:

```latex
% With cleveref: ~ is handled internally
\cref{thm:main}   % correct, no ~ needed
\Cref{fig:arch}    % correct, no ~ needed
```

### Customizing cleveref Output

You can customize the format for specific reference types:

```latex
% Make theorem references bold
\crefformat{theorem}{#2\textbf{Theorem~#1}#3}

% Customize equation format
\crefformat{equation}{#2(#1)#3}

% Custom names for amsthm environments
\crefname{proposition}{proposition}{propositions}
\Crefname{proposition}{Proposition}{Propositions}
```

## Part 3: Combining Macros and Cross-References

### Macros That Reference Labels

When building macros that produce cross-references, always use the cleveref commands:

```latex
% A macro that states a result and references it
\newcommand{\bytheorem}[1]{(by \cref{#1})}

% Usage:
The bound follows \bytheorem{thm:main}.
```

### Theorem Environments with Custom Macros

When defining theorem-like environments with amsthm, set up the corresponding cleveref names:

```latex
\usepackage{amsthm}
\usepackage{cleveref}

\newtheorem{theorem}{Theorem}[section]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{corollary}[theorem]{Corollary}

\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}

\theoremstyle{remark}
\newtheorem{remark}[theorem]{Remark}

% cleveref picks up the names from \newtheorem automatically,
% but you can override if needed:
\crefname{corollary}{corollary}{corollaries}
\Crefname{corollary}{Corollary}{Corollaries}
```

## Sources

- Mittelbach, F. and Fischer, U. *The LaTeX Companion*. 3rd ed., 2024.
- Niederberger, T. *cleveref* package documentation. CTAN.
- Downes, M. and Beeton, B. *Short Math Guide for LaTeX*. AMS, 2017.
- Wright, J. *mathtools* package documentation. CTAN.
