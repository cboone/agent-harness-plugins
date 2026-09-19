# Lean Tests Review Checklist

Applies to the compile-time test library `<Name>Test/` that mirrors a Lean library `<Name>/`, and to library changes that add, rename, restate or remove exported declarations. Cite findings as `write-lean-tests: Rule name`.

## Important

- **Tests move with the library**: A pull request that adds, renames, restates or removes an exported definition or lemma updates the mirrored test module in the same change. A new library module gets a sibling test module.
- **No sorry in tests**: No test `example` is closed with `sorry`. When the public API cannot close an example, the gap is a library issue to file, not a test to weaken.
- **Public surface only**: Test modules import only public modules. No `import <Name>.X.Internal`, no `open` of an internal namespace, and no qualified names that reach into private or internal namespaces.
- **Test library builds**: Every test module is reached by the build. Either the `<Name>Test` library uses a submodule glob, or a top-level `<Name>Test.lean` imports every test module.

## Nits

- **Mirrored paths**: `<Name>/X/Y.lean` is tested in `<Name>Test/X/Y.lean`, with no renaming and no grouping of several library modules into one test file.
- **Matching namespaces**: A test section uses the same namespace as the library section it covers.
- **One example per symbol**: Each exported definition gets one `example` fixing its type or definitional shape, and each exported lemma gets one `example` restating its statement.
- **Signature, not implementation**: Examples close with `by exact`, `by simpa using`, `rfl` or the lemma as a term. A test that copies the library's proof is coupled to the implementation.
- **Round trips**: A pair of form-conversion lemmas, or an `iff`, gets an `example` using the conversion in each direction.
- **Composition**: Each milestone's test module has at least one `example` that chains two or more exported lemmas into the consequence the milestone was meant to unblock.
- **No monster example**: A single `example` does not exercise a whole milestone; separate examples keep breakage localized.
- **Fixtures stay local**: Concrete instances are `private def` fixtures in the test file. Helpers used only by tests are not added to the library's public API.
- **Test driver**: The package config prefers `testDriver = "<Name>Test"` so `lake test` is a separate signal from `lake build`.
- **Light documentation**: A test file has a short `/-! -/` module docstring and section comments; individual examples need no docstring.

## Do not flag

- **Readability opens**: `open <Name>` or `open` of a dependency's public namespace.
- **Numerical coverage**: A handful of concrete instances is enough; exhaustive numeric cases are not required.
- **Merged default target**: `defaultTargets` listing both the library and the test library is acceptable in a small project.
- **Library style**: Naming, proof style and Mathlib conventions inside test files are covered by the Lean checklist, not this one.
