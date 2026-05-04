# Overlap Rules

When multiple scaffolding and setup tools apply to the same project, some include functionality that others also provide. These rules prevent duplicate work by specifying which tools to skip or scope down when another tool covers their output.

## Decision Table

Each row reads as: "If **Tool A** will run, then apply **Action** to **Tool B**, because **Reason**."

| Tool A                  | Tool B                    | Action         | Reason                                                                                                   |
| ----------------------- | ------------------------- | -------------- | -------------------------------------------------------------------------------------------------------- |
| `scaffold-go-cli`       | `setup-ci`                | Skip           | `scaffold-go-cli` generates `.github/workflows/ci.yml` and Makefile                                      |
| `scaffold-go-cli`       | `add-goreleaser-homebrew` | Skip           | `scaffold-go-cli` generates `.goreleaser.yml` and release workflow                                       |
| `scaffold-go-cli`       | `setup-linters`           | Scope down     | Makefile lint target exists; add `.golangci.yml` and cross-language tools                                |
| `scaffold-go-cli`       | `scaffold-new-repo`       | Scope down     | `scaffold-go-cli` generates LICENSE, README, .gitignore; still run for agent config files                |
| `scaffold-go-library`   | `setup-ci`                | Skip           | `scaffold-go-library` generates CI workflow and Makefile                                                 |
| `scaffold-go-library`   | `setup-linters`           | Scope down     | `.golangci.yml` is configured; only add cross-language tools                                             |
| `scaffold-go-library`   | `scaffold-new-repo`       | Scope down     | `scaffold-go-library` generates LICENSE, README, .gitignore; still run for agent config files            |
| `scaffold-lean-library` | `setup-ci`                | Skip           | `scaffold-lean-library` generates Lean CI, text lint CI, and Makefile                                    |
| `scaffold-lean-library` | `setup-linters`           | Scope down     | Lean lint, Markdown lint, spelling config, and text lint CI are generated; only add selected refinements |
| `scaffold-lean-library` | `scaffold-new-repo`       | Scope down     | `scaffold-lean-library` generates LICENSE, README, .gitignore, AGENTS.md, and Copilot instructions       |
| `scaffold-lean-library` | `add-goreleaser-homebrew` | Not applicable | Lean libraries do not publish GoReleaser or Homebrew binaries                                            |
| `scaffold-lean-library` | `setup-installers`        | Not applicable | Lean libraries do not produce distributable CLI binaries                                                 |
| `scaffold-lean-library` | `add-scrut-cli-tests`     | Not applicable | Lean libraries use compile-time API regression tests, not scrut CLI tests                                |
| `scaffold-rust-cli`     | `setup-ci`                | Skip           | `scaffold-rust-cli` generates CI workflow and Makefile                                                   |
| `scaffold-rust-cli`     | `setup-linters`           | Scope down     | Rust linting configured; add cross-language tools                                                        |
| `scaffold-rust-cli`     | `scaffold-new-repo`       | Scope down     | `scaffold-rust-cli` generates LICENSE, README, .gitignore; still run for agent config files              |

Tool applicability (e.g., CLI-only tools not running on libraries) is defined in the **Applicability Rules** section below.

## Independent Tools

These tools have no overlap with any other tool and always run when applicable:

- **`setup-secret-scanning`**: Secret scanning workflows are unique to this tool.

## Scope-Down Details

### setup-linters after scaffold-go-library

`scaffold-go-library` generates `.golangci.yml` with full linter configuration. Skip Go-specific tools and only install cross-language tools:

- Prettier
- EditorConfig
- markdownlint-cli2
- Any other file-type-specific tools detected (Actionlint, yamllint, Hadolint, etc.)

### setup-linters after scaffold-go-cli

`scaffold-go-cli` adds a Makefile `lint` target that calls `golangci-lint` but does not generate a `.golangci.yml` config file. Install `.golangci.yml` configuration plus cross-language tools.

### scaffold-new-repo after a Go scaffolder

Both `scaffold-go-cli` and `scaffold-go-library` generate LICENSE, README, .gitignore, and CHANGELOG. When scoped down, `scaffold-new-repo` should only generate agent config files:

- `AGENTS.md`
- `CLAUDE.md` (symlink to AGENTS.md)
- `.claude/settings.json`
- `.github/copilot-instructions.md`

### setup-linters after scaffold-rust-cli

`scaffold-rust-cli` generates `rustfmt.toml`, `deny.toml`, `typos.toml`, and configures clippy in the Makefile and CI. Skip Rust-specific tools and only install cross-language tools:

- Prettier
- EditorConfig
- markdownlint-cli2
- Any other file-type-specific tools detected (Actionlint, yamllint, Hadolint, etc.)

### scaffold-new-repo after scaffold-rust-cli

`scaffold-rust-cli` generates LICENSE, README, .gitignore, and CHANGELOG. When scoped down, `scaffold-new-repo` should only generate agent config files:

- `AGENTS.md`
- `CLAUDE.md` (symlink to AGENTS.md)
- `.claude/settings.json`
- `.github/copilot-instructions.md`

### setup-linters after scaffold-lean-library

`scaffold-lean-library` generates `lintDriver = "batteries/runLinter"`, the `_check-mathlib-cache` and `lean-lint` Makefile targets, baseline markdownlint and cspell configs, and split Lean/text CI workflows. Skip Lean linter wiring and do not create another CI workflow. Only add selected refinements:

- Additional cross-language tools the user explicitly selected and the Lean scaffolder did not generate
- Pandoc-academic preset refinements for paper-backed projects when the user selected them after scaffolding
- Updates to existing lint configs if the project was not freshly scaffolded

### scaffold-new-repo after scaffold-lean-library

`scaffold-lean-library` generates LICENSE, README, CHANGELOG, .gitignore, `AGENTS.md`, a safe `CLAUDE.md` symlink, and `.github/copilot-instructions.md`. When scoped down, `scaffold-new-repo` should only generate missing agent/config extras that the Lean scaffolder did not create, typically:

- `.claude/settings.json`

## Applicability Rules

Some tools only apply to certain project types:

| Tool                      | Applicable when                                                                |
| ------------------------- | ------------------------------------------------------------------------------ |
| `scaffold-go-cli`         | Go CLI project (go.mod + main.go or cmd/)                                      |
| `scaffold-go-library`     | Go library project (go.mod, no main.go or cmd/)                                |
| `scaffold-lean-library`   | Lean library or formalization project without Lean executable targets          |
| `scaffold-rust-cli`       | Rust CLI project (Cargo.toml + src/main.rs, src/bin/*.rs, or `[[bin]]` target) |
| `add-goreleaser-homebrew` | Go CLI project without existing GoReleaser                                     |
| `setup-installers`        | Project produces a distributable binary (CLI)                                  |
| `add-scrut-cli-tests`     | Project produces a CLI binary                                                  |
| `setup-ci`                | Any project without existing CI workflow                                       |
| `setup-linters`           | Any project                                                                    |
| `setup-secret-scanning`   | Any project                                                                    |
| `scaffold-new-repo`       | Any project missing foundational files                                         |
