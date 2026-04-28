# Release Workflow Template (macOS-only)

Create `.github/workflows/release.yml` with the following content.

Replace `PROJECT-NAME` with the project name.

Uses the `cboone/gh-actions` reusable workflow with targets constrained to macOS. Use this template when the project only targets macOS (depends on Security.framework, AppKit, etc.).

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
    uses: cboone/gh-actions/.github/workflows/rust-release.yml@v2
    with:
      binary-name: PROJECT-NAME
      targets: "x86_64-apple-darwin aarch64-apple-darwin"
```

## Notes

- Builds 2 macOS targets: amd64 (Intel) and arm64 (Apple Silicon). No Linux or Windows targets.
- The `targets` input overrides the default 5-target list to include only macOS targets.
- The reusable workflow handles native macOS builds, artifact packaging, SHA-256 checksums, and GitHub release creation internally.
- Triggered by pushing tags matching `v*` (e.g., `git tag v0.1.0 && git push origin v0.1.0`).
