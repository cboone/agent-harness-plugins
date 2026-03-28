# Zig CI Workflow

Use this template for Zig projects.

5 parallel jobs: test, format, build, cross-compile, test-scrut (conditional).

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
  test:
    name: Test
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Zig
        uses: mlugg/setup-zig@v2

      - name: Run tests
        run: zig build test

  format:
    name: Format
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Zig
        uses: mlugg/setup-zig@v2

      - name: Check formatting
        run: zig fmt --check src/ build.zig

  build:
    name: Build
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Zig
        uses: mlugg/setup-zig@v2

      - name: Build
        run: zig build

  cross-compile:
    name: Cross-Compile
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Zig
        uses: mlugg/setup-zig@v2

      - name: Cross-compile all release targets
        run: |
          targets=(
            x86_64-linux
            aarch64-linux
            x86_64-macos
            aarch64-macos
            x86_64-windows
          )
          for target in "${targets[@]}"; do
            echo "Building for ${target}..."
            zig build -Dtarget="${target}" -Doptimize=ReleaseSafe
          done
```

## Notes

- Uses `mlugg/setup-zig@v2` for toolchain setup. The action reads the Zig version from `build.zig.zon` `minimum_zig_version` by default.
- No separate lint job: Zig has no Clippy equivalent. The format job (`zig fmt --check`) and the build job (compiler warnings) cover lint-like checks.
- The cross-compile job builds all 5 release targets on a single `ubuntu-latest` runner. Unlike Rust, Zig requires no extra toolchains or macOS runners for cross-compilation.
- If scrut tests exist (`tests/scrut/` directory), add a `test-scrut` job following the pattern in the scrut CLI tests reference.
- **Action pinning**: `mlugg/setup-zig@v2` follows this project's convention of pinning third-party actions to upstream-maintained tags rather than commit SHAs.
