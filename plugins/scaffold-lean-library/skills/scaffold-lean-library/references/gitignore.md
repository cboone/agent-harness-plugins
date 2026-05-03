# .gitignore Template

Use this template for `.gitignore`.

```gitignore
# Lake build output and dependency checkouts
.lake/

# Editor and OS metadata
.DS_Store
# .idea/
# .vscode/

# Local environment files
.env
.env.*
```

## Notes

- Do not ignore `lean-toolchain` or `lakefile.toml`.
- Commit `lake-manifest.json` after `lake update` when the project wants reproducible resolved dependency revisions.
