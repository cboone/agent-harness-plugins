# cmd/version.go Template

Use this template for the `version` subcommand. Replace `PROJECT-NAME` with the binary name as it should appear in the human-readable header (for example `bopca`, `right-round`). Replace `ROOT-COMMAND-VAR` with the root command variable identifier detected from the target project's `package cmd` root command declaration.

```go
package cmd

import (
	"encoding/json"
	"fmt"
	"runtime"

	"github.com/spf13/cobra"
)

type versionInfo struct {
	Version   string `json:"version"`
	Commit    string `json:"commit"`
	Date      string `json:"date"`
	GoVersion string `json:"goVersion"`
}

var versionJSON bool

var versionCmd = &cobra.Command{
	Use:   "version",
	Short: "Print version information",
	Long:  `Print version information for PROJECT-NAME, including the commit hash, build date, and Go runtime version.`,
	RunE: func(cmd *cobra.Command, _ []string) error {
		info := versionInfo{
			Version:   version,
			Commit:    commit,
			Date:      date,
			GoVersion: runtime.Version(),
		}

		out := cmd.OutOrStdout()

		if versionJSON {
			encoded, err := json.MarshalIndent(info, "", "  ")
			if err != nil {
				return fmt.Errorf("encode version info: %w", err)
			}
			fmt.Fprintln(out, string(encoded))
			return nil
		}

		fmt.Fprintf(out, "PROJECT-NAME %s\n", info.Version)
		fmt.Fprintf(out, "  commit: %s\n", info.Commit)
		fmt.Fprintf(out, "  built:  %s\n", info.Date)
		fmt.Fprintf(out, "  go:     %s\n", info.GoVersion)
		return nil
	},
}

func init() {
	versionCmd.Flags().BoolVar(&versionJSON, "json", false, "Output version information as JSON")
	ROOT-COMMAND-VAR.AddCommand(versionCmd)
}
```

## Notes

- The `version`, `commit`, and `date` package-level variables come from `cmd/root.go` (see `./root-go-update.md`). They are populated at startup by `SetVersionInfo`, called from `main.go` (see `./main-go-update.md`).
- `runtime.Version()` is read at execution time, so the Go runtime version always matches the binary's actual toolchain. There is no need to inject it via ldflags.
- Output is written to `cmd.OutOrStdout()` so tests can capture it with the root command's `SetOut(...)` method.
- The JSON encoder uses indented output to keep the human-piping case (`<binary> version --json | jq`) readable while still being machine-parseable.
- Cobra's built-in `--version` flag (set on the root command via `SetVersionInfo`) continues to work and emits a single-line "PROJECT-NAME version VERSION" string. The subcommand exists for the richer multi-line output.
- Project-specific commands (for example bopca's `output.Print`) are intentionally not used here. Use plain `fmt.Fprintf` so the subcommand has no extra dependencies and can drop into any Cobra project.
