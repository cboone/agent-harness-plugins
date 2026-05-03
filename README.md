# Claude Code Plugins

A collection of plugins (skills, commands, and hooks) for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [OpenAI's Codex CLI](https://developers.openai.com/codex/cli), and [OpenCode](https://opencode.ai/docs/skills/), from [Christopher Boone](https://cboone.github.io).

## Install

### Claude Code

From within `claude`, open the plugins manager via `/plugin`, tab to `Marketplace`, and hit `enter` on `Add Marketplace`. Type `cboone/cboone-cc-plugins`, then choose which plugins to install.

Or, from within `claude`:

```bash
/plugin marketplace add cboone/cboone-cc-plugins
```

### Codex CLI

```bash
codex plugin marketplace add cboone/cboone-cc-plugins
```

See [Using with Codex CLI](#using-with-codex-cli) below for the `plugin_hooks` feature flag, marketplace upgrade and remove semantics, and Codex-specific limitations.

### OpenCode

```bash
export OPENCODE_CONFIG_DIR="$(pwd)/dist/opencode"
```

See [Using with OpenCode](#using-with-opencode) below for mirror regeneration and known limitations.

## Skills

Each skill links to its own README. The `Trigger` column shows the slash command. Some style-guide skills also activate automatically when you touch their target file types; see the per-plugin README for activation rules.

### Git

| Plugin | Trigger | What it does |
| --- | --- | --- |
| [Commit](./plugins/commit/README.md) | `/commit` | Smart, context-aware git commits with conventional commit messages and plan awareness. |
| [Merge Main](./plugins/merge-main/README.md) | `/merge-main` | Fetch and merge the base branch into the current feature branch with automatic conflict resolution. |
| [PR](./plugins/pr/README.md) | `/pr` | Lint, commit, push, and create a pull request in one step with no prompts. |
| [Rebase Onto Main](./plugins/rebase-onto-main/README.md) | `/rebase-onto-main` | Fetch and rebase the current feature branch onto the base branch with automatic conflict resolution and force-with-lease push. |
| [Release](./plugins/release/README.md) | `/release` | Prepare a versioned release or Claude Code marketplace catalog state tag: update release files, create a release commit, tag locally, and optionally publish a GitHub Release. |
| [Review Branch](./plugins/review-branch/README.md) | `/review-branch` | Review and evaluate all work done on the current branch: summarize changes, assess plan compliance, and evaluate code quality. |
| [Use Git](./plugins/use-git/README.md) | `/use-git` | Git and GitHub CLI conventions for Claude Code: tmpfile patterns, HEREDOC commits, GPG signing, safe push practices, and permission-prompt avoidance. |

**External tools:**

- *PR:* [`gh`](https://cli.github.com/)
- *Merge Main, Rebase Onto Main:* [`gh`](https://cli.github.com/) (falls back to `git remote show origin` if unavailable)
- *Release:* [`jq`](https://jqlang.org/) for marketplace catalog releases; [`gh`](https://cli.github.com/) optional for GitHub Release creation

### Issues and Worktrees

| Plugin | Trigger | What it does |
| --- | --- | --- |
| [Address Issue](./plugins/address-issue/README.md) | `/address-issue` | Fetch a GitHub issue, plan the work, execute changes, and commit with issue references. |
| [Create Issue](./plugins/create-issue/README.md) | `/create-issue` | Create GitHub issues using tmpfiles to avoid permission prompts from large multiline Bash arguments. |
| [Create Worktree](./plugins/create-worktree/README.md) | `/create-worktree` | Create a git worktree, branch, and tmux window with a task prompt using workmux. |
| [Create Worktree from Issue](./plugins/create-worktree-from-issue/README.md) | `/create-worktree-from-issue` | Find a GitHub issue and create a worktree, branch, and tmux window for working on it, with issue context injected as a task prompt. |
| [Suggest Next Issue](./plugins/suggest-next-issue/README.md) | `/suggest-next-issue` | Review open GitHub issues and recommend what to work on next with prioritized reasoning. |

**External tools:**

- *Address Issue, Create Issue, Suggest Next Issue:* [`gh`](https://cli.github.com/)
- *Create Worktree:* [`workmux`](https://github.com/paiml/workmux)
- *Create Worktree from Issue:* [`gh`](https://cli.github.com/), [`workmux`](https://github.com/paiml/workmux)

### Code Review

| Plugin | Trigger | What it does |
| --- | --- | --- |
| [Address Review](./plugins/address-review/README.md) | `/address-review <path>` | Parse a review document for actionable feedback, work through items systematically, and track resolution progress. |
| [Resolve Copilot PR Feedback](./plugins/resolve-copilot-pr-feedback/README.md) | `/resolve-copilot-pr-feedback` | Process and resolve GitHub Copilot automated PR review comments. |
| [Update Review](./plugins/update-review/README.md) | `/update-review` | Find the latest branch review, assess commits made since, and update the review document with a synthesized reassessment. |

### Code Quality

| Plugin | Trigger | What it does |
| --- | --- | --- |
| [Add Scrut CLI Tests](./plugins/add-scrut-cli-tests/README.md) | `/add-scrut-cli-tests` | Set up scrut snapshot-based CLI integration testing for a CLI project. |
| [Check Zsh Scripts](./plugins/check-zsh-scripts/README.md) | `/check-zsh-scripts` | Check and evaluate zsh scripts using shellcheck, shfmt, shellharden, zsh -n, zcompile, setopt warn_create_global/warn_nested_var, and checkbashisms. |
| [Handle Secrets](./plugins/handle-secrets/README.md) | `/handle-secrets` | Best practices for handling user-provided secrets in CLI tools: secure input methods, credential storage, secret masking, and language-specific libraries. |
| [Lint and Fix](./plugins/lint-and-fix/README.md) | `/lint-and-fix` | Detect project linters and formatters, run them with auto-fix, resolve remaining issues, then commit and push the fixes. |
| [Setup Linters](./plugins/setup-linters/README.md) | `/setup-linters` | Detect project languages, recommend linters and formatters, install them, and generate config files, including Pandoc-academic Markdown presets. |
| [Write Bash Scripts](./plugins/write-bash-scripts/README.md) | `/write-bash-scripts` | Bash style conventions for creating and editing Bash scripts. |
| [Write Go Code](./plugins/write-go-code/README.md) | `/write-go-code` | Go code style guide based on Google Go Style Guide, Effective Go, Code Review Comments, and Cobra CLI behavior. |
| [Write LaTeX](./plugins/write-latex/README.md) | `/write-latex` | LaTeX mathematical typesetting style guide based on AMS, IEEE, ISO 80000-2, and Knuth conventions. |
| [Write Lean Code](./plugins/write-lean-code/README.md) | `/write-lean-code` | Lean 4 style guide and Mathlib conventions for naming, proofs, formatting, and metaprogramming. |
| [Write Lean Tests](./plugins/write-lean-tests/README.md) | `/write-lean-tests` | Conventions for compile-time, example-based Lean 4 API regression tests that mirror a library's public surface. |
| [Write Scrut Tests](./plugins/write-scrut-tests/README.md) | `/write-scrut-tests` | Scrut test style conventions for writing and editing scrut test files for CLI binaries and zsh plugins. |
| [Write Zsh Scripts](./plugins/write-zsh-scripts/README.md) | `/write-zsh-scripts` | Zsh style conventions for creating and editing zsh scripts, configurations, and completions. |

**External tools:**

- *Add Scrut CLI Tests:* [`scrut`](https://github.com/facebookincubator/scrut) (Makefile checks for availability and provides install instructions)
- *Check Zsh Scripts:* [`shellcheck`](https://www.shellcheck.net/), [`shfmt`](https://github.com/mvdan/sh), [`shellharden`](https://github.com/anordal/shellharden), [`checkbashisms`](https://packages.debian.org/devscripts)

### Writing

| Plugin | Trigger | What it does |
| --- | --- | --- |
| [Write Formalization Roadmap](./plugins/write-formalization-roadmap/README.md) | `/write-formalization-roadmap` | Document-structure guide for multi-milestone formalization roadmaps in Lean, Rocq, Isabelle, HOL, and other proof assistants. |
| [Write Markdown](./plugins/write-markdown/README.md) | `/write-markdown` | Markdown style conventions for creating and editing Markdown files. |
| [Write Math](./plugins/write-math/README.md) | `/write-math` | Mathematical writing and exposition guide based on Tao, Knuth, Halmos, and other leading references. |
| [Write Pandoc Markdown](./plugins/write-pandoc-markdown/README.md) | `/write-pandoc-markdown` | Pandoc-flavored Markdown conventions for academic papers with LaTeX output. |

### Scaffolding

| Plugin | Trigger | What it does |
| --- | --- | --- |
| [Add Community Files](./plugins/add-community-files/README.md) | `/add-community-files` | Add standard community files to a project: CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, and PR template. |
| [Bootstrap Project](./plugins/bootstrap-project/README.md) | `/bootstrap-project` | Assess a repository, determine what scaffolding and setup tools are needed, present a plan, and execute them in the correct order. |
| [Manage Repo Licensing](./plugins/manage-repo-licensing/README.md) | `/manage-repo-licensing` | Bootstrap, audit, and maintain REUSE-style mixed-license coverage in a repository: LICENSES/, NOTICE, REUSE.toml, SPDX headers, and reuse lint cleanliness. |
| [Refresh Project Scaffolding](./plugins/refresh-project-scaffolding/README.md) | `/refresh-project-scaffolding` | Refresh existing project scaffolding against the latest plugin templates. |
| [Scaffold Go CLI](./plugins/scaffold-go-cli/README.md) | `/scaffold-go-cli` | Scaffold a complete Go CLI project with Cobra, GoReleaser, GitHub Actions, and Homebrew tap support. |
| [Scaffold Go Library](./plugins/scaffold-go-library/README.md) | `/scaffold-go-library` | Scaffold a Go library project with GoReleaser changelog releases, golangci-lint, GitHub Actions CI/CD, and Makefile. |
| [Scaffold New Repo](./plugins/scaffold-new-repo/README.md) | `/scaffold-new-repo` | Scaffold the universal boilerplate for a new repository: LICENSE, README, CHANGELOG, .gitignore, agent config files, and a plans directory. |
| [Scaffold Rust CLI](./plugins/scaffold-rust-cli/README.md) | `/scaffold-rust-cli` | Scaffold a complete Rust CLI project with Cargo, cargo-deny, cargo-nextest, git-cliff, GitHub Actions CI/CD, and Makefile. |

**External tools:**

- *Manage Repo Licensing:* [`reuse`](https://reuse.software/). Install via [Homebrew](https://brew.sh): `brew install reuse`

### CI and Release

| Plugin | Trigger | What it does |
| --- | --- | --- |
| [Add GoReleaser Homebrew](./plugins/add-goreleaser-homebrew/README.md) | `/add-goreleaser-homebrew` | Add GoReleaser and Homebrew tap publishing to an existing Go CLI project, with conditional support for completions, man pages, and macOS-only builds. |
| [Optimize Runner Usage](./plugins/optimize-runner-usage/README.md) | `/optimize-runner-usage` | Add paths-ignore, concurrency groups, and timeout-minutes to existing GitHub Actions workflows. |
| [Pin Everything](./plugins/pin-everything/README.md) | `/pin-everything` | Pin every version surface in a repository (action SHAs, packageManager integrity digests, dependency exact-pins, runtime version files, install commands) for one-shot supply-chain hardening. |
| [Setup CI](./plugins/setup-ci/README.md) | `/setup-ci` | Set up GitHub Actions CI with test, lint, format, and vulnerability check jobs, plus matching Makefile targets. |
| [Setup Installers](./plugins/setup-installers/README.md) | `/setup-installers` | Set up installer and distribution methods for Go, Swift, Rust, and Zig projects: Homebrew tap, go/cargo install, and release workflow. |
| [Setup Secret Scanning](./plugins/setup-secret-scanning/README.md) | `/setup-secret-scanning` | Set up secret scanning with gitleaks and TruffleHog GitHub Actions workflows and optional gitleaks configuration. |
| [Upgrade Everything](./plugins/upgrade-everything/README.md) | `/upgrade-everything` | Assess every version reference in a repository, evaluate available upgrades with repo-specific risk and reward, and present selectable upgrade options. |

**External tools:**

- *Pin Everything:* [`gh`](https://cli.github.com/), [`jq`](https://jqlang.org/); optional [`corepack`](https://github.com/nodejs/corepack) (only when pinning Yarn or pnpm) and [`reuse`](https://reuse.software/) (only in REUSE-licensed repos)

### Agents

| Plugin | Trigger | What it does |
| --- | --- | --- |
| [Clean Up Agent Config](./plugins/clean-up-agent-config/README.md) | `/clean-up-agent-config` | Review and reorganize AI coding agent configuration and instruction files across Claude Code, Codex, Copilot, and OpenCode. |
| [Create Plugin](./plugins/create-plugin/README.md) | `/create-plugin` | Guide for creating new plugins in this repository with consistent structure and conventions. |

## Hooks

Hooks are event-driven; they have no slash-command trigger.

| Plugin | What it does |
| --- | --- |
| [Notify (macOS)](./plugins/notify/README.md) | Sends macOS notifications when Claude Code, OpenCode, or Codex CLI finishes a task or needs your attention. |
| [Update Docs Reminder](./plugins/update-docs-reminder/README.md) | Reminds you to update documentation when a commit includes significant code changes. |

**External tools:**

- *Notify:* [`alerter`](https://github.com/vjeantet/alerter). Install via [Homebrew](https://brew.sh): `brew install vjeantet/tap/alerter`
- *Update Docs Reminder:* [`jq`](https://jqlang.org/)

## Using with Codex CLI

This repository works as a native [Codex CLI](https://developers.openai.com/codex/cli) plugin marketplace. Codex reads the generated `.agents/plugins/marketplace.json`, which points at committed plugin roots under `dist/codex/plugins/`. Those generated roots mirror the canonical `plugins/*` directories but replace skill frontmatter descriptions with shorter Codex-facing descriptions from the marketplace entries. The canonical `plugins/*/skills/*/SKILL.md` files keep their richer Claude Code trigger descriptions.

For per-plugin metadata Codex prefers `.codex-plugin/plugin.json` when present and falls back to `.claude-plugin/plugin.json` otherwise. Hook registration requires a `.codex-plugin/plugin.json` with a non-empty `hooks` path (for example `"hooks": "./hooks/hooks.json"`); this lets hook plugins point Codex at a Codex-compatible hook file. Codex exposes `${CLAUDE_PLUGIN_ROOT}` to plugin-bundled hook commands for backward compatibility with existing Claude Code plugins.

Codex CLI currently manages plugins at the marketplace level. In Codex CLI 0.128.0, `codex plugin` exposes the `marketplace` subcommand with `add`, `upgrade`, and `remove`; it does not expose a separate `codex plugin install` subcommand.

Enable plugin-bundled hooks once per host so the `notify` and `update-docs-reminder` hooks fire:

```bash
codex features enable plugin_hooks
```

Plugin-bundled hooks are gated behind the `plugin_hooks` feature flag (listed as `under development` in Codex CLI 0.128.0). Without it the marketplace add and skill discovery still work, but `hooks/hooks.json` files inside installed plugins are silently ignored.

Refresh a Git-backed marketplace after pulling repository updates or after a published release:

```bash
codex plugin marketplace upgrade cboone-cc-plugins
```

`codex plugin marketplace upgrade` and `remove` take the marketplace name (`cboone-cc-plugins`, derived from the repository name), not the `owner/repo` identifier used by `add`.

When changing plugin metadata, skills, hooks, scripts, or references, regenerate the Codex marketplace with `bin/build-codex-marketplace` and commit `.agents/plugins/marketplace.json` plus `dist/codex/`. For a local-path marketplace, restart Codex after changing plugin files so it can rebuild cached plugin copies from the local source.

Remove the configured marketplace by name:

```bash
codex plugin marketplace remove cboone-cc-plugins
```

### Codex CLI known limitations

- **Plugin-bundled hooks are gated behind a feature flag.** `plugin_hooks` is `under development` in Codex CLI 0.128.0 and is `false` by default. Run `codex features enable plugin_hooks` once before expecting `notify` or `update-docs-reminder` to fire on Codex; see above.
- **`Notification` and `PreCompact` hook events are not supported.** Codex CLI's hook schema only supports `PreToolUse`, `PermissionRequest`, `PostToolUse`, `SessionStart`, `UserPromptSubmit`, and `Stop`. The `notify` plugin therefore wires only the turn-completion notification on Codex (its other Claude Code events have no Codex equivalent). For idle, elicitation, and permission alerts, enable Codex's built-in `tui.notifications = true` in `~/.codex/config.toml`. See the [`notify` plugin README](./plugins/notify/README.md) for details.
- **No custom prompts shipped.** Codex's `~/.codex/prompts/` mechanism is officially deprecated in favor of skills. This repository ships skills (and hooks), not prompts.

## Using with OpenCode

This repository also works with the skills, commands, and hooks in [OpenCode](https://opencode.ai) via a committed mirror at [`dist/opencode/`](./dist/opencode/).

When adding or removing a plugin, regenerate the mirror with `bin/build-opencode-mirror` and commit the result. CI fails if the mirror drifts from the source plugins. Hooks are mirrored to `dist/opencode/plugins/` as TypeScript plugins, sourced from each plugin's `opencode/index.ts`.

### OpenCode known limitations

- **`${CLAUDE_PLUGIN_ROOT}` references do not expand.** Some commands and one skill use Claude Code's `@${CLAUDE_PLUGIN_ROOT}/references/...` pattern to inline reference files at runtime. OpenCode does not expand this variable, so those inclusions appear to the agent as literal path strings rather than inlined content. The inline workflow text in each affected file still loads correctly. Affected commands: `/add-goreleaser-homebrew`, `/scaffold-go-cli`, `/scaffold-go-library`, `/scaffold-new-repo`, `/scaffold-rust-cli`, `/setup-ci`, `/setup-secret-scanning`. Affected skill: `create-plugin`. For full fidelity in these cases, run them in Claude Code.
- **Hook event parity is approximate.** OpenCode's event model collapses several distinct Claude Code notification matchers (`idle_prompt`, `elicitation_dialog`, `permission_prompt`) and the `PreCompact` event is mapped to an experimental OpenCode hook. See each hook's README for the specific mapping.

## License

[MIT License](./LICENSE). TL;DR: Do whatever you want with this software, just keep the copyright notice included. The authors aren't liable if something goes wrong.
