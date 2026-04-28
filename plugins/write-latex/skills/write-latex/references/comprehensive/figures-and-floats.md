
# Figures, Graphics, and Float Placement

## Graphics Format Rules

Choose the format based on the content type:

| Content Type                 | Format     | Reason                                           |
| ---------------------------- | ---------- | ------------------------------------------------ |
| Diagrams, plots, line art    | PDF or EPS | Vector formats scale without pixelation          |
| Photographs, screenshots     | PNG or JPG | Raster is acceptable for continuous-tone images  |
| Generated plots (matplotlib) | PDF        | Always export as vector; never screenshot a plot |
| TikZ/PGF figures             | Compiled   | Generate directly in LaTeX or export to PDF      |

**Never use bitmaps (PNG, JPG, BMP, GIF) for plots, diagrams, or any content with lines, text, or geometric shapes.**
Bitmapped plots look blurry when printed or zoomed, and they inflate file size compared to vector equivalents.

When including external graphics:

```latex
\usepackage{graphicx}

% Set search paths so \includegraphics doesn't need full paths
\graphicspath{{images/}{figures/}{plots/}}

% Include without file extension (LaTeX picks the best format)
\includegraphics[width=0.8\textwidth]{performance-comparison}
```

Omitting the file extension allows LaTeX to select the optimal format if multiple versions exist (PDF over PNG, for example).

## The subcaption Package

The `subcaption` package is the modern, maintained way to create subfigures.
It replaces the obsolete `subfigure` and unmaintained `subfig` packages.

### Basic Subfigure Layout

```latex
\usepackage{subcaption}

\begin{figure}[tbp]
  \begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\textwidth]{result-baseline.pdf}
    \caption{Baseline model.}
    \label{fig:result-baseline}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.48\textwidth}
    \centering
    \includegraphics[width=\textwidth]{result-proposed.pdf}
    \caption{Proposed model.}
    \label{fig:result-proposed}
  \end{subfigure}
  \caption{Comparison of baseline and proposed models on the test dataset.}
  \label{fig:comparison}
\end{figure}
```

Key points:

- Each `subfigure` environment takes an optional alignment argument (`[b]` for bottom-aligned, `[t]` for top-aligned) and a mandatory width.
- Use `\hfill` between subfigures to distribute remaining horizontal space evenly.
- Each subfigure gets its own `\caption` and `\label` for individual references.
- The parent `figure` gets an overall `\caption` and `\label`.
- References: `\cref{fig:result-baseline}` produces "Figure 1a"; `\cref{fig:comparison}` produces "Figure 1".

### Using `\subcaptionbox`

For simpler cases, `\subcaptionbox` is more compact:

```latex
\begin{figure}[tbp]
  \centering
  \subcaptionbox{Baseline.\label{fig:baseline}}
    [0.48\textwidth]{\includegraphics[width=0.45\textwidth]{baseline.pdf}}
  \hfill
  \subcaptionbox{Proposed.\label{fig:proposed}}
    [0.48\textwidth]{\includegraphics[width=0.45\textwidth]{proposed.pdf}}
  \caption{Overall comparison.}
  \label{fig:overall}
\end{figure}
```

### Three or More Subfigures

For three subfigures in a row, use one-third widths:

```latex
\begin{figure}[tbp]
  \centering
  \begin{subfigure}[b]{0.31\textwidth}
    \centering
    \includegraphics[width=\textwidth]{plot-a.pdf}
    \caption{Dataset A.}
    \label{fig:plot-a}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.31\textwidth}
    \centering
    \includegraphics[width=\textwidth]{plot-b.pdf}
    \caption{Dataset B.}
    \label{fig:plot-b}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.31\textwidth}
    \centering
    \includegraphics[width=\textwidth]{plot-c.pdf}
    \caption{Dataset C.}
    \label{fig:plot-c}
  \end{subfigure}
  \caption{Results across all three datasets.}
  \label{fig:all-datasets}
\end{figure}
```

For a 2x2 grid, separate rows with a blank line or `\\[1em]` between subfigure pairs.

## Graphics Path Configuration

Use `\graphicspath` to specify one or more directories for graphics files.
This keeps `\includegraphics` calls clean and makes it easy to reorganize images later:

```latex
% Multiple directories, each in its own set of braces
\graphicspath{{images/}{figures/}{../shared/figures/}}

% Now just use the filename
\includegraphics[width=0.6\textwidth]{architecture-diagram}
```

Each path must end with a trailing `/` inside its braces.

## Caption Placement

This rule is a universal typographic convention:

- **Figures:** Caption goes **below** the figure.
- **Tables:** Caption goes **above** the table.

The rationale: readers scan a table's header first (so the caption should precede it), but they see a figure as a whole before reading its description.

```latex
% Figure: caption below
\begin{figure}[tbp]
  \centering
  \includegraphics[width=0.7\textwidth]{results.pdf}
  \caption{Experimental results on the benchmark dataset.}
  \label{fig:results}
\end{figure}

% Table: caption above
\begin{table}[tbp]
  \caption{Summary statistics for all participants.}
  \label{tbl:summary}
  \centering
  \begin{tabular}{@{}lcc@{}}
    \toprule
    Group & Mean & Std.\ Dev. \\
    \midrule
    Control   & 42.3 & 5.1 \\
    Treatment & 51.7 & 4.8 \\
    \bottomrule
  \end{tabular}
\end{table}
```

## Label Placement

The `\label` command must appear **immediately after** `\caption`.
Placing it before the caption, after the float body, or outside the float produces incorrect references.

```latex
% CORRECT: \label right after \caption
\caption{Description of the figure.}
\label{fig:my-figure}

% WRONG: \label before \caption
\label{fig:my-figure}
\caption{Description of the figure.}

% WRONG: \label after \end{tabular} but before \caption
\end{tabular}
\label{tbl:my-table}   % points to section, not table
\caption{Description.}
```

**Why:** LaTeX's `\label` captures the value of the most recently incremented counter.
The `\caption` command is what increments the figure or table counter.
If `\label` appears before `\caption`, it captures the section counter instead.

## Float Specifiers

The float placement specifier tells LaTeX where it is *allowed* to place the float.
It is a permission list, not a command.

| Specifier | Meaning                                                |
| --------- | ------------------------------------------------------ |
| `t`       | Top of a text page                                     |
| `b`       | Bottom of a text page                                  |
| `p`       | Dedicated float page (for large floats)                |
| `h`       | Here, approximately where it appears in the source     |
| `!`       | Override internal aesthetic limits (more aggressive)   |
| `H`       | Exactly here (float package); disables float mechanism |

### Recommended Defaults

```latex
% Good default: allows top, bottom, or float page
\begin{figure}[tbp]

% When "here" is desired, still allow alternatives
\begin{figure}[htbp]

% For large floats that should get their own page
\begin{figure}[p]
```

### Why Not `[H]`

The `[H]` specifier (from the `float` package) removes the float from LaTeX's placement algorithm entirely, forcing it to appear at the exact source location.
This causes several problems:

1. **Large blank spaces** when the float does not fit on the current page.
2. **Cascading displacement** of subsequent floats, which pile up and get pushed to the end of the section or document.
3. **Poor page breaks** because LaTeX cannot rearrange content to fill pages evenly.

If you feel the need for `[H]`, restructure the surrounding text instead: add a forward reference and let the float go where LaTeX places it.

## Controlling Float Placement

### The `flafter` Package

Loading `flafter` ensures that floats never appear before their source position in the text:

```latex
\usepackage{flafter}
```

Without `flafter`, a float defined near the bottom of a page may appear at the top of the *same* page (before the paragraph that references it).
This package prevents that behavior.

### The `placeins` Package and `\FloatBarrier`

The `placeins` package provides the `\FloatBarrier` command, which forces LaTeX to process all pending floats before continuing:

```latex
\usepackage{placeins}

% All floats defined above this point are placed before LaTeX continues
\FloatBarrier

% Option: automatically place barriers at section boundaries
\usepackage[section]{placeins}
```

The `[section]` option prevents floats from drifting past `\section` boundaries, keeping figures close to the text that discusses them.

**Use sparingly.** Excessive `\FloatBarrier` calls constrain LaTeX's placement algorithm and can worsen page layout.

## Self-Contained Captions

A figure's caption should be understandable without reading the surrounding text.
A reader scanning the document should be able to understand what the figure shows from its caption alone.

```latex
% WEAK: requires reading the paper to understand
\caption{Results.}

% BETTER: self-contained and informative
\caption{Classification accuracy on CIFAR-10 for three model architectures.
  The proposed ResNet variant (solid blue) outperforms both baselines
  across all training epochs.}
```

Guidelines for self-contained captions:

- State what is being shown (the metric, the dataset, the comparison).
- Identify visual elements (colors, line styles, markers) when there are multiple series.
- Summarize the key finding or trend if the figure supports a specific claim.
- Keep the caption concise but complete; it should not repeat the full analysis from the text.

## Dual Captions: Short and Long Versions

The `\caption` command accepts an optional short form for the List of Figures (or List of Tables):

```latex
\caption[Short caption for LoF]{Long, detailed caption that appears
  below the figure with full explanation of what is shown, including
  axis labels, data sources, and key observations.}
\label{fig:detailed}
```

The short version appears in the front matter's List of Figures.
The long version appears with the float itself.
Use this when the full caption is too long or too detailed for a table of contents entry.

## Consistent Formatting Across Figures

All figures in a document should share consistent visual conventions:

- **Axes:** Same font family and size for axis labels and tick marks across all plots.
- **Line weights:** Consistent stroke width for lines, borders, and arrows.
- **Colors:** Use a single, colorblind-safe palette throughout the document.
- **Labels:** Identical formatting for legends (same font, position, border style).
- **Dimensions:** Maintain consistent width for related figures (all single-column figures the same width, all double-column figures the same width).

When generating figures programmatically (matplotlib, R, gnuplot), define a style file or configuration that is shared across all plotting scripts.
This ensures visual consistency without manual adjustment.

## Sources

- Overleaf. "Inserting Images," "How to Write a Thesis in LaTeX: Figures, Tables, and Captions." Guides.
- Mittelbach, F. and Fischer, U. *The LaTeX Companion*. 3rd ed., 2024. Chapters on floats and graphics.
- Carlisle, D. *graphicx* package documentation. CTAN.
- Sommerfeldt, A. *caption* and *subcaption* package documentation. CTAN.
