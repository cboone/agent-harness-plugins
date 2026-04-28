
# Tables in LaTeX with Booktabs

Comprehensive reference for creating professional tables in LaTeX using the booktabs package. Based on the booktabs philosophy of clean, readable tables; Nicholas Higham's posts on tables; and the Chicago Manual of Style (17th edition) guidance on table formatting.

## The Booktabs Philosophy

The guiding principles for professional tables:

1. **Never use vertical rules.** Vertical lines add clutter without improving readability.
2. **Never use double rules.** Double horizontal lines are a legacy of typewriter-era formatting.
3. **Use only three horizontal rules** in a simple table: one above the header, one below the header, and one at the bottom.
4. **Add space, not lines.** If rows need visual grouping, use extra vertical space (via `\addlinespace`) rather than horizontal rules.

These conventions match the practice of every major scientific publisher and style guide.

## Basic Structure

A minimal booktabs table:

```latex
\begin{table}[tbp]
  \caption{Comparison of password strength estimators}
  \label{tab:estimators}
  \centering
  \begin{tabular}{@{}lcc@{}}
    \toprule
    Estimator  & Accuracy (\%) & Runtime (ms) \\
    \midrule
    zxcvbn     & 72.3          & 12           \\
    PCFG       & 68.1          & 340          \\
    Neural     & 81.7          & 56           \\
    \bottomrule
  \end{tabular}
\end{table}
```

### The three rules

| Command       | Purpose                    | Thickness  |
| ------------- | -------------------------- | ---------- |
| `\toprule`    | Above the column headers   | Thickest   |
| `\midrule`    | Below the column headers   | Medium     |
| `\bottomrule` | At the bottom of the table | Thickest   |

The `\toprule` and `\bottomrule` are slightly thicker than `\midrule` by default. This visual hierarchy helps the reader's eye distinguish the header from the data and the data from what follows the table.

### Edge removal with @{}

The `@{}` column specifier removes the default padding at the left and right edges of the table. Always use it:

```latex
% Correct: no extra padding at edges
\begin{tabular}{@{}lcc@{}}

% Wrong: default padding makes the rules overhang
\begin{tabular}{lcc}
```

Without `@{}`, the horizontal rules (`\toprule`, `\midrule`, `\bottomrule`) extend slightly beyond the text, which looks untidy.

## Partial Rules with cmidrule

Use `\cmidrule` for rules that span only some columns. This is useful for grouping related columns under a spanning header.

```latex
\begin{tabular}{@{}lcccc@{}}
  \toprule
  & \multicolumn{2}{c}{Training} & \multicolumn{2}{c}{Testing} \\
  \cmidrule(lr){2-3} \cmidrule(lr){4-5}
  Model  & Accuracy & Loss & Accuracy & Loss \\
  \midrule
  LSTM   & 94.2     & 0.18 & 91.7     & 0.24 \\
  GRU    & 93.8     & 0.19 & 91.3     & 0.25 \\
  \bottomrule
\end{tabular}
```

### Trim parameters

The parenthetical arguments trim whitespace from the ends of the rule to prevent adjacent `\cmidrule` commands from touching:

| Parameter  | Effect                               |
| ---------- | ------------------------------------ |
| `(l)`      | Trim from the left end               |
| `(r)`      | Trim from the right end              |
| `(lr)`     | Trim from both ends                  |
| `(l{2pt})` | Trim a specific amount from the left |

The most common usage is `(lr)` to separate adjacent group rules:

```latex
\cmidrule(lr){2-3} \cmidrule(lr){4-5}
```

Without trimming, the two rules would merge into what looks like a single rule spanning columns 2 through 5, defeating the purpose of grouping.

## Column Types

### Standard column types

| Type       | Alignment     | Notes                                      |
| ---------- | ------------- | ------------------------------------------ |
| `l`        | Left          | Default for text columns                   |
| `c`        | Center        | Good for short numeric or categorical data |
| `r`        | Right         | Rarely used as primary alignment           |
| `p{width}` | Left, wrapped | For columns with long text                 |

### Decimal alignment with siunitx

The `S` column type from siunitx aligns numbers on their decimal point:

```latex
\usepackage{siunitx}

\begin{tabular}{@{}l S[table-format=2.1] S[table-format=3.0]@{}}
  \toprule
  {Method}  & {Accuracy (\%)} & {Runtime (ms)} \\
  \midrule
  zxcvbn    & 72.3             & 12             \\
  PCFG      & 68.1             & 340            \\
  Neural    & 81.7             & 56             \\
  \bottomrule
\end{tabular}
```

Key points for the `S` column type:

- Wrap non-numeric header text in braces: `{Method}`, `{Accuracy (\%)}`
- Use `table-format` to specify the expected number format (digits before and after the decimal point)
- Numbers are automatically aligned on the decimal separator

## Caption Placement

### Caption above the table

Place the caption above the table, not below. This is the convention prescribed by the Chicago Manual of Style and followed by IEEE, ACM, and most scientific publishers. The rationale: readers encounter the caption first, understand what they are about to see, and then read the data.

```latex
\begin{table}[tbp]
  \caption{Results of the password strength evaluation}
  \label{tab:results}
  \centering
  \begin{tabular}{@{}lcc@{}}
    % ...
  \end{tabular}
\end{table}
```

Note the contrast with figures, where the caption goes below. The difference is conventional: tables are read top-down (caption first, then data), while figures are scanned visually before reading the description.

### Short caption for list of tables

If the caption is long, provide a short version for the list of tables:

```latex
\caption[Password strength results]{%
  Results of evaluating three password strength estimation
  methods on the RockYou dataset, showing accuracy and runtime}
```

## Label Placement

Place `\label` immediately after `\caption`. If `\label` appears before `\caption` or outside the float, the reference number will be wrong.

```latex
\begin{table}[tbp]
  \caption{Summary statistics}
  \label{tab:summary}       % Correct: immediately after \caption
  \centering
  \begin{tabular}{@{}lc@{}}
    % ...
  \end{tabular}
\end{table}
```

## Float Positioning

### Recommended specifiers

Use `[tbp]` (top, bottom, page) as the default float placement:

```latex
\begin{table}[tbp]
```

This gives LaTeX maximum flexibility to place the float where it fits best. LaTeX's float algorithm, while not perfect, produces good results when given room to work.

### Specifiers to avoid

- **`[h]`**: "Here" placement. LaTeX ignores it when the float does not fit. It almost never produces good results.
- **`[H]`** (from the float package): Forces placement at the exact location. This breaks the float mechanism entirely and often pushes content off the page or leaves large gaps.
- **`[!]`**: Override internal float limits. Rarely needed and often a sign of deeper layout issues.

If a float is not appearing where you want it, the solution is usually to adjust the surrounding text or add more content, not to force the float position.

## Additional Spacing

### addlinespace

Use `\addlinespace` to add vertical space between groups of rows, instead of adding more horizontal rules:

```latex
\begin{tabular}{@{}lcc@{}}
  \toprule
  Category & Method & Score \\
  \midrule
  Offline  & PCFG   & 68.1  \\
  Offline  & Markov & 65.4  \\
  \addlinespace
  Online   & zxcvbn & 72.3  \\
  Online   & Neural & 81.7  \\
  \bottomrule
\end{tabular}
```

An optional argument controls the space size: `\addlinespace[0.5em]`.

## Complete Minimal Example

A self-contained example combining all best practices:

```latex
\documentclass{article}
\usepackage{booktabs}
\usepackage{siunitx}

\begin{document}

\begin{table}[tbp]
  \caption{Password cracking performance by attack type}
  \label{tab:cracking-performance}
  \centering
  \begin{tabular}{@{}l S[table-format=2.1] S[table-format=6.0] c@{}}
    \toprule
    {Attack}         & {Success (\%)} & {Guesses} & {Complexity} \\
    \midrule
    Dictionary       & 23.4           & 100000    & Low          \\
    Rule-based       & 41.2           & 500000    & Medium       \\
    Markov chain     & 38.7           & 350000    & Medium       \\
    \addlinespace
    PCFG             & 52.1           & 1000000   & High         \\
    Neural           & 58.3           & 1000000   & High         \\
    \bottomrule
  \end{tabular}
\end{table}

\end{document}
```

This example demonstrates:

- Caption above the table with `\label` immediately after
- `[tbp]` float placement
- `@{}` edge removal
- Three-rule structure with `\toprule`, `\midrule`, `\bottomrule`
- `\addlinespace` for visual grouping
- `S` column for decimal-aligned numbers
- Non-numeric headers wrapped in braces
- No vertical rules
