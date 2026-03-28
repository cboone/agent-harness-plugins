# CI Workflow Template (macOS-only)

Create `.github/workflows/ci.yml` with the following content.

Use this template when the project depends on macOS system frameworks (Security.framework, AppKit, CoreFoundation, etc.) and cannot build or test on Linux.

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
    runs-on: macos-latest
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
    runs-on: macos-latest
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
    runs-on: macos-latest
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
    runs-on: macos-latest
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
    runs-on: macos-latest
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
    runs-on: macos-latest
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
    runs-on: macos-latest
    timeout-minutes: 5
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Check for typos
        uses: crate-ci/typos@v1
```

## Notes

- Identical to the cross-platform CI template except all jobs use `runs-on: macos-latest`.
- macOS runners are more expensive than Ubuntu runners. Only use this template when the project cannot build or test on Linux.
- Indicators that a project is macOS-only:
  - `Cargo.toml` contains `[target.'cfg(target_os = "macos")']` dependencies
  - Source code imports `security_framework`, `core_foundation`, `cocoa`, `objc`, or similar crates
  - The project only compiles on macOS (no `cfg` gates for other platforms)
