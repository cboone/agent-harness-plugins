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

For a runnable root with subcommands and no positional root arguments, prefer one combined line:

```text
Usage:
  myapp [command] [flags]
```

If the runnable root also accepts positional arguments in `Use`, keep the runnable-root form and subcommand form as separate alternatives. Do not document `myapp [file] [command] [flags]`, because Cobra treats the first non-flag token as either a root argument or a subcommand.

## Add a guarded usage-template replacement

Do not paste a full Cobra default usage template from another project or a newer Cobra release. Cobra has changed template fields over time, and fields such as command groups may not exist in older versions. Instead, start from the project's installed Cobra default template and replace only the top `Usage:` block.

Guard the replacement so template drift is visible. An unchecked `strings.Replace` can silently leave help output unchanged when the installed Cobra template differs from the example block.

Use `.UseLine()` when constructing the runnable command form. It preserves positional arguments from the command's `Use` string, such as `myapp [file]`, and respects options such as `DisableFlagsInUseLine`. Insert `[command]` before an existing `[flags]` suffix rather than adding `[flags]` yourself.

```go
package cmd

import (
	"fmt"
	"strings"

	"github.com/spf13/cobra"
)

const defaultUsageBlock = `Usage:{{if .Runnable}}
  {{.UseLine}}{{end}}{{if .HasAvailableSubCommands}}
  {{.CommandPath}} [command]{{end}}`

const combinedUsageBlock = `Usage:{{usageLines .}}`

func init() {
	cobra.AddTemplateFunc("usageLines", usageLines)
	if err := setUsageTemplate(rootCmd); err != nil {
		panic(err)
	}
	rootCmd.AddCommand(newServeCommand())
}

func setUsageTemplate(cmd *cobra.Command) error {
	usageTemplate := cmd.UsageTemplate()
	if !strings.Contains(usageTemplate, defaultUsageBlock) {
		return fmt.Errorf("unexpected Cobra usage template; update the Usage block replacement")
	}

	cmd.SetUsageTemplate(strings.Replace(usageTemplate, defaultUsageBlock, combinedUsageBlock, 1))
	return nil
}

func usageLines(cmd *cobra.Command) string {
	if !cmd.Runnable() {
		if cmd.HasAvailableSubCommands() {
			return "\n  " + cmd.CommandPath() + " [command]"
		}
		return ""
	}

	useLine := cmd.UseLine()
	if !cmd.HasAvailableSubCommands() {
		return "\n  " + useLine
	}

	if hasUseArgs(cmd) {
		return "\n  " + useLine + "\n  " + cmd.CommandPath() + " [command]"
	}

	return "\n  " + insertCommandInUseLine(useLine)
}

func hasUseArgs(cmd *cobra.Command) bool {
	return len(strings.Fields(cmd.Use)) > 1
}

func insertCommandInUseLine(useLine string) string {
	const flagsSuffix = " [flags]"
	if strings.HasSuffix(useLine, flagsSuffix) {
		return strings.TrimSuffix(useLine, flagsSuffix) + " [command]" + flagsSuffix
	}
	return useLine + " [command]"
}
```

If the guarded replacement fails because the project has already customized `UsageTemplate()`, inspect the local template and make the same narrow edit to its `Usage:` block. Keep all other sections from the project's current template intact.

## Expected usage forms

The template should produce these forms:

| Command shape                      | Usage line                                                      |
| ---------------------------------- | --------------------------------------------------------------- |
| Runnable with subcommands          | `myapp [command] [flags]`                                       |
| Runnable with subcommands and args | `myapp [file] [flags]` plus `myapp [command]` as separate lines |
| Runnable with no subcommands       | Cobra's existing `.UseLine()`                                   |
| Non-runnable with subcommands      | `myapp [command]`                                               |
| Non-runnable with no subcommands   | no usage line                                                   |

## Verify help output

When applying this guidance, run the CLI help for the root command and at least one child command:

```bash
go run . --help
go run . child --help
```

Confirm that the root usage has one line, flags still render, subcommands still render, and grouped command sections still render if the project uses Cobra command groups.
