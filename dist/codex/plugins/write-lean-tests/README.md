# Write Lean Tests

Conventions for compile-time, `example`-based Lean 4 API regression tests that mirror a library's public surface.

**Type:** Skill
**Trigger:** `/write-lean-tests` (also activates automatically)

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Provides conventions for the test-side of Lean libraries: a sibling `<Name>Test/` directory of compile-time `example`-based regression tests that pin every exported definition and lemma to its public signature. Tests catch accidental renames, tightened hypotheses, and removed re-exports in a deliberate, localized way. Pairs with the `write-lean-code` skill, which governs the library code itself.

Covers test mirroring (1:1 with library structure), import discipline (public surface only, no `Internal` reach-arounds), composition tests per milestone, build-gate wiring (`testDriver` vs default targets), and anti-patterns to avoid.

## Usage

```text
/write-lean-tests
```

The skill also activates automatically when Claude Code touches files under a `<Name>Test/` directory or wires `lake test` configuration.

## Examples

- Adding a new module under the main library and creating its sibling test module
- Reviewing a PR that touches library or test code
- Wiring `lake test` via `testDriver` in `lakefile.toml` or `lakefile.lean`
- "/write-lean-tests": loads the full conventions explicitly

## See Also

- [Write Lean Code](../write-lean-code/README.md): the library-side companion (naming, proof style, Mathlib conventions)
- [Write Formalization Roadmap](../write-formalization-roadmap/README.md): structuring multi-milestone proof projects with parallel test surface
- [All plugins](../../../../README.md)
