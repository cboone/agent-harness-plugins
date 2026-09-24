# CI Workflow Template

Create `.github/workflows/ci.yml` with the following content.

No replacements needed (the workflow is project-name-independent).

Uses the `cboone/gh-actions` reusable workflow, which creates parallel jobs for test, format check, build, and cross-compilation internally.

Zig has no separate linter tool. `zig fmt` is the formatter, and the compiler itself catches most lint-like issues. The cross-compile job validates all release targets on every PR, which Zig does on one runner with no extra toolchains.

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

- `zig-version-file: build.zig.zon` makes the wrapped `mlugg/setup-zig` action read `minimum_zig_version` from `build.zig.zon`, so the project's Zig version is the single source of truth. Never restate the version in this file.
- `zig-version-file` is an input of the reusable workflow, not of `mlugg/setup-zig`. The action itself has no such input, so passing `version-file:` to it directly is ignored with a warning rather than honored.
- The reusable workflow creates parallel jobs internally for test, format check (`zig fmt --check`), build, and cross-compilation.
- Test, format check and build are on by default. Cross-compilation and scrut are both off, and this template turns on the first of them: `run-cross-compile: true` validates the release targets on every PR, which Zig does on one runner with no extra toolchains, and catches the platform-specific compile errors that only appear off the host target. Scrut stays opt-in, per the note below.
- To disable a specific check, set its input to `false` (e.g., `run-test: false`, `run-fmt: false`, `run-build: false`).
- Optional inputs include `cross-targets` (space-separated target triples, defaults to linux/macOS/Windows), `run-scrut` for CLI snapshot testing, and `scrut-build-cmd`/`scrut-env`/`scrut-test-dir` for scrut configuration. Setting them is a manual step. The add-scrut-cli-tests skill edits **this file** but not this job: it adds a sibling `test-scrut` job that calls `run-scrut-tests.yml`, and leaves the `ci` job's inputs alone, so `run-scrut` here stays off. The result is one workflow with two jobs. Enabling `run-scrut` as well would run the snapshot tests twice, so pick one: the input reuses the Zig toolchain this job already installs, while the separate job installs scrut from a checksum manifest the reusable workflow maintains.
- The workflow's format job checks `build.zig`, `build.zig.zon` and `src` by default, so an unformatted or missing manifest fails CI. The Makefile's `fmt` target covers the same paths, so `make check` catches it locally first. Set `fmt-paths` if this project's layout differs.
- Refresh the pinned SHA and its `# vX.Y.Z` comment before emitting this file; see the SHA refresh section in the skill body.
