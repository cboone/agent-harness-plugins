# Setup Installers

Set up installer and distribution methods for projects: Homebrew tap formula, shell install script with OS/arch detection, and go install compatibility.

**Type:** Command
**Trigger:** `/setup-installers`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Setup Installers** from the available plugins.

## What It Does

Detects existing release infrastructure (GoReleaser, GitHub Releases, existing install scripts) and generates appropriate distribution files. Supports three installer types:

- **Homebrew**: standalone tap formula, or defers to GoReleaser when already configured
- **Shell install script**: portable `install.sh` with OS/arch detection, GitHub Release download, and checksum verification
- **go install**: verifies module compatibility and adds README instructions

## Usage

```text
/setup-installers
```

Pass an argument to skip the selection prompt:

```text
/setup-installers homebrew
/setup-installers shell
/setup-installers go-install
```

## Examples

- `/setup-installers`: walks through all three installer types interactively
- `/setup-installers shell`: generates only the shell install script
- `/setup-installers homebrew`: sets up only Homebrew distribution

## See Also

- [Add GoReleaser Homebrew](../add-goreleaser-homebrew/README.md): add GoReleaser with Homebrew tap publishing (release pipeline)
- [Scaffold Go CLI](../scaffold-go-cli/README.md): scaffold a full Go CLI project (includes GoReleaser)
- [All plugins](../../README.md)
