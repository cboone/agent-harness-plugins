# Revision, Process, and Reading Mathematics

Comprehensive reference for the mathematical writing process, from first draft through submission. Covers drafting workflow, revision strategy, collaboration, feedback, and techniques for reading and debugging mathematical text. Based on Pak, Tao, Krantz, Cohn, Lee, Su, and Tsitsiklis.

## Drafting Workflow

### Skeleton-first drafting

Tao advocates treating paper composition like a rapid prototyping cycle in software: build a working skeleton before you fill in any details, so that structural problems surface early when they are cheap to fix. The four stages:

1. **Skeleton.** Write a draft that contains approximate statements of every key lemma, proposition, theorem, and definition, with all proofs omitted or sketched in a single informal sentence. The priority is logical organization and the big picture, not precision. This draft is legible only to you.
2. **Precise statements.** Tighten the statements of the lemmas, propositions, theorems, and definitions until they are stable. Do not write proofs yet; statement boundaries often shift during this stage, and proving against a moving target is wasted work.
3. **Key structural proofs.** Write the proofs of the results that connect major milestones. These are the load-bearing arguments that verify the structure actually works. If the structure turns out to be wrong, you find out now rather than after fifty pages of polished prose.
4. **Routine proofs and introduction.** Fill in the proofs of the supporting lemmas and applications. Write the introduction and motivational sections last, when you finally understand what the paper is really about.

**Tactical tricks while drafting:**

- Use placeholder constants (`let $\delta := {?}$`) for parameters whose values depend on decisions you have not yet made. Pinning down $\delta$ too early forces cascading revisions.
- Capture fleeting ideas as stubs in the place they belong: a one-sentence note "TODO: this probably also implies (X)" is better than either pursuing the digression immediately or losing the thought entirely.

**Reconciliation with "pencil and paper first" below.** Pak's rule says work proofs out with pencil and paper before typesetting, and Tao's rule says build a digital skeleton early. These are complementary, not in conflict: use pencil and paper for mathematical discovery, use the digital skeleton for paper architecture. Neither invites you to polish proofs in a LaTeX editor before you know they work.

### Pencil and paper first

Pak insists: write mathematics with pencil and paper before typesetting. Work out the proof, check every step, and understand the argument fully before opening a LaTeX editor. Typesetting while discovering the proof creates what Pak calls "dysfunctional cohabitation," where formatting decisions distract from mathematical thinking and half-finished arguments accumulate in polished-looking documents that obscure their own gaps.

The pencil-and-paper draft does not need to be complete or beautiful. It is a working document for you. Its purpose is to separate the act of mathematical discovery from the act of mathematical communication.

### Identify the main contribution first

Krantz advises: before writing a single sentence, identify your main idea or contribution. What is the paper about? What is the one thing you want the reader to take away? If you cannot state this in two sentences, you are not ready to write. This clarity of purpose shapes every decision that follows: what to include, what to omit, what to emphasize, and how to structure the argument.

**Exercise:** Write a two-sentence summary of your paper. The first sentence states the problem. The second states your result or contribution. If you cannot do this, you have a research problem, not a writing problem.

### Identify your reader

Lee stresses the importance of choosing a specific audience before drafting. The level of detail, the amount of background, and the style of exposition all depend on who will read the paper. Common audience targets:

- **Expert in your subfield:** minimal background, maximum technical detail, emphasis on novelty
- **Expert in a neighboring field:** moderate background, careful notation, emphasis on connections
- **Beginning graduate student:** substantial background, many examples, emphasis on intuition
- **Broad mathematical audience:** extensive motivation, limited technical prerequisites, emphasis on ideas over machinery

Most research papers should target the second or third audience. Papers aimed only at the first audience limit their own impact.

### Outlining

Krantz recommends making an outline before writing prose. The outline should include:

1. **Table of contents:** section and subsection headings
2. **Bullet points for each section:** the key claim, the method, and the main difficulty
3. **Theorem statements:** draft versions of your main results, even if approximate
4. **Dependencies:** which results depend on which, so you can order sections logically

The outline reveals structural problems early. If Section 4 requires notation from Section 6, the sections are in the wrong order. If three sections each contain one small lemma, they might be a single section with three subsections.

### Write the introduction first

Tsitsiklis recommends writing the introduction before the body. This may seem backwards, but it works for two reasons. First, the introduction forces you to articulate the problem, the motivation, and the main results in plain language, which clarifies your own thinking. Second, the introduction serves as a roadmap for the rest of the paper, so writing it first gives you a structural blueprint to follow.

Be prepared to rewrite the introduction after completing the body. Your understanding of your own contribution will sharpen as you write the technical sections. The final introduction should reflect this sharper understanding, not the preliminary version you started with.

### Linear development

Structure the paper so that a reader proceeding from start to finish never encounters a concept, symbol, or result that has not been introduced. Forward references ("as we will see in Section 5") are acceptable for motivation, but the reader should never need to read Section 5 in order to understand Section 3.

## Revision Strategy

### Revise on paper

Pak recommends printing your draft and revising by hand on the printout rather than editing directly on the computer. The change of medium shifts your perspective: you read the paper as a reader rather than as a writer. Errors, awkward phrasings, and structural problems that are invisible on screen become obvious on paper.

Mark up the printout with a pen. Circle unclear passages. Draw arrows to indicate where material should be moved. Write marginal notes like "motivate this" or "example needed." Then return to the computer and implement the changes.

### Multiple drafts

Expect multiple drafts. All sources agree that a first draft, however carefully written, contains errors, redundancies, and unclear passages. Rewrite entire sections if needed; do not try to patch a fundamentally flawed section with local edits. A section that does not work is better rewritten from scratch, using the original as a reference, than repaired sentence by sentence.

**Typical revision cycle:**

1. **First draft:** get the mathematics right; do not worry about polish
2. **Second draft:** restructure for the reader; add motivation, examples, signposting
3. **Third draft:** tighten prose; remove redundancy; check notation consistency
4. **Final pass:** proofread for typos, broken references, formatting errors

### Fresh eyes

Su recommends setting a draft aside for a day or two before rereading it. The break allows you to approach the text with fresh perspective, catching errors and awkwardness that were invisible when the writing was still in your working memory. This simple technique is one of the most effective revision tools available.

### The streamlining question

Pak suggests asking yourself after each draft: "Did I use every tool I introduced? Can I streamline?" If you defined a piece of notation in Section 2 and never used it again, remove it. If you proved a lemma that is not cited in any subsequent argument, either remove it or explain why it is included (perhaps as context or as a result of independent interest). Every element in the paper should earn its place.

### Do not over-optimize

Knuth's dictum that "premature optimization is the root of all evil" applies to mathematical writing as well as to code. Once the easy improvements to a draft are in, you encounter a law of diminishing returns: further gains come at the cost of disproportionate effort or of trade-offs in other qualities of the paper.

**The lemma-optimization trap.** Given a serviceable lemma, it is tempting to weaken the hypotheses and strengthen the conclusion until you reach the "sharpest" version. This often lengthens the proof of the lemma, obscures how the lemma is actually used in the rest of the paper, and yields a statement that is harder to cite because its surface is more complicated. A lemma that is pleasant to apply beats a lemma that is maximally general but awkward to deploy.

**Future-proofing is risky.** Optimizing notation and results in the hope that future researchers will thank you is a speculative investment. Later authors may introduce tools that render your painstakingly optimized result obsolete, and the effort you spent will have bought nothing.

**Overcompression hurts the reader.** A short paper is not automatically a good paper. A longer, gentler treatment is easier to follow than a compressed one of the same content, and reader time is scarcer than page count.

**The one exception.** Optimizing for readability is always safe, except when it comes at the expense of rigor or accuracy. If an easier-to-read phrasing is also correct and precise, prefer it; if it smudges a hypothesis or sweeps a case under the rug, restore the more careful version.

**Reconciliation with "The streamlining question" above.** Streamlining removes dead weight (notation or lemmas you introduced and never used). Over-optimization squeezes live weight (making used material "sharper" at the cost of its role). The first is always worth doing; the second rarely is.

### Polishing restraint (Johnson's rule)

Samuel Johnson's advice to writers, which Tao echoes, is: "Wherever you meet with a passage which you think is particularly fine, strike it out." In mathematical writing this means: when you notice you have written a sentence that feels unusually witty, philosophical, or literary, suspect it. A mathematical paper is a record of results, not a showcase for prose style, and clever passages distract from the argument. Informal remarks and opinions are welcome when clearly labeled as such, but ornate writing that calls attention to itself is a reliable warning sign that the sentence should be cut or rewritten flat.

### Writing as understanding

Lee observes that writing clarifies your own thinking. If you cannot write a passage clearly, you probably do not understand it well enough. This is not a failure of writing skill; it is a diagnostic. The remedy is not to polish the prose but to return to the mathematics and deepen your understanding. When the understanding is complete, the clear writing follows.

## Collaboration

### Early notation conventions

Krantz advises establishing notation conventions at the very beginning of a collaboration. If one author writes $\|x\|$ and another writes $|x|$ for the same norm, the inconsistency will propagate through the paper and require tedious correction later. Agree on notation, terminology, and formatting conventions before anyone begins drafting.

**Practical checklist for collaborators:**

- Symbol choices for recurring objects (groups, spaces, operators, constants)
- Naming conventions for theorems, lemmas, and definitions
- Citation style (author-year vs. numeric, natbib commands)
- Section structure and numbering scheme
- LaTeX macros to be used (share a common preamble or macros file)

### Tracking changes

If using collaborative editing (Overleaf, Git, or shared LaTeX files), track changes carefully. Use version control, margin comments, or the `changes` LaTeX package to record who changed what. This is especially important in the late stages of revision, when an untracked edit can introduce an error that is difficult to diagnose.

### Consistency enforcement

Krantz recommends designating one person to ensure consistency of style and notation across the paper. In a two-author paper, this usually falls to whichever author is more detail-oriented or has more writing experience. In a larger collaboration, it should be an explicit role.

The consistency enforcer reads the entire paper looking for:

- Notation that changes meaning between sections
- Terminology that shifts (e.g., "compact" in one section, "pre-compact" in another for the same concept)
- Formatting inconsistencies (e.g., "Theorem" vs. "Thm." in cross-references)
- Tone shifts between sections written by different authors

### Collaborative rewriting

Rewrite collaboratively rather than editing sequentially. Sequential editing, where one author drafts and another edits, produces a paper with a split personality. Collaborative rewriting, where both authors work through the prose together (in person, on a call, or through detailed comments), produces a unified voice.

## Feedback

### Pre-submission review

Cohn strongly recommends getting detailed feedback from colleagues or friends before submitting. Ask someone who is not a coauthor to read the paper and report:

- Where they got confused
- Where they lost the thread of the argument
- Which definitions felt unmotivated
- Whether the introduction made them want to read the rest

### Ask for criticism, not praise

Cohn advises asking reviewers for honest criticism. "Is anything unclear?" is a better question than "What did you think?" A reviewer who says "it's fine" has not helped you. A reviewer who says "I didn't understand the transition between Lemma 3.2 and Theorem 3.3" has given you gold.

**Useful prompts for reviewers:**

- "Where did you have to read a sentence twice?"
- "Which assumptions felt unmotivated?"
- "Was there a point where you wanted an example and didn't get one?"
- "Did the introduction give you enough context to understand the main result?"

### Clear writing as competitive advantage

In a competitive academic environment, the clearer of two papers presenting the same result gets the credit. This is not cynicism; it is a practical observation. Referees who can follow your argument are more likely to recommend acceptance. Readers who can understand your results are more likely to cite them. Colleagues who can explain your contribution are more likely to recommend you. Clear writing is not a luxury; it is an investment.

### Reducing the burden on others

Clear writing reduces the burden on supervisors (who must read and comment on your drafts), referees (who must evaluate your claims), and future readers (who must build on your results). Every hour you spend improving your exposition saves many hours of collective reader effort.

## Reading and Debugging Mathematical Text

Tao provides detailed advice on reading mathematical papers, which is equally valuable as a guide for writing. Understanding how readers parse and debug text helps you avoid common pitfalls.

### When a passage is unclear

When you encounter an unclear passage, read the next one or two lines before stopping to puzzle over it. Often the author provides the clarification immediately afterward, or the context of the next sentence disambiguates the meaning. Stopping too early wastes time on confusion that resolves itself.

### Searching forward for context

For deeper confusion, search ahead in the paper to where the problematic lemma or definition is actually used. The application often reveals the intended meaning more clearly than the abstract statement. If a lemma's statement is opaque, reading its application in the proof of the main theorem may clarify what the lemma really says.

**Practical technique:** In a PDF, use text search to find where a lemma number or term appears later in the document. The usage context often disambiguates the statement.

### Accepting that authors make errors

Tao notes that authors sometimes make minor errors: off-by-one mistakes, mismatched quantifiers, or conclusions that are slightly different from what was actually proved. When you encounter a statement that seems wrong, check whether the author consistently meant a slightly different (correct) conclusion. If the error is cosmetic and the argument works with a small correction, note the correction and move on.

### Noticing the absence of transition words

When reading a proof and encountering a statement that seems to appear from nowhere, notice whether the statement is preceded by a transition word like "thus," "therefore," "hence," or "it follows that." If it is, the statement is a conclusion drawn from what precedes it, and you should look backward for the premises. If no transition word is present, the statement may be a new hypothesis, a side remark, or the beginning of a new step in the argument.

As a writer, the lesson is: always include transition words to signal deductive structure. "Thus," "since," "because," and "it follows that" are not filler; they are logical signposts that tell the reader how each sentence relates to its neighbors.

### Diagramming logical flow

Tao recommends drawing boxes for lemmas and theorems with arrows showing the logical dependencies. This exercise, done either while reading or while outlining your own paper, reveals the structure of the argument at a glance. If the diagram has a clean tree or DAG structure, the paper is well-organized. If the diagram is a tangle of cross-references, the paper may benefit from restructuring.

**Example diagram:**

```text
Lemma 2.1 ──┐
             ├──> Theorem 3.1 ──> Main Theorem (4.1)
Lemma 2.3 ──┘                         ^
                                       |
Lemma 2.2 ──────> Proposition 3.2 ─────┘
```

### Local versus global errors

Tao distinguishes two fundamentally different ways a proof can fail.

**Local errors** are step-level. A single deduction does not follow; a quantifier is misordered; two steps rely on a term with two different meanings. A special case: **circular reasoning**, where fact $A$ is used to justify $B$ and $B$ is used to justify $A$, even when each implication holds in isolation. Ambiguity across steps is a local error: if a term $T$ could mean $T_1$ or $T_2$, and step 1 establishes $A \to T_1$ while step 5 uses $T_2 \to C$, the chain $A \to C$ is broken by the ambiguity even though both halves look fine individually.

**Global errors** are whole-proof. If the proof were valid, it would imply something already known to be false, most often via a counterexample to the main claim or to an intermediate statement. A global error kills all reasonable perturbations of the proof at once: you cannot patch it by fixing a step, because any proof producing the same conclusion would hit the same counterexample.

**Different diagnostic effort.** Local errors require line-by-line reading. Global errors can often be detected by skimming the large-scale structure and checking whether the claimed output is even plausible.

**Different rigor standards at different stages.** When building a proof, use the highest rigor you can afford; a missed local error is expensive to debug later. When testing for errors in a finished draft, heuristics, hand-waving, and sanity checks (does this bound have the right scaling? is the conclusion even consistent with small cases?) are fine and often more efficient than formal re-verification.

**Fault-tolerant structure.** As a writer, structure long proofs so that a local slip does not kill the global argument. Independent lemmas that each carry a named conclusion are safer than a chain where every step depends on the previous one's details. Tao's advice to break long proofs into lemmas (see `theorems-and-proofs.md`) is partly an error-containment measure: if Lemma 3.2 has a local bug, only Lemma 3.2 needs repair, not the two pages following it.

### Reducing complexity for understanding

When a proof is hard to follow, Tao suggests simplifying along one or more dimensions:

- **Reduce dimension:** work in $\mathbb{R}$ or $\mathbb{R}^2$ instead of $\mathbb{R}^n$
- **Ignore error terms:** pretend all $O(\varepsilon)$ terms are zero and see if the core argument becomes clear
- **Analyze near-counterexamples:** consider inputs that almost violate the theorem's conclusion, and trace how the proof handles them
- **Specialize parameters:** set $k = 1$ or $p = 2$ and work through the argument in this case first

These simplifications help you isolate the key ideas from the technical scaffolding. Once you understand the simplified version, the general case is often a matter of bookkeeping.

### From reading to writing

The debugging techniques above translate directly into writing advice:

- If your proof requires the reader to hold many threads simultaneously, restructure it
- If a lemma's statement is only clear in context, add a motivating sentence before the statement
- If your argument works by contradiction and the reader cannot tell which hypothesis is being contradicted, state it explicitly
- If your error terms obscure the main idea, present the clean version first, then the technical version

## Quick Reference: Process Stages

| Stage          | Key Action                                                     |
| -------------- | -------------------------------------------------------------- |
| Pre-writing    | Work out the proof on paper; identify the main contribution    |
| Outlining      | Table of contents with bullet points; draft theorem statements |
| First draft    | Get the mathematics right; write the introduction first        |
| Second draft   | Restructure for the reader; add examples and signposting       |
| Third draft    | Tighten prose; enforce notation consistency; streamline        |
| Pre-submission | Get feedback from non-coauthors; ask for criticism             |
| Final pass     | Proofread on paper; check references and formatting            |
| Post-rejection | Use referee reports constructively; revise and resubmit        |

## Sources

- Pak, I. "How to Write a Clear Math Paper: Some 21st Century Tips."
- Tao, T. "Advice on Writing Papers" (Compilation Errors, Submit to Appropriate Journal, Write a Rapid Prototype First, Don't Overoptimise, On Local and Global Errors, Write Professionally). terrytao.wordpress.com.
- Krantz, S. G. "How to Write Your First Paper." AMS, 2007.
- Cohn, H. "Advice." cohn.mit.edu.
- Lee, K. P. "A Guide to Writing Mathematics." MIT.
- Su, F. E. "Guidelines for Good Mathematical Writing."
- Tsitsiklis, J. N. "A Few Tips on Writing Papers with Mathematical Content."
