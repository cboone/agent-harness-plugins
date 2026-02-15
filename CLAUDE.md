# Claude Code Plugins

## Project Overview

This repository contains plugins (hooks and skills) for Claude Code.

## Structure

```text
cboone-cc-plugins/
├── .claude-plugin/
│   └── marketplace.json            # Plugin registry for this repository
└── plugins/
    ├── commit/                      # Smart git commit skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── commit/
    │           └── SKILL.md
    ├── create-worktree-from-issue/  # Issue-to-worktree skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── create-worktree-from-issue/
    │           └── SKILL.md
    ├── write-go-code/              # Go style guide skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── write-go-code/
    │           ├── SKILL.md
    │           └── references/
    │               ├── comprehensive/
    │               │   ├── code-organization.md
    │               │   ├── concurrency.md
    │               │   ├── data-types.md
    │               │   ├── errors.md
    │               │   ├── functions.md
    │               │   ├── interfaces.md
    │               │   ├── naming.md
    │               │   └── testing.md
    │               └── essential/
    │                   └── checklist.md
    ├── notify/                     # Notification hooks plugin
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── hooks/
    │   │   └── hooks.json
    │   └── scripts/
    │       └── notify
    ├── resolve-copilot-pr-feedback/ # Copilot PR feedback resolver skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── scripts/
    │   │   └── resolve-copilot-threads
    │   └── skills/
    │       └── resolve-copilot-pr-feedback/
    │           └── SKILL.md
    ├── suggest-next-issue/         # Issue prioritization skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── suggest-next-issue/
    │           └── SKILL.md
    ├── write-shell-scripts/        # Bash style guide skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── write-shell-scripts/
    │           ├── SKILL.md
    │           └── references/
    │               └── BASH.md
    └── clean-up-agent-config/      # Agent config cleanup skill
        ├── .claude-plugin/
        │   └── plugin.json
        └── skills/
            └── clean-up-agent-config/
                ├── SKILL.md
                └── references/
                    ├── agent-instruction-files.md
                    └── agent-config-files.md
```

## Development

When adding new plugins:

1. Create the plugin directory under `plugins/`
2. Add a `.claude-plugin/plugin.json` with metadata
3. Register the plugin in `.claude-plugin/marketplace.json`
4. Update README.md with the new plugin description

## License

MIT License - see LICENSE file for details.
