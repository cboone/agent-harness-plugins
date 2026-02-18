# Add GoReleaser Homebrew

Add GoReleaser configuration and a GitHub Actions release workflow to an existing Go CLI project with Homebrew tap publishing.

**Type:** Skill
**Trigger:** `/add-goreleaser-homebrew`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Add GoReleaser Homebrew** from the available plugins.

## What It Does

Generates a `.goreleaser.yml` and a `.github/workflows/release.yml` for an existing Go CLI project. Detects shell completions, man page generation, and macOS-only build constraints, then conditionally adjusts the configuration. Optionally adds a `release-dry-run` Makefile target.

## Usage

```text
/add-goreleaser-homebrew
```

The skill prompts for project details and confirms detected features before generating files.

## Examples

- "add goreleaser": detects project features and generates release configuration
- "set up homebrew tap": same behavior
- "add release workflow": same behavior

## See Also

- [Scaffold Go CLI](../scaffold-go-cli/README.md): scaffold a new Go CLI project (includes GoReleaser from the start)
- [All plugins](../../README.md)
