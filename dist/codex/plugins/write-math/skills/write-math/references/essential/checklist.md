
# Mathematical Writing Essential Checklist

Quick reference for reviews. For detailed guidance, see `../comprehensive/`.

## Notation

- [ ] Introduce notation only for expressions used 3 or more times
- [ ] Match existing literature conventions so readers adapt easily
- [ ] Define TeX macros for notation you might change later
- [ ] Define every symbol at or before first use
- [ ] Use consistent letter choices across similar contexts
- [ ] Pair objects with their notation: "the vector space $V$"
- [ ] No overloading: one symbol, one meaning throughout the paper
- [ ] Minimize subscripts; use set-element notation when indexing is not essential

## Theorem and Lemma Architecture

- [ ] Theorem = main result; Proposition = independent technical fact
- [ ] Lemma = supporting fact for another result; Corollary = follows directly
- [ ] Keep theorem statements short and crisp
- [ ] Define all terms and notation before the formal statement
- [ ] Don't include discussion of consequences in the statement itself
- [ ] Use a single numbering system across all theorem-like environments
- [ ] Capitalize formal references: "by Theorem 5" but "by the previous theorem"
- [ ] State known limitations honestly; flag unproven assertions with "It can be shown that..."

## Proof Structure

- [ ] State the theorem before the proof (never prove first, state after)
- [ ] Summarize the main idea or proof strategy outside the proof itself
- [ ] Present the formal argument in linear forward flow
- [ ] Explain what each claim follows from: "By Lemma 3.2..." or "Since $x > 0$..."
- [ ] Separate motivation and explanation from the rigorous argument
- [ ] Avoid proof by contradiction when a direct proof works just as well
- [ ] Break long proofs into lemmas to reduce cognitive load
- [ ] Structure proofs so a local slip does not compromise the global argument
- [ ] Don't over-optimize lemma statements at the cost of obscuring their role

## Paper Organization

- [ ] Title: informative, no symbols, distinct from prior work
- [ ] First sentence of the introduction leads with the specific subject, not "An X is Y"
- [ ] Text reads correctly with section headings removed
- [ ] Abstract: 3-6 lines, results first then methods, no marketing or jargon
- [ ] Abstract: no precise definitions, no references, self-contained
- [ ] Introduction: frame the problem immediately, not background first
- [ ] Introduction: motivation, literature comparison, main results, roadmap
- [ ] Introduction: state main results informally; formal statements in the body
- [ ] Body sections: 1-3 pages each, with signpost openings ("In this section...")
- [ ] Conclusions: only if adding new insight (open problems, conjectures)
- [ ] Appendices: main text must be self-contained without the appendix

## English Usage

- [ ] Active voice with "we" (author and reader together)
- [ ] Never start a sentence with a mathematical symbol
- [ ] Spell out quantifiers: "for all" not $\forall$, "there exists" not $\exists$
- [ ] Spell out abbreviations: "without loss of generality" not "WLOG"
- [ ] Spell out "if and only if" not "iff"; "such that" not "s.t."
- [ ] Punctuate displayed equations as part of the sentence
- [ ] No colon before a displayed equation that completes the sentence
- [ ] Tie displayed formulas into running commentary; never list formulas without connecting prose
- [ ] Include "that" after "assume" and "suppose" for parsing clarity (but never "We have that")
- [ ] Use "if...then" structure consistently for clarity
- [ ] Avoid "obvious", "trivial", "easy", "clearly" unless justified
- [ ] Use short sentences; break complex logic into multiple sentences
- [ ] Parallel construction for parallel ideas
- [ ] Prefer "each" or "every" over ambiguous "any"; maintain present tense

## Notation Hygiene

- [ ] Remove any symbol that is defined but never referenced again
- [ ] Standard variable assignments: $x$ for reals, $z$ for complex, $n$ for naturals
- [ ] Unknowns on the left of inequalities: $x < 5$, not $5 > x$
- [ ] Disambiguate ambiguous expressions with parentheses or `\frac`
- [ ] Don't use set names ($\mathbb{Z}$, $\mathbb{R}$) for individual variables
- [ ] "The function $f$" not "the function $f(x)$" when referring to the function itself

## Citations

- [ ] Signpost citations: "Smith [3] showed" not "it was shown [3]"
- [ ] Provide specific references: "[Knuth, Thm. 3.14, p. 47]"
- [ ] Don't over-cite standard results (one textbook reference suffices)
- [ ] Review bibliography for depth and breadth
- [ ] Attribute ideas and arguments properly, even when paraphrased
- [ ] Paraphrase prior work in your own voice; never copy paragraphs verbatim

## Reader-Centered Writing

- [ ] Write for a graduate student beginning studies in the field
- [ ] Use concrete examples before general statements
- [ ] Explain motivation for definitions: why these assumptions?
- [ ] Remind reader of earlier notation when referencing distant definitions
- [ ] Highlight important ideas three times: abstract, introduction, body
- [ ] Signal transitions: "We now turn to...", "In the next section..."
- [ ] Make clear the status of every assertion (definition, theorem, conjecture)
- [ ] Calibrate proof detail to what the reader likely already knows
