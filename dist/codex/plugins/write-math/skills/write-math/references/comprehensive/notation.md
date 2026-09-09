# Notation Principles for Mathematical Writing

Good notation is invisible: it lets the reader focus on ideas rather than decoding symbols. Poor notation forces readers to maintain a mental lookup table, distracting from the mathematics itself. The principles below, drawn from Tao, Poonen, Wang, Conrad, and Cohn, provide concrete rules for choosing, introducing, and maintaining notation throughout a mathematical document.

## When to Introduce Notation

**Only name what you use repeatedly.** If an expression appears three or more times, give it notation. For one-off or two-off uses, write the expression inline. Unnecessary notation forces readers to memorize a symbol they will rarely encounter again.

Bad: "Let $\mathcal{Q}$ denote the set of primes less than 100. Since $\mathcal{Q}$ is finite, we can enumerate $\mathcal{Q}$."
(If this is the only paragraph mentioning the set, just write "the set of primes less than 100" each time.)

Good: "Let $S_n$ denote the symmetric group on $n$ letters." (Used throughout the paper in dozens of results.)

**Create TeX macros for any notation you might revise.** Define `\newcommand{\probset}{\mathcal{P}}` so that changing notation later requires editing one line, not fifty. This also enforces visual consistency: every instance of the symbol renders identically.

## Global vs. Local Notation

**Global notation belongs near the front.** If a symbol appears across multiple sections, introduce it in a dedicated "Notation" or "Preliminaries" section. Readers who lose track can flip back to a single location.

**Local notation belongs where it is used.** If a symbol appears only within one proof or one subsection, define it at the point of first use. Do not clutter the global notation table with temporary variables.

**Clearly mark scope.** When introducing local notation inside a proof, signal its scope explicitly: "For this proof, let $\delta$ denote..." This prevents readers from assuming $\delta$ carries meaning elsewhere.

## Match Existing Literature

**Use conventions your audience already knows.** If every paper in the field uses $G$ for a group, $H$ for a subgroup, and $\phi$ for a homomorphism, adopt the same. Deviating without reason forces readers to mentally translate.

**Use standard terminology rather than inventing your own, even if yours seems superior.** Readers search for known terms. A novel name for a known concept creates a barrier: readers must discover that your "admissible partition" is what everyone else calls a "balanced coloring." If you must introduce new terminology, explicitly connect it to existing terms.

**Standard variable conventions include:**

- $x, y$ for real variables
- $z, w$ for complex variables
- $n, m, k$ for natural numbers and indices
- $p, q$ for primes
- $\varepsilon, \delta$ for small positive quantities
- $f, g, h$ for functions
- $V, W$ for vector spaces
- $G, H$ for groups
- $R, S$ for rings

## Meaningful Letter Choices

**Choose letters that suggest meaning.** Use $p$ for a prime, $m$ for a matrix (or module, but not both in one paper), $n$ for a count, $t$ for time. The mnemonic link reduces cognitive load.

**Be consistent across similar contexts.** If you write "$A_j$ where $1 \le j \le n$" in Section 2, do not switch to "$A_k$ where $1 \le k \le n$" in Section 4. The inconsistency signals a distinction that does not exist, confusing readers.

**Avoid overloading symbols.** If $m$ is a matrix in one section, do not let $m$ be a module in another. If you run out of letters, use subscripts, calligraphic letters ($\mathcal{M}$), or bold variants ($\mathbf{m}$) to disambiguate.

## Pairing Objects with Their Notation

**Always introduce notation alongside a description of the object.** Write "the vector space $V$", "the prime $p$", "the continuous function $f \colon [0,1] \to \mathbb{R}$." This pairing anchors the symbol to its mathematical meaning immediately.

Bad: "Let $V$ be as above." (Forces the reader to search backward.)

Good: "Let $V$ be the vector space of square-integrable functions on $[0,1]$."

**Don't let a symbol appear before its definition.** Even if the definition is only one sentence away, reading an undefined symbol creates momentary confusion.

## Planning Notation Before Drafting

**Record all notation on a separate sheet before you begin writing.** List every symbol, its meaning, and where it first appears. Check for:

- Conflicts: two different meanings for the same symbol
- Redundancy: two different symbols for the same object
- Complexity: symbols that are hard to write, hard to read, or visually similar to others (e.g., $v$ and $\nu$, $\ell$ and $1$, $O$ and $0$)

**Revise the notation sheet as the paper evolves.** Notation that seemed necessary in an early draft may become unnecessary after restructuring.

## Avoiding Clever or Self-Referential Notation

**Use bland names for peripheral concepts.** If a construction appears only in one proof and serves a supporting role, give it a forgettable name. Reserve vivid, memorable notation for the central objects of your paper.

**Never name concepts after yourself.** Even if you invented the construction, self-naming appears immodest and is not how mathematical naming works in practice. Let the community assign eponymous names if the concept merits it.

**Avoid "cute" notation.** Notation should be functional, not entertaining. A notation that makes you smile but confuses readers is a net loss.

## Functions vs. Their Values

**Distinguish "the function $f$" from "the value $f(x)$."** These are different mathematical objects. Write "the function $f$ is continuous" (not "the function $f(x)$ is continuous," since $f(x)$ is a number, not a function). Write "the value $f(x)$ is positive for $x > 0$."

Exception: In contexts where the variable is essential for clarity, writing "the function $f(x) = x^2 + 1$" is acceptable as a definition.

## Minimizing Subscripts

**Don't introduce subscripted elements when set-element notation suffices.** If you only need a generic element of $P$, write "let $p \in P$" rather than "let $p_i$ be an element of $P$." Reserve indexed notation for situations where the index is essential to the argument.

**Avoid subscripted subscripts.** When working with subsets of a set $X = \{x_1, \dots, x_n\}$, the subset will require doubly-indexed elements like $x_{i_1}, \dots, x_{i_m}$. If the subset's internal ordering does not matter, refer to elements $x$ and $y$ of $X$ instead, or use set-element notation throughout.

**Name subexpressions to reduce subscript depth.** When a formula involves deeply nested subscripts or an unwieldy subexpression, introduce an auxiliary variable to factor the complexity. Write "$v = c + ku$, where $k = c_i - c_j + 1$" rather than "$v = c + u(c_i - c_j + 1)$" when $k$ will be manipulated further. This "name and conquer" technique keeps formulas readable and makes subsequent algebraic steps easier to follow.

## Conventions for Inequalities and Expressions

**Place unknowns on the left of inequalities.** Write $x < 5$, not $5 > x$. The convention aligns with how we read: the object of interest appears first.

**Keep inequality direction consistent across a passage.** If you write $p_i < p_j$ with $i < j$, keep both relations pointing the same way throughout the argument. Don't flip to $p_j > p_i$ or write $i < j$ alongside $p_j < p_i$. The former is much easier for a reader to visualize; the latter forces them to mentally reverse one of the inequalities.

**Prefer bounding non-negative quantities.** Write $|x - a| < \varepsilon$ rather than $-\varepsilon < x - a < \varepsilon$ when the absolute value form is cleaner and more standard.

**Place main terms first, error terms after.** Write $f(x) = x^2 + O(x)$, not $f(x) = O(x) + x^2$. The dominant term should appear first so the reader grasps the leading behavior immediately.

## Fractions in Prose

**Prefer slashed fractions in inline expressions.** Write $(1+x)/y$ rather than $\frac{1+x}{y}$ in running text. Stacked fractions in inline mode expand the line height and crowd surrounding text.

**Never use stacked fractions inside exponents or subscripts.** Stacking creates tiny, nearly unreadable numerals. Write $e^{n(n+1)(2n+1)/3}$, not $e^{\frac{n(n+1)(2n+1)}{3}}$. This is the single most common typographic error that mathematicians make when they control their own typesetting.

## Vectors

**Column vectors are the standard convention.** When working in linear algebra, assume vectors are column vectors unless stated otherwise. If you need row vectors, say so explicitly: "the row vector $v^T$."

## Summary Checklist

Before submitting, verify:

1. Every symbol is defined before first use
2. No symbol has two meanings in the same paper
3. No two symbols denote the same object
4. Notation matches field conventions where possible
5. Peripheral concepts have simple, forgettable names
6. TeX macros exist for any notation that might change
7. Inequalities place unknowns on the left, main terms first
8. Inequality direction is consistent across each passage
9. Subscripts are minimized; set-element notation used when indexing is not essential
10. No stacked fractions inside exponents or subscripts
11. Functions are distinguished from their values
12. Notation scope (global vs. local) is clear to the reader
13. Visually similar symbols ($v/\nu$, $\ell/1$, $O/0$) are avoided or distinguished by context
