# Add Cobra Version

Add a `version` subcommand with full build metadata to an existing Cobra-based Go CLI.

**Type:** Skill
**Trigger:** `/add-cobra-version`

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Generates a `cmd/version.go` and coordinates the matching ldflags wiring across `main.go`, `cmd/root.go`, `.goreleaser.yml`, and the `Makefile` so a Cobra CLI can report:

- Version (from git tag, falling back to `"dev"`)
- Commit hash (short)
- Build date (UTC, ISO 8601)
- Go runtime version (from `runtime.Version()`)

Output is human-readable by default with an optional `--json` flag for scripts. Cobra's built-in `--version` flag continues to work and reports the same version string.

## Usage

```text
/add-cobra-version
```

The skill detects the project's existing version wiring (basic `var version` only versus full `version`/`commit`/`date`) and then:

- Adds `cmd/version.go` (skips or asks before overwriting if one already exists).
- Adds package-level `commit` and `date` variables to `cmd/root.go` alongside `version`, exposing a `SetVersionInfo(v, c, d string)` helper. If only `SetVersion` exists, it is replaced.
- Adds `commit` and `date` package-level vars to `main.go` and updates the call to `cmd.SetVersionInfo`.
- Extends GoReleaser `ldflags` to include `-X main.commit={{.ShortCommit}}` and `-X main.date={{.Date}}`.
- Extends the Makefile `LDFLAGS` to include matching `-X` entries plus `COMMIT` and `DATE` variables.

## Examples

- "add a version subcommand to this CLI": detects state and wires everything up
- "wire up version, commit, and date ldflags": same behavior
- "add `--json` to the version command": same behavior, ensures the `--json` flag is present

## See Also

- [Scaffold Go CLI](../scaffold-go-cli/README.md): scaffolding a brand-new Go CLI (starts with the basic `version` variable).
- [Add GoReleaser Homebrew](../add-goreleaser-homebrew/README.md): adding GoReleaser and the release workflow when those are missing too.
- [All plugins](../../../../README.md)
