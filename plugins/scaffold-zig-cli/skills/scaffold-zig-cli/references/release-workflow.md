# Release Workflow Template

Create `.github/workflows/release.yml` with the following content.

Replace `PROJECT-NAME` with the project name.

Uses the `cboone/gh-actions` reusable workflow, which handles Zig setup, cross-compilation, archive packaging, checksum generation, and GitHub release creation internally.

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: false

permissions:
  contents: write

jobs:
  release:
    uses: cboone/gh-actions/.github/workflows/release-zig-binaries.yml@17f94b08428565213e70ae19c37a7be894a172d2 # v3.1.1
    with:
      binary-name: PROJECT-NAME
      zig-version-file: build.zig.zon
```

## Notes

- The `binary-name` input is required. Set it to the binary name from `build.zig`'s `b.addExecutable(.{ .name = ... })`, which is the kebab-case project name rather than the underscored package name in `build.zig.zon`.
- `zig-version-file: build.zig.zon` keeps the release toolchain on the same pin as CI and the developer's machine. Without it the workflow falls back to whatever the action resolves on its own.
- The reusable workflow builds 5 targets by default: Linux (x86_64, aarch64), macOS (x86_64, aarch64), and Windows (x86_64). All of them build on a single `ubuntu-latest` runner: Zig cross-compiles without extra toolchains, so there is no macOS runner in the bill.
- Windows produces a `.zip` archive; every other target produces a `.tar.gz`. SHA-256 checksums are generated for all of them.
- Optional inputs include `targets` (space-separated Zig target triples to override the defaults), `optimize` (default: `ReleaseSafe`), `runs-on`, and `timeout-minutes` (default: 30).
- Triggered by pushing tags matching `v*` (e.g., `git tag v0.1.0 && git push origin v0.1.0`).
- `cancel-in-progress: false` ensures releases are never cancelled mid-flight.
- Refresh the pinned SHA and its `# vX.Y.Z` comment before emitting this file; see the SHA refresh section in the skill body.
