---
name: write-lean-code
description: >-
  Lean 4 style guide and Mathlib conventions. Use whenever Lean code is the
  subject of the work, not only when editing: (1) writing, editing, or
  reviewing .lean files, (2) reading Lean source to answer a user question
  about it, (3) planning, proposing, or naming lemmas, definitions, theorems,
  or tactics before implementation, (4) discussing Lean design decisions,
  refactors, API choices, or proof strategies, (5) summarizing proof status
  or reporting on formalization progress, (6) writing or editing Lean
  docstrings and comments, (7) formalizing mathematical proofs, (8) writing
  custom tactics or metaprograms. Applies to any touch on .lean files or the
  proofs/ directory, including reading and discussion, not just edits.
  Covers naming, formatting, proof style, Mathlib conventions, general
  functional programming, and metaprogramming.
---

# Write Lean Code

## Core Principles

1. **Type-driven development**: let the type system guide implementation; express invariants in types
1. **Leverage Mathlib**: use existing theorems, definitions, and tactics before building from scratch
1. **Tactic proofs for incremental feedback**: prefer tactic mode for complex proofs; use the VS Code infoview for step-by-step development
1. **Clarity and composability**: write small, focused lemmas; name them to be discoverable via `exact?` and `apply?`

## Workflow

1. In a fresh clone or worktree, run the project's documented bootstrap script before any direct `lake build`. Mathlib must come from `lake exe cache get` (prebuilt artifacts), not a local source compilation.
1. After bootstrap has succeeded in the current worktree, run `lake build <Module.Name>` to check compilation; run project linters if available.
1. **Update the tests in the same change as the proof code** if the project has a test suite that mirrors the proof code. Whenever you add, rename, restate, or delete anything on a module's public surface, update the matching test file in the same change. Treat the test suite as part of the proof code, not an optional extra. For the compile-time, `example`-based regression style those test modules typically use (import discipline, 1:1 naming mirror, composition per milestone, anti-patterns), invoke the companion `write-lean-tests` skill; `references/comprehensive/build-infrastructure.md` covers the `testDriver` / `defaultTargets` wiring side.
1. Before declaring a proof change finished, run the project's full local check (build + tests + any proof-boundary or lint checks the project defines).
1. Review against essential checklist: `references/essential/checklist.md`
1. For specific questions, consult: `references/comprehensive/{topic}.md`

## Project-Local Caveats

Each project using this skill should document its own bootstrap script, test-mirroring convention, namespace rules, and any vendored Lean dependencies that must be excluded from style searches. Read the invoking project's CLAUDE.md (or equivalent agent-config file) for those specifics before applying the generic guidance below.

**Vendored Lean dependencies are not style references.** When a project pulls in a third-party Lean library through `lake` (under `.lake/packages/<name>/` or the equivalent), that code is a build artifact, not a reference for Lean naming, proof style, tactic preferences, comment or docstring format, file structure, or math prose. Exclude such paths from grep-for-conventions searches. The invoking project's CLAUDE.md should name the specific packages to exclude.

Valid Lean references, in priority order: (1) the project's own code, (2) Mathlib under the project's Mathlib package path (search for both `theorem` and `lemma` declarations -- Mathlib uses both), (3) Lean core, and (4) the published documentation linked in the Sources section below.

**Mathlib build policy:** never use `lake build` as the first command in a clean worktree or clone. The supported bootstrap path runs `lake update`, downloads prebuilt Mathlib artifacts with `lake exe cache get`, verifies those artifacts exist, and only then builds the local libraries. If Mathlib artifacts are missing, rerun the project's bootstrap script rather than letting Lake compile Mathlib from source.

## Reference Navigation

**Quick reviews (default):**

- `references/essential/checklist.md`: condensed, actionable rules

**Deep dives by topic:**

- `references/comprehensive/naming.md`: identifiers, types, lemmas, files, Mathlib naming scheme
- `references/comprehensive/style-and-formatting.md`: indentation, imports, operators, sections
- `references/comprehensive/proof-style.md`: tactic vs term mode, structured proofs, automation, exploration tactics
- `references/comprehensive/mathlib.md`: documentation (module docstrings, tactic docs, citations, linting), variable conventions, API design, heartbeats
- `references/comprehensive/mathlib-api-discovery.md`: finding lemmas, navigating the module hierarchy, search strategies, common lookup patterns
- `references/comprehensive/general-programming.md`: type classes, monads, pattern matching, dependent types, IO, `lake`
- `references/comprehensive/build-infrastructure.md`: bootstrap script, Makefile target set, `lintDriver`, entrypoint manifest, `testDriver` vs `defaultTargets`, and test-library discipline for Mathlib-downstream projects
- `references/comprehensive/pfr-downstream.md`: finite-alphabet specialization, `noncomputable def` + `volume_tac`, measurability hygiene, and anonymous-constructor pair notation for projects built on PFR's entropy API
- `references/comprehensive/metaprogramming.md`: macros, custom tactics, syntax, elaboration, monad hierarchy

## Sources

- [Lean 4 Language Reference](https://lean-lang.org/doc/reference/latest/)
- [Lean 4 Naming Conventions](https://github.com/leanprover/lean4/blob/master/doc/std/naming.md)
- [Mathlib Library Style Guidelines](https://leanprover-community.github.io/contribute/style.html)
- [Mathlib Naming Conventions](https://leanprover-community.github.io/contribute/naming.html)
- [Mathlib Documentation Guidelines](https://leanprover-community.github.io/contribute/doc.html)
- [Mathematics in Lean](https://leanprover-community.github.io/mathematics_in_lean/)
- [Functional Programming in Lean](https://lean-lang.org/functional_programming_in_lean/)
- [Theorem Proving in Lean 4](https://lean-lang.org/theorem_proving_in_lean4/)
- [Metaprogramming in Lean 4](https://leanprover-community.github.io/lean4-metaprogramming-book/)
