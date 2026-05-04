# Test Prelude Template

Use this template for `LEAN-TEST-NAMESPACE/Prelude.lean`.

```lean
/-
Copyright (c) YEAR COPYRIGHT-HOLDER. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: COPYRIGHT-HOLDER
-/

import LEAN-NAMESPACE

/-!
# LEAN-TEST-NAMESPACE Prelude

Compile-time API regression tests for the public `LEAN-NAMESPACE` entrypoint.

## Main statements

- This module verifies that the public entrypoint imports and composes.

## Tags

tests, api
-/

namespace LEAN-TEST-NAMESPACE

open LEAN-NAMESPACE

example : True := by
  trivial

end LEAN-TEST-NAMESPACE
```

## Notes

- Test modules should import the public surface they exercise. Do not reach into internal helpers.
- Each public module under `LEAN-NAMESPACE/` should gain a matching compile-time test module under `LEAN-TEST-NAMESPACE/`.
