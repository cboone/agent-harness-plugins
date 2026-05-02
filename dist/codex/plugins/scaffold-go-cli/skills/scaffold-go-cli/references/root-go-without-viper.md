# cmd/root.go Template (Without Viper)

Use this template when the user does **not** want Viper config management. Replace `PROJECT-NAME` and `PROJECT-DESCRIPTION` with the actual values.

```go
package cmd

import "github.com/spf13/cobra"

var rootCmd = &cobra.Command{
	Use:           "PROJECT-NAME",
	Short:         "PROJECT-DESCRIPTION",
	SilenceUsage:  true,
	SilenceErrors: true,
}

// Execute runs the root command.
func Execute() error {
	return rootCmd.Execute()
}

// SetVersion sets the version string on the root command.
func SetVersion(v string) {
	rootCmd.Version = v
}
```

## Notes

- `SilenceUsage: true` prevents Cobra from printing usage on every error
- `SilenceErrors: true` prevents Cobra from printing errors (the caller handles that)
- `SetVersion` receives the version from `main.go` where it is injected via ldflags
- The `Use` field is the binary name (what the user types to run the command)
