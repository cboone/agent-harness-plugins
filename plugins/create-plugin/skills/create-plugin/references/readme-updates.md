# README.md Updates Reference

When adding a new plugin, update the compact category table in the root `README.md` and create a per-plugin `README.md` in the plugin directory. Do not add a root README table of contents or H3 plugin-description sections unless the root README is intentionally redesigned again.

## Root README Category Tables

The root `README.md` lists skills and command-style plugins under `## Skills`, grouped by category. Each category has a 3-column table:

```markdown
| Plugin | Trigger | What it does |
| --- | --- | --- |
| [Plugin Name](./plugins/plugin-name/README.md) | `/plugin-name` | Canonical marketplace description. |
```

Format rules:

- Keep the category order used by the root README: Git, Issues and Worktrees, Code Review, Code Quality, Writing, Scaffolding, CI and Release, Agents.
- Insert the row alphabetically by plugin display name within the selected category table.
- Link the plugin name to `./plugins/PLUGIN-NAME/README.md`.
- Use the slash command in the `Trigger` column, usually `/PLUGIN-NAME`.
- For style-guide skills that also activate automatically, do not annotate automatic activation in the root table. Explain activation behavior in the per-plugin README instead.
- Copy the canonical marketplace `description` field verbatim into `What it does`.
- Do not add individual install commands to the root README. The marketplace install flow covers installation.

### Category Guide for Skills and Command-Style Plugins

Use this guide to choose the root README category and the matching marketplace `category` value.

| Root README category     | Marketplace category   | Covers                                                      | Examples                                                 |
| ------------------------ | ---------------------- | ----------------------------------------------------------- | -------------------------------------------------------- |
| **Git**                  | `git`                  | Commit-to-PR pipeline                                       | commit, merge-main, pr, review-branch, use-git           |
| **Issues and Worktrees** | `issues-and-worktrees` | Multi-agent and issue-driven work                           | create-worktree, suggest-next-issue                      |
| **Code Review**          | `code-review`          | Responding to external feedback                             | address-review, resolve-copilot-pr-feedback              |
| **Code Quality**         | `code-quality`         | Style guides for code, linting, formatting                  | lint-and-fix, write-go-code                              |
| **Writing**              | `writing`              | Style and structure guides for prose and document artifacts | write-markdown, write-pandoc-markdown                    |
| **Scaffolding**          | `scaffolding`          | Project and repo scaffolding                                | scaffold-go-cli, bootstrap-project                       |
| **CI and Release**       | `ci-and-release`       | CI workflows, installers, release automation, repo audits   | setup-ci, add-goreleaser-homebrew, setup-secret-scanning |
| **Agents**               | `agents`               | Meta-tools for the agent ecosystem                          | clean-up-agent-config, create-plugin                     |

### Adding a New Skill or Command-Style Plugin

1. Add the plugin to `.claude-plugin/marketplace.json` with the correct `category` and canonical `description`.
1. Insert a row in the matching root README category table.
1. Use the exact marketplace description in `What it does`.
1. Create a per-plugin README (see below).

## Hooks Table

Hooks are listed under `## Hooks` in a 2-column table because they have no slash-command trigger:

```markdown
| Plugin | What it does |
| --- | --- |
| [Hook Name](./plugins/hook-name/README.md) | Canonical marketplace description. |
```

Format rules:

- Insert the row alphabetically by hook display name.
- Link the hook name to `./plugins/PLUGIN-NAME/README.md`.
- Copy the canonical marketplace `description` field verbatim into `What it does`.

### Category Guide for Hooks

| Root README section | Marketplace category | Covers                         | Examples                     |
| ------------------- | -------------------- | ------------------------------ | ---------------------------- |
| **Hooks**           | `workflow`           | General workflow utility hooks | notify, update-docs-reminder |

### Adding a New Hook

1. Add the hook to `.claude-plugin/marketplace.json` with the correct `category` and canonical `description`.
1. Insert a row in the hooks table.
1. Use the exact marketplace description in `What it does`.
1. Create a per-plugin README (see below).

## External Tools

If a plugin requires external tools, update the `**External tools:**` bullet list immediately below the relevant category table. Use one bullet per plugin, or one bullet for a small group of plugins that share the same requirement:

```markdown
**External tools:**

- *Plugin Name:* [`tool`](https://example.com/)
- *Plugin A, Plugin B:* [`tool`](https://example.com/)
```

Omit the external-tools list for categories where no listed plugin requires external tools.

## Per-Plugin README

Every plugin has a `README.md` in its plugin directory (`plugins/<name>/README.md`). This is user-facing documentation, distinct from the agent-facing `SKILL.md`.

### Template for Skills

````markdown
# Plugin Name

One-sentence description.

**Type:** Skill
**Trigger:** `/plugin-name` [(also activates automatically)]

## Installation

Add the [`cboone/agent-harness-plugins`](https://github.com/cboone/agent-harness-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/agent-harness-plugins
```

Then select **Plugin Name** from the available plugins.

## What It Does

2-4 sentences describing the outcome for the user. Focus on what the user
gets, not internal agent workflow.

## Requirements

(Only if external dependencies exist.)

- [`dependency`](URL). Install via Homebrew: `brew install dependency`

## Usage

The trigger command and any flags/options.

## Recommended Permissions

(Only if the skill runs Bash commands that trigger permission prompts.)

This skill runs [brief description of command types] that trigger permission
prompts. To allow them automatically, add these rules to your
`.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(command pattern 1)", "Bash(command pattern 2)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it.
Review and adjust the rules to match your security preferences.

## Examples

Trigger phrases or usage scenarios.

## See Also

- [Related Plugin](../related-plugin/README.md): brief reason
- [All plugins](../../README.md)
````

### Template for Hooks

````markdown
# Hook Name

One-sentence description.

**Type:** Hook
**Requires:** [`dependency`](URL). Install via [Homebrew](https://brew.sh): `brew install dependency`

## Installation

Add the [`cboone/agent-harness-plugins`](https://github.com/cboone/agent-harness-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/agent-harness-plugins
```

Then select **Hook Name** from the available plugins.

## What It Does

2-4 sentences describing the outcome for the user.

## When It Fires

Describe what events trigger the hook and what happens.

## See Also

- [All plugins](../../README.md)
````

### Template for Commands

````markdown
# Command Name

One-sentence description.

**Type:** Command
**Trigger:** `/command-name`

## Installation

Add the [`cboone/agent-harness-plugins`](https://github.com/cboone/agent-harness-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/agent-harness-plugins
```

Then select **Command Name** from the available plugins.

## What It Does

2-4 sentences describing the outcome for the user. Focus on what the user
gets, not internal agent workflow.

## Requirements

(Only if external dependencies exist.)

- [`dependency`](URL). Install via Homebrew: `brew install dependency`

## Usage

The trigger command and any arguments.

```text
/command-name [argument]
```

## Arguments

| Argument   | Description                          |
| ---------- | ------------------------------------ |
| `arg-name` | What this argument does. (Optional.) |

## See Also

- [Related Plugin](../related-plugin/README.md): brief reason
- [All plugins](../../README.md)
````

### Variations

- **Style guides** (write-go-code, write-markdown, write-bash-scripts): Note automatic activation in the trigger line. Mention the reference structure.
- **Simple skills** with no options: Omit the options table from Usage.
- **Hooks** with no dependencies: Omit the Requires line.
- **Skills that run Bash commands**: Include the Recommended Permissions section with specific `Bash(pattern)` rules derived from the SKILL.md commands. Omit this section for skills that only use Read/Glob/Grep tools.
- **Commands** with no arguments: Omit the Arguments table from Usage.
- **Commands** with arguments: Include the Arguments table and show usage examples.

## Notes

- Keep descriptions concise and focused on what the user gets from installing the plugin.
- The README audience is users deciding whether to install a plugin, not developers extending one.
- Match the tone and level of detail of existing entries.
