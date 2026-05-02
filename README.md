# Claude Code Plugins

A collection of plugins for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [OpenAI's Codex CLI](https://developers.openai.com/codex/cli), and [OpenCode](https://opencode.ai/docs/skills/), from [Christopher Boone](https://cboone.github.io).

**Skills**
<br>Git:
[Commit](#commit)
∙ [Merge Main](#merge-main)
∙ [PR](#pr)
∙ [Rebase Onto Main](#rebase-onto-main)
∙ [Release](#release)
∙ [Review Branch](#review-branch)
∙ [Use Git](#use-git)
<br>Issues and Worktrees:
[Address Issue](#address-issue)
∙ [Create Issue](#create-issue)
∙ [Create Worktree](#create-worktree)
∙ [Create Worktree from Issue](#create-worktree-from-issue)
∙ [Suggest Next Issue](#suggest-next-issue)
<br>Code Review:
[Address Review](#address-review)
∙ [Resolve Copilot PR Feedback](#resolve-copilot-pr-feedback)
∙ [Update Review](#update-review)
<br>Code Quality:
[Add Scrut CLI Tests](#add-scrut-cli-tests)
∙ [Check Zsh Scripts](#check-zsh-scripts)
∙ [Handle Secrets](#handle-secrets)
∙ [Lint and Fix](#lint-and-fix)
∙ [Setup Linters](#setup-linters)
∙ [Write Bash Scripts](#write-bash-scripts)
∙ [Write Go Code](#write-go-code)
∙ [Write LaTeX](#write-latex)
∙ [Write Lean Code](#write-lean-code)
∙ [Write Lean Tests](#write-lean-tests)
∙ [Write Scrut Tests](#write-scrut-tests)
∙ [Write Zsh Scripts](#write-zsh-scripts)
<br>Writing:
[Write Formalization Roadmap](#write-formalization-roadmap)
∙ [Write Markdown](#write-markdown)
∙ [Write Math](#write-math)
∙ [Write Pandoc Markdown](#write-pandoc-markdown)
<br>Scaffolding:
[Add Community Files](#add-community-files)
∙ [Bootstrap Project](#bootstrap-project)
∙ [Manage Repo Licensing](#manage-repo-licensing)
∙ [Refresh Project Scaffolding](#refresh-project-scaffolding)
∙ [Scaffold Go CLI](#scaffold-go-cli)
∙ [Scaffold Go Library](#scaffold-go-library)
∙ [Scaffold New Repo](#scaffold-new-repo)
∙ [Scaffold Rust CLI](#scaffold-rust-cli)
<br>CI and Release:
[Add GoReleaser Homebrew](#add-goreleaser-homebrew)
∙ [Optimize Runner Usage](#optimize-runner-usage)
∙ [Setup CI](#setup-ci)
∙ [Setup Installers](#setup-installers)
∙ [Setup Secret Scanning](#setup-secret-scanning)
<br>Agents:
[Clean Up Agent Config](#clean-up-agent-config)
∙ [Create Plugin](#create-plugin)

**Hooks**
<br>Workflow:
[Notify](#notify-macos)
∙ [Update Docs Reminder](#update-docs-reminder)

## Installation

From within `claude`, open the plugins manager via `/plugin`, then `tab` to `Marketplace`, and hit `enter` to `Add Marketplace`. Type `cboone/cboone-cc-plugins`, then choose which plugins you would like to install.

Or, from within `claude`, run:

```bash
/plugin marketplace add cboone/cboone-cc-plugins
```

### Using with Codex CLI

This repository is also a native [Codex CLI](https://developers.openai.com/codex/cli) plugin marketplace.

```bash
codex plugin marketplace add cboone/cboone-cc-plugins
```

See below for [more details](#using-with-codex-cli-1), including refresh commands and [known limitations](#codex-cli-known-limitations).

### Using with OpenCode

The skills, commands, and hooks also work in [OpenCode](https://opencode.ai) via a committed mirror at [`dist/opencode/`](./dist/opencode/).

```bash
export OPENCODE_CONFIG_DIR="$(pwd)/dist/opencode"
```

See below for [more details](#using-with-opencode-1) and [known limitations](#opencode-known-limitations).

## Skills

### Git

Skills for the commit-to-PR pipeline. Stage, commit, merge, review, and open pull requests without leaving the conversation.

#### Commit

Smart, context-aware git commits with conventional commit messages and plan awareness. Analyzes your diff to generate well-structured commit messages, handles staged-only vs. all changes, and supports commit-and-push workflows.

> **Trigger:** `/commit`
> **Details:** [README](./plugins/commit/README.md)

#### Merge Main

Fetch and merge the repository's base branch into the current feature branch. Automatically detects the default branch, handles uncommitted changes, resolves merge conflicts, and pushes after a successful merge.

> **Trigger:** `/merge-main`
> **Requires:** [`gh`](https://cli.github.com/) (falls back to `git remote show origin` if unavailable)
> **Details:** [README](./plugins/merge-main/README.md)

#### PR

Commit all changes, push to remote, and create a GitHub pull request in one automated step with no prompts. Detects connected issues and adds closing references automatically.

> **Trigger:** `/pr`
> **Requires:** [`gh`](https://cli.github.com/)
> **Details:** [README](./plugins/pr/README.md)

#### Rebase Onto Main

Fetch and rebase the current feature branch onto the repository's base branch. Automatically detects the default branch, handles uncommitted changes, resolves conflicts per replayed commit, and pushes after a successful rebase (using `--force-with-lease` only when the rebase rewrote history). The merge-main counterpart for projects that prefer a linear history.

> **Trigger:** `/rebase-onto-main`
> **Requires:** [`gh`](https://cli.github.com/) (falls back to `git remote show origin` if unavailable)
> **Details:** [README](./plugins/rebase-onto-main/README.md)

#### Release

Prepare a versioned release by analyzing conventional commits, updating release files, creating a release commit, tagging locally, and optionally pushing and creating a GitHub Release. Detects project type automatically (Claude Code marketplace, Go CLI, Go library, or generic). For Claude Code marketplaces, computes `metadata.version` as a catalog state tag such as `catalog-M55-m101-p44-n49` and uses `Marketplace <catalog-state>` as the GitHub Release title; for other projects, recommends a SemVer bump and manages version references and `CHANGELOG.md`.

> **Trigger:** `/release`
> **Requires:** [`jq`](https://jqlang.org/) for Claude Code marketplace releases; [`gh`](https://cli.github.com/) is optional for GitHub Release creation
> **Details:** [README](./plugins/release/README.md)

#### Review Branch

Summarize all work done on the current branch compared to the base branch. Groups changes by area, highlights notable modifications, and optionally compares progress against a plan document.

> **Trigger:** `/review-branch`
> **Details:** [README](./plugins/review-branch/README.md)

#### Use Git

Git and GitHub CLI conventions for Claude Code. Covers when to use tmpfiles vs HEREDOCs for passing content, GPG signing, safe push practices, secret file exclusion, and parallel tool call patterns to avoid permission prompts.

> **Trigger:** `/use-git` (also activates automatically)
> **Details:** [README](./plugins/use-git/README.md)

### Issues and Worktrees

Parallel development with git worktrees. Pick an issue, spin up an isolated worktree with its own agent session, and let each agent work independently.

#### Address Issue

Fetch a GitHub issue by number or search text, classify it, plan the work, execute changes in the current branch, and commit with conventional commit messages referencing the issue. Marks the issue "in progress" at the start and removes the label when done.

> **Trigger:** `/address-issue`
> **Requires:** [`gh`](https://cli.github.com/)
> **Details:** [README](./plugins/address-issue/README.md)

#### Create Issue

Create GitHub issues by writing the body to a tmpfile and passing `--body-file` to `gh`, avoiding permission prompts from large multiline Bash arguments. Supports labels, assignees, milestones, and cross-repo issue creation.

> **Trigger:** `/create-issue`
> **Requires:** [`gh`](https://cli.github.com/)
> **Details:** [README](./plugins/create-issue/README.md)

#### Create Worktree

Create a new git worktree, branch, and tmux window with a task prompt injected into the new agent session. Derives the branch name from the task description or accepts an explicit branch name.

> **Trigger:** `/create-worktree`
> **Requires:** [`workmux`](https://github.com/paiml/workmux)
> **Details:** [README](./plugins/create-worktree/README.md)

#### Create Worktree from Issue

Find a GitHub issue and create a dedicated worktree, branch, and tmux window for working on it. Derives the branch name from the issue title and labels, and injects the issue context into the new session.

> **Trigger:** `/create-worktree-from-issue`
> **Requires:** [`gh`](https://cli.github.com/), [`workmux`](https://github.com/paiml/workmux)
> **Details:** [README](./plugins/create-worktree-from-issue/README.md)

#### Suggest Next Issue

Review all open GitHub issues, analyze them in context, and recommend what to work on next with prioritized reasoning.

> **Trigger:** `/suggest-next-issue`
> **Requires:** [`gh`](https://cli.github.com/)
> **Details:** [README](./plugins/suggest-next-issue/README.md)

### Code Review

Process feedback from human reviewers and automated tools. Parse review documents, triage Copilot suggestions, and resolve comments systematically.

#### Address Review

Parse a review document for actionable feedback items, work through them systematically, and track resolution progress. Commits fixes in logical groups by default.

> **Trigger:** `/address-review <path>`
> **Details:** [README](./plugins/address-review/README.md)

#### Resolve Copilot PR Feedback

Process and resolve GitHub Copilot automated PR review comments. Categorizes threads, resolves them, and updates Copilot instruction files when feedback is incorrect.

> **Trigger:** `/resolve-copilot-pr-feedback`
> **Details:** [README](./plugins/resolve-copilot-pr-feedback/README.md)

#### Update Review

Find the latest branch review, assess commits made since, and update the review document in place with a synthesized reassessment. Plan compliance is recalculated from scratch, and the code quality assessment highlights what changed since the last review.

> **Trigger:** `/update-review`
> **Details:** [README](./plugins/update-review/README.md)

### Code Quality

Style guides, linters, and security practices. These skills activate automatically when working with their target languages and file types.

#### Add Scrut CLI Tests

Set up scrut snapshot-based CLI integration testing for a CLI project. Detects the project language, creates starter test files, adds Makefile targets, and configures CI to run scrut tests.

> **Trigger:** `/add-scrut-cli-tests`
> **Requires:** [`scrut`](https://github.com/facebookincubator/scrut) (Makefile checks for availability and provides install instructions)
> **Details:** [README](./plugins/add-scrut-cli-tests/README.md)

#### Check Zsh Scripts

Check and evaluate zsh scripts using multiple static analysis, syntax checking, and formatting tools. Runs `zsh -n`, `zcompile`, `shellcheck`, `checkbashisms`, `shellharden`, variable scope warnings, and `shfmt` in recommended order, with false-positive filtering for tools that have limited zsh support.

> **Trigger:** `/check-zsh-scripts` (also activates automatically)
> **Requires:** [`shellcheck`](https://www.shellcheck.net/), [`shfmt`](https://github.com/mvdan/sh), [`shellharden`](https://github.com/anordal/shellharden), [`checkbashisms`](https://packages.debian.org/devscripts)
> **Details:** [README](./plugins/check-zsh-scripts/README.md)

#### Handle Secrets

Best practices for handling user-provided secrets in CLI tools. Covers secure input methods, credential storage, secret masking, and language-specific libraries.

> **Trigger:** `/handle-secrets`
> **Details:** [README](./plugins/handle-secrets/README.md)

#### Lint and Fix

Detect available linters and formatters in the project, run them with auto-fix, and resolve remaining issues. Supports ESLint, Prettier, markdownlint, ShellCheck, shfmt, Knip, cspell, and project-specific lint scripts.

> **Trigger:** `/lint-and-fix`
> **Details:** [README](./plugins/lint-and-fix/README.md)

#### Setup Linters

Detect project languages and file types, recommend appropriate linters and formatters, install them, and generate config files. Supports JavaScript/TypeScript (ESLint + Prettier), Go, Python, Rust, Ruby, Shell, Zsh, Lean, the Pandoc-academic Markdown preset, and cross-language tools (EditorConfig, markdownlint, cspell, Stylelint, Hadolint, Actionlint, and more).

> **Trigger:** `/setup-linters`
> **Details:** [README](./plugins/setup-linters/README.md)

#### Write Bash Scripts

Bash style conventions for creating and editing Bash scripts. Activates automatically when creating or editing Bash scripts.

> **Trigger:** `/write-bash-scripts` (also activates automatically)
> **Details:** [README](./plugins/write-bash-scripts/README.md)

#### Write Go Code

Go code style guide based on Google Go Style Guide, Effective Go, and Code Review Comments. Organized into an essential checklist and comprehensive references by topic.

> **Trigger:** `/write-go-code` (also activates automatically)
> **Details:** [README](./plugins/write-go-code/README.md)

#### Write LaTeX

LaTeX mathematical typesetting style guide based on AMS, IEEE, ISO 80000-2, and Knuth conventions. Covers math typesetting, document conventions, packages, macros and cross-references, figures and floats, tables, spacing and alignment, ISO conventions, bibliography, and common mistakes.

> **Trigger:** `/write-latex` (also activates automatically)
> **Details:** [README](./plugins/write-latex/README.md)

#### Write Lean Code

Lean 4 style guide and Mathlib conventions covering naming, proof style, formatting, Mathlib API discovery, build infrastructure, metaprogramming, and general functional-programming idioms. Organized into an essential checklist and comprehensive references by topic.

> **Trigger:** `/write-lean-code` (also activates automatically)
> **Details:** [README](./plugins/write-lean-code/README.md)

#### Write Lean Tests

Conventions for compile-time, `example`-based Lean 4 API regression tests that mirror a library's public surface. Pairs with `write-lean-code` (which governs the library code itself).

> **Trigger:** `/write-lean-tests` (also activates automatically)
> **Details:** [README](./plugins/write-lean-tests/README.md)

#### Write Scrut Tests

Scrut test style conventions for writing and maintaining snapshot-based test files for CLI binaries and zsh plugins. Activates automatically when creating or editing scrut test files.

> **Trigger:** `/write-scrut-tests` (also activates automatically)
> **Details:** [README](./plugins/write-scrut-tests/README.md)

#### Write Zsh Scripts

Zsh style conventions for creating and editing zsh scripts, configurations, and completions. Activates automatically when creating or editing zsh files. Includes a comprehensive scripting guide and a separate completion function reference drawn from the upstream zsh completion-style-guide.

> **Trigger:** `/write-zsh-scripts` (also activates automatically)
> **Details:** [README](./plugins/write-zsh-scripts/README.md)

### Writing

Style and structure guides for prose, documentation, and document artifacts. These skills activate automatically when working with their target file types and content.

#### Write Formalization Roadmap

Document-structure guide for multi-milestone formalization roadmaps in Lean, Rocq, Isabelle, HOL, and other proof assistants. Sibling to `write-math`: governs the structure of long-lived mechanization plans (10-section schema, 5-part milestone anatomy) without dictating mathematical prose style.

> **Trigger:** `/write-formalization-roadmap` (also activates automatically)
> **Details:** [README](./plugins/write-formalization-roadmap/README.md)

#### Write Markdown

Markdown style conventions targeting GitHub Flavored Markdown (GFM), aligned with markdownlint-cli2 rules. Activates automatically when creating or editing Markdown files. Distinct from `write-pandoc-markdown`, which targets Pandoc-flavored Markdown for academic papers.

> **Trigger:** `/write-markdown` (also activates automatically)
> **Details:** [README](./plugins/write-markdown/README.md)

#### Write Math

Mathematical writing and exposition guide based on Tao, Knuth, Halmos, and other leading references. Covers clarity, notation discipline, theorem and proof structure, paper organization, and revision workflow. Activates automatically when producing or discussing mathematical content in any venue, including chat responses and Lean docstrings.

> **Trigger:** `/write-math` (also activates automatically)
> **Details:** [README](./plugins/write-math/README.md)

#### Write Pandoc Markdown

Pandoc-flavored Markdown conventions for academic papers with LaTeX output. Covers YAML frontmatter, math and citations, cross-references, raw LaTeX blocks, and the Pandoc-to-LaTeX build pipeline. Distinct from `write-markdown`, which targets GitHub Flavored Markdown.

> **Trigger:** `/write-pandoc-markdown` (also activates automatically)
> **Details:** [README](./plugins/write-pandoc-markdown/README.md)

### Scaffolding

Orchestrate project setup and refresh existing scaffolding. Assess what is needed, run all applicable setup tools in the correct order, and keep generated project files aligned with current templates.

#### Add Community Files

Add standard community files to a project preparing for public release: CONTRIBUTING.md, CODE_OF_CONDUCT.md, .github/SECURITY.md, and a pull request template. Detects the project's build system and tooling to populate contribution guidelines with relevant setup, test, and lint commands.

> **Trigger:** `/add-community-files`
> **Details:** [README](./plugins/add-community-files/README.md)

#### Bootstrap Project

Assess a repository, determine what scaffolding and setup tools are needed, present a plan, and execute them in the correct order. Detects the project type, checks for existing infrastructure, resolves overlap between tools, and runs everything from foundational boilerplate to CI, linters, secret scanning, and installer setup.

> **Trigger:** `/bootstrap-project`
> **Details:** [README](./plugins/bootstrap-project/README.md)

#### Manage Repo Licensing

Bootstrap, audit, and maintain REUSE-style mixed-license coverage in a repository: populate `LICENSES/`, author `NOTICE`, wire `REUSE.toml`, apply SPDX headers or sidecars, and keep `reuse lint` clean. Three operating modes: Bootstrap (new repo), Maintain (audit and fix drift on an existing repo), and New-file drop (single file).

> **Trigger:** `/manage-repo-licensing` (also activates automatically)
> **Requires:** [`reuse`](https://reuse.software/). Install via [Homebrew](https://brew.sh): `brew install reuse`
> **Details:** [README](./plugins/manage-repo-licensing/README.md)

#### Refresh Project Scaffolding

Refresh existing project scaffolding against the latest plugin templates. The maintenance companion to Bootstrap Project: bootstrap sets things up, this keeps them current. Detects which tools have been used, compares files against current templates, presents a plan, and applies confirmed updates.

> **Trigger:** `/refresh-project-scaffolding`
> **Details:** [README](./plugins/refresh-project-scaffolding/README.md)

#### Scaffold Go CLI

Scaffold a complete Go CLI project with Cobra, GoReleaser, GitHub Actions CI/CD, and Homebrew tap support. Generates all project files and supports optional Viper and Charmbracelet dependencies.

> **Trigger:** `/scaffold-go-cli`
> **Details:** [README](./plugins/scaffold-go-cli/README.md)

#### Scaffold Go Library

Scaffold a Go library project with GoReleaser changelog-only releases, golangci-lint, GitHub Actions CI/CD (multi-version Go matrix), and Makefile. Generates the package source file, doc.go, go.mod, Makefile, .gitignore, .goreleaser.yml, .golangci.yml, .editorconfig, CI and release workflows, LICENSE, README, and a plans directory. Optionally generates example tests.

> **Trigger:** `/scaffold-go-library`
> **Details:** [README](./plugins/scaffold-go-library/README.md)

#### Scaffold New Repo

Scaffold the universal boilerplate for any new repository: LICENSE, README, .gitignore, agent config files, and a plans directory. Supports multiple project types.

> **Trigger:** `/scaffold-new-repo`
> **Details:** [README](./plugins/scaffold-new-repo/README.md)

#### Scaffold Rust CLI

Scaffold a complete Rust CLI project with Cargo, cargo-deny, cargo-nextest, git-cliff, GitHub Actions CI/CD, and Makefile. Generates `Cargo.toml`, `src/main.rs`, `rust-toolchain.toml`, `rustfmt.toml`, `deny.toml`, `typos.toml`, `cliff.toml`, Makefile, CI and release workflows, LICENSE, README, and directory stubs. Supports optional clap argument parsing and macOS-only project configuration.

> **Trigger:** `/scaffold-rust-cli`
> **Details:** [README](./plugins/scaffold-rust-cli/README.md)

### CI and Release

Wire up GitHub Actions CI, secret scanning, release automation, and installer distribution for an existing project. Optimize those workflows over time.

#### Add GoReleaser Homebrew

Add GoReleaser configuration and a GitHub Actions release workflow to an existing Go CLI project with Homebrew tap publishing to `cboone/homebrew-tap`. Detects project features (shell completions, man page generation, macOS-only constraints) and generates appropriate configuration with conventional commit changelog grouping. Optionally adds a `release-dry-run` Makefile target.

> **Trigger:** `/add-goreleaser-homebrew`
> **Details:** [README](./plugins/add-goreleaser-homebrew/README.md)

#### Optimize Runner Usage

Add paths-ignore, concurrency groups, and timeout-minutes to existing GitHub Actions workflows. Scans all workflow files, classifies each by trigger pattern, and applies only the optimizations appropriate for each workflow type.

> **Trigger:** `/optimize-runner-usage`
> **Details:** [README](./plugins/optimize-runner-usage/README.md)

#### Setup CI

Set up GitHub Actions CI with test, lint, format, and vulnerability check jobs, plus matching Makefile targets. Detects the project language (Go, JavaScript/TypeScript, Python, Rust, Ruby, Shell, Zig, Zsh) and generates appropriate parallel CI jobs and Makefile targets.

> **Trigger:** `/setup-ci`
> **Details:** [README](./plugins/setup-ci/README.md)

#### Setup Installers

Set up installer and distribution methods for Go, Swift, and Rust projects: Homebrew tap formula, go/cargo install, release workflow generation, and homebrew-tap issue creation. Detects existing release infrastructure and generates appropriate files.

> **Trigger:** `/setup-installers`
> **Details:** [README](./plugins/setup-installers/README.md)

#### Setup Secret Scanning

Set up secret scanning with gitleaks and TruffleHog GitHub Actions workflows and optional gitleaks configuration. Gitleaks provides fast pattern matching on every push and PR; TruffleHog adds deeper verification-based scanning on pushes to main.

> **Trigger:** `/setup-secret-scanning`
> **Details:** [README](./plugins/setup-secret-scanning/README.md)

### Agents

Meta-tools for the agent ecosystem. Audit agent configuration files and create new plugins.

#### Clean Up Agent Config

Review and reorganize AI coding agent configuration files across Claude Code, OpenAI Codex, GitHub Copilot, and OpenCode. Identifies duplications, proposes a consolidated structure, and includes comprehensive reference documentation.

> **Trigger:** `/clean-up-agent-config`
> **Details:** [README](./plugins/clean-up-agent-config/README.md)

#### Create Plugin

Guide for creating new plugins in this repository with consistent structure and conventions. Walks through the full process from choosing a plugin type to registering in the marketplace.

> **Trigger:** `/create-plugin`
> **Details:** [README](./plugins/create-plugin/README.md)

## Hooks

### Workflow

Stay informed about agent activity.

#### Notify (macOS)

Sends macOS notifications when Claude finishes a task or needs your attention.

> **Requires:** [`terminal-notifier`](https://github.com/julienXX/terminal-notifier). Install via [Homebrew](https://brew.sh): `brew install terminal-notifier`
> **Details:** [README](./plugins/notify/README.md)

#### Update Docs Reminder

Analyzes git commits for changes that typically need documentation updates and provides specific, actionable reminders.

> **Requires:** [`jq`](https://jqlang.github.io/jq/)
> **Details:** [README](./plugins/update-docs-reminder/README.md)

## Using with Codex CLI

This repository works as a native [Codex CLI](https://developers.openai.com/codex/cli) plugin marketplace. Codex reads the generated `.agents/plugins/marketplace.json`, which points at committed plugin roots under `dist/codex/plugins/`. Those generated roots mirror the canonical `plugins/*` directories but replace skill frontmatter descriptions with shorter Codex-facing descriptions from the marketplace entries. The canonical `plugins/*/skills/*/SKILL.md` files keep their richer Claude Code trigger descriptions.

For per-plugin metadata Codex prefers `.codex-plugin/plugin.json` when present and falls back to `.claude-plugin/plugin.json` otherwise. Hook registration requires a `.codex-plugin/plugin.json` with a non-empty `hooks` path (for example `"hooks": "./hooks/hooks.json"`); this lets hook plugins point Codex at a Codex-compatible hook file. Codex exposes `${CLAUDE_PLUGIN_ROOT}` to plugin-bundled hook commands for backward compatibility with existing Claude Code plugins.

Add the marketplace:

```bash
codex plugin marketplace add cboone/cboone-cc-plugins
```

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

- **Plugin-bundled hooks are gated behind a feature flag.** `plugin_hooks` is `under development` in Codex CLI 0.128.0 and is `false` by default. Run `codex features enable plugin_hooks` once before expecting `notify` or `update-docs-reminder` to fire on Codex; see the install section above.
- **`Notification` and `PreCompact` hook events are not supported.** Codex CLI's hook schema only supports `PreToolUse`, `PermissionRequest`, `PostToolUse`, `SessionStart`, `UserPromptSubmit`, and `Stop`. The `notify` plugin therefore wires only the turn-completion notification on Codex (its other Claude Code events have no Codex equivalent). For idle, elicitation, and permission alerts, enable Codex's built-in `tui.notifications = true` in `~/.codex/config.toml`. See the [`notify` plugin README](./plugins/notify/README.md) for details.
- **No custom prompts shipped.** Codex's `~/.codex/prompts/` mechanism is officially deprecated in favor of skills. This repository ships skills (and hooks), not prompts.

## Using with OpenCode

This repository also works with the skills, commands, and hooks in [OpenCode](https://opencode.ai) via a committed mirror at [`dist/opencode/`](./dist/opencode/).

```bash
export OPENCODE_CONFIG_DIR="$(pwd)/dist/opencode"
```

When adding or removing a plugin, regenerate the mirror with `bin/build-opencode-mirror` and commit the result. CI fails if the mirror drifts from the source plugins. Hooks are mirrored to `dist/opencode/plugins/` as TypeScript plugins, sourced from each plugin's `opencode/index.ts`.

### OpenCode known limitations

- **`${CLAUDE_PLUGIN_ROOT}` references do not expand.** Some commands and one skill use Claude Code's `@${CLAUDE_PLUGIN_ROOT}/references/...` pattern to inline reference files at runtime. OpenCode does not expand this variable, so those inclusions appear to the agent as literal path strings rather than inlined content. The inline workflow text in each affected file still loads correctly. Affected commands: `/add-goreleaser-homebrew`, `/scaffold-go-cli`, `/scaffold-go-library`, `/scaffold-new-repo`, `/scaffold-rust-cli`, `/setup-ci`, `/setup-secret-scanning`. Affected skill: `create-plugin`. For full fidelity in these cases, run them in Claude Code.
- **Hook event parity is approximate.** OpenCode's event model collapses several distinct Claude Code notification matchers (`idle_prompt`, `elicitation_dialog`, `permission_prompt`) and the `PreCompact` event is mapped to an experimental OpenCode hook. See each hook's README for the specific mapping.

## License

[MIT License](./LICENSE). TL;DR: Do whatever you want with this software, just keep the copyright notice included. The authors aren't liable if something goes wrong.
