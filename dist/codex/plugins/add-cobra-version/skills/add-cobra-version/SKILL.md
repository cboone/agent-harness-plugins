---
name: add-cobra-version
description: >-
  Add a version subcommand with build metadata (version, commit hash, build
  date, Go runtime version, optional JSON output) to an existing Cobra-based Go
  CLI, wiring up ldflags in main.go, the cmd package, GoReleaser, and the
  Makefile.
---

# Add Cobra Version

Add a `version` subcommand with version, commit hash, build date, and Go runtime version to an existing Cobra-based Go CLI, and coordinate the matching ldflags wiring across `main.go`, `cmd/root.go`, `.goreleaser.yml`, and the `Makefile`.

## Workflow

### 1. Verify the Project

Confirm the current directory is a Go CLI project with Cobra:

- `go.mod` exists. If not, abort with a message that this skill requires an existing Go module.
- A Cobra root command exists. Check for `cmd/root.go` (the canonical location used by `scaffold-go-cli`); if absent, grep for `&cobra.Command{` in `*.go` and `cmd/*.go`. If no Cobra command is found, abort: this skill is Cobra-specific.
- Read `go.mod` to extract the module path; needed when reasoning about ldflags `-X` targets.

### 2. Detect Current Version State

Determine which of three states the project is in. The state controls how aggressive the changes need to be.

1. **No version wiring**: no `var version` declaration in any Go source file.
1. **Basic version only**: `var version = "dev"` (or similar) exists, typically in `main.go` or `cmd/root.go`, but no `commit` or `date` variables.
1. **Full version info already present**: `version`, `commit`, and `date` package-level variables all exist.

Detection commands:

```bash
# Find version declarations across the project.
grep -rn 'var\s\+version\b' --include='*.go' .
grep -rn 'var\s\+commit\b' --include='*.go' .
grep -rn 'var\s\+date\b' --include='*.go' .
```

Also check for an existing version subcommand:

```bash
# Existing cmd/version.go file.
test -f cmd/version.go && echo "cmd/version.go exists"

# Existing version subcommand registration via &cobra.Command{ Use: "version", ... }.
grep -rn 'Use:\s*"version"' --include='*.go' .
```

If a `cmd/version.go` already exists, read it. Decide:

- If it already prints version, commit, date, and Go runtime version with a `--json` flag, treat it as up to date and skip step 5 (only continue with the wiring steps for any state still missing).
- Otherwise, ask the user whether to overwrite. If they decline, abort the skill.

### 3. Detect ldflags Target Package

The version variables can live in `package main` (`-X main.version=...`) or in the `cmd` package (`-X MODULE-PATH/cmd.version=...`). Pick a target convention:

1. If `var version` already exists in `main.go` or any file in `package main`, target `main`. The `cmd` package will receive the values via a `SetVersionInfo` call from `main`.
1. If `var version` exists only in the `cmd` package and `main.go` does not declare it, still target `main`: this skill standardizes on the `main`-declared, `cmd.SetVersionInfo`-injected pattern (it is the pattern produced by `scaffold-go-cli` and used by `bopca`). Plan to move the declaration into `main.go` and add the `commit`/`date` siblings there.
1. If no `version` declaration exists anywhere, target `main`: the skill will add the variables to `main.go`.

Record the chosen ldflags prefix (`main.`) and the resolved module path; both are used in steps 7 and 8.

### 4. Determine Project Name for Output Headers

The version subcommand prints a human-readable header that begins with the binary name (for example `bopca 1.2.3`). Determine the binary name in this precedence order:

1. The `Use` field on the Cobra root command (read from `cmd/root.go`). Strip any trailing argument hints, for example `Use: "bopca [flags]"` becomes `bopca`.
1. A `BINARY` or similar Makefile variable.
1. The last segment of the module path in `go.mod`.

Use the result wherever templates reference `PROJECT-NAME`.

### 5. Generate `cmd/version.go`

Read `./references/version-go.md` for the `cmd/version.go` template and create the file from it.

- Replace `PROJECT-NAME` with the binary name from step 4.
- Do not modify the file if step 2 found an up-to-date `cmd/version.go` and the user chose to keep it.

The generated subcommand:

- Prints version, commit, date, and `runtime.Version()` to `cmd.OutOrStdout()`.
- Accepts a `--json` flag for machine-readable output.
- Registers itself on `rootCmd` from its `init()` function, so no edits to `cmd/root.go` are required to wire it up.

### 6. Update `cmd/root.go`

Read `./references/root-go-update.md` for the modifications to apply.

If the file already declares the package-level variables (`version`, `commit`, `date`) and exposes a `SetVersionInfo(v, c, d string)` function, leave it alone.

Otherwise:

- Add (or extend) the package-level `var ( ... )` block to declare `version = "dev"`, `commit = "none"`, and `date = "unknown"`.
- Add a `SetVersionInfo(v, c, d string)` function that assigns the three variables and sets `rootCmd.Version = v` so Cobra's built-in `--version` flag still works. If a `SetVersion(v string)` function already exists, replace it with `SetVersionInfo`. If callers in `main.go` reference the old name, they will be updated in step 7.
- If the file currently sets `Version: version` directly on `rootCmd` and nothing else, leave that field in place; `SetVersionInfo` will overwrite it at startup.

### 7. Update `main.go`

Read `./references/main-go-update.md` for the modifications to apply.

If `main.go` already declares all three `version`, `commit`, `date` package-level variables and calls `cmd.SetVersionInfo(version, commit, date)` before `cmd.Execute()`, leave the file alone.

Otherwise:

- Ensure the package-level declarations include `version = "dev"`, `commit = "none"`, and `date = "unknown"`. Add missing siblings; do not remove unrelated variables.
- Replace any existing `cmd.SetVersion(version)` call with `cmd.SetVersionInfo(version, commit, date)`.
- If no `SetVersion`-style call exists yet, add `cmd.SetVersionInfo(version, commit, date)` immediately before `cmd.Execute()`.

### 8. Update `.goreleaser.yml`

Read `./references/goreleaser-update.md` for the modifications to apply.

GoReleaser may use `.goreleaser.yml` or `.goreleaser.yaml`. Check both. If neither exists, skip this step and note in the summary that GoReleaser is not configured (the user can run `/add-goreleaser-homebrew` to add it).

In the existing config, find the `builds[].ldflags` list. Ensure all three `-X` entries are present:

```yaml
- -X main.version={{.Version}}
- -X main.commit={{.ShortCommit}}
- -X main.date={{.Date}}
```

If `-X main.version=...` is already present, keep it. Add only the `-X` entries that are missing. Preserve any existing `-s -w` or other ldflags.

### 9. Update the Makefile

Read `./references/makefile-update.md` for the modifications to apply.

If no `Makefile` exists in the project root, skip this step and note in the summary.

Otherwise, ensure the Makefile defines:

- `VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")`
- `COMMIT ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo "none")`
- `DATE ?= $(shell date -u +%Y-%m-%dT%H:%M:%SZ)`

Then ensure `LDFLAGS` (or the equivalent variable already in use) contains the matching `-X` entries:

```makefile
LDFLAGS := -s -w \
	-X main.version=$(VERSION) \
	-X main.commit=$(COMMIT) \
	-X main.date=$(DATE)
```

Preserve any other flags already in `LDFLAGS`. Ensure the `build` target uses `$(LDFLAGS)` in its `go build` invocation; if it already uses a sub-variable, leave it alone.

### 10. Verify the Build

Run a quick build to confirm everything compiles and the new subcommand wires up cleanly:

```bash
go build ./...
```

If a Makefile build target now exists with the expanded ldflags, prefer:

```bash
make build
```

Then exercise the new command, ignoring exit code (the subcommand always exits 0 on success):

```bash
go run . version
go run . version --json
go run . --version
```

If any of those fail, inspect the error and fix the offending file before continuing.

### 11. Summary

Print a summary covering:

- Files created (`cmd/version.go`).
- Files modified (`main.go`, `cmd/root.go`, `.goreleaser.yml`, `Makefile`), one bullet each, noting whether the change was a clean add or a replacement of an existing `SetVersion`/`-X main.version` site.
- Skipped steps and why (for example "no GoReleaser config detected; run `/add-goreleaser-homebrew` to set one up").
- The three commands the user can now run: `<binary> version`, `<binary> version --json`, and `<binary> --version`.
- A reminder that local builds without ldflags will display `dev` / `none` / `unknown`, and that a tagged GoReleaser release is what fills in real values.

## Error Handling

- If `go.mod` is missing, abort: this skill requires an existing Go module.
- If no Cobra root command can be located, abort: this skill is Cobra-specific.
- If `cmd/version.go` already exists and the user declines to overwrite it, skip step 5 but continue with the remaining wiring steps so partial state is repaired.
- If the version variables are split between `main.go` and `cmd/root.go` in a way that conflicts (for example, both declare `var version` with different defaults), surface the conflict to the user and ask which file should own the canonical declarations before proceeding.
- If `go build ./...` fails after the edits, show the error and attempt to fix it; do not leave the project in a broken state.

## Reference Templates

- `./references/version-go.md` -- the `cmd/version.go` template.
- `./references/root-go-update.md` -- modifications to `cmd/root.go`.
- `./references/main-go-update.md` -- modifications to `main.go`.
- `./references/goreleaser-update.md` -- ldflags additions for `.goreleaser.yml`/`.goreleaser.yaml`.
- `./references/makefile-update.md` -- `VERSION`/`COMMIT`/`DATE` and `LDFLAGS` additions for the Makefile.
