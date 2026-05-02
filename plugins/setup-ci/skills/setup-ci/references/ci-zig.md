# Zig CI Workflow

Use this template for Zig projects. Uses the `cboone/gh-actions` reusable workflow, which creates parallel jobs for test, format check, build, and cross-compilation internally.

Zig has no separate linter tool. `zig fmt` is the formatter, and the compiler itself catches most lint-like issues. The cross-compile job validates all release targets on every PR, which is cheap with Zig (single runner, no extra toolchains).

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
    uses: cboone/gh-actions/.github/workflows/zig-ci.yml@7371f5d84ff9f0b0e38bfde10ab7a46ddb331e92 # v2.2.0
    with:
      zig-version-file: build.zig.zon
      run-cross-compile: true
```

## Notes

- `zig-version-file: build.zig.zon` makes the wrapped `mlugg/setup-zig` action read `minimum_zig_version` from `build.zig.zon`, so the project's Zig version is the single source of truth.
- The reusable workflow creates parallel jobs internally for test, format check (`zig fmt --check`), build, and cross-compilation
- All checks are enabled by default except cross-compilation. Set `run-cross-compile: true` to validate release targets on every PR. Cross-compilation is cheap with Zig (single runner, no extra toolchains).
- To disable a specific check, set its input to `false` (e.g., `run-test: false`, `run-fmt: false`, `run-build: false`)
- The reusable workflow handles Zig toolchain setup internally
- Optional inputs include `cross-targets` (space-separated target triples, defaults to linux/macOS/Windows), `run-scrut` for CLI snapshot testing, and `scrut-build-cmd`/`scrut-env`/`scrut-test-dir` for scrut configuration
