
# Citations, References, and Journal Selection

Comprehensive reference for integrating citations into mathematical prose, providing specific and informative references, managing citation scope, and selecting journals. Based on Higham, Berndt, Cohn, Krantz, and Tao.

## Signposting Citations

### Integrate citations into prose

A citation should be part of a sentence, not a disconnected afterthought. The reader should understand who did what without consulting the bibliography.

**Good:** "Smith [3] showed that every compact operator on a Hilbert space has a non-trivial invariant subspace."
**Poor:** "It was shown that every compact operator on a Hilbert space has a non-trivial invariant subspace [3]."

The first version tells the reader immediately that Smith is responsible for the result. The second forces them to flip to the bibliography to find out.

### When bare numbers work

Higham notes that bare bracketed numbers serve well in survey-style passages where the point is breadth rather than attribution. In these contexts, naming every author would clutter the prose.

**Example:** "The matrix logarithm appears in applications ranging from reduced-order models [2] to image registration [8] and diffusion tensor imaging [15]."

Here the citations point the reader to further reading. The emphasis is on the breadth of applications, not on crediting individual contributors. This style works for lists of references but should not replace named citations when attribution matters.

### Parenthetical versus textual citations

In author-year systems (e.g., natbib, biblatex), distinguish between parenthetical and textual citations.

- **Textual:** "Knuth (1989) emphasized that..."
- **Parenthetical:** "This approach has been widely adopted (Knuth, 1989; Lamport, 1994)."

In numeric systems, the analogous distinction is between integrating the author's name into the sentence and placing the number at the end of a clause.

- **Integrated:** "Knuth [7] emphasized that..."
- **End-of-clause:** "This approach has been widely adopted [7, 12]."

### Citing multiple works

When citing multiple works together, order them logically. Common orderings: chronological (to show development of an idea), alphabetical (when order does not matter), or by relevance (most relevant first). Be consistent within a paper.

**Chronological:** "The problem was first posed by Euler [5], partially solved by Gauss [8], and fully resolved by Riemann [14]."
**By relevance:** "Our approach builds on the framework of Smith [3], with additional ideas from Jones [7] and Brown [1]."

## Specific References

### Theorem and page numbers

Berndt strongly advocates providing specific theorem numbers, page numbers, or section numbers when citing a result. This practice serves the reader who wants to verify a claim or read more context. It also demonstrates that the author has actually consulted the source.

**Specific:** "The result follows from the Hahn-Banach theorem [Rudin, Thm. 3.3, p. 59]."
**Vague:** "The result follows from the Hahn-Banach theorem [Rudin]."

The vague citation points to a 400-page book. The specific citation points to a single page.

### Citing textbooks versus research papers

When citing a textbook for a standard result, provide enough detail that the reader can locate the result quickly. When citing a research paper, the entire paper is typically relevant, so a bare citation may suffice. However, if you use only one theorem from a long paper, say which one.

### Informativeness as the primary purpose

Berndt argues that the primary role of a citation is to be informative, not to fulfill a scholarly duty. Every citation should answer a question the reader might have: "Where does this come from? Where can I learn more? Who deserves credit?" If a citation does not answer any of these questions, reconsider whether it belongs.

### Precise attribution

Give precise attribution for ideas and results, even when you paraphrase rather than quote. If your proof technique is adapted from another source, say so: "Our argument follows the strategy of [3, Theorem 2.1], with the modification that we replace the compactness argument by a direct construction." This is both honest and helpful.

### Paraphrase, do not copy

**Never reuse paragraphs verbatim from prior papers, even with attribution.** Mathematical prose should be in your voice, not stitched together from the voices of your sources. Copying, even honestly, produces a paper with inconsistent tone, awkward transitions, and a mismatch between the imported prose and the notation and framing of the current paper.

**Paraphrase and interpret.** Read the source carefully, then close it and write the passage in your own words, using your paper's notation and its level of detail. The paraphrase will usually be shorter (because you can skip whatever the source elaborated for its own purposes) and clearer in context (because you are writing to serve your argument, not its original argument).

**Cite adapted ideas explicitly.** Loose-attribution phrasings are standard and expected:

- "The proof here is loosely based on that of [5, Theorem 2.1]."
- "We follow the strategy of [3], with the modifications required to handle the non-compact setting."
- "The construction in Section 3 generalizes the one given by Smith [7] for the finite case."

The reader is told exactly what is borrowed and what is new, which is both honest and useful.

**Voice harmonization in coauthored papers.** When two or more authors draft different sections, the resulting draft will read as if written by different people, because it was. Designate one author as the "consistency pass" owner late in the revision cycle: their job is to read the whole paper and homogenize tone, rhythm, and word choice without changing the mathematics. A paper in a single coherent voice reads better than a technically identical paper in several voices.

## Citation Scope

### Avoiding over-citation

Cohn warns against over-citation. If a result is standard (known to your target audience), one reference to a textbook suffices. Piling up five references for a well-known fact suggests either insecurity or padding. Save multiple citations for results where the reader might genuinely benefit from seeing different treatments or perspectives.

**Over-cited:** "The Cauchy-Schwarz inequality [1, 3, 7, 12, 15, 22] implies that..."
**Appropriate:** "By the Cauchy-Schwarz inequality (see, e.g., [7, p. 42]), we have..."

### Bibliography depth and breadth

Krantz observes that a narrow bibliography is suspicious. If your paper touches on three distinct areas and your bibliography contains only papers from one of them, referees will question whether you have done a thorough literature search. Conversely, a bibliography stuffed with tangentially related works looks padded.

**Aim for:** citations that collectively cover (1) the direct antecedents of your work, (2) the competing or alternative approaches, and (3) the key background references a new reader would need.

### Proper attribution of ideas

All sources agree: attribute ideas and arguments properly, even when you paraphrase or adapt them. Mathematical culture values honest attribution, and failure to credit predecessors is both ethically problematic and practically costly (referees notice).

**Good:** "The key idea of encoding the constraint as a linear program is due to Dantzig [5]. We adapt his approach to the stochastic setting."
**Poor:** "We encode the constraint as a linear program." (With no mention that this idea originated elsewhere.)

### Using MathSciNet and other databases

Cohn recommends using MathSciNet (or zbMATH, Google Scholar, Semantic Scholar) for a thorough literature search before writing. A systematic search helps you discover related work you might have missed, ensure your results are genuinely new, and find the best references for standard results.

**Practical workflow:**

1. Search for your main keywords and key results
2. Check the "cited by" lists of the most relevant papers
3. Follow references backward through the foundational papers
4. Verify that your bibliography includes the essential prior work

## Journal Selection

### Honest self-assessment

Tao advises against automatically submitting to the most prestigious journal in your field. Instead, assess your work honestly across several dimensions before choosing a venue:

- **Correctness:** Is the proof complete and verified?
- **Novelty:** Does the result advance the field, or is it incremental?
- **Professionalism:** Does the paper meet professional standards of writing and presentation?
- **Presentation quality:** Is the exposition clear, well-organized, and accessible?

Higher scores across all dimensions suggest suitability for higher-tier journals. A paper that is correct and novel but poorly written will fare badly at a top journal, as will a beautifully written paper with incremental results.

### Matching editorial expertise

Check that at least one member of the journal's editorial board has expertise matching your paper's subject area. A paper in combinatorial number theory submitted to a journal whose board consists entirely of analysts is unlikely to receive a fair or efficient review, regardless of the paper's quality.

### Reviewing sample issues

Before submitting, browse recent issues of the journal. Do the papers resemble yours in scope, length, and level of technical detail? If every paper in the journal is 50 pages and yours is 8, or if every paper uses techniques from algebraic geometry and yours is purely combinatorial, the fit may be poor.

### Multiple submissions to the same journal

Tao notes: do not submit two unrelated papers to the same journal simultaneously. This places an undue burden on the editor, who must find referees for both papers at once, and it can create the impression that you are flooding the journal.

### Rejection and resubmission

Rejection is a normal part of mathematical publishing. It does not necessarily mean the paper is bad; it may mean the paper is not right for that particular journal, or that the exposition needs improvement. Use referee reports constructively:

1. Read the report carefully, setting aside initial defensiveness
2. Address every concern, either by revising the paper or by explaining (in a cover letter) why you disagree
3. Improve the exposition based on any points of confusion the referee identified
4. Resubmit to an appropriate journal (the same one if the editor invited resubmission, or a different one if the rejection was firm)

### Pricing and accessibility

Tao suggests factoring in pricing and accessibility when selecting a venue. Open-access journals, journals with reasonable page charges, and journals whose publishers offer preprint-friendly policies all increase the reach and impact of your work. When two journals are otherwise comparable, prefer the one that makes your paper more accessible to the community.

## Quick Reference: Citation Practices

| Practice | Example |
|---|---|
| Named citation | "Smith [3] proved that..." |
| Bare citation for surveys | "...in applications [2, 8, 15]" |
| Specific reference | "[Rudin, Thm. 3.3, p. 59]" |
| Standard result | One textbook reference suffices |
| Adapted technique | "Our argument follows [3, Thm. 2.1], with..." |
| Over-citation | Avoid listing 5+ refs for a well-known fact |
| Attribution | Credit ideas even when paraphrasing |

## Sources

- Tao, T. "Advice on Writing Papers" (Submit to Appropriate Journal, Write in Your Own Voice). terrytao.wordpress.com.
- Higham, N. J. *Handbook of Writing for the Mathematical Sciences*. SIAM.
- Berndt, B. C. "How to Write Mathematical Papers." UIUC.
- Cohn, H. "Advice." cohn.mit.edu.
- Krantz, S. G. "How to Write Your First Paper." AMS, 2007.
