# Update Docs Reminder

Reminds you to update documentation when a commit includes significant code changes.

**Type:** Hook
**Requires:** [`jq`](https://jqlang.github.io/jq/). Install via [Homebrew](https://brew.sh): `brew install jq`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Update Docs Reminder** from the available plugins.

## What It Does

Analyzes each git commit for changes that typically require documentation updates and provides specific, actionable reminders. Detects new scripts, CLI flags, directories, dependencies, environment variables, configuration changes, and public API additions, then maps each to the relevant documentation files.

## When It Fires

This hook runs as a `PostToolUse` hook on the `Bash` tool. After every successful shell command, the hook checks whether a `git commit` just ran. If so, it analyzes the committed diff and reports which documentation files may need attention. Non-commit commands are ignored with minimal overhead.

| Change detected                     | Documentation to check            |
| ----------------------------------- | --------------------------------- |
| New scripts in `bin/` or `scripts/` | README.md (usage section)         |
| New CLI flags or arguments          | README.md (usage/options section) |
| New top-level directories           | CLAUDE.md (structure), README.md  |
| New dependencies                    | README.md (installation section)  |
| New environment variables           | README.md (configuration section) |
| Configuration file changes          | README.md (configuration section) |
| CI/CD workflow changes              | README.md (CI section)            |
| New public API exports              | README.md, API docs               |

## Skipped Commits

The hook skips analysis for:

- Merge commits
- Commits with conventional prefixes: `style:`, `chore:`, `docs:`, `ci:`, `test:`
- Commits that only touch test files
- Commits that only touch documentation files
- The first commit in a repository

## Configuration

The hook works with sensible defaults and requires no configuration. To customize behavior per project, create a `.update-docs-reminder.json` file in the project root:

```json
{
  "enabled": true,
  "skip_prefixes": ["style", "chore", "docs", "ci", "test"],
  "checks": {
    "scripts": true,
    "directories": true,
    "dependencies": true,
    "config": true,
    "ci": true,
    "env_vars": true,
    "cli_flags": true,
    "public_api": true
  }
}
```

Set `enabled` to `false` to disable the hook entirely for a project. Set individual checks to `false` to skip specific heuristics. Customize `skip_prefixes` to change which conventional commit prefixes are ignored.

## See Also

- [All plugins](../../README.md)
