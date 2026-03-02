# Overlap Rules

When multiple scaffolding and setup tools apply to the same project, some include functionality that others also provide. These rules prevent duplicate work by specifying which tools to skip or scope down when another tool covers their output.

## Decision Table

Each row reads as: "If **Tool A** will run, then apply **Action** to **Tool B**, because **Reason**."

| Tool A                | Tool B                    | Action     | Reason                                                               |
| --------------------- | ------------------------- | ---------- | -------------------------------------------------------------------- |
| `scaffold-go-cli`     | `setup-ci`                | Skip       | `scaffold-go-cli` generates `.github/workflows/ci.yml` and Makefile  |
| `scaffold-go-cli`     | `add-goreleaser-homebrew` | Skip       | `scaffold-go-cli` generates `.goreleaser.yml` and release workflow   |
| `scaffold-go-cli`     | `setup-linters`           | Scope down | Go-specific linters are configured; only add cross-language tools    |
| `scaffold-go-cli`     | `scaffold-new-repo`       | Skip       | `scaffold-go-cli` generates LICENSE, README, .gitignore, agent files |
| `scaffold-go-library` | `setup-ci`                | Skip       | `scaffold-go-library` generates CI workflow and Makefile             |
| `scaffold-go-library` | `add-goreleaser-homebrew` | N/A        | Libraries do not produce binaries; GoReleaser is not applicable      |
| `scaffold-go-library` | `setup-installers`        | N/A        | Libraries do not produce binaries; installers are not applicable     |
| `scaffold-go-library` | `add-scrut-cli-tests`     | N/A        | Libraries do not produce a CLI; scrut tests are not applicable       |
| `scaffold-go-library` | `setup-linters`           | Scope down | Go-specific linters are configured; only add cross-language tools    |
| `scaffold-go-library` | `scaffold-new-repo`       | Skip       | `scaffold-go-library` generates LICENSE, README, .gitignore          |

## Independent Tools

These tools have no overlap with any other tool and always run when applicable:

- **`setup-gitleaks`**: Secret scanning workflow is unique to this tool.

## Scope-Down Details

When `setup-linters` is scoped down because a Go scaffolder already ran, skip Go-specific tools (`golangci-lint`) and only install cross-language tools:

- Prettier
- EditorConfig
- markdownlint-cli2
- Any other file-type-specific tools detected (Actionlint, yamllint, Hadolint, etc.)

## Applicability Rules

Some tools only apply to certain project types:

| Tool                      | Applicable when                                 |
| ------------------------- | ----------------------------------------------- |
| `scaffold-go-cli`         | Go CLI project (go.mod + main.go or cmd/)       |
| `scaffold-go-library`     | Go library project (go.mod, no main.go or cmd/) |
| `add-goreleaser-homebrew` | Go CLI project without existing GoReleaser      |
| `setup-installers`        | Project produces a distributable binary (CLI)   |
| `add-scrut-cli-tests`     | Project produces a CLI binary                   |
| `setup-ci`                | Any project without existing CI workflow        |
| `setup-linters`           | Any project                                     |
| `setup-gitleaks`          | Any project                                     |
| `scaffold-new-repo`       | Any project missing foundational files          |
