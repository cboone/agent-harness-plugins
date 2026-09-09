# Lean 4 Style Essential Checklist

Quick reference for code reviews. For detailed guidance, see `../comprehensive/`.

## Project-Local Conventions

The invoking project's CLAUDE.md (or equivalent agent-config file) is authoritative for:

- [ ] Bootstrap script to run in a fresh clone or worktree before any direct `lake build` (Mathlib must come from `lake exe cache get`, not a local source compilation)
- [ ] Test-suite layout and the rule for keeping tests in lockstep with proof code (if the project mirrors its test suite against proof modules)
- [ ] Namespace conventions (single top-level namespace, nested paper-specific namespaces, or other)
- [ ] Vendored Lean dependencies that must be excluded from grep-for-conventions searches and from Mathlib API searches
- [ ] The command(s) that constitute the full local check before declaring a proof change finished

For the canonical Mathlib-downstream shape (bootstrap script, Makefile target set, `lintDriver = "batteries/runLinter"`, entrypoint manifest that re-exports every submodule, `testDriver` vs `defaultTargets`, test-library naming and discipline), see `../comprehensive/build-infrastructure.md`.

## Naming

- [ ] Types, structures, classes: `UpperCamelCase`

  ```lean
  structure MyConfig where
    fieldName : Nat
  ```

- [ ] Terms, proofs, functions, theorems: `snake_case` (or `lowerCamelCase` matching return type)

  ```lean
  def is_prime (n : Nat) : Bool := ...
  theorem add_comm (a b : Nat) : a + b = b + a := ...
  ```

- [ ] Acronyms with 3 or fewer letters: keep same case (`IO`, `IORef`, `ioRef`)
- [ ] Acronyms with 4+ letters: lowercase from second letter (`Json`, `JsonRPC`)
- [ ] Predicates: prefix form preferred (`isClosed_Icc` not `Icc_isClosed`)
- [ ] Files: `UpperCamelCase.lean`, matching the module path
- [ ] Lemma names: compose from type, operation, and property (`List.map_append`, `Nat.add_comm`)
- [ ] Mathlib variable conventions: `u, v, w` (universes), `α, β, γ` (generic types), `m, n, k` (naturals), `h` (hypotheses), `G` (groups), `R` (rings), `K` (fields)
- [ ] Symbol names follow Mathlib dictionary (`∨` -> `or`, `∈` -> `mem`, `+` -> `add`, `⊔` -> `sup`, etc.)
- [ ] Prefer `le`/`lt` over `ge`/`gt` in names
- [ ] "of" separates hypotheses in theorem order (`lt_of_le_of_ne`, not reversed)
- [ ] Prop-valued noun classes prefixed with `Is` (`IsNormal`, `IsTopologicalRing`)
- [ ] American English for declaration names (`factorization`, `Localization`)

## Formatting

- [ ] Indentation: 2 spaces (never tabs)
- [ ] No hardwrapping; let the editor handle visual wrapping
- [ ] Continuation lines: 4-space indentation
- [ ] Spaces around `:`, `:=`, and infix operators
- [ ] Operators placed at the start of continuation lines, not at the end of the preceding line

  ```lean
  -- Good
  def longExample :=
    someValue
    + anotherValue

  -- Bad
  def longExample :=
    someValue +
    anotherValue
  ```

- [ ] No trailing whitespace
- [ ] Single trailing newline at end of file
- [ ] Explicit type annotations and return types on all declarations
- [ ] Prefer `fun` with `↦`; `·` only for very simple closures
- [ ] `calc` relation symbols aligned vertically
- [ ] Use `<|` and `|>` to minimize parentheses

## File Structure

- [ ] Copyright header, then `module` keyword on its own line
- [ ] `public import` statements, then regular `import` statements (both alphabetical)
- [ ] Module docstring present (using `/-! -/` delimiters) with mandatory sections:

  ```lean
  /-!
  # Module Title

  Summary of what this module provides.

  ## Main definitions

  - `MyType`: description

  ## Main statements

  - `my_theorem`: description

  ## Notation

  (if any notation is introduced)

  ## Implementation notes

  (design decisions, non-obvious choices)

  ## References

  * [Author, *Title*][bibtex_key]

  ## Tags

  keyword1, keyword2
  -/
  ```

- [ ] Declaration docstrings use `/-- -/`, placed directly above the declaration

  ```lean
  /-- `factorial n` computes `n!` for natural numbers. -/
  def factorial : Nat → Nat
    | 0 => 1
    | n + 1 => (n + 1) * factorial n
  ```

- [ ] Tactic docstrings: complete sentence as subject, bullet-point options, "Examples:" section
- [ ] Sectioning comments (`/-! ### Section title -/`) to group related declarations
- [ ] Named theorems boldfaced in docstrings

## Proof Style

- [ ] `by` placed at end of preceding line, not on its own line

  ```lean
  -- Good
  theorem my_thm : P := by
    exact h

  -- Bad
  theorem my_thm : P :=
  by
    exact h
  ```

- [ ] Tactic blocks indented 2 spaces from `by`
- [ ] Subgoals focused with `·`, indented 2 spaces

  ```lean
  theorem my_thm : P ∧ Q := by
    constructor
    · exact hp
    · exact hq
  ```

- [ ] Prefer terminal tactics that close goals: `simp`, `omega`, `decide`, `norm_num`, `ring`, `linarith`, `exact`, `assumption`
- [ ] Terminal `simp` is NOT squeezed (leave as-is when it closes the goal)
- [ ] Non-terminal `simp` replaced with `simp only [...]`
- [ ] Use structured proof elements (`have`, `suffices`, `calc`, `show`) for clarity in complex proofs
- [ ] No `sorry` in finished code (acceptable as a placeholder during development)
- [ ] Hypotheses preferred left of the colon when proof introduces them immediately

## Comments

- [ ] `/-! -/` for section headers and documentation (rendered in generated docs)
- [ ] `/- -/` for technical notes and TODOs
- [ ] `--` for inline comments
- [ ] No hardwrapping in comments or docstrings -- each paragraph is a single long line, blank lines separate paragraphs
- [ ] Comments in proof bodies explain WHY, not WHAT — calibrated to the audience. Strip phase markers (`-- Step 1:`, `-- **Step N.**`, `-- Now we...`) and WHAT-narration; the tactic names describe the block. Keep comments that surface hidden constraints, unusual lemma choices, load-bearing invariants, or — if the expected reader is still learning Lean — a brief framing near a specialized lemma/tactic they would not recognize (see `../comprehensive/style-and-formatting.md#comments`).

## Documentation

- [ ] English required in all documentation
- [ ] American English for declaration names
- [ ] Citations reference `docs/references.bib` using `[AuthorYear]` syntax
- [ ] Run `#lint only docBlame` to check for missing docstrings

## Common Pitfalls

- [ ] Lean is whitespace-sensitive: multi-line blocks (`by`, `do`, `match`, `where`) end via dedentation
- [ ] `rfl` only works for definitional equality, not propositional equality; use `simp` or `rw` for the latter
- [ ] Before `induction`, `clear` unused variables from the local context to avoid unwanted generalization
- [ ] Use `lake new` (not `lake init`) to create new projects; `lake init` does not create a new directory
- [ ] Escape curly braces in docstrings that contain Lean syntax
- [ ] `omit [instance] in` goes _before_ the docstring and `private lemma`, not after. Parser rejects the inverse order.
- [ ] `Finset.sum_nbij'` takes simple functions `ι → κ`; `Finset.sum_bij'` takes dependent `∀ a ∈ s, κ`. Wrapping `embed` as `fun d _ => embed d` for `sum_nbij'` triggers a universe unification failure (see `../comprehensive/proof-style.md#reindexing-finset-sums`).

## Proof Performance

- [ ] Default `maxHeartbeats` is 200000. Soft review threshold: 400000 (2×). Mathlib tech-debt line: 800000 (4×).
- [ ] Before bumping `maxHeartbeats`, extract sub-lemmas. `maxHeartbeats` is per-declaration, so splitting an over-budget proof into N named lemmas gives each its own fresh 200000 budget — order-of-magnitude improvement (see `../comprehensive/mathlib.md#heartbeats-and-build-performance`).
- [ ] Tactical tweaks (`simp only`, merging `simp`s, narrower `rw` chains) are tens-of-percent improvements. Apply _after_ extraction, not instead.
- [ ] Any surviving `set_option maxHeartbeats` needs a one-line WHY comment; anything above 800000 is a TODO to split further.
- [ ] When extracting from a `classical`-prefixed proof, add `classical` to each extracted sub-lemma. The parent's `classical` does not propagate, and product-type `DecidableEq` synthesis fails silently without it.

## Mathlib API Discovery

- [ ] Before writing a custom lemma, search for an existing Mathlib lemma: predict the name from naming conventions, try `exact?`/`apply?`/`rw?`, then grep the project's Mathlib package path
- [ ] For `Finset` operations, check `Mathlib.Data.Finset.{Basic,Card,Image,Filter,Sum,Lattice}` and `Mathlib.Algebra.BigOperators.Group.Finset`
- [ ] For `Fin`/`Fintype` operations, check `Mathlib.Data.Fin.Basic` and `Mathlib.Data.Fintype.{Basic,Card,Pi}`
- [ ] When `exact?` times out, narrow the goal with `show`, `have`, or `change` before retrying
- [ ] When grepping Mathlib source, search for both `theorem` and `lemma` declarations
- [ ] Exclude any vendored Lean dependencies the project's CLAUDE.md flags (e.g. third-party packages that live under the project's `.lake/packages/` but are not Mathlib)

## API Design (Mathlib)

- [ ] Default to `semireducible` transparency
- [ ] Use type synonyms instead of `irreducible` when hiding implementation
- [ ] Prefer `where` syntax over braces for instance declarations
- [ ] Deprecations include date and migration path

  ```lean
  @[deprecated (since := "2026-04-05")] alias old_name := new_name
  ```

- [ ] Allow 6 months before removing deprecated definitions
