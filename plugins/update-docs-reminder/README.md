# Update Docs Reminder

Reminds you to update documentation when a commit includes significant code changes.

**Type:** Hook
**Requires:**

- `bash` 3.2 or newer. The system `bash` on macOS (`/bin/bash`, version 3.2.57) works; no Homebrew `bash` install is needed.
- [`jq`](https://jqlang.github.io/jq/). Install via [Homebrew](https://brew.sh): `brew install jq`.
- `git`. The hook silently skips analysis when not invoked inside a git repository.

## Installation

### Claude Code

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Update Docs Reminder** from the available plugins.

### Codex CLI

```bash
codex plugin marketplace add cboone/cboone-cc-plugins
```

Codex CLI manages this plugin through the marketplace. For a Git-backed marketplace, refresh it after repository updates with `codex plugin marketplace upgrade cboone-cc-plugins` (note that `upgrade` takes the marketplace name `cboone-cc-plugins`, derived from the repository name, not the `owner/repo` identifier used by `add`). For a local-path marketplace, restart Codex after changing plugin files so it can rebuild cached plugin copies from the local source. The plugin includes a Codex manifest with `"hooks": "./hooks/hooks.json"`, so Codex registers the same `PostToolUse` hook definition used by Claude Code.

Enable plugin-bundled hooks once per host so the `PostToolUse` hook fires:

```bash
codex features enable plugin_hooks
```

Without this flag the plugin installs successfully but the hook is ignored. See [Codex CLI known limitations](../../README.md#codex-cli-known-limitations) for context.

### Using with OpenCode

OpenCode loads the plugin automatically when [`OPENCODE_CONFIG_DIR`](../../README.md#using-with-opencode) is set to this repository's `dist/opencode/` mirror. The TypeScript plugin lives at [`opencode/index.ts`](./opencode/index.ts) and uses the `tool.execute.after` hook with the same skip rules, file patterns, and per-project `.update-docs-reminder.json` schema as the Claude Code version.

OpenCode has no surface comparable to Claude Code's PostToolUse stdout, so the reminder is appended to the bash tool's `output.output` instead. The agent reads it on its next turn, with the same wording and bullet structure.

## What It Does

Analyzes each git commit for changes that typically require documentation updates and provides specific, actionable reminders. Detects new scripts, CLI flags, directories, dependencies, environment variables, configuration changes, and public API additions, then maps each to the relevant documentation files.

## When It Fires

This hook runs as a `PostToolUse` hook on the `Bash` tool. After every successful shell command, the hook checks whether a `git commit` just ran. If so, it analyzes the committed diff and reports which documentation files may need attention. Non-commit commands are ignored with minimal overhead. Claude Code and Codex CLI use the same `hooks/hooks.json` definition.

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
