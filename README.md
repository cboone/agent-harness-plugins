# Claude Code Plugins

A collection of plugins for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), from [Christopher Boone](https://cboone.github.io).

**Skills**
<br>_Agents_
[Clean Up Agent Config](#clean-up-agent-config)
| [Create Plugin](#create-plugin)
<br>_Workflow_
[Commit](#commit)
| [Create Worktree](#create-worktree)
| [Create Worktree from Issue](#create-worktree-from-issue)
| [Merge Main](#merge-main)
| [PR](#pr)
| [Resolve Copilot PR Feedback](#resolve-copilot-pr-feedback)
| [Scaffold New Repo](#scaffold-new-repo)
| [Suggest Next Issue](#suggest-next-issue)
<br>_Languages_
[Write Go Code](#write-go-code)
| [Write Shell Scripts](#write-shell-scripts)
<br>**Hooks**
[Block rm -rf](#block-rm--rf)
| [Notify](#notify-macos)

## Installation

From within `claude`, open the plugins manager via `/plugin`, then `tab` to `Marketplace`, and hit `enter` to `Add Marketplace`. Type `cboone/cboone-cc-plugins`, then choose which plugins you would like to install.

Or, from within `claude`, run:

```bash
/plugin marketplace add cboone/cboone-cc-plugins
```

## Skills

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
