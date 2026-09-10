# Lint and Fix

Detect project linters and formatters, run them with auto-fix, resolve remaining issues, then commit and push the fixes.

**Type:** Skill
**Trigger:** `/lint-and-fix`

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Checks for configuration files to detect ESLint, Prettier, markdownlint, ShellCheck, shfmt, Knip, cspell, and project-specific lint scripts. Runs each detected tool with auto-fix flags, reports what was fixed and what remains, attempts to manually resolve remaining issues, then commits and pushes the fixes.

Detection is a guess, so before running anything the skill reads the project's own agent config (`CLAUDE.md` and `AGENTS.md` in the repository root, and `.github/copilot-instructions.md`) for rules that constrain how linters run:

- **A forbidden fix command** downgrades that tool to check mode instead of being ignored. `markdownlint-cli2 --fix` rewrites everything matching its configured globs regardless of the paths it is given, so a repository that protects an append-only directory has good reason to ban it.
- **A prescribed order** between tools is honored. The detection table has no notion of ordering, so two fixers that both claim `**/*.md` will otherwise fight.
- **A documented lint sequence** runs verbatim in place of the reconstructed commands, including its file selection. A `git ls-files`-driven `shfmt` invocation exists because `shfmt` does not read `.gitignore`.

A downgrade is reported at every stage rather than being applied silently, so "the fixer ran and found nothing" never reads the same as "the fixer was not permitted to run."

## Usage

```text
/lint-and-fix
/lint-and-fix --check
/lint-and-fix --tool eslint
/lint-and-fix --no-commit
/lint-and-fix --no-push
```

| Option          | Description                                 |
| --------------- | ------------------------------------------- |
| `--check`       | Report issues without fixing (dry run)      |
| `--tool <name>` | Run only a specific tool                    |
| `--no-commit`   | Skip committing and pushing                 |
| `--no-push`     | Commit but leave push to the caller or user |

## Recommended Permissions

This skill runs linters, formatters, and git commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(npx eslint *)", "Bash(npx prettier *)", "Bash(prettier *)", "Bash(yarn prettier *)", "Bash(pnpm exec prettier *)", "Bash(bunx prettier *)", "Bash(npx markdownlint-cli2 *)", "Bash(markdownlint-cli2 *)", "Bash(yarn markdownlint-cli2 *)", "Bash(pnpm exec markdownlint-cli2 *)", "Bash(bunx markdownlint-cli2 *)", "Bash(shellcheck *)", "Bash(shfmt *)", "Bash(npx knip*)", "Bash(npx cspell*)", "Bash(npm run lint*)", "Bash(npm run format*)", "Bash(npm run check*)", "Bash(bin/lint*)", "Bash(scripts/lint*)", "Bash(script/lint*)", "Bash(git status --porcelain)", "Bash(git add *)", "Bash(git commit *)", "Bash(git push*)"]
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
- [All plugins](../../../../README.md)
