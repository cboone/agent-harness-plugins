# Project Type Detection

Detect the project type to determine where version numbers live and how to update them. Check types in priority order: the first match wins.

## Detection Priority

1. Go CLI
1. Go library
1. Generic (fallback)

## Go CLI

**Detection:** `go.mod` exists AND at least one of:

- A `cmd/` directory exists
- `.goreleaser.yml` or `.goreleaser.yaml` exists

**Version files:** Search for `var version` or `const version` in `.go` files. Common locations:

- `main.go`
- `cmd/root.go`
- `internal/version/version.go`

**Note:** Many Go CLIs inject the version via ldflags at build time (`-X main.version=...`), so a version constant may not exist in source. In that case, the version comes solely from the git tag. Report this to the user and skip source file version updates.

## Go Library

**Detection:** `go.mod` exists WITHOUT main-package indicators (no `cmd/` directory, no `.goreleaser.yml`/`.goreleaser.yaml`, no `func main()` in root `.go` files).

**Version files:** Search for an exported `Version` constant (e.g., `const Version = "1.2.3"`). Many libraries rely solely on git tags for versioning; if no version constant is found, skip source file version updates and note this to the user.

## Generic (Fallback)

**Detection:** None of the above matched.

**Version files:** Check for these ecosystem files and their version keys:

| File | Version location |
| ---- | ---------------- |
| `package.json` | `"version": "X.Y.Z"` |
| `pyproject.toml` | `[project]` section, `version = "X.Y.Z"` |
| `Cargo.toml` | `[package]` section, `version = "X.Y.Z"` |
| `setup.py` | `version="X.Y.Z"` argument |
| `VERSION` or `VERSION.txt` | Plain text, entire file content |
| `version.txt` | Plain text, entire file content |

If multiple files match, update all of them to keep versions consistent. If none match, skip source file version updates and rely solely on the git tag.
