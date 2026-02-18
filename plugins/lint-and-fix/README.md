# Lint and Fix

Detect available linters and formatters in the project, run them with auto-fix, and resolve remaining issues.

**Type:** Skill
**Trigger:** `/lint-and-fix`

## What It Does

Checks for configuration files to detect ESLint, Prettier, markdownlint, ShellCheck, shfmt, Knip, and project-specific lint scripts. Runs each detected tool with auto-fix flags, reports what was fixed and what remains, then attempts to manually resolve remaining issues.

## Usage

```text
/lint-and-fix
/lint-and-fix --check
/lint-and-fix --tool eslint
/lint-and-fix --commit
/lint-and-fix --no-commit
```

| Option          | Description                            |
| --------------- | -------------------------------------- |
| `--check`       | Report issues without fixing (dry run) |
| `--tool <name>` | Run only a specific tool               |
| `--commit`      | Commit fixes automatically             |
| `--no-commit`   | Do not commit fixes                    |

## Examples

- "lint and fix" — detects and runs all available linters with auto-fix
- "run the linter --check" — reports issues without modifying files
- "fix lint errors --tool prettier" — runs only Prettier

## See Also

- [Write Go Code](../write-go-code/README.md) — Go-specific style enforcement
- [Write Markdown](../write-markdown/README.md) — Markdown-specific style enforcement
- [All plugins](../../README.md)
