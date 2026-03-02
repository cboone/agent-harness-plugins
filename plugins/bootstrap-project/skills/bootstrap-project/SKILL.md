---
name: bootstrap-project
description: >-
  Assess a repository, determine what scaffolding and setup tools are needed,
  present a plan, and execute them in the correct order.
---

# Bootstrap Project

Assess the current repository, detect what scaffolding and setup is already in place, build a plan of which tools to run, get user approval, and execute everything in the correct order.

Works for both brand-new and existing repositories.

## Workflow

### 1. Detect Project Type

Scan for language and framework markers using Glob. Exclude `node_modules/`, `.yarn/`, `vendor/`, and other dependency directories from all searches.

| Marker(s)                                            | Project type          |
| ---------------------------------------------------- | --------------------- |
| `go.mod` + (`main.go` or `cmd/`)                     | Go CLI                |
| `go.mod` without `main.go` or `cmd/`                 | Go library            |
| `package.json` + JS/TS source files                  | JavaScript/TypeScript |
| `pyproject.toml`, `setup.py`, `requirements.txt`     | Python                |
| `Cargo.toml`                                         | Rust                  |
| `Gemfile`, `*.gemspec`                                | Ruby                  |
| `*.sh`, `bin/*`, `scripts/*`                         | Shell                 |
| No recognizable files                                | New/empty repo        |

If no recognizable files are found, ask the user what type of project they intend to create.

If multiple types are detected (monorepo), note all of them.

### 2. Detect Existing Infrastructure

Check for files and directories that indicate what is already set up:

| Check                                | Indicates                | Typically provided by              |
| ------------------------------------ | ------------------------ | ---------------------------------- |
| `LICENSE`                            | License exists           | `scaffold-new-repo`                |
| `README.md`                          | README exists            | `scaffold-new-repo`                |
| `CHANGELOG.md`                       | Changelog exists         | `scaffold-new-repo`                |
| `AGENTS.md` or `CLAUDE.md`          | Agent config exists      | `scaffold-new-repo`                |
| `.github/workflows/ci.yml`          | CI exists                | `setup-ci` / `scaffold-go-*`      |
| `.github/workflows/release.yml`     | Release workflow exists  | `scaffold-go-*` / `add-goreleaser-homebrew` |
| `.github/workflows/gitleaks.yml`    | Gitleaks exists          | `setup-gitleaks`                   |
| `.goreleaser.yml`                    | GoReleaser exists        | `scaffold-go-cli` / `add-goreleaser-homebrew` |
| `Makefile`                           | Build targets exist      | `scaffold-go-*` / `setup-ci`      |
| Linter config files                 | Linters exist            | `setup-linters` / `scaffold-go-*` |
| `tests/scrut/`                      | Scrut tests exist        | `add-scrut-cli-tests`              |
| `install.sh` or `Formula/`          | Installers exist         | `setup-installers`                 |

### 3. Build the Plan

Determine which tools to run based on the project type, existing infrastructure, and the overlap rules in `./references/overlap-rules.md`. Read that file for the full decision table.

Key overlap rules:

- If `scaffold-go-cli` will run: skip `setup-ci`, skip `add-goreleaser-homebrew` (both are included), skip `scaffold-new-repo` (included).
- If `scaffold-go-library` will run: skip `setup-ci` (included), skip `scaffold-new-repo` (included). `add-goreleaser-homebrew` and `setup-installers` are not applicable for libraries.
- If a Go scaffolder runs: still run `setup-linters` but only for cross-language tools (Prettier, EditorConfig, markdownlint) since Go-specific linters are already configured.
- `setup-gitleaks` is always independent (no overlap with other tools).
- `add-scrut-cli-tests` is applicable only if the project produces a CLI binary.

Execution order (dependencies flow downward):

1. `scaffold-new-repo` (foundation: LICENSE, README, .gitignore, agent config)
2. `scaffold-go-cli` OR `scaffold-go-library` (language-specific scaffolding, if applicable)
3. `setup-ci` (if not already covered by step 2)
4. `setup-linters` (cross-language tools, or full setup if no Go scaffolder ran)
5. `setup-gitleaks` (secret scanning)
6. `add-goreleaser-homebrew` (if Go CLI and not already covered by step 2)
7. `setup-installers` (if CLI project)
8. `add-scrut-cli-tests` (if CLI project)

### 4. Present the Plan

Show the user a table with each tool and its status. Use these status values:

| Status           | Meaning                                                   |
| ---------------- | --------------------------------------------------------- |
| Will run         | Tool is needed and will be invoked                        |
| Scoped down      | Tool will run with a reduced scope (see overlap rules)    |
| Already set up   | Infrastructure already exists; nothing to do              |
| Skipped          | Another tool covers this functionality                    |
| Not applicable   | Tool does not apply to this project type                  |

Example output:

```text
| #   | Tool                     | Status         | What it does                                |
| --- | ------------------------ | -------------- | ------------------------------------------- |
| 1   | scaffold-new-repo        | Already set up | LICENSE, README, .gitignore, agent config   |
| 2   | scaffold-go-cli          | Already set up | Go CLI project structure, CI, GoReleaser    |
| 3   | setup-ci                 | Skipped        | Covered by scaffold-go-cli                  |
| 4   | setup-linters            | Scoped down    | Cross-language tools only (Prettier, etc.)  |
| 5   | setup-gitleaks           | Will run       | Gitleaks secret scanning workflow           |
| 6   | add-goreleaser-homebrew  | Skipped        | Covered by scaffold-go-cli                  |
| 7   | setup-installers         | Will run       | Homebrew formula, install.sh                |
| 8   | add-scrut-cli-tests      | Will run       | Scrut CLI integration tests                 |
```

Ask the user to confirm the plan. They may:

- Deselect items they do not want
- Add items that were marked as skipped or not applicable

Wait for explicit approval before proceeding.

### 5. Execute

Invoke each confirmed tool in order using the Skill tool. Each tool is registered as a slash command (e.g., `/scaffold-new-repo`, `/setup-ci`).

Between each invocation:

1. Verify the tool completed successfully.
2. If a tool fails, report the error to the user and ask whether to continue with the remaining tools or stop.

When invoking `setup-linters` in scoped-down mode, tell it to skip language-specific linters that the Go scaffolder already configured and only set up cross-language tools.

### 6. Summary

After all tools have run, print a summary:

- List everything that was set up, grouped by tool.
- Note any issues encountered during execution.
- Suggest next steps:
  - Run `/lint-and-fix` to fix any initial linting issues.
  - Make an initial commit if the repo is new.
  - Push to the remote and verify CI passes.

## Error Handling

- **Empty repository with no user input**: If the repo is empty and the user does not specify a project type, ask before proceeding. Do not assume a type.
- **Tool invocation failure**: Report the error, ask whether to continue with remaining tools, and note the failure in the final summary.
- **Partial infrastructure**: If some files exist but are incomplete (e.g., a CI workflow exists but is missing lint jobs), note this in the plan and let the relevant tool handle it.
- **User declines all tools**: If the user deselects everything, confirm and stop gracefully.
