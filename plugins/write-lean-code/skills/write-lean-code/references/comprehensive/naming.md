
# Naming Conventions

Naming in Lean 4 follows conventions from the standard library and Mathlib. Good names make definitions discoverable via search tactics like `exact?` and `apply?`. Use American English for declaration names (`factorization`, `Localization`, `FiberBundle`, not British variants).

## Table of Contents

- [Case rules](#case-rules)
- [Acronyms](#acronyms)
- [File naming](#file-naming)
- [Lemma and theorem naming](#lemma-and-theorem-naming)
- [Symbol names dictionary](#symbol-names-dictionary)
- [Ordering: le/lt vs ge/gt](#ordering-lelt-vs-gegt)
- [Axiomatic descriptions](#axiomatic-descriptions)
- [Hypothesis separation](#hypothesis-separation)
- [Abbreviations](#abbreviations)
- [Left/right variants](#leftright-variants)
- [Namespaced references in lemma names](#namespaced-references-in-lemma-names)
- [Structural lemma naming](#structural-lemma-naming)
- [Predicate and class naming](#predicate-and-class-naming)
- [Unexpanded vs expanded function forms](#unexpanded-vs-expanded-function-forms)
- [Dots and namespaces for logical connectives](#dots-and-namespaces-for-logical-connectives)
- [Variable naming](#variable-naming)
- [Namespace conventions](#namespace-conventions)

## Case Rules

| Category                             | Convention                       | Examples                                         |
| ------------------------------------ | -------------------------------- | ------------------------------------------------ |
| Types, structures, classes           | `UpperCamelCase`                 | `NatPrime`, `MonoidHom`, `MyConfig`              |
| Prop constructors                    | `UpperCamelCase`                 | `Or.inl`, `And.intro`, `Exists.intro`            |
| Propositions (when used as types)    | `UpperCamelCase`                 | `Decidable`, `Nonempty`                          |
| Functions returning `Type` or `Sort` | `UpperCamelCase`                 | `List.cons` returns `List`, so `List.Cons`       |
| Functions returning a term           | `snake_case`                     | `is_prime`, `add_comm`, `map_append`             |
| Structure fields                     | follows return-type rule         | `UpperCamelCase` if `Type`; `snake_case` if term |
| Inductive constructors               | follows return-type rule         | `UpperCamelCase` if `Type`; `snake_case` if term |
| Local variables                      | `lowerCamelCase` or `snake_case` | `myVar`, `local_hyp`                             |

Functions are named after what they return. If a function returns a type (`Type` or `Sort`), it uses `UpperCamelCase`. If it returns a term, it uses `snake_case`.

When an `UpperCamelCase` name appears as a component within a `snake_case` lemma name, it becomes `lowerCamelCase`. For example, `Nat.cast` becomes `natCast` in a lemma name like `map_natCast`, and `Int.cast_natCast` embeds both casts in `snake_case` context.

### Notable Exceptions

- `Ne` uses `UpperCamelCase` to mirror `Eq`, even though it is a `Prop`-valued function
- `outParam` uses `lowerCamelCase` despite returning a `Sort`
- Interval notation uses a capitalized `I` prefix: `Set.Icc`, `Set.Iic`, `Set.Ico`, `Set.Ioo`

## Acronyms

The casing of acronyms depends on their length:

| Length     | Rule                             | Examples                           |
| ---------- | -------------------------------- | ---------------------------------- |
| 3 or fewer | Same case as surrounding context | `IO`, `IORef`, `ioRef`, `RPC`      |
| 4 or more  | Lowercase from the second letter | `Json`, `JsonRPC`, `Http`, `Wasm`  |

```lean
-- Good
structure JsonParser where ...
def parseJson (s : String) : IO Json := ...

-- Bad
structure JSONParser where ...
def parseJSON (s : String) : IO JSON := ...
```

## File Naming

Files use `UpperCamelCase` with the `.lean` extension, matching the module path:

```text
MyProject/
  Basic.lean          -- MyProject.Basic
  Data/
    List.lean         -- MyProject.Data.List
    List/
      Lemmas.lean     -- MyProject.Data.List.Lemmas
```

Each file should correspond to exactly one module. The directory structure mirrors the namespace hierarchy.

## Lemma and Theorem Naming

Mathlib uses a compositional naming scheme where lemma names encode the types, operations, and properties involved.

### Structure

```text
[Namespace.]operation_property
```

### Components

| Component | Description               | Examples                                  |
| --------- | ------------------------- | ----------------------------------------- |
| Type      | The primary type involved | `Nat`, `List`, `Finset`                   |
| Operation | The function or relation  | `add`, `mul`, `map`, `filter`, `mem`      |
| Property  | The property being proved | `comm`, `assoc`, `zero`, `succ`, `nil`    |
| Modifier  | Qualifiers and separators | `left`, `right`, `iff`                    |

### Examples

```lean
-- Pattern: Type.operation_property
theorem Nat.add_comm : ...           -- commutativity of Nat.add
theorem Nat.add_assoc : ...          -- associativity of Nat.add
theorem Nat.mul_one : ...            -- right identity of Nat.mul

-- Pattern: Type.operation1_operation2
theorem List.map_append : ...        -- map distributes over append
theorem List.filter_map : ...        -- interaction of filter and map

-- Pattern: Type.property
theorem List.length_nil : ...        -- length of empty list
theorem List.length_cons : ...       -- length after cons

-- Pattern: Predicate_property
theorem isPrime_of_gt : ...          -- sufficient condition for isPrime
```

## Symbol Names Dictionary

These tables list the standard Lean/Mathlib names for common symbols used in lemma and theorem names. The "Lean input" column shows the keyboard input sequence; use the "Name" column in theorem names.

### Logic

| Lean input   | Name       | Notes                  |
| ------------ | ---------- | ---------------------- |
| `\or`        | `or`       |                        |
| `\and`       | `and`      |                        |
| `\to` / `->` | `of`/`imp` | conclusion first       |
| `\iff`       | `iff`      | often omitted in names |
| `\not`       | `not`      |                        |
| `\exists`    | `exists`   | `bex` for bounded      |
| `\forall`    | `forall`   | `ball` for bounded     |
| `=`          | `eq`       | often omitted          |
| `\ne`        | `ne`       |                        |
| `\comp`      | `comp`     |                        |

### Set

| Lean input     | Name        | Notes              |
| -------------- | ----------- | ------------------ |
| `\in`          | `mem`       |                    |
| `\notin`       | `notMem`    |                    |
| `\cup`         | `union`     |                    |
| `\cap`         | `inter`     |                    |
| `\Union`       | `iUnion`    | `biUnion` bounded  |
| `\Inter`       | `iInter`    | `biInter` bounded  |
| `\Union\0`     | `sUnion`    | set union          |
| `\Inter\0`     | `sInter`    | set intersection   |
| `\`            | `sdiff`     | set difference     |
| `\compl`       | `compl`     | complement         |
| `{x \| p}`     | `setOf`     |                    |
| `{x}`          | `singleton` |                    |

### Algebra

| Lean input | Name        | Notes                 |
| ---------- | ----------- | --------------------- |
| `0`        | `zero`      |                       |
| `+`        | `add`       |                       |
| `-`        | `neg`/`sub` | unary/binary          |
| `1`        | `one`       |                       |
| `*`        | `mul`       |                       |
| `^`        | `pow`       |                       |
| `/`        | `div`       |                       |
| `\smul`    | `smul`      | scalar multiplication |
| `\inv`     | `inv`       |                       |
| `\invOf`   | `invOf`     |                       |
| `\dvd`     | `dvd`       | divisibility          |
| `\sum`     | `sum`       |                       |
| `\prod`    | `prod`      |                       |

### Lattices

| Lean input | Name   | Notes                         |
| ---------- | ------ | ----------------------------- |
| `<`        | `lt`   | prefer over `gt`              |
| `\le`      | `le`   | prefer over `ge`              |
| `>`        | `gt`   | use only when needed          |
| `\ge`      | `ge`   | use only when needed          |
| `\sup`     | `sup`  |                               |
| `\inf`     | `inf`  |                               |
| `\Sup`     | `iSup` | `biSup`/`ciSup` for variants  |
| `\Inf`     | `iInf` | `biInf`/`ciInf` for variants  |
| `\bot`     | `bot`  |                               |
| `\top`     | `top`  |                               |

## Ordering: le/lt vs ge/gt

Default to `le`/`lt` in theorem names. Use `ge`/`gt` only when:

1. Arguments appear in different orders than the `le`/`lt` version
2. Matching argument order of another relation (like `=`)
3. Describing the relation with swapped arguments
4. The second argument is "more variable"

```lean
-- Standard: use le/lt by default
theorem lt_iff_le_not_ge [Preorder α] {a b : α} :
    a < b ↔ a ≤ b ∧ ¬b ≤ a := sorry

-- ge justified: matching argument order of Eq
theorem Eq.ge [Preorder α] {a b : α} (h : a = b) :
    b ≤ a := sorry

-- gt justified: describing swapped relation
theorem ne_of_gt [Preorder α] {a b : α} (h : b < a) :
    a ≠ b := sorry
```

## Axiomatic Descriptions

Standard names for structural properties used in theorem names:

| Name                | Meaning              |
| ------------------- | -------------------- |
| `refl`              | reflexivity          |
| `irrefl`            | irreflexivity        |
| `symm`              | symmetry             |
| `trans`             | transitivity         |
| `antisymm`          | antisymmetry         |
| `asymm`             | asymmetry            |
| `congr`             | congruence           |
| `comm`              | commutativity        |
| `assoc`             | associativity        |
| `left_comm`         | left commutativity   |
| `right_comm`        | right commutativity  |
| `mul_left_cancel`   | left cancellation    |
| `mul_right_cancel`  | right cancellation   |
| `inj`               | injectivity          |
| `def`               | definition unfolding |

## Hypothesis Separation

The word "of" separates hypotheses in a theorem name. Hypotheses appear in the same order as in the theorem statement (not reversed):

```lean
#check lt_of_succ_le        -- succ_le is the hypothesis
#check lt_of_not_ge
#check lt_of_le_of_ne       -- two hypotheses: le, then ne
#check add_lt_add_of_lt_of_le
```

The conclusion comes first, then "of", then hypotheses left to right:

```text
conclusion_of_hypothesis1_of_hypothesis2
```

## Abbreviations

Use short forms instead of verbose descriptions:

| Short form | Replaces  |
| ---------- | --------- |
| `pos`      | `zero_lt` |
| `neg`      | `lt_zero` |
| `nonpos`   | `le_zero` |
| `nonneg`   | `zero_le` |

```lean
#check mul_pos
#check mul_nonpos_of_nonneg_of_nonpos
#check add_lt_of_lt_of_nonpos
```

## Left/Right Variants

Use `_left` and `_right` suffixes for variants operating on different arguments:

```lean
#check add_le_add_left
#check add_le_add_right
#check le_of_mul_le_mul_left
#check le_of_mul_le_mul_right
```

## Namespaced References in Lemma Names

When a namespace-qualified definition appears as part of a lemma name, remove the namespace prefix. If the bare name is ambiguous, prepend it in `lowerCamelCase`:

```lean
#check Prod.fst         -- the definition
#check continuous_fst   -- lemma about it (no namespace needed)

#check Nat.cast         -- the definition
#check map_natCast      -- lowerCamelCase to disambiguate

#check Int.cast_natCast -- both casts embedded in snake_case
```

## Structural Lemma Naming

### Extensionality

- `(forall x, f x = g x) -> f = g` is named `.ext` and tagged `@[ext]`
- `f = g <-> forall x, f x = g x` is named `.ext_iff`

### Injectivity

- Unidirectional (`Function.Injective f`): named `f_injective`
- Bidirectional (`f x = f y <-> x = y`): named `f_inj` or `.inj`, often `@[simp]`
- `_left`/`_right` refer to the changing argument: `sub_right_inj` for `a - b = a - c <-> b = c`

### Induction and Recursion Principles

| Motive eliminates into    | Value first      | Constructions first |
| ------------------------- | ---------------- | ------------------- |
| `Prop`                    | `T.induction_on` | `T.induction`       |
| `Sort u` or `Type u`      | `T.recOn`        | `T.rec`             |

Include `on` when the value precedes the constructions in argument order.

## Predicate and Class Naming

### Predicate Position

Predicates use prefix form by default:

```lean
-- Good: predicate first
theorem isClosed_Icc : IsClosed (Set.Icc a b) := ...

-- Bad: subject first
theorem Icc_isClosed : IsClosed (Set.Icc a b) := ...
```

### Suffix Exceptions

Some predicates appear as suffixes rather than prefixes:

- `_inj`, `_injective`, `_surjective`, `_bijective`
- `_mono`, `_monotone`, `_antitone`, `_strictMono`, `_strictAnti`

For binary operations, `_left`/`_right` precede the suffix (e.g., `mul_left_monotone`).

### Prop-Valued Classes

- Noun classes: prefix with `Is` (e.g., `IsNormal`, `IsTopologicalRing`)
- Adjective classes: may omit `Is` when the English reads naturally (e.g., `Normal`, since "subgroup is normal" works as prose)

## Unexpanded vs Expanded Function Forms

Distinguish between `f * g` (pointwise) and `fun x => f x * g x` (expanded):

- Unexpanded (`f * g`): use the operation name alone (e.g., `mul`)
- Expanded (`fun x => f x * g x`): prefix with `fun_` (e.g., `fun_mul`)

```lean
theorem Continuous.mul (hf : Continuous f) (hg : Continuous g) :
    Continuous (f * g)

theorem Continuous.fun_mul (hf : Continuous f) (hg : Continuous g) :
    Continuous fun x => f x * g x
```

Both variants should have the `fun_prop` attribute. The same pattern applies to `add`, `sub`, `neg`, `pow`, and composition.

## Dots and Namespaces for Logical Connectives

Introduction, elimination, and destruction rules use dot notation:

```lean
-- Introduction and elimination
And.intro    And.left     And.right
Or.inl       Or.inr       Or.elim
Iff.intro    Iff.mp       Iff.mpr
Not.intro    Not.elim
Exists.intro Exists.elim
Eq.refl      Eq.subst
True.intro   False.elim
```

Properties with projection notation:

```lean
And.symm     Or.symm      Or.resolve_left  Or.resolve_right
Eq.symm      Eq.trans      Iff.symm         Iff.refl
```

## Variable Naming

Mathlib uses conventional single-letter names for mathematical objects:

| Variable | Meaning                            |
| -------- | ---------------------------------- |
| `u v w`  | Universe levels                    |
| `a b c`  | Elements of a type                 |
| `m n k`  | Natural numbers                    |
| `f g`    | Functions or morphisms             |
| `h`      | Hypotheses (e.g., `h1`, `h2`)      |
| `s t`    | Sets                               |
| `x y z`  | Elements (generic)                 |
| `G`      | Groups                             |
| `R`      | Rings                              |
| `K`      | Fields                             |
| `M`      | Monoids or modules                 |
| `p q`    | Propositions or primes             |

For Greek letters used as type variables (`α`, `β`, `γ`) and analysis constants (`ε`, `δ`), use the standard Lean input notation (`\alpha`, `\beta`, `\gamma`, `\epsilon`, `\delta`).

```lean
-- Good: conventional variables
variable {α : Type*} {G : Type*} [Group G]
theorem mul_inv_cancel (a : G) : a * a⁻¹ = 1 := ...

-- Bad: unconventional names
variable {MyType : Type*} {MyGroup : Type*} [Group MyGroup]
```

## Namespace Conventions

- Place definitions and theorems about a type in that type's namespace
- Use `open` judiciously; prefer qualified names for clarity in library code
- Use `scoped` for notation and instances that should only be active when the namespace is opened

```lean
namespace Nat

theorem add_comm (m n : Nat) : m + n = n + m := ...

end Nat

-- Usage
#check Nat.add_comm
open Nat in #check add_comm
```
