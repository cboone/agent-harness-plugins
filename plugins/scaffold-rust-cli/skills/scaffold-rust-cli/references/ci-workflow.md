# CI Workflow Template (Cross-Platform)

Create `.github/workflows/ci.yml` with the following content.

Uses the `cboone/gh-actions` reusable workflow, which creates parallel jobs for test (with nextest), lint (clippy), format check, deny, audit, and typos internally.

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
  ci:
    uses: cboone/gh-actions/.github/workflows/rust-ci.yml@v2
```

## Notes

- The reusable workflow creates parallel jobs internally for test (with nextest), lint (clippy with `-D warnings`), format check (rustfmt), deny, audit, and typos
- All checks are enabled by default with no `with:` inputs needed
- There is no separate build job because `cargo nextest run` compiles the project as part of testing
- The reusable workflow handles Rust toolchain setup, dependency caching, and tool installation internally
