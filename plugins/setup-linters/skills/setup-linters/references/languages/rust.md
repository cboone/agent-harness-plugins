# Rust

## Tools

- **clippy**: The official Rust linter. Ships with rustup, no separate install needed.
- **rustfmt**: The official Rust formatter. Ships with rustup, no separate install needed.

## Install

Both tools are included with the Rust toolchain. Verify availability:

```bash
rustup component add clippy
rustup component add rustfmt
```

## Config

### rustfmt.toml

Create `rustfmt.toml` in the project root:

```toml
edition = "2024"
max_width = 100
use_small_heuristics = "Default"
```

### clippy.toml (optional)

Create `clippy.toml` in the project root if custom thresholds are needed:

```toml
too-many-arguments-threshold = 8
type-complexity-threshold = 350
```

## Commands

```bash
# Lint with clippy (deny all warnings)
cargo clippy -- -D warnings

# Check formatting (CI mode, no changes)
cargo fmt -- --check

# Format code (apply changes)
cargo fmt
```

## Makefile Targets

```makefile
.PHONY: lint fmt

lint: ## Run clippy
	cargo clippy -- -D warnings

fmt: ## Format Rust code
	cargo fmt
```

## Notes

- `cargo clippy -- -D warnings` treats all warnings as errors, which is the recommended CI setting.
- `rustfmt.toml` applies to the entire workspace. No per-crate config is needed.
- Both tools respect `Cargo.toml` edition settings automatically.
- `clippy.toml` is rarely needed. Only create it if default thresholds are too restrictive.
