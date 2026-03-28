# Rust CI Workflow

Use this template for Rust projects.

7 parallel jobs: test, lint, format, build, deny, audit, typos.

```yaml
name: CI

on:
  push:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"
  pull_request:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Rust
        uses: dtolnay/rust-toolchain@stable

      - name: Cache dependencies
        uses: Swatinem/rust-cache@v2

      - name: Install nextest
        uses: taiki-e/install-action@nextest

      - name: Run tests
        run: cargo nextest run

  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy

      - name: Cache dependencies
        uses: Swatinem/rust-cache@v2

      - name: Run clippy
        run: cargo clippy -- -D warnings

  format:
    name: Format
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt

      - name: Check formatting
        run: cargo fmt -- --check

  build:
    name: Build
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Rust
        uses: dtolnay/rust-toolchain@stable

      - name: Cache dependencies
        uses: Swatinem/rust-cache@v2

      - name: Build
        run: cargo build

  deny:
    name: Deny
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Install cargo-deny
        uses: taiki-e/install-action@cargo-deny

      - name: Run cargo deny
        run: cargo deny check

  audit:
    name: Audit
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Install cargo-audit
        uses: taiki-e/install-action@cargo-audit

      - name: Run cargo audit
        run: cargo audit

  typos:
    name: Typos
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Check for typos
        uses: crate-ci/typos@v1
```

## Notes

- Uses `dtolnay/rust-toolchain@stable` for toolchain setup
- `Swatinem/rust-cache@v2` caches Cargo dependencies and build artifacts
- Clippy runs with `-D warnings` to fail on any warning
- The format job uses `cargo fmt -- --check` (check mode, no modifications)
- `cargo nextest run` replaces `cargo test` for faster parallel test execution with better output. Installed via `taiki-e/install-action@nextest`.
- `cargo-deny` checks dependency licenses, bans, advisories, and sources against a `deny.toml` config. The deny and audit jobs do not need Rust cache since they install standalone binaries.
- `cargo-audit` scans the RustSec advisory database for known vulnerabilities in dependencies.
- `typos` catches spelling mistakes in source code and documentation. The job does not need a Rust toolchain since the action bundles the binary.
- **Action pinning**: `dtolnay/rust-toolchain@stable`, `Swatinem/rust-cache@v2`, `taiki-e/install-action@nextest`, `taiki-e/install-action@cargo-deny`, `taiki-e/install-action@cargo-audit`, and `crate-ci/typos@v1` follow this project's convention of pinning third-party actions to upstream-maintained tags and branch references rather than commit SHAs. Generated workflows should keep these references as shown.

## macOS-Only Projects

For projects that depend on macOS system frameworks (Security.framework, AppKit, CoreFoundation, etc.), swap all `runs-on: ubuntu-latest` to `runs-on: macos-latest`. Indicators that a project is macOS-only:

- `Cargo.toml` contains `[target.'cfg(target_os = "macos")']` dependencies
- Source code imports `security_framework`, `core_foundation`, `cocoa`, `objc`, or similar crates
- The project only compiles on macOS (no `cfg` gates for other platforms)

macOS runners are more expensive. Only use them when the project cannot build or test on Linux.
