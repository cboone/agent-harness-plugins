# Bootstrap Project

Assess a repository, determine what scaffolding and setup tools are needed, present a plan, and execute them in the correct order.

**Type:** Skill
**Trigger:** `/bootstrap-project`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Bootstrap Project** from the available plugins.

## What It Does

Scans the repository for language markers and existing infrastructure, determines which scaffolding and setup tools are needed, presents a plan with status for each tool, and executes confirmed tools in the correct dependency order. Handles overlap between tools automatically (e.g., `scaffold-go-cli` already includes CI and GoReleaser, so those are skipped).

Orchestrates these tools:

- `scaffold-new-repo`: LICENSE, README, .gitignore, agent config
- `scaffold-go-cli` / `scaffold-go-library`: language-specific project structure
- `setup-ci`: GitHub Actions CI workflow and Makefile targets
- `setup-linters`: linters and formatters
- `setup-secret-scanning`: secret scanning workflows
- `add-goreleaser-homebrew`: GoReleaser and Homebrew tap publishing
- `setup-installers`: Homebrew formula
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
- [Setup Linters](../setup-linters/README.md): linter and formatter setup only
- [All plugins](../../../../README.md)
