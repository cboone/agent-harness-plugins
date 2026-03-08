# Claude Code Plugins

## Project Overview

This repository contains plugins (hooks and skills) for Claude Code.

## Structure

```text
cboone-cc-plugins/
├── .claude-plugin/
│   └── marketplace.json            # Plugin registry for this repository
└── plugins/
    ├── add-community-files/          # Community files skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── add-community-files/
    │           ├── SKILL.md
    │           └── references/
    │               ├── code-of-conduct.md
    │               ├── contributing.md
    │               ├── pr-template.md
    │               └── security.md
    ├── add-goreleaser-homebrew/     # GoReleaser + Homebrew tap setup command
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── commands/
    │       └── add-goreleaser-homebrew.md
    ├── add-scrut-cli-tests/         # Scrut CLI integration testing command
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── commands/
    │       └── add-scrut-cli-tests.md
    ├── address-review/              # Review feedback resolver skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── address-review/
    │           └── SKILL.md
    ├── block-rm-rf/                 # Recursive rm blocker hook
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   ├── hooks/
    │   │   └── hooks.json
    │   └── scripts/
    │       └── check-rm
    ├── bootstrap-project/           # Full project bootstrap skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── bootstrap-project/
    │           ├── SKILL.md
    │           └── references/
    │               └── overlap-rules.md
    ├── commit/                      # Smart git commit skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── commit/
    │           └── SKILL.md
    ├── create-issue/                # GitHub issue creation skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── create-issue/
    │           └── SKILL.md
    ├── create-plugin/               # Plugin creation guide skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
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
    │   ├── README.md
    │   └── skills/
    │       └── create-worktree/
    │           └── SKILL.md
    ├── create-worktree-from-issue/  # Issue-to-worktree skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
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
    │   ├── README.md
    │   └── skills/
    │       └── lint-and-fix/
    │           └── SKILL.md
    ├── merge-main/                  # Base branch merge skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── merge-main/
    │           └── SKILL.md
    ├── write-go-code/              # Go style guide skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
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
    │   ├── README.md
    │   └── skills/
    │       └── pr/
    │           └── SKILL.md
    ├── release/                     # Versioned release preparation skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── release/
    │           ├── SKILL.md
    │           └── references/
    │               ├── changelog-format.md
    │               ├── conventional-commits.md
    │               ├── doc-checklist.md
    │               ├── project-types.md
    │               └── version-patterns.md
    ├── notify/                     # Notification hooks plugin
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   ├── hooks/
    │   │   └── hooks.json
    │   └── scripts/
    │       └── notify
    ├── review-branch/               # Branch work summarizer skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── review-branch/
    │           └── SKILL.md
    ├── resolve-copilot-pr-feedback/ # Copilot PR feedback resolver skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   ├── scripts/
    │   │   └── resolve-copilot-threads
    │   └── skills/
    │       └── resolve-copilot-pr-feedback/
    │           └── SKILL.md
    ├── scaffold-new-repo/          # New repository scaffolding command
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── commands/
    │       └── scaffold-new-repo.md
    ├── scaffold-go-cli/            # Go CLI project scaffolding command
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── commands/
    │       └── scaffold-go-cli.md
    ├── scaffold-go-library/        # Go library project scaffolding command
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── commands/
    │       └── scaffold-go-library.md
    ├── setup-ci/                   # GitHub Actions CI setup command
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── commands/
    │       └── setup-ci.md
    ├── setup-secret-scanning/      # Secret scanning setup command
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── commands/
    │       └── setup-secret-scanning.md
    ├── setup-installers/           # Installer/distribution setup command
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── commands/
    │       └── setup-installers.md
    ├── setup-linters/              # Linter and formatter setup skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── setup-linters/
    │           ├── SKILL.md
    │           └── references/
    │               ├── checklist.md
    │               ├── languages/
    │               │   ├── go.md
    │               │   ├── javascript.md
    │               │   ├── python.md
    │               │   ├── ruby.md
    │               │   ├── rust.md
    │               │   └── shell.md
    │               └── tools/
    │                   ├── actionlint.md
    │                   ├── editorconfig.md
    │                   ├── github-actions-ci.md
    │                   ├── hadolint.md
    │                   ├── knip.md
    │                   ├── markdownlint.md
    │                   ├── prettier.md
    │                   ├── stylelint.md
    │                   ├── taplo.md
    │                   └── yamllint.md
    ├── suggest-next-issue/         # Issue prioritization skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── suggest-next-issue/
    │           └── SKILL.md
    ├── use-git/                     # Git and gh CLI conventions skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── use-git/
    │           ├── SKILL.md
    │           └── references/
    │               ├── common-operations.md
    │               ├── diff-output.md
    │               ├── heredoc-pattern.md
    │               ├── safety-rules.md
    │               └── tmpfile-pattern.md
    ├── update-everything/           # Audit and update repo against latest templates
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── commands/
    │       └── update-everything.md
    ├── write-markdown/              # Markdown style guide skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── write-markdown/
    │           ├── SKILL.md
    │           └── references/
    │               └── MARKDOWN.md
    ├── write-scrut-tests/           # Scrut test style guide skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── write-scrut-tests/
    │           ├── SKILL.md
    │           └── references/
    │               └── SCRUT.md
    ├── write-shell-scripts/        # Bash style guide skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── write-shell-scripts/
    │           ├── SKILL.md
    │           └── references/
    │               └── BASH.md
    └── clean-up-agent-config/      # Agent config cleanup skill
        ├── .claude-plugin/
        │   └── plugin.json
        ├── README.md
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
1. Add a `.claude-plugin/plugin.json` with metadata
1. Register the plugin in `.claude-plugin/marketplace.json`
1. Create a per-plugin `README.md` in the plugin directory
1. Update the root `README.md` with the new plugin description and details link

### README ToC Format

The README table of contents uses **one entry per line** to prevent merge conflicts when multiple branches add plugins simultaneously. Skills are organized into subcategories (Git, Issues and Worktrees, Code Review, Code Quality, Scaffolding, Agents). Hooks are organized into subcategories (Security, Workflow). Each continuation link starts with `∙` (middle dot, space) at the beginning of the line:

```markdown
**Skills**
<br>Git:
[Skill A](#skill-a)
∙ [Skill B](#skill-b)
<br>Issues and Worktrees:
[Skill C](#skill-c)
<br>Code Review:
[Skill D](#skill-d)
<br>Code Quality:
[Skill E](#skill-e)
<br>Scaffolding:
[Skill F](#skill-f)
<br>Agents:
[Skill G](#skill-g)

**Hooks**
<br>Security:
[Hook A](#hook-a)
<br>Workflow:
[Hook B](#hook-b)
```

Rules:

- Never put multiple links on the same line.
- The first link in each subcategory has no leading `∙`; subsequent links start with `∙`.
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
