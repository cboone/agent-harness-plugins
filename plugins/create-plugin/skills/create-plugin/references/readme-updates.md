# README.md Updates Reference

When adding a new plugin, update three sections in the root `README.md`: the table of contents, installation commands, and the plugin description section.

## Table of Contents

The ToC is at the top of the file, organized by type and subcategory. Each entry is on its own line to prevent merge conflicts when multiple branches add plugins simultaneously:

```markdown
**Skills**
<br>_Agents_
[Skill A](#skill-a)
| [Skill B](#skill-b)
<br>_Workflow_
[Skill C](#skill-c)
| [Skill D](#skill-d)
<br>_Languages_
[Skill E](#skill-e)
<br>**Hooks**
[Hook A](#hook-a)
```

Format rules:
- **One entry per line.** This is critical for avoiding merge conflicts.
- `**Skills**` and `**Hooks**` labels have no trailing colons.
- Skills are grouped into subcategories: _Agents_, _Workflow_, _Languages_.
- Subcategory labels use `<br>_Name_` format on their own line.
- The first link in each subcategory has no leading pipe; subsequent links start with `| ` (pipe-space).
- Skills and hooks are listed alphabetically within their respective groups/subcategories.
- Anchor links use the kebab-case H3 heading (e.g., `#create-worktree-from-issue`).

### Adding a New Skill

Insert a new line with `| [Skill Name](#skill-name)` in alphabetical order within the appropriate subcategory (_Agents_, _Workflow_, or _Languages_). If the new entry is the first in its subcategory, omit the leading `| `.

### Adding a New Hook

Insert a new line with `| [Hook Name](#hook-name)` in alphabetical order within the **Hooks** group. If the new entry is the first hook, omit the leading `| `.

## Installation Commands

The installation section lists one command per plugin, alphabetically:

```markdown
/plugin install PLUGIN-NAME@cboone/cboone-cc-plugins
```

Insert the new plugin's install command in alphabetical order.

## Plugin Description Sections

### Skills Section

Each skill gets an H3 subsection under `## Skills`, in alphabetical order:

```markdown
### Skill Name

One-paragraph description of what the skill does, what it creates or produces,
and any notable behavior.

You can trigger it directly via `/skill-name`.

Requires [`dependency`](URL) to be installed.
```

Key patterns:
- The H3 heading is title case (e.g., "Create Worktree from Issue")
- The description paragraph is 1-3 sentences
- Include the `/skill-name` trigger line
- Include dependency requirements with links (only if the skill has external dependencies)
- Style guide skills note that "Claude Code should automatically use it when..." instead of listing trigger phrases

### Hooks Section

Each hook gets an H3 subsection under `## Hooks`:

````markdown
### Hook Name

Description of what the hook does and when it fires.

Requires [`dependency`](URL). Installation instructions:

```bash
install command
```
````

## Notes

- Keep descriptions concise and focused on what the user gets from installing the plugin.
- The README audience is users deciding whether to install a plugin, not developers extending one.
- Match the tone and level of detail of existing entries.
