# Claude Code Plugins

A collection of plugins for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), from [Christopher Boone](https://cboone.github.io).

**Skills**
<br>Git:
[Commit](#commit)
∙ [Merge Main](#merge-main)
∙ [PR](#pr)
∙ [Release](#release)
∙ [Review Branch](#review-branch)
∙ [Use Git](#use-git)
<br>Issues and Worktrees:
[Create Issue](#create-issue)
∙ [Create Worktree](#create-worktree)
∙ [Create Worktree from Issue](#create-worktree-from-issue)
∙ [Suggest Next Issue](#suggest-next-issue)
<br>Code Review:
[Address Review](#address-review)
∙ [Resolve Copilot PR Feedback](#resolve-copilot-pr-feedback)
∙ [Update Review](#update-review)
<br>Code Quality:
[Handle Secrets](#handle-secrets)
∙ [Lint and Fix](#lint-and-fix)
∙ [Setup Linters](#setup-linters)
∙ [Write Go Code](#write-go-code)
∙ [Write Markdown](#write-markdown)
∙ [Write Scrut Tests](#write-scrut-tests)
∙ [Write Shell Scripts](#write-shell-scripts)
<br>Scaffolding:
[Add Community Files](#add-community-files)
∙ [Bootstrap Project](#bootstrap-project)
<br>Agents:
[Clean Up Agent Config](#clean-up-agent-config)
∙ [Create Plugin](#create-plugin)

**Commands**
<br>Code Quality:
[Add Scrut CLI Tests](#add-scrut-cli-tests)
<br>CI Optimization:
[Optimize Runner Usage](#optimize-runner-usage)
<br>Scaffolding:
[Add GoReleaser Homebrew](#add-goreleaser-homebrew)
∙ [Scaffold Go CLI](#scaffold-go-cli)
∙ [Scaffold Go Library](#scaffold-go-library)
∙ [Scaffold New Repo](#scaffold-new-repo)
∙ [Setup CI](#setup-ci)
∙ [Setup Secret Scanning](#setup-secret-scanning)
∙ [Setup Installers](#setup-installers)
∙ [Update Everything](#update-everything)

**Hooks**
<br>Security:
[Block rm -rf](#block-rm--rf)
<br>Workflow:
[Notify](#notify-macos)

## Installation

From within `claude`, open the plugins manager via `/plugin`, then `tab` to `Marketplace`, and hit `enter` to `Add Marketplace`. Type `cboone/cboone-cc-plugins`, then choose which plugins you would like to install.

Or, from within `claude`, run:

```bash
/plugin marketplace add cboone/cboone-cc-plugins
```

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

#### Release

Prepare a versioned release by analyzing conventional commits, recommending a version bump, updating version references in project files and documentation, managing `CHANGELOG.md` in Keep a Changelog format, creating a release commit, and tagging locally. Detects project type automatically (Go CLI, Go library, or generic).

> **Trigger:** `/release`
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

#### Handle Secrets

Best practices for handling user-provided secrets in CLI tools. Covers secure input methods, credential storage, secret masking, and language-specific libraries.

> **Trigger:** `/handle-secrets`
> **Details:** [README](./plugins/handle-secrets/README.md)

#### Lint and Fix

Detect available linters and formatters in the project, run them with auto-fix, and resolve remaining issues. Supports ESLint, Prettier, markdownlint, ShellCheck, shfmt, Knip, cspell, and project-specific lint scripts.

> **Trigger:** `/lint-and-fix`
> **Details:** [README](./plugins/lint-and-fix/README.md)

#### Write Go Code

Go code style guide based on Google Go Style Guide, Effective Go, and Code Review Comments. Organized into an essential checklist and comprehensive references by topic.

> **Trigger:** `/write-go-code` (also activates automatically)
> **Details:** [README](./plugins/write-go-code/README.md)

#### Write Markdown

Markdown style conventions targeting GitHub Flavored Markdown (GFM), aligned with markdownlint-cli2 rules. Activates automatically when creating or editing Markdown files.

> **Trigger:** `/write-markdown` (also activates automatically)
> **Details:** [README](./plugins/write-markdown/README.md)

#### Write Scrut Tests

Scrut test style conventions for writing and maintaining snapshot-based CLI test files. Activates automatically when creating or editing scrut test files.

> **Trigger:** `/write-scrut-tests` (also activates automatically)
> **Details:** [README](./plugins/write-scrut-tests/README.md)

#### Write Shell Scripts

Bash style conventions for creating and editing shell scripts. Activates automatically when creating or editing shell scripts.

> **Trigger:** `/write-shell-scripts` (also activates automatically)
> **Details:** [README](./plugins/write-shell-scripts/README.md)

#### Setup Linters

Detect project languages and file types, recommend appropriate linters and formatters, install them, and generate config files. Supports JavaScript/TypeScript (ESLint + Prettier), Go, Python, Rust, Ruby, Shell, and cross-language tools (EditorConfig, markdownlint, cspell, Stylelint, Hadolint, Actionlint, and more).

> **Trigger:** `/setup-linters`
> **Details:** [README](./plugins/setup-linters/README.md)

### Scaffolding

Orchestrate project setup. Assess what is needed and run all applicable scaffolding and setup tools in the correct order.

#### Add Community Files

Add standard community files to a project preparing for public release: CONTRIBUTING.md, CODE_OF_CONDUCT.md, .github/SECURITY.md, and a pull request template. Detects the project's build system and tooling to populate contribution guidelines with relevant setup, test, and lint commands.

> **Trigger:** `/add-community-files`
> **Details:** [README](./plugins/add-community-files/README.md)

#### Bootstrap Project

Assess a repository, determine what scaffolding and setup tools are needed, present a plan, and execute them in the correct order. Detects the project type, checks for existing infrastructure, resolves overlap between tools, and runs everything from foundational boilerplate to CI, linters, secret scanning, and installer setup.

> **Trigger:** `/bootstrap-project`
> **Details:** [README](./plugins/bootstrap-project/README.md)

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

## Commands

Commands are invoked explicitly via `/command-name` and are not loaded into the system prompt. Use these for one-time setup tasks.

### Code Quality

#### Add Scrut CLI Tests

Set up scrut snapshot-based CLI integration testing for a CLI project. Detects the project language, creates starter test files, adds Makefile targets, and configures CI to run scrut tests.

> **Trigger:** `/add-scrut-cli-tests`
> **Requires:** [`scrut`](https://github.com/facebookincubator/scrut) (Makefile checks for availability and provides install instructions)
> **Details:** [README](./plugins/add-scrut-cli-tests/README.md)

### CI Optimization

Reduce wasted GitHub Actions minutes on existing workflows.

#### Optimize Runner Usage

Add paths-ignore, concurrency groups, and timeout-minutes to existing GitHub Actions workflows. Scans all workflow files, classifies each by trigger pattern, and applies only the optimizations appropriate for each workflow type.

> **Trigger:** `/optimize-runner-usage`
> **Details:** [README](./plugins/optimize-runner-usage/README.md)

### Scaffolding

Bootstrap new projects with consistent structure. Generate boilerplate, CI/CD pipelines, and security scanning from templates.

#### Add GoReleaser Homebrew

Add GoReleaser configuration and a GitHub Actions release workflow to an existing Go CLI project with Homebrew tap publishing to `cboone/homebrew-tap`. Detects project features (shell completions, man page generation, macOS-only constraints) and generates appropriate configuration with conventional commit changelog grouping. Optionally adds a `release-dry-run` Makefile target.

> **Trigger:** `/add-goreleaser-homebrew`

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

#### Setup CI

Set up GitHub Actions CI with test, lint, format, and vulnerability check jobs, plus matching Makefile targets. Detects the project language (Go, JavaScript/TypeScript, Python, Rust, Ruby, Shell) and generates appropriate parallel CI jobs and Makefile targets.

> **Trigger:** `/setup-ci`
> **Details:** [README](./plugins/setup-ci/README.md)

#### Setup Secret Scanning

Set up secret scanning with gitleaks and TruffleHog GitHub Actions workflows and optional gitleaks configuration. Gitleaks provides fast pattern matching on every push and PR; TruffleHog adds deeper verification-based scanning on pushes to main.

> **Trigger:** `/setup-secret-scanning`
> **Details:** [README](./plugins/setup-secret-scanning/README.md)

#### Setup Installers

Set up installer and distribution methods for Go, Swift, and Rust projects: Homebrew tap formula, shell install script, go/cargo install, release workflow generation, and homebrew-tap issue creation. Detects existing release infrastructure and generates appropriate files.

> **Trigger:** `/setup-installers`
> **Details:** [README](./plugins/setup-installers/README.md)

#### Update Everything

Audit a repository against the latest plugin templates and update anything out of date. The maintenance companion to Bootstrap Project: bootstrap sets things up, this keeps them current. Detects which tools have been used, compares files against current templates, presents a plan, and applies confirmed updates.

> **Trigger:** `/update-everything`
> **Details:** [README](./plugins/update-everything/README.md)

## Hooks

### Security

Prevent destructive operations before they happen.

#### Block rm -rf

Blocks recursive `rm` commands before they execute and suggests using `trash` instead, which moves files to the system Trash.

> **Requires:** [`trash`](https://hasseg.org/trash/). Install via [Homebrew](https://brew.sh): `brew install trash`
> **Details:** [README](./plugins/block-rm-rf/README.md)

### Workflow

Stay informed about agent activity.

#### Notify (macOS)

Sends macOS notifications when Claude finishes a task or needs your attention.

> **Requires:** [`terminal-notifier`](https://github.com/julienXX/terminal-notifier). Install via [Homebrew](https://brew.sh): `brew install terminal-notifier`
> **Details:** [README](./plugins/notify/README.md)

## License

[MIT License](./LICENSE). TL;DR: Do whatever you want with this software, just keep the copyright notice included. The authors aren't liable if something goes wrong.
