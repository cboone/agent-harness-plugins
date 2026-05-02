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

## Add a combined usage template

Add a package-level template near the root command definition and install it in `init()`:

```go
const usageTemplate = `Usage:{{if or .Runnable .HasAvailableSubCommands}}
  {{.CommandPath}}{{if .HasAvailableSubCommands}} [command]{{end}}{{if .HasAvailableFlags}} [flags]{{end}}{{end}}{{if gt (len .Aliases) 0}}

Aliases:
  {{.NameAndAliases}}{{end}}{{if .HasExample}}

Examples:
{{.Example}}{{end}}{{if .HasAvailableSubCommands}}{{$cmds := .Commands}}{{if eq (len .Groups) 0}}

Available Commands:{{range $cmds}}{{if (or .IsAvailableCommand (eq .Name "help"))}}
  {{rpad .Name .NamePadding }} {{.Short}}{{end}}{{end}}{{else}}{{range $group := .Groups}}

{{.Title}}{{range $cmds}}{{if (and (eq .GroupID $group.ID) (or .IsAvailableCommand (eq .Name "help")))}}
  {{rpad .Name .NamePadding }} {{.Short}}{{end}}{{end}}{{end}}{{if not .AllChildCommandsHaveGroup}}

Additional Commands:{{range $cmds}}{{if (and (eq .GroupID "") (or .IsAvailableCommand (eq .Name "help")))}}
  {{rpad .Name .NamePadding }} {{.Short}}{{end}}{{end}}{{end}}{{end}}{{end}}{{if .HasAvailableLocalFlags}}

Flags:
{{.LocalFlags.FlagUsages | trimTrailingWhitespaces}}{{end}}{{if .HasAvailableInheritedFlags}}

Global Flags:
{{.InheritedFlags.FlagUsages | trimTrailingWhitespaces}}{{end}}{{if .HasHelpSubCommands}}

Additional help topics:{{range .Commands}}{{if .IsAdditionalHelpTopicCommand}}
  {{rpad .CommandPath .CommandPathPadding}} {{.Short}}{{end}}{{end}}{{end}}{{if .HasAvailableSubCommands}}

Use "{{.CommandPath}} [command] --help" for more information about a command.{{end}}
`

func init() {
	rootCmd.SetUsageTemplate(usageTemplate)
	rootCmd.AddCommand(newServeCommand())
}
```

Keep the rest of Cobra's default sections intact unless the project already has a local usage template. If a project has an existing custom template, preserve its local sections and adjust only the usage line logic.

## Expected usage forms

The template should produce these forms:

| Command shape                    | Usage line                |
| -------------------------------- | ------------------------- |
| Runnable with subcommands        | `myapp [command] [flags]` |
| Runnable with no subcommands     | `myapp [flags]`           |
| Non-runnable with subcommands    | `myapp [command]`         |
| Non-runnable with no subcommands | no usage line             |

## Verify help output

When applying this guidance, run the CLI help for the root command and at least one child command:

```bash
go run . --help
go run . child --help
```

Confirm that the root usage has one line, flags still render, subcommands still render, and grouped command sections still render if the project uses Cobra command groups.
