# main.go Template

Use this template for the root `main.go` file. Replace `PROJECT-NAME` with the actual project name.

```go
package main

import (
	"fmt"
	"os"

	"github.com/GITHUB-USERNAME/PROJECT-NAME/cmd"
)

var version = "dev"

func main() {
	cmd.SetVersion(version)
	if err := cmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %s\n", err)
		os.Exit(1)
	}
}
```

## Notes

- The `version` variable is injected at build time via ldflags (`-X main.version=...`)
- The default value `"dev"` is used during local development
- `cmd.SetVersion()` passes the version to the Cobra root command
- Errors from `Execute()` are printed to stderr before exiting with code 1
