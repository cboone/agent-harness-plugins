# Setup Installers: Multi-Language Support and Fixes

Addresses issues #130, #131, #132, #133, #134.

## Context

The `setup-installers` command is Go-only. When used on a Swift project (pbcopy2), it couldn't detect the project type, couldn't generate a platform-constrained Homebrew formula, didn't create a release workflow for building and publishing binaries, and the generated `install.sh` had ShellCheck and Prettier compatibility issues. These five issues capture everything that had to be done manually.

## Files to Modify

| File | What Changes |
|------|-------------|
| `plugins/setup-installers/commands/setup-installers.md` | All five issues: multi-language detection, release workflow, tap issue, ShellCheck, Prettier |
| `plugins/setup-installers/.claude-plugin/plugin.json` | Version 1.1.0 to 1.3.0, updated description and keywords |
| `.claude-plugin/marketplace.json` | Matching version, description, keywords for setup-installers entry |
| `plugins/setup-installers/README.md` | Rewrite for multi-language support |
| `README.md` (root) | Update setup-installers description line |

## Implementation

### Commit 1: ShellCheck and Prettier fixes (#134, #133)

In `setup-installers.md`, Section 6 (Set Up Shell Install Script):

**ShellCheck (#134)**:

1. Add `# shellcheck disable=SC2016` before the PATH output line in the install.sh template (line 229)
2. Add a paragraph after `chmod +x install.sh` instructing to run `shellcheck install.sh` if available, fix or suppress any findings, and note if ShellCheck is not installed

**Prettier (#133)**:

3. Add a paragraph after the ShellCheck step: if `.prettierignore` exists and does not already contain `*.sh`, append `*.sh` to it. Skip if no `.prettierignore` exists.

### Commit 2: Multi-language detection and templates (#132)

This is the foundational change, touching most sections of `setup-installers.md`.

**Frontmatter and intro**:

- Update description to mention Go, Swift, and Rust
- Update `argument-hint` to include `cargo-install`
- Add cargo install to the installer type list

**Section 1 (Detect Project Type)**: Replace Go-only detection with a language detection table:

| Marker | Language | Notes |
|--------|----------|-------|
| `go.mod` | Go | Also check for `.goreleaser.yml`/`.goreleaser.yaml` |
| `Package.swift` | Swift | Check for macOS-only constraints (AppKit/Cocoa imports, `.macOS` platform) |
| `Cargo.toml` | Rust | Check for `[[bin]]` or `src/main.rs` to confirm binary crate |

If none found, only the shell install script is applicable as a generic binary distribution method.

**Section 2 (Detect Existing Installers)**: Add cargo install detection (grep README for `cargo install`).

**Section 3 (Select Installer Types)**: Add applicability table:

| Installer | Go | Swift | Rust | Other |
|-----------|-----|-------|------|-------|
| Homebrew | Yes | Yes | Yes | No |
| Shell install script | Yes | Yes | Yes | Yes |
| go install | Yes | No | No | No |
| cargo install | No | No | Yes | No |

**Section 4 (Gather Project Info)**: Expand binary name inference per language (Swift: Package.swift target; Rust: Cargo.toml `[[bin]]` or `package.name`).

**Section 5 (Set Up Homebrew)**: Add a platform-constrained formula variant for macOS-only projects with `depends_on :macos` and only `on_intel`/`on_arm` blocks (no `on_linux`). Cross-platform projects use the existing four-block formula.

**Section 6 (Set Up Shell Install Script)**: For macOS-only projects, add a platform guard at the top of the generated script (`uname -s != Darwin` check) and simplify OS detection to always set `OS="darwin"`.

**Section 7 (Set Up go install)**: Rename to "Set Up Language-Specific Install Method". Keep existing go install content as a subsection. Add a cargo install subsection that checks for path dependencies, determines install command (crates.io vs `--git`), and outputs README content only.

**Section 8 (Update README)**: Add cargo install template to the README Installation section.

**Error Handling**: Add cases for Swift library projects (no executable targets) and Rust library crates (no `[[bin]]` or `src/main.rs`).

### Commit 3: Release workflow generation (#130)

Add a new section between current Sections 7 and 8 (becomes new Section 8, renumbering subsequent sections to 9 and 10).

**Section 8: Set Up Release Workflow**

- If GoReleaser exists: skip, note in summary
- If `.github/workflows/release.yml` exists: present contents and ask to overwrite, skip, or merge
- Otherwise, generate from language-specific templates below

**Go (without GoReleaser) release workflow**: Matrix build with `GOOS`/`GOARCH` for linux/darwin x amd64/arm64 on `ubuntu-latest`. Cross-compile with `CGO_ENABLED=0`. Upload artifacts, then a publish job downloads them, generates `checksums.txt` with `sha256sum`, and creates a release via `softprops/action-gh-release@v2`.

**Swift release workflow**: Build on `macos-15` runner for `arm64` and `x86_64` architectures. Use `swift build -c release --arch ARCH`. Same publish pattern with checksums and `softprops/action-gh-release@v2`. For macOS-only projects (the common case), only Darwin matrix entries.

**Rust release workflow**: Matrix with four targets (`x86_64-unknown-linux-gnu`, `aarch64-unknown-linux-gnu`, `x86_64-apple-darwin`, `aarch64-apple-darwin`). Linux targets on `ubuntu-latest`, macOS on `macos-latest`. Cross-compilation for `aarch64-unknown-linux-gnu` installs `gcc-aarch64-linux-gnu`. Same publish pattern. For macOS-only projects, remove Linux matrix entries.

**Template notes** (included in the command file for the executing agent):

- `PROJECT-NAME` placeholder replacement
- Tarball naming must match `install.sh` and Homebrew formula: `BINARY-VERSION-OS-ARCH.tar.gz`
- `softprops/action-gh-release@v2` follows project convention (version tags, not SHAs)
- `generate_release_notes: true` for auto-generated notes

Update the summary section to include release workflow in "Files created" and add a next step about tagging the first release.

### Commit 4: Homebrew-tap issue creation (#131)

Add to Section 5 (Set Up Homebrew), at the end of the standalone formula logic.

**Detection**: Run `gh repo view OWNER/homebrew-tap` to check if the tap repo exists.

**If tap repo exists**: Offer to create an issue there using `gh issue create --repo OWNER/homebrew-tap`. Issue body contains:

1. Project description
2. Complete formula content in a Ruby code block
3. Tarball naming convention
4. SHA256 computation instructions (download release tarballs, run `shasum -a 256`)
5. Note about waiting for the first tagged release
6. For macOS-only projects: note the `depends_on :macos` requirement

**If tap repo does not exist**: Suggest creating it with `gh repo create OWNER/homebrew-tap --public`, then offer to create the issue.

Update the summary to note whether a tap issue was created, with the issue URL.

### Commit 5: Version bumps and metadata updates

**`plugin.json`**:

- `version`: `"1.1.0"` to `"1.3.0"`
- `description`: "Set up installer and distribution methods for Go, Swift, and Rust projects: Homebrew tap, shell install script, go/cargo install, and release workflow."
- `keywords`: add `"swift"`, `"rust"`, `"cargo"`, `"release"`, `"github-actions"`

**`marketplace.json`** (setup-installers entry):

- `version`: `"1.1.0"` to `"1.3.0"`
- `description`: match plugin.json
- `keywords`: match plugin.json

**`plugins/setup-installers/README.md`**:

- Update opening to mention Go, Swift, and Rust
- Add release workflow generation and tap issue creation to "What It Does"
- Add cargo install to installer types
- Update usage examples
- Add a "Supported Languages" table

**Root `README.md`**: Update the setup-installers description line (~line 310) to mention Go, Swift, Rust, and release workflows.

## Verification

1. Read the final `setup-installers.md` end-to-end and confirm all five issues are addressed
2. Run `check-versions` skill to verify plugin.json and marketplace.json versions match
3. Verify section numbering is sequential and all cross-references are correct
4. Confirm tarball naming is consistent across the release workflow templates, install.sh template, and Homebrew formula templates
5. Check that the root README entry accurately reflects the new capabilities
