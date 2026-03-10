# doc.go Template

Use this template for `doc.go`, the package-level documentation file. Replace `PACKAGE-NAME`, `PROJECT-DESCRIPTION`, `GITHUB-USERNAME`, and `PROJECT-NAME` with the actual values.

```go
// Package PACKAGE-NAME PROJECT-DESCRIPTION
//
// # Installation
//
//	go get github.com/GITHUB-USERNAME/PROJECT-NAME
package PACKAGE-NAME
```

## Notes

- This is the canonical location for the package-level doc comment (following Go convention)
- The first line follows the `// Package name ...` convention required by godoc
- The `PROJECT-DESCRIPTION` should start with a lowercase letter (it continues the "Package name" sentence)
- The `# Installation` section uses a godoc heading and an indented code block
- Keep doc.go focused on the package overview -- detailed API docs belong on exported symbols
