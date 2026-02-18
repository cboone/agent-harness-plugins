# Claude Code Plugins

A collection of plugins for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), from [Christopher Boone](https://cboone.github.io).

**Skills**
<br>Git:
[Commit](#commit)
∙ [Merge Main](#merge-main)
∙ [PR](#pr)
∙ [Review Branch](#review-branch)
<br>Issues and Worktrees:
[Create Worktree](#create-worktree)
∙ [Create Worktree from Issue](#create-worktree-from-issue)
∙ [Suggest Next Issue](#suggest-next-issue)
<br>Code Review:
[Address Review](#address-review)
∙ [Resolve Copilot PR Feedback](#resolve-copilot-pr-feedback)
<br>Code Quality:
[Handle Secrets](#handle-secrets)
∙ [Lint and Fix](#lint-and-fix)
∙ [Write Go Code](#write-go-code)
∙ [Write Markdown](#write-markdown)
∙ [Write Shell Scripts](#write-shell-scripts)
<br>Scaffolding:
[Add GoReleaser Homebrew](#add-goreleaser-homebrew)
∙ [Scaffold Go CLI](#scaffold-go-cli)
∙ [Scaffold Go Library](#scaffold-go-library)
∙ [Scaffold New Repo](#scaffold-new-repo)
∙ [Setup Gitleaks](#setup-gitleaks)
<br>Agents:
[Clean Up Agent Config](#clean-up-agent-config)
∙ [Create Plugin](#create-plugin)

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

#### Review Branch

Summarize all work done on the current branch compared to the base branch. Groups changes by area, highlights notable modifications, and optionally compares progress against a plan document.

> **Trigger:** `/review-branch`
> **Details:** [README](./plugins/review-branch/README.md)

### Issues and Worktrees

Parallel development with git worktrees. Pick an issue, spin up an isolated worktree with its own agent session, and let each agent work independently.

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

### Code Quality

Style guides, linters, and security practices. These skills activate automatically when working with their target languages and file types.

#### Handle Secrets

Best practices for handling user-provided secrets in CLI tools. Covers secure input methods, credential storage, secret masking, and language-specific libraries.

> **Trigger:** `/handle-secrets`
> **Details:** [README](./plugins/handle-secrets/README.md)

#### Lint and Fix

Detect available linters and formatters in the project, run them with auto-fix, and resolve remaining issues. Supports ESLint, Prettier, markdownlint, ShellCheck, shfmt, Knip, and project-specific lint scripts.

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

#### Write Shell Scripts

Bash style conventions for creating and editing shell scripts. Activates automatically when creating or editing shell scripts.

> **Trigger:** `/write-shell-scripts` (also activates automatically)
> **Details:** [README](./plugins/write-shell-scripts/README.md)

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

#### Setup Gitleaks

Set up gitleaks secret scanning with a GitHub Actions workflow and optional configuration. Detects organization vs. personal repositories and generates the appropriate workflow.

> **Trigger:** `/setup-gitleaks`
> **Details:** [README](./plugins/setup-gitleaks/README.md)

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
