# Release Workflow Template (Cross-Platform)

Create `.github/workflows/release.yml` with the following content.

Replace `PROJECT-NAME` with the project name.

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
  build:
    runs-on: ${{ matrix.runner }}
    timeout-minutes: 30
    strategy:
      matrix:
        include:
          - target: x86_64-unknown-linux-gnu
            runner: ubuntu-latest
            arch: amd64
            os: linux
          - target: aarch64-unknown-linux-gnu
            runner: ubuntu-latest
            arch: arm64
            os: linux
          - target: x86_64-apple-darwin
            runner: macos-latest
            arch: amd64
            os: darwin
          - target: aarch64-apple-darwin
            runner: macos-latest
            arch: arm64
            os: darwin
    steps:
      - uses: actions/checkout@v6

      - uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}

      - name: Install cross-compilation tools
        if: matrix.target == 'aarch64-unknown-linux-gnu'
        run: |
          sudo apt-get update
          sudo apt-get install -y gcc-aarch64-linux-gnu
          echo "CARGO_TARGET_AARCH64_UNKNOWN_LINUX_GNU_LINKER=aarch64-linux-gnu-gcc" >> "$GITHUB_ENV"

      - name: Build
        run: |
          VERSION="${GITHUB_REF_NAME#v}"
          BINARY="PROJECT-NAME"
          cargo build --release --target ${{ matrix.target }}
          tar -czf "${BINARY}-${VERSION}-${{ matrix.os }}-${{ matrix.arch }}.tar.gz" \
            -C "target/${{ matrix.target }}/release" "${BINARY}"

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: release-${{ matrix.os }}-${{ matrix.arch }}
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

- Builds 4 targets: Linux (amd64, arm64) and macOS (amd64, arm64).
- The `aarch64-unknown-linux-gnu` target requires cross-compilation tools. The workflow installs `gcc-aarch64-linux-gnu` and sets the appropriate linker environment variable.
- macOS targets (both amd64 and arm64) build natively on `macos-latest` without cross-compilation.
- The publish job collects all artifacts, generates SHA-256 checksums, and creates a GitHub release.
- Triggered by pushing tags matching `v*` (e.g., `git tag v0.1.0 && git push origin v0.1.0`).
- `cancel-in-progress: false` ensures releases are never cancelled mid-flight.
