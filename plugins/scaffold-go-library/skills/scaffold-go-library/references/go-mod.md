# go.mod Template

Do not write `go.mod` manually. Initialize it with `go mod init`.

## Initialize

```bash
go mod init github.com/GITHUB-USERNAME/PROJECT-NAME
```

## Tidy

After all source files are written:

```bash
go mod tidy
```

## Notes

- The module path is always `github.com/GITHUB-USERNAME/PROJECT-NAME`
- Go libraries should start with no external dependencies (stdlib-only)
- Add dependencies only when the library genuinely needs them
- The Go version in `go.mod` is set automatically by `go mod init` based on the installed Go toolchain
- `go mod tidy` removes unused dependencies and adds missing ones
