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
    ├── add-goreleaser-homebrew/     # GoReleaser + Homebrew tap setup skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── add-goreleaser-homebrew/
    │           ├── SKILL.md
    │           └── references/
    │               ├── conditional-features.md
    │               ├── goreleaser-base.md
    │               ├── homebrew-tap-token.md
    │               ├── makefile-targets.md
    │               ├── migration-guide.md
    │               └── release-workflow.md
    ├── add-scrut-cli-tests/         # Scrut CLI integration testing skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── add-scrut-cli-tests/
    │           └── SKILL.md
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
    ├── check-zsh-scripts/           # Zsh script checking skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── check-zsh-scripts/
    │           ├── SKILL.md
    │           └── references/
    │               └── tools/
    │                   ├── checkbashisms.md
    │                   ├── setopt-warnings.md
    │                   ├── shellcheck.md
    │                   ├── shellharden.md
    │                   ├── shfmt.md
    │                   ├── zcompile.md
    │                   └── zsh-n.md
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
    │               ├── command-md.md
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
    ├── manage-repo-licensing/       # REUSE/SPDX licensing skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── manage-repo-licensing/
    │           ├── SKILL.md
    │           └── references/
    │               ├── commit-sequence.md
    │               ├── example-flows.md
    │               ├── file-type-matrix.md
    │               ├── license-split.yaml
    │               ├── NOTICE.template.md
    │               ├── reference-material-text.md
    │               └── verification.md
    ├── merge-main/                  # Base branch merge skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── merge-main/
    │           └── SKILL.md
    ├── write-formalization-roadmap/ # Formalization roadmap structure skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── write-formalization-roadmap/
    │           ├── SKILL.md
    │           └── references/
    │               ├── comprehensive/
    │               │   ├── anti-patterns.md
    │               │   ├── conventions.md
    │               │   ├── document-structure.md
    │               │   ├── examples.md
    │               │   └── milestone-anatomy.md
    │               └── essential/
    │                   └── checklist.md
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
    ├── rebase-onto-main/             # Base branch rebase skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── rebase-onto-main/
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
    ├── scaffold-new-repo/          # New repository scaffolding skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── scaffold-new-repo/
    │           ├── SKILL.md
    │           └── references/
    │               ├── agents-md.md
    │               ├── changelog.md
    │               ├── copilot-instructions.md
    │               ├── gitignore-templates.md
    │               ├── license.md
    │               └── readme.md
    ├── scaffold-go-cli/            # Go CLI project scaffolding skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── scaffold-go-cli/
    │           ├── SKILL.md
    │           └── references/
    │               ├── ci-workflow.md
    │               ├── gitignore.md
    │               ├── go-mod.md
    │               ├── goreleaser.md
    │               ├── homebrew-tap-token.md
    │               ├── license.md
    │               ├── main-go.md
    │               ├── makefile.md
    │               ├── readme.md
    │               ├── release-workflow.md
    │               ├── root-go-with-viper.md
    │               └── root-go-without-viper.md
    ├── scaffold-go-library/        # Go library project scaffolding skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── scaffold-go-library/
    │           ├── SKILL.md
    │           └── references/
    │               ├── ci-workflow.md
    │               ├── doc-go.md
    │               ├── editorconfig.md
    │               ├── gitignore.md
    │               ├── go-mod.md
    │               ├── golangci.md
    │               ├── goreleaser.md
    │               ├── license.md
    │               ├── makefile.md
    │               ├── package-file.md
    │               ├── readme.md
    │               └── release-workflow.md
    ├── scaffold-rust-cli/          # Rust CLI project scaffolding skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── scaffold-rust-cli/
    │           ├── SKILL.md
    │           └── references/
    │               ├── cargo-toml.md
    │               ├── ci-workflow.md
    │               ├── ci-workflow-macos-only.md
    │               ├── cliff.md
    │               ├── deny.md
    │               ├── gitignore.md
    │               ├── license.md
    │               ├── main-rs.md
    │               ├── main-rs-with-clap.md
    │               ├── makefile.md
    │               ├── readme.md
    │               ├── release-workflow.md
    │               ├── release-workflow-macos-only.md
    │               ├── rust-toolchain.md
    │               ├── rustfmt.md
    │               └── typos.md
    ├── setup-ci/                   # GitHub Actions CI setup skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── setup-ci/
    │           ├── SKILL.md
    │           └── references/
    │               ├── ci-go-cli.md
    │               ├── ci-go-library.md
    │               ├── ci-javascript.md
    │               ├── ci-multi-language.md
    │               ├── ci-python.md
    │               ├── ci-ruby.md
    │               ├── ci-rust.md
    │               ├── ci-shell.md
    │               ├── ci-zig.md
    │               ├── ci-zsh.md
    │               ├── makefile-go-cli.md
    │               ├── makefile-go-library.md
    │               ├── makefile-javascript.md
    │               ├── makefile-python.md
    │               ├── makefile-ruby.md
    │               ├── makefile-rust.md
    │               ├── makefile-shell.md
    │               ├── makefile-zig.md
    │               └── makefile-zsh.md
    ├── setup-secret-scanning/      # Secret scanning setup skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── setup-secret-scanning/
    │           ├── SKILL.md
    │           └── references/
    │               ├── gitleaks-config.md
    │               ├── gitleaks-workflow.md
    │               └── trufflehog-workflow.md
    ├── setup-installers/           # Installer/distribution setup skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── setup-installers/
    │           └── SKILL.md
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
    ├── update-docs-reminder/        # Documentation update reminder hook
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   ├── hooks/
    │   │   └── hooks.json
    │   └── scripts/
    │       └── check-docs
    ├── update-everything/           # Audit and update repo against latest templates
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── update-everything/
    │           └── SKILL.md
    ├── update-review/               # Review update synthesizer skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── update-review/
    │           └── SKILL.md
    ├── write-latex/                 # LaTeX typesetting style guide skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── write-latex/
    │           ├── SKILL.md
    │           └── references/
    │               ├── comprehensive/
    │               │   ├── bibliography.md
    │               │   ├── common-mistakes.md
    │               │   ├── document-conventions.md
    │               │   ├── figures-and-floats.md
    │               │   ├── iso-conventions.md
    │               │   ├── macros-and-cross-refs.md
    │               │   ├── math-typesetting.md
    │               │   ├── packages.md
    │               │   ├── spacing-and-alignment.md
    │               │   └── tables.md
    │               └── essential/
    │                   └── checklist.md
    ├── write-lean-code/             # Lean 4 and Mathlib style guide skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── write-lean-code/
    │           ├── SKILL.md
    │           └── references/
    │               ├── comprehensive/
    │               │   ├── build-infrastructure.md
    │               │   ├── general-programming.md
    │               │   ├── mathlib-api-discovery.md
    │               │   ├── mathlib.md
    │               │   ├── metaprogramming.md
    │               │   ├── naming.md
    │               │   ├── pfr-downstream.md
    │               │   ├── proof-style.md
    │               │   └── style-and-formatting.md
    │               └── essential/
    │                   └── checklist.md
    ├── write-lean-tests/            # Lean 4 API regression tests skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── write-lean-tests/
    │           └── SKILL.md
    ├── write-markdown/              # Markdown style guide skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── write-markdown/
    │           ├── SKILL.md
    │           └── references/
    │               └── MARKDOWN.md
    ├── write-math/                  # Mathematical writing and exposition skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── write-math/
    │           ├── SKILL.md
    │           └── references/
    │               ├── comprehensive/
    │               │   ├── citations-and-references.md
    │               │   ├── english-usage.md
    │               │   ├── notation.md
    │               │   ├── paper-structure.md
    │               │   ├── reader-centered-writing.md
    │               │   ├── revision-and-process.md
    │               │   └── theorems-and-proofs.md
    │               └── essential/
    │                   └── checklist.md
    ├── write-pandoc-markdown/       # Pandoc Markdown for academic papers skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── write-pandoc-markdown/
    │           ├── SKILL.md
    │           └── references/
    │               ├── comprehensive/
    │               │   ├── build-pipeline.md
    │               │   ├── cross-references.md
    │               │   ├── math-and-citations.md
    │               │   ├── raw-latex-blocks.md
    │               │   └── yaml-frontmatter.md
    │               └── essential/
    │                   └── checklist.md
    ├── write-scrut-tests/           # Scrut test style guide skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── write-scrut-tests/
    │           ├── SKILL.md
    │           └── references/
    │               ├── SCRUT.md
    │               └── zsh-plugin-testing.md
    ├── write-bash-scripts/        # Bash style guide skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── write-bash-scripts/
    │           ├── SKILL.md
    │           └── references/
    │               └── BASH.md
    ├── write-zsh-scripts/          # Zsh style guide skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── write-zsh-scripts/
    │           ├── SKILL.md
    │           └── references/
    │               ├── ZSH.md
    │               └── completions.md
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

If the plugin uses hook events that Codex CLI does not support (`Notification`, `PreCompact`, `SubagentStop`, `SessionEnd`), add a `.codex-plugin/plugin.json` sibling to `.claude-plugin/plugin.json` that points at a codex-compatible hooks file via the `hooks` field. See `plugins/notify/` for the pattern. Codex's strict hook schema (`PreToolUse`, `PermissionRequest`, `PostToolUse`, `SessionStart`, `UserPromptSubmit`, `Stop`) will reject the entire `hooks.json` if any unsupported event is present.

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

This repository uses two levels of versioning:

**Marketplace `metadata.version`** (in `.claude-plugin/marketplace.json`):

- This is a catalog state tag, not SemVer.
- Format: `catalog-M<major-sum>-m<minor-sum>-p<patch-sum>-n<plugin-count>`
- `M`: sum of all plugin major versions
- `m`: sum of all plugin minor versions
- `p`: sum of all plugin patch versions
- `n`: number of marketplace plugins
- Do not normalize or carry between components.
- Recompute it from `.plugins[].version` whenever any marketplace plugin version changes.

**Individual plugin `version`** (in `plugin.json` and mirrored in `marketplace.json`):

- **Patch**: bug fixes, wording tweaks, prompt adjustments
- **Minor**: new capabilities or meaningful behavior changes
- **Major**: breaking changes (e.g., removing or restructuring a skill)
- New plugins start at `1.0.0`
- The version in `plugin.json` and its `marketplace.json` entry must always match

**Version checks on branch operations**: After merging, rebasing, or before creating a PR, use the `check-versions` skill to verify version correctness. Another branch may have already incremented a version, so always check.

## License

MIT License - see LICENSE file for details.
