# CI Workflow Template (macOS-only)

Create `.github/workflows/ci.yml` with the following content.

Uses the `cboone/gh-actions` reusable workflow with `runs-on: macos-latest` for projects that depend on macOS system frameworks (Security.framework, AppKit, CoreFoundation, etc.) and cannot build or test on Linux.

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
    with:
      runs-on: macos-latest
```

## Notes

- Identical to the cross-platform CI template except `runs-on: macos-latest` is set to run all jobs on macOS runners.
- macOS runners are more expensive than Ubuntu runners. Only use this template when the project cannot build or test on Linux.
- Indicators that a project is macOS-only:
  - `Cargo.toml` contains `[target.'cfg(target_os = "macos")']` dependencies
  - Source code imports `security_framework`, `core_foundation`, `cocoa`, `objc`, or similar crates
  - The project only compiles on macOS (no `cfg` gates for other platforms)
