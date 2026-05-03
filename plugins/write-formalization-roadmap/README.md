# Write Formalization Roadmap

Document-structure guide for multi-milestone formalization roadmaps in Lean, Rocq, Isabelle, HOL, and other proof assistants.

**Type:** Skill
**Trigger:** `/write-formalization-roadmap` (also activates automatically)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Provides the document-structure conventions for multi-milestone formalization roadmaps: a 10-section schema and 5-part milestone anatomy designed for long-lived mechanization plans where scope resolutions are frozen in-document and tests land in parallel with proofs.

Sibling to `write-math` (which governs *mathematical prose*), `write-formalization-roadmap` governs *document structure* for roadmap planning files. Applies regardless of which proof assistant or host library the roadmap targets.

Activates when: writing or editing a new roadmap under `docs/plans/todo/` that lays out a multi-milestone proof project, reviewing an existing roadmap for structural drift or missing conventions, updating a roadmap when scope or milestones change, deciding whether a planning document should be a roadmap or a single-implementation plan, spinning out a per-milestone plan file from a roadmap entry, or auditing a milestone entry for the five required parts.

## Usage

```text
/write-formalization-roadmap
```

The skill also activates automatically when the roadmap file is the subject of work.

## Examples

- Drafting a new roadmap for a Lean/Mathlib formalization project
- Auditing an existing roadmap's milestone entries for missing parts
- Spinning out an individual milestone into its own implementation plan
- "/write-formalization-roadmap": loads the full structure guide explicitly

## See Also

- [Write Math](../write-math/README.md): mathematical prose conventions for the roadmap's exposition
- [Write Lean Code](../write-lean-code/README.md): library-side conventions when the roadmap targets Lean
- [Write Lean Tests](../write-lean-tests/README.md): test-side conventions for parallel proof/test landings
- [Write Pandoc Markdown](../write-pandoc-markdown/README.md): Pandoc Markdown when the roadmap exports to a paper
- [All plugins](../../README.md)
