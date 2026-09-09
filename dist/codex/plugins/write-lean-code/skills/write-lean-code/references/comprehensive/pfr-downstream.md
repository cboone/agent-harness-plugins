# PFR Downstream Conventions

Conventions for Lean 4 projects that depend on the Polynomial Freiman-Ruzsa (PFR) formalization's entropy API (`H[·]`, `I[·:·]`, `I[·:·|·]`, `condMutualInfo_eq`, `mutualInfo_comm`, `condMutualInfo_comm`, and friends). PFR is one of the few projects with a mature Mathlib-adjacent Shannon-entropy surface, but its lemmas carry side conditions along three axes (discrete/countable codomain, measurable-singleton class, `FiniteRange` on the random variables) that can be discharged uniformly with a single specialization pattern. This file documents that pattern so each downstream project does not re-derive it.

## Table of Contents

- [Finite-alphabet specialization](#finite-alphabet-specialization)
- [`noncomputable def` + default measure via `volume_tac`](#noncomputable-def--default-measure-via-volume_tac)
- [Measurability hygiene](#measurability-hygiene)
- [Anonymous-constructor pair notation](#anonymous-constructor-pair-notation)
- [Notation deferral](#notation-deferral)

## Finite-Alphabet Specialization

When a downstream module works with random variables whose codomains are finite types, package the discrete/countable/singleton-measurable assumptions in a shared `variable` block at module scope. For four random variables `Z : Ω → S₁`, `U : Ω → S₂`, `X : Ω → S₃`, `Y : Ω → S₄`:

```lean
variable {Ω : Type*} [MeasurableSpace Ω]
variable {S₁ S₂ S₃ S₄ : Type*}
  [Fintype S₁] [Fintype S₂] [Fintype S₃] [Fintype S₄]
  [MeasurableSpace S₁] [MeasurableSpace S₂]
  [MeasurableSpace S₃] [MeasurableSpace S₄]
  [MeasurableSingletonClass S₁] [MeasurableSingletonClass S₂]
  [MeasurableSingletonClass S₃] [MeasurableSingletonClass S₄]
```

Why this bundle:

- **`Fintype`** gives the alphabet a finite list of elements, which is the assumption PFR actually wants at the semantic level ("Shannon entropy of a random variable with finite alphabet").
- **`MeasurableSpace`** is a prerequisite for any talk of measurable random variables at all.
- **`MeasurableSingletonClass`** makes the `{x}` sets measurable for each `x : Sᵢ`, which is what PFR's entropy-theoretic lemmas need when they enumerate over point-masses.
- **`FiniteRange`** of each random variable — which PFR lemmas require — comes for free via PFR's instance `{Ω G : Type*} (X : Ω → G) [Finite G] : FiniteRange X`. Because `Fintype Sᵢ` implies `Finite Sᵢ`, the `FiniteRange` obligations are discharged automatically; they never appear explicitly in lemma statements.

The bundle is honest about the assumption: downstream proofs are stating "this holds for finite-alphabet random variables," not "this holds for arbitrary random variables." That is the right default for non-Shannon information inequality work and for downstream theorems that mechanize finite-alphabet Shannon-theory results. When a theorem genuinely needs a weaker hypothesis (e.g. `Countable` + `MeasurableSingletonClass` but not `Fintype`), make that the exceptional case and state it locally rather than weakening the module default.

### Staging when the bundle is overkill

If some lemmas in the module are purely algebraic and need only `[MeasurableSpace Sᵢ]` (the definition itself, definitional-unfolding lemmas, symmetries that only use commutativity of `I[·:·]`), stage the `variable` block so the extra instances land inside a nested `section` rather than at the top of the file:

```lean
-- Outer variable block: just measurability
variable {Ω : Type*} [MeasurableSpace Ω]
variable {S₁ S₂ S₃ S₄ : Type*}
  [MeasurableSpace S₁] [MeasurableSpace S₂]
  [MeasurableSpace S₃] [MeasurableSpace S₄]

-- definition + purely algebraic lemmas go here

section FiniteAlphabet

variable [Fintype S₁] [Fintype S₂]
  [MeasurableSingletonClass S₁] [MeasurableSingletonClass S₂]

-- lemmas that use PFR's entropy-expansion or commutativity on the measured variables go here

section ConditioningFinite

variable [Fintype S₃] [Fintype S₄]
  [MeasurableSingletonClass S₃] [MeasurableSingletonClass S₄]

-- lemmas that also expand the conditioning variables go here

end ConditioningFinite

end FiniteAlphabet
```

That keeps the outer lemmas honest about what they actually need (many are `simp`-closable algebra that does not even touch the probability measure) while the heavy lemmas get the full PFR-compatible bundle.

## `noncomputable def` + Default Measure via `volume_tac`

PFR's `mutualInfo` and `condMutualInfo` are `noncomputable` and take a probability measure with a `volume_tac`-supplied default:

```lean
noncomputable def mutualInfo
    {Ω S T : Type*} [MeasurableSpace Ω] [MeasurableSpace S] [MeasurableSpace T]
    (X : Ω → S) (Y : Ω → T) (μ : Measure Ω := by volume_tac) : ℝ := ...
```

Mirror this shape in downstream definitions built on top of PFR's API:

```lean
noncomputable def delta
    (Z : Ω → S₁) (U : Ω → S₂) (X : Ω → S₃) (Y : Ω → S₄)
    (μ : Measure Ω := by volume_tac) : ℝ :=
  I[Z : U ; μ] - I[Z : U | X ; μ] - I[Z : U | Y ; μ]
```

Rationale:

- **`noncomputable`** is forced by the PFR API: `mutualInfo` and `condMutualInfo` are already `noncomputable`, so any definition that composes them is too. Marking the definition explicitly prevents surprising error messages about `noncomputable theory` at later use sites.
- **`(μ : Measure Ω := by volume_tac)`** lets callers omit the measure when `MeasureSpace Ω` is available (the measure defaults to `volume`). Matches the call convention in PFR's API and in Mathlib's `MeasureTheory` lemmas, so callers do not have to thread `μ` through every invocation.

## Measurability Hygiene

Keep finite-alphabet (`Fintype`, `MeasurableSpace`, `MeasurableSingletonClass`) assumptions in the shared `variable` block. Keep `Measurable` hypotheses on the random variables as **explicit function arguments** on the lemmas that need them, not in the `variable` block:

```lean
-- Good
lemma delta_comm_main
    {Z : Ω → S₁} {U : Ω → S₂} (hZ : Measurable Z) (hU : Measurable U)
    (X : Ω → S₃) (Y : Ω → S₄) (μ : Measure Ω) :
    delta Z U X Y μ = delta U Z X Y μ := by
  simp only [delta_def, mutualInfo_comm hZ hU μ,
             condMutualInfo_comm hZ hU _ μ]

-- Bad (hides which lemmas need measurability and which do not)
variable {Z : Ω → S₁} {U : Ω → S₂}
variable (hZ : Measurable Z) (hU : Measurable U)  -- don't
```

This matches PFR's style and makes signatures honest: callers see at a glance which random variables need measurability for which downstream lemma. Algebraic lemmas that only use commutativity of mutual information or pure arithmetic do not need `Measurable` arguments at all, and the signature reflects that. Bundling `Measurable` into the `variable` block would silently pay the cost at every call site, including ones that do not need it.

When a proof takes several measurability hypotheses, list them in the same order as the random variables themselves (`hZ : Measurable Z`, then `hU : Measurable U`, etc.) so the signature reads consistently.

## Anonymous-Constructor Pair Notation

PFR uses the anonymous-constructor syntax `⟨Z, U⟩` to denote the pair random variable `fun ω => (Z ω, U ω)`, relying on Lean's elaboration to resolve it against `Prod.mk` at the expected `Ω → S₁ × S₂` type:

```lean
-- Pair random variable: the product-valued function (Z, U)
I[X : ⟨Z, U⟩ ; μ]
```

Mirror this usage in downstream lemmas. The anonymous-constructor form reads closer to mathematical notation `(Z, U)` than the explicit `fun ω => (Z ω, U ω)` and keeps lemma statements compact. Fall back to `(fun ω => (Z ω, U ω))` only when Lean cannot elaborate `⟨Z, U⟩` — typically when the expected type is not concrete enough for the anonymous constructor to dispatch to `Prod.mk`.

## Notation Deferral

Defer custom notation (e.g. `Δ[Z : U | X, Y ; μ]` for the Zhang-Yeung delta) until the proofs that would benefit from it are complex enough to make plain function application unreadable. Early-stage modules with only a definition and a handful of definitional-unfolding or symmetry lemmas read perfectly well as `delta Z U X Y μ`; introducing notation before the proofs need it adds a layer of indirection reviewers and `exact?` users have to work around.

When notation is eventually introduced, state the decision in the module's "Notation" docstring section (required by the Mathlib module-docstring convention when any notation is introduced) and make sure it does not collide with anything in PFR's namespace. `Δ`-style Greek-letter notation is particularly safe because PFR uses `H`, `I`, and bracket forms rather than Greek letters for its own entropy functions.
