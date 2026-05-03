# Write Scrut Tests

Applies scrut test style conventions when creating or editing scrut CLI test files.

**Type:** Skill
**Trigger:** `/write-scrut-tests` (also activates automatically)

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Provides style conventions for writing [scrut](https://github.com/facebookincubator/scrut) snapshot-based test files for CLI binaries and zsh plugins. Covers file organization, naming conventions, assertion type selection, error testing patterns, test isolation, zsh plugin invocation, and maintainability. Activates automatically when creating or editing scrut test files.

## Usage

```text
/write-scrut-tests
```

The skill also activates automatically when creating or editing `.md` files in `tests/scrut/` or similar test directories.

## Examples

- "add a scrut test for the config command": applies style conventions while writing the test
- "review the scrut tests": checks existing tests against the style guide
- "write scrut tests for error handling": follows conventions for error test patterns
- "write scrut tests for my zsh plugin": uses source-based invocation with `--shell zsh`

## See Also

- [Add Scrut CLI Tests](../add-scrut-cli-tests/README.md): set up scrut testing infrastructure in a CLI project
- [All plugins](../../../../README.md)
