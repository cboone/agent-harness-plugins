# Cobra CLI Commands

Cobra command trees need one extra review pass because help output is user-facing behavior, not only style. When editing a Cobra root command, check whether it is both runnable and a command group.

## Detect runnable roots with subcommands

A Cobra command is affected when all of these are true:

- The root command is a `*cobra.Command`.
- The root command has `Run` or `RunE`.
- The command tree registers subcommands with `AddCommand`.

Without a custom usage template, Cobra's default template prints separate usage lines:

```text
Usage:
  myapp [flags]
  myapp [command]
```

For a runnable root with subcommands, prefer one combined line:

```text
Usage:
  myapp [command] [flags]
```

## Add a version-compatible usage template

Do not paste a full Cobra default usage template from another project or a newer Cobra release. Cobra has changed template fields over time, and fields such as command groups may not exist in older versions. Instead, start from the project's installed Cobra default template and replace only the top `Usage:` block.

Use `.UseLine()` when constructing the runnable command form. It preserves positional arguments from the command's `Use` string, such as `myapp [file]`.

```go
package cmd

import (
	"strings"

	"github.com/spf13/cobra"
)

const defaultUsageBlock = `Usage:{{if .Runnable}}
  {{.UseLine}}{{end}}{{if .HasAvailableSubCommands}}
  {{.CommandPath}} [command]{{end}}`

const combinedUsageBlock = `Usage:{{if or .Runnable .HasAvailableSubCommands}}
  {{combinedUseLine .}}{{end}}`

func init() {
	cobra.AddTemplateFunc("combinedUseLine", combinedUseLine)
	rootCmd.SetUsageTemplate(strings.Replace(rootCmd.UsageTemplate(), defaultUsageBlock, combinedUsageBlock, 1))
	rootCmd.AddCommand(newServeCommand())
}

func combinedUseLine(cmd *cobra.Command) string {
	if !cmd.Runnable() {
		return cmd.CommandPath() + " [command]"
	}

	useLine := cmd.UseLine()
	if !cmd.HasAvailableSubCommands() {
		return useLine
	}

	useLine = strings.TrimSuffix(useLine, " [flags]")
	if cmd.HasAvailableFlags() {
		return useLine + " [command] [flags]"
	}

	return useLine + " [command]"
}
```

If `strings.Replace` does not match because the project has already customized `UsageTemplate()`, inspect the local template and make the same narrow edit to its `Usage:` block. Keep all other sections from the project's current template intact.

## Expected usage forms

The template should produce these forms:

| Command shape                         | Usage line                         |
| ------------------------------------- | ---------------------------------- |
| Runnable with subcommands             | `myapp [command] [flags]`          |
| Runnable with subcommands and args    | `myapp [file] [command] [flags]`   |
| Runnable with no subcommands          | Cobra's existing `.UseLine()`      |
| Non-runnable with subcommands         | `myapp [command]`                  |
| Non-runnable with no subcommands      | no usage line                      |

## Verify help output

When applying this guidance, run the CLI help for the root command and at least one child command:

```bash
go run . --help
go run . child --help
```

Confirm that the root usage has one line, flags still render, subcommands still render, and grouped command sections still render if the project uses Cobra command groups.
