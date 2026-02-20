# Add Scrut CLI Tests

Set up scrut snapshot-based CLI integration testing for a Go CLI project.

**Type:** Skill
**Trigger:** `/add-scrut-cli-tests`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Add Scrut CLI Tests** from the available plugins.

## What It Does

Adds [scrut](https://github.com/facebookincubator/scrut) snapshot-based CLI integration testing to an existing Go CLI project. Creates a `tests/scrut/` directory with starter test files for help and version output, adds Makefile targets for running and updating tests, and configures the CI workflow to install scrut and run CLI tests.

## Usage

```text
/add-scrut-cli-tests
```

The skill detects the binary name and build configuration from the existing Makefile and generates test files accordingly.

## Examples

- "add scrut tests": sets up scrut testing in the current project
- "add CLI tests": same behavior
- "set up scrut": same behavior
- "add e2e tests for my CLI": same behavior

## See Also

- [Scaffold Go CLI](../scaffold-go-cli/README.md): scaffold a new Go CLI project (includes build targets this skill depends on)
- [Write Go Code](../write-go-code/README.md): Go style guide for the CLI source code
- [Lint and Fix](../lint-and-fix/README.md): run linters and formatters
- [All plugins](../../README.md)
