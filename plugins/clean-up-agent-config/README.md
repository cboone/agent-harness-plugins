# Clean Up Agent Config

Review and reorganize AI coding agent configuration and instruction files.

**Type:** Skill
**Trigger:** `/clean-up-agent-config`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Clean Up Agent Config** from the available plugins.

## What It Does

Audits agent configuration files across Claude Code, OpenAI Codex, GitHub Copilot (CLI and code review), and OpenCode. Identifies duplications and misplaced settings, proposes a consolidated structure, handles the `settings.json` vs `settings.local.json` split, sets up `AGENTS.md` as the single source of truth with `CLAUDE.md` as a symlink, and takes advantage of tool-specific features like Copilot's path-scoped `.instructions.md` files.

Includes comprehensive reference documentation on all agent instruction and configuration file formats.

## Usage

```text
/clean-up-agent-config
```

## Examples

- "clean up agent config": audits and reorganizes all agent config files
- "organize agent files": same behavior
- "consolidate agent files": same behavior

## See Also

- [Create Plugin](../create-plugin/README.md): create new plugins for the agent ecosystem
- [All plugins](../../README.md)
