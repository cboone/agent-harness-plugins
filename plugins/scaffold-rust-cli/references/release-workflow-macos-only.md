# Release Workflow Template (macOS-only)

Create `.github/workflows/release.yml` with the following content.

Replace `PROJECT-NAME` with the project name.

Use this template when the project only targets macOS (depends on Security.framework, AppKit, etc.).

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
  build:
    runs-on: macos-latest
    timeout-minutes: 30
    strategy:
      matrix:
        include:
          - target: x86_64-apple-darwin
            arch: amd64
          - target: aarch64-apple-darwin
            arch: arm64
    steps:
      - uses: actions/checkout@v6

      - uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}

      - name: Build
        run: |
          VERSION="${GITHUB_REF_NAME#v}"
          BINARY="PROJECT-NAME"
          cargo build --release --target ${{ matrix.target }}
          tar -czf "${BINARY}-${VERSION}-darwin-${{ matrix.arch }}.tar.gz" \
            -C "target/${{ matrix.target }}/release" "${BINARY}"

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: release-darwin-${{ matrix.arch }}
          path: "*.tar.gz"

  publish:
    needs: build
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          pattern: release-*
          merge-multiple: true

      - name: Generate checksums
        run: sha256sum ./*.tar.gz > checksums.txt

      - name: Create release
        uses: softprops/action-gh-release@v2
        with:
          files: |
            *.tar.gz
            checksums.txt
          generate_release_notes: true
```

## Notes

- Builds 2 macOS targets: amd64 (Intel) and arm64 (Apple Silicon). No Linux targets.
- Both targets build natively on `macos-latest` without cross-compilation.
- The publish job runs on `ubuntu-latest` since it only downloads artifacts and creates the release (no macOS-specific dependencies needed).
- Triggered by pushing tags matching `v*` (e.g., `git tag v0.1.0 && git push origin v0.1.0`).
