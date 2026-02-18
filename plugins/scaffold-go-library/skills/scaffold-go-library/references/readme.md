# README.md Template

Use this template for the project `README.md`. Replace `PROJECT-NAME` (kebab-case), `PROJECT-TITLE` (title case), `PROJECT-DESCRIPTION`, `GITHUB-USERNAME`, and `PACKAGE-NAME` with the actual values.

````markdown
# PROJECT-TITLE

PROJECT-DESCRIPTION

## Installation

```sh
go get github.com/GITHUB-USERNAME/PROJECT-NAME
```

## Usage

```go
package main

import (
	"fmt"

	"github.com/GITHUB-USERNAME/PROJECT-NAME"
)

func main() {
	fmt.Println(PACKAGE-NAME.Version)
}
```

## Development

```sh
git clone https://github.com/GITHUB-USERNAME/PROJECT-NAME.git
cd PROJECT-NAME
make all
```

Run `make help` to see all available targets.

## License

[MIT License](./LICENSE). TL;DR: Do whatever you want with this software, just keep the copyright notice included. The authors aren't liable if something goes wrong.
````

## Notes

- The heading uses the project name in title case (e.g., "Stipple", "My Lib")
- Installation uses `go get` (the standard way to add a Go library dependency)
- The usage example shows a minimal import and usage of the package
- The development section covers cloning and running the full quality pipeline
- Replace `PACKAGE-NAME` in the usage example with the actual package name (hyphens removed)
- License section uses the standard MIT license wording
