
# Document Structure

The 10 top-level sections of a formalization roadmap, in order. Every roadmap should carry these sections under these names. Sections may carry sub-headings and prose; the ordering and section names are fixed.

## 1. Context

**Purpose.** Tell a cold reader what paper is being formalized, what the central result is, and why the project exists. A roadmap opens with context so that every subsequent section lands in a setting the reader already understands.

**Required content.**

- Paper identity: authors, title, venue, year, page range. Include a canonical source pointer (e.g., `references/papers/zhangyeung1998.pdf`) and, if available, a verified transcription pointer (e.g., `references/transcriptions/zhangyeung1998.md (verified 2026-04-16)`).
- Central result in prose: one paragraph naming the main theorem(s) and their significance. Reference specific theorem numbers and equations from the paper.
- Why formalize this paper. What is gained that does not already exist upstream. Name the existing gap (e.g., "no proof assistant has formalized any non-Shannon-type inequality").
- Resolved decisions block (optional but recommended when the roadmap is first spun up). A short list of early scope decisions, labeled as such.

**Signals of a weak Section 1.**

- Opens with code or file paths before the reader knows what is being formalized.
- Names "the theorem" without saying which theorem, which paper, or which equation.
- Skips the why-formalize argument, implying the reader already knows.

## 2. State of the Art

**Purpose.** Survey what exists that this project will depend on, reuse, or deliberately not reuse. Orients the reader about where the roadmap's work sits in the ecosystem.

**Required content.** Subsections, one per relevant ecosystem:

- The host library for the target proof assistant (Mathlib for Lean, infotheo for Rocq, AFP entries for Isabelle, etc.). Name specific modules and lemmas that are directly usable; name the gaps that are not yet upstream.
- User-owned adjacent projects that might contribute reusable pieces (e.g., `cboone/shannon-entropy` for the Zhang-Yeung roadmap). Detail what each provides and what gaps remain relative to this project's needs.
- Other proof-assistant formalizations of adjacent results (Rocq, Isabelle, HOL family, Mizar). Helps scope the contribution and identifies translation opportunities.
- Upstream PR status: which relevant PRs are open, merged, or stalled in the host library. A point-in-time snapshot; update when material changes happen.
- Non-formalized tooling that solves an adjacent problem (LP solvers, numerical checkers, paper-style arguments). Helps disambiguate machine-checkable proof from algorithmic verification.

**Signals of a weak Section 2.**

- "Mathlib has everything we need" without naming the specific modules.
- No mention of adjacent proof-assistant work, implying none exists when it does.
- Fresh claims about API availability without a verification date.

## 3. Architecture

**Purpose.** Give the reader the dependency graph of the proof itself: which of this project's own modules depend on which, and where they sit relative to the host library.

**Required content.**

- A "representation tension" subsection when two competing designs exist (e.g., `ProbDist` vs measure-space random variables). Lay out the tradeoff in a comparison table.
- A named, resolved strategy. After the tension is discussed, the roadmap picks a side and explains the choice.
- Diagrams when they clarify (ASCII dependency graphs are fine and common). A dependency graph in Section 6 covers per-milestone dependencies; Section 3's graph covers architectural dependencies across modules.

**Signals of a weak Section 3.**

- Describes modules without saying how they depend on one another.
- Two alternatives discussed without a resolution.
- No acknowledgment that the choice has consequences for later milestones.

## 4. Scope (Resolved)

**Purpose.** Freeze the scope of the roadmap's first release. Every open question about what is in, what is out, and what is optional gets a written answer.

**Required content.**

- Explicit resolution line in the section header or opening sentence: e.g., "Scope (resolved: S2 + Theorem 5 stretch)."
- **Core** subsection listing the theorems, lemmas, and constructions that must ship. For each, state the precise paper-level identity (equation numbers, theorem numbers, page numbers). Describe what lands as a usable Lean (or equivalent) artifact.
- **Stretch** subsection listing items included only if the schedule permits. Same citation discipline as Core.
- **Out of scope** statement when it is not obvious. If readers will reasonably ask "why not X," answer it here rather than in Section 9.

**Signals of a weak Section 4.**

- Any sentence phrased as an open question ("do we want to include Theorem 5?"). If the roadmap is in use, such questions are bugs; close them.
- Core items described without equation-level citations.
- Stretch items that are actually the same size as core items without any reason given for the relegation.

## 5. File Layout

**Purpose.** Tell a contributor where code goes. The layout codifies the project's module naming and the companion test library structure.

**Required content.**

- A `text` or `plain` code block showing the directory tree: lakefile, toolchain, top-level re-export modules, per-milestone modules under `<Name>/`, matching test modules under `<Name>Test/`, CI config.
- Namespace conventions when nontrivial (e.g., "`ZhangYeung` namespace for public API; `ZhangYeung.Internal` for helpers that should not be imported by downstream modules").
- Where shared helpers live versus where milestone-specific code lives. Usually `<Name>/Prelude.lean` or similar for shared infrastructure; per-milestone modules for milestone-specific content.

**Signals of a weak Section 5.**

- No directory tree. Prose descriptions of layout are harder to check against than a tree.
- Test library mentioned only as an aside, not as a first-class part of the layout.
- Shared helpers discussed without naming a home module.

## 6. Milestone-by-Milestone Plan

**Purpose.** The body of the roadmap. One short entry per milestone from M0 through the final milestone, each following the 5-part anatomy documented in `milestone-anatomy.md`.

**Required content.**

- A dependency graph at the top of the section (ASCII is fine). Shows which milestones depend on which.
- A parallelism analysis when multiple worktrees or branches can run concurrently. If the whole project must be sequential, say so.
- One subsection per milestone, each a short, fixed-shape summary following the 5-part anatomy. See `milestone-anatomy.md` for the anatomy and `conventions.md` for the spin-out rule.

**Signals of a weak Section 6.**

- Milestones that are essentially one-liners without the five required parts.
- No dependency graph.
- Milestones that elaborate full implementation details rather than summarizing. Elaboration belongs in the spun-out plan file.
- M0 absent or merged into M1.

## 7. Key Risks and Unknowns

**Purpose.** Surface the failure modes and open uncertainties. Every risk gets a concrete assessment, not just a worry.

**Required content.**

- A numbered list (7.1, 7.2, ...) of named risks. One risk per entry.
- For each entry: a short title, a description of the failure mode, a severity or likelihood judgment (e.g., "moderate-high"), and a **Mitigation** line.
- Risks specific to this paper's proof strategy. Generic "Lean is hard" entries are not useful; "the copy lemma measurability bookkeeping is nontrivial because it requires sigma-finiteness at three composition steps" is.

**Signals of a weak Section 7.**

- Risk entries without mitigations.
- Severity descriptions omitted.
- Risks copied from a generic template rather than named from this paper's specific proof strategy.

## 8. Verification Plan

**Purpose.** Define what "the roadmap is done" means at each milestone and at the aggregate. Both per-milestone checkpoints and the CI gate live here.

**Required content.**

- A **Milestone rule** line stating that every milestone adds or updates a matching test module. This is the place the test-parallel-with-proof rule lives, beyond the per-milestone entries in Section 6.
- **Build gate** specification: what `lake build` must build by default, what `lake lint` must pass, what `lake test` must pass.
- **Concrete targets by milestone** list: a bullet per milestone summarizing what its test module covers.
- **CI** subsection: which commands run in CI, what coverage they provide.

**Signals of a weak Section 8.**

- Verification deferred to "the test suite" without naming the suite.
- CI described only in terms of "green build" without naming the gates.
- Milestones whose verification is less specific than their deliverables.

## 9. Extensions (Future Work)

**Purpose.** Record what the project explicitly does *not* do in the current roadmap but might do later. Helps future readers understand why the current scope stops where it stops.

**Required content.**

- A ranked or ordered list of plausible follow-on results. Each entry names the paper or theorem and explains why it is deferred.
- Cross-references to out-of-scope items from Section 4 where relevant.
- Brief notes on what infrastructure a future extension would need that the current roadmap does not provide.

**Signals of a weak Section 9.**

- Used as a dumping ground for loose ideas without justification or ordering.
- Overlaps with Section 4's out-of-scope statement without clarifying the difference.
- Promises follow-ons that are actually within the current scope but mislabeled.

## 10. Critical Files

**Purpose.** Exhaustive, at-a-glance mapping of files to milestones. A quick reference for "which milestone creates this file," and a short list of external dependencies the project relies on.

**Required content.**

- A **New (this project)** subsection listing every new file, grouped or annotated with the milestone that creates it.
- An **External (depend on, do not modify)** subsection listing the host library modules and other upstream artifacts that the proof imports but does not own.
- File paths are exact; do not paraphrase.

**Signals of a weak Section 10.**

- Missing files that are mentioned in Section 6 milestone deliverables.
- No distinction between files this project creates and files the project depends on.
- Paths paraphrased ("some file under Mathlib") rather than specified.
