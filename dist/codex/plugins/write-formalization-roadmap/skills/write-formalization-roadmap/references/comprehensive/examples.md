
# Annotated Examples

Fragments of working formalization roadmaps, annotated to show how the 10-section schema, the 5-part milestone anatomy, and the mandated conventions show up in practice.

Primary source: `cboone/zhang-yeung-inequality/docs/plans/todo/2026-04-15-zhang-yeung-formalization-roadmap.md`. Secondary source: `cboone/shannon-entropy/docs/plans/todo/2026-04-14-shannon-proofs-roadmap.md`.

## Example 1: Opening a Roadmap (Section 1, Context)

```markdown
# Zhang-Yeung Inequality Formalization Roadmap

**Created:** 2026-04-15
**Target:** Lean 4 / Mathlib 4
**Paper:** Zhang & Yeung, "On Characterization of Entropy Function via
  Information Inequalities," *IEEE TIT* 44(4), July 1998, pp. 1440-1452.
**Source PDF:** `references/papers/zhangyeung1998.pdf`
**Source transcription:** `references/transcriptions/zhangyeung1998.md`
  (verified 2026-04-16)

**Resolved decisions:**

- **Scope:** S2 + Theorem 5 (stretch). Theorems 3, 4 as core; Theorem 5
  (n+2-variable generalization) as stretch.
- **Dependency:** Permanent PFR dependency for Shannon entropy primitives.
- **Blueprint:** No. Lean-only.
- **Mathlib intent:** Copy lemma yes (designed for upstream). Rest stays local.

## 1. Context

The Zhang-Yeung inequality is the first known *non-Shannon-type*
information inequality. ...
```

**What this does well.**

- Paper identity block above Section 1: authors, venue, year, pages, PDF path, transcription path with verification date. A cold reader can orient instantly.
- Resolved decisions block surfaces the four highest-leverage scope decisions up front. Future sessions do not have to dig through Section 4 to know what is settled.
- Section 1 opens with the paper's place in the field ("first known non-Shannon-type inequality") before any file paths.

**Where a weaker version would slip.**

- No paper identity block. Section 1 would have to carry it.
- No resolved decisions summary. Readers would have to scan Section 4 to learn the scope choices.
- Opens with implementation details rather than context.

## Example 2: State of the Art (Section 2)

```markdown
## 2. State of the Art

### 2.1 Mathlib 4

Already upstream and directly usable (verified 2026-04-15):

- `Mathlib.MeasureTheory.Measure.ProbabilityMeasure`,
  `Mathlib.Probability.Distributions.Uniform` (finite-support RVs via
  `PMF`).
- ...

**Gap:** Mathlib has no Shannon entropy `H[X]`, `H[X|Y]`, `I[X:Y]`,
`I[X:Y|Z]` operators.

### 2.2 `cboone/shannon-entropy` (user's own project)

A substantial Lean 4 formalization (~1,888 lines, 10 modules) of
Shannon's 1948 finite-alphabet characterization theorem. ...

### 2.3 PFR project (`teorth/pfr`)

...

### 2.5 Other proof assistants

- **Coq/Rocq `infotheo`** (Affeldt et al.): full Shannon apparatus,
  source/channel coding theorems, no non-Shannon.
- **Isabelle/HOL** (Hoelzl; AFP): measure-theoretic entropy, Shannon
  coding, no non-Shannon.
- **HOL4** (Hasan/Tahar): discrete entropy and relative entropy, no
  non-Shannon.
- **Mizar:** no relevant entries.
```

**What this does well.**

- Sub-sections name the ecosystem pieces individually. Each gets the space it needs; none is lost in a paragraph.
- Each subsection is explicit about the verification date ("verified 2026-04-15"), the specific module names, and the specific gaps.
- Section 2.5 covers adjacent proof-assistant work explicitly, which orients the reader about the contribution's novelty.

## Example 3: Scope Resolution (Section 4)

```markdown
## 4. Scope (resolved: S2 + Theorem 5 stretch)

### What we are building

**Core (S2):**

- **Theorem 2 (warm-up; Zhang-Yeung 1997 conditional inequality,
  restated from [39] as Theorem 2 of the paper):** Under
  I(X; Y) = I(X; Y | Z) = 0, I(X; Y | Z, U) <= I(Z; U | X, Y) +
  I(X; Y | U). Uses a single auxiliary copy (a degenerate form of the
  M2 construction); serves as a warm-up that exercises the construction
  machinery before the two-copy argument.
- **Lemma 2 / copy construction (copy lemma):** The highest-leverage
  artifact. Standalone, reusable, Mathlib-ready. Bundles the auxiliary
  distribution of eq. (44) and the Delta-identity of Lemma 2 (eq. 45).
- **Theorem 3 (Zhang-Yeung inequality):** For four discrete RVs X, Y,
  Z, U, paper's equation (21):
  Delta(Z, U | X, Y) <= (1/2) [I(X; Y) + I(X; Z, U) + I(Z; U | X)
  - I(Z; U | Y)], together with the dual (22) (via X <-> Y swap) and
  the averaged corollary (23).
- **Theorem 4 (Shannon is incomplete):** Explicit witness function F
  in Gamma_4 \ tilde{Gamma}_4, proving cl(Gamma*_n) != Gamma_n for
  n >= 4.

**Stretch (Theorem 5):**

- n+2-variable generalization. Same copy-lemma strategy with induction
  on n.
```

**What this does well.**

- Section header carries the resolution line: "(resolved: S2 + Theorem 5 stretch)." No open questions.
- Each Core item is named by its paper identity (Theorem 2, Lemma 2, Theorem 3, Theorem 4) and its equation number (44, 45, 21, 22, 23) where applicable.
- Each Core item explains what lands as a reusable artifact. The copy lemma entry goes further by flagging its upstream-Mathlib intent.

## Example 4: A Milestone Entry (Section 6)

```markdown
### M3: Theorem 3

- `ZhangYeung/Theorem3.lean`: derive the main inequality.
- Follow Section III. Two applications of Lemma 2 give
  `Delta(Z, U | X, Y) <= I(X; Y_1)` and `I(Z; U) - 2 I(Z; U | X) <=
  I(X; X_1)`. Combine: `2 I(Z; U) - 3 I(Z; U | X) - I(Z; U | Y) <=
  I(X; X_1, Y_1) + I(X_1; Y_1)`. Two distinct Shannon ingredients close
  the chase: (a) *marginal equality* `I(X_1; Y_1) = I(X; Y)` (the
  (X_1, Y_1, Z, U) marginal of q coincides with the (X, Y, Z, U)
  marginal of p, per eq. 44); (b) *data processing* `I(X; X_1, Y_1) <=
  I(X; Z, U)` via the Markov chain (X_1, Y_1) - (Z, U) - X under q.
- All steps are Shannon-type; the non-Shannon character enters only
  through the copy lemma.
- Prove (21) as the headline theorem, derive (22) by the X <-> Y swap,
  and (23) by averaging.
- **Testing:** `ZhangYeungTest/Theorem3.lean` should include an
  independent-variable smoke test and a theorem-application test that
  derives the averaged form (23) from the public theorem plus the M1
  form-conversion lemmas.
- **Prelude promotion:** M2 left two private helpers in
  `ZhangYeung/CopyLemma.lean` ... [policy note omitted]
- **Checkpoint:** `theorem zhangYeung ... : delta Z U X Y mu <= (1/2)
  * (I[X : Y; mu] + I[X : (Z, U); mu] + I[Z : U | X; mu]
  - I[Z : U | Y; mu])` with all hypotheses explicit; averaged
  corollary follows mechanically, and the theorem test module builds.
```

**Mapped to the 5-part anatomy.**

1. **Title and one-line summary.** "M3: Theorem 3." The heading level and the single-sentence deliverable summary together carry this.
1. **Deliverables.** `ZhangYeung/Theorem3.lean` with the main inequality, its dual, and the averaged corollary. Plus the test module.
1. **Why-now reasoning.** Implicit through the roadmap's dependency graph (M3 consumes the copy lemma from M2). The entry carries the *proof strategy* why-now: specifically, that the two applications of Lemma 2 plus Shannon basics close the chase, and that the non-Shannon character enters only through M2.
1. **Testing approach.** `ZhangYeungTest/Theorem3.lean`, independent-variable smoke test plus averaged-form-derivation test.
1. **Checkpoint gate.** Exact theorem statement with all hypotheses explicit, averaged corollary follows mechanically, test module builds.

**Where a weaker entry would slip.**

- Dropping the equation number "(eq. 44)" in favor of "per the marginal-equality argument."
- Naming the test file as "a corresponding test module" instead of `ZhangYeungTest/Theorem3.lean`.
- A checkpoint that says "theorem is proven" without the statement and the test-module condition.

## Example 5: Phase-Oriented Variant

Some roadmaps use Phase labels instead of M\<N\>. The Shannon roadmap does this:

```markdown
## Phase B: Revision, tighten correspondence with Shannon's narrative

Goal: make each existing proof traceable to a specific page / argument
in Shannon's paper; fill test-coverage gaps; introduce the base-2
public API that Phases D and E will use; start populating the Verso
book with the already-done material.
```

**What changes.** Heading labels use "Phase X" instead of "MX," but the 5-part anatomy still applies. Each Phase carries title/summary, deliverables, why-now reasoning (often framed as Goals), testing approach, and checkpoint gates.

**What stays the same.** The 10-section structure, the test-parallel rule, the equation-numbered citations, the buildable-linted-testable checkpoint gates, and the spin-out rule. The label system is a stylistic choice; the conventions are not.

**Mix-and-match caution.** Pick one label system per roadmap. A document that uses M0, M1, then Phase C, then M4 will confuse readers.

## Example 6: Risk Entry with Assessment

```markdown
### 7.2 Copy-lemma measurability bookkeeping (moderate-high)

The conceptual content of Lemma 2 is elementary, but the Lean proof
needs to discharge measurability / standard-Borel / sigma-finite side
conditions at each step. Finite RVs make standard Borel trivial but do
not make `Kernel.compProd` go through without work. **Mitigation:**
specialize to `Fintype` initially; generalize later.
```

**What this does well.**

- Title names the specific risk (measurability bookkeeping), not a generic worry.
- Severity label ("moderate-high") is explicit.
- Description distinguishes conceptual difficulty (low) from formalization difficulty (high). This is the useful observation.
- Mitigation is concrete and names the initial move (`Fintype` specialization).

**Contrast with a weak version.** "7.2 Proof might be tricky (medium)." No specificity, no mitigation, no actionable content.
