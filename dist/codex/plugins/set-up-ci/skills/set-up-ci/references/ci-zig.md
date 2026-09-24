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
    uses: cboone/gh-actions/.github/workflows/run-zig-ci.yml@bbe15187a1a8c60caded9295d1d2d90338a0bb93 # v4.1.0
    with:
      zig-version-file: build.zig.zon
      run-cross-compile: true
```

## Notes

- `zig-version-file: build.zig.zon` makes the wrapped `mlugg/setup-zig` action read `minimum_zig_version` from `build.zig.zon`, so the project's Zig version is the single source of truth.
- The reusable workflow creates parallel jobs internally for test, format check (`zig fmt --check`), build, and cross-compilation
- The format job checks `build.zig`, `build.zig.zon` and `src` by default, so an unformatted or missing manifest fails it. Run `zig fmt build.zig.zon`, or set `fmt-paths` to the paths this project's layout uses.
- All checks are enabled by default except cross-compilation. Set `run-cross-compile: true` to validate release targets on every PR. Cross-compilation is cheap with Zig (single runner, no extra toolchains).
- To disable a specific check, set its input to `false` (e.g., `run-test: false`, `run-fmt: false`, `run-build: false`)
- The reusable workflow handles Zig toolchain setup internally
- Optional inputs include `cross-targets` (space-separated target triples, defaults to linux/macOS/Windows), `run-scrut` for CLI snapshot testing, and `scrut-build-cmd`/`scrut-env`/`scrut-test-dir` for scrut configuration
