# Taplo

TOML formatter and linter. Useful for `pyproject.toml`, `Cargo.toml`, `taplo.toml`, and other TOML configuration files.

## When to Offer

When `*.toml` files are detected in the project (beyond `Cargo.toml`, which is covered by Rust tooling).

## Install

```bash
# Homebrew (recommended)
brew install taplo

# Cargo (alternative)
cargo install taplo-cli

# npm (alternative)
npm install -D @taplo/cli
```

## Config (optional)

Create `taplo.toml` in the project root if custom formatting is needed:

```toml
[formatting]
align_entries = false
array_trailing_comma = true
compact_arrays = false
compact_inline_tables = false
indent_string = "  "
reorder_keys = true
```

## Commands

```bash
# Format all TOML files
taplo format

# Check formatting (CI mode, no changes)
taplo check

# Lint (validate TOML syntax)
taplo lint
```

## Notes

- Taplo works out of the box with sensible defaults. The config file is optional.
- `taplo format` reformats TOML files in place. `taplo check` exits non-zero if files need formatting.
- `reorder_keys = true` sorts keys alphabetically within tables, which produces cleaner diffs.
- For Rust projects, Taplo formats `Cargo.toml` and `rustfmt.toml`. For Python projects, it formats `pyproject.toml`.
- Taplo supports schema validation for known TOML formats (e.g., `pyproject.toml`, `Cargo.toml`).
