# Dependency Blocks

Use exactly one dependency block in `lakefile.toml`.

## Mathlib

Replace `DEPENDENCY-REF` with the explicit or derived Mathlib ref.

```toml
[[require]]
name = "mathlib"
scope = "leanprover-community"
rev = "DEPENDENCY-REF"
```

## PFR

Replace `DEPENDENCY-REF` with the explicit `teorth/pfr` ref supplied by the user.

```toml
[[require]]
name = "PFR"
git = "https://github.com/teorth/pfr.git"
rev = "DEPENDENCY-REF"
```

## Import Selection

Use the matching import in `LEAN-NAMESPACE/Prelude.lean`.

| Dependency family | `DEPENDENCY-IMPORT`            |
| ----------------- | ------------------------------ |
| `Mathlib`         | `Mathlib`                      |
| `PFR`             | `PFR.ForMathlib.Entropy.Basic` |
