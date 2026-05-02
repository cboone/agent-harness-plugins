# Release Workflow Template (Cross-Platform)

Create `.github/workflows/release.yml` with the following content.

Replace `PROJECT-NAME` with the project name.

Uses the `cboone/gh-actions` reusable workflow, which handles cross-compilation, artifact collection, checksum generation, and GitHub release creation internally.

Use this template when the project should produce release binaries for both Linux and macOS. For macOS-only projects, use the macOS-only variant instead.

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
    uses: cboone/gh-actions/.github/workflows/release-rust-binaries.yml@91f9abd25d4f82354c0f950dfc8b6d7525b0f5b5 # v3.0.0
    with:
      binary-name: PROJECT-NAME
```

## Notes

- The `binary-name` input is required. Set it to the crate's binary name (from `Cargo.toml` `[[bin]]` or `[package] name`).
- The reusable workflow builds 5 targets by default: Linux (x86_64, aarch64), macOS (x86_64, aarch64), and Windows (x86_64). It handles cross-compilation tools, artifact packaging, SHA-256 checksums, and GitHub release creation internally.
- Optional inputs include `rust-version` (default: `stable`), `targets` (space-separated target triples to override defaults), `cargo-args` (default: `--release`), and `timeout-minutes` (default: 30).
- Triggered by pushing tags matching `v*` (e.g., `git tag v0.1.0 && git push origin v0.1.0`).
- `cancel-in-progress: false` ensures releases are never cancelled mid-flight.
