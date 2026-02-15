# Claude Code Plugins

A collection of plugins for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), from [Christopher Boone](https://cboone.github.io). Includes skills (slash commands) and hooks (automatic behaviors).

## Installation

Install plugins from this repository using Claude Code. The simplest way is open the plugins manager via `/plugin`, then `tab` to `Marketplace`, and hit `enter` to `Add Marketplace`. Type `cboone/cboone-cc-plugins`, then choose which plugins you would like to install.

Or you can run more direct commands, either from within `claude`:

```bash
/plugin marketplace add cboone/cboone-cc-plugins

/plugin install create-worktree-from-issue@cboone/cboone-cc-plugins
/plugin install notify@cboone/cboone-cc-plugins
/plugin install resolve-copilot-pr-feedback@cboone/cboone-cc-plugins
/plugin install suggest-next-issue@cboone/cboone-cc-plugins
/plugin install write-go-code@cboone/cboone-cc-plugins
/plugin install write-shell-scripts@cboone/cboone-cc-plugins
```

Or from the command line:

```bash
claude plugin marketplace add cboone/cboone-cc-plugins

claude plugin install create-worktree-from-issue@cboone/cboone-cc-plugins
claude plugin install notify@cboone/cboone-cc-plugins
claude plugin install resolve-copilot-pr-feedback@cboone/cboone-cc-plugins
claude plugin install suggest-next-issue@cboone/cboone-cc-plugins
claude plugin install write-go-code@cboone/cboone-cc-plugins
claude plugin install write-shell-scripts@cboone/cboone-cc-plugins
```

## Skills

### Create Worktree from Issue

Find a GitHub issue in the current repository (by number or fuzzy text search) and create a dedicated worktree, branch, and tmux window for working on it using [workmux](https://github.com/paiml/workmux). Derives the branch name from the issue title and labels (e.g., `feature/add-dark-mode-support` or `fix/login-fails-with-special-chars`).

You can trigger it directly via `/create-worktree-from-issue`.

Requires [`gh`](https://cli.github.com/) and [`workmux`](https://github.com/paiml/workmux) to be installed.

### Resolve Copilot PR Feedback

Process and resolve GitHub Copilot automated PR review comments. Fetches unresolved Copilot threads via GraphQL, categorizes them (nitpick, outdated, incorrect, valid, deferred), resolves threads, and updates Copilot instruction files under `.github/` (repo-wide `copilot-instructions.md` or path-specific `*.instructions.md`) when Copilot feedback is incorrect.

You can trigger it directly via `/resolve-copilot-pr-feedback`.

### Write Go Code

Go code style guide based on Google Go Style Guide, Effective Go, and Code Review Comments. Claude Code should automatically use it when writing, reviewing, or refactoring Go code.

You can trigger it directly via `/write-go-code`.

The style guides are organized into:

- Essential checklist for quick reviews
- Comprehensive references by topic (naming, errors, concurrency, testing, code organization, data types, functions, interfaces)

### Suggest Next Issue

Review all open GitHub issues in the current repository, analyze them in context (current branches, recent work, project goals, dependencies), and recommend what to work on next with prioritized reasoning. Issues are categorized as quick wins, high impact, unblocks others, or overdue, with specific reasoning for each recommendation.

You can trigger it directly via `/suggest-next-issue`.

Requires [`gh`](https://cli.github.com/) to be installed.

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
