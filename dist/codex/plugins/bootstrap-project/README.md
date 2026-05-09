# Bootstrap Project

Assess a repository, determine what scaffolding and setup tools are needed, present a plan, and execute them in the correct order.

**Type:** Skill
**Trigger:** `/bootstrap-project`

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Scans the repository for language markers and existing infrastructure, determines which scaffolding and setup tools are needed, presents a plan with status for each tool, and executes confirmed tools in the correct dependency order. Handles overlap between tools automatically (e.g., `scaffold-go-cli` already includes CI and GoReleaser, so those are skipped).

Orchestrates these tools:

- `scaffold-new-repo`: LICENSE, README, .gitignore, agent config
- `scaffold-go-cli` / `scaffold-go-library` / `scaffold-lean-library`: language-specific project structure
- `set-up-ci`: GitHub Actions CI workflow and Makefile targets
- `set-up-linters`: linters and formatters
- `set-up-secret-scanning`: secret scanning workflows
- `add-goreleaser-homebrew`: GoReleaser and Homebrew tap publishing
- `set-up-installers`: Homebrew formula
- `add-scrut-cli-tests`: scrut CLI integration tests

## Usage

```text
/bootstrap-project
```

## Examples

- "bootstrap this project": full assessment and setup
- "set up everything": same behavior
- "scaffold everything": same behavior
- "full project setup": same behavior

## See Also

- [Scaffold New Repo](../scaffold-new-repo/README.md): foundational repo boilerplate only
- [Scaffold Go CLI](../scaffold-go-cli/README.md): Go CLI project scaffolding only
- [Scaffold Go Library](../scaffold-go-library/README.md): Go library project scaffolding only
- [Scaffold Lean Library](../scaffold-lean-library/README.md): Lean 4 library project scaffolding only
- [Set-Up Linters](../set-up-linters/README.md): linter and formatter setup only
- [All plugins](../../../../README.md)
