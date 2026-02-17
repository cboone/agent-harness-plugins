# Claude Code Plugins

## Project Overview

This repository contains plugins (hooks and skills) for Claude Code.

## Structure

```text
cboone-cc-plugins/
├── .claude-plugin/
│   └── marketplace.json            # Plugin registry for this repository
└── plugins/
    ├── block-rm-rf/                 # Recursive rm blocker hook
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── hooks/
    │   │   └── hooks.json
    │   └── scripts/
    │       └── check-rm
    ├── commit/                      # Smart git commit skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── commit/
    │           └── SKILL.md
    ├── create-plugin/               # Plugin creation guide skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── create-plugin/
    │           ├── SKILL.md
    │           └── references/
    │               ├── hooks-json.md
    │               ├── marketplace-json.md
    │               ├── plugin-json.md
    │               ├── readme-updates.md
    │               ├── scripts.md
    │               └── skill-md.md
    ├── create-worktree/              # General worktree creation skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── create-worktree/
    │           └── SKILL.md
    ├── create-worktree-from-issue/  # Issue-to-worktree skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── create-worktree-from-issue/
    │           └── SKILL.md
    ├── merge-main/                  # Base branch merge skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── merge-main/
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
    ├── pr/                          # Commit, push, and create PR skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── pr/
    │           └── SKILL.md
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

### README ToC Format

The README table of contents uses **one entry per line** to prevent merge conflicts when multiple branches add plugins simultaneously. Skills are organized into subcategories (Agents, Workflow, Languages). Each continuation link starts with `| ` (pipe-space) at the beginning of the line:

```markdown
**Skills**
<br>_Agents_
[Skill A](#skill-a)
| [Skill B](#skill-b)
<br>_Workflow_
[Skill C](#skill-c)
| [Skill D](#skill-d)
<br>_Languages_
[Skill E](#skill-e)
<br>**Hooks**
[Hook A](#hook-a)
```

Rules:
- Never put multiple links on the same line.
- The first link in each subcategory has no leading pipe; subsequent links start with `| `.
- Subcategory labels use `<br>_Name_` format.
- Labels have no trailing colons.

### Versioning

This repository uses two levels of semver versioning:

**Marketplace `metadata.version`** (in `.claude-plugin/marketplace.json`):
- Bump **minor** when adding or removing a plugin (the catalog changed)
- Do NOT bump for changes to existing plugin content

**Individual plugin `version`** (in `plugin.json` and mirrored in `marketplace.json`):
- **Patch**: bug fixes, wording tweaks, prompt adjustments
- **Minor**: new capabilities or meaningful behavior changes
- **Major**: breaking changes (e.g., removing or restructuring a skill)
- New plugins start at `1.0.0`
- The version in `plugin.json` and its `marketplace.json` entry must always match

**Version checks on branch operations**: After merging, rebasing, or before creating a PR, always review `plugin.json` and `marketplace.json` for version conflicts or missed bumps. Another branch may have already incremented a version, so verify that all version numbers are correct and consistent.

## License

MIT License - see LICENSE file for details.
