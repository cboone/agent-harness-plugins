# Plan: update-docs-reminder hook (issue #16)

## Context

Analysis of session history revealed ~42 occurrences of documentation update commands, often performed as an afterthought after code changes are already committed. A PostToolUse hook can catch these moments proactively by analyzing each git commit and providing specific, actionable reminders about which documentation files may need updating.

## Approach

Create a **PostToolUse command hook on Bash** that:

1. Fires after every Bash tool call (fast exit for non-commits)
1. Detects `git commit` commands and analyzes the committed diff
1. Runs heuristics to identify changes that typically need documentation
1. Outputs reminders to stdout (injected into Claude's context as feedback)
1. Skips commits that are unlikely to need docs (merge commits, `style:`, `chore:`, `docs:`, `ci:`, `test:` prefixes, test-only changes)

### Why PostToolUse (not Stop)

PostToolUse gives immediate feedback right after a commit, when context is fresh and the user can act on it. A Stop hook fires at session end, which is too late to be actionable.

### Why command-based (not prompt-based)

A shell script is deterministic, fast, and inspectable. Prompt-based hooks would add latency to every Bash call and consume tokens. The heuristics are structural (file paths, dependency files, diff patterns), not semantic, so a script handles them well.

## Files to create

### 1. `plugins/update-docs-reminder/.claude-plugin/plugin.json`

Standard plugin manifest, version 1.0.0. No external dependencies beyond `jq`.

### 2. `plugins/update-docs-reminder/hooks/hooks.json`

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/check-docs",
            "type": "command"
          }
        ],
        "matcher": "Bash"
      }
    ]
  }
}
```

### 3. `plugins/update-docs-reminder/scripts/check-docs`

Core script. Architecture:

```text
main
  read JSON stdin, extract command
  fast exit if not a git commit
  fast exit if merge commit (multiple parents)
  fast exit if commit message matches skip prefixes
  fast exit if only test files changed
  run heuristics on git diff HEAD~1..HEAD
  if any reminders, output to stdout
  exit 0
```

**JSON input handling** (backward-compatible):

```bash
command="$(jq -r '.tool_input.command // .input.command // empty')"
```

**Detection heuristics** (each appends to a `REMINDERS` array):

| Function                   | Detects                                                                                            | Suggests                            |
| -------------------------- | -------------------------------------------------------------------------------------------------- | ----------------------------------- |
| `check_new_scripts`        | New files in `bin/`, `scripts/`, `cmd/`                                                            | README.md usage section             |
| `check_new_directories`    | New top-level directories (from added files)                                                       | CLAUDE.md structure, README.md      |
| `check_dependency_changes` | Changes to `go.mod`, `package.json`, `requirements.txt`, `Cargo.toml`, `Gemfile`, `pyproject.toml` | README.md installation/requirements |
| `check_config_changes`     | Changes to `.env.example`, `docker-compose*`, `Dockerfile`                                         | README.md configuration section     |
| `check_ci_changes`         | Changes in `.github/workflows/` or `.github/actions/`                                              | README.md CI section                |
| `check_new_env_vars`       | New `os.Getenv`, `process.env`, `os.environ` patterns in diff                                      | README.md configuration section     |
| `check_cli_flags`          | New flag definitions (`flag.String`, `pflag`, `argparse`, `cobra.Command`, `.option(`) in diff     | README.md usage/options section     |
| `check_public_api`         | New exported functions/types (`func [A-Z]`, `export function`, `pub fn`) in diff                   | README.md, API docs                 |

**False positive avoidance:**

- Focus on ADDED files, not modifications (for structural checks)
- Skip merge commits, docs-only commits, test-only commits, style/chore commits
- Content-level diff checks (flags, env vars, API) only run on a limited set of files (`head -5`) with truncated output (`head -200`)
- Guard for first commit (`git rev-parse --verify HEAD~1`)

**Output format** (plain text to stdout):

```text
Documentation reminder: the committed changes may need documentation updates:
  - New script added in scripts/: update README.md usage section
  - Dependencies changed (go.mod): update README.md installation section
```

**Per-project configuration:**

The script checks for an optional `.update-docs-reminder.json` in the git root. If absent, all checks are enabled. Format:

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

### 4. `plugins/update-docs-reminder/README.md`

Hook README following the template from `create-plugin` references. Includes:

- Type: Hook
- Requires: `jq`
- What It Does: analyzes commits for doc-worthy changes
- When It Fires: PostToolUse on Bash, after git commit
- Table of change types and which docs to check
- Skipped commit types
- Configuration section documenting `.update-docs-reminder.json`

## Files to modify

### 5. `.claude-plugin/marketplace.json`

- Add `update-docs-reminder` entry in alphabetical order (after `update-everything`, before `use-git`)
- Category: `"productivity"`
- Version: `"1.0.0"`
- Bump `metadata.version` from `1.21.0` to `1.22.0`

### 6. `README.md` (root)

- **ToC**: Add `∙ [Update Docs Reminder](#update-docs-reminder)` under Hooks > Workflow (after Notify)
- **Description section**: Add H4 under `### Workflow` after Notify:

```markdown
#### Update Docs Reminder

Analyzes git commits for changes that typically need documentation updates and provides specific, actionable reminders.

> **Requires:** [`jq`](https://jqlang.github.io/jq/)
> **Details:** [README](./plugins/update-docs-reminder/README.md)
```

### 7. `CLAUDE.md` (root)

Add the plugin directory to the structure tree in alphabetical order among existing plugins:

```text
    ├── update-docs-reminder/        # Documentation update reminder hook
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   ├── hooks/
    │   │   └── hooks.json
    │   └── scripts/
    │       └── check-docs
```

## Implementation sequence

1. Create plugin directory structure and `plugin.json`
1. Create `hooks/hooks.json`
1. Create `scripts/check-docs` and `chmod +x`
1. Create per-plugin `README.md`
1. Update root `README.md` (ToC + description)
1. Update `.claude-plugin/marketplace.json` (add entry + bump version)
1. Update root `CLAUDE.md` (structure tree)

## Verification

1. **shellcheck**: Run `shellcheck plugins/update-docs-reminder/scripts/check-docs` to validate the script
1. **Dry run**: Make a test commit in a scratch repo and pipe sample PostToolUse JSON through the script to verify output
1. **Fast path**: Pipe non-commit JSON through the script and confirm it exits silently
1. **check-versions skill**: Run after all changes to verify version consistency
1. **lint-and-fix skill**: Run to check formatting
1. **Manual test**: Install the plugin in Claude Code and make a commit that adds a new file in `scripts/` to confirm the reminder appears

## Key files to reference during implementation

- `plugins/block-rm-rf/scripts/check-rm` (simple hook script pattern)
- `plugins/notify/scripts/notify` (complex script with `do_` functions, JSON parsing)
- `plugins/create-plugin/skills/create-plugin/references/hooks-json.md` (hooks.json format)
- `plugins/create-plugin/skills/create-plugin/references/scripts.md` (script conventions)
- `plugins/create-plugin/skills/create-plugin/references/readme-updates.md` (README templates)
