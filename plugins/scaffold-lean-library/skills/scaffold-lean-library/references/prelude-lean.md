# Main Prelude Template

Use this template for `LEAN-NAMESPACE/Prelude.lean`.

```lean
/-
Copyright (c) YEAR COPYRIGHT-HOLDER. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: COPYRIGHT-HOLDER
-/

import DEPENDENCY-IMPORT

/-!
# LEAN-NAMESPACE Prelude

Shared imports and namespace setup for PROJECT-TITLE.

## Main definitions

This module intentionally contains no public definitions yet.

## Tags

prelude, imports
-/

namespace LEAN-NAMESPACE

end LEAN-NAMESPACE
```

## Notes

- For Mathlib projects, `DEPENDENCY-IMPORT` is `Mathlib`.
- For PFR projects, `DEPENDENCY-IMPORT` is `PFR.ForMathlib.Entropy.Basic`.
- Keep project-wide notation and shared imports modest. Move domain-specific material into focused modules as soon as it exists.
