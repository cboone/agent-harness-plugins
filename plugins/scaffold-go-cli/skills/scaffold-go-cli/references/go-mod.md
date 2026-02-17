# go.mod Template

Do not write `go.mod` manually. Initialize it with `go mod init`, then add dependencies with `go get`.

## Initialize

```bash
go mod init github.com/cboone/PROJECT-NAME
```

## Add Core Dependencies

Always add Cobra:

```bash
go get github.com/spf13/cobra@latest
```

## Add Optional Dependencies

### Viper (config management)

Only add if the user requested Viper:

```bash
go get github.com/spf13/viper@latest
```

### Charmbracelet TUI

Only add if the user requested TUI dependencies:

```bash
go get github.com/charmbracelet/bubbletea@latest
go get github.com/charmbracelet/lipgloss@latest
go get github.com/charmbracelet/bubbles@latest
```

## Tidy

After all dependencies are added:

```bash
go mod tidy
```

## Notes

- The module path is always `github.com/cboone/PROJECT-NAME`
- Use `@latest` to get the most recent stable version
- `go mod tidy` removes unused dependencies and adds missing ones
- The Go version in `go.mod` is set automatically by `go mod init` based on the installed Go toolchain
