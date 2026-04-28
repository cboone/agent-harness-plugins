
# Mathlib Conventions

Conventions and patterns for using Mathlib4 effectively, incorporating the Mathlib community documentation guide. For finding lemmas, navigating the module hierarchy, and search strategies, see `mathlib-api-discovery.md`.

## Table of Contents

- [Module structure](#module-structure)
- [Documentation requirements](#documentation-requirements)
  - [Module docstrings](#module-docstrings)
  - [Declaration docstrings](#declaration-docstrings)
  - [Docstring format details](#docstring-format-details)
  - [Tactic documentation format](#tactic-documentation-format)
  - [Sectioning comments](#sectioning-comments)
  - [LaTeX and Markdown in docstrings](#latex-and-markdown-in-docstrings)
  - [Citations](#citations)
  - [Named theorems](#named-theorems)
  - [Language](#language)
  - [Linting commands](#linting-commands)
- [Variable conventions](#variable-conventions)
- [API design](#api-design)
- [Heartbeats and build performance](#heartbeats-and-build-performance)
- [Deprecation](#deprecation)

## Module Structure

Every Mathlib file follows this exact order:

1. Copyright header (`/- Copyright (c) ... -/`)
2. `module` keyword on its own line
3. `public import` statements (one per line)
4. Regular `import` statements (one per line)
5. Module docstring (`/-! -/` with mandatory sections)
6. Open/variable declarations
7. Definitions and theorems

```lean
/- Copyright (c) 2018 Robert Y. Lewis. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Robert Y. Lewis -/

module Mathlib.NumberTheory.Padics.PadicNorm

public import Mathlib.Algebra.Order.AbsoluteValue.Basic
public import Mathlib.NumberTheory.Padics.PadicVal.Basic

/-! # p-adic norm

This file defines the `p`-adic norm on `ℚ`.

## Main definitions

- `padicNorm`: the p-adic norm function on ℚ

## Implementation notes

Much, but not all, of this file assumes that `p` is prime.

## References

* [F. Q. Gouvêa, *p-adic numbers*][gouvea1997]

## Tags

p-adic, norm, valuation
-/

open BigOperators

variable {p : ℕ} [Fact (Nat.Prime p)]

-- definitions and theorems follow
```

## Documentation Requirements

### Module docstrings

Every file must have a module docstring using `/-! -/`. The docstring begins with a `#` heading and a 1-2 sentence summary. After the summary, include sections in this mandatory order:

| Section              | Required?                              |
| -------------------- | -------------------------------------- |
| Main definitions     | Optional if covered in summary         |
| Main statements      | Optional if covered in summary         |
| Notation             | Required unless no notation introduced |
| Implementation notes | When there are design decisions        |
| References           | Linking to `docs/references.bib`       |
| Tags                 | Searchable keywords, always present    |

Note: the section formerly called "Main Results" is named **"Main statements"** per the community guide.

### Declaration docstrings

Every public definition and theorem should have a docstring using `/-- -/`:

```lean
/-- A `Widget` represents a composable UI element with a unique identifier
and optional children. -/
structure Widget where
  id : Nat
  children : List Widget

/-- `Widget.childCount w` returns the number of direct children of `w`. -/
def Widget.childCount (w : Widget) : Nat :=
  w.children.length
```

Docstrings go directly above the declaration with no blank line between them. Start with the name of the thing being documented in backticks.

### Docstring format details

Delimiters `/--` and `-/` are placed with text separated by newlines or single spaces. Subsequent lines are unindented (flush left). Complete sentences end with periods. Docstrings may contain Markdown and LaTeX.

Docstrings may "lie slightly" about the implementation while preserving mathematical meaning. For example, if a definition uses a computationally efficient but mathematically opaque construction, the docstring may describe the mathematically equivalent formulation instead.

**Named theorems** should appear in **boldface** in docstrings.

### Tactic documentation format

Begin with a complete sentence using the tactic name as the subject. List all options and forms in bullet points. Include an "Examples:" section with code blocks.

````lean
/-- `ring` solves goals of the form `a = b` where `a` and `b` are
expressions in a commutative (semi)ring.

- `ring` closes the current goal
- `ring_nf` normalizes without closing the goal
- `ring_nf at h` normalizes a hypothesis

Examples:

```
example (x y : ℤ) : (x + y) ^ 2 = x ^ 2 + 2 * x * y + y ^ 2 := by ring
```
-/
````

### Sectioning comments

Use `/-! ... -/` with `###` headers to group related declarations within a file:

```lean
namespace Name

/-! ### Declarations about `name` -/

/-- Find the largest prefix `n` of a `Name` such that
`f n != none`, then replace this prefix. -/
def mapPrefix (f : Name → Option Name) (n : Name) : Name := ...

end Name
```

### LaTeX and Markdown in docstrings

- **Lean declaration references**: enclose in backticks for auto-linking in generated docs
- **URLs**: enclose in angle brackets (`<https://example.com>`)
- **Inline math**: `$ ... $`
- **Display math**: `$$ ... $$`
- **Environments**: `\begin{*} ... \end{*}` (no dollar signs needed)

### Citations

Add references to `docs/references.bib` in BibTeX format. Normalize with bibtool:

```bash
bibtool --preserve.key.case=on --preserve.keys=on \
  --print.use.tab=off --pass.comments=on -s \
  -i docs/references.bib -o docs/references.bib
```

Citation syntax in docstrings:

- Basic citation: `[Boole1854]` renders as a linked reference
- Custom text: `[Grundlagen der Geometrie][hilbert1999]`

### Named theorems

Reference named theorems in **boldface** within docstrings. For example: "This is a formalization of the **Hahn-Banach theorem**."

### Language

Write documentation in English. British, American, or Australian English are all acceptable. Use American English for declaration names (see naming conventions).

### Linting commands

Run these commands to check documentation coverage:

```lean
#lint only docBlame              -- missing doc strings
#lint only docBlame docBlameThm  -- definitions and theorems
#lint                            -- all default linters
#lint docBlameThm                -- all linters + theorem check
```

## Variable Conventions

Use `variable` to declare universally quantified variables at section scope:

```lean
variable {α : Type*}              -- generic type
variable {G : Type*} [Group G]    -- group with instance
variable {R : Type*} [Ring R]     -- ring with instance
variable {M : Type*} [AddCommMonoid M] [Module R M]  -- module
```

**Type variables**: use `Type*` (universe-polymorphic) rather than `Type` (universe 0) unless you specifically need a fixed universe.

**Instance arguments**: use square brackets `[...]` for type class instances. The elaborator finds them automatically.

**Implicit vs explicit**: make arguments implicit `{...}` when they can be inferred from later arguments. Make them explicit `(...)` when the caller must provide them.

```lean
-- Good: α inferred from the list argument
theorem List.length_map {α β : Type*} (f : α → β) (l : List α) :
    (l.map f).length = l.length := by
  simp

-- Good: n is explicit because it is the primary input
def Fin.last (n : Nat) : Fin (n + 1) :=
  ⟨n, Nat.lt_succ_iff.mpr (Nat.le_refl n)⟩
```

## API Design

### Transparency

Default to `semireducible` transparency. This means definitions unfold during type checking but not during tactic execution unless explicitly requested.

When you need to hide implementation details, prefer type synonyms over `irreducible`:

```lean
-- Preferred: type synonym
def Probability := { x : Float // 0 ≤ x ∧ x ≤ 1 }

-- Avoid: irreducible (makes working with the type unnecessarily difficult)
@[irreducible] def Probability := Float
```

### Decidable instances

Provide `Decidable` instances for propositions when computationally feasible. This enables `decide` and `#eval` to work with your types.

```lean
instance : DecidableEq MyType := by
  intro a b
  -- provide a decision procedure
  sorry
```

### Simp lemmas

Mark lemmas with `@[simp]` when they:

- Reduce complex expressions to simpler ones
- Establish a canonical normal form
- Will not cause looping (the left side must be "more complex" than the right)

```lean
@[simp]
theorem List.length_nil : ([] : List α).length = 0 := rfl

@[simp]
theorem List.length_cons (x : α) (xs : List α) :
    (x :: xs).length = xs.length + 1 := rfl
```

### Ext lemmas

Mark lemmas with `@[ext]` when they characterize equality of a type by its components:

```lean
@[ext]
theorem Point.ext {p q : Point} (hx : p.x = q.x) (hy : p.y = q.y) : p = q := by
  cases p; cases q; simp_all
```

## Heartbeats and Build Performance

A heartbeat is Lean's deterministic proxy for "work done" (roughly 1000 small kernel allocations). Every declaration elaborates under a budget; the default is 200000. `whnf`, typeclass search, `simp`, `decide`, `ring`, `linarith`, unification, and recursion through `fun_prop`/`positivity` all draw from the same pool.

**Thresholds to know:**

- **Default:** `maxHeartbeats 200000` per declaration.
- **Soft comfort zone:** up to `400000` (2×) passes Mathlib review without comment.
- **Needs justification:** `400000`–`800000` (2×–4×) should carry a one-line WHY comment.
- **Tech-debt threshold:** anything above `800000` (4×) is considered technical debt by the Mathlib community. Leave it only with a concrete plan to remove.

### Split first, optimize second

The most effective fix for a bloated declaration is almost always to **extract sub-lemmas**, not to tweak tactics. Because `maxHeartbeats` is *per-declaration*, splitting one giant proof into N smaller named lemmas gives each piece its own fresh 200000-heartbeat budget. The combiner then invokes N pre-compiled closed terms, which elaborate nearly for free.

Empirically validated result: on a proof with two declarations carrying `1600000` (8×) and `2400000` (12×) bumps, extracting eleven per-case facts into their own `private lemma`s dropped *both* declarations to the default `200000`, eliminating the bumps entirely. Build time fell from ~70s to ~3.5s. The file grew by ~90 lines of signatures but became more readable and reusable.

**Extraction prompts to ask when a declaration is over budget:**

- Does the proof have an "N parallel cases" shape (per-projection, per-coordinate, per-argument)? Extract one lemma per case.
- Are there distinct reasoning phases (pointwise identity, then reindex, then combine)? Extract one lemma per phase.
- Is the body longer than ~100 lines? Extraction will almost always help regardless of structure.

**Tactical tweaks (use after extraction, if still over budget):**

- `simp only [...]` instead of bare `simp` (narrows the rewrite set).
- Merge consecutive `simp only [..]` calls into one (halves goal traversals).
- Break a long `rw [a, b, c, d, ...]` chain into two or three shorter chains.
- Cache reused measurability / positivity proofs as named `have`s so they elaborate once.
- Provide explicit type annotations where elaboration has to search.
- Use `show <normalized form>; rfl` to sidestep expensive `rw` matching when the goal reduces definitionally.

These trim tens of percent at best. Splitting yields order-of-magnitude improvements because it changes the denominator.

**Raising the bump is last resort.** When keeping a bump, always:

- State the reason in a one-line comment immediately above `set_option maxHeartbeats`.
- Prefer the smallest power-of-two multiple that still compiles (test by escalating from default through `400000`, `800000`, `1600000`).
- Treat any bump above `800000` as a TODO to split further.

## Deprecation

When renaming or replacing a definition, Mathlib uses `@[deprecated]` with a date and an alias:

```lean
@[deprecated (since := "2026-04-05")]
alias old_theorem_name := new_theorem_name
```

The old name continues to work but produces a warning. When you encounter a deprecation warning while using Mathlib, switch to the new name it suggests. For the full contribution-side deprecation protocol (timelines, migration paths), see the [Mathlib contributor guide](https://leanprover-community.github.io/contribute/style.html).
