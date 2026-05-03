# Setup Installers

Set up installer and distribution methods for Go, Swift, Rust, and Zig projects: Homebrew tap formula, go/cargo install, and release workflow.

**Type:** Command
**Trigger:** `/setup-installers`

## Installation

See the [marketplace install instructions](../../README.md#install).

## Supported Languages

| Language | Homebrew | go install | cargo install | Release Workflow        |
| -------- | -------- | ---------- | ------------- | ----------------------- |
| Go       | Yes      | Yes        | -             | Yes (unless GoReleaser) |
| Swift    | Yes      | -          | -             | Yes                     |
| Rust     | Yes      | -          | Yes           | Yes                     |
| Zig      | Yes      | -          | -             | Yes                     |

## What It Does

Detects the project language and existing release infrastructure, then generates appropriate distribution files:

- **Homebrew**: standalone tap formula (cross-platform or macOS-only), with optional issue creation on the homebrew-tap repo. Defers to GoReleaser when already configured.
- **go install**: verifies Go module compatibility and adds README instructions
- **cargo install**: verifies Rust crate compatibility and adds README instructions
- **Release workflow**: generates `.github/workflows/release.yml` with language-specific build matrix, checksums, and GitHub Release creation

## Usage

```text
/setup-installers
```

Pass an argument to skip the selection prompt:

```text
/setup-installers homebrew
/setup-installers go-install
/setup-installers cargo-install
```

## Examples

- `/setup-installers`: walks through all applicable installer types interactively
- `/setup-installers homebrew`: sets up only Homebrew distribution

## See Also

- [Add GoReleaser Homebrew](../add-goreleaser-homebrew/README.md): add GoReleaser with Homebrew tap publishing (release pipeline)
- [Scaffold Go CLI](../scaffold-go-cli/README.md): scaffold a full Go CLI project (includes GoReleaser)
- [All plugins](../../README.md)
