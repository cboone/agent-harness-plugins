# Help Test

Starter test file template for verifying `--help` output.

## Template

Write `tests/scrut/help.md` with the following content:

````markdown
# Help output

Tests for TOOL help commands.

## Root help

```scrut
$ "${TOOL_BIN}" --help
HELP_OUTPUT
```

## Short help flag

```scrut
$ "${TOOL_BIN}" -h
HELP_OUTPUT
```
````

## Placeholders

| Placeholder   | Description                                         | Example                 |
| ------------- | --------------------------------------------------- | ----------------------- |
| `TOOL`        | Human-readable tool name                            | `bopca`                 |
| `TOOL_BIN`    | Environment variable name for the binary path       | `BOPCA_BIN`             |
| `HELP_OUTPUT` | Actual output from running the binary with `--help` | (captured during setup) |

## Notes

- Both `--help` and `-h` should produce identical output. If they differ, adjust accordingly.
- The `HELP_OUTPUT` should be the exact output captured from running the binary. Use `scrut create` or `scrut update` to populate this.
- To bootstrap the test file with actual output, write the template with a `* (glob+)` placeholder for the output, then run `make test-scrut-update` to replace it with the real output.
- If the tool has subcommands, add a separate test file for subcommand help output (e.g., `subcommand-help.md`).
