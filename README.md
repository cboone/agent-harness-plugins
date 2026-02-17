# Claude Code Plugins

A collection of plugins for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), from [Christopher Boone](https://cboone.github.io).

**Skills**
<br>Agents:
[Clean Up Agent Config](#clean-up-agent-config)
∙ [Create Plugin](#create-plugin)
<br>Workflow:
[Address Review](#address-review)
∙ [Commit](#commit)
∙ [Create Worktree](#create-worktree)
∙ [Create Worktree from Issue](#create-worktree-from-issue)
∙ [Lint and Fix](#lint-and-fix)
∙ [Merge Main](#merge-main)
∙ [PR](#pr)
∙ [Resolve Copilot PR Feedback](#resolve-copilot-pr-feedback)
∙ [Review Branch](#review-branch)
∙ [Scaffold Go CLI](#scaffold-go-cli)
∙ [Scaffold New Repo](#scaffold-new-repo)
∙ [Suggest Next Issue](#suggest-next-issue)
<br>Languages:
[Write Go Code](#write-go-code)
∙ [Write Markdown](#write-markdown)
∙ [Write Shell Scripts](#write-shell-scripts)
<br>Security:
[Handle Secrets](#handle-secrets)

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

### Address Review

Parse a review document (typically in `docs/reviews/` or similar) for actionable feedback items, work through them systematically, and track resolution progress. Extracts items from checkboxes, bullets, numbered lists, and headings. Categorizes each item by type (code change, documentation, question, style), presents a summary for confirmation, then resolves items one by one. Commits fixes in logical groups by default, or per-item with `--commit-per-item`. Supports `--dry-run` to preview items without making changes and `--skip` to exclude specific items.

> **Trigger:** `/address-review <path>`

### Clean Up Agent Config

Review and reorganize AI coding agent configuration and instruction files across Claude Code, OpenAI Codex, GitHub Copilot (CLI and code review), and OpenCode. Audits existing files (`CLAUDE.md`, `AGENTS.md`, `.claude/settings.json`, `.github/copilot-instructions.md`, etc.), identifies duplications and misplaced settings, and proposes a consolidated structure. Handles the `settings.json` vs `settings.local.json` split, sets up `AGENTS.md` as the single source of truth with `CLAUDE.md` as a symlink, and takes advantage of tool-specific features like Copilot's path-scoped `.instructions.md` files.

Includes comprehensive reference documentation on all agent instruction and configuration file formats.

> **Trigger:** `/clean-up-agent-config`

### Commit

Smart, context-aware git commits with conventional commit messages and plan awareness. Analyzes your diff to generate well-structured commit messages, handles staged-only vs. all changes, supports commit-and-push workflows, and can detect and handle plan files separately.

> **Trigger:** `/commit`

### Create Plugin

Guide for creating new plugins in this repository with consistent structure and conventions. Walks through the full process: choosing a plugin type (skill, hook, or both), scaffolding the directory structure, writing all required files, and registering the plugin in the marketplace.

> **Trigger:** `/create-plugin`

### Create Worktree

Create a new git worktree, branch, and tmux window using [workmux](https://github.com/paiml/workmux), with a task prompt injected into the new session so the agent knows what to work on. Derives the branch name from the task description (e.g., `feature/add-dark-mode-support` or `fix/auth-timeout`), or accepts an explicit branch name.

> **Trigger:** `/create-worktree`
> **Requires:** [`workmux`](https://github.com/paiml/workmux)

### Create Worktree from Issue

Find a GitHub issue in the current repository (by number or fuzzy text search) and create a dedicated worktree, branch, and tmux window for working on it using [workmux](https://github.com/paiml/workmux). Derives the branch name from the issue title and labels (e.g., `feature/add-dark-mode-support` or `fix/login-fails-with-special-chars`). Injects the issue title, labels, and body as a task prompt into the new session so the agent has full context.

> **Trigger:** `/create-worktree-from-issue`
> **Requires:** [`gh`](https://cli.github.com/), [`workmux`](https://github.com/paiml/workmux)

### Handle Secrets

Best practices for handling secrets that users pass to your CLI tool (API keys, tokens, passwords). Covers the full security hierarchy of input methods (from OS keychains down to the never-use-CLI-arguments rule), credential storage patterns, secret masking in output, and the credential resolution fallback chain. Activates automatically when building CLI tools that accept credentials.

Organized into an actionable checklist for quick reviews and comprehensive references by topic (security hierarchy, design patterns, anti-patterns, language-specific libraries for Rust, Go, Python, Node.js, and Ruby).

> **Trigger:** `/handle-secrets` (also activates automatically)

### Lint and Fix

Detect available linters and formatters in the project by checking for configuration files (ESLint, Prettier, markdownlint, ShellCheck, shfmt, Knip, and project-specific lint scripts). Run each detected tool with auto-fix flags, report what was fixed and what remains, then attempt to manually resolve remaining issues. Supports `--check` for dry runs, `--tool <name>` to target a single tool, and `--commit` / `--no-commit` to control post-fix commit behavior.

> **Trigger:** `/lint-and-fix`

### Merge Main

Fetch and merge the repository's base branch (usually `main`) into the current feature branch. Automatically detects the default branch, handles uncommitted changes, resolves merge conflicts, and optionally pushes after a successful merge.

> **Trigger:** `/merge-main`
> **Requires:** [`gh`](https://cli.github.com/) (falls back to `git remote show origin` if unavailable)

### PR

Commit all changes, push to remote, and create a GitHub pull request in one automated step with no prompts. Stages everything, generates a conventional commit message from the diff, pushes the branch, and opens a PR with an auto-generated title and summary. Handles branches with no upstream, skips the commit step when the working tree is clean, and detects when a PR already exists.

> **Trigger:** `/pr`
> **Requires:** [`gh`](https://cli.github.com/)

### Resolve Copilot PR Feedback

Process and resolve GitHub Copilot automated PR review comments. Fetches unresolved Copilot threads via GraphQL, categorizes them (nitpick, outdated, incorrect, valid, deferred), resolves threads, and updates Copilot instruction files under `.github/` (repo-wide `copilot-instructions.md` or path-specific `*.instructions.md`) when Copilot feedback is incorrect.

> **Trigger:** `/resolve-copilot-pr-feedback`

### Review Branch

Summarize all work done on the current branch compared to the base branch. Groups changes by area/concern, lists new/modified/deleted files, and highlights notable changes (new dependencies, config changes, schema changes, API changes). Optionally compares progress against a plan document, reporting completed, in-progress, and remaining items with a completion percentage.

Supports custom base references (`--since <ref>`), plan comparison (`--plan <path>`), and brief mode (`--brief`).

> **Trigger:** `/review-branch`

### Scaffold Go CLI

Scaffold a complete Go CLI project with Cobra, GoReleaser, GitHub Actions CI/CD, and Homebrew tap support. Generates main.go, cmd/root.go, go.mod, Makefile, .gitignore, .goreleaser.yml, CI and release workflows, LICENSE, README, and directory stubs. Supports optional Viper config management and Charmbracelet TUI dependencies.

> **Trigger:** `/scaffold-go-cli`

### Scaffold New Repo

Scaffold the universal boilerplate for any new repository, regardless of language. Generates LICENSE (MIT), README.md, a project-type-specific .gitignore, agent config files (AGENTS.md, CLAUDE.md symlink, `.claude/settings.json`, `.github/copilot-instructions.md`), and a `docs/plans/` directory. Infers the project type from an existing .gitignore when possible. Supports Go CLI, Go library, Shell, JavaScript, Ruby, and generic project types.

> **Trigger:** `/scaffold-new-repo`

### Suggest Next Issue

Review all open GitHub issues in the current repository, analyze them in context (current branches, recent work, project goals, dependencies), and recommend what to work on next with prioritized reasoning. Issues are categorized as quick wins, high impact, unblocks others, or overdue, with specific reasoning for each recommendation.

> **Trigger:** `/suggest-next-issue`
> **Requires:** [`gh`](https://cli.github.com/)

### Write Go Code

Go code style guide based on Google Go Style Guide, Effective Go, and Code Review Comments. Activates automatically when writing, reviewing, or refactoring Go code.

Organized into an essential checklist for quick reviews and comprehensive references by topic (naming, errors, concurrency, testing, code organization, data types, functions, interfaces).

> **Trigger:** `/write-go-code` (also activates automatically)

### Write Markdown

Markdown style conventions for creating and editing Markdown files. Targets GitHub Flavored Markdown (GFM) and aligns with markdownlint-cli2 rules. Activates automatically when creating, editing, or reviewing Markdown files.

> **Trigger:** `/write-markdown` (also activates automatically)

### Write Shell Scripts

Bash style conventions for creating and editing shell scripts. Activates automatically when creating, editing, or reviewing shell scripts.

> **Trigger:** `/write-shell-scripts` (also activates automatically)

## Hooks

### Block rm -rf

Blocks recursive `rm` commands (`rm -rf`, `rm -r`, `rm -R`, `rm --recursive`, and variants) before they execute. Rejects the command and suggests using `trash` instead, which moves files to the system Trash instead of permanently deleting them.

> **Requires:** [`trash`](https://hasseg.org/trash/) — install via [Homebrew](https://brew.sh): `brew install trash`

### Notify (macOS)

Notifies you when Claude finishes a task or needs your attention via macOS notifications.

> **Requires:** [`terminal-notifier`](https://github.com/julienXX/terminal-notifier) — install via [Homebrew](https://brew.sh): `brew install terminal-notifier`

## License

[MIT License](./LICENSE). TL;DR: Do whatever you want with this software, just keep the copyright notice included. The authors aren't liable if something goes wrong.
