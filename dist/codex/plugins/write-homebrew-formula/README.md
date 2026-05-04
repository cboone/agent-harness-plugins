# Write Homebrew Formula

Write or update Homebrew formulae using current Homebrew guidance and `cboone/homebrew-tap` conventions.

**Type:** Skill
**Trigger:** `/write-homebrew-formula`

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## Requirements

- [Homebrew](https://brew.sh/) for formula audit, style, install, and test validation.

## What It Does

Guides formula authoring for stable release formulae, HEAD-only pre-release formulae, Go source builds, GoReleaser-generated outputs, and shell tools with services or setup caveats. Uses `cboone/homebrew-tap` as the only cboone-specific pattern source, while treating official Homebrew documentation as the source for generic formula behavior.

## Usage

```text
/write-homebrew-formula
```

The skill gathers project metadata, selects the right formula pattern, writes or updates the Ruby formula, and validates the result with available Homebrew tooling.

## Examples

- "write a Homebrew formula for this Go CLI"
- "update this HEAD-only formula to a stable release"
- "review this formula against cboone/homebrew-tap conventions"
- "add caveats and a service block to this shell-tool formula"

## See Also

- [Add GoReleaser Homebrew](../add-goreleaser-homebrew/README.md): add GoReleaser with Homebrew tap publishing
- [Setup Installers](../setup-installers/README.md): set up standalone Homebrew distribution for a project
- [All plugins](../../../../README.md)
