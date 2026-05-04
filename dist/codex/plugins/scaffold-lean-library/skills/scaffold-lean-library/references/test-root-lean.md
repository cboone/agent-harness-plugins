# Test Entrypoint Template

Use this template for `LEAN-TEST-NAMESPACE.lean`.

```lean
/-
Copyright (c) YEAR COPYRIGHT-HOLDER. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: COPYRIGHT-HOLDER
-/

import LEAN-TEST-NAMESPACE.Prelude
```

## Notes

- This is the explicit entrypoint manifest for the compile-time API regression test library.
- Add each test module import here when matching public modules are added under `LEAN-NAMESPACE/`.
