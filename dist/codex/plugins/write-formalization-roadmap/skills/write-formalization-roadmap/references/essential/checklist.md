
# Formalization Roadmap Essential Checklist

Quick reference for reviews. For detailed guidance, see `../comprehensive/`.

## Top-Level Document Structure (10 Sections, In Order)

- [ ] Section 1: **Context** -- why formalize this paper, what the central result is, one-paragraph summary that names the paper, venue, year, and central theorem
- [ ] Section 2: **State of the Art** -- prior formalizations (if any, across Lean, Rocq, Isabelle, HOL family, Mizar), ecosystem dependencies, what is reusable from upstream
- [ ] Section 3: **Architecture** -- dependency graph of the proof's own modules, and the proof's position against the host library's API surface
- [ ] Section 4: **Scope** -- explicit resolution line (e.g., "resolved: S2 + Theorem 5 stretch") so later sessions know which options were settled; every open question here should be answered, not parked
- [ ] Section 5: **File Layout** -- `<Name>/`, `<Name>Test/`, namespace conventions, where shared helpers live versus per-milestone modules
- [ ] Section 6: **Milestone-by-Milestone Plan** -- M0 through M\<N\>, one short entry per milestone, each entry following the 5-part anatomy below
- [ ] Section 7: **Key Risks and Unknowns** -- numbered, each with a brief *assessment* (not just a list of worries); every risk has a mitigation line
- [ ] Section 8: **Verification Plan** -- per-milestone checkpoints plus aggregate CI gate
- [ ] Section 9: **Extensions** -- future work, post-release, explicitly out of scope for the current roadmap
- [ ] Section 10: **Critical Files** -- exhaustive mapping of file to milestone that lands it, separating files this project creates from external dependencies the project relies on

Sections may carry prose and sub-headings, but the top-level ordering and naming are fixed. Deviations need an explicit justification recorded in Section 1 or Section 4.

## Milestone Entry Anatomy (5 Parts Per Entry)

For every milestone in Section 6:

- [ ] **Title and one-line summary.** The milestone ID (e.g., M2, Phase B) plus a short phrase naming the deliverable ("M2: The copy lemma").
- [ ] **Deliverables.** Files created or modified, key definitions, theorems, and tests that land. Not "work on X" but "file Y exists with theorem Z."
- [ ] **Why-now reasoning.** Which dependencies are satisfied at this point, and what downstream milestones this unblocks. Explicit, not inferred from ordering.
- [ ] **Testing approach.** Which `<Name>Test/<Module>.lean` (or equivalent for other proof assistants) mirrors this milestone, and what the test module covers.
- [ ] **Checkpoint gate.** The concrete buildable-linted-testable condition that declares the milestone shipped: `lake build <Module>` passes, `lake lint` is green on the new code, `lake test` is green, plus any milestone-specific sanity check.

## Mandated Conventions

- [ ] **M0 = project scaffolding as a dedicated milestone.** Never implicit. Lakefile, toolchain, CI, test-library plumbing, first `lake build` all live here.
- [ ] **Test-parallel-with-proof rule.** Every milestone M\<N\> (for N >= 1) adds or updates a matching `<Name>Test/` module. The roadmap entry names the test module explicitly.
- [ ] **Paper-citation discipline.** Cite specific equation numbers, theorem numbers, and page numbers from the verified transcription (e.g., "eq. (23), p. 1442" or "Theorem 3, p. 1443"), not "see Theorem 3."
- [ ] **Buildable + linted + testable checkpoint gates.** No "partial milestone" state. Either the whole checkpoint compiles, lints, and passes its tests, or the milestone slips. Record the slip.
- [ ] **Scope resolution is frozen in-doc.** Once a scope question is answered, record the resolution in Section 4 rather than leaving it open, scattered, or only in chat.
- [ ] **Milestone plans are spun out.** Section 6 entries are short summaries; each milestone's elaboration is a separate plan file under `docs/plans/todo/<date>-<milestone-slug>.md`. When the milestone ships, move the plan to `docs/plans/done/`. Do not duplicate content between the roadmap entry and the spun-out plan.

## Anti-Patterns to Flag

- [ ] Milestones without a named test module
- [ ] Missing checkpoint gates ("the work is done" without "here is what 'done' means")
- [ ] Loose paper references instead of equation-numbered citations
- [ ] Risks section without assessments ("could be hard" is not a risk entry)
- [ ] Open scope questions left unresolved after the roadmap is in use
- [ ] Duplicated milestone content in both the roadmap entry and the spun-out plan file
- [ ] M0 absorbed into M1 rather than called out as its own milestone
- [ ] Parallelism claims without a dependency graph or a concurrent-worktree strategy
- [ ] Sections reordered, renamed, or dropped without a justification in the roadmap itself

## Review Heuristics

When reviewing a roadmap:

1. Count the top-level sections. If there are not ten in the expected order, ask why.
1. Open Section 6 and spot-check three milestones. If any is missing one of the five parts, flag it.
1. Search the document for "Theorem" and "eq." If any paper reference does not name an equation or page number, flag it.
1. Read Section 4 end to end. If any sentence is phrased as an open question, flag it.
1. Read Section 7. If any risk lacks a mitigation line, flag it.
1. Check whether the milestone plan files referenced under `docs/plans/todo/` exist. If the roadmap references plans that do not yet exist, note which ones still need to be spun out.
