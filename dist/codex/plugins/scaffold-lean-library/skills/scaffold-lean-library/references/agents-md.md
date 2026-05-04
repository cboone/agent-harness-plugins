# AGENTS.md Template

Use this template for `AGENTS.md`.

````markdown
# PROJECT-NAME

## Overview

PROJECT-DESCRIPTION

## Structure

```text
.
├── LEAN-NAMESPACE.lean
├── LEAN-NAMESPACE/
│   └── Prelude.lean
├── LEAN-TEST-NAMESPACE.lean
├── LEAN-TEST-NAMESPACE/
│   └── Prelude.lean
├── bin/
│   └── bootstrap-worktree
├── lakefile.toml
└── lean-toolchain
```

## Development

- Run `bin/bootstrap-worktree` in every fresh clone or worktree before direct `lake build`, `lake test`, or `lake lint`.
- Run `make build` to build the main Lean library.
- Run `make test` to build the compile-time API regression test library.
- Run `make lean-lint` to run `lake lint` through `batteries/runLinter`.
- Run `make lint` to run Markdown and spelling checks.
- Run `make check` before considering a change complete.

## Lean Conventions

- Use `LEAN-NAMESPACE` as the top-level namespace for project code.
- Keep `LEAN-NAMESPACE.lean` as an explicit public import manifest. Do not remove imports from the manifest just because they are transitively available.
- Keep `LEAN-TEST-NAMESPACE.lean` as the explicit test import manifest.
- Every public module under `LEAN-NAMESPACE/` should have a matching compile-time API regression module under `LEAN-TEST-NAMESPACE/`.
- Search project code first, then Mathlib, before inventing local Lean conventions.
- Exclude `.lake/` from style searches; it contains dependency and build output, not project conventions.
- Do not enforce a hard line length in Lean code, comments, or docstrings. Let editors handle visual wrapping.
- Comments and docstrings are single long lines per paragraph; blank lines separate paragraphs.

## Dependency Notes

- Dependency family: `DEPENDENCY-FAMILY`.
- Dependency ref: `DEPENDENCY-REF`.
- Mathlib artifacts must come from `lake exe cache get`, not local source compilation.
````

## Notes

- After creating `AGENTS.md`, create `CLAUDE.md` as a symlink only when safe. Use the safe symlink step from the skill workflow.
- Add any project-specific deviations from Mathlib conventions here, not in global memory.
