# Scrut Test Format

Reference for writing scrut test files. See the [scrut documentation](https://facebookincubator.github.io/scrut/) for the complete specification.

## File Structure

Scrut test files are standard Markdown files (`.md`) containing fenced code blocks with the `scrut` language identifier. Each file represents a group of related test cases. All test cases within a single file share the same shell process, so variables, aliases, and exports persist across blocks.

Lines starting with `$` are shell commands. Lines starting with `>` are command continuations. All other lines within the code block are expected output.

## Assertion Types

### Exact match (default)

The expected output must match exactly, line by line:

```scrut
$ echo "hello world"
hello world
```

### Glob matching

Use `*` (any characters) and `?` (one character) with the `(glob)` suffix:

```scrut
$ my-tool version
my-tool v* (glob)
  commit: * (glob)
  built:  * (glob)
```

### Regex matching

Use regular expressions with the `(regex)` suffix:

```scrut
$ my-tool version
my-tool v\d+\.\d+\.\d+ (regex)
```

### Escaped matching

Match output containing non-printable characters (ANSI escapes, tabs) with the `(escaped)` suffix:

```scrut
$ printf "foo\tbar"
foo\tbar (escaped)
```

## Quantifiers

Quantifiers control how many output lines a single expectation line can match:

| Quantifier | Meaning            | Example     |
| ---------- | ------------------ | ----------- |
| `?`        | Zero or one line   | `* (glob?)` |
| `*`        | Zero or more lines | `* (glob*)` |
| `+`        | One or more lines  | `* (glob+)` |

Common pattern for matching variable-length output:

```scrut
$ my-tool --help
Usage:
  my-tool [command]
* (glob+)
```

## Exit Codes

By default, scrut expects exit code 0. Specify non-zero exit codes with bracket notation as the last line of expected output:

```scrut
$ my-tool --bad-flag 2>&1 | head -1
Error: unknown flag "--bad-flag"
[1]
```

## Empty Output

When a command should produce no output, leave the code block empty after the command:

```scrut
$ my-tool --quiet version
```

## Stderr

By default, scrut validates stdout only. To validate stderr, use the `output_stream` attribute:

```scrut {output_stream: stderr}
$ my-tool --bad-flag
Error: unknown flag "--bad-flag"
[1]
```

To validate combined stdout and stderr, either use the attribute or redirect in the command:

```scrut
$ my-tool bad-command 2>&1 | head -1
Error: unknown command "bad-command" for "my-tool"
```

## Per-Test Configuration

Attributes can be set in curly braces after the language tag:

| Attribute       | Description                 | Example                         |
| --------------- | --------------------------- | ------------------------------- |
| `timeout`       | Max execution time          | `{timeout: 10s}`                |
| `fail_fast`     | Stop document on failure    | `{fail_fast: true}`             |
| `output_stream` | Stream to validate          | `{output_stream: stderr}`       |
| `environment`   | Extra environment variables | `{environment: {"KEY": "val"}}` |

## Document Configuration (Frontmatter)

YAML frontmatter controls document-level settings:

```yaml
---
prepend:
  - "../shared/setup.md"
defaults:
  timeout: 10s
total_timeout: 30s
---
```

## Built-in Environment Variables

Scrut provides these variables in every test execution:

| Variable    | Description                             |
| ----------- | --------------------------------------- |
| `$TESTDIR`  | Directory containing the test file      |
| `$TESTFILE` | Name of the current test file           |
| `$TMPDIR`   | Fresh temporary directory per test file |

## Tips

- Use `NO_COLOR=1` to suppress color codes in output.
- Pipe through `head`, `tail`, or `grep` to test specific lines.
- Use `$(mktemp -d)` for operations that create files.
- Sort non-deterministic output with `| sort`.
- Prefer JSON output with `jq` extraction over snapshotting raw text for structured data.
- Use one test file per logical group of related behaviors (e.g., `help.md`, `version.md`, `error-handling.md`).
- Run `make test-scrut-update` to regenerate expected output after intentional changes.
