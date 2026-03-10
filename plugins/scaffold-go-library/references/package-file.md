# Package File Template

Use this template for `PACKAGE-NAME.go`, the main package source file. Replace `PACKAGE-NAME` with the derived package name (project name with hyphens removed).

```go
package PACKAGE-NAME

// Version is the current version of PACKAGE-NAME.
const Version = "0.0.0-dev"
```

## Notes

- The `Version` constant provides a programmatic way to check the library version
- No doc comment on this file -- the canonical package doc lives in `doc.go`
- The initial version is `0.0.0-dev` to indicate pre-release status
- Users will add their library's exported API to this file (or additional files in the same package)
