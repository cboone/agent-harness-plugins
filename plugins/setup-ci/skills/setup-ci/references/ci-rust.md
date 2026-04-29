# Rust CI Workflow

Use this template for Rust projects. Uses the `cboone/gh-actions` reusable workflow, which creates parallel jobs for test (with nextest), lint (clippy), format check, deny, audit, and typos internally.

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
  ci:
    uses: cboone/gh-actions/.github/workflows/rust-ci.yml@f69487c36f4e217afe28ea631de39edf17d35238 # v2.1.4
```

## Notes

- The reusable workflow creates parallel jobs internally for test (with nextest), lint (clippy with `-D warnings`), format check (rustfmt), deny, audit, and typos
- All checks are enabled by default with no `with:` inputs needed. To disable a specific check, set its input to `false` (e.g., `run-deny: false`, `run-audit: false`, `run-typos: false`)
- There is no separate build job because `cargo nextest run` compiles the project as part of testing
- The reusable workflow handles Rust toolchain setup, dependency caching, and tool installation internally
- Optional inputs include `rust-version` (default: `stable`), `use-nextest` (default: `true`), `clippy-args`, `cargo-features`, and `coverage` (with Codecov integration)

## macOS-Only Projects

For projects that depend on macOS system frameworks (Security.framework, AppKit, CoreFoundation, etc.), add the `runs-on` input:

```yaml
jobs:
  ci:
    uses: cboone/gh-actions/.github/workflows/rust-ci.yml@f69487c36f4e217afe28ea631de39edf17d35238 # v2.1.4
    with:
      runs-on: macos-latest
```

Indicators that a project is macOS-only:

- `Cargo.toml` contains `[target.'cfg(target_os = "macos")']` dependencies
- Source code imports `security_framework`, `core_foundation`, `cocoa`, `objc`, or similar crates
- The project only compiles on macOS (no `cfg` gates for other platforms)

macOS runners are more expensive. Only use them when the project cannot build or test on Linux.
