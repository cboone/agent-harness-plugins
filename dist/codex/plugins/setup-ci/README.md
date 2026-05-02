# Setup CI

Set up GitHub Actions CI with test, lint, format, and vulnerability check jobs, plus matching Makefile targets.

**Type:** Command
**Trigger:** `/setup-ci`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Setup CI** from the available plugins.

## What It Does

Detects the project's language(s), creates a GitHub Actions CI workflow (`.github/workflows/ci.yml`) with appropriate parallel jobs, and creates matching Makefile targets for local development.

Supported languages: Go (CLI and library), JavaScript/TypeScript, Python, Rust, Ruby, Shell, Zig, and Zsh. Multi-language projects get a combined workflow with one job group per language.

## Usage

```text
/setup-ci
```

## Examples

- "set up CI": detects language and generates workflow + Makefile targets
- "add CI to this project": same behavior
- "setup ci": same behavior

## See Also

- [Setup Secret Scanning](../setup-secret-scanning/README.md): add secret scanning to CI
- [Setup Linters](../setup-linters/README.md): configure linter and formatter tools
- [Scaffold Go CLI](../scaffold-go-cli/README.md): scaffold a full Go CLI project (includes CI)
- [Scaffold Go Library](../scaffold-go-library/README.md): scaffold a Go library project (includes CI)
- [All plugins](../../../../README.md)
