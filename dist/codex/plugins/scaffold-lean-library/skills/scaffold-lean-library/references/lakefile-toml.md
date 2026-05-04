# lakefile.toml Template

Use this template for `lakefile.toml`.

```toml
name = "PROJECT-NAME"
version = "0.1.0"
defaultTargets = ["LEAN-NAMESPACE"]
lintDriver = "batteries/runLinter"
testDriver = "LEAN-TEST-NAMESPACE"

[leanOptions]
pp.unicode.fun = true
autoImplicit = false
relaxedAutoImplicit = false
weak.linter.mathlibStandardSet = true

DEPENDENCY-REQUIRE-BLOCK

[[lean_lib]]
name = "LEAN-NAMESPACE"

[[lean_lib]]
name = "LEAN-TEST-NAMESPACE"
```

## Notes

- `defaultTargets = ["LEAN-NAMESPACE"]` keeps `lake build` focused on the main library.
- `testDriver = "LEAN-TEST-NAMESPACE"` makes `lake test` build the compile-time API regression test library.
- `lintDriver = "batteries/runLinter"` makes `lake lint` a real linter run instead of a no-op.
- `autoImplicit = false` and `relaxedAutoImplicit = false` are intentional strict implicit settings.
- Do not add a Lean long-line limit. This project family lets editors handle visual wrapping.
