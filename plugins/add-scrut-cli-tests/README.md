# Add Scrut CLI Tests

Set up scrut snapshot-based CLI integration testing for a CLI project.

**Type:** Skill
**Trigger:** `/add-scrut-cli-tests`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Add Scrut CLI Tests** from the available plugins.

## What It Does

Adds [scrut](https://github.com/facebookincubator/scrut) snapshot-based CLI integration testing to an existing CLI project. Detects the project language (Go, Swift, Rust, Python, Ruby, shell), creates a `tests/scrut/` directory with starter test files for help and version output, adds Makefile targets for running and updating tests, and configures the CI workflow to install scrut and run CLI tests.

## Usage

```text
/add-scrut-cli-tests
```

The skill detects the project type and binary name from existing project files and generates test files accordingly.

## Examples

- "add scrut tests": sets up scrut testing in the current project
- "add CLI tests": same behavior
- "set up scrut": same behavior
- "add e2e tests for my CLI": same behavior

## See Also

- [Write Scrut Tests](../write-scrut-tests/README.md): style conventions for writing scrut test files
- [Lint and Fix](../lint-and-fix/README.md): run linters and formatters
- [Scaffold Go CLI](../scaffold-go-cli/README.md): scaffold a new Go CLI project (includes build targets compatible with this skill)
- [All plugins](../../README.md)
