# CI Workflow Template

Create `.github/workflows/ci.yml` with the following content.

No replacements needed (the workflow is project-name-independent).

Uses the `cboone/gh-actions` reusable workflow, which creates parallel jobs for test, format check, build, and cross-compilation internally.

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
    uses: cboone/gh-actions/.github/workflows/run-zig-ci.yml@17f94b08428565213e70ae19c37a7be894a172d2 # v3.1.1
    with:
      zig-version-file: build.zig.zon
      run-cross-compile: true
```

## Notes

- `zig-version-file: build.zig.zon` makes the wrapped `mlugg/setup-zig` action read `minimum_zig_version` from `build.zig.zon`, so the project's Zig version is the single source of truth. Never restate the version in this file.
- `zig-version-file` is an input of the reusable workflow, not of `mlugg/setup-zig`. The action itself has no such input, so passing `version-file:` to it directly is ignored with a warning rather than honored.
- The reusable workflow creates parallel jobs internally for test, format check (`zig fmt --check`), build, and cross-compilation.
- All checks are enabled by default except cross-compilation. `run-cross-compile: true` validates the release targets on every PR, which is cheap with Zig (single runner, no extra toolchains) and catches the platform-specific compile errors that only appear off the host target.
- To disable a specific check, set its input to `false` (e.g., `run-test: false`, `run-fmt: false`, `run-build: false`).
- Optional inputs include `cross-targets` (space-separated target triples, defaults to linux/macOS/Windows), `run-scrut` for CLI snapshot testing, and `scrut-build-cmd`/`scrut-env`/`scrut-test-dir` for scrut configuration. The add-scrut-cli-tests skill wires those up.
- The workflow's format job runs `zig fmt --check src/ build.zig`, which does not cover `build.zig.zon`. The Makefile's `fmt` target does, so run `make check` locally rather than relying on CI to catch an unformatted manifest.
- Refresh the pinned SHA and its `# vX.Y.Z` comment before emitting this file; see the SHA refresh section in the skill body.
