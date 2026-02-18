# Claude Code Plugins

## Project Overview

This repository contains plugins (hooks and skills) for Claude Code.

## Structure

```text
cboone-cc-plugins/
├── .claude-plugin/
│   └── marketplace.json            # Plugin registry for this repository
└── plugins/
    ├── address-review/              # Review feedback resolver skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── address-review/
    │           └── SKILL.md
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
    ├── handle-secrets/              # User secret handling best practices skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── handle-secrets/
    │           ├── SKILL.md
    │           └── references/
    │               ├── anti-patterns.md
    │               ├── checklist.md
    │               ├── design-patterns.md
    │               ├── language-libraries.md
    │               └── security-hierarchy.md
    ├── lint-and-fix/                # Lint and format auto-fixer skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── lint-and-fix/
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
    ├── review-branch/               # Branch work summarizer skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── review-branch/
    │           └── SKILL.md
    ├── resolve-copilot-pr-feedback/ # Copilot PR feedback resolver skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── scripts/
    │   │   └── resolve-copilot-threads
    │   └── skills/
    │       └── resolve-copilot-pr-feedback/
    │           └── SKILL.md
    ├── scaffold-new-repo/          # New repository scaffolding skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── scaffold-new-repo/
    │           ├── SKILL.md
    │           └── references/
    │               ├── agents-md.md
    │               ├── copilot-instructions-md.md
    │               ├── gitignore.md
    │               ├── license.md
    │               └── readme.md
    ├── scaffold-go-cli/            # Go CLI project scaffolding skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── scaffold-go-cli/
    │           ├── SKILL.md
    │           └── references/
    │               ├── ci-workflow.md
    │               ├── gitignore.md
    │               ├── go-mod.md
    │               ├── goreleaser.md
    │               ├── license.md
    │               ├── main-go.md
    │               ├── makefile.md
    │               ├── readme.md
    │               ├── release-workflow.md
    │               ├── root-go-viper.md
    │               └── root-go.md
    ├── setup-gitleaks/             # Gitleaks secret scanning setup skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── setup-gitleaks/
    │           ├── SKILL.md
    │           └── references/
    │               ├── config.md
    │               └── workflow.md
    ├── suggest-next-issue/         # Issue prioritization skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── suggest-next-issue/
    │           └── SKILL.md
    ├── write-markdown/              # Markdown style guide skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── write-markdown/
    │           ├── SKILL.md
    │           └── references/
    │               └── MARKDOWN.md
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

The README table of contents uses **one entry per line** to prevent merge conflicts when multiple branches add plugins simultaneously. Skills are organized into subcategories (Agents, Workflow, Languages). Hooks are organized into subcategories (Security, Workflow). Each continuation link starts with `∙ ` (middle dot, space) at the beginning of the line:

```markdown
**Skills**
<br>Agents:
[Skill A](#skill-a)
∙ [Skill B](#skill-b)
<br>Workflow:
[Skill C](#skill-c)
∙ [Skill D](#skill-d)
<br>Languages:
[Skill E](#skill-e)

**Hooks**
<br>Security:
[Hook A](#hook-a)
<br>Workflow:
[Hook B](#hook-b)
```

Rules:
- Never put multiple links on the same line.
- The first link in each subcategory has no leading `∙`; subsequent links start with `∙ `.
- Subcategory labels use `<br>Name:` format (plain text with trailing colon).
- **Skills** and **Hooks** are separated by a blank line.
- Hooks have their own subcategories (Security, Workflow).

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

**Version checks on branch operations**: After merging, rebasing, or before creating a PR, use the `check-versions` skill to verify version correctness. Another branch may have already incremented a version, so always check.

## License

MIT License - see LICENSE file for details.
