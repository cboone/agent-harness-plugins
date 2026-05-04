# main.go Modifications

`main.go` declares the three `version`, `commit`, and `date` package-level variables that GoReleaser and the Makefile inject via `-X main.<name>=...` ldflags. It then calls `cmd.SetVersionInfo` to forward those values into the `cmd` package before running the CLI.

## Target State

After the modifications, the relevant portion of `main.go` should look like:

```go
package main

import (
	"fmt"
	"os"

	"github.com/GITHUB-USERNAME/PROJECT-NAME/cmd"
)

// Build metadata, populated at link time via -X ldflags.
var (
	version = "dev"
	commit  = "none"
	date    = "unknown"
)

func main() {
	cmd.SetVersionInfo(version, commit, date)
	if err := cmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %s\n", err)
		os.Exit(1)
	}
}
```

The exact `func main()` body may differ in real projects (signal handling, status-line cleanup, exit-code mapping). Preserve all of that. The two non-negotiable shape elements are:

1. The `version`, `commit`, and `date` package-level variables.
1. A `cmd.SetVersionInfo(version, commit, date)` call before `cmd.Execute()`.

## Edit Strategy

1. **Variable block.** If `var version = "dev"` already exists, promote it into a `var ( ... )` block (or an existing one) that also declares `commit = "none"` and `date = "unknown"`. If `commit` and `date` are already declared, leave them alone.
1. **`cmd.SetVersion(version)` -> `cmd.SetVersionInfo(version, commit, date)`.** Replace any existing `cmd.SetVersion(version)` call with `cmd.SetVersionInfo(version, commit, date)`. If no such call exists, insert `cmd.SetVersionInfo(version, commit, date)` immediately before `cmd.Execute()`.
1. **Imports.** No new imports are needed; `cmd` is already imported in any project that uses Cobra in this layout.

## Notes

- Ldflags target `main.<name>` because the variables live in `package main`. The `cmd` package receives the values through the `SetVersionInfo` call rather than via separate `-X` entries. This avoids needing to know the full module path in `.goreleaser.yml` and the Makefile.
- Defaults of `"dev"`, `"none"`, `"unknown"` make it obvious when a binary was built without ldflags (`go run .`, plain `go build .`).
- If the project has additional initialization in `main` (signal handling, output cleanup), leave it. `SetVersionInfo` is cheap and safe to call at any point before `Execute`; placing it as the first line of `main()` is conventional but not required.
