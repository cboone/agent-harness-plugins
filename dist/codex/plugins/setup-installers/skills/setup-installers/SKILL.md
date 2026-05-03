---
name: setup-installers
description: >-
  Set up installer and distribution methods for Go, Swift, Rust, and Zig
  projects: Homebrew tap, go/cargo install, and release workflow.
---

# Setup Installers

Set up installer and distribution methods for a project. Supports Go, Swift, Rust, and Zig projects.

Installer types:

- **Homebrew**: a Homebrew tap formula for `brew install`
- **go install**: compatibility and README instructions for `go install` (Go only)
- **cargo install**: compatibility and README instructions for `cargo install` (Rust only)

## Workflow

### 1. Detect Project Type

Scan the project to determine its language and structure:

| Marker          | Language | Notes                                               |
| --------------- | -------- | --------------------------------------------------- |
| `go.mod`        | Go       | Also check for `.goreleaser.yml`/`.goreleaser.yaml` |
| `Package.swift` | Swift    | Check for macOS-only constraints                    |
| `Cargo.toml`    | Rust     | Check for binary targets                            |
| `build.zig`     | Zig      | Check for executable targets                        |

Additional checks regardless of language:

- Check for a `Makefile`
- Run `gh repo view --json owner,name,description` to get GitHub repo info

**Go sub-detection**: If `.goreleaser.yml` or `.goreleaser.yaml` exists, note that GoReleaser is already configured (this affects Homebrew and release workflow steps).

**Swift platform detection**: Check for macOS-only constraints:

1. Grep source files for AppKit, Cocoa, or macOS-specific framework imports
1. Look for conditional compilation or macOS-only availability checks (for example `#if os(macOS)`, `canImport(AppKit)`)
1. If inconclusive, ask the user whether the project is macOS-only or cross-platform

**Rust binary detection**: Check `Cargo.toml` for `[[bin]]` sections, a `src/main.rs` file, or binaries under `src/bin/` (for example, `src/bin/*.rs`) to confirm this is a binary crate (not a library).

**Zig binary detection**: Check `build.zig` for `b.addExecutable(.{ .name = "..." })` calls or a `src/main.zig` file to confirm this is an executable project (not a library).

If none of the above markers are found, inform the user that the project type is not supported. This command requires a Go, Swift, Rust, or Zig project.

### 2. Detect Existing Installers

Check for installers that are already set up:

- **Homebrew**: look for a `homebrew_casks:` or `brews:` section in `.goreleaser.yml` or `.goreleaser.yaml`, or a standalone `Formula/` directory
- **go install**: grep the README for `go install` instructions (Go only)
- **cargo install**: grep the README for `cargo install` instructions (Rust only)
- **Release workflow**: look for `.github/workflows/release.yml` or `.github/workflows/release.yaml`

Report any existing installers to the user before proceeding. Existing installers can be updated or skipped.

### 3. Select Installer Types

If the user named an installer type in their request (e.g., `homebrew`, `go-install`, `cargo-install`, or a comma-separated combination), use that selection.

Otherwise, ask the user which installer types to set up. Present applicable options based on the detected language:

| Installer     | Go  | Swift | Rust | Zig |
| ------------- | --- | ----- | ---- | --- |
| Homebrew      | Yes | Yes   | Yes  | Yes |
| go install    | Yes | No    | No   | No  |
| cargo install | No  | No    | Yes  | No  |

Include notes about which installers are already detected and which are not applicable to the project type.

### 4. Gather Project Information

Collect the following, inferring from existing files where possible. Do not re-ask for information the user already provided:

- **Binary name**:
  - Go: from Makefile, `.goreleaser.yml`, or the last segment of the Go module path
  - Swift: from `Package.swift` executable target name, or the package name
  - Rust: from `Cargo.toml` `[[bin]]` name, `package.name`, or the directory name
  - Zig: from `build.zig` by reading the `.name` field in `b.addExecutable(.{ .name = "..." })`, or the directory name
- **Project description**: from the README or `gh repo view`
- **GitHub owner/repo**: from `gh repo view`, the Go module path, or `git remote`
- **Latest tag**: run `git describe --tags --abbrev=0 2>/dev/null` (may not exist yet)
- **Platform constraints**: macOS-only or cross-platform (from step 1 detection)

### 5. Set Up Homebrew

Skip this section if the user did not select Homebrew.

**If GoReleaser exists with a `homebrew_casks:` or `brews:` section**: Homebrew is already handled by GoReleaser. Tell the user and check for the `HOMEBREW_TAP_TOKEN` secret:

```bash
gh secret list | grep HOMEBREW_TAP_TOKEN || true
```

If the secret is missing, warn the user that releases will fail without it. Suggest invoking the add-goreleaser-homebrew skill for a guided setup that includes interactive token configuration, or manually adding the secret (see the HOMEBREW_TAP_TOKEN Setup reference in the add-goreleaser-homebrew skill).

**If GoReleaser exists without a `homebrew_casks:` or `brews:` section**: suggest invoking the add-goreleaser-homebrew skill to add Homebrew support through GoReleaser, which is the preferred approach for Go projects with GoReleaser. That skill includes interactive `HOMEBREW_TAP_TOKEN` setup. Skip creating a standalone formula.

**If no GoReleaser exists**: create a standalone Homebrew formula. Choose the appropriate template based on platform constraints.

#### Cross-Platform Homebrew Formula

For projects that support both macOS and Linux (most Go and Rust projects), generate `Formula/PROJECT-NAME.rb`:

```ruby
class ProjectName < Formula
  desc "PROJECT-DESCRIPTION"
  homepage "https://github.com/OWNER/REPO"
  version "0.1.0"
  license "MIT"

  on_macos do
    on_intel do
      url "https://github.com/OWNER/REPO/releases/download/v0.1.0/PROJECT-NAME-0.1.0-darwin-amd64.tar.gz"
      sha256 "SHA256_FOR_DARWIN_AMD64"
    end

    on_arm do
      url "https://github.com/OWNER/REPO/releases/download/v0.1.0/PROJECT-NAME-0.1.0-darwin-arm64.tar.gz"
      sha256 "SHA256_FOR_DARWIN_ARM64"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/OWNER/REPO/releases/download/v0.1.0/PROJECT-NAME-0.1.0-linux-amd64.tar.gz"
      sha256 "SHA256_FOR_LINUX_AMD64"
    end

    on_arm do
      url "https://github.com/OWNER/REPO/releases/download/v0.1.0/PROJECT-NAME-0.1.0-linux-arm64.tar.gz"
      sha256 "SHA256_FOR_LINUX_ARM64"
    end
  end

  def install
    bin.install "PROJECT-NAME"
  end

  test do
    system bin/"PROJECT-NAME", "--version"
  end
end
```

#### macOS-Only Homebrew Formula

For macOS-only projects (e.g., Swift apps using AppKit), generate `Formula/PROJECT-NAME.rb` with a macOS dependency and no Linux blocks:

```ruby
class ProjectName < Formula
  desc "PROJECT-DESCRIPTION"
  homepage "https://github.com/OWNER/REPO"
  version "0.1.0"
  license "MIT"

  depends_on :macos

  on_intel do
    url "https://github.com/OWNER/REPO/releases/download/v0.1.0/PROJECT-NAME-0.1.0-darwin-amd64.tar.gz"
    sha256 "SHA256_FOR_DARWIN_AMD64"
  end

  on_arm do
    url "https://github.com/OWNER/REPO/releases/download/v0.1.0/PROJECT-NAME-0.1.0-darwin-arm64.tar.gz"
    sha256 "SHA256_FOR_DARWIN_ARM64"
  end

  def install
    bin.install "PROJECT-NAME"
  end

  test do
    system bin/"PROJECT-NAME", "--version"
  end
end
```

Adjust the license field based on the project's actual license file.

#### Create Issue on Homebrew Tap Repository

After generating the standalone formula, detect the user's homebrew-tap repository:

```bash
OWNER=$(gh repo view --json owner -q .owner.login)
gh repo view "${OWNER}/homebrew-tap" --json name -q .name 2>/dev/null
```

**If the tap repo exists**, offer to create an issue there with the formula and setup instructions. Write the issue body to a temp file (using `mktemp`) and use `gh issue create`:

```bash
tmp_issue_body="$(mktemp)"
trap 'rm -f "${tmp_issue_body}"' EXIT

# Write the issue body to "${tmp_issue_body}" here.

gh issue create --repo "${OWNER}/homebrew-tap" \
  --title "Add PROJECT-NAME formula" \
  --body-file "${tmp_issue_body}"
```

The issue body should contain:

1. A brief description of the project
1. The complete formula content in a Ruby code block
1. The tarball naming convention used by the release workflow (e.g., `PROJECT-NAME-VERSION-OS-ARCH.tar.gz`)
1. Instructions for computing SHA256 values after the first release:
   - Download the release tarballs from the GitHub Release page
   - Run `shasum -a 256 *.tar.gz`
   - Replace the placeholder `SHA256_FOR_*` values in the formula
1. A note that this formula should be added after the first tagged release produces artifacts
1. For macOS-only projects: note the `depends_on :macos` requirement

**If the tap repo does not exist**, tell the user and suggest creating it:

```bash
gh repo create "${OWNER}/homebrew-tap" --public --description "Homebrew tap for ${OWNER}'s tools"
```

Then offer to create the issue after the repo is created.

### 6. Set Up Language-Specific Install Method

#### go install (Go projects only)

Skip this section if the user did not select go install, or if this is not a Go project.

Check compatibility:

1. Read `go.mod` for any `replace` directives. If present, warn the user that `go install` does not work with `replace` directives in the module root. Suggest either removing the directives or skipping `go install` instructions.
1. Determine the install path:
   - If `main.go` is in the repo root: `go install github.com/OWNER/REPO@latest`
   - If `main.go` is in a subdirectory (e.g., `cmd/PROJECT-NAME/`): `go install github.com/OWNER/REPO/cmd/PROJECT-NAME@latest`
1. Verify the module path is a valid import path (starts with a domain name).

Do not create any files for this installer type. The output is README content only.

#### cargo install (Rust projects only)

Skip this section if the user did not select cargo install, or if this is not a Rust project.

Check compatibility:

1. Read `Cargo.toml` for `path` dependencies. If present, warn the user that `cargo install` may not work with local path dependencies.
1. Use the broader Rust binary detection logic (the same used for other Rust installers) to determine available binary targets. This must handle:
   - Explicit `[[bin]]` sections in `Cargo.toml`
   - The default binary from `src/main.rs` when no `[[bin]]` is present
   - Additional binaries under `src/bin/*.rs`
1. Determine the install command using the detected crate/binary name:
   - If the crate is published to crates.io: `cargo install PROJECT-NAME`
   - If not published: `cargo install --git https://github.com/OWNER/REPO`

Do not create any files for this installer type. The output is README content only.

### 7. Set Up Release Workflow

If the user selected Homebrew, the generated files depend on GitHub Releases with tarballs in a specific naming format. Offer to generate a release workflow.

**If GoReleaser exists**: Skip this step. GoReleaser handles releases. Note this in the summary.

**If a release workflow already exists** at `.github/workflows/release.yml` or `.github/workflows/release.yaml`: present its content and ask whether to overwrite, skip, or merge.

**Otherwise**: Generate `.github/workflows/release.yml` from the appropriate language template below. The `.github/workflows/` directory will be created automatically if it does not exist.

All release workflow templates share:

- Trigger: push tags matching `v*`
- `permissions: contents: write` (needed to create releases)
- Build matrix producing tarballs in the format `BINARY-VERSION-OS-ARCH.tar.gz`
- A `publish` job that downloads all artifacts, generates `checksums.txt`, and creates a GitHub Release via `cboone/gh-actions/actions/create-gh-release@91f9abd25d4f82354c0f950dfc8b6d7525b0f5b5 # v3.0.0`
- `generate-release-notes: true` for auto-generated release notes

Replace `PROJECT-NAME` with the actual binary name in all templates.

#### Reference: Go Release Workflow (without GoReleaser)

Use when the project has `go.mod` but no GoReleaser configuration. Cross-compiles for linux/darwin on amd64/arm64.

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
    runs-on: ubuntu-latest
    timeout-minutes: 30
    strategy:
      matrix:
        include:
          - goos: linux
            goarch: amd64
          - goos: linux
            goarch: arm64
          - goos: darwin
            goarch: amd64
          - goos: darwin
            goarch: arm64
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2

      - uses: actions/setup-go@4a3601121dd01d1626a1e23e37211e3254c1c06c # v6.4.0
        with:
          go-version-file: go.mod

      - name: Build
        env:
          GOOS: ${{ matrix.goos }}
          GOARCH: ${{ matrix.goarch }}
          CGO_ENABLED: "0"
        run: |
          VERSION="${GITHUB_REF_NAME#v}"
          BINARY="PROJECT-NAME"
          go build -ldflags "-s -w -X main.version=${VERSION}" -o "${BINARY}" .
          tar -czf "${BINARY}-${VERSION}-${{ matrix.goos }}-${{ matrix.goarch }}.tar.gz" "${BINARY}"

      - name: Upload artifact
        uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1
        with:
          name: release-${{ matrix.goos }}-${{ matrix.goarch }}
          path: "*.tar.gz"

  publish:
    needs: build
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8.0.1
        with:
          pattern: release-*
          merge-multiple: true

      - name: Generate checksums
        run: sha256sum *.tar.gz > checksums.txt

      - name: Create release
        uses: cboone/gh-actions/actions/create-gh-release@91f9abd25d4f82354c0f950dfc8b6d7525b0f5b5 # v3.0.0
        with:
          files: |
            *.tar.gz
            checksums.txt
          generate-release-notes: true
```

Notes:

- Concurrency uses `cancel-in-progress: false` to avoid interrupting active releases
- Adjust the `-X main.version` ldflags path if the version variable is in a different package
- For projects with `main.go` in a subdirectory (e.g., `cmd/PROJECT-NAME/`), adjust the `go build` path accordingly
- `CGO_ENABLED=0` produces static binaries for maximum portability

#### Reference: Swift Release Workflow

Use for Swift projects. Builds on `macos-15` runner. For macOS-only projects (the common case), builds `arm64` and `x86_64` for Darwin only.

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
    # macOS runner required for Swift compilation
    runs-on: macos-15
    timeout-minutes: 30
    strategy:
      matrix:
        arch: [arm64, x86_64]
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2

      - name: Build
        run: |
          VERSION="${GITHUB_REF_NAME#v}"
          BINARY="PROJECT-NAME"
          swift build -c release --arch ${{ matrix.arch }}
          BUILT=".build/apple/Products/Release/${BINARY}"
          if [ ! -f "${BUILT}" ]; then
            BUILT="$(swift build -c release --arch ${{ matrix.arch }} --show-bin-path)/${BINARY}"
          fi
          ARCH="${{ matrix.arch }}"
          if [ "${ARCH}" = "x86_64" ]; then
            ARCH="amd64"
          fi
          tar -czf "${BINARY}-${VERSION}-darwin-${ARCH}.tar.gz" -C "$(dirname "${BUILT}")" "${BINARY}"

      - name: Upload artifact
        uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1
        with:
          name: release-darwin-${{ matrix.arch }}
          path: "*.tar.gz"

  publish:
    needs: build
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8.0.1
        with:
          pattern: release-*
          merge-multiple: true

      - name: Generate checksums
        run: sha256sum *.tar.gz > checksums.txt

      - name: Create release
        uses: cboone/gh-actions/actions/create-gh-release@91f9abd25d4f82354c0f950dfc8b6d7525b0f5b5 # v3.0.0
        with:
          files: |
            *.tar.gz
            checksums.txt
          generate-release-notes: true
```

Notes:

- Concurrency uses `cancel-in-progress: false` to avoid interrupting active releases
- The build step maps `x86_64` to `amd64` in the tarball name to match the tarball naming convention used by Homebrew formulas
- The binary path varies between Swift versions; the template tries `.build/apple/Products/Release/` first, then falls back to `--show-bin-path`
- Swift cross-compilation to Linux is not supported in this template; add Linux targets manually if needed

#### Reference: Rust Release Workflow

Use for Rust projects. Cross-compiles for linux/darwin on amd64/arm64.

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
            os: linux
            arch: amd64
          - target: aarch64-unknown-linux-gnu
            runner: ubuntu-latest
            os: linux
            arch: arm64
          # macOS runners cost 10x Linux. For cost optimization, consider
          # cargo-zigbuild to cross-compile darwin targets on Linux.
          - target: x86_64-apple-darwin
            runner: macos-latest
            os: darwin
            arch: amd64
          - target: aarch64-apple-darwin
            runner: macos-latest
            os: darwin
            arch: arm64
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2

      - uses: dtolnay/rust-toolchain@29eef336d9b2848a0b548edc03f92a220660cdb8 # stable
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
        uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1
        with:
          name: release-${{ matrix.os }}-${{ matrix.arch }}
          path: "*.tar.gz"

  publish:
    needs: build
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8.0.1
        with:
          pattern: release-*
          merge-multiple: true

      - name: Generate checksums
        run: sha256sum *.tar.gz > checksums.txt

      - name: Create release
        uses: cboone/gh-actions/actions/create-gh-release@91f9abd25d4f82354c0f950dfc8b6d7525b0f5b5 # v3.0.0
        with:
          files: |
            *.tar.gz
            checksums.txt
          generate-release-notes: true
```

Notes:

- Concurrency uses `cancel-in-progress: false` to avoid interrupting active releases
- For macOS-only Rust projects, remove the two Linux matrix entries
- `aarch64-unknown-linux-gnu` cross-compilation requires `gcc-aarch64-linux-gnu` on Ubuntu runners
- For Rust workspace projects, adjust the `cargo build` command to target the specific binary
- **Action pinning**: every `uses:` ref (third-party and `cboone/gh-actions`) is pinned to a 40-char commit SHA with a `# vX.Y.Z` comment. Tags are mutable; SHAs are not. The comment lets Dependabot and human reviewers see the intended version. The `cboone/gh-actions` SHAs in the templates rot as new releases ship; refresh them at scaffold time per the note in this skill's SKILL.md.
- **`dtolnay/rust-toolchain` channel pin**: this action releases through the moving `stable`/`nightly`/`beta` channel aliases rather than SemVer tags, so the comment is `# stable` (or the chosen channel) rather than `# vX.Y.Z`. The SHA is still pinned for security; refresh it manually when you want to pick up a newer Rust toolchain. `bin/version-audit` does not track drift on channel-pinned refs.

#### Reference: Zig Release Workflow

Use for Zig projects. Cross-compiles for linux/darwin on amd64/arm64 plus Windows amd64. Unlike Rust, all targets build on a single `ubuntu-latest` runner with no extra toolchains.

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
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2

      - name: Set up Zig
        uses: mlugg/setup-zig@d1434d08867e3ee9daa34448df10607b98908d29 # v2.2.1

      - name: Build release binaries
        run: |
          VERSION="${GITHUB_REF_NAME#v}"
          BINARY="PROJECT-NAME"
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
            # Map Zig target triples to archive naming convention
            case "${target}" in
              x86_64-linux)   os="linux";  arch="amd64" ;;
              aarch64-linux)  os="linux";  arch="arm64" ;;
              x86_64-macos)   os="darwin"; arch="amd64" ;;
              aarch64-macos)  os="darwin"; arch="arm64" ;;
              x86_64-windows) os="windows"; arch="amd64" ;;
            esac
            if [ "${os}" = "windows" ]; then
              zip "${BINARY}-${VERSION}-${os}-${arch}.zip" "zig-out/bin/${BINARY}.exe"
            else
              tar -czf "${BINARY}-${VERSION}-${os}-${arch}.tar.gz" -C "zig-out/bin" "${BINARY}"
            fi
          done

      - name: Upload artifacts
        uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1
        with:
          name: release-binaries
          path: |
            *.tar.gz
            *.zip

  publish:
    needs: build
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8.0.1
        with:
          name: release-binaries

      - name: Generate checksums
        run: sha256sum *.tar.gz *.zip > checksums.txt

      - name: Create release
        uses: cboone/gh-actions/actions/create-gh-release@91f9abd25d4f82354c0f950dfc8b6d7525b0f5b5 # v3.0.0
        with:
          files: |
            *.tar.gz
            *.zip
            checksums.txt
          generate-release-notes: true
```

Notes:

- Concurrency uses `cancel-in-progress: false` to avoid interrupting active releases
- All 5 targets build on a single `ubuntu-latest` runner. Zig's cross-compilation requires no extra toolchains, no macOS runners, and no cross-compilation tools.
- The `mlugg/setup-zig@d1434d08867e3ee9daa34448df10607b98908d29 # v2.2.1` action reads the Zig version from `build.zig.zon` by default
- Windows produces a `.zip` archive; all other targets produce `.tar.gz`
- **Action pinning**: every `uses:` ref (third-party and `cboone/gh-actions`) is pinned to a 40-char commit SHA with a `# vX.Y.Z` comment. Tags are mutable; SHAs are not. The comment lets Dependabot and human reviewers see the intended version. The `cboone/gh-actions` SHAs in the templates rot as new releases ship; refresh them at scaffold time per the note in this skill's SKILL.md.

### 8. Update README

Add or merge an **Installation** section in the README. If an Installation section already exists, merge the new methods into it without removing existing content.

Use this structure (including only the methods that were set up):

````markdown
## Installation

### Homebrew

```bash
brew install OWNER/tap/PROJECT-NAME
```

### go install

Requires Go 1.21 or later:

```bash
go install github.com/OWNER/REPO@latest
```

### cargo install

Requires Rust 1.XX or later:

```bash
cargo install PROJECT-NAME
```

Or install from source:

```bash
cargo install --git https://github.com/OWNER/REPO
```
````

Adjust the Go version requirement based on the minimum version in `go.mod`. Adjust the Rust version requirement based on `rust-version` in `Cargo.toml` or the MSRV.

If the README already has installation instructions, integrate the new methods into the existing section rather than creating a duplicate.

### 9. Print Summary

After completing all selected installer types, print a summary:

- **Files created**: list each new file with its path (including release workflow if generated)
- **Files modified**: list each modified file with what changed
- **Skipped installers**: note any installers that were skipped and why (e.g., "Homebrew: already configured via GoReleaser", "Release workflow: GoReleaser handles releases")
- **Next steps**: note any required follow-up actions:
  - For Homebrew standalone formula: if an issue was created on the tap repo, note the issue URL; otherwise, remind the user to create the tap repository and push the formula
  - For go install: ensure the module has no `replace` directives and is tagged with a version
  - For cargo install: ensure the crate is published to crates.io (if applicable)
  - For release workflow: tag a release to trigger the workflow (e.g., `git tag v0.1.0 && git push origin v0.1.0`)
  - If `HOMEBREW_TAP_TOKEN` was found to be missing during step 5: remind the user to configure it before the first release, either by invoking the add-goreleaser-homebrew skill for guided setup or by manually creating a fine-grained PAT and adding it as a repository secret

## Error Handling

- If not in a git repository, abort with a message
- If `gh` is not installed, fall back to inferring owner/repo from `git remote`, `go.mod`, or `Cargo.toml`
- If no GitHub Releases exist yet, note that installers depend on tagged releases
- If `go.mod` has `replace` directives, warn about go install incompatibility
- If `Cargo.toml` has `path` dependencies, warn about cargo install incompatibility
- If `Package.swift` has no executable targets, warn that the project may be a library (installer setup is for binary distributions)
- If `Cargo.toml` has no `[[bin]]` section and no `src/main.rs`, warn that the project may be a library
- If the README does not exist, create one with just the Installation section
- If the release workflow already exists, ask before overwriting
- If the homebrew-tap repo cannot be accessed, fall back to providing formula content inline

## Refresh `cboone/gh-actions` SHAs before scaffolding

The `cboone/gh-actions` reusable-workflow refs in this skill's templates are SHA-pinned with a `# vX.Y.Z` comment that was current when the template was authored. New releases of `cboone/gh-actions` rot those SHAs. Before emitting a workflow into a user's repo, refresh both the SHA and the comment to current latest:

```bash
TAG="$(gh release view --repo cboone/gh-actions --json tagName --jq '.tagName')"
SHA="$(gh api "repos/cboone/gh-actions/commits/${TAG}" --jq '.sha')"
echo "${SHA} # ${TAG}"
```

Replace each `cboone/gh-actions/.../<workflow>.yml@<old-sha> # <old-tag>` in the emitted workflow with the new SHA and tag. Dependabot in the user's repo keeps them in sync afterwards.
