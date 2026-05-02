---
name: write-lean-tests
description: >-
  Conventions for compile-time, example-based Lean 4 API regression tests that
  mirror a library's public surface.
---

# Write Lean Tests

> **Note on examples.** Code examples in this skill use the `strength-model` Lean formalization project (the codebase from which this skill was originally extracted) as a concrete case study. The library name `StrengthModel`, module paths under `proofs/StrengthModel/`, and domain types like `Attacker` and `VerificationFunction` are specific to that project. Substitute your project's library name, paths, and domain types when applying these patterns. Prose in this skill uses `<Name>` as the placeholder for the host project's library name.

## Purpose

Lean libraries that adopt this convention ship a sibling `<Name>Test/` directory of compile-time, `example`-based API regression tests. The test modules pin each exported definition and lemma to its public signature so that accidental renames, tightened hypotheses, or removed re-exports break the test build in a deliberate, localized way. Tests are not runtime behavior checks (there is no runtime); they are a machine-checked contract that the public API of a milestone still types, still composes, and still suffices for the downstream consequences the milestone is supposed to unblock.

This skill codifies the style. `write-lean-code` still governs library code (naming, proofs, Mathlib conventions); this skill governs only the test modules under `<Name>Test/`.

## Core Principles

1. **Test the signature, not the implementation.** An `example` that can be closed with `by exact <lemma>` or `by simpa using <lemma>` is the gold standard: if the public lemma exists with the expected statement, the test passes in one line. Rebuilding the proof inside the test couples the test to internals and misses the point.
1. **Use only the public surface.** A test module that needs `open Internal` or that reaches into an unexported helper is a signal that either the library is missing an exported API or the test is exercising the wrong abstraction level. Fix the library, not the test.
1. **Mirror the main library structure 1:1.** `<Name>/X/Y.lean` gets a sibling `<Name>Test/X/Y.lean`. Structure is predictable; a reader who finds a library module can find its test module by mechanical substitution.
1. **Prove the composition, not just the pieces.** For each milestone, at least one `example` must chain two or more exported lemmas into the intended downstream consequence. Piecewise tests can all pass while the API still fails to compose.
1. **`sorry` is a library bug, not a test escape hatch.** If a test cannot be closed by the public API, the missing piece is a library issue. Open that issue; do not fudge the test.

## Workflow

When adding a definition, lemma, or theorem to `<Name>/...`, update the matching `<Name>Test/...` in the same change. When renaming, restating, or deleting something, update the test in the same change so the test build stays green. When introducing an entirely new module under `<Name>/`, create the sibling test module alongside it.

1. **Mirror the filename.** `<Name>/X/Y.lean` → `<Name>Test/X/Y.lean`. No renaming, no grouping multiple library modules into one test file.
1. **Import only the public surface.** `import <Name>` or `import <Name>.X` where `X` is a public module. Never `import <Name>.X.Internal` and never reach around the barrel by qualifying into an internal namespace.
1. **Restate each exported symbol once.** For every exported definition, write one `example` that fixes its type or reduces to a definitional equality. For every exported lemma, write one `example` restating the statement and closing it by `by exact <lemma>` or `by simpa using <lemma>`.
1. **Round-trip form-conversion lemmas.** When the library exposes two forms of the same fact (an `iff`, or a pair of forward and reverse lemmas), write one `example` that uses the conversion in each direction to demonstrate both halves are usable from outside.
1. **Add at least one composition per milestone.** Chain two or more exported lemmas to prove the downstream consequence the milestone is supposed to unblock. If the composition cannot be closed from the public API, treat that as a library issue.
1. **Wire the build gate.** Prefer `testDriver = "<Name>Test"` in the package config so `lake test` is the explicit test signal (see "Build-gate wiring" below).
1. **Run the project's full local check** before declaring the change done: build + tests + any proof-boundary or lint checks the project defines.

## Import discipline

Test modules see only what consumers of the library see.

```lean
-- Good: depends on the public module.
import StrengthModel.Entropy

-- Bad: reaches into a namespace the library did not export.
import StrengthModel.Entropy.Internal
```

`open` is allowed for readability (`open StrengthModel` or `open <Name> <Dependency>`), but never `open <Name>.Internal`. If the test appears to need an internal helper, the correct fix is almost always to export a named lemma from the library and cite it.

The import-discipline rule is what makes the test module a meaningful regression check. When a public definition gets renamed or its hypotheses tighten, the test module breaks loudly at the affected `example`. When a test module silently reaches around the public barrel, a rename can leave the library broken for consumers while the test build still passes.

## Test shape

Prefer one `example` per exported symbol, closed by a one-liner whose proof term is the symbol itself.

```lean
-- Restate an exported lemma.
example {U A : Type} (a : Attacker) (vf : VerificationFunction U A) :
    0 < effectiveThroughput a vf :=
  effectiveThroughput_pos a vf

-- Fix the shape of an exported definition.
example {U A : Type} (a : Attacker) (vf : VerificationFunction U A) :
    reachableGuessCount a vf .offline = Nat.floor (rawGuessBudget a vf) :=
  reachableGuessCount_eq_floor_rawGuessBudget_offline a vf
```

Close with `by exact`, `by simpa using`, `by simpa [...] using`, or `rfl` / term mode when possible. Use `norm_num` or `native_decide` for concrete numeric instances where they fire cleanly. Reach for longer tactic scripts only when the consequence is a composition that genuinely requires several exported lemmas, and even then keep the script to the public surface.

For docstring discipline inside test files, a short module docstring at the top (`/-! # ... -/`) and section comments (`/-! ## ... -/` or `/-! ### ... -/`) are enough. Individual `example`s usually do not need a docstring; the name of the lemma they exercise is already in the proof.

## Composition per milestone

Each milestone's test module must include at least one `example` that derives a downstream consequence by chaining exported lemmas. This is what catches over-specialized hypotheses and missing API surface: a library whose individual lemmas all have passing single-line tests can still have an API that does not compose into the result the milestone was supposed to unlock.

```lean
-- A downstream consequence chaining Proposition-1 with a concrete cost change.
example (α : Attack (Fin 3)) (p : Fin 3)
    (h : survives α p threeGuessAttacker cheapHashVf .offline) :
    survives α p threeGuessAttacker expensiveHashVf .offline :=
  survives_mono_costPerQuery α p threeGuessAttacker .offline
    (by norm_num [cheapHashVf, expensiveHashVf]) h
```

When a composed `example` fails, the fix is usually in the library (loosen a hypothesis, export a missing intermediate lemma, strengthen a `simp` set), not in the test. Record the gap as a library issue rather than weakening the test.

## Naming mirror

`<Name>/X/Y.lean` mirrors 1:1 to `<Name>Test/X/Y.lean`. Examples from the `strength-model` project:

| Library module                              | Test module                                     |
| ------------------------------------------- | ----------------------------------------------- |
| `proofs/StrengthModel/Survival.lean`        | `proofs/StrengthModelTest/Survival.lean`        |
| `proofs/StrengthModel/Entropy.lean`         | `proofs/StrengthModelTest/Entropy.lean`         |
| `proofs/StrengthModel/LargeDeviations.lean` | `proofs/StrengthModelTest/LargeDeviations.lean` |

Namespaces inside the test module match the library's namespaces for the section they cover: `namespace <Name>.LargeDeviations ... end <Name>.LargeDeviations`. When the library's entrypoint is `<Name>.lean` and the test library is configured with a submodule glob (in the example's case, `proofs/lakefile.toml`):

```toml
[[lean_lib]]
name = "<Name>Test"
globs = ["<Name>Test.+"]
```

no top-level `<Name>Test.lean` is needed; the build target is the glob-expanded submodule list. When the test library is configured without a submodule glob, create a top-level `<Name>Test.lean` that `import`s every submodule so the build target pulls them all in.

## Anti-patterns

Avoid these, and fix rather than paper over when you see them in existing code.

- **Reaching into proof internals.** `import <Name>.X.Internal`, `open <Name>.Internal`, or qualifying into a private namespace. Fix by exporting a named lemma from the library.
- **Mocking or stubbing.** Compile-time tests have no runtime, so there is nothing to mock. Use small `private def` fixtures when a concrete instance is needed (the `threeGuessAttacker`, `cheapHashVf`, `iphoneDefense` fixtures in `strength-model`'s `proofs/StrengthModelTest/Survival.lean` illustrate the pattern).
- **`sorry` in test proofs.** A `sorry` in a test is a false signal that the API exists and is usable. If the public API cannot close the `example`, the library is missing something; file that as a library issue and leave the test broken (or omit the `example` with a `TODO` citing the issue) rather than closing with `sorry`.
- **Restating the implementation.** A test that inlines the library's proof is coupled to the proof, not the signature. The test should look like `by exact <lemma>` or `by simpa using <lemma>`, not like a copy of the library proof.
- **One monster `example`.** A single test `example` that touches every lemma in a milestone saves lines but loses the localized-break property. Prefer one `example` per exported symbol plus one or more composition tests.
- **Test-only lemmas in the library.** If a helper is only referenced from the test file, either mark it `private` in the library (if it stays there for clarity) or keep it inside the test file as a `private def` / `private theorem`. Do not promote helpers into the public API just to make a test easier.

## Build-gate wiring

Two acceptable wirings for a `<Name>` library with a sibling `<Name>Test` library. Prefer the first.

**Preferred: explicit test driver.** The library is the default build target; `lake test` runs the test library.

```toml
name = "<Name>"
testDriver = "<Name>Test"
defaultTargets = ["<Name>"]

[[lean_lib]]
name = "<Name>"

[[lean_lib]]
name = "<Name>Test"
globs = ["<Name>Test.+"]
```

This pattern (used in `strength-model`'s `proofs/lakefile.toml`) gives a clean split: `lake build <Name>` verifies the library, `lake test` verifies the tests, and CI can assert both signals separately.

**Acceptable for small projects: merged default target.** Both libraries are default targets; `lake build` covers everything.

```toml
name = "<Name>"
defaultTargets = ["<Name>", "<Name>Test"]

[[lean_lib]]
name = "<Name>"

[[lean_lib]]
name = "<Name>Test"
globs = ["<Name>Test.+"]
```

This is simpler but collapses the build-vs-test signals into one. Fine for a single-milestone project; upgrade to the `testDriver` form as soon as the test surface grows beyond a few files or CI needs to distinguish the signals.

In `lakefile.toml`, use `defaultTargets = [...]` at package scope. In `lakefile.lean`, use `@[default_target]` on the relevant libraries.

## What to cover per milestone

For each milestone that lands a new module or extends an existing one:

- **Every exported definition**: one `example` fixing its signature or definitional shape.
- **Every exported lemma**: one `example` restating the statement and closing by `by exact <lemma>` or `by simpa using <lemma>`.
- **Every form-conversion lemma** (an `iff`, or a paired forward/reverse): one round-trip `example` using the conversion in each direction.
- **At least one downstream composition**: an `example` chaining two or more exported lemmas to derive the consequence the milestone was supposed to unblock. If the milestone touches multiple consequences, prefer one composition test per consequence over one monster test.

Do not aim for exhaustive numerical coverage; a handful of concrete instances (e.g., `uniformPNat 2`, `uniformPNat 4` in `Entropy.lean`) is enough to pin behavior. The goal is API regression, not runtime verification.

## Sources

- `strength-model`'s `proofs/StrengthModelTest/` directory is the primary exemplar this skill was extracted from. `Core.lean`, `Entropy.lean`, `Survival.lean`, and `LargeDeviations.lean` span the full range from small signature-fixing modules to larger composed-downstream-use modules.
- `strength-model`'s `proofs/lakefile.toml` is the reference wiring: `testDriver = "StrengthModelTest"` with a glob-expanded `[[lean_lib]]` for `StrengthModelTest`.
- `write-lean-code` owns library-side conventions (naming, proof style, Mathlib API discovery); this skill defers to it for anything that is not specific to the test surface.
