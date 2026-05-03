
# Organizing a Mathematics Paper

A mathematics paper is not a chronological record of the author's discoveries; it is an optimized communication artifact designed to convey results and their justifications to a reader who starts with zero context. The principles below, drawn from Tsitsiklis, Lagarias, Krantz, Berndt, Goldreich, and Pak, cover the structural components of a paper from title to appendix.

## Title

**Make the title informative but concise.** The title is the first (and sometimes only) thing a potential reader sees. It should convey the subject, the type of contribution, and enough specificity to distinguish the paper from others in the field.

Good: "Sharp Bounds for the Chromatic Number of Random Graphs"
Bad: "On Certain Graph Coloring Problems" (too vague)
Bad: "A Complete Characterization of the Asymptotic Behavior of the Chromatic Number of Erdos-Renyi Random Graphs $G(n,p)$ for All Regimes of $p$" (too long)

**Avoid symbols and formulas in the title.** Titles appear in databases, indexes, and search results where mathematical formatting may not render correctly. Write "Sharp Bounds for Chromatic Numbers" rather than "Sharp Bounds for $\chi(G(n,p))$."

**Make the title distinct from prior work.** If your paper extends "Eigenvalues of Random Matrices" by Smith, do not title yours "Eigenvalues of Random Matrices II." Instead, highlight the new contribution: "Tail Bounds for Eigenvalues of Sparse Random Matrices."

## Abstract

**Write 3 to 6 lines: crisp, self-contained, and focused on results.** The abstract should answer two questions: What did you study? What did you find?

**State results first, then methods.** Lead with the contribution: "We prove that every connected graph on $n$ vertices has at most $2^{n/2}$ maximal independent sets. The proof combines a structural decomposition with an entropy argument."

**Avoid the following in abstracts:**

- Marketing language ("This groundbreaking result...", "We solve a long-standing open problem...")
- Historical background ("Since Euler's foundational work in 1736...")
- Precise technical definitions ("Let $\mathcal{F}$ be a sheaf of $\mathcal{O}_X$-modules on a Noetherian scheme...")
- Citations or references ("[3, Theorem 2.1]")
- Undefined notation or jargon

**Use simple declarative structure.** The pattern "We consider [problem]. We show that [result]. The proof uses [method]." works reliably and reads clearly.

## Introduction

The introduction is the most important section of the paper. Most readers who open the paper will read the introduction; far fewer will read Section 4. Front-load accordingly.

### First Sentence and Opening Paragraph

**The opening paragraph should be your best paragraph, and its first sentence your best sentence.** If a paper starts badly, the reader will wince and be resigned to fighting with the prose. If the beginning flows smoothly, the reader will be hooked and will not notice occasional lapses later.

**Never open with the generic pattern "An X is Y."** This construction buries the specific subject behind an indefinite article. "An important method for internal sorting is quicksort" is weaker than "Quicksort is an important method for internal sorting, because..." Lead with the concrete subject.

### Problem Statement

**Frame the problem immediately.** The first paragraph should tell the reader what the paper is about: "In this paper, we study the distribution of prime gaps in arithmetic progressions." Do not begin with two pages of historical context before revealing the topic.

### Motivation

**Explain why the problem matters.** Connect it to the broader mathematical landscape: "Understanding prime gaps is central to analytic number theory because..." Keep this brief (one to two paragraphs). The motivation should make a non-specialist care, not provide a comprehensive survey.

### Candor About Progress on Famous Problems

**When your paper touches a named conjecture, evaluate your progress honestly.** A paper that cites a famous open problem in its title or abstract and then delivers a small partial result invites charges of "false advertising" or "name-dropping." The remedy is a single candid paragraph in the introduction that states what your result does and does not establish toward the conjecture:

> Our main theorem establishes the conjecture of Erdős and Turán under the additional assumption of (H); we do not resolve the general case, and the techniques here do not appear to extend without a new idea in Step 2.

This paragraph costs three sentences and earns the reader's trust for the rest of the paper. It also saves the referee from having to reconstruct the gap themselves. The general rule: the title, abstract, and introduction together should leave no expert in the field able to accuse you of overclaiming.

### Background and Related Work

**Compare with the closest related work explicitly.** Do not merely list prior results; explain how yours relate to them:

- "Theorem A of [12] establishes the bound $O(n^2)$; we improve this to $O(n \log n)$."
- "Our approach differs from the method of [8] in that we avoid the use of Fourier analysis entirely."
- "The result of [5] applies only to regular graphs; we extend it to all graphs of bounded degree."

This comparison helps the reader understand the paper's contribution relative to what they may already know.

### Summary of Main Results

**State the main results informally in the introduction.** Give the reader a preview: "Our main result (Theorem 3.5) shows that the chromatic number of $G(n, 1/2)$ is concentrated in an interval of width $O(\sqrt{n})$." The formal statement with all hypotheses belongs in the body.

**If the paper has multiple main results, list them as a numbered or bulleted summary.** This helps readers decide which sections to read.

### Roadmap

**Include a roadmap paragraph.** At the end of the introduction, describe the paper's organization:

> The rest of the paper is organized as follows. Section 2 establishes notation and reviews background on random graphs. Section 3 proves the main concentration result. Section 4 develops applications to graph coloring algorithms. Section 5 discusses open problems and extensions.

This roadmap costs a few lines and saves every reader the effort of skimming section headings to understand the paper's trajectory.

## Body Sections

### Section Length and Granularity

**Keep sections to 1 to 3 pages.** Longer sections should be subdivided. Subsections serve as signposts: a reader scanning the paper can locate relevant material by section title without reading every page.

**Use descriptive section titles.** "Concentration via the Second Moment Method" is more informative than "Main Proof." "Error Analysis for the Truncated Series" is better than "Technical Estimates."

### Section Headings Are Not Part of the Text

**The running text must make sense if section headings are removed.** A heading is a marginal signpost, not part of the sentence flow. Do not write "This technique, invented by Cauchy, is used..." when "This technique" refers to the heading "Contour Integration." Instead write "The technique of integrating along curves in the complex plane, invented by Cauchy, is used..."

### Section Openings

**Every section should begin with orientation.** Start with a sentence or short paragraph that tells the reader what the section accomplishes and how it connects to the rest of the paper:

> In this section, we prove the key technical estimate (Lemma 4.3) that will drive the proof of the main theorem. The argument combines a martingale inequality with the structural result from Section 3.

This framing prevents the reader from feeling lost.

### Inverted Pyramid

**Put the most important material first.** Within each section, lead with the main result or the central idea. Supporting lemmas, technical details, and special cases follow. A reader who stops reading mid-section should still have absorbed the most valuable content.

### Examples and Counterexamples

**Illustrate with concrete examples.** After stating an abstract result, show it in action on a specific, simple case. Examples build intuition and help readers verify their understanding.

**Use counterexamples to clarify boundaries.** After proving that all connected graphs satisfy property $P$, show a disconnected graph that fails property $P$. This anchors the hypotheses: the reader sees exactly why connectedness is needed.

### Marking Importance

**Distinguish central material from supporting detail.** Use phrases like "The key insight is..." or "The following technical lemma, while necessary for completeness, is not essential for understanding the main argument." This helps readers allocate their attention.

**Consider relegating technical but non-essential material to an appendix.** If a three-page calculation is necessary for rigor but does not illuminate the main ideas, move it to an appendix and summarize the result in the body.

### Results-to-Effort Ratio (Local Maximum Principle)

**A paper should sit at a local maximum of results relative to effort invested, both yours and the reader's.** Two rules of thumb follow from this principle.

**Include cheap extensions.** If your main result has natural consequences, variants, generalizations, or illustrative counterexamples that can be established with only moderate additional effort, include them. The reader would otherwise have to rederive them independently, which is wasteful at scale. Counterexamples showing that a hypothesis cannot be dropped are especially cheap for you (you already understand the proof) and especially valuable to the reader (they pin down exactly why the hypothesis is needed).

**Remove disproportionately expensive sections.** If a large fraction of the paper is devoted to a minor extension or a technical refinement of the main result, consider cutting it back to a remark, a short sketch, or a note that the refinement is possible. A five-page improvement of a bound by a logarithmic factor rarely justifies its page cost; a one-paragraph remark pointing to the refinement does.

**Strategic sequencing for partial progress.** When a paper is a partial result on a larger problem, decide whether to publish now or wait:

- If cheap techniques give your current result and the expensive techniques you are still developing would not substantially improve it, publish now.
- If the expensive techniques are likely to yield a meaningfully stronger result, wait until they mature. Two-paper strategies (an economical first paper that motivates a sophisticated sequel, possibly sharing lemmas) are sometimes the right answer.

## Conclusions / Final Remarks

### When to Include a Conclusion

**Only include a concluding section if it adds new insight.** A conclusion that merely restates the introduction is wasted space. If you have nothing to add beyond what the introduction and body already say, omit the section entirely.

### What Belongs in a Conclusion

**Discuss key ideas that emerged during the work.** Sometimes the process of proving a result reveals structural insights that were not apparent at the outset. The conclusion is the place to articulate these.

**State open problems and conjectures.** Be specific: "We conjecture that Theorem 3.5 extends to graphs of unbounded degree, provided the average degree grows sublinearly." Vague gestures ("It would be interesting to study this further") are less useful.

**Describe extensions and future directions.** "Our method applies to random regular graphs; it would be natural to ask whether a similar approach works for random bipartite graphs."

### Modern Formatting

**Consider titling the section "Final Remarks" or "Discussion" rather than "Conclusion."** Many authors use subsections within this section to separate open problems, conjectures, and methodological reflections.

## Appendices

### Purpose

**Use appendices for material that breaks the flow of the main text.** Long proofs of technical lemmas, extensive calculations, tables of computed values, and background material that only some readers need are all candidates.

### Self-Containment of the Main Text

**The main text must be self-contained.** Never write "the proof follows from Lemma A.3" in the body without stating Lemma A.3 (or at least its conclusion) in the body as well. A reader who skips the appendix should still be able to follow the main argument.

**Do not use notation in the main text that is only defined in the appendix.** All notation needed for the body must be introduced in the body.

### Referencing Appendix Material

When citing an appendix result in the main text, state the result informally and point to the appendix for the proof:

> The error term satisfies $|R_n| \le C/n^2$ (see Appendix A for the detailed calculation).

This pattern gives the reader the fact they need without forcing a detour.

## Structuring Checklist

Before finalizing a paper, verify:

1. The title is informative, concise, and symbol-free
2. The abstract is 3 to 6 lines, states results before methods, and contains no citations or definitions
3. The first sentence of the introduction leads with the specific subject, not "An X is Y"
4. The introduction frames the problem in the first paragraph
5. The introduction compares explicitly with the closest related work
6. Main results are stated informally in the introduction
7. A roadmap paragraph describes the paper's organization
8. Every section opens with an orienting sentence
9. Text reads correctly with section headings removed (headings are signposts, not part of the prose)
10. Sections are 1 to 3 pages; longer sections have subsections
11. Examples follow abstract results
12. The conclusion adds new insight (open problems, conjectures, reflections), not a summary
13. The main text is self-contained regardless of appendices
14. Appendix material is referenced from the body with a summary of the result
