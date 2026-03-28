# CI Workflow Template (Cross-Platform)

Create `.github/workflows/ci.yml` with the following content.

Use this template when the project builds and tests on Linux (the default). For macOS-only projects, use the macOS-only variant instead.

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

- 7 parallel jobs. All run on `ubuntu-latest`.
- `cargo nextest run` replaces `cargo test` for faster parallel test execution.
- The deny and audit jobs do not need Rust cache since they install standalone binaries.
- The typos job does not need a Rust toolchain; the action bundles its own binary.
- **Action pinning**: All actions use upstream-maintained tags rather than commit SHAs. Generated workflows should keep these references as shown.
