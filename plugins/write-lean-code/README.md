# Write Lean Code

Lean 4 and Mathlib conventions for code, proofs, naming, documentation and compile-time tests that mirror the public library API.

**Type:** Skill
**Trigger:** `/write-lean-code` (also activates automatically)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Provides Lean 4 style conventions covering naming, proof style, formatting, Mathlib API discovery, build infrastructure, metaprogramming, and general functional-programming idioms. Activates automatically when working with `.lean` files, Lean docstrings, the `proofs/` directory, or any discussion of Lean naming or design decisions.

Includes a condensed essential checklist plus comprehensive references organized by topic. Covers Lake build wiring patterns, Mathlib search workflows, and PFR-downstream conventions.

## Usage

```text
/write-lean-code
```

The skill also activates automatically when Claude Code touches Lean source.

## Examples

- Editing a `.lean` file: activates automatically
- "review this Lean proof for style": activates automatically
- Naming a new lemma or definition: activates automatically
- "/write-lean-code": loads the full style guide explicitly

## See Also

- [Write Lean Tests](#additional-workflows): the sibling test-side conventions for compile-time API regression tests
- [Write Math](../write-math/README.md): mathematical exposition for Lean docstrings and informal proof prose
- [Write Formalization Roadmap](../write-formalization-roadmap/README.md): structuring multi-milestone proof projects
- [All plugins](../../README.md)

## Additional workflows

Compile-time test conventions are in `skills/write-lean-code/references/tests/workflow.md`. The single Lean review checklist includes mirrored test coverage where the project uses that convention.
