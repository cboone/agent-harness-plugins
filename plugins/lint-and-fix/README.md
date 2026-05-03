# Lint and Fix

Detect available linters and formatters in the project, run them with auto-fix, resolve remaining issues, then commit and push the fixes.

**Type:** Skill
**Trigger:** `/lint-and-fix`

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Checks for configuration files to detect ESLint, Prettier, markdownlint, ShellCheck, shfmt, Knip, cspell, and project-specific lint scripts. Runs each detected tool with auto-fix flags, reports what was fixed and what remains, attempts to manually resolve remaining issues, then commits and pushes the fixes.

## Usage

```text
/lint-and-fix
/lint-and-fix --check
/lint-and-fix --tool eslint
/lint-and-fix --no-commit
/lint-and-fix --no-push
```

| Option          | Description                                       |
| --------------- | ------------------------------------------------- |
| `--check`       | Report issues without fixing (dry run)            |
| `--tool <name>` | Run only a specific tool                          |
| `--no-commit`   | Skip committing and pushing                       |
| `--no-push`     | Commit but do not push (default: commit and push) |

## Recommended Permissions

This skill runs linters, formatters, and git commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(npx eslint *)", "Bash(npx prettier *)", "Bash(npx markdownlint-cli2 *)", "Bash(shellcheck *)", "Bash(shfmt *)", "Bash(npx knip*)", "Bash(npx cspell*)", "Bash(npm run lint*)", "Bash(npm run format*)", "Bash(npm run check*)", "Bash(bin/lint*)", "Bash(scripts/lint*)", "Bash(script/lint*)", "Bash(git status --porcelain)", "Bash(git add *)", "Bash(git commit *)", "Bash(git push*)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "lint and fix": detects and runs all available linters with auto-fix
- "run the linter --check": reports issues without modifying files
- "fix lint errors --tool prettier": runs only Prettier

## See Also

- [Write Go Code](../write-go-code/README.md): Go-specific style enforcement
- [Write Markdown](../write-markdown/README.md): Markdown-specific style enforcement
- [All plugins](../../README.md)
