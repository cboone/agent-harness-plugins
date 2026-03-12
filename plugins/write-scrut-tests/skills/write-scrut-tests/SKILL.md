---
name: write-scrut-tests
description: >-
  Applies scrut test style conventions when creating or editing scrut test
  files for CLI binaries and zsh plugins. Use when: (1) creating new scrut
  test files in tests/scrut/, (2) editing existing scrut test .md files,
  (3) reviewing scrut tests for style and maintainability, or (4) testing
  zsh plugins or sourced libraries with scrut.
---

# Scrut Test Style Guide

Apply the scrut test conventions from `./references/SCRUT.md` when creating or editing scrut CLI test files.

## Key Conventions

Read `./references/SCRUT.md` for the complete guide. Summary:

### File Organization

- Place tests in `tests/scrut/` at the repository root
- One file per behavior group (`help.md`, `error-handling.md`, `flag-validation.md`)
- Use `kebab-case.md` file names describing the behavior tested

### Test Structure

- One logical assertion per scrut block for precise failure locations
- Use `> ` continuation prefix to split long `&&`-chained commands across lines
- Order blocks: happy path first, then common variations, then edge cases, then errors
- Level-1 heading for the test group, level-2 headings for individual test cases

### Binary Invocation

- Always reference the binary via `"${TOOL_BIN}"` environment variable, never by path
- Use `NO_COLOR=1` for commands that may produce colored output
- Use `$(mktemp -d)` for commands that create files

### Assertion Selection

- Exact match (default) for stable, deterministic output like help text
- `(glob)` for dynamic values: versions, timestamps, commit hashes, paths
- `(glob+)` for variable-length sections you want to acknowledge but not pin
- `(regex)` only when glob patterns are insufficient
- Prefer `NO_COLOR=1` over `(escaped)` matching for colored output

### Error Testing

- Always include the expected exit code: `[1]`
- Redirect stderr to stdout: `2>&1`
- Pipe through `head -1` for long error output with usage text
- Use `{output_stream: stderr}` attribute as an alternative to redirection

### Maintainability

- Pin help text and error messages exactly (catches regressions in user-facing text)
- Use glob for values that change between builds (versions, hashes, timestamps)
- Review diffs after `make test-scrut-update` to ensure glob/regex patterns were not replaced with literals

## Zsh Plugin and Library Testing

For testing zsh plugins and sourced library code with scrut, read `./references/zsh-plugin-testing.md`. Key points:

- Use `--shell zsh` flag with `scrut test` and `scrut update`
- Use `source "${TESTDIR}/path/to/file.zsh"` instead of `"${TOOL_BIN}"`
- Each scrut block supports only one `$` line; additional `$` lines are treated as expected output
- Do not set `ERR_EXIT` at file level; use `emulate -L zsh` with strict options inside functions
- Chain `source` and function calls with `&&` on the same command line

## Validation

After writing or editing scrut tests, run them to verify:

```bash
make test-scrut
```

If snapshots need updating after intentional output changes:

```bash
make test-scrut-update
```
