# zsh -n

## Purpose

Syntax checking without execution. Parses the script and reports any syntax errors without running any commands.

## Command

```bash
zsh -n <file>
```

## Exit Codes

- `0`: No syntax errors
- Non-zero: Parse errors found

## What It Catches

- Unmatched brackets, braces, and parentheses
- Invalid syntax constructs
- Bad redirections
- Unterminated strings and heredocs
- Missing `do`/`done`, `then`/`fi`, `esac` keywords

## What It Misses

- Runtime errors (undefined variables, missing commands)
- Logic errors
- Permission issues
- Errors in sourced files

## Notes

- Always run first. Syntax errors block meaningful results from other tools.
- Fast to execute; adds negligible overhead.
- Does not check files sourced by the script (use `setopt warn_create_global` for deeper analysis).
