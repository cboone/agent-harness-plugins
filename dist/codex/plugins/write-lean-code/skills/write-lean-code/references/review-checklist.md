# Lean Review Checklist

Applies to Lean 4 source files (`*.lean`), including mirrored compile-time test libraries and their exported declarations. Test-specific rules apply where the project uses that convention. Cite findings as `write-lean-code: Rule name`.

## Important

- **No sorry**: Finished declarations contain no `sorry`, except tracked placeholders allowed by project instructions. Test examples never use `sorry`; an API gap is a library issue.
- **Heartbeat budgets**: New or raised `maxHeartbeats` options have a reason comment. Above 800000, split the proof into named sub-lemmas.
- **Non-terminal simp**: A `simp` that leaves goals uses `simp only [...]`.
- **Deprecations**: Renamed or removed public declarations leave a `@[deprecated (since := "YYYY-MM-DD")]` alias naming the replacement.
- **Classical in extracted lemmas**: Extracted sub-lemmas needing decidability start with their own `classical`.
- **Tests move with the library**: Exported API changes update mirrored tests in the same change; new modules get sibling tests.
- **Public surface only**: Tests import public modules and never open or qualify private or internal namespaces.
- **Test library builds**: A submodule glob or root test module reaches every test module.

## Nits

- **Declaration case**: Types and Type/Sort-valued functions use `UpperCamelCase`; theorems and term-valued functions use `snake_case`. Embedded type names use `lowerCamelCase`, as in `map_natCast`.
- **Acronyms**: Up to three letters keep one case (`IO`, `ioRef`); longer acronyms capitalize only the first letter (`Json`).
- **Lemma names**: Follow Mathlib's type, operation, property and symbol vocabulary; hypotheses appear in order with `of`.
- **le and lt**: Prefer `le` and `lt` over `ge` and `gt`.
- **Predicate names**: Use prefix form (`isClosed_Icc`); Prop-valued classes use `Is`.
- **American English**: Declaration names use American spelling.
- **File names**: `UpperCamelCase.lean`, matching the module path.
- **Type annotations**: Declarations state argument and return types.
- **by placement**: `by` ends the preceding line; tactics indent two spaces; focus subgoals with `·`.
- **Continuation lines**: Indent four spaces and begin continuations with operators.
- **Lambda syntax**: Use `fun x ↦ ...`; reserve `·` for simple closures.
- **Structured proofs**: Long proofs use `have`, `suffices`, `calc` and `show`.
- **Hypotheses before the colon**: State immediately introduced hypotheses left of the colon.
- **Module docstring**: Files have a title and summary, plus Main definitions and Main statements where applicable. Test modules use short module and section docstrings.
- **Declaration docstrings**: Public definitions and main theorems have preceding `/-- -/` docstrings. Test examples need no individual docstring.
- **Comments explain why**: Describe constraints, lemma choices or invariants rather than proof-step narration.
- **No hard wrapping**: Comment and docstring paragraphs occupy one line; blank lines separate them.
- **Existing Mathlib API**: Helpers do not restate existing Mathlib lemmas.
- **Instance syntax**: Use `where`, not braces.
- **Mirrored paths**: Each library module has its matching test path, without renaming or grouping.
- **Matching namespaces**: Test sections match library namespaces.
- **One example per symbol**: Each exported definition fixes its type or definitional shape; each lemma has a restated example.
- **Signature, not implementation**: Examples cite public lemmas with `exact`, `simpa`, term mode or `rfl`, rather than copying proofs.
- **Round trips**: Test both directions of conversions and equivalences.
- **Composition**: Each milestone chains at least two exported lemmas into its intended consequence.
- **Separate examples**: Use separate examples rather than exercising an entire milestone in one example.
- **Fixtures stay local**: Use private test fixtures; do not add test-only helpers to the public API.
- **Test driver**: Prefer `testDriver` so `lake test` is a separate signal from `lake build`.

## Do not flag

- **Terminal simp**: Goal-closing `simp` need not become `simp only`.
- **Project conventions**: Project instructions govern namespaces, tests, bootstrap and dependencies.
- **Linter findings**: Omit findings already reported by CI compilation or Lean/Mathlib linters; build failures remain reportable if CI builds nothing.
- **Heartbeat options at or below 400000**: Accepted with a reason comment.
- **Readability opens**: Opening public library or dependency namespaces in tests is allowed.
- **Numerical coverage**: A handful of concrete instances suffices; exhaustive numeric cases are not required.
- **Merged default target**: A small project may build library and tests through `defaultTargets`.
