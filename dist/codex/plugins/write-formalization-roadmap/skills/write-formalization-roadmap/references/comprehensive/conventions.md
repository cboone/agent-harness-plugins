
# Mandated Conventions

Six conventions that every formalization roadmap should follow. These are not style preferences; they are structural contracts that make roadmaps portable between sessions, worktrees, and contributors.

## 1. M0 Is Explicit Project Scaffolding

**The rule.** The first milestone, named M0 (or Phase 0, or Phase A for phase-oriented roadmaps), is a dedicated project-scaffolding milestone. It is never absorbed into M1 or treated as infrastructure the roadmap assumes.

**What M0 includes.**

- `lakefile.toml` (or equivalent build-system manifest) with declared dependencies pinned.
- `lean-toolchain` (or equivalent) specifying the language version.
- CI configuration (`.github/workflows/ci.yml` or equivalent) running `lake build` and `lake lint`.
- Top-level re-export module (e.g., `ZhangYeung.lean`) that imports the project's public surface.
- Sibling test library (`ZhangYeungTest/` plus `ZhangYeungTest.lean` top-level re-export) wired into the default `lake build` target.
- At least one smoke-test module in the test library, so `lake test` has something to run from day one.
- First successful `lake build` and `lake test` commit.

**Why.** Making M0 explicit prevents two common failure modes: (a) M1 grows a silent "before we start, set up the project" preamble that duplicates infrastructure work across roadmaps; (b) test-library plumbing gets deferred to "later" and never actually lands with the expected rigor.

**Anti-pattern.** "M1: Project setup and Delta lemmas." If scaffolding is bundled with domain work, neither is properly scoped.

## 2. Test-Parallel-with-Proof Rule

**The rule.** Every milestone M\<N\> for N >= 1 adds or updates a matching module in the companion test library. The roadmap entry for the milestone names the test module explicitly in its Testing Approach part.

**What parallel means.**

- Each public module in `<Name>/` has a corresponding module in `<Name>Test/` with the same path.
- The test module imports only the public surface of the proof module, not its internals.
- Tests land in the same commit or PR as the proof code. A milestone that ships proof code without its test module is not complete.
- Tests are `example`-level API regression tests plus small-model concrete-witness checks where the milestone's subject supports them. They are not re-proofs of the theorems.

**Why.** Test-parallel discipline catches signature drift, missing re-exports, over-specialized hypotheses, and downstream proof scripts that quietly go red. In a multi-milestone project, the test library is how future milestones know the earlier API surface stayed usable.

**Anti-pattern.** "Tests as appropriate" in the milestone entry without naming the test module. Or, worse, a milestone that declares shipped with no test module added.

## 3. Equation-Numbered Paper Citations

**The rule.** Paper citations must name specific equation numbers, theorem numbers, or definition numbers, plus page numbers, from the verified transcription or source PDF. Loose references ("see Theorem 3") are not acceptable.

**Format examples.**

- "eq. (23), p. 1442"
- "Theorem 3, p. 1443"
- "Lemma 2 (eq. 45), p. 1445"
- "Section III, p. 1444"

**What counts as a citation.**

- A reference to a numbered artifact in the paper (theorem, lemma, equation, definition, section). The number is given explicitly; the page is given explicitly.
- A cross-reference to the verified transcription if one exists, preserving the paper's numbering.

**Why.** Cross-checks need to be mechanical. When a Lean proof is being reconciled with the paper's derivation, "eq. (23), p. 1442" points to the exact line; "see Theorem 3" requires the reader to read the whole paper to find the reference. Roadmaps live for months; readers come and go; citations must survive that turnover.

**Anti-pattern.** Mentioning a theorem by an adjective or descriptive phrase ("the main theorem," "the inequality on page 1443") instead of by its published identity.

## 4. Buildable-Linted-Testable Checkpoint Gates

**The rule.** Every milestone's checkpoint is a three-way gate: `lake build` passes, `lake lint` passes, `lake test` passes. Plus any milestone-specific sanity check.

**What "passes" means.**

- `lake build <Module>` succeeds, and the new modules are part of the default build target.
- `lake lint` is green on the new code. Lint warnings converted into errors for the new files, not grandfathered.
- `lake test` is green, and the new test module is part of the default test target.
- Any milestone-specific check (arithmetic witness, paper-cross-check identity, concrete-model verification) passes.

**Why.** The partial-milestone state is the silent failure mode of long-running formalization projects. If a milestone can ship with "almost all green" tests, the project accumulates a growing tail of almost-shipped work. The three-way gate forces the question: either this is done, or it is not. There is no intermediate position.

**Anti-pattern.** A checkpoint that says "compiles" without mentioning lint or tests. Or a checkpoint that allows itself to be waived ("we'll come back to the lint warnings later"). When a checkpoint slips, say the milestone slipped; do not lower the gate.

## 5. Scope Resolutions Are Frozen In-Doc

**The rule.** Once a scope question is answered, the answer is recorded in Section 4 of the roadmap. Open questions do not live in chat history, in commit messages, or in parallel planning documents; they live in the roadmap and they get closed.

**How to freeze a resolution.**

- Add an explicit resolution line at the top of Section 4 (e.g., "Scope (resolved: S2 + Theorem 5 stretch)").
- Move the question from "open" to "resolved" in the section body. If it was previously phrased as a question, rewrite it as a declarative statement.
- If the resolution affects later sections, propagate the consequences. A scope change that splits a milestone should update Section 6.

**Why.** A roadmap that still has open scope questions after it is in use is a hazard. Future sessions cannot tell whether the open questions represent genuine uncertainty or forgotten decisions. Freezing keeps the roadmap honest.

**Anti-pattern.** A scope section that reads like a design document, with options listed and discussed but not selected. Or a resolution line that is contradicted by the body text.

## 6. Milestone Plans Spin Out

**The rule.** Section 6 milestone entries in the roadmap are short summaries following the 5-part anatomy. The full elaboration of a milestone lives in a separate plan file under `docs/plans/todo/<YYYY-MM-DD>-<milestone-slug>.md`. When the milestone ships, the plan file moves to `docs/plans/done/`.

**What stays in the roadmap.**

- The five required parts of the milestone entry (title/summary, deliverables, why-now, testing, checkpoint).
- High-level prose that helps the reader understand the milestone's role in the overall plan.
- References to the spun-out plan file (typically by path).

**What goes in the spun-out plan file.**

- The full implementation plan for the milestone: task breakdown, commit plan, detailed proof strategy, code sketches.
- Any decisions specific to this milestone's implementation that do not affect the broader project (e.g., which Mathlib lemma to use for a specific measure-theoretic step).
- Notes on alternatives considered and rejected.

**Why.** Two failure modes motivate the rule. (a) If the roadmap tries to carry full elaboration, Section 6 grows into an unreadable dump. (b) If a milestone's full plan lives only in the roadmap, refactoring the plan during the milestone forces roadmap edits for every in-flight decision, and the roadmap's Section 6 becomes a moving target.

**Naming the spin-out.**

- Date prefix: YYYY-MM-DD of plan creation.
- Slug: descriptive, matching the milestone ("copy-lemma," "theorem-4-witness").
- Example: `docs/plans/todo/2026-04-20-copy-lemma-implementation.md`.

**Anti-pattern.** A roadmap where the Section 6 entries run to several pages each, duplicating content that belongs in spun-out plans. Or a spun-out plan that repeats the roadmap's why-now reasoning verbatim instead of elaborating the implementation.
