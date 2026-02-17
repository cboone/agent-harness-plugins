# cmd/root.go Template (With Viper)

Use this template when the user **does** want Viper config management. Replace `PROJECT-NAME` and `PROJECT-DESCRIPTION` with the actual values.

```go
package cmd

import (
	"errors"
	"os"
	"path/filepath"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var (
	cfgFile string
	rootCmd = &cobra.Command{
		Use:           "PROJECT-NAME",
		Short:         "PROJECT-DESCRIPTION",
		SilenceUsage:  true,
		SilenceErrors: true,
	}
)

// Execute runs the root command.
func Execute() error {
	return rootCmd.Execute()
}

// SetVersion sets the version string on the root command.
func SetVersion(v string) {
	rootCmd.Version = v
}

func init() {
	cobra.OnInitialize(initConfig)
	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default: ~/.config/PROJECT-NAME/config.yaml)")
}

func initConfig() {
	if cfgFile != "" {
		viper.SetConfigFile(cfgFile)
	} else {
		home, err := os.UserHomeDir()
		if err == nil {
			viper.AddConfigPath(filepath.Join(home, ".config", "PROJECT-NAME"))
			viper.SetConfigName("config")
			viper.SetConfigType("yaml")
		}
	}

	viper.AutomaticEnv()

	if err := viper.ReadInConfig(); err != nil {
		var notFound viper.ConfigFileNotFoundError
		if !errors.As(err, &notFound) {
			// Only surface unexpected errors; missing config is fine.
			_ = err
		}
	}
}
```

## Notes

- Adds `--config` persistent flag for explicit config file path
- Default config location is `~/.config/PROJECT-NAME/config.yaml`
- `viper.AutomaticEnv()` binds environment variables automatically
- Missing config file is silently ignored (common for CLIs that work without config)
- The `PROJECT-NAME` in the config path and flag help should match the binary name
