
# Mathlib API Discovery

How to find existing Mathlib lemmas, navigate the module hierarchy, and avoid reinventing what Mathlib already provides. This is the usage-side complement to `mathlib.md` (documentation and API design conventions) and `naming.md` (the compositional naming scheme).

## Table of Contents

- [Search strategy ladder](#search-strategy-ladder)
- [Module hierarchy map](#module-hierarchy-map)
  - [Finite sets and combinatorics](#finite-sets-and-combinatorics)
  - [Finite types and cardinality](#finite-types-and-cardinality)
  - [Number types](#number-types)
  - [Algebraic structures and big operators](#algebraic-structures-and-big-operators)
  - [Order and lattice theory](#order-and-lattice-theory)
  - [Analysis and inequalities](#analysis-and-inequalities)
  - [Tactics](#tactics)
- [Common lookup patterns](#common-lookup-patterns)
  - [Finset sums](#finset-sums)
  - [Finset membership and filtering](#finset-membership-and-filtering)
  - [Finset cardinality](#finset-cardinality)
  - [Fin and coercions](#fin-and-coercions)
  - [Real-number arithmetic](#real-number-arithmetic)
  - [Logarithms](#logarithms)
  - [Division and reciprocals](#division-and-reciprocals)
- [Reading Mathlib source](#reading-mathlib-source)
- [When search tactics fail](#when-search-tactics-fail)

## Search Strategy Ladder

When you need a Mathlib lemma, work through these steps in order. Each step is more expensive than the previous one; stop as soon as you find what you need.

### 1. Predict the name

Mathlib naming is compositional: the name encodes the type, the operation, and the property. See `naming.md` for the full scheme. The key pattern is `Type.operation_property` or `operation_property_of_hypothesis`:

```text
Finset.sum_congr        -- Finset + sum + congruence
Finset.card_filter_le   -- Finset + cardinality + filter + le
Nat.add_comm            -- Nat + add + commutativity
Real.log_mul            -- Real + log + multiplication
List.map_append         -- List + map + append
```

Once you have a predicted name, test it with `#check`:

```lean
#check Finset.sum_congr
#check @Finset.sum_congr  -- shows all implicit arguments
```

### 2. Use search tactics

These tactics search the Mathlib API for lemmas that close or simplify the current goal. They work best on focused, specific goals.

| Tactic   | What it searches for                                           |
| -------- | -------------------------------------------------------------- |
| `exact?` | A single lemma or term that closes the goal exactly            |
| `apply?` | A lemma whose conclusion matches the goal (may leave subgoals) |
| `rw?`    | A rewrite rule that applies to some part of the goal           |
| `simp?`  | The minimal `simp only [...]` call that simplifies the goal    |

See `proof-style.md` under "Exploration tactics" for syntax details.

`exact?` and `apply?` are the workhorses: try them first on any goal you suspect Mathlib already covers. If the goal is too complex, narrow it with `show`, `have`, or `change` before searching (see "When search tactics fail" below).

### 3. Grep Mathlib source

When search tactics time out or return nothing, grep the local Mathlib installation directly:

```bash
cd <project's Mathlib package path>/Mathlib

# Search for a lemma by partial name
grep -rn "theorem.*sum_comm" Data/Finset/
grep -rn "lemma.*sum_comm" Data/Finset/

# Search for lemmas about a specific operation on a specific type
grep -rn "theorem.*Finset.*card.*filter" Data/Finset/
grep -rn "lemma.*Finset.*card.*filter" Data/Finset/

# Search for a specific statement pattern
grep -rn "Finset.sum.*Finset.sum" Data/Finset/
```

Mathlib uses both `theorem` and `lemma` keywords for provable declarations. Always search for both, or use a pattern that matches either (e.g., `\(theorem\|lemma\)`).

When grepping from the repository root, always exclude any vendored Lean dependencies the project's CLAUDE.md flags (e.g. third-party packages under `.lake/packages/` that are not Mathlib).

### 4. Browse the module hierarchy

When you know the general area but not the specific lemma, browse the relevant module. The module hierarchy map below shows where to look. Open the file in an editor and scan the declaration names; Mathlib files are organized so that related lemmas cluster together.

### 5. Check the Mathlib documentation site

For broader exploration or when local search fails, the online documentation at `https://leanprover-community.github.io/mathlib4_docs/` has full-text search and cross-referenced declarations.

## Module Hierarchy Map

This map covers Mathlib areas commonly depended on by theorem-proving projects. Each entry lists the most relevant files and what they provide. Adjust the map to the Mathlib areas your project actually imports.

### Finite sets and combinatorics

The `Finset` family is the most heavily used part of Mathlib in this project.

| Module path                                 | Provides                                                     |
| ------------------------------------------- | ------------------------------------------------------------ |
| `Mathlib.Data.Finset.Basic`                 | Core `Finset` type, membership, `∅`, `insert`, `∪`, `∩`      |
| `Mathlib.Data.Finset.Card`                  | `Finset.card`, cardinality lemmas                            |
| `Mathlib.Data.Finset.Image`                 | `Finset.image`, `Finset.map`                                 |
| `Mathlib.Data.Finset.Filter`                | `Finset.filter`, membership and cardinality of filtered sets |
| `Mathlib.Data.Finset.Sum`                   | Disjoint union of finsets                                    |
| `Mathlib.Data.Finset.Lattice`               | `Finset.sup`, `Finset.inf`, lattice operations on finsets    |
| `Mathlib.Data.Finset.Prod`                  | `Finset.product`, cartesian product                          |
| `Mathlib.Data.Finset.Sort`                  | Sorted lists from finsets                                    |
| `Mathlib.Algebra.BigOperators.Group.Finset` | `Finset.sum`, `Finset.prod`, `∑` and `∏` notation            |

`Finset.sum` and `Finset.prod` live in `Algebra.BigOperators`, not in `Data.Finset`. This is the single most common source of confusion when searching for sum-related lemmas.

### Finite types and cardinality

| Module path                    | Provides                                         |
| ------------------------------ | ------------------------------------------------ |
| `Mathlib.Data.Fin.Basic`       | `Fin n`, coercions, arithmetic, ordering         |
| `Mathlib.Data.Fin.VecNotation` | `![a, b, c]` notation for `Fin n -> α`           |
| `Mathlib.Data.Fin.Tuple.Sort`  | Sorting operations on `Fin`-indexed tuples       |
| `Mathlib.Data.Fintype.Basic`   | `Fintype` class, `Fintype.card`, `Finset.univ`   |
| `Mathlib.Data.Fintype.Card`    | Cardinality lemmas for composite finite types    |
| `Mathlib.Data.Fintype.Pi`      | `Fintype` instances for dependent function types |
| `Mathlib.Data.Fintype.Prod`    | `Fintype` instances for product types            |

`Finset.univ` (the finset of all elements of a `Fintype`) is defined in `Fintype.Basic`, not in `Finset.Basic`. Another common source of confusion.

### Number types

| Module path                  | Provides                                     |
| ---------------------------- | -------------------------------------------- |
| `Mathlib.Data.Real.Basic`    | `Real` (ℝ), field operations, ordering       |
| `Mathlib.Data.PNat.Basic`    | `PNat` (ℕ+), positive natural numbers        |
| `Mathlib.Data.ENat.Basic`    | `ENat` (ℕ∞), extended naturals with infinity |
| `Mathlib.Data.NNReal.Basic`  | `NNReal` (ℝ≥0), nonnegative reals            |
| `Mathlib.Data.ENNReal.Basic` | `ENNReal` (ℝ≥0∞), extended nonnegative reals |

### Algebraic structures and big operators

| Module path                                  | Provides                                             |
| -------------------------------------------- | ---------------------------------------------------- |
| `Mathlib.Algebra.BigOperators.Group.Finset`  | `∑` and `∏` over `Finset`, core sum/prod lemmas      |
| `Mathlib.Algebra.BigOperators.Order`         | Ordered sums: `sum_le_sum`, `sum_nonneg`, etc.       |
| `Mathlib.Algebra.Order.Field.Basic`          | Ordered field lemmas (division, reciprocal ordering) |
| `Mathlib.Algebra.Order.AbsoluteValue`        | Absolute value on ordered rings                      |
| `Mathlib.Algebra.GroupWithZero.Units.Lemmas` | Division and inverse in groups with zero             |

### Order and lattice theory

| Module path                     | Provides                                                          |
| ------------------------------- | ----------------------------------------------------------------- |
| `Mathlib.Order.Basic`           | `LE`, `LT`, `Preorder`, `PartialOrder`                            |
| `Mathlib.Order.Lattice`         | `Sup`, `Inf`, `Lattice`                                           |
| `Mathlib.Order.Filter.Basic`    | Filters (used in limit definitions, not in this project directly) |
| `Mathlib.Order.CompleteLattice` | `iSup`, `iInf` for indexed suprema/infima                         |

### Analysis and inequalities

| Module path                                   | Provides                                     |
| --------------------------------------------- | -------------------------------------------- |
| `Mathlib.Analysis.MeanInequalities`           | Jensen's inequality, power mean inequalities |
| `Mathlib.Analysis.SpecialFunctions.Log.Basic` | `Real.log`, logarithm identities             |

### Tactics

| Module path      | Provides                                                                                                                                                                 |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Mathlib.Tactic` | Kitchen-sink import: `simp`, `ring`, `linarith`, `omega`, `positivity`, `norm_num`, `field_simp`, `gcongr`, `ext`, `push_neg`, `contrapose`, and all exploration tactics |

Importing `Mathlib.Tactic` is convenient but heavy. For production code, prefer importing only the specific tactic modules you need.

## Common Lookup Patterns

Quick reference for frequently needed lemma families, organized by proof goal.

### Finset sums

| You need to...                         | Look for                                                                               |
| -------------------------------------- | -------------------------------------------------------------------------------------- |
| Rewrite a sum by rewriting each term   | `Finset.sum_congr` (needs proof that the index set is equal and terms agree pointwise) |
| Swap the order of a double sum         | `Finset.sum_comm`                                                                      |
| Split a sum over a union               | `Finset.sum_union` (requires disjointness)                                             |
| Split a sum into filter and complement | `Finset.sum_filter_add_sum_filter_not`                                                 |
| Factor a constant out of a sum         | `Finset.mul_sum`, `Finset.sum_mul`                                                     |
| Bound a sum by bounding each term      | `Finset.sum_le_sum` (needs pointwise `≤`)                                              |
| Bound a single term by the whole sum   | `Finset.single_le_sum` (needs each term `≥ 0`)                                         |
| Show a sum of nonneg terms is nonneg   | `Finset.sum_nonneg`                                                                    |
| Telescope a sum                        | `Finset.sum_range_succ`, `Finset.sum_Ico_eq_sum_range`                                 |
| Sum over the empty set                 | `Finset.sum_empty`                                                                     |
| Sum over a singleton                   | `Finset.sum_singleton`                                                                 |

### Finset membership and filtering

| You need to...                       | Look for                          |
| ------------------------------------ | --------------------------------- |
| Unfold membership in a filtered set  | `Finset.mem_filter`               |
| Unfold membership in an intersection | `Finset.mem_inter`                |
| Unfold membership in a union         | `Finset.mem_union`                |
| Unfold membership in a singleton     | `Finset.mem_singleton`            |
| Unfold membership in an image        | `Finset.mem_image`                |
| Unfold membership in `Finset.univ`   | `Finset.mem_univ` (always `True`) |
| Show two filters are equal           | `Finset.filter_congr`             |
| Compose two filters                  | `Finset.filter_filter`            |

### Finset cardinality

| You need to...                              | Look for                                                   |
| ------------------------------------------- | ---------------------------------------------------------- |
| Card of a filtered set                      | `Finset.card_filter_le`                                    |
| Card of a union                             | `Finset.card_union_le`, `Finset.card_union_add_card_inter` |
| Card of an image (injective function)       | `Finset.card_image_of_injective`                           |
| Card of `Finset.univ` equals `Fintype.card` | `Finset.card_univ`                                         |
| Card of the empty set                       | `Finset.card_empty`                                        |
| Card of a singleton                         | `Finset.card_singleton`                                    |

### Fin and coercions

| You need to...                                  | Look for                                |
| ----------------------------------------------- | --------------------------------------- |
| Extract the `Nat` value from `Fin n`            | `Fin.val` (the coercion `↑i` uses this) |
| Prove `(i : Fin n).val < n`                     | `Fin.isLt`, `i.isLt`                    |
| Cast between `Fin n` and `Fin m`                | `Fin.cast`, `Fin.castLE`                |
| Construct a `Fin (n+1)` from `Fin n`            | `Fin.castSucc`, `Fin.succ`              |
| The last element of `Fin (n+1)`                 | `Fin.last`                              |
| Extensionality: two `Fin` values equal iff vals | `Fin.ext`, `Fin.ext_iff`                |

### Real-number arithmetic

| You need to...                  | Look for                                       |
| ------------------------------- | ---------------------------------------------- |
| Show something is positive      | `positivity` tactic (handles most cases)       |
| Show something is nonneg        | `positivity`, or `le_of_lt` after `positivity` |
| Clear denominators              | `field_simp` tactic                            |
| Normalize polynomial expression | `ring` tactic                                  |
| Linear inequality               | `linarith` tactic                              |
| Nonlinear inequality            | `nlinarith` tactic                             |
| Multiply both sides by positive | `mul_lt_mul_of_pos_right` and variants         |
| Divide both sides               | `div_le_div_of_nonneg_right` and variants      |

### Logarithms

| You need to...                          | Look for          |
| --------------------------------------- | ----------------- |
| `log(a * b) = log(a) + log(b)`          | `Real.log_mul`    |
| `log(a / b) = log(a) - log(b)`          | `Real.log_div`    |
| `log(a ^ n) = n * log(a)`               | `Real.log_pow`    |
| `log(1) = 0`                            | `Real.log_one`    |
| `log` is monotone                       | `Real.log_le_log` |
| `log` is strictly monotone on positives | `Real.log_lt_log` |

### Division and reciprocals

| You need to...                               | Look for                           |
| -------------------------------------------- | ---------------------------------- |
| `a / b * b = a` (when `b ≠ 0`)               | `div_mul_cancel₀`                  |
| `a * (b / a) = b`                            | `mul_div_cancel₀`                  |
| `1 / a = a⁻¹`                                | `one_div`                          |
| `(a / b) / c = a / (b * c)`                  | `div_div`                          |
| Ordering: `a / b ≤ c / d` from cross-product | `div_le_div_iff` (needs pos denom) |

## Reading Mathlib Source

When you find a Mathlib file that looks relevant, these patterns help you read it efficiently.

**Follow the import chain.** A file's imports tell you what vocabulary is available. If a lemma mentions `Finset.sum` but the file does not import `BigOperators`, the sum API came in transitively through another import. Use `#check` or `#print` to confirm availability.

**Find where instances come from.** When the elaborator says "failed to synthesize instance," grep for the instance declaration:

```bash
grep -rn "instance.*:.*Fintype.*Fin" <Mathlib package path>/Mathlib/Data/
grep -rn "instance.*:.*DecidableEq.*Fin" <Mathlib package path>/Mathlib/Data/
```

**Read `@[simp]` and `@[ext]` annotations.** Lemmas tagged `@[simp]` are applied automatically by `simp`. If your goal should simplify but does not, check whether the relevant simp lemma exists and is tagged. Lemmas tagged `@[ext]` enable the `ext` tactic for that type.

**Understand `noncomputable`.** Many Mathlib definitions involving `Real` or classical choice are marked `noncomputable`. This is normal and does not affect proof correctness. It means the definition cannot be evaluated with `#eval` but can still be used in proofs. If you see `noncomputable` on your own definition, it usually means a dependency is noncomputable, which is fine for this project's theorem-proving use case.

**Check `@[deprecated]` aliases.** When a lemma has been renamed, Mathlib provides a deprecated alias pointing from the old name to the new one. If `#check oldName` produces a deprecation warning, use the new name it suggests.

## When Search Tactics Fail

### `exact?` or `apply?` times out

The search space is too large. Narrow the goal before retrying:

```lean
-- Before: complex goal, exact? times out
example (s : Finset ℕ) (f g : ℕ → ℝ) (h : ∀ x ∈ s, f x = g x) :
    ∑ x ∈ s, f x = ∑ x ∈ s, g x := by
  exact?  -- times out

-- After: use `show` or `suffices` to focus the search
example (s : Finset ℕ) (f g : ℕ → ℝ) (h : ∀ x ∈ s, f x = g x) :
    ∑ x ∈ s, f x = ∑ x ∈ s, g x := by
  apply Finset.sum_congr rfl
  exact h
```

You can also increase the heartbeat limit locally:

```lean
set_option maxHeartbeats 400000 in
example : ... := by exact?
```

But this is a last resort. Narrowing the goal is almost always better.

### `exact?` returns nothing

Several possible causes:

1. **Missing instances.** The lemma you need may require a type class instance that is not in scope. Check whether the relevant `variable` or `open` declarations are present.

2. **Missing imports.** The lemma exists but its module is not imported. Check the module hierarchy map above and add the import.

3. **Wrong form.** The goal may need massaging before a lemma applies. Try `simp` to normalize, or `rw` to put the goal into a standard form.

4. **The lemma genuinely does not exist.** After exhausting other options, this is a legitimate conclusion. Write the lemma yourself and consider whether it belongs in the project's local library.

### `#check` fails on a name you expected to exist

1. **Try `#check @theName`.** The `@` form shows all implicit arguments and sometimes resolves ambiguity.

2. **The lemma was renamed.** Search for `deprecated.*oldName` or `alias.*oldName` in Mathlib source.

3. **The lemma is in a namespace you have not opened.** Try `#check Namespace.theName` with the full qualified name.

4. **Universe mismatch.** The lemma may be universe-polymorphic in a way that does not match your context. Check whether `Type*` vs `Type u` is an issue.
