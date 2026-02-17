# AGENTS.md Template

This is the single source of truth for all AI coding agents (Claude Code, Codex, Copilot, OpenCode). CLAUDE.md is created as a symlink pointing to this file.

Replace `PROJECT-NAME` with the project name in title case and `SHORT-DESCRIPTION` with the one-sentence description.

````markdown
# PROJECT-NAME

## Overview

SHORT-DESCRIPTION

## Structure

```text
TODO
```

## Development

TODO
````

## Notes

- The heading uses the project name in title case (e.g., `my-cool-tool` becomes `My Cool Tool`).
- CLAUDE.md should be a symlink to this file: `ln -sfn AGENTS.md CLAUDE.md`
- The Structure section should be filled in once the project has enough files to document.
- The Development section should list common commands (build, test, lint, run) once they are established.
- Keep AGENTS.md under 200 lines. Use `.claude/rules/*.md` for Claude-specific instructions.
