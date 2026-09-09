# Anti-Patterns

Patterns the skill flags when reviewing a formalization roadmap. Each is paired with its positive counterexample. When reviewing, enumerate these explicitly; when drafting, re-read this file before calling the draft finished.

## 1. Milestones Without a Named Test Module

**Symptom.** A milestone's Testing Approach says "tests as appropriate" or "add tests covering the new lemmas" without naming the test module file.

**Why it fails.** The test-parallel-with-proof rule turns into a suggestion. A future session reading the roadmap cannot tell whether a test module was planned, deferred, or forgotten.

**Positive counterexample.** "`ZhangYeungTest/Theorem3.lean` should include an independent-variable smoke test and a theorem-application test that derives the averaged form (23) from the public theorem plus the M1 form-conversion lemmas." Specific file, specific coverage.

## 2. Missing Checkpoint Gates

**Symptom.** A milestone ends with "the work is done" or "implementation complete" without naming what concretely must pass.

**Why it fails.** "Done" is subjective; "`lake build`, `lake lint`, `lake test` all green plus arithmetic witness check" is mechanical. The latter can be falsified by running commands; the former can only be debated.

**Positive counterexample.** "Checkpoint: `theorem zhangYeung ... : delta Z U X Y mu <= (1/2) * (I[X : Y; mu] + I[X : (Z, U); mu] + I[Z : U | X; mu] - I[Z : U | Y; mu])` with all hypotheses explicit; averaged corollary follows mechanically, and the theorem test module builds."

## 3. Loose Paper References

**Symptom.** "See Theorem 3." "As in the paper." "The main inequality."

**Why it fails.** A reader doing a cross-check has to find the reference in the paper. Over many milestones and many readers, the cost compounds.

**Positive counterexample.** "The copy-lemma identity is eq. (45), p. 1445, in Zhang and Yeung 1998 (`references/transcriptions/zhangyeung1998.md`, verified 2026-04-16)."

## 4. Risks Without Assessments

**Symptom.** A risk entry reads "could be hard" or "might have issues" without a severity, likelihood, or mitigation line.

**Why it fails.** "Could be hard" is not actionable. A risk must be concrete enough to either rule it out or plan around it.

**Positive counterexample.** "**7.2 Copy-lemma measurability bookkeeping (moderate-high).** The conceptual content of Lemma 2 is elementary, but the Lean proof needs to discharge measurability / standard-Borel / sigma-finite side conditions at each step. Finite RVs make standard Borel trivial but do not make `Kernel.compProd` go through without work. **Mitigation:** specialize to `Fintype` initially; generalize later."

## 5. Open Scope Questions in a Roadmap That Is in Use

**Symptom.** Section 4 has sentences phrased as questions ("Should we include Theorem 5?") or enumerates alternatives without a resolution line.

**Why it fails.** A roadmap is a contract with future sessions. If scope is open, later work cannot tell whether an in-scope item is actually in scope or merely under consideration.

**Positive counterexample.** "Scope (resolved: S2 + Theorem 5 stretch). Core: Theorem 2 (warm-up), Copy Lemma, Theorem 3, Theorem 4. Stretch: Theorem 5 (n+2-variable generalization)." Explicit resolution; no open questions.

## 6. Duplicated Content Between Roadmap and Spun-Out Plan

**Symptom.** A milestone entry in Section 6 runs several pages, elaborating implementation details that also live in the milestone's `docs/plans/todo/` plan file.

**Why it fails.** Two sources of truth. When implementation strategy changes, one of the two drifts, and readers cannot tell which is canonical.

**Positive counterexample.** The roadmap's Section 6 entry is short and covers the 5-part anatomy. It references the plan file by path: "See `docs/plans/todo/2026-04-20-copy-lemma-implementation.md` for the implementation plan." The plan file carries the elaboration.

## 7. M0 Absorbed Into M1

**Symptom.** The first milestone is named "M1: Project setup and Delta lemmas" or similar. Scaffolding and domain work are bundled together.

**Why it fails.** Neither is properly scoped. The scaffolding work gets hand-waved because it is not the star of the milestone; the domain work gets delayed because it is blocked on scaffolding that keeps revealing new requirements.

**Positive counterexample.** "M0: Project scaffolding" as a dedicated milestone whose sole deliverable is a green-CI, buildable, linted, testable project skeleton with the test library already wired in. M1 starts from a working skeleton and adds domain content.

## 8. Parallelism Claims Without a Dependency Graph

**Symptom.** The roadmap asserts that two milestones can run concurrently but does not show the dependency structure or explain how the branches rejoin.

**Why it fails.** "These can run in parallel" is a claim; showing that they actually can requires a graph. Without it, the claim is unverifiable and usually wrong.

**Positive counterexample.** "Dependency graph: M0 -> M1 -> M1.5 -> M2 -> M3 and M4 (partial) -> M5. M4 is partially independent of M3. Theorem 4's counterexample proof has two halves: (a) proving F satisfies all basic Shannon inequalities (entirely independent of M2/M3), and (b) proving F violates the Zhang-Yeung inequality (requires M3's theorem statement as a black box). Worktree A runs M0 -> M1 -> M1.5 -> M2 -> M3 -> M5. Worktree B runs M4 part (a), merges with A once M3 lands to close M4 part (b)."

## 9. Sections Reordered, Renamed, or Dropped Without Justification

**Symptom.** A roadmap uses "Goals" instead of "Context," merges Scope into Architecture, or drops the Extensions section entirely.

**Why it fails.** The 10-section schema is the contract between roadmaps. A session picking up a new roadmap cold should not have to re-learn the structure each time.

**Positive counterexample.** The roadmap uses the 10 canonical section names in order. If a section genuinely does not apply to this project (rare), the section heading is still present with a one-sentence explanation of why it is empty.

## 10. Testing Approach That Re-Proves the Theorem

**Symptom.** The Testing Approach part of a milestone says the test module will duplicate the proof, or will prove the theorem a second way.

**Why it fails.** Test modules in a test-parallel-with-proof setup are API regression tests, not re-proofs. A test module that duplicates the proof couples to internals; a signature change in the proof forces a matching change in the duplicate.

**Positive counterexample.** "The test module restates the public theorem in `example` form, verifies downstream consumers type-check against the exported surface, and exercises the intended API shape (hypothesis ordering, implicit arguments, return type). It does not re-prove the theorem."

## 11. Checkpoint That Waives Its Gate

**Symptom.** "Checkpoint: passes lake build, lint, and test, except for the lint warnings in `CopyLemma.lean` which we will come back to."

**Why it fails.** A waived gate is a lowered gate. The whole point of the three-way gate is that it cannot be partially satisfied. If the milestone cannot meet its gate, the milestone is not done.

**Positive counterexample.** Either the milestone meets its gate in full, or the roadmap records that the milestone slipped and names what is blocking closure. No waivers inside a checkpoint.

## 12. Why-Now Silence

**Symptom.** A milestone's entry skips the Why-Now Reasoning part, letting the ordering imply the reasoning.

**Why it fails.** Ordering is not reasoning. Later sessions cannot tell whether M3 comes before M4 because it must or because the author happened to write it that way.

**Positive counterexample.** "**Why now:** M2 landed the copy-lemma construction. M3 consumes the copy lemma twice to derive the main inequality; it is the first milestone that can start. M4 partially parallelizes (see Dependency graph), but its Part (b) waits for M3."
