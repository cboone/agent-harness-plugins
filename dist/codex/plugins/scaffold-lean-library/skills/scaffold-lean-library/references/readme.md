# README Template

Use this template for `README.md`.

````markdown
# PROJECT-NAME

PROJECT-DESCRIPTION

## Requirements

- [Lean 4](https://lean-lang.org/) through [elan](https://github.com/leanprover/elan), using the toolchain in `lean-toolchain`
- Lake, provided by the Lean toolchain
- `make`
- `markdownlint-cli2` and `cspell` for local text linting

## Bootstrap

Run the bootstrap script before any direct Lean build in a fresh clone or worktree:

```bash
bin/bootstrap-worktree
```

The script runs `lake update`, downloads Mathlib prebuilt artifacts with `lake exe cache get`, verifies that the cache exists, and builds `LEAN-NAMESPACE`.

## Development

```bash
make help
```

Common targets:

- `make build`: build `LEAN-NAMESPACE`
- `make test`: build `LEAN-TEST-NAMESPACE`
- `make lean-lint`: run `lake lint`
- `make lint`: run Markdown and spelling checks
- `make check`: run the full local check

## Dependency

This project depends on `DEPENDENCY-FAMILY` at ref `DEPENDENCY-REF`.

## License

Apache-2.0. See [LICENSE](./LICENSE).
````

## Notes

- Keep the README concise. Add mathematical exposition to paper notes, roadmap documents, or module docstrings rather than bloating the project landing page.
- If paper-backed mode is enabled, add a short section linking to `references/`.
