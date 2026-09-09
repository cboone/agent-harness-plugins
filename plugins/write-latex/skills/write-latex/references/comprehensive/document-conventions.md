# Document Conventions for Mathematical LaTeX

## Punctuating Displayed Equations

Displayed equations are grammatically part of the surrounding sentence.
They must be punctuated accordingly: commas, periods, and semicolons go at the end of the display, _inside_ the math environment.

```latex
% CORRECT: period inside the display ends the sentence
The quadratic formula gives
\[
  x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}.
\]

% CORRECT: comma because the sentence continues
Since
\[
  f(x) = x^2 + 1,
\]
we see that $f$ is always positive.

% CORRECT: semicolons to separate cases
We consider two cases:
\begin{align}
  f(x) &= x^2,    &\quad& \text{if } x \geq 0; \label{eq:pos} \\
  f(x) &= -x^2,   &\quad& \text{if } x < 0.    \label{eq:neg}
\end{align}
```

**Never place punctuation on the text line following the display.** The punctuation belongs to the formula, not to the next paragraph:

```latex
% WRONG: period on the next line
\[
  x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
\]
.   % This looks wrong and may create a new paragraph
```

### No Colon Before Equations That Complete the Sentence

When the introductory clause and the displayed equation form one grammatical sentence, no colon should precede the display. The colon is appropriate only when the display is introduced as a list or apposition.

```latex
% WRONG: colon breaks a grammatical sentence
We define the set of nonincreasing vectors:
\[
  A_n = \{(a_1, \dots, a_n) \in N^n \mid a_1 \ge \dots \ge a_n\}.
\]

% CORRECT: the sentence flows into the display
We define the set of ``nonincreasing'' vectors,
\[
  A_n = \{(a_1, \dots, a_n) \in N^n \mid a_1 \ge \dots \ge a_n\}.
\]

% CORRECT: colon is appropriate before a list or apposition
We consider two cases:
\begin{align}
  f(x) &= x^2,   &\quad& \text{if } x \geq 0; \\
  f(x) &= -x^2,  &\quad& \text{if } x < 0.
\end{align}
```

### How to Decide Which Punctuation

Read the sentence aloud as if the equation were a noun phrase. Whatever punctuation you would put after a word in that position goes at the end of the display:

- "The solution is [formula]." (period)
- "Given that [formula], we proceed." (comma)
- "We define [formula]; this is standard." (semicolon)

### Selective Equation Numbering

**Number only displayed equations that are referenced later or that the reader might want to cite.** Numbering every display clutters the margin and dilutes the signal that a numbered equation is important. Use `equation*`, `\[...\]`, or `\notag` for equations that need no reference.

A good test: if you can remove the number without breaking any `\eqref` or `\cref` elsewhere in the document, the equation did not need a number.

## Commas and Math in Running Text

When listing mathematical expressions in running text, place commas _outside_ math mode.
This is Knuth's advice from _Mathematical Writing_: commas belong to the sentence, not to the formula.

```latex
% CORRECT: commas outside math mode
where $x$, $y$, and $z$ are integers

% WRONG: commas inside math mode
where $x, y,$ and $z$ are integers

% WRONG: all in one math group
where $x, y, z$ are integers
```

**Why it matters:**

1. **Spacing:** A comma inside math mode gets math-mode spacing (thin space), which differs from the text-mode spacing a reader expects in prose.
2. **Line breaking:** LaTeX can break the line after a text-mode comma but not after a math-mode comma, which can cause overfull lines.
3. **Consistency:** Treating each variable as a separate math expression within an English sentence keeps the boundary between math and prose clean.

The same principle applies to other punctuation. Colons, semicolons, and periods should be in text mode when they serve a grammatical (not mathematical) purpose:

```latex
% CORRECT: colon in text mode
Let $n$: the number of elements.

% CORRECT: period in text mode
The function $f$ is continuous. Moreover, $g$ is bounded.
```

## Signposting Citations

Integrate citations into prose with context so the reader understands the reference without consulting the bibliography.
Name the author or describe the contribution:

```latex
% GOOD: signposted citation
Smith~\cite{smith2023} showed that password strength
follows a log-normal distribution.

% GOOD: signposted with description
The log-normal model of password strength~\cite{smith2023}
provides a tractable analytical framework.

% WEAK: bare citation with no context
It was shown that password strength follows a
log-normal distribution~\cite{smith2023}.
```

Guidelines:

- Mention the author by name when their identity is relevant ("Bonneau~\cite{bonneau2012} introduced...").
- Describe the contribution when the _what_ matters more than the _who_ ("The guessing-entropy metric~\cite{bonneau2012} measures...").
- Avoid chains of bare citations: "[1], [2], [3] showed that..." gives the reader no way to distinguish the references.
- For background citations that support a general claim, a parenthetical is acceptable: "Password reuse remains common~\cite{das2014, wash2016}."

## Dual Captions: Short and Long Versions

The `\caption` command accepts an optional short form that appears in the List of Figures or List of Tables:

```latex
\caption[Accuracy vs.\ training epochs]{Classification accuracy
  on CIFAR-10 for three model architectures as a function of
  training epochs. The proposed ResNet variant (solid blue)
  outperforms both baselines across all epochs, reaching 94.2\%
  accuracy at epoch 200.}
\label{fig:accuracy}
```

- The **short caption** (in square brackets) should be a concise noun phrase suitable for a table of contents: "Accuracy vs.\ training epochs".
- The **long caption** (in curly braces) is the full description that appears with the float.
- Use dual captions when the full caption exceeds one line. For short captions, the optional argument is unnecessary.

## Label Placement

The `\label` command must appear **immediately after** `\caption`.
This is because `\label` captures the most recently incremented counter, and `\caption` is what increments the figure/table counter.

```latex
% CORRECT
\caption{Results of the experiment.}
\label{fig:results}

% WRONG: label before caption (captures the section counter)
\label{fig:results}
\caption{Results of the experiment.}

% WRONG: label after the float body (may capture wrong counter)
\end{tabular}
\label{tbl:data}   % may point to section, not table
\caption{Data summary.}
```

For equations, `\label` goes on the same line as the equation content (or immediately after it, before `\\`):

```latex
\begin{align}
  E &= mc^2 \label{eq:einstein} \\
  F &= ma   \label{eq:newton}
\end{align}
```

## List Formatting with enumitem

The `enumitem` package provides fine control over list spacing and formatting.

### Removing Extra Vertical Space

LaTeX's default lists add `\topsep`, `\partopsep`, `\itemsep`, and `\parsep`, which can create too much whitespace.
Use `nosep` to remove all extra spacing:

```latex
\usepackage{enumitem}

\begin{itemize}[nosep]
  \item First item
  \item Second item
  \item Third item
\end{itemize}
```

### Removing Left Indentation

Use `wide` (or `leftmargin=*`) to align list items with the surrounding text:

```latex
\begin{enumerate}[wide, nosep]
  \item Flush with the margin
  \item No indentation
\end{enumerate}
```

### Custom Labels

The `label` key controls the item marker:

```latex
% Roman numerals in parentheses
\begin{enumerate}[label=(\roman*)]
  \item First criterion
  \item Second criterion
\end{enumerate}

% Lowercase letters with a closing parenthesis
\begin{enumerate}[label=\alph*)]
  \item Case one
  \item Case two
\end{enumerate}

% Custom text label
\begin{enumerate}[label=Step \arabic*:]
  \item Collect data.
  \item Train model.
  \item Evaluate results.
\end{enumerate}
```

Available counter formats: `\arabic*`, `\alph*`, `\Alph*`, `\roman*`, `\Roman*`.

### Punctuating List Items

Choose one convention and apply it consistently throughout the document:

- **Complete sentences:** Capitalize and end with a period.
- **Fragments completing a stem:** Lowercase, end with a semicolon (or comma), and end the final item with a period.
- **Short noun phrases:** No punctuation.

```latex
% Fragment style: stem sentence followed by fragment completions
The system must:
\begin{enumerate}[nosep, label=(\roman*)]
  \item accept passwords of at least 8 characters;
  \item reject passwords found in breach databases;
  \item provide real-time strength feedback.
\end{enumerate}
```

### Setting Global Defaults

To apply settings to all lists in the document:

```latex
% In the preamble
\setlist{nosep}                      % remove extra spacing globally
\setlist[enumerate]{label=(\arabic*)} % default enumerate label
\setlist[itemize]{label=\textbullet}  % default itemize marker
```

## Sentence Structure Around Math

### Never Start a Sentence with a Symbol

Beginning a sentence with a mathematical symbol makes the sentence boundary ambiguous, especially after a displayed equation:

```latex
% WRONG: sentence starts with a symbol
$x$ is defined as the population mean.

% CORRECT: rephrase to start with a word
The variable $x$ is defined as the population mean.
```

This applies to all mathematical symbols, including Greek letters:

```latex
% WRONG
$\epsilon$ denotes the error tolerance.

% CORRECT
The tolerance $\epsilon$ bounds the approximation error.
```

### Introducing Notation

When defining notation, use a clear pattern:

```latex
% Pattern 1: "Let [symbol] denote [meaning]"
Let $n$ denote the number of users.

% Pattern 2: "where [symbol] is [meaning]"
The loss function is $L(\theta) = \sum_{i=1}^{n} \ell(y_i, f(x_i; \theta))$,
where $\theta$ is the parameter vector and $n$ is the number of training samples.

% Pattern 3: "We write [symbol] for [meaning]"
We write $\mathcal{P}$ for the set of all valid passwords.
```

## Allow Display Breaks

By default, LaTeX does not break pages within `align`, `gather`, or similar environments.
For long derivations, this can push content to the next page and leave large blank spaces.

```latex
% Allow page breaks within all align environments
\allowdisplaybreaks

% Control aggressiveness: [1] (reluctant) to [4] (eager)
\allowdisplaybreaks[1]  % only break if necessary
\allowdisplaybreaks[4]  % break freely
```

Place `\allowdisplaybreaks` in the preamble for document-wide effect, or locally within a group:

```latex
% Local: only this derivation allows breaks
\begingroup
\allowdisplaybreaks
\begin{align}
  a &= b + c \\
  d &= e + f \\
  g &= h + i \\
  j &= k + l
\end{align}
\endgroup
```

To prevent a break at a specific line within an environment that allows breaks, use `\\*`:

```latex
\allowdisplaybreaks
\begin{align}
  a &= b + c \\*   % no page break after this line
  d &= e + f \\     % page break allowed here
  g &= h + i
\end{align}
```

## Unbreakable Spaces

Use the tilde (`~`) to prevent line breaks between elements that should stay together:

```latex
% References: type name and number should not be separated
Theorem~2.1
Section~3
Figure~\ref{fig:main}
Table~\ref{tbl:data}
Equation~\eqref{eq:loss}

% Names: title/honorific and surname
Dr.~Smith
Prof.~Jones

% Units: number and unit (or use siunitx)
42~km
100~MB
```

**Note:** When using `\cref` from the cleveref package, the unbreakable space between the type name and number is inserted automatically. You do not need to write `Theorem~\cref{thm:main}`; just write `\cref{thm:main}`.

Unbreakable spaces are still needed with bare `\ref` and `\eqref`, and in all non-reference contexts (names, units, abbreviations).

### Ties in Mathematical Prose

Beyond references and names, use `~` to prevent psychologically bad line breaks in mathematical prose. A line break that strands a short word or symbol away from its context jars the reader even when the text is technically correct. Common cases:

```latex
% Between a word and the variable it introduces
the function~$f$ is continuous
the set~$S$ contains

% Between "if" and the condition
if~$\varepsilon > 0$, then\dots

% Between a symbol and a short qualifier
for all~$n$
some~$x \in S$
```

The general rule: if a line break between two tokens would leave either one looking orphaned, insert a tie.

## Hyperref PDF Metadata

The `hyperref` package can embed metadata in the PDF file, which is used by search engines, screen readers, and file managers.

### Basic Configuration

```latex
\usepackage{hyperref}
\hypersetup{
  pdftitle   = {A Formal Model of Password Strength},
  pdfauthor  = {Jane Smith and John Doe},
  pdfsubject = {Computer Security},
  pdfkeywords = {passwords, authentication, security, formal methods},
  colorlinks = true,
  linkcolor  = blue,
  citecolor  = blue,
  urlcolor   = blue,
}
```

### Auto-Populating from Document Metadata

The `pdfusetitle` option automatically sets `pdftitle` and `pdfauthor` from the `\title` and `\author` commands:

```latex
\usepackage[pdfusetitle]{hyperref}

\title{A Formal Model of Password Strength}
\author{Jane Smith \and John Doe}
```

This avoids duplication and ensures the PDF metadata matches the document.

### Load Order

hyperref should be loaded **near-last** in the preamble because it redefines many internal LaTeX commands.
Most packages should be loaded before hyperref. The main exception is cleveref, which must be loaded _after_ hyperref:

```latex
% Typical load order
\usepackage{mathtools}
\usepackage{amsthm}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{enumitem}
\usepackage{microtype}
% ... other packages ...
\usepackage{hyperref}    % near-last
\usepackage{cleveref}    % after hyperref
```

## Sources

- Knuth, D. E., Larrabee, T., and Roberts, P. M. _Mathematical Writing_. MAA Notes, 1989.
- Higham, N. J. _Handbook of Writing for the Mathematical Sciences_. 3rd ed., SIAM, 2020.
- Higham, N. J. "How to Prepare Lists in LaTeX." Blog post, 2015.
- Higham, N. J. "How to Typeset a Book or Thesis." Blog post, 2016.
- Rahtz, S. and Oberdiek, H. _hyperref_ package documentation. CTAN.
- Bezos, J. _enumitem_ package documentation. CTAN.
