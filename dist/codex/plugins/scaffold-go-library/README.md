# Scaffold Go Library

Scaffold a Go library project with GoReleaser changelog-only releases, golangci-lint, GitHub Actions CI/CD, and Makefile.

**Type:** Skill
**Trigger:** `/scaffold-go-library`

## What It Does

Generates the full boilerplate for a new Go library project: package source file, `doc.go`, `go.mod`, `Makefile`, `.gitignore`, `.goreleaser.yml`, `.golangci.yml`, `.editorconfig`, CI and release workflows, `LICENSE`, `README`, and a plans directory. Optionally generates example tests.

## Usage

```text
/scaffold-go-library
```

The skill prompts for project name, description, minimum Go version, and whether to include example tests during setup.

## Examples

- "scaffold go library" -- starts the interactive scaffolding process
- "new go package" -- same behavior
- "create go library" -- same behavior

## See Also

- [Scaffold Go CLI](../scaffold-go-cli/README.md) -- scaffold a Go CLI project with Cobra and Homebrew
- [Scaffold New Repo](../scaffold-new-repo/README.md) -- language-agnostic repo boilerplate
- [Write Go Code](../write-go-code/README.md) -- Go style guide for writing code in the new project
- [All plugins](../../../../README.md)
