
# Milestone Entry Anatomy

Every milestone in Section 6 of a formalization roadmap is a short, fixed-shape summary. The full elaboration lives in a spun-out plan file under `docs/plans/todo/`. The summary has five parts; this file documents each in detail.

Related conventions (in `conventions.md`): M0 is always an explicit scaffolding milestone; the test-parallel-with-proof rule mandates a matching test module for every M\<N\> with N >= 1; the spin-out rule keeps the roadmap entry short while the plan file carries the elaboration.

## Part 1: Title and One-Line Summary

**What it is.** A heading or opening sentence that names the milestone ID, the deliverable, and (optionally) the character of the work.

**Format.** Either:

- A sub-section heading: `### M2: The copy lemma`.
- A phase-oriented heading: `## Phase B: Revision and base-2 API`.

A single heading style should be used throughout the roadmap; mixing M\<N\> and Phase X within one roadmap confuses the reader.

**Signals of a weak title.**

- "Milestone 2" with no naming of the deliverable.
- Marketing-style phrasing ("Unleashing the copy lemma") instead of content-focused phrasing.
- Heading that names a file path rather than a deliverable.

## Part 2: Deliverables

**What it is.** The concrete artifacts the milestone produces: files, definitions, theorems, tests, and any ancillary outputs (CI changes, documentation, build-target updates).

**Format.** A bullet list or short prose. Name files by path and definitions by declaration name. "`ZhangYeung/CopyLemma.lean`: state and prove the generalized copy lemma" is specific; "work on the copy lemma" is not.

**What to include.**

- Every `.lean` (or equivalent) file the milestone creates.
- Every key definition, lemma, theorem, or instance that lands. Name the theorem with a short English description; use the roadmap's Section 4 citations when appropriate.
- The matching `<Name>Test/<Module>.lean` (or equivalent) file. Cross-reference Part 4 so the reader can see the link.
- Any cross-cutting changes (e.g., a Mathlib pin bump, a CI workflow update, a documentation change).

**Signals of a weak deliverables list.**

- Descriptions of work rather than artifacts ("explore the kernel-composition machinery" instead of "file `CopyLemma.lean` with `copyLemma` theorem").
- Missing the matching test module.
- File paths paraphrased or abbreviated (`the test file` instead of `ZhangYeungTest/CopyLemma.lean`).

## Part 3: Why-Now Reasoning

**What it is.** An explanation of why this milestone comes next in the plan. Names the dependencies that are now satisfied and the downstream milestones this one unblocks.

**Format.** One or two paragraphs, or a short bulleted list if the dependencies are many.

**What to include.**

- Which earlier milestone(s) landed the infrastructure this milestone needs.
- What downstream milestones this one enables, and whether they are blocked or merely facilitated by it.
- If the milestone is a deliberate warm-up (e.g., Zhang-Yeung's Theorem 2 as a single-copy exercise before the two-copy main theorem), say so. Warm-up milestones have a specific why-now: they exercise a pattern on a simpler problem before the main attempt.
- If the milestone ends a parallelism branch, say which branch converges here.

**Signals of weak why-now reasoning.**

- Silence. A milestone that says only "deliverables" without reasoning leaves later readers guessing at the ordering.
- Circular dependencies (e.g., "needs M3 to land" for M3 itself).
- Why-now that could apply verbatim to any milestone ("because it is needed"). The answer must be specific to this milestone's position.

## Part 4: Testing Approach

**What it is.** Names the `<Name>Test/<Module>.lean` (or equivalent) file that mirrors this milestone, and specifies what that test module covers.

**Format.** A short paragraph or a bullet list.

**What to include.**

- The exact test file path. Every M\<N\> with N >= 1 must name at least one.
- What the test module covers: API regression tests, `example` restatements of the public theorems, arithmetic checks, small-model specializations. The level of test detail should scale with the milestone's complexity.
- The intended consumer surface. A test module that only exercises the public API catches signature drift; one that reaches into internals creates brittle tests.
- Any edge cases the milestone must cover (e.g., "witness arithmetic separately verified for the Shannon-side constraints and the strict Zhang-Yeung violation").

**Signals of a weak testing approach.**

- "Tests as appropriate" without naming the file.
- Tests that repeat the proof rather than exercising the public surface.
- Milestones that name a test file not matching the test-library naming convention documented in Section 5.

## Part 5: Checkpoint Gate

**What it is.** The concrete, buildable-linted-testable condition that declares the milestone shipped.

**Format.** A short paragraph, sometimes with a sub-item listing specific commands.

**What to include.**

- `lake build <Module.Name>` (or equivalent) passes for the modules the milestone creates or modifies.
- `lake lint` (or equivalent) is green on the new code.
- `lake test` (or equivalent) is green, and the newly-added test module is part of the default test target.
- Any milestone-specific sanity check: a small-model arithmetic check, a concrete witness verification, a paper-cross-check identity, a performance threshold. Be specific.

The checkpoint is all-or-nothing. A milestone that compiles but fails lint is not done. A milestone that compiles and lints but whose test module is unfinished is not done. A milestone whose sanity check does not match the paper's derivation is not done.

**Signals of a weak checkpoint gate.**

- "Done when it compiles" without mentioning lint or test.
- A checkpoint that depends on subjective judgment ("done when it feels right").
- A checkpoint that quietly lowers the bar below the project's ordinary buildable-linted-testable baseline.

## A Complete Example

From the Zhang-Yeung roadmap's M2 entry:

> **M2: The copy lemma**
>
> - `ZhangYeung/CopyLemma.lean`: state and prove the generalized copy lemma.
> - **Statement:** given a probability measure mu on Omega with four RVs X, Y, Z, U ... (elaborated)
> - **Construction:** nu = mu otimes\_m (condDistrib (X, Y) (Z, U) mu), a two-step kernel composition.
> - **Supporting lemmas:** `IdentDistrib` for (X, Z, U) vs (X\_1, Z, U) and symmetrically.
> - **Key Mathlib deps:** `Kernel.compProd`, `condDistrib`, `condExpKernel`. Measurability bookkeeping concentrates here.
> - **Design for Mathlib:** parametrize over any four RVs on Fintype (not specialized to the paper). Clean statement, no paper-specific notation.
> - **Testing:** `ZhangYeungTest/CopyLemma.lean` should restate the public theorem in example form and exercise the intended downstream APIs (`IdentDistrib`, conditional independence, and the projection laws) without reaching into proof internals.
> - **Checkpoint:** compiles with all measure-theoretic side conditions discharged, and the copy-lemma test module builds cleanly.

Mapped to the five parts:

1. **Title and one-line summary.** "M2: The copy lemma."
1. **Deliverables.** File `CopyLemma.lean`, theorem `copyLemma` with stated construction and supporting lemmas, plus design-for-Mathlib framing.
1. **Why-now reasoning.** Implicit from position (after M1 Delta lemmas, before M3 Theorem 3). In this particular entry the reasoning is carried by the Statement and Construction subsections; an even stronger entry would add an explicit "Why now" line.
1. **Testing approach.** `ZhangYeungTest/CopyLemma.lean`, public-API `example`s only, no reaching into internals.
1. **Checkpoint gate.** Compiles, side conditions discharged, test module builds.

This entry is about the right length. Shorter would lose the statement; longer would start duplicating the spun-out plan file's content.
