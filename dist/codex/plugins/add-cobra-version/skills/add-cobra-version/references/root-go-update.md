# cmd/root.go Modifications

`cmd/root.go` owns the package-level `version`, `commit`, and `date` variables used by `cmd/version.go` and any other command that needs build metadata. It also exposes the `SetVersionInfo` setter that `main.go` calls at startup.

## Target State

After the modifications, the relevant portions of `cmd/root.go` should look like the snippet below. Other content in the file (flag wiring, `init()`, custom usage templates, etc.) is preserved.

```go
package cmd

import "github.com/spf13/cobra"

var (
	// Version info populated at startup by SetVersionInfo (called from main).
	version = "dev"
	commit  = "none"
	date    = "unknown"
)

var rootCmd = &cobra.Command{
	Use:           "PROJECT-NAME",
	Short:         "PROJECT-DESCRIPTION",
	Version:       version,
	SilenceUsage:  true,
	SilenceErrors: true,
}

// Execute runs the root command.
func Execute() error {
	return rootCmd.Execute()
}

// SetVersionInfo sets the build metadata reported by the version subcommand
// and Cobra's built-in --version flag. Call from main.go after parsing
// ldflags-injected variables.
func SetVersionInfo(v, c, d string) {
	version = v
	commit = c
	date = d
	rootCmd.Version = v
}
```

## Edit Strategy

The file usually already has most of this content (from `scaffold-go-cli` or hand-rolled). Apply only the parts that are missing.

1. **Variable block.** Find the existing `var version` declaration (if any). Promote it into a `var ( ... )` block that also declares `commit = "none"` and `date = "unknown"`. If `commit` and `date` are already declared, leave them alone.
1. **`SetVersion` -> `SetVersionInfo`.** If a `SetVersion(v string)` function exists, replace it with `SetVersionInfo(v, c, d string)` as shown above. Update any in-package callers; `main.go` is updated separately in `./main-go-update.md`.
1. **`Version: version` field on `rootCmd`.** Keep it if it exists. `SetVersionInfo` overwrites it at startup, but having a default lets `--version` print `dev` on local builds even before `SetVersionInfo` runs (for example in tests that exercise the root command directly).
1. **Imports.** No new imports are needed beyond `github.com/spf13/cobra`.

## Notes

- The default values (`"dev"`, `"none"`, `"unknown"`) match the pattern used by `bopca` and several reference Cobra CLIs. They make local-build output unambiguous: anyone seeing `commit: none` immediately understands the binary was not built through GoReleaser or `make build`.
- Do not move the variables to a new `cmd/version_info.go` file; keeping them in `cmd/root.go` puts them next to `rootCmd` (which they configure via `SetVersionInfo`), and matches the existing single-file layout produced by `scaffold-go-cli`.
- If the project uses Viper or other initialization in `cmd/root.go`, leave that code untouched. The variable block and `SetVersionInfo` can sit alongside it.
