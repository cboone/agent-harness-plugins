---
name: bootstrap-project
description: >-
  Assess a repository, determine what scaffolding and setup tools are needed,
  present a plan, and execute them in the correct order. Use when the user says
  "bootstrap this project", "set up everything", "scaffold everything", "full
  project setup", or any variant involving bootstrapping or scaffolding an
  entire project.
---

# Bootstrap Project

Assess the current repository, detect what scaffolding and setup is already in place, build a plan of which tools to run, get user approval, and execute everything in the correct order.

Works for both brand-new and existing repositories.

## Workflow

### 1. Detect Project Type

Scan for language and framework markers using Glob. Exclude `node_modules/`, `.yarn/`, `.lake/`, `vendor/`, and other dependency directories from all searches.

| Marker(s)                                                                                           | Project type          |
| --------------------------------------------------------------------------------------------------- | --------------------- |
| `go.mod` + (`main.go` or `cmd/`)                                                                    | Go CLI                |
| `go.mod` without `main.go` or `cmd/`                                                                | Go library            |
| `package.json` + JS/TS source files                                                                 | JavaScript/TypeScript |
| `pyproject.toml`, `setup.py`, `requirements.txt`                                                    | Python                |
| `Cargo.toml` + (`src/main.rs`, `src/bin/*.rs`, or `[[bin]]` in Cargo.toml)                          | Rust CLI              |
| `Cargo.toml` without `src/main.rs`, `src/bin/*.rs`, or `[[bin]]`                                    | Rust library          |
| `lakefile.toml` or `lakefile.lean` with `[[lean_exe]]`, `lean_exe`, `Main.lean`, or user says CLI   | Lean CLI              |
| `lean-toolchain`, `lakefile.toml`, `lakefile.lean`, or `*.lean` without Lean CLI markers            | Lean library          |
| User says Lean formalization, Mathlib-downstream library, PFR downstream project, or theorem prover | Lean library          |
| `build.zig` + (`src/main.zig` or `src/`)                                                            | Zig CLI               |
| `Gemfile`, `*.gemspec`                                                                              | Ruby                  |
| `*.sh`, `bin/*`, `scripts/*`                                                                        | Shell                 |
| `*.zsh`, `#!/usr/bin/env zsh` shebangs, `.zshrc`, `.zshenv`                                         | Zsh                   |
| No recognizable files                                                                               | New/empty repo        |

If no recognizable files are found, ask the user what type of project they intend to create.

If multiple types are detected (monorepo), note all of them.

### 2. Detect Existing Infrastructure

Check for files and directories that indicate what is already set up:

| Check                              | Indicates               | Typically provided by                         |
| ---------------------------------- | ----------------------- | --------------------------------------------- |
| `LICENSE`                          | License exists          | `scaffold-new-repo`                           |
| `README.md`                        | README exists           | `scaffold-new-repo`                           |
| `CHANGELOG.md`                     | Changelog exists        | `scaffold-new-repo`                           |
| `AGENTS.md` or `CLAUDE.md`         | Agent config exists     | `scaffold-new-repo`                           |
| `.github/workflows/ci.yml`         | CI exists               | `set-up-ci` / `scaffold-go-*`                 |
| `.github/workflows/text-lint.yml`  | Text lint CI exists     | `scaffold-lean-library` / `set-up-linters`    |
| `.github/workflows/release.yml`    | Release workflow exists | `scaffold-go-*` / `add-goreleaser-homebrew`   |
| `.github/workflows/gitleaks.yml`   | Gitleaks exists         | `set-up-secret-scanning`                      |
| `.github/workflows/trufflehog.yml` | TruffleHog exists       | `set-up-secret-scanning`                      |
| `lean-toolchain`                   | Lean toolchain exists   | `scaffold-lean-library`                       |
| `lakefile.toml` or `lakefile.lean` | Lake package exists     | `scaffold-lean-library`                       |
| `bin/bootstrap-worktree`           | Lean bootstrap exists   | `scaffold-lean-library`                       |
| `.goreleaser.yml`                  | GoReleaser exists       | `scaffold-go-cli` / `add-goreleaser-homebrew` |
| `rustfmt.toml`                     | Rust formatter config   | `scaffold-rust-cli` / `set-up-linters`        |
| `deny.toml`                        | cargo-deny config       | `scaffold-rust-cli` / `set-up-linters`        |
| `typos.toml`                       | typos config            | `scaffold-rust-cli` / `set-up-linters`        |
| `cliff.toml`                       | git-cliff config        | `scaffold-rust-cli`                           |
| `Makefile`                         | Build targets exist     | `scaffold-go-*` / `set-up-ci`                 |
| Linter config files                | Linters exist           | `set-up-linters` / `scaffold-go-*`            |
| `tests/scrut/`                     | Scrut tests exist       | `add-scrut-cli-tests`                         |
| `Formula/`                         | Installers exist        | `set-up-installers`                           |
| `CONTRIBUTING.md`                  | Community files exist   | `add-community-files`                         |

### 3. Build the Plan

Determine which tools to run based on the project type, existing infrastructure, and the overlap rules in `./references/overlap-rules.md`. Read that file for the full decision table.

Key overlap rules:

- If `scaffold-go-cli` will run: skip `set-up-ci`, skip `add-goreleaser-homebrew` (both are included). Scope down `scaffold-new-repo` to only generate agent config files (AGENTS.md, CLAUDE.md, .claude/settings.json, .github/copilot-instructions.md).
- If `scaffold-go-library` will run: skip `set-up-ci` (included). Scope down `scaffold-new-repo` to only generate agent config files. `add-goreleaser-homebrew` and `set-up-installers` are not applicable for libraries.
- If `scaffold-go-library` will run: still run `set-up-linters` but only for cross-language tools (Prettier, EditorConfig, markdownlint) since `.golangci.yml` is already configured.
- If `scaffold-go-cli` will run: still run `set-up-linters` for `.golangci.yml` configuration and cross-language tools (the Makefile lint target exists but no golangci config).
- If `scaffold-rust-cli` will run: skip `set-up-ci` (included). Scope down `scaffold-new-repo` to only generate agent config files. Still run `set-up-linters` but only for cross-language tools since Rust linting is already configured.
- If `scaffold-lean-library` will run: skip `set-up-ci` (included). Scope down `scaffold-new-repo` to only generate missing agent/config extras not produced by the Lean scaffolder. Scope down `set-up-linters` to extra cross-language or Pandoc-academic refinements only, since the Lean scaffolder generates `lintDriver`, `lean-lint`, Markdown and cspell configs, and split CI workflows.
- If `scaffold-lean-library` will run: mark `add-goreleaser-homebrew`, `set-up-installers`, and `add-scrut-cli-tests` as not applicable because Lean libraries do not produce distributable binaries.
- `set-up-secret-scanning` is always independent (no overlap with other tools).
- `add-scrut-cli-tests` is applicable only if the project produces a CLI binary.

Execution order (dependencies flow downward):

1. `scaffold-new-repo` (foundation: LICENSE, README, .gitignore, agent config)
1. `scaffold-go-cli` OR `scaffold-go-library` OR `scaffold-lean-library` OR `scaffold-rust-cli` (language-specific scaffolding, if applicable)
1. `set-up-ci` (if not already covered by step 2)
1. `set-up-linters` (cross-language tools, or full setup if no language scaffolder already covered lint wiring)
1. `set-up-secret-scanning` (secret scanning)
1. `add-goreleaser-homebrew` (if Go CLI and not already covered by step 2)
1. `add-community-files` (community files: CONTRIBUTING, CoC, SECURITY, PR template)
1. `set-up-installers` (if CLI project)
1. `add-scrut-cli-tests` (if CLI project)

### 4. Present the Plan

Show the user a table with each tool and its status. Use these status values:

| Status         | Meaning                                                |
| -------------- | ------------------------------------------------------ |
| Will run       | Tool is needed and will be invoked                     |
| Scoped down    | Tool will run with a reduced scope (see overlap rules) |
| Already set up | Infrastructure already exists; nothing to do           |
| Skipped        | Another tool covers this functionality                 |
| Not applicable | Tool does not apply to this project type               |

Example output:

```text
| #   | Tool                     | Status         | What it does                                |
| --- | ------------------------ | -------------- | ------------------------------------------- |
| 1   | scaffold-new-repo        | Already set up | LICENSE, README, .gitignore, agent config   |
| 2   | scaffold-go-cli          | Already set up | Go CLI project structure, CI, GoReleaser    |
| 3   | set-up-ci                 | Skipped        | Covered by scaffold-go-cli                  |
| 4   | set-up-linters            | Scoped down    | Cross-language tools only (Prettier, etc.)  |
| 5   | set-up-secret-scanning    | Will run       | Gitleaks + TruffleHog secret scanning       |
| 6   | add-goreleaser-homebrew  | Skipped        | Covered by scaffold-go-cli                  |
| 7   | add-community-files      | Will run       | CONTRIBUTING, CoC, SECURITY, PR template    |
| 8   | set-up-installers         | Will run       | Homebrew formula                            |
| 9   | add-scrut-cli-tests      | Will run       | Scrut CLI integration tests                 |
```

Ask the user to confirm the plan. They may:

- Deselect items they do not want
- Add items that were marked as skipped or not applicable

Wait for explicit approval before proceeding.

### 5. Execute

The tools referenced in this plan are skills. Invoke each selected item using the Skill tool:

- `add-community-files`
- `scaffold-new-repo`
- `scaffold-go-cli`
- `scaffold-go-library`
- `scaffold-rust-cli`
- `scaffold-lean-library`
- `set-up-ci`
- `set-up-linters`
- `set-up-secret-scanning`
- `add-goreleaser-homebrew`
- `set-up-installers`
- `add-scrut-cli-tests`

For each confirmed tool, in execution order:

1. Invoke it via the Skill tool.
1. Verify the tool completed successfully.
1. If a tool fails, report the error to the user and ask whether to continue with the remaining tools or stop.

When invoking `set-up-linters` in scoped-down mode, tell it to skip language-specific linters that the Go scaffolder already configured and only set up cross-language tools.

When invoking `set-up-linters` for a Lean library in scoped-down mode, tell it to skip Lean linter wiring that `scaffold-lean-library` already generated. Only request additional cross-language tools, existing-config refinement, or Pandoc-academic preset updates that the user selected.

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
