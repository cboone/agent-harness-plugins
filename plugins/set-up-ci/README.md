# Set-Up CI

Set up GitHub Actions CI with test, lint, format, and vulnerability check jobs, plus matching Makefile targets.

**Type:** Skill
**Trigger:** `/set-up-ci`

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Detects the project's language(s), creates a GitHub Actions CI workflow (`.github/workflows/ci.yml`) with appropriate parallel jobs, and creates matching Makefile targets for local development.

Supported languages: Go (CLI and library), JavaScript/TypeScript, Python, Rust, Ruby, Shell, Zig, and Zsh. Multi-language projects get a combined workflow with one job group per language.

## Usage

```text
/set-up-ci
```

## Examples

- "set up CI": detects language and generates workflow + Makefile targets
- "add CI to this project": same behavior
- "configure CI": same behavior

## See Also

- [Set-Up Secret Scanning](../set-up-secret-scanning/README.md): add secret scanning to CI
- [Set-Up Linters](../set-up-linters/README.md): configure linter and formatter tools
- [Scaffold Go CLI](../scaffold-go-cli/README.md): scaffold a full Go CLI project (includes CI)
- [Scaffold Go Library](../scaffold-go-library/README.md): scaffold a Go library project (includes CI)
- [All plugins](../../README.md)
