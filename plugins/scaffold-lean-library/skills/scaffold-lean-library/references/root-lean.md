# Main Entrypoint Template

Use this template for `LEAN-NAMESPACE.lean`.

```lean
/-
Copyright (c) YEAR COPYRIGHT-HOLDER. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: COPYRIGHT-HOLDER
-/

import LEAN-NAMESPACE.Prelude
```

## Notes

- This file is an explicit entrypoint manifest. Add each public module import here when new modules are created.
- Do not remove imports from this manifest merely because they are transitively imported elsewhere.
