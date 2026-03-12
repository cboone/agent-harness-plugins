# Scrut Test Style Guide

Conventions for writing and maintaining [scrut](https://github.com/facebookincubator/scrut) CLI test files. These conventions are derived from established patterns in production CLI repositories and scrut's official documentation.

## File Organization

### Directory Structure

Place scrut tests in `tests/scrut/` at the repository root:

```text
tests/
└── scrut/
    ├── help.md
    ├── version.md
    ├── error-handling.md
    ├── flag-validation.md
    └── subcommand-help.md
```

### File Grouping

Organize test files by **behavior group**, not by subcommand:

Good:

- `help.md` (all help output tests)
- `error-handling.md` (all error cases across commands)
- `flag-validation.md` (all flag parsing behavior)

Avoid:

- `serve.md` (mixing all tests for one subcommand)
- `config.md` (mixing init, display, and validation without clear grouping)

### File Naming

- Use `kebab-case.md` for all test file names.
- Name files after the behavior they test, not the implementation.
- Keep names short but descriptive.

## Naming Conventions

### Document Title

Use a level-1 heading that describes the test group:

```markdown
# Help output
```

Not:

```markdown
# Tests for help command

# help.md
```

### Test Case Headings

Use level-2 headings that describe the specific scenario being tested:

```markdown
## Root help with --help flag

## Version command output

## Error on invalid subcommand
```

Describe what is being tested and any relevant variant (which flag, what error condition). Do not describe expectations:

- Good: `## Root help with --help flag`
- Avoid: `## Should print help text`

### Optional Description

Add a brief description paragraph after the document title when the purpose is not obvious from the title alone:

```markdown
# Flag validation

Tests for flag parsing, mutual exclusion, and type validation.
```

## Test Structure

### One Assertion Per Block

Prefer one logical assertion per scrut block. This gives precise failure locations when a test breaks:

Good:

````markdown
## Root help

```scrut
$ "${TOOL_BIN}" --help
Usage:
  tool [command]
...
```

## Short help flag

```scrut
$ "${TOOL_BIN}" -h
Usage:
  tool [command]
...
```
````

Avoid combining unrelated assertions in a single block:

````markdown
## Help flags

```scrut
$ "${TOOL_BIN}" --help
...output...
$ "${TOOL_BIN}" -h
...output...
```
````

Multiple commands in a single block are fine when they form a logical sequence (e.g., setup then verify). For long command chains, see [Continuation Lines for Long Commands](#continuation-lines-for-long-commands).

````markdown
## Config init creates file

```scrut
$ cd "$(mktemp -d)" && NO_COLOR=1 "${TOOL_BIN}" config init && test -f .config.yaml && echo "File created"
Created configuration file: .config.yaml
File created
```
````

### Continuation Lines for Long Commands

Scrut supports a `> ` continuation prefix (inherited from cram) that lets you split long `&&`-chained commands across multiple lines. Use continuation lines when a command chain exceeds a comfortable line length.

The `> ` prefix must appear at the start of the line, followed by exactly two spaces of indentation for readability. The indentation is literal and becomes part of the command, but shell parsing ignores leading whitespace in continuation contexts.

The "Config init creates file" example above, rewritten with continuation lines:

````markdown
## Config init creates file

```scrut
$ cd "$(mktemp -d)" \
>   && NO_COLOR=1 "${TOOL_BIN}" config init \
>   && test -f .config.yaml \
>   && echo "File created"
Created configuration file: .config.yaml
File created
```
````

Prefer the single-line form for short chains (two or three short commands). Use continuation lines when the single-line form is hard to read at a glance.

### Block Order

Within a file, order test cases from most common to most specific:

1. Happy path / default behavior
1. Common flags and variations
1. Edge cases
1. Error conditions

## Binary Invocation

### Always Use Environment Variables

Reference the binary via an environment variable set by the Makefile, never by path:

Good:

```scrut
$ "${TOOL_BIN}" --help
```

Avoid:

```scrut
$ ./bin/tool --help
$ tool --help
```

The environment variable name follows the pattern: binary name uppercased, hyphens replaced with underscores, suffixed with `_BIN`:

- `bopca` becomes `BOPCA_BIN`
- `my-tool` becomes `MY_TOOL_BIN`
- `gh-problemas` becomes `GH_PROBLEMAS_BIN`

### Suppress Color Output

When testing commands that may produce colored output, set `NO_COLOR=1`:

```scrut
$ NO_COLOR=1 "${TOOL_BIN}" config display
```

Or use the environment attribute:

```scrut {environment: {"NO_COLOR": "1"}}
$ "${TOOL_BIN}" config display
```

Prefer `NO_COLOR=1` over `(escaped)` assertion matching. It produces cleaner, more readable tests.

## Assertion Selection

### Prefer Exact Match for Stable Output

Use exact matching (the default) when output is deterministic and unlikely to change between builds. Help text and error messages are good candidates:

```scrut
$ "${TOOL_BIN}" --help
Usage:
  tool [command]

Available Commands:
  completion  Generate shell completions
  help        Help about any command
  version     Print version information

Flags:
  -h, --help      help for tool
  -v, --verbose   increase output verbosity

Use "tool [command] --help" for more information about a command.
```

### Use Glob for Dynamic Values

Use `(glob)` for lines containing values that change between builds, like versions, timestamps, commit hashes, or file paths:

```scrut
$ "${TOOL_BIN}" version
tool v* (glob)
  commit: * (glob)
  built:  * (glob)
```

### Use Glob Quantifiers for Variable-Length Output

Use `(glob+)` to match one or more lines of variable content. This is useful for sections of output you want to acknowledge exist but not pin to exact content:

```scrut
$ "${TOOL_BIN}" --help
Usage:
  tool [command]
* (glob+)
```

Use `(glob*)` (zero or more) when the section may be empty.

### Reserve Regex for Complex Patterns

Only use `(regex)` when glob patterns are insufficient, such as matching specific numeric formats:

```scrut
$ "${TOOL_BIN}" status
Processing: [0-9]+/[0-9]+ items (regex)
```

### Avoid Escaped Matching When Possible

Use `NO_COLOR=1` to suppress ANSI escape codes rather than matching them with `(escaped)`:

Prefer:

```scrut
$ NO_COLOR=1 "${TOOL_BIN}" status
Status: ready
```

Over:

```scrut
$ "${TOOL_BIN}" status
\x1b[32mStatus: ready\x1b[0m (escaped)
```

## Handling Dynamic Output

### Version Information

Always use glob patterns for version lines since they change with every release:

```scrut
$ "${TOOL_BIN}" version
tool v* (glob)
```

### File Paths

Use glob for paths, and `$(mktemp -d)` for temporary directories:

```scrut
$ cd "$(mktemp -d)" && "${TOOL_BIN}" init
Created configuration file: * (glob)
```

### Non-Deterministic Order

Sort output that may vary in order:

```scrut
$ "${TOOL_BIN}" list | sort
bar
baz
foo
```

### Structured Data

For JSON output, extract specific fields with `jq` rather than snapshotting raw JSON:

```scrut
$ "${TOOL_BIN}" status --json | jq -r '.state'
running
```

## Error Testing

### Always Assert Exit Codes

For error cases, always include the expected non-zero exit code as the last line:

```scrut
$ "${TOOL_BIN}" --bad-flag 2>&1 | head -1
Error: unknown flag "--bad-flag"
[1]
```

### Capture Stderr

Most CLI errors write to stderr. Redirect to stdout for testing:

```scrut
$ "${TOOL_BIN}" invalid-command 2>&1 | head -1
Error: unknown command "invalid-command" for "tool"
```

Or use the `output_stream` attribute:

```scrut {output_stream: stderr}
$ "${TOOL_BIN}" --bad-flag
Error: unknown flag "--bad-flag"
[1]
```

The `2>&1` redirect approach is simpler for one-off cases. Use `{output_stream: stderr}` when the entire block validates stderr.

### Test Only the Relevant Error Output

Error messages from CLI frameworks (e.g., Cobra for Go, Swift Argument Parser, clap for Rust) often include usage text after the error line. Pipe through `head -1` or `head -n N` to test only the meaningful part:

```scrut
$ "${TOOL_BIN}" nonexistent 2>&1 | head -1
Error: unknown command "nonexistent" for "tool"
```

### Use Glob for Variable Error Details

When error messages include file paths, values, or other dynamic content:

```scrut
$ "${TOOL_BIN}" open nonexistent-file 2>&1
Error: * no such file * (glob)
[1]
```

## Test Isolation

### Use Temporary Directories for Side Effects

When a command creates, modifies, or deletes files, use `$(mktemp -d)` to isolate the test from the file system:

```scrut
$ cd "$(mktemp -d)" && "${TOOL_BIN}" init && test -f .config.yaml && echo "File created"
Created configuration file: .config.yaml
File created
```

### Set Environment Variables Inline

Use inline env vars for test-specific configuration:

```scrut
$ NO_COLOR=1 "${TOOL_BIN}" --verbose status
```

Or the `environment` attribute for multiple variables:

```scrut {environment: {"TOOL_CONFIG": "/dev/null", "NO_COLOR": "1"}}
$ "${TOOL_BIN}" config display
```

### Use fail_fast for Critical Setup

When a test block sets up state that subsequent blocks depend on, use `{fail_fast: true}` to abort the file early on failure:

```scrut {fail_fast: true}
$ cd "$(mktemp -d)" && "${TOOL_BIN}" init
Created configuration file: .config.yaml
```

## Common Patterns

### Help Output

Test both `--help` and `-h` flags. Pin the full output for regression detection:

````markdown
## Root help

```scrut
$ "${TOOL_BIN}" --help
Usage:
  tool [command]

Available Commands:
  completion  Generate shell completions
  help        Help about any command
  version     Print version information

Flags:
  -h, --help      help for tool
  -v, --verbose   increase output verbosity

Use "tool [command] --help" for more information about a command.
```
````

### Subcommand Help

Dedicate a separate file (`subcommand-help.md`) for subcommand help, or add a section within `help.md`:

````markdown
## Config subcommand help

```scrut
$ "${TOOL_BIN}" config --help
Manage configuration settings.
* (glob+)
```
````

### Flag Validation

Test flags with bad values, missing required flags, and mutually exclusive flags:

````markdown
## Missing required flag

```scrut
$ "${TOOL_BIN}" run 2>&1 | head -1
Error: required flag "target" not set
[1]
```

## Mutually exclusive flags

```scrut
$ "${TOOL_BIN}" run --json --yaml 2>&1 | head -1
Error: flags "json" and "yaml" are mutually exclusive
[1]
```
````

### Verbose and Quiet Modes

````markdown
## Quiet mode suppresses output

```scrut
$ "${TOOL_BIN}" --quiet version
```

## Verbose mode adds detail

```scrut
$ "${TOOL_BIN}" -v --help | grep "verbose count"
  -v, --verbose count   Increase output verbosity (-v or -vv)
```
````

### Config Commands

Test init (in a temp directory), display (with known config), and validation:

````markdown
## Config init creates file

```scrut
$ cd "$(mktemp -d)" && NO_COLOR=1 "${TOOL_BIN}" config init && test -f .config.yaml && echo "File created"
Created configuration file: .config.yaml
File created
```
````

### Completion Scripts

Test that shell completion scripts are generated without errors:

````markdown
## Bash completion

```scrut
$ "${TOOL_BIN}" completion bash | head -1
# bash completion V2 for * (glob)
```

## Zsh completion

```scrut
$ "${TOOL_BIN}" completion zsh | head -1
#compdef * (glob)
```
````

## Maintainability

### Pin What Matters, Flex What Changes

- Pin help text and error messages exactly to catch regressions in user-facing text.
- Use glob for version numbers, timestamps, commit hashes, and paths.
- Use `* (glob+)` for sections that may grow or change order.

### Keep Tests Focused

Each test file should be independently understandable. Avoid relying on state from other test files (each file gets its own shell process).

### Update Snapshots Intentionally

After making intentional changes to CLI output:

```bash
make test-scrut-update
```

Always review the diff after updating. Glob and regex patterns are replaced with literal text during updates, so check for any patterns that need to be restored.

### Document Non-Obvious Tests

When a test case is not self-explanatory, add a brief description between the heading and the code block:

````markdown
## Handles YAML with unicode

Verifies that configuration files with non-ASCII characters are parsed correctly.

```scrut
$ cd "$(mktemp -d)" && printf 'name: "café"' > .config.yaml && "${TOOL_BIN}" config display | grep name
name: café
```
````
