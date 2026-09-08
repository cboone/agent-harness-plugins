# Reader-Centered Mathematical Writing

Comprehensive reference for writing mathematics that serves the reader. Covers audience calibration, examples and intuition, signposting, assertion status, handling definitions, recalling earlier material, and minimizing complexity. Based on Goldreich, Pak, Lee, Cohn, Tsitsiklis, Tao, Poonen, and MIT course notes.

## Audience Calibration

### The default reader

Write for a graduate student who is beginning studies in your field. This reader is intelligent, has basic mathematical maturity, and knows the standard background of the area, but nothing more. Do not assume familiarity with the specific problem, the history of your particular line of research, or any unpublished conventions used in your research group.

This calibration serves two purposes. First, it forces you to spell out enough detail that a competent non-expert can follow the argument. Second, it prevents condescension toward experts, because a well-structured paper at this level remains pleasant to read for specialists.

### Assume intelligence, not knowledge

Goldreich emphasizes: assume the reader is intelligent but knows only the standard background. If you introduce a concept beyond that background, define it. If you use a result from a neighboring field, state it or cite a precise reference. The goal is not to write a textbook, but to close every gap that would force the reader to guess.

### Calibrate detail to the reader's likely knowledge

Audience calibration determines _who_ you are writing for. Detail calibration determines _how much_ you write about each piece of the argument. These are separate decisions, and the second one is easier to get wrong, because authors tend to overexpose the material they know best and skim the material they consider obvious.

**Standard results get brief treatment.** If a lemma is well known to experts in the field and already in the literature, do not reprove it or work through its consequences in detail. A one-sentence reminder and a precise citation is enough:

> By the Hahn-Banach theorem [Rudin, Thm. 3.3, p. 59], the functional $\varphi$ extends to all of $X$.

The reader who knows the theorem skims the sentence; the reader who does not knows exactly where to look.

**Unfamiliar material gets expanded, even when "obvious" to you.** Computations, definitions, or conventions that are not widely known in your target field should be written out, even if years of work have made them second nature to you. The expansion costs a paragraph; leaving it out forces every reader to reconstruct your private knowledge.

**Cite obscure results precisely.** When you reach for a lemma from your own earlier work or from a long and technical paper, never write "by a lemma in [my previous 100-page paper]." Give the exact theorem or lemma number, the page if the document is long, and (when helpful) a one-line paraphrase of the statement so the reader does not need to fetch the reference to follow the local argument.

**Sketch crucial proofs.** For a lemma whose proof genuinely matters to the story (the key idea, the crucial trick, the step the rest of the paper balances on), a paragraph-length sketch is worth the space even if the full proof lives elsewhere. Sketches let the reader understand what is happening without having to open another paper.

**Anchor: Littlewood on "momentary points."** Littlewood wrote that the educated reader should "catch on at once to the momentary point and take details for granted." Detail calibration is the writer's side of this: what you elaborate should be what the reader needs to catch the momentary point, and the rest should be compressed so it does not dilute the signal.

### Put yourself in the reader's shoes

Lee recommends imagining a reader who has not worked on this problem. They do not carry the context that you spent weeks accumulating. Ask yourself at each step: "Would I understand this paragraph if I were reading it for the first time?" If the answer is uncertain, add a sentence of motivation or a forward pointer.

### Generality versus clarity

Pak advises against presenting results in maximum generality when a special case would be clearer first. A common and effective pattern: state and prove a concrete version, then explain how the argument generalizes. The reader who understands the special case will have the intuition needed to absorb the general statement. The reader who encounters the general statement cold may have neither.

### Minimize new concepts

Goldreich observes that the reader's capacity for absorbing new definitions is bounded. Every new concept imposes a cognitive cost. Before introducing a definition, ask whether it earns its place. If a concept appears only once, consider inlining it. If two concepts can be unified under a single abstraction, do so. The fewer names the reader must track, the more attention they can devote to your argument.

## Examples and Intuition

### Concrete examples before general statements

Every source agrees on this principle: present at least one concrete example before (or immediately after) a general definition or theorem. The example gives the reader a mental picture that anchors the abstraction. Without it, definitions float free and theorems feel unmotivated.

**Pattern:** "Consider the case when $n = 2$. Here the matrix $A$ is simply... [work through the example]. More generally, for arbitrary $n$, we have the following."

### Counterexamples

Pak stresses the value of counterexamples. When a theorem requires a particular hypothesis, show what goes wrong without it. This serves three functions: it validates the hypothesis (it is not an artifact of the proof method), it deepens the reader's understanding, and it helps the reader remember the result.

**Example:** "The conclusion of Theorem 3.1 fails without the compactness assumption. Consider $X = (0,1)$ with the standard topology. The sequence $x_n = 1/n$ has no convergent subsequence in $X$, demonstrating that compactness cannot be dropped."

### Why results fail

Beyond counterexamples, explain at the intuitive level why assumptions are needed. "The compactness assumption ensures that we can extract a convergent subsequence. Without it, the iterative construction in Step 3 may not terminate." This kind of explanation costs one sentence and saves the reader from wondering whether the hypothesis is an artifact.

### Diagrams and illustrations

Diagrams provide intuition that words and symbols cannot. A commutative diagram, a graph of a function, or a picture of a geometric configuration can replace paragraphs of verbal description. When the subject admits a visual representation, include one.

### Running examples

Pak recommends using a single running example that recurs throughout the paper. Each time a new concept is introduced, the reader sees it instantiated in a familiar setting. This technique is especially effective in papers that build up a complex framework incrementally.

### Self-contained captions

Tsitsiklis notes that figure captions should be substantial and self-contained. Many readers skim a paper by looking at figures and reading their captions. A caption that says "Figure 3: Results" wastes this opportunity. A caption that says "Figure 3: Convergence rate of Algorithm 1 for three choices of step size. The dashed line shows the theoretical lower bound from Theorem 2.4." gives the skimming reader genuine information.

## Signposting

### Structural repetition

Goldreich recommends mentioning every key idea three times: once in the abstract, once in the introduction, and once in the body where it is developed fully. This is not redundancy; it serves different readers at different levels of engagement. The abstract reader gets the headline. The introduction reader gets the context. The body reader gets the details.

### Headings and subheadings as navigation

Use headings and subheadings as signposts, not decorations. A heading should tell the reader what the section accomplishes, not merely label it. "Bounding the spectral gap" is more informative than "Technical lemma." Goldreich advises that every section should open by explaining what comes next and how it fits into the overall argument.

### Explicit transitions

Signal transitions between topics explicitly. Phrases like "We now turn to the proof of the upper bound" or "Having established the necessary algebraic machinery, we prove the main theorem" orient the reader. Without them, the reader must deduce the logical flow from context, which is taxing and error-prone.

**Good practice:**

- "In this section, we prove Theorem 1.2. The argument has two steps: first we establish a reduction to the finite case (Lemma 3.1), then we handle the finite case directly (Lemma 3.2)."
- "We now change perspective. Rather than analyzing the algorithm directly, we study the dual problem."

**Poor practice:**

- A section that begins with "Let $G$ be a graph..." without explaining why graphs have appeared or what the section will accomplish.

### Section openings

Every section should begin with a brief paragraph that orients the reader. State what the section will accomplish, how it connects to what came before, and (if applicable) what the main difficulty or key idea is. This paragraph costs a few sentences and saves the reader from disorientation.

## Assertion Status

### Making status explicit

Pak insists that the reader must always know the logical status of every assertion. Is this a definition, a theorem, a lemma, a conjecture, a remark, a heuristic claim, or an assumption made for convenience? Ambiguity about status is one of the most common sources of confusion in mathematical writing.

**Clear:** "We conjecture that the bound in Theorem 3.1 is tight."
**Ambiguous:** "The bound in Theorem 3.1 is probably tight." (Is this a formal conjecture? An informal observation? A claim the author will prove later?)

### Visual formatting for definitions

Poonen recommends using formatting (definition environments, boxes, extra vertical spacing) to make definitions easy to locate when the reader flips back to find them. A definition buried in the middle of a paragraph is effectively invisible to a reader who is scanning.

### Marking newly defined terms

When a term is defined for the first time, mark it with italics or boldface. This convention is nearly universal in mathematics, and readers rely on it. If they see an unfamiliar term in roman type, they assume it was defined earlier and they missed it; if they see it in italics, they know this is the definition.

**Pattern:** "A group $G$ is called _residually finite_ if for every non-identity element $g \in G$, there exists a homomorphism $\varphi$ from $G$ to a finite group such that $\varphi(g) \neq e$."

### Distinguishing standard from new

When you use a term or result, make clear whether it is standard in the field, borrowed from another source, or original to your paper. Readers need this information to calibrate their expectations. A standard result can be cited without proof. A borrowed result needs a reference and perhaps a brief statement. A new result needs a full proof.

## Handling Definitions

### Precision is non-negotiable

Lee emphasizes that a definition must be truly precise, not vague or hand-wavy. "A large graph" is not a definition. "A graph on $n$ vertices with minimum degree at least $n/2$" is a definition. If you find yourself unable to make a definition precise, you may not yet understand the concept well enough to write about it.

### Good definitions hide difficulty

Goldreich observes that good definitions capture and hide the main difficulty of a subject. The right definition makes theorems easy to state and proofs natural. If your theorems are awkward to state, consider whether the problem lies in your definitions rather than in the results themselves.

### Discussing definitional choices

Pak advises discussing your definitional choices explicitly. Are they arbitrary conventions? Simplifying assumptions that could be relaxed? Essential features of the problem? The reader who understands why you made a particular choice is better equipped to evaluate your results and to adapt them.

**Example:** "We define convergence with respect to the $L^2$ norm. The choice of norm matters: Theorem 4.1 fails for the $L^\infty$ norm (see Remark 4.3), but holds for any $L^p$ norm with $p < \infty$ by a straightforward modification of the argument."

### Motivation for assumptions

Explain why each assumption is present. Pak and Goldreich both stress this point. "We assume $f$ is Lipschitz continuous" raises the question: is this for convenience, or is it essential? A sentence like "The Lipschitz condition is used in Step 2 to ensure that the Picard iterates converge; see Remark 3.5 for a counterexample when $f$ is merely continuous" answers the question definitively.

### State definitions twice in complementary ways

When introducing a definition, give two complementary descriptions: one formal and one informal, or one symbolic and one verbal. This dual statement reinforces the reader's understanding and helps readers with different backgrounds latch onto the meaning. For example, when defining $N^n$ as the set of $n$-tuples of nonnegative integers, also describe the subset $A_n$ as "nonincreasing" vectors. When defining $L(C, P)$, characterize it both by the formula and as "the smallest subset of $N^n$ that contains $C$ and is closed under the addition of elements of $P$." The two descriptions illuminate each other.

### Placement of definitions

State definitions at the start of a line or sentence, never buried mid-sentence. The reader scanning for a definition should be able to find it by looking at sentence beginnings and environment labels.

**Good:** "We say that a metric space is _proper_ if every closed bounded subset is compact."
**Poor:** "Since every closed bounded subset of a proper metric space is compact, we can apply..."

The second example uses "proper" before defining it, and the definition is syntactically subordinate to another clause.

## Recalling Earlier Material

### The distant-definition problem

Goldreich warns against referencing a term or symbol defined many pages earlier without a brief reminder. By the time the reader reaches page 15, they may not remember a definition from page 3. A short parenthetical costs almost nothing and prevents a frustrating backward search.

**Pattern:** "Recall that $c_n = n / \log n$ (cf. Eq. (3.2))."
**Pattern:** "Since $G$ is residually finite (Definition 2.1), we can find a finite quotient..."

### Answering implicitly raised questions

Pak notes that every statement in a paper implicitly raises questions. If you state a theorem with a particular hypothesis, the reader wonders whether the hypothesis is necessary. If you define a quantity, the reader wonders whether it is computable. If you implicitly raise a question and never address it, the reader is left with an unsatisfying gap. Either answer the question or explicitly acknowledge it as open.

### Using earlier unclear remarks to resolve later confusion

Tao offers practical advice for both writers and readers: if you encounter an unexplained deduction in a proof, look back at any earlier remark or aside that seemed unclear at the time. Often, the earlier remark contains a hypothesis or observation that the author intended to use at exactly this point but failed to make the connection explicit. As a writer, the lesson is: when you plant a seed for later use, make the forward reference explicit.

**Good:** "We record the following estimate for later use in the proof of Theorem 5.1."
**Poor:** "We note that $|f(x)| \leq C$." (With no indication of why this observation matters or where it will be used.)

## Minimizing Complexity

### Clear antecedents

Goldreich warns against a "labyrinth of implicit pointers." Pronouns like "it," "this," and "that" must have clear, unambiguous antecedents. When in doubt, repeat the noun.

**Ambiguous:** "We apply the theorem to the sequence and the limit, and it shows that it converges."
**Clear:** "We apply Theorem 3.1 to the sequence $(a_n)$. The theorem shows that $(a_n)$ converges to $L$."

### Separating symbols and prose

Goldreich advises against mixing mathematical symbols and prose in ways that create parsing ambiguity. A sentence like "Since $f$ $g$ $h$ are continuous" forces the reader to determine where the symbol list ends and the predicate begins. Use commas and write "Since $f$, $g$, and $h$ are continuous."

### Hierarchical structure

Pak recommends using headings to create a visual hierarchy where important ideas stand out and secondary discussions (remarks, technical details, historical notes) are clearly marked as subordinate. This lets different readers engage at different levels of detail without losing the main thread.

**Structural hierarchy example:**

- **Section heading:** names the main result or topic
- **Subsection heading:** names a component of the argument
- **Remarks and notes:** flagged as such, indented or set in a different environment
- **Technical lemmas:** grouped together, preceded by a sentence explaining their collective purpose

### Controlling information flow

Present information in the order the reader needs it. A forward reference ("as we will see in Section 5") is acceptable for motivation, but the reader should never need to read Section 5 before understanding Section 3. If they do, your sections are in the wrong order.

## Quick Reference: Principles at a Glance

| Principle            | Action                                                 |
| -------------------- | ------------------------------------------------------ |
| Audience             | Write for a beginning graduate student in the field    |
| Examples first       | Concrete instance before general definition            |
| Counterexamples      | Show what fails without each hypothesis                |
| Signpost three times | Abstract, introduction, body                           |
| Section openings     | State what comes next and why                          |
| Assertion status     | Definition, theorem, conjecture: always explicit       |
| Definition placement | Start of sentence or environment, never buried         |
| Recall earlier terms | Parenthetical reminders for distant definitions        |
| Clear antecedents    | Repeat nouns rather than relying on pronouns           |
| Hierarchy            | Headings distinguish main ideas from secondary details |

## Sources

- Goldreich, O. "How to Write a Paper."
- Pak, I. "How to Write a Clear Math Paper: Some 21st Century Tips."
- Lee, K. P. "A Guide to Writing Mathematics." MIT.
- Cohn, H. "Advice." cohn.mit.edu.
- MIT 18.821. "Notes on Writing Mathematics."
- Tsitsiklis, J. N. "A Few Tips on Writing Papers with Mathematical Content."
- Tao, T. "Advice on Writing Papers" (Give Appropriate Amounts of Detail). terrytao.wordpress.com.
- Poonen, B. "Practical Suggestions for Mathematical Writing." MIT.
