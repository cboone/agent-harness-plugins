# Rust

## Tools

- **clippy**: The official Rust linter. Ships with rustup, no separate install needed.
- **rustfmt**: The official Rust formatter. Ships with rustup, no separate install needed.
- **cargo-deny**: Checks dependency licenses, bans, advisories, and sources. Standard in the Rust ecosystem for supply chain auditing.
- **typos**: Fast source code spell checker written in Rust. Widely used in the Rust ecosystem as an alternative to cspell.

## Install

Both clippy and rustfmt are included with the Rust toolchain. Verify availability:

```bash
rustup component add clippy
rustup component add rustfmt
```

### cargo-deny

```bash
cargo install --locked --version 0.19.4 cargo-deny
```

Or install via `taiki-e/install-action@cargo-deny` in CI.

### typos

```bash
cargo install --locked --version 1.45.2 typos-cli
```

Or use the `crate-ci/typos@v1` GitHub Action in CI.

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

### deny.toml

Create `deny.toml` in the project root:

```toml
[advisories]
vulnerability = "deny"
unmaintained = "warn"

[licenses]
unlicensed = "deny"
allow = [
  "MIT",
  "Apache-2.0",
  "BSD-2-Clause",
  "BSD-3-Clause",
  "ISC",
  "Unicode-3.0",
]

[bans]
multiple-versions = "warn"
wildcards = "allow"

[sources]
unknown-registry = "deny"
unknown-git = "deny"
```

The license allowlist covers the vast majority of Rust ecosystem crates. Add additional licenses as needed for your project's dependencies.

### typos.toml (optional)

Create `typos.toml` in the project root if custom exclusions are needed:

```toml
[default.extend-words]
# Add project-specific words that are not typos

[files]
extend-exclude = ["CHANGELOG.md"]
```

## Commands

```bash
# Lint with clippy (deny all warnings)
cargo clippy -- -D warnings

# Check formatting (CI mode, no changes)
cargo fmt -- --check

# Format code (apply changes)
cargo fmt

# Check dependency licenses, advisories, and bans
cargo deny check

# Check for typos in source code and docs
typos
```

## Makefile Targets

```makefile
.PHONY: lint fmt deny typos

lint: ## Run clippy
	cargo clippy -- -D warnings

fmt: ## Format Rust code
	cargo fmt

deny: ## Check dependencies with cargo-deny
	cargo deny check

typos: ## Check for typos
	typos
```

## Notes

- `cargo clippy -- -D warnings` treats all warnings as errors, which is the recommended CI setting.
- `rustfmt.toml` applies to the entire workspace. No per-crate config is needed.
- Both clippy and rustfmt respect `Cargo.toml` edition settings automatically.
- `clippy.toml` is rarely needed. Only create it if default thresholds are too restrictive.
- `cargo deny check` runs all checks (advisories, licenses, bans, sources) by default. The `deny.toml` config file controls severity.
- `cargo-deny` is especially valuable for projects that will be published or used in compliance-sensitive environments.
- `typos` is fast enough to run on every save. It checks all files in the project unless excluded in `typos.toml`.
- `CHANGELOG.md` is excluded from typos checking by default because it commonly contains names and version strings that trigger false positives.
