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

### Subcategory Guide

Use this guide to determine which subcategory a new plugin belongs to:

| Subcategory | Covers | Examples |
| ----------------------- | ----------------------------------------- | ---------------------------------------- |
| **Git** | Commit-to-PR pipeline | commit, merge-main, pr, review-branch |
| **Issues and Worktrees** | Multi-agent and issue-driven work | create-worktree, suggest-next-issue |
| **Code Review** | Responding to external feedback | address-review, resolve-copilot-pr-feedback |
| **Code Quality** | Style guides, linting, formatting | lint-and-fix, write-go-code |
| **Scaffolding** | Project and repo setup | scaffold-go-cli, setup-gitleaks |
| **Agents** | Meta-tools for the agent ecosystem | clean-up-agent-config, create-plugin |

### Adding a New Skill

1. Insert a new line with `∙ [Skill Name](#skill-name)` in alphabetical order within the appropriate subcategory. If the new entry is the first in its subcategory, omit the leading `∙`.
1. Add an H3 description section (see below).
1. Create a per-plugin README (see below).

### Adding a New Hook

1. Insert a new line with `∙ [Hook Name](#hook-name)` in alphabetical order within the appropriate subcategory (Security or Workflow). If the new entry is the first in its subcategory, omit the leading `∙`.
1. Add an H3 description section (see below).
1. Create a per-plugin README (see below).

## Installation Section

The installation section directs users to add the marketplace and browse plugins from there. It does not list individual install commands; users select plugins interactively after adding the marketplace.

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
- When a skill also activates automatically, note it parenthetically: `` > **Trigger:** `/skill-name` (also activates automatically) ``

### Hooks Section

Each hook gets an H3 subsection under `## Hooks`. The description is 1-2 sentences, followed by a blockquote with any dependency requirements and a details link:

```markdown
### Hook Name

Description of what the hook does and when it fires.

> **Requires:** [`dependency`](URL). Install via [Homebrew](https://brew.sh): `install command`
> **Details:** [README](./plugins/hook-name/README.md)
```

## Per-Plugin README

Every plugin has a `README.md` in its plugin directory (`plugins/<name>/README.md`). This is user-facing documentation, distinct from the agent-facing `SKILL.md`.

### Template for Skills

```markdown
# Plugin Name

One-sentence description.

**Type:** Skill
**Trigger:** `/plugin-name` [(also activates automatically)]

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

` ```text `
/plugin marketplace add cboone/cboone-cc-plugins
` ``` `

Then select **Plugin Name** from the available plugins.

## What It Does

2-4 sentences describing the outcome for the user. Focus on what the user
gets, not internal agent workflow.

## Requirements

(Only if external dependencies exist.)

- [`dependency`](URL). Install via Homebrew: `brew install dependency`

## Usage

The trigger command and any flags/options.

## Examples

Trigger phrases or usage scenarios.

## See Also

- [Related Plugin](../related-plugin/README.md): brief reason
- [All plugins](../../README.md)
```

### Template for Hooks

```markdown
# Hook Name

One-sentence description.

**Type:** Hook
**Requires:** [`dependency`](URL). Install via [Homebrew](https://brew.sh): `brew install dependency`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

` ```text `
/plugin marketplace add cboone/cboone-cc-plugins
` ``` `

Then select **Hook Name** from the available plugins.

## What It Does

2-4 sentences describing the outcome for the user.

## When It Fires

Describe what events trigger the hook and what happens.

## See Also

- [All plugins](../../README.md)
```

### Variations

- **Style guides** (write-go-code, write-markdown, write-shell-scripts): Note automatic activation in the trigger line. Mention the reference structure.
- **Simple skills** with no options: Omit the options table from Usage.
- **Hooks** with no dependencies: Omit the Requires line.

## Notes

- Keep descriptions concise and focused on what the user gets from installing the plugin.
- The README audience is users deciding whether to install a plugin, not developers extending one.
- Match the tone and level of detail of existing entries.
