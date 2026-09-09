# Proof Style

Guide to writing proofs in Lean 4, covering tactic mode, term mode, structured proofs, and automation.

## Table of Contents

- [Tactic mode vs term mode](#tactic-mode-vs-term-mode)
- [Tactic formatting](#tactic-formatting)
- [Structured proofs](#structured-proofs)
- [Exploration tactics](#exploration-tactics)
- [Terminal tactics and automation](#terminal-tactics-and-automation)
- [Proof organization](#proof-organization)
- [Common patterns](#common-patterns)

## Tactic Mode vs Term Mode

**Tactic mode** (`by` blocks) is preferred for most proofs, especially complex ones. It provides incremental feedback through the VS Code infoview and is easier to maintain.

**Term mode** (direct proof terms) is appropriate for:

- Simple proofs that are a single expression
- Proofs that are essentially function application
- Constructing data as proof (e.g., providing witnesses)

```lean
-- Tactic mode: preferred for complex proofs
theorem add_comm (m n : Nat) : m + n = n + m := by
  induction m with
  | zero => simp
  | succ k ih => simp [Nat.succ_add, ih]

-- Term mode: fine for simple proofs
theorem and_comm_simple (h : P ∧ Q) : Q ∧ P :=
  ⟨h.2, h.1⟩

-- Term mode: providing witnesses
theorem exists_even : ∃ n : Nat, n % 2 = 0 :=
  ⟨4, rfl⟩
```

## Tactic Formatting

**`by` placement**: at the end of the preceding line, with tactic block indented 2 spaces:

```lean
-- Good
theorem my_thm : P := by
  exact h

-- Bad: by on its own line
theorem my_thm : P :=
by
  exact h

-- Bad: everything on one line (unless very short)
theorem my_thm : P := by exact h  -- OK only for trivial single-tactic proofs
```

**Subgoal focusing** with `·`: indent 2 spaces from the tactic that created the subgoals.

```lean
theorem and_swap (h : P ∧ Q) : Q ∧ P := by
  constructor
  · exact h.2
  · exact h.1
```

**Multi-line tactics**: indent continuation lines 2 spaces from the tactic keyword.

```lean
theorem my_thm : Statement := by
  apply long_lemma_name
    argument1
    argument2
```

**Combinator style**: use `<;>` to apply a tactic to all goals, but only when all goals are genuinely similar.

```lean
-- Good: all goals solved by the same tactic
theorem my_thm : P ∧ P := by
  constructor <;> exact hp
```

## Structured Proofs

Use `have`, `suffices`, `calc`, and `show` to break complex proofs into readable steps.

### `have` for intermediate results

```lean
theorem my_thm (n : Nat) (h : n > 0) : n * 2 > 0 := by
  have h1 : n ≥ 1 := h
  have h2 : n * 2 ≥ 2 := by omega
  omega
```

### `suffices` for backward reasoning

```lean
theorem my_thm : P := by
  suffices h : Q by
    exact derive_P_from_Q h
  -- now prove Q
  sorry
```

### `calc` for chains of equalities or inequalities

Place `calc` at the end of the preceding line. Align relation symbols vertically:

```lean
theorem calc_example (a b c : Nat) : (a + b) + c = (c + b) + a := by
  calc (a + b) + c
      _ = a + (b + c) := by ring
      _ = a + (c + b) := by ring
      _ = (c + b) + a := by ring
```

See `style-and-formatting.md` for additional formatting rules on `calc` blocks.

### `show` for clarifying the current goal

```lean
theorem my_thm : P ∧ Q := by
  constructor
  · show P
    exact hp
  · show Q
    exact hq
```

## Exploration Tactics

When developing proofs interactively, these tactics help discover the right approach:

| Tactic   | Purpose                                      |
| -------- | -------------------------------------------- |
| `exact?` | Search for a term that closes the goal       |
| `apply?` | Search for a lemma whose conclusion matches  |
| `rw?`    | Search for a rewrite rule that applies       |
| `simp?`  | Run `simp` and report which lemmas were used |
| `decide` | Decide propositions with decidable instances |

**Important**: replace exploration tactics with their output before finalizing code, with one exception: **do not squeeze terminal `simp`**. A terminal `simp` that closes a goal should be left as `simp` or `simp [specific_lemmas]`. Only non-terminal `simp` (followed by more tactics) should become `simp only [...]`.

```lean
-- During development: non-terminal simp?
theorem my_thm : P := by
  simp?
  exact h

-- After development: replace non-terminal with specific output
theorem my_thm : P := by
  simp only [Nat.reduceAdd]
  exact h

-- Terminal simp: leave as-is (do NOT squeeze)
theorem my_thm : 2 + 3 = 5 := by simp
```

## Terminal Tactics and Automation

Prefer automation tactics that close goals completely:

| Tactic     | Domain                                      |
| ---------- | ------------------------------------------- |
| `simp`     | Simplification using lemma database         |
| `omega`    | Linear arithmetic over `Nat` and `Int`      |
| `decide`   | Decidable propositions (finite computation) |
| `norm_num` | Numerical normalization                     |
| `ring`     | Ring equalities                             |
| `linarith` | Linear arithmetic over ordered fields       |
| `aesop`    | Automated reasoning (broader search)        |
| `tauto`    | Propositional tautologies                   |
| `trivial`  | Simple goals (`rfl`, `assumption`, etc.)    |
| `exact`    | Provide the exact proof term                |

**`simp` best practices**:

- For non-terminal `simp` (followed by more tactics): prefer `simp only [lemma1, lemma2]` over bare `simp`; bare `simp` is fragile because the simp set changes over time
- For terminal `simp` (closes the goal): leave as `simp` or `simp [specific_lemmas]`; do not squeeze to `simp only [...]`
- Use `@[simp]` on lemmas that simplify toward a normal form (e.g., reducing `length (x :: xs)` to `1 + length xs`)
- Do not mark lemmas as `@[simp]` if they could loop or if the "simplified" form is not obviously simpler

**Pipe operators**: use `<|` and `|>` to minimize parentheses in tactic mode:

```lean
-- Good: pipe operator avoids nesting
exact h |>.symm

-- Less clear: nested parentheses
exact (h).symm
```

## Proof Organization

**When to split lemmas**: extract a separate lemma when:

- An intermediate result is reusable
- A proof exceeds ~30 tactic lines
- A `have` block is self-contained and non-trivial
- A declaration is over the heartbeat budget. Extraction redistributes work across per-declaration budgets; see `mathlib.md#heartbeats-and-build-performance` for the order-of-magnitude-effectiveness argument and specific thresholds.

**When extracting from inside a `classical`-prefixed proof**, add `classical` to each extracted sub-lemma unless every missing `DecidableEq` is already in the `variable` block or a section instance. The parent's `classical` does not propagate to extracted lemmas — they start with a fresh elaboration context. A common symptom is `failed to synthesize instance of type class DecidableEq (S₁ × S₃)` in an extracted reindex lemma whose main-proof twin worked without issue.

**When extracting from a proof that used local `set` abbreviations**, the sub-lemma can state its signature with the unfolded form. At the call site, the caller's `set pXZ := fun p => ...` still accepts the extracted fact through definitional equality: `pXZ (t.1, t.2.2.1)` and `(μ.map ⟨X, Z⟩).real {(t.1, t.2.2.1)}` are defeq via the `set`-local let-binding, so `have hEq := extracted_lemma ...` carries the ascription as the caller wrote it. This avoids having to parameterize the sub-lemma over the local abbreviation.

**Ordering**: place helper lemmas before the main theorem that uses them, or use `where` for small local helpers.

```lean
-- Helper before main theorem
private theorem helper_lemma : ... := by sorry

theorem main_theorem : ... := by
  exact helper_lemma ...

-- Or use where for small helpers
theorem main_theorem : ... := by
  exact aux
where
  aux : ... := by sorry
```

**`private` keyword**: use for lemmas that are implementation details and should not be accessed outside the file.

## Common Patterns

### Induction

```lean
-- Standard induction
theorem list_length_nonneg (l : List α) : 0 ≤ l.length := by
  induction l with
  | nil => simp
  | cons x xs ih => simp [ih]
```

### Cases

```lean
-- Pattern matching on hypotheses
theorem or_comm_proof (h : P ∨ Q) : Q ∨ P := by
  cases h with
  | inl hp => exact Or.inr hp
  | inr hq => exact Or.inl hq
```

### Rewriting

```lean
-- Rewriting with equations
theorem my_thm (h : a = b) (h2 : b = c) : a = c := by
  rw [h, h2]

-- Rewriting in a hypothesis
theorem my_thm (h : a = b) (h2 : a > 0) : b > 0 := by
  rw [h] at h2
  exact h2
```

### Reindexing `Finset` sums

Two near-identical lemmas trip up newcomers. Pick by what the bijection looks like:

- `Finset.sum_nbij'` takes **simple** functions `i : ι → κ` and `j : κ → ι`. The hypotheses verify that `i` maps `s` into `t` and `j` maps `t` into `s` plus mutual inverse laws _on those finsets_.
- `Finset.sum_bij'` takes **dependent** functions `i : ∀ a ∈ s, κ` and `j : ∀ a ∈ t, ι`. Use when the bijection needs the membership witness to type-check.

```lean
-- Correct: sum_nbij' with simple functions
(Finset.sum_nbij' embed extract
  (fun d _ => ...)  -- membership forward
  (fun t _ => ...)  -- membership backward
  (fun d _ => ...)  -- extract ∘ embed = id on s
  (fun t _ => ...)  -- embed ∘ extract = id on t
  (fun _ _ => ...)  -- f = g ∘ i (or rfl)
).symm

-- Wrong: wrapping `embed` in `fun d _ => embed d` for `sum_nbij'` causes a
-- universe unification failure. The `_` membership argument is NOT part of
-- the function signature for `sum_nbij'`; it is part of the membership
-- obligations instead.
```

If you need to unfold a filter-sum over `Finset.univ.filter (proj · = c)` into a direct sum over a complement type `δ`, supply `embed : δ → α` and `extract : α → δ` along with three inversion facts: `proj ∘ embed = const c`, `extract ∘ embed = id`, and `embed ∘ extract = id` on the fibre. `sum_nbij'` then closes the equality. This pattern generalizes cleanly to a helper lemma when you have many parallel applications.

### Working with existentials

```lean
-- Introducing existentials
theorem exists_example : ∃ n : Nat, n > 5 := by
  exact ⟨6, by omega⟩

-- Eliminating existentials
theorem from_exists (h : ∃ n : Nat, n > 5) : True := by
  obtain ⟨n, hn⟩ := h
  trivial
```
