
# English Usage in Mathematical Writing

Mathematics is communicated in English (or another natural language), not in pure symbols. The quality of the English directly affects the reader's ability to understand the mathematics. The principles below, drawn from Tao, Trzeciak, Wang, Poonen, Su, Berndt, and MIT writing resources, cover logical connectives, sentence construction, word choice, common errors, the integration of symbols into prose, and punctuation of mathematical expressions.

## Logical Connectives and Transitional Language

### Choosing the Right Connective

English connectives carry logical meaning. Choose them deliberately:

| Connective | Logical role | Example |
|---|---|---|
| since, because | cause/reason (premise to conclusion) | "Since $f$ is continuous, it is bounded on $[0,1]$." |
| therefore, thus, hence | conclusion (follows from above) | "The set is closed and bounded; therefore it is compact." |
| in particular | specialization (key consequence) | "Every compact set is bounded. In particular, $K \subset [-M, M]$." |
| moreover, furthermore | addition (new supporting fact) | "The function is differentiable. Moreover, its derivative is Lipschitz." |
| however, on the other hand | contrast or qualification | "The bound is tight for $n = 2$. However, for $n \ge 3$, we can improve it." |
| also | neutral addition | "The map is injective. It is also surjective." |
| namely | clarification/restatement | "There is exactly one fixed point, namely $x = 0$." |
| recall that | reminder of earlier fact | "Recall that $G$ is assumed to be abelian." |

**Do not use "since" for temporal sequence in mathematical writing.** Reserve it for logical causation. Write "After establishing Lemma 2, we turn to..." for temporal ordering, and "Since Lemma 2 gives us a bound on $|G|$, we can now..." for logical dependence.

### Contextual Modulation

**Use connectives to signal the weight of a step.** "In particular" tells the reader that the upcoming statement is an especially important consequence. "Trivially" or "immediately" signals that the step requires no real work. "The key observation is that..." marks the intellectual crux of the argument.

### Plain Language

**Replace obscure words with plainer equivalents.** The goal of mathematical writing is communication, not impression. "Use" is better than "utilize." "Show" is better than "elucidate." "Enough" is better than "sufficient" in informal discussion (though "sufficient" has a precise meaning in formal statements).

## Sentence Structure

### Short Sentences

**Break long sentences into multiple short ones.** Mathematical content is already dense. Long sentences with multiple clauses force the reader to hold too much in working memory.

Bad: "Since the function $f$ is continuous on the compact set $K$, and since $K$ is a subset of the domain of $g$, which is also continuous, we can apply the composition theorem to conclude that $g \circ f$ is continuous on $K$, which in turn implies, by the extreme value theorem, that $g \circ f$ attains its maximum on $K$."

Good: "The function $f$ is continuous on the compact set $K$. Since $K \subset \operatorname{dom}(g)$ and $g$ is also continuous, the composition $g \circ f$ is continuous on $K$. By the extreme value theorem, $g \circ f$ attains its maximum on $K$."

### Parallel Construction

**Use parallel grammatical structure in lists and comparisons.** When listing properties or steps, keep the grammatical form consistent.

Bad: "The map is injective, has a dense image, and we show it preserves the norm."
(Mixes adjective, verb phrase, and independent clause.)

Good: "The map is injective, has dense image, and preserves the norm."
(Three parallel verb phrases.)

### Active Voice with "We"

**Use "we" (author and reader together) as the default subject.** This convention is universal in mathematical writing. "We" invites the reader to participate in the argument: "We now show that $f$ is bounded." "We apply Lemma 3.2 to obtain..."

**Avoid "I" unless the paper is single-authored and you are expressing a personal opinion:** "I believe this conjecture is true, though I have not been able to prove it."

**Avoid impersonal "one":** "One can show that..." sounds stilted. Prefer "We can show that..." or the direct "The following argument shows that..."

### Reading Aloud

**Read your sentences aloud.** If a sentence is hard to say, it is hard to read. Stumbling points in speech correspond to parsing difficulties on the page. Also try reading at speed: skimming your own prose reveals rhythm problems that are invisible at a careful, word-by-word pace.

### Orwell's Four Questions

Tao cites Orwell's checklist for every sentence a writer commits to the page:

1. What am I trying to say?
2. What words will express it?
3. What image or idiom will make it clearer?
4. Is this image fresh enough to have an effect?

In mathematical writing the fourth question is especially useful as an anti-cliché filter: stock phrases ("it is well known that," "in a certain sense") rarely carry information and often hide the fact that the writer has not yet decided what the sentence should say.

## Word Choice

### Precision over Variety

**Repeating a word is better than using an inexact synonym.** If you have been calling something a "bound" throughout, do not suddenly switch to "estimate" or "constraint" for variety. Synonyms suggest distinctions. If no distinction is intended, repetition is clearer.

**Use a dictionary, not a thesaurus.** A thesaurus finds words with similar meanings, but similar is not identical. "Adequate" and "sufficient" are near-synonyms, but "adequate" connotes "barely enough" while "sufficient" is neutral. In mathematical writing, such connotative differences can mislead.

**Space "sticky" words apart.** Words like "this," "also," and unusual or polysyllabic terms tend to linger in a reader's mind longer than ordinary words. When the same sticky word appears in consecutive sentences, it creates an unintended echo. Good style keeps such words spaced well apart.

### Words to Avoid

**Avoid "easy," "trivial," "obvious," and "clearly" unless you can justify why.** These words dismiss the reader's potential difficulty. If something is truly obvious, it needs no label. If it is not obvious, the label insults the reader. Replace with a brief justification:

Bad: "It is obvious that $f$ is continuous."
Good: "Since $f$ is a polynomial, it is continuous."

Bad: "The result follows trivially."
Good: "The result follows by applying the triangle inequality."

**Avoid informal verbs in formal writing.** Prefer "obtain" over "get," "establish" over "have," "deduce" or "derive" over "receive." Write "we obtain the bound $|f(x)| \le M$" rather than "we get the bound."

### Jargon

**Avoid jargon unless necessary.** If a technical term is essential, define it at first use. If a simpler term conveys the same meaning to your audience, prefer it. Even specialists get more pleasure from papers that use a nonspecialist's vocabulary.

**Avoid noun-string adjectives.** Long chains of nouns used as modifiers are hard to parse: "the packet switched data communication network protocol problem" forces the reader to determine which nouns modify which. Break the chain with prepositions: "the protocol problem for packet-switched data communication networks."

### Precise Quantifier Words

**Prefer "each" or "every" over "any."** In English, "any" is ambiguous between universal and existential quantification:

- "Does any $x$ satisfy $P(x)$?" (existential: is there at least one?)
- "Any $x$ satisfies $P(x)$." (universal: all of them do)

In mathematical writing, eliminate the ambiguity by using "each" or "every" for universal claims and "some" for existential claims. Reserve "any" for negated or interrogative contexts where English idiom demands it ("there is no $x$ with any of these properties").

**Reserve "equivalent" for precisely stated equivalences.** When two statements are formally equivalent (each implies the other), "equivalent" is the right word. When two expressions are merely interchangeable or yield the same numerical value, prefer "equal" or "the same as." Using "equivalent" loosely invites the reader to hunt for a formal equivalence that is not there.

**Avoid "where" clauses as afterthoughts.** A trailing "where $f$ is continuous" smuggles a hypothesis into the middle of a sentence and makes it easy for the reader (and the writer) to miss that an assumption has been introduced. Move the hypothesis to the front ("Let $f$ be continuous. Then...") or into the explicit premises of a theorem or lemma.

### Tense Consistency

**Maintain present tense for mathematical statements.** Write "Theorem 3.1 shows that $X$," not "Theorem 3.1 showed that $X$." Mathematical facts are timeless, and the present tense reinforces that the reader can apply them here and now.

**Reserve past tense for historical attribution.** "Euler proved in 1736 that $X$" uses past tense correctly; "Euler's argument shows that $X$" returns to the present tense when stating the substantive content. When revising, search a draft for "-ed" endings and "will" and convert stray past or future tense to present unless the sentence is genuinely about history or anticipated future work.

### Write Proofs Forward

**Present the logical chain in the order the reader encounters it.** Premises come first, intermediate deductions follow, and the conclusion comes last. Backwards proofs ("to prove $C$, it suffices to prove $B$; to prove $B$, it suffices to prove $A$; now $A$ is clear") force the reader to hold an unresolved goal in working memory until the very end. Forward proofs ("$A$ is clear, so we have $B$, which gives $C$") let each sentence stand on its own.

There are situations where a backward framing is unavoidable (notably when the conclusion is complex and the reader needs to see where the argument is heading), but these should be exceptions, and when they occur the writer should explicitly signpost the structure: "We work backwards from the desired conclusion."

### Phrasing Proof by Contradiction

**When contradiction is necessary, use forward-flowing phrasing.** Avoid "Assume by contradiction that $\langle$blah$\rangle$," which front-loads the negated conclusion before the reader knows the proof strategy. Better alternatives:

- "The proof that $\langle$blah$\rangle$ is by contradiction."
- "To prove $\langle$grunt$\rangle$, let us assume the opposite and see what happens."

These phrasings tell the reader the strategy before asking them to hold a negated hypothesis in working memory. See also the discussion of direct proofs in `theorems-and-proofs.md`.

## Common Errors

### Ambiguous Pronouns

**Avoid ambiguous "it" and "this."** After a complex sentence or paragraph, "this" can refer to several things. Repeat the noun or provide a summary noun.

Bad: "We proved that $f$ is continuous and $g$ is bounded. This implies compactness."
(What does "this" refer to? The continuity of $f$? The boundedness of $g$? Both together?)

Good: "We proved that $f$ is continuous and $g$ is bounded. The boundedness of $g$ implies compactness."
Or: "These two properties together imply compactness."

### That vs. Which

**"That" introduces a restrictive (essential) clause; "which" introduces a non-restrictive (descriptive) clause set off by commas.**

Restrictive: "The function that maps $x$ to $x^2$ is convex."
(Identifies which function.)

Non-restrictive: "The square function, which maps $x$ to $x^2$, is convex."
(Provides additional information about an already-identified function.)

Test: if the clause can be removed without changing the sentence's core meaning, use "which" with commas. If removing it changes the meaning, use "that" without commas.

### Comma Splices

**Do not join two independent clauses with only a comma.** This is a comma splice.

Bad: "The set is infinite, we pick a finite subset."

Correct alternatives:

- "The set is infinite. We pick a finite subset." (period)
- "The set is infinite; we pick a finite subset." (semicolon)
- "The set is infinite, so we pick a finite subset." (comma + coordinating conjunction)
- "Since the set is infinite, we pick a finite subset." (subordination)

### Dangling Participles

**Ensure participial phrases modify the correct subject.**

Bad: "Solving the equation, the roots are real."
(Grammatically, the roots are solving the equation.)

Good: "Solving the equation, we find that the roots are real."
Or: "When we solve the equation, the roots turn out to be real."

### Don't Omit "That"

**Include "that" after "assume" and "suppose" for parsing clarity.** The word "that" helps the reader identify where the hypothesis begins. Without it, the sentence momentarily parses as a different construction.

Bad: "Assume $A$ is a group."
Good: "Assume that $A$ is a group."

The words "assume" and "suppose" should usually be followed by "that" unless another "that" appears nearby, in which case the double "that" sounds awkward and the first may be dropped.

**Exception: never write "We have that."** The phrase "We have that $x = y$" is ungrammatical in English. Write "We have $x = y$" (the equation is the direct object) or "We see that $x = y$."

### Quantifier Ambiguity in English

**Make the scope of quantifiers unmistakable.**

Ambiguous: "For every $n$, we have $f(n) < C$, for some constant $C$."
(Does $C$ depend on $n$, or is $C$ universal?)

Clear (universal $C$): "There exists a constant $C$ such that $f(n) < C$ for every $n$."
Clear (dependent $C$): "For every $n$, there exists a constant $C_n$ such that $f(n) < C_n$."

## Symbols in Prose

### Symbols to Never Use in Formal Writing

**Write out the following in words; do not use their symbolic forms in running text:**

| Symbol | Write instead |
|---|---|
| $\forall$ | "for all" or "for every" |
| $\exists$ | "there exists" |
| $\wedge$ | "and" |
| $\vee$ | "or" |
| $\Rightarrow$ | "implies" or "if...then" |
| $\Leftrightarrow$ | "if and only if" |
| $\neg$ | "not" |
| s.t. | "such that" |

**The symbol $\in$ is acceptable in formal writing:** "Let $x \in \mathbb{R}$" is standard and reads naturally.

### Abbreviations to Spell Out

In formal writing, spell out:

- "without loss of generality" (not "WLOG")
- "if and only if" (not "iff")
- "such that" (not "s.t.")
- "left-hand side" and "right-hand side" (not "LHS" and "RHS")
- "with respect to" (not "w.r.t.")

These abbreviations are acceptable in blackboard lectures and personal notes but not in published papers.

### Contractions

**Do not use contractions in formal mathematical writing.** Write "does not" instead of "doesn't," "cannot" instead of "can't," "it is" instead of "it's."

## Punctuation of Mathematics

### Displayed Equations as Sentences

**Displayed equations are part of the sentence.** Punctuate them accordingly.

If the sentence ends with the equation, place a period after it:
> The quadratic formula gives
> $$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}.$$

If the sentence continues after the equation, place a comma:
> Since
> $$f(x) = x^2 + 1,$$
> we have $f(x) \ge 1$ for all $x$.

### No Colon Before Equations That Complete the Sentence

**Do not insert a colon before a displayed equation that grammatically completes the introductory clause.** The clause and the equation form one sentence; a colon breaks it.

Bad: "We define the set of nonincreasing vectors:"
(followed by a displayed equation)

Good: "We define the set of nonincreasing vectors,"
(followed by a displayed equation)

A colon is correct only when the display is introduced as a list or apposition: "We consider two cases:" followed by a numbered display.

### Tie Formulas into Running Commentary

**Do not list a sequence of formulas without connecting prose.** A chain of displayed equations with no words between them reads like a homework solution, not a mathematical argument. Each formula should be introduced, and its role or derivation explained, even if the explanation is only a few words ("Substituting into (3), we obtain" or "Combining these two bounds gives").

### Equals Sign Is Not a Verb

**Do not use "=" as a verb in a sentence.**

Bad: "If $n$ is odd, $n = 2k + 1$."
(This reads as two separate assertions with no logical connection.)

Good: "If $n$ is odd, then $n = 2k + 1$ for some integer $k$."
(The "then" creates a proper conditional structure.)

### If...Then Structure

**Always include "then" in conditional statements for parsing clarity.** Without "then," the reader may not know where the hypothesis ends and the conclusion begins.

Bad: "If $f$ is continuous, $f$ is integrable."
Good: "If $f$ is continuous, then $f$ is integrable."

This is especially important in complex statements: "If $f$ is continuous on $[a,b]$ and differentiable on $(a,b)$, then there exists $c \in (a,b)$ such that $f'(c) = \frac{f(b) - f(a)}{b - a}$."

### "Since" for Logic, Not Time

**"Since" indicates a logical relationship (because), not a temporal one (from that time onward).** In mathematical writing, "since $f$ is continuous" means "because $f$ is continuous." For temporal sequence, use "after" or "once": "After establishing the bound, we turn to the convergence argument."

### Never Start a Sentence with a Symbol

**Do not begin a sentence with a mathematical symbol.** The visual break between the period ending one sentence and the symbol starting the next is too small, causing the reader to run sentences together.

Bad: "$f$ is continuous on $[0,1]$."
Good: "The function $f$ is continuous on $[0,1]$."

Bad: "$n$ is assumed to be odd."
Good: "The integer $n$ is assumed to be odd."

If restructuring is awkward, add a descriptive word: "Here $f$ denotes the characteristic function."

## Notes for Non-Native English Speakers

**Trzeciak's "Writing Mathematical Papers in English" (EMS, 1995) is an invaluable reference.** It covers the specific patterns of English that cause difficulty for non-native speakers writing mathematics:

- **Articles (a/an/the):** "Let $G$ be a group" (introducing), "the group $G$" (referring back). Omission of articles is the most common error in non-native mathematical English.
- **Prepositions:** "a function on $X$", "a bound for $f$", "convergence to $L$", "independent of $n$". These are largely idiomatic and must be learned individually.
- **Word order:** English places adjectives before nouns ("a continuous function") and adverbs before the verb or at the end ("we quickly obtain" or "we obtain the result quickly").

## Summary Checklist

Before submitting, verify:

1. Logical connectives accurately reflect the relationship between statements
2. Sentences are short enough to parse in a single reading
3. "We" is the default subject; "I" and "one" are rare
4. No ambiguous pronouns ("it," "this") without clear antecedents
5. "That" and "which" are used correctly (restrictive vs. non-restrictive)
6. No comma splices or dangling participles
7. Quantifier scope is unambiguous in every statement
8. Logical symbols ($\forall$, $\exists$, $\Rightarrow$, etc.) do not appear in running text
9. Abbreviations (WLOG, iff, s.t.) are spelled out
10. Displayed equations are punctuated as part of the sentence
11. No colon before a displayed equation that completes the sentence
12. Formulas are tied into running commentary, never listed without connecting prose
13. "If...then" conditionals always include "then"
14. "That" follows "assume" and "suppose" (but never "We have that")
15. No sentence begins with a mathematical symbol
16. No contractions appear in formal text
17. "Since" is used for logic, not temporal sequence
