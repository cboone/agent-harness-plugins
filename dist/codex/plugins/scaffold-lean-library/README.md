# Scaffold Lean Library

Scaffold a Lean 4 library project with Mathlib or PFR dependencies, Lake test/lint wiring, GitHub Actions CI, text linting, and agent instructions.

**Type:** Skill
**Trigger:** `/scaffold-lean-library`

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Generates the standard files for a Mathlib-downstream Lean 4 library: `lean-toolchain`, `lakefile.toml`, entrypoint manifests, `Prelude` modules, compile-time test wiring, `bin/bootstrap-worktree`, `Makefile`, split Lean and text-lint workflows, Markdown and spelling lint configs, editor settings, `AGENTS.md`, `README.md`, `LICENSE`, `CHANGELOG.md`, and optional paper-backed reference stubs.

The project can depend directly on Mathlib or on the PFR formalization's entropy API. PFR projects import `PFR.ForMathlib.Entropy.Basic` and require an explicit PFR git ref.

## Usage

```text
/scaffold-lean-library
```

The skill prompts for project name, description, top-level Lean namespace, Lean toolchain version, dependency family, dependency git ref, paper-backed mode, GitHub username, and copyright holder when those values are not already provided.

## Examples

- "scaffold Lean library" starts the interactive scaffolding process.
- "new Mathlib project" creates a Mathlib-downstream library.
- "create a PFR downstream formalization" creates a Lean library depending on `teorth/pfr`.

## See Also

- [Write Lean Code](../write-lean-code/README.md): Lean naming, proof, and module conventions
- [Write Lean Tests](../write-lean-tests/README.md): compile-time API regression test conventions
- [Write Formalization Roadmap](../write-formalization-roadmap/README.md): roadmap structure for formalization projects
- [All plugins](../../../../README.md)
