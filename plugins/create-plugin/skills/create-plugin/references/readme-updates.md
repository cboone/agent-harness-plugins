# README.md Updates Reference

When adding a new plugin, update three sections in the root `README.md`: the table of contents, installation commands, and the plugin description section.

## Table of Contents

The ToC is at the top of the file, organized by type:

```markdown
**Skills:** [Skill A](#skill-a) | [Skill B](#skill-b)<br>
**Hooks:** [Hook A](#hook-a)
```

- Skills and hooks are listed alphabetically within their respective lines.
- Separators are ` | ` (space-pipe-space).
- The Skills line ends with `<br>` to separate it from the Hooks line.
- Anchor links use the kebab-case H3 heading (e.g., `#create-worktree-from-issue`).

### Adding a New Skill

Insert the new skill link alphabetically in the **Skills** line.

### Adding a New Hook

Insert the new hook link alphabetically in the **Hooks** line.

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
