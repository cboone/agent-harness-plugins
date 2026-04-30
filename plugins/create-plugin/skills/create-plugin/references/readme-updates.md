# README.md Updates Reference

When adding a new plugin, update two sections in the root `README.md` (the table of contents and the plugin description section) and create a per-plugin `README.md` in the plugin directory.

## Table of Contents

The ToC is at the top of the file, organized by type and subcategory. Each entry is on its own line to prevent merge conflicts when multiple branches add plugins simultaneously:

```markdown
**Skills**
<br>Git:
[Skill A](#skill-a)
∙ [Skill B](#skill-b)
<br>Issues and Worktrees:
[Skill C](#skill-c)
<br>Code Review:
[Skill D](#skill-d)
<br>Code Quality:
[Skill E](#skill-e)
<br>Scaffolding:
[Skill F](#skill-f)
<br>Agents:
[Skill G](#skill-g)

**Hooks**
<br>Security:
[Hook A](#hook-a)
<br>Workflow:
[Hook B](#hook-b)
```

Format rules:

- **One entry per line.** This is critical for avoiding merge conflicts.
- **Skills** and **Hooks** are separated by a blank line.
- Skills are grouped into subcategories: Git, Issues and Worktrees, Code Review, Code Quality, Scaffolding, Agents.
- Hooks are grouped into subcategories: Security, Workflow.
- Subcategory labels use `<br>Name:` format (plain text with trailing colon) on their own line.
- The first link in each subcategory has no leading middle dot; subsequent links start with `∙` (middle dot, space).
- Skills and hooks are listed alphabetically within their respective groups/subcategories.
- Anchor links use the kebab-case H3 heading (e.g., `#create-worktree-from-issue`).

### Subcategory Guide for Skills

Use this guide to determine which subcategory a new skill belongs to. Each subcategory maps directly to a marketplace `category` value (kebab-case version of the label). Keep the README ToC subcategory and the marketplace `category` aligned so filtering in either place yields the same grouping.

| Subcategory              | Marketplace category   | Covers                                                      | Examples                                                 |
| ------------------------ | ---------------------- | ----------------------------------------------------------- | -------------------------------------------------------- |
| **Git**                  | `git`                  | Commit-to-PR pipeline                                       | commit, merge-main, pr, review-branch, use-git           |
| **Issues and Worktrees** | `issues-and-worktrees` | Multi-agent and issue-driven work                           | create-worktree, suggest-next-issue                      |
| **Code Review**          | `code-review`          | Responding to external feedback                             | address-review, resolve-copilot-pr-feedback              |
| **Code Quality**         | `code-quality`         | Style guides for code, linting, formatting                  | lint-and-fix, write-go-code                              |
| **Writing**              | `writing`              | Style and structure guides for prose and document artifacts | write-markdown, write-pandoc-markdown                    |
| **Scaffolding**          | `scaffolding`          | Project and repo scaffolding                                | scaffold-go-cli, bootstrap-project                       |
| **CI and Release**       | `ci-and-release`       | CI workflows, installers, release automation, repo audits   | setup-ci, add-goreleaser-homebrew, setup-secret-scanning |
| **Agents**               | `agents`               | Meta-tools for the agent ecosystem                          | clean-up-agent-config, create-plugin                     |

### Adding a New Skill

1. Insert a new line with `∙ [Skill Name](#skill-name)` in alphabetical order within the appropriate subcategory. If the new entry is the first in its subcategory, omit the leading `∙`.
1. Add an H3 description section (see below).
1. Create a per-plugin README (see below).

### Subcategory Guide for Hooks

Use this guide to determine which subcategory a new hook belongs to. Each subcategory maps directly to a marketplace `category` value.

| Subcategory  | Marketplace category | Covers                                | Examples                       |
| ------------ | -------------------- | ------------------------------------- | ------------------------------ |
| **Security** | `security`           | Hooks that block dangerous operations | block-rm-rf                    |
| **Workflow** | `workflow`           | General workflow utility hooks        | notify, update-docs-reminder   |

### Adding a New Hook

1. Insert a new line with `∙ [Hook Name](#hook-name)` in alphabetical order within the appropriate subcategory (Security or Workflow). If the new entry is the first in its subcategory, omit the leading `∙`.
1. Add an H3 description section (see below).
1. Create a per-plugin README (see below).

## Installation Section

The installation section directs users to add the marketplace and browse plugins from there. It does not list individual install commands; users select plugins interactively after adding the marketplace.

## Table of Contents: Commands

Commands follow the same one-entry-per-line pattern, with their own subcategories:

```markdown
**Commands**
<br>Scaffolding:
[Command A](#command-a)
∙ [Command B](#command-b)
<br>CI/CD:
[Command C](#command-c)
<br>Security:
[Command D](#command-d)
```

Format rules are identical to Skills and Hooks. Commands are separated from Skills and Hooks by a blank line.

### Subcategory Guide for Commands

| Subcategory     | Covers                               | Examples                           |
| --------------- | ------------------------------------ | ---------------------------------- |
| **Scaffolding** | Project and repo setup commands      | scaffold-go-cli, scaffold-new-repo |
| **CI/CD**       | CI, release, and distribution setup  | setup-ci, add-goreleaser-homebrew  |
| **Security**    | Secret scanning and security tooling | setup-secret-scanning              |

### Adding a New Command

1. Insert a new line with `∙ [Command Name](#command-name)` in alphabetical order within the appropriate subcategory. If the new entry is the first in its subcategory, omit the leading `∙`.
1. Add an H3 description section (see below).
1. Create a per-plugin README (see below).

## Plugin Description Sections

### Skills Section

Each skill gets an H3 subsection under `## Skills`, in alphabetical order. The description is 1-2 sentences, followed by a blockquote metadata block with the trigger command, any external dependencies, and a link to the per-plugin README:

```markdown
### Skill Name

One-to-two sentence summary of what the skill does.

> **Trigger:** `/skill-name`
> **Requires:** [`dependency`](URL)
> **Details:** [README](./plugins/skill-name/README.md)
```

Key patterns:

- The H3 heading is title case (e.g., "Create Worktree from Issue")
- The description is 1-2 concise sentences
- The blockquote metadata block goes at the end of each section
- Always include the `> **Trigger:**` line
- Include `> **Requires:**` only if the skill has external dependencies
- Always include the `> **Details:**` line linking to the per-plugin README
- When a skill also activates automatically, note it parenthetically: ``> **Trigger:** `/skill-name` (also activates automatically)``

### Hooks Section

Each hook gets an H3 subsection under `## Hooks`. The description is 1-2 sentences, followed by a blockquote with any dependency requirements and a details link:

```markdown
### Hook Name

Description of what the hook does and when it fires.

> **Requires:** [`dependency`](URL). Install via [Homebrew](https://brew.sh): `install command`
> **Details:** [README](./plugins/hook-name/README.md)
```

### Commands Section

Each command gets an H3 subsection under `## Commands`, in alphabetical order. The description is 1-2 sentences, followed by a blockquote metadata block with the trigger command, any external dependencies, and a link to the per-plugin README:

```markdown
### Command Name

One-to-two sentence summary of what the command does.

> **Trigger:** `/command-name`
> **Requires:** [`dependency`](URL)
> **Details:** [README](./plugins/command-name/README.md)
```

Key patterns:

- The H3 heading is title case (e.g., "Setup CI", "Scaffold Go CLI")
- The description is 1-2 concise sentences
- The blockquote metadata block goes at the end of each section
- Always include the `> **Trigger:**` line
- Include `> **Requires:**` only if the command has external dependencies
- Always include the `> **Details:**` line linking to the per-plugin README

## Per-Plugin README

Every plugin has a `README.md` in its plugin directory (`plugins/<name>/README.md`). This is user-facing documentation, distinct from the agent-facing `SKILL.md`.

### Template for Skills

````markdown
# Plugin Name

One-sentence description.

**Type:** Skill
**Trigger:** `/plugin-name` [(also activates automatically)]

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
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

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
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

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
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
