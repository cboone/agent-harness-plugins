# Claude Code Plugins

A collection of plugins for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), from [Christopher Boone](https://cboone.github.io).

**Skills:**
[Clean Up Agent Config](#clean-up-agent-config) |
[Commit](#commit) |
[Create Worktree](#create-worktree) |
[Create Worktree from Issue](#create-worktree-from-issue) |
[Merge Main](#merge-main) |
[Resolve Copilot PR Feedback](#resolve-copilot-pr-feedback) |
[Suggest Next Issue](#suggest-next-issue) |
[Write Go Code](#write-go-code) |
[Write Shell Scripts](#write-shell-scripts)
<br>
**Hooks:**
[Notify](#notify-macos)

## Installation

Install plugins from this repository using Claude Code. The simplest way is open the plugins manager via `/plugin`, then `tab` to `Marketplace`, and hit `enter` to `Add Marketplace`. Type `cboone/cboone-cc-plugins`, then choose which plugins you would like to install.

Or you can run more direct commands from within `claude`:

```bash
/plugin marketplace add cboone/cboone-cc-plugins

/plugin install clean-up-agent-config@cboone/cboone-cc-plugins
/plugin install commit@cboone/cboone-cc-plugins
/plugin install create-worktree@cboone/cboone-cc-plugins
/plugin install create-worktree-from-issue@cboone/cboone-cc-plugins
/plugin install merge-main@cboone/cboone-cc-plugins
/plugin install notify@cboone/cboone-cc-plugins
/plugin install resolve-copilot-pr-feedback@cboone/cboone-cc-plugins
/plugin install suggest-next-issue@cboone/cboone-cc-plugins
/plugin install write-go-code@cboone/cboone-cc-plugins
/plugin install write-shell-scripts@cboone/cboone-cc-plugins
```

## Skills

### Clean Up Agent Config

Review and reorganize AI coding agent configuration and instruction files across Claude Code, OpenAI Codex, GitHub Copilot (CLI and code review), and OpenCode. Audits existing files (CLAUDE.md, AGENTS.md, `.claude/settings.json`, `.github/copilot-instructions.md`, etc.), identifies duplications and misplaced settings, and proposes a consolidated structure. Handles the `settings.json` vs `settings.local.json` split, sets up AGENTS.md as the single source of truth with CLAUDE.md as a symlink, and takes advantage of tool-specific features like Copilot's path-scoped `.instructions.md` files.

You can trigger it directly via `/clean-up-agent-config`.

Includes comprehensive reference documentation on all agent instruction and configuration file formats.

### Commit

Smart, context-aware git commits with conventional commit messages and plan awareness. Analyzes your diff to generate well-structured commit messages, handles staged-only vs. all changes, supports commit-and-push workflows, and can detect and handle plan files separately.

You can trigger it directly via `/commit`.

### Create Worktree

Create a new git worktree, branch, and tmux window using [workmux](https://github.com/paiml/workmux), with a task prompt injected into the new session so the agent knows what to work on. Derives the branch name from the task description (e.g., `feature/add-dark-mode-support` or `fix/auth-timeout`), or accepts an explicit branch name.

You can trigger it directly via `/create-worktree`.

Requires [`workmux`](https://github.com/paiml/workmux) to be installed.

### Create Worktree from Issue

Find a GitHub issue in the current repository (by number or fuzzy text search) and create a dedicated worktree, branch, and tmux window for working on it using [workmux](https://github.com/paiml/workmux). Derives the branch name from the issue title and labels (e.g., `feature/add-dark-mode-support` or `fix/login-fails-with-special-chars`). Injects the issue title, labels, and body as a task prompt into the new session so the agent has full context.

You can trigger it directly via `/create-worktree-from-issue`.

Requires [`gh`](https://cli.github.com/) and [`workmux`](https://github.com/paiml/workmux) to be installed.

### Merge Main

Fetch and merge the repository's base branch (usually `main`) into the current feature branch. Automatically detects the default branch, handles uncommitted changes, resolves merge conflicts, and optionally pushes after a successful merge.

You can trigger it directly via `/merge-main`.

Requires [`gh`](https://cli.github.com/) to be installed (falls back to `git remote show origin` if unavailable).

### Resolve Copilot PR Feedback

Process and resolve GitHub Copilot automated PR review comments. Fetches unresolved Copilot threads via GraphQL, categorizes them (nitpick, outdated, incorrect, valid, deferred), resolves threads, and updates Copilot instruction files under `.github/` (repo-wide `copilot-instructions.md` or path-specific `*.instructions.md`) when Copilot feedback is incorrect.

You can trigger it directly via `/resolve-copilot-pr-feedback`.

### Suggest Next Issue

Review all open GitHub issues in the current repository, analyze them in context (current branches, recent work, project goals, dependencies), and recommend what to work on next with prioritized reasoning. Issues are categorized as quick wins, high impact, unblocks others, or overdue, with specific reasoning for each recommendation.

You can trigger it directly via `/suggest-next-issue`.

Requires [`gh`](https://cli.github.com/) to be installed.

### Write Go Code

Go code style guide based on Google Go Style Guide, Effective Go, and Code Review Comments. Claude Code should automatically use it when writing, reviewing, or refactoring Go code.

You can trigger it directly via `/write-go-code`.

The style guides are organized into:

- Essential checklist for quick reviews
- Comprehensive references by topic (naming, errors, concurrency, testing, code organization, data types, functions, interfaces)

### Write Shell Scripts

Applies Bash style conventions when creating or editing shell scripts. Claude Code should automatically use it when creating, editing, or reviewing shell scripts.

You can trigger it directly via `/write-shell-scripts`.

## Hooks

### Notify (macOS)

Notifies you when Claude finishes a task or needs your attention. Uses macOS notifications to alert you.

Requires [`terminal-notifier`](https://github.com/julienXX/terminal-notifier). The easiest installation method is via [Homebrew](https://brew.sh):

```bash
brew install terminal-notifier
```

## License

[MIT License](./LICENSE). TL;DR: Do whatever you want with this software, just keep the copyright notice included. The authors aren't liable if something goes wrong.
