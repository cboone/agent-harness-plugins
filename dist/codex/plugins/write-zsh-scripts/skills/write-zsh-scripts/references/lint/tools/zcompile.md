# zcompile

## Purpose

Compile zsh scripts to wordcode (`.zwc` format). Catches errors that `zsh -n` might miss in certain edge cases, particularly around autoload function definitions and complex parameter expansions.

## Command

```bash
zsh -c 'zcompile "$1"' _ <file>
```

`zcompile` is a zsh builtin. The `zsh -c` wrapper ensures it runs in zsh even when invoked from a bash shell. The `_` is a conventional placeholder for `$0` in `zsh -c` invocations; using `--` does not work because zsh interprets it as a filename rather than an option separator.

## Cleanup

Always remove the `.zwc` artifact after checking:

```bash
rm -f <file>.zwc
```

## Exit Codes

- `0`: Compilation successful
- Non-zero: Compilation error

## What It Catches

- Errors in autoload-compatible function files
- Certain parameter expansion edge cases
- Syntax issues specific to compiled contexts

## Notes

- The `.zwc` file is a compilation artifact and serves no purpose for this check. Always clean it up.
- If `zsh -n` passes but `zcompile` fails, the error is likely in an edge case worth investigating.
- Normally used for performance optimization (pre-compiled scripts load faster), but here it is repurposed as a validation tool.
