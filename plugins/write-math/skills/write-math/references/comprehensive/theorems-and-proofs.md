# Theorem Statements and Proof Structure

The theorem-proof cycle is the backbone of mathematical writing. A well-designed theorem statement tells the reader exactly what is true and under what conditions; a well-structured proof convinces the reader why it is true without wasting their time. The principles below, drawn from Tao, Poonen, Berndt, Goldreich, Pak, Lee, and the Cambridge mathematics guide, cover both the architecture of results (how to decompose a paper into theorems, lemmas, and corollaries) and the mechanics of individual proofs.

## Theorem/Lemma Architecture

### When to Create a Lemma

**Use lemmas to isolate intermediate facts that support a main result.** The key benefit: once a lemma is proved, readers can forget its proof and retain only its statement. This reduces the cognitive load of the main proof.

**Frame lemma statements for ease of use, not ease of proof.** The hypotheses should be natural (conditions the reader expects or can easily verify), and the conclusion should be manifestly useful in subsequent arguments. A lemma whose conclusion requires further manipulation to be useful has the wrong boundary.

Bad lemma statement: "If $f$ is a bounded measurable function on $[0,1]$ with $\|f\|_\infty \le M$ and $\int_0^1 f(x)\,dx = 0$, then for all $\varepsilon > 0$ there exists $\delta > 0$ such that..."
(Overly specific hypotheses that obscure the lemma's role.)

Better: "Let $f \in L^\infty([0,1])$ with mean zero. Then $f$ satisfies the following approximation property: ..."
(Clean hypotheses, clearly stated conclusion.)

### Combining and Splitting Lemmas

**If two technical lemmas only make sense together, combine them.** When Lemma A's conclusion is exactly Lemma B's hypothesis and neither statement is independently interesting, merge them into one lemma. Move the intermediate statement into the proof as an unlabeled claim or sublemma.

**When auxiliary lemmas create a very long proof, promote the main result.** If proving Theorem X requires Lemmas X.1, X.2, and X.3, each with substantial proofs, consider making Theorem X a section-level result (a Proposition or named Theorem) and devoting an entire section to it and its supporting lemmas.

### Lemmas as Signposts

**Use lemmas to recap running hypotheses.** In a long paper, readers may have forgotten what assumptions are in force. A lemma statement that begins "Under the hypotheses of Theorem 3.1, and with the notation of Section 2..." reminds the reader of the context without forcing them to flip back.

## Theorem Statement Design

### Clarity and Brevity

**Keep theorem statements short and crisp.** A theorem should be quotable: a reader should be able to state it to a colleague without consulting the paper. If the statement requires a full paragraph, consider whether some conditions belong in the surrounding text as "standing assumptions."

**Define all terms before the statement.** Every symbol, concept, and condition mentioned in the theorem must be defined or referenced before the reader encounters the formal statement. Never force the reader to look forward for a definition.

Bad ordering:

> **Theorem 3.1.** Every $\alpha$-regular graph is $\beta$-chromatic.
> **Definition 3.2.** A graph is $\alpha$-regular if...

Good ordering:

> **Definition 3.1.** A graph is $\alpha$-regular if...
> We can now state the main result of this section.
> **Theorem 3.2.** Every $\alpha$-regular graph is $\beta$-chromatic.

### Separating Statement from Discussion

**Do not embed consequences or discussion in the theorem statement.** The statement should contain only the hypotheses and conclusion. Develop corollaries, special cases, and interpretations in the text following the theorem.

Bad: "**Theorem.** If $G$ is a finite group, then $|G|$ divides $|S_n|$ for some $n$, which has important implications for representation theory because..."

Good: "**Theorem.** If $G$ is a finite group of order $m$, then $G$ is isomorphic to a subgroup of $S_m$."
(Discuss implications in the paragraph that follows.)

### Introducing the Statement

**Precede a theorem with a complete sentence that sets it up.** Examples:

- "We can now prove the main result of this section."
- "The following proposition provides the key estimate."
- "As a consequence of Lemma 4.2, we obtain the following."

This sentence creates a smooth transition and signals the reader that a formal statement is coming.

### Strength Axes and Signposting Amplifications

Theorems vary in strength along several axes, even though all true theorems are logically equivalent as propositions. Naming the axes helps the writer calibrate what a result actually claims, and helps the reader locate the load-bearing step in a proof.

**Common axes of strength:**

- **Universal versus existential.** "$P(x)$ holds for every $x$" is stronger than "$P(x)$ holds for some $x$" over a non-empty domain. Intermediate claims ("for almost every $x$," "for many $x$") occupy the middle.
- **Asymptotic versus non-asymptotic.** "For every fixed $n$" is stronger than "for sufficiently large $n$"; an exact bound is stronger than an approximate one, all else equal.
- **General versus special.** A statement about arbitrary groups is stronger than the same statement about finite abelian groups, though broader applicability often forces weaker conclusions, so the trade-off must be named.
- **Difficulty of the objects.** Results about well-understood objects (linear operators, equations over $\mathbb{R}$) are weaker than analogous results about poorly understood ones (nonlinear operators, Diophantine equations).

**Signpost where your statement amplifies strength.** When a proof upgrades a claim along one of these axes (for example, from "for some $x$" to "for every $x$," or from "asymptotic" to "uniform"), the step that does the amplifying is usually the load-bearing idea of the argument. Name it in the prose surrounding the theorem so the reader can locate it:

> The key amplification is the passage from a pointwise bound (Lemma 3.3) to a uniform bound (Lemma 3.4); everything else in this section is routine.

This signposting doubles as a sanity check. A suspiciously large jump in strength without a corresponding idea often indicates an error.

### Accurate Scope: State Limitations Explicitly

**A theorem statement should describe neither more nor less than what you proved.** Honest scope matters for two reasons: it prevents the reader from mistaking the strength of your result, and it directs future work toward the real gaps.

**State limitations openly.** If a hypothesis is stronger than you would like, say so in the text surrounding the statement:

> **Theorem 3.1.** Let $G$ be a connected, simply connected Lie group. Then...
>
> We do not know whether the simple-connectedness assumption is necessary; the proof uses it only in Step 2 (Lemma 3.5), and a weaker topological hypothesis may suffice.

**Note open subquestions.** When the theorem raises an obvious follow-up question, mention it explicitly rather than letting it dangle. "The case $p = 2$ remains open" is more useful than silence, because it signals both the gap and, implicitly, its approximate difficulty.

**Flag unproven assertions.** When you state a fact you do not intend to prove, mark it clearly so the reader can tell the claim apart from your own results:

- "It can be shown that $f$ is Lipschitz; we will not need this in what follows."
- "Although we will not prove this fact here, the estimate is sharp (see [7])."

Unflagged assertions that the reader cannot verify locally erode trust across the rest of the paper.

## Hierarchy of Named Results

### Choosing the Right Label

- **Theorem**: a main result of the paper, or of a major section. Reserve this label for results that justify the paper's existence.
- **Proposition**: an independent technical fact that is interesting in its own right but is not a main result.
- **Lemma**: a supporting fact whose primary purpose is to serve another result. Readers expect to use the statement and forget the proof.
- **Corollary**: a result that follows directly (often in one or two lines) from a theorem or proposition.

### Unified Numbering

**Use a single numbering system across all result types.** Number results consecutively within sections: Theorem 3.1, Lemma 3.2, Proposition 3.3, Corollary 3.4. This makes cross-references unambiguous; "result 3.2" can only refer to one thing.

### Capitalization in References

**Capitalize when referring by number:** "by Theorem 5.2", "applying Lemma 3.1."

**Lowercase when referring generically:** "the previous theorem", "the following lemma", "the above corollary."

## Proof Structure

### Statement Before Proof

**Always state the theorem before the proof, never the reverse.** A proof without a preceding statement forces readers to discover the destination as they walk the path. This is disorienting. Even if the proof motivates the result, state what you will prove first, then prove it.

### Proof Overviews

**Summarize the main idea outside the proof environment.** Before the formal "Proof." marker, provide a brief paragraph explaining the strategy:

> The proof proceeds in three steps. First, we reduce to the case where $G$ is abelian using Lemma 2.3. Second, we construct an explicit homomorphism. Third, we verify the universal property.

This roadmap helps readers follow the argument and understand where each step fits.

### Linear Forward Flow

**Establish facts first, then build toward the conclusion.** A proof should read as a logical chain: each statement follows from previous ones. Avoid structures where the reader must accept a claim on faith and verify it later.

**Explain what each claim follows from.** Write "By Lemma 3.2, we have $|G| \le n$" rather than "We have $|G| \le n$." The citation tells the reader where the justification lives, even if they choose not to verify it immediately.

### Separating Motivation from Rigor

**Distinguish informal explanation from formal argument.** Mark transitions clearly:

- "Informally, the idea is that..." (motivation)
- "We now make this precise." (transition to rigor)
- "More precisely, we claim that..." (formal statement)

This separation lets readers who want intuition get it and readers who want the proof skip to it.

### Avoiding Magic Tricks

**Do not lay out a sequence of facts and then suddenly declare the theorem proven.** Each step should visibly advance toward the goal. If a step's purpose is not immediately clear, explain its role: "The following estimate will let us apply the dominated convergence theorem in the next step."

### Direct Proofs over Contradiction

**Prefer direct proof when one is available.** Proof by contradiction adds a layer of indirection (negate the conclusion, derive a contradiction, negate again). When a direct proof of comparable length exists, it is clearer because the reader follows the actual logical chain rather than its contrapositive shadow.

Reserve contradiction for situations where it genuinely simplifies the argument, such as proving irrationality or establishing that a set is empty.

**When you do use contradiction, phrase it forward.** Avoid "Assume by contradiction that $\langle$blah$\rangle$," which front-loads the negated conclusion before the reader knows the proof strategy. Better alternatives:

- "The proof that $\langle$blah$\rangle$ is by contradiction." (names the strategy first)
- "To prove $\langle$grunt$\rangle$, let us assume the opposite and see what happens." (conversational, signposted)

### Don't Display False Equations

**A displayed equation draws the reader's eye and is treated as true.** If you need to present a false equation (to show what does not hold, or to exhibit a common error), keep it inline and flag it explicitly: "the equation $\ldots$ is always false." A false statement set in a display invites the reader to absorb it as fact on a first skim.

### Match Proof Order to Definition Order

**When a definition has several cases, present the proof cases in the same order.** If the definition lists cases (i), (ii), (iii), the proof should address them as (i), (ii), (iii), not (ii), (i), (iii). Matching the order lets the reader track exactly where they are in the argument without cross-referencing.

### Breaking Long Proofs

**Decompose long proofs into lemmas, even if each lemma is used only once.** A two-page proof is much harder to digest than three half-page lemmas followed by a short assembly proof. The lemma boundaries create natural resting points and make the logical structure explicit.

### Quantifier Precision

**Make quantifiers unambiguous.** Write "for all $x \in \mathbb{R}$" rather than "for $x \in \mathbb{R}$," which is ambiguous between universal quantification and existential introduction.

Bad: "For $\varepsilon > 0$, there exists $\delta > 0$..."
(Is this "for all $\varepsilon > 0$" or "for some particular $\varepsilon > 0$"?)

Good: "For every $\varepsilon > 0$, there exists $\delta > 0$ such that..."

**Clarify the order of quantifiers.** The statement "for every $n$, we have $f(n) < C$ for some constant $C$" is ambiguous. Does $C$ depend on $n$? Rewrite as either:

- "There exists a constant $C$ such that $f(n) < C$ for every $n$." ($C$ is universal)
- "For every $n$, there exists a constant $C_n$ such that $f(n) < C_n$." ($C$ depends on $n$)

## Ending a Proof

**Signal the end clearly.** Use a QED symbol ($\square$), the word "QED," or the `\qedhere` command in LaTeX. If a proof ends with a displayed equation, place the QED symbol on the same line as the equation to avoid ambiguity about where the proof ends.

**For proofs that end with "...which completes the proof," the QED symbol still appears.** The verbal signal and the visual marker reinforce each other.

## Summary Checklist

Before finalizing any theorem-proof pair, verify:

1. All terms in the theorem statement are defined before it
2. The statement is short enough to quote from memory
3. Discussion and consequences appear outside the statement
4. The preceding sentence creates a smooth transition
5. A proof overview summarizes the strategy before the formal proof
6. Each step cites its justification explicitly
7. Quantifiers are unambiguous (for all vs. for some, and their ordering)
8. Long proofs are broken into labeled lemmas
9. The proof ends with a visible QED marker
10. The result is labeled correctly (Theorem vs. Lemma vs. Proposition vs. Corollary)
