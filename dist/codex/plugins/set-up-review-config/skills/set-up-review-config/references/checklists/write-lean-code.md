# Lean Review Checklist

Applies to Lean 4 source files (`*.lean`). Cite findings as `write-lean-code: Rule name`.

## Important

- **No sorry**: Finished declarations contain no `sorry`, unless the project's own instructions allow a tracked placeholder.
- **Heartbeat budgets**: A new or raised `set_option maxHeartbeats` has a one-line comment saying why. Anything above 800000 needs the proof split into named sub-lemmas instead, since each declaration gets its own budget.
- **Non-terminal simp**: A `simp` that does not close its goal is written as `simp only [...]`, so the proof does not break when simp lemmas change.
- **Deprecations**: A renamed or removed public declaration leaves a `@[deprecated (since := "YYYY-MM-DD")]` alias that names its replacement.
- **Classical in extracted lemmas**: A sub-lemma extracted from a `classical` proof starts with `classical` itself when it needs decidability instances.

## Nits

- **Declaration case**: Names follow what the declaration returns. Types, structures, classes and functions returning a `Type` or `Sort` use `UpperCamelCase`; theorems and functions returning a term use `snake_case`. An `UpperCamelCase` name inside a `snake_case` name becomes `lowerCamelCase` (`map_natCast`).
- **Acronyms**: Three letters or fewer keep one case (`IO`, `ioRef`); four or more capitalize only the first letter (`Json`).
- **Lemma names**: Built from the type, operation and property (`List.map_append`), following Mathlib's symbol dictionary (`mem`, `add`, `sup`) and naming hypotheses in order with `of` (`lt_of_le_of_ne`).
- **le and lt**: Names and statements prefer `le` and `lt` over `ge` and `gt`.
- **Predicate names**: Prefix form (`isClosed_Icc`), and Prop-valued classes take an `Is` prefix (`IsNormal`).
- **American English**: Declaration names use American spelling (`factorization`).
- **File names**: `UpperCamelCase.lean`, matching the module path.
- **Type annotations**: Every declaration states its argument and return types.
- **by placement**: `by` ends the preceding line; tactic blocks are indented two spaces; subgoals are focused with `·`.
- **Continuation lines**: Four-space indent, with operators at the start of the continuation line rather than the end of the previous one.
- **Lambda syntax**: `fun x ↦ ...`, with `·` only for very simple closures.
- **Structured proofs**: Long proofs use `have`, `suffices`, `calc` and `show` instead of a long flat tactic sequence.
- **Hypotheses before the colon**: Hypotheses a proof introduces immediately are stated left of the colon.
- **Module docstring**: Each file has a `/-! -/` module docstring with a title, summary, and Main definitions and Main statements sections where they apply.
- **Declaration docstrings**: Public definitions and main theorems have a `/-- -/` docstring directly above them.
- **Comments explain why**: Proof comments state hidden constraints, unusual lemma choices or load-bearing invariants, not step-by-step narration such as `-- Step 1:`.
- **No hard wrapping**: Each comment or docstring paragraph is one line; blank lines separate paragraphs.
- **Existing Mathlib API**: A new helper lemma does not restate a lemma Mathlib already provides.
- **Instance syntax**: Instances use `where` rather than braces.

## Do not flag

- **Terminal simp**: A `simp` that closes its goal does not need to be squeezed into `simp only`.
- **Project conventions**: Namespace layout, test layout, bootstrap scripts and vendored dependencies follow the project's own `AGENTS.md` or `CLAUDE.md`, which take precedence over this checklist.
- **Linter findings**: Anything `lake lint` or Mathlib's style linters report when they run in CI, and anything that stops `lake build` from succeeding.
- **Heartbeat options at or below 400000**: When they carry a comment saying why.
