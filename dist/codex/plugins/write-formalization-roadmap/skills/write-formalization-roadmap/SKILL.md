---
name: write-formalization-roadmap
description: >-
  Document-structure guide for multi-milestone formalization roadmaps in Lean,
  Rocq, Isabelle, HOL, and other proof assistants.
---

# Write Formalization Roadmap

Apply the structural conventions from the reference files below when
drafting or editing a multi-milestone formalization roadmap.

## When to Use

A _formalization roadmap_ is the long-lived planning document for a
multi-milestone mechanization of a specific paper, theorem, or related
cluster of results. It lives under `docs/plans/todo/` until the whole
program ships, then moves to `docs/plans/done/`. It coordinates work
that will span many sessions, many commits, and usually multiple
worktrees or branches.

Use this skill when the planning document is a _roadmap_ in that
sense. Do not use it for:

- Single-bounded implementation plans (one feature, one fix, one
  reorganization). Those follow the ordinary `docs/plans/todo/` plan
  conventions, not the roadmap schema.
- Paper manuscripts, framework notes, or prose about mathematics. Use
  `write-math`, `write-pandoc-markdown`, and `write-latex` instead.
- Per-milestone plan files that a roadmap spins out. Those are
  ordinary implementation plans; the roadmap's Section 6 entry is the
  short summary, and the spun-out file is the elaboration.

## Core Principles

1. **Structure is the contract**. The 10-section schema and the
   5-part milestone anatomy are the interface between the roadmap
   author and every future session that reads it. Deviating silently
   makes the roadmap harder to pick up cold; deviating with an
   explicit justification recorded in the roadmap is fine.
1. **Resolutions freeze in-doc**. Once a scope question is answered,
   record the resolution in Section 4 rather than leaving it open or
   scattering the answer across chat history. Later sessions must be
   able to reconstruct the decision from the document alone.
1. **Tests are part of the milestone**. Every proof milestone has a
   named test module that lands in the same checkpoint. Milestones
   without named tests are not complete milestones.
1. **Checkpoint gates are buildable, linted, and testable**. There is
   no "partial milestone" state. Either the whole checkpoint compiles
   and passes its gates or the milestone slips; record the slip
   explicitly.
1. **Cite equations, not gestures**. Paper citations must name
   specific equation numbers, theorem numbers, and page numbers from
   the verified transcription. "See Theorem 3" is not a citation.
1. **Roadmap entries summarize; plan files elaborate**. A Section 6
   milestone entry is a short, fixed-shape summary. The full
   elaboration lives in a spun-out plan file under
   `docs/plans/todo/<date>-<milestone-slug>.md`. Do not duplicate.

## Workflow

1. Review the essential checklist:
   `references/essential/checklist.md`
1. For specific questions, consult the comprehensive references
   below
1. When reviewing an existing roadmap, run through `anti-patterns.md`
   explicitly and call out each match

## Reference Navigation

**Quick reviews (default):**

- `references/essential/checklist.md`: condensed, actionable rules
  covering the 10 sections, the 5-part milestone anatomy, mandated
  conventions, and anti-patterns

**Deep dives by topic:**

- `references/comprehensive/document-structure.md`: the 10 top-level
  sections in order, with purpose, required content, and signals for
  each
- `references/comprehensive/milestone-anatomy.md`: the 5-part
  milestone entry schema, with examples of each part
- `references/comprehensive/conventions.md`: mandated conventions
  (M0 as explicit scaffolding, test-parallel-with-proof rule,
  equation-numbered citations, buildable/linted/testable checkpoint
  gates, frozen scope resolutions, milestone plan spin-out)
- `references/comprehensive/anti-patterns.md`: flagged patterns, each
  paired with its positive counterexample
- `references/comprehensive/examples.md`: annotated fragments from a
  working roadmap, showing the schema in practice

## Sources

- `cboone/zhang-yeung-inequality/docs/plans/todo/2026-04-15-zhang-yeung-formalization-roadmap.md` --
  cleanest current exemplar (10 sections, M0 through M6, explicit
  scope resolution, test-parallel rule enforced throughout).
- `cboone/shannon-entropy/docs/plans/todo/2026-04-14-shannon-proofs-roadmap.md` --
  phase-oriented variant (Phase A through Phase F) demonstrating the
  same structural contract with different milestone labels.
- `cboone/strength-model` planning surfaces -- larger-scale program
  that extends the template across multiple papers and a shared proof
  project.
