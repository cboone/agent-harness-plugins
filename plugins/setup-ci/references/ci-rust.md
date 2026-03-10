# Rust CI Workflow

Use this template for Rust projects.

4 parallel jobs: test, lint, format, build.

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

      - name: Run tests
        run: cargo test

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
```

## Notes

- Uses `dtolnay/rust-toolchain@stable` for toolchain setup
- `Swatinem/rust-cache@v2` caches Cargo dependencies and build artifacts
- Clippy runs with `-D warnings` to fail on any warning
- The format job uses `cargo fmt -- --check` (check mode, no modifications)
- **Action pinning**: `dtolnay/rust-toolchain@stable` and `Swatinem/rust-cache@v2` follow this project's convention of pinning third-party actions to upstream-maintained tags and branch references rather than commit SHAs. Generated workflows should keep these references as shown.
