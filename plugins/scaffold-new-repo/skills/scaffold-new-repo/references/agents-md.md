# AGENTS.md Template

This is the single source of truth for all AI coding agents (Claude Code, Codex, Copilot, OpenCode). CLAUDE.md is created as a symlink pointing to this file.

Replace `PROJECT-NAME` with the project name in title case and `SHORT-DESCRIPTION` with the one-sentence description.

````markdown
# PROJECT-NAME

## Overview

SHORT-DESCRIPTION
````

## Notes

- The heading uses the project name in title case (e.g., `my-cool-tool` becomes `My Cool Tool`).
- CLAUDE.md should be a symlink to this file: `ln -sfn AGENTS.md CLAUDE.md`
- Add a `## Structure` section (with a fenced code block directory tree) once the project has enough files to document.
- Add a `## Development` section listing common commands (build, test, lint, run) once they are established.
- Keep AGENTS.md under 200 lines. Use `.claude/rules/*.md` for Claude-specific instructions.
