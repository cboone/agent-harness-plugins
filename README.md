# Claude Code Plugins

A collection of plugins for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), from [Christopher Boone](https://cboone.github.io).

## Write Go Code

**Type**: Skills / Commands

Go code style guide based on Google Go Style Guide, Effective Go, and Code Review Comments. Claude Code should automatically use it when writing, reviewing, or refactoring Go code.

You can trigger it directly via `/write-go-code`.

The style guides are organized into:
- Essential checklist for quick reviews
- Comprehensive references by topic (naming, errors, concurrency, testing, code organization, data types, functions, interfaces)

## Resolve Copilot PR Feedback

**Type**: Skills / Commands

Process and resolve GitHub Copilot automated PR review comments. Fetches unresolved Copilot threads via GraphQL, categorizes them (nitpick, outdated, incorrect, valid, deferred), resolves threads, and updates Copilot instruction files under `.github/` (repo-wide `copilot-instructions.md` or path-specific `*.instructions.md`) when Copilot feedback is incorrect.

You can trigger it directly via `/resolve-copilot-pr-feedback`.

## Notify

**Type**: Hooks

Notifies you when Claude finishes a task or needs your attention. Uses macOS notifications to alert you.

Requires [`terminal-notifier`](https://github.com/julienXX/terminal-notifier). The easiest installation method is via [Homebrew](https://brew.sh):

```bash
brew install terminal-notifier
```

## Write Shell Scripts

**Type**: Skills / Commands (merged as of [Claude Code 2.1.3](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md#213))

Applies Bash style conventions when creating or editing shell scripts. Claude Code should automatically use it when creating, editing, or reviewing shell scripts.

You can trigger it directly via `/write-shell-scripts`.

The Bash style conventions are in [`BASH.md`](./plugins/write-shell-scripts/skills/write-shell-scripts/references/BASH.md).

## Installation

Install plugins from this repository using Claude Code. The simplest way is open the plugins manager via `/plugin`, then `tab` to `Marketplace`, and hit `enter` to `Add Marketplace`. Type `cboone/cboone-cc-plugins`, then choose which plugins you would like to install.

Or you can run more direct commands, either from within `claude`:

```bash
/plugin marketplace add cboone/cboone-cc-plugins

/plugin install write-go-code@cboone/cboone-cc-plugins
/plugin install notify@cboone/cboone-cc-plugins
/plugin install resolve-copilot-pr-feedback@cboone/cboone-cc-plugins
/plugin install write-shell-scripts@cboone/cboone-cc-plugins
```

Or from the command line:

```bash
claude plugin marketplace add cboone/cboone-cc-plugins

claude plugin install write-go-code@cboone/cboone-cc-plugins
claude plugin install notify@cboone/cboone-cc-plugins
claude plugin install resolve-copilot-pr-feedback@cboone/cboone-cc-plugins
claude plugin install write-shell-scripts@cboone/cboone-cc-plugins
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
