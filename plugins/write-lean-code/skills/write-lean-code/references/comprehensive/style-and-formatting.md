
# Style and Formatting

Formatting rules for Lean 4 code, drawn primarily from the Mathlib community style guide. Where the community guide and other sources disagree, the community guide takes precedence.

## Table of Contents

- [Indentation](#indentation)
- [Whitespace and operators](#whitespace-and-operators)
- [Import organization](#import-organization)
- [Sections and namespaces](#sections-and-namespaces)
- [Declarations](#declarations)
- [Hypotheses positioning](#hypotheses-positioning)
- [Anonymous functions](#anonymous-functions)
- [Calculation proofs](#calculation-proofs)
- [Documentation](#documentation)
- [Comments](#comments)
- [Terminal simp](#terminal-simp)

## Indentation

**Indentation**: 2 spaces, consistently. Never use tabs. Do not hardwrap lines; let the editor handle visual wrapping.

**Continuation lines use 4-space indentation.** When a declaration signature is too long, break after `:` or before `->` and indent continuation lines by 4 spaces:

```lean
-- Good: 2-space indentation for body, 4-space for continuation
def myFunction (n : Nat) : Nat :=
  if n = 0 then
    1
  else
    n * myFunction (n - 1)

-- Bad: 4-space indentation for body
def myFunction (n : Nat) : Nat :=
    if n = 0 then
        1
    else
        n * myFunction (n - 1)
```

```lean
-- Good: 4-space continuation for long signatures
theorem very_long_theorem_name
    (h₁ : Condition1) (h₂ : Condition2)
    (h₃ : Condition3) :
    Conclusion := by
  sorry

-- Good: break before arrow in function types
def transform
    (input : VeryLongTypeName)
    → AnotherLongTypeName
    → ResultType :=
  sorry
```

## Whitespace and Operators

**Spaces around operators**: always include spaces around `:`, `:=`, `->`, `<-`, `<->`, `/\`, `\/`, `+`, `*`, and all other infix operators.

```lean
-- Good
def f (x : Nat) : Nat := x + 1
theorem h : P /\ Q <-> Q /\ P := ...

-- Bad
def f (x:Nat):Nat:=x+1
```

**Operator placement on line breaks**: place the operator at the start of the continuation line, not at the end of the preceding line.

```lean
-- Good: operator leads continuation
def result :=
  firstTerm
  + secondTerm
  + thirdTerm

-- Bad: operator trails
def result :=
  firstTerm +
  secondTerm +
  thirdTerm
```

**Pipe operators**: use `<|` and `|>` to minimize parentheses, especially in tactic mode:

```lean
-- Good: pipe operator
exact h |>.symm

-- Instead of nested parentheses
exact (h).symm
```

**Blank lines**:

- One blank line between top-level declarations
- No blank line between a docstring and its declaration
- One blank line before and after section/namespace blocks (when not at file boundaries)
- No multiple consecutive blank lines

## Import Organization

The `module` keyword goes on its own line after the copyright header, before any imports. Distinguish `public import` (re-exported to downstream files) from regular `import`. Both groups are sorted alphabetically.

```lean
/- Copyright (c) 2026 Author Name. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Author Name -/

module MyProject.MyModule

public import Mathlib.Algebra.Group.Defs

import Mathlib.Tactic.Ring
import MyProject.Basic
```

Within each group, sort alphabetically. Do not rename imports unless there is a genuine name collision.

## Sections and Namespaces

**Sections** group related variable declarations:

```lean
section GroupTheory

variable {G : Type*} [Group G]

theorem mul_left_cancel (a b c : G) (h : a * b = a * c) : b = c := by
  sorry

theorem mul_right_cancel (a b c : G) (h : b * a = c * a) : b = c := by
  sorry

end GroupTheory
```

**Namespaces** scope definitions and create dot notation:

```lean
namespace MyStructure

def create : MyStructure := ...
def transform (s : MyStructure) : MyStructure := ...

end MyStructure

-- Usage via dot notation
#check MyStructure.create
#check myInstance.transform
```

**Guidelines**:

- Use `section` for grouping variable declarations that apply to multiple theorems
- Use `namespace` for organizing definitions belonging to a type or concept
- Do not nest more than 2-3 levels deep
- Close sections and namespaces promptly; avoid leaving them open across many unrelated definitions
- Use `open ... in` for localized namespace opening rather than bare `open` at file scope

```lean
-- Good: localized open
open Finset in
theorem card_union_le : ...

-- Acceptable at file scope when the namespace is used pervasively
open BigOperators
```

**`omit` clause for unused section variables.** When a `variable` block binds typeclass hypotheses that a specific lemma does not need, Lean's linter warns about `automatically included section variable(s) unused`. Suppress the warning with `omit [...] in` directly above the declaration. Placement matters:

```lean
-- Good: omit BEFORE the docstring, directly above the declaration.
omit [MeasurableSingletonClass S₁] [MeasurableSingletonClass S₂] in
/-- Useful lemma. -/
private lemma my_lemma : ... := ...

-- Bad: omit AFTER the docstring. Parser rejects with "unexpected token 'omit'".
/-- Useful lemma. -/
omit [MeasurableSingletonClass S₁] in
private lemma my_lemma : ... := ...
```

Multi-instance omits stack on one line or wrap across lines; either works. Do not wrap `omit` at arbitrary column counts — use `in` on the final line to anchor the scope:

```lean
omit [MeasurableSingletonClass S₁] [MeasurableSingletonClass S₂]
     [MeasurableSingletonClass S₃] [MeasurableSingletonClass S₄] in
private lemma wide_omit : ...
```

When a cluster of lemmas all omit the same instances, prefer nested `section`s that introduce only the fixtures actually needed, rather than scattering `omit` repeatedly. `omit` is the right tool for one-off deviations, not the recurring pattern.

## Declarations

**Type annotations**: always provide explicit type annotations, even when Lean can infer them. Always provide explicit return types for all declarations.

```lean
-- Good: explicit type annotation and return type
def double (n : Nat) : Nat := 2 * n

-- Bad: omitted return type
def double (n : Nat) := 2 * n
```

**Definition style**: use pattern matching when there are multiple cases, `:=` for simple definitions.

```lean
-- Good: pattern matching for multiple cases
def factorial : Nat → Nat
  | 0 => 1
  | n + 1 => (n + 1) * factorial n

-- Good: simple definition
def double (n : Nat) : Nat := 2 * n

-- Good: where clause for local definitions
def f (x : Nat) : Nat :=
  g x + h x
where
  g (n : Nat) : Nat := n + 1
  h (n : Nat) : Nat := n * 2
```

**Structure declarations**: align field names when it improves readability.

```lean
structure Point where
  x : Float
  y : Float
  z : Float
  deriving Repr, BEq
```

**Instance declarations**: use `instance` with anonymous names for standard instances; name them when they need to be referenced. Prefer `where` syntax over braces for instance declarations.

```lean
-- Good: where syntax (preferred)
instance : Add MyType where
  add a b := ...

-- Good: named instance with where syntax
instance myTypeOrd : Ord MyType where
  compare a b := ...

-- Bad: brace syntax
instance : Add MyType := {
  add := fun a b => ...
}
```

## Hypotheses Positioning

Prefer placing hypotheses as arguments left of the colon when the proof introduces them immediately. This improves readability.

```lean
-- Preferred: hypothesis left of colon
theorem mul_comm (a b : G) : a * b = b * a := by
  sorry

-- Less preferred when proof uses the hypothesis immediately
theorem mul_comm : ∀ (a b : G), a * b = b * a := by
  intro a b
  sorry
```

## Anonymous Functions

Prefer `fun` with `↦` over `λ` or `$`. Use centered dot `·` only for very simple functions.

```lean
-- Good
List.map (fun x ↦ x + 1) xs

-- Good: centered dot for very simple cases
List.map (· + 1) xs

-- Bad: lambda notation
List.map (λ x => x + 1) xs
```

## Calculation Proofs

Align relation symbols vertically. Place the `calc` keyword at the end of the preceding line:

```lean
theorem example_calc (a b c : Nat) (hab : a = b) (hbc : b = c) : a = c := by
  calc a = b := hab
    _ = c := hbc
```

See `proof-style.md` for detailed proof technique guidance.

## Documentation

**Module docstrings** use `/-! -/` and appear after imports, before any declarations:

```lean
/-!
# Linear Maps

This module defines linear maps between modules and proves basic properties.

## Main Definitions

- `LinearMap`: a structure representing a linear map `M →ₗ[R] N`
- `LinearMap.comp`: composition of linear maps
- `LinearMap.id`: the identity linear map

## Main Results

- `LinearMap.comp_assoc`: composition is associative
- `LinearMap.id_comp`: identity is a left unit for composition

## Notation

- `M →ₗ[R] N` for `LinearMap R M N`

## Implementation Notes

We use bundled morphisms rather than unbundled predicate-based approaches.
-/
```

**Declaration docstrings** use `/-- -/`, placed directly above with no blank line:

```lean
/-- `factorial n` computes the factorial of `n`.

This uses the recursive definition: `0! = 1` and `(n+1)! = (n+1) * n!`. -/
def factorial : Nat → Nat
  | 0 => 1
  | n + 1 => (n + 1) * factorial n
```

Docstring paragraphs are single long lines; do not insert hard line breaks within a paragraph. See [Comments](#comments) for the no-hardwrap rule.

## Comments

Lean uses three tiers of comments, each with a distinct purpose:

| Syntax   | Purpose                                                        |
| -------- | -------------------------------------------------------------- |
| `/-! -/` | Section headers and documentation (rendered in generated docs) |
| `/- -/`  | Technical notes, TODOs, and non-documentation comments         |
| `--`     | Inline comments                                                |

```lean
/-! ### Group theory results -/

/- TODO: generalize to monoids -/

-- This step uses the cancellation lemma
```

Place comments above the code they describe, not inline, when the explanation is more than a few words.

**Do not hardwrap comment text.** This applies to all comment forms (`/-- -/`, `/-! -/`, `/- -/`, `--`) and to docstrings. Each paragraph is a single long line; blank lines separate paragraphs. Let the editor handle visual wrapping. Mathlib source itself often hardwraps comments, but for this style guide the no-hardwrap rule applies to comments as well as code.

**Comments in proof bodies explain WHY, not WHAT — calibrated to the audience.** The WHY-not-WHAT rule applies with extra force inside tactic proofs because tactic names already *are* the description. Phase markers (`-- Step 1:`, `-- **Step N.**`), announcements of what a block does (`-- Rewrite p̂/p̃ as a single fraction`), and restatements of intermediate goal states (`-- Now both sides are combinations of …`) are almost always cuttable — they narrate what the next few tactics will accomplish, which those tactics will accomplish whether or not the comment describes them first.

What survives depends on the reader you are writing for. Three kinds of comment reliably earn their place regardless of audience: hidden constraints, load-bearing invariants, and unusual lemma choices that a reader would not derive from the tactics themselves. A fourth kind earns its place *audience-dependently*: a brief framing near a tactic or lemma name the expected reader would not recognize.

```lean
-- Bad: narrates the tactics, which already say what they do.
-- Expand delta entropy-by-entropy, applying chain_rule and entropy_comm.
rw [delta_eq_entropy hZ hU hX hY μ, chain_rule'' μ hZ hX, ...]
-- Lift each entropy to a 4-tuple sum via `entropy_eq_sum_joint`.
have hHZ := entropy_eq_sum_joint ...

-- Good for an expert reader: no comment. The tactics are self-describing.
rw [delta_eq_entropy hZ hU hX hY μ, chain_rule'' μ hZ hX, ...]
have hHZ := entropy_eq_sum_joint ...

-- Good (non-obvious invariant — earns its place regardless of audience):
-- Rearranges the factors to keep `pZU (z, u)` adjacent so `Real.log_mul` succeeds with
-- `hZU_pos.ne'` rather than needing a separate `positivity` call.
rw [show a * b * c * d * pZU (z, u) = a * (b * (c * (d * pZU (z, u)))) from by ring]
```

**Calibrating to the audience.** In a Mathlib PR reviewed by experts, self-evident tactics (`rfl`, `ring`, `positivity`, `linarith`, `simp`, plain `rw`, `intro`, `cases`, `omega`) never need commentary, and structural narration is noise. In a project whose primary reader is still learning Lean — or learning formalization — the threshold for "obvious" is lower: a specialized lemma name (`Finset.sum_nbij'`, `condIndepFun_iff_condIndepSet`), an unusual `simp_rw` argument list, a `measurability` call in an unexpected place, or a tactic combination that encodes a specific rewriting strategy may warrant a one-line WHY framing. Docstrings on declarations lean longer in learner-facing projects too: a few sentences explaining the role of the lemma in the broader proof is appropriate where a Mathlib-PR docstring would be a terse reference-style one-liner.

Two calibration tests:

- *If this comment disappeared, would the expected reader still be able to trace the proof?* If yes for an expert but no for a learner, the answer depends on who the reader is. Err on the side of keeping the comment when the project's documentation indicates a less-experienced audience, or the user or project CLAUDE.md requests more thorough comments.
- *Does the comment describe WHAT the next few tactics will do, or WHY this approach rather than the obvious alternative?* WHAT is cuttable if tactic names suffice. WHY is a keeper.

Phase markers — `-- **Step 1.**`, `-- **Step 2.**`, `-- N.`, `-- Now …`, `-- Combine …`, `-- Use that …` — are the most common offenders and usually cuttable. If a long proof has genuine structural phases (a multi-phase reduction the reader needs to orient through), prefer section headers via `/-! ### Phase N -/` inside the proof file, or a sentence in the declaration's docstring describing the plan, over inline `--` narration.

## Terminal Simp

Do not squeeze terminal `simp` calls (those that close a goal). Leave them as `simp` or `simp [specific_lemmas]`. Only squeeze non-terminal `simp` (followed by more tactics) to `simp only [...]`.
