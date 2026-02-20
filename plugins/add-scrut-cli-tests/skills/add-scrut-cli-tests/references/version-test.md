# Version Test

Starter test file template for verifying version command output.

## Template

Write `tests/scrut/version.md` with the following content:

````markdown
# Version output

Tests for TOOL version commands.

## Version command

```scrut
$ "${TOOL_BIN}" version
TOOL v* (glob)
  commit: * (glob)
  built:  * (glob)
```

## Version flag

```scrut
$ "${TOOL_BIN}" --version
TOOL v* (glob)
  commit: * (glob)
  built:  * (glob)
```
````

## Placeholders

| Placeholder | Description                                         | Example     |
| ----------- | --------------------------------------------------- | ----------- |
| `TOOL`      | Human-readable tool name (as printed by the binary) | `bopca`     |
| `TOOL_BIN`  | Environment variable name for the binary path       | `BOPCA_BIN` |

## Notes

- Version output typically contains dynamic values (version number, commit hash, build timestamp). Use `(glob)` patterns for these lines.
- The template assumes the version output format includes version, commit, and build timestamp. Adjust the expected output to match the project's actual version format.
- If the project only supports `--version` and not a `version` subcommand (or vice versa), remove the test case that does not apply.
- If the project does not have version output yet, skip this test file and note it as a follow-up.
