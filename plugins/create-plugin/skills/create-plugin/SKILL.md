---
name: create-plugin
description: >-
  Guide for creating new plugins in this repository with consistent structure
  and conventions. Use when the user says "create a plugin", "add a new skill",
  "add a new hook", "new plugin", "scaffold plugin", "create a new plugin", or
  asks to add a skill or hook to this repository.
---

# Create Plugin

Create a new plugin for this repository following established conventions.

## Workflow

### 1. Determine Plugin Type

Infer the plugin type from the user's request:

- **Skills plugin**: Provides instructions and workflows that Claude Code follows (e.g., style guides, multi-step procedures). Most plugins are this type.
- **Hooks plugin**: Provides event-driven shell commands that run automatically in response to Claude Code lifecycle events (e.g., notifications on task completion).
- **Both**: A plugin can provide both skills and hooks.

If the request doesn't imply a type (e.g., just "create a plugin"), ask. If ambiguous, default to a skills plugin.

### 2. Choose a Name

The plugin name must be:

- **Kebab-case** (e.g., `write-go-code`, `suggest-next-issue`)
- **Verb-noun preferred** (e.g., `create-worktree-from-issue`, `resolve-copilot-pr-feedback`)
- **Descriptive** of what the plugin does
- **Unique** within the `plugins/` directory

If the user provided a name, use it. Otherwise, generate a descriptive name from the plugin's purpose and proceed.

### 3. Create Directory Structure

No manual `mkdir` is needed — the Write tool creates parent directories automatically when writing files. The directories below are created implicitly when their first file is written in the subsequent steps.

#### Skills Plugin

```text
plugins/PLUGIN-NAME/.claude-plugin/
plugins/PLUGIN-NAME/skills/PLUGIN-NAME/
```

Add a `references/` subdirectory if the skill needs supplementary documentation:

```text
plugins/PLUGIN-NAME/skills/PLUGIN-NAME/references/
```

#### Hooks Plugin

```text
plugins/PLUGIN-NAME/.claude-plugin/
plugins/PLUGIN-NAME/hooks/
plugins/PLUGIN-NAME/scripts/
```

#### Both

Combine both structures under the same plugin directory.

### 4. Write plugin.json

Create `.claude-plugin/plugin.json` with alphabetized fields. See `./references/plugin-json.md` for the full field list, versioning rules, and templates for each plugin type.

Key points:

- New plugins start at version `1.0.0`
- Include `"skills": "./skills"` only if the plugin provides skills
- The `name` field must match the directory name

### 5. Write SKILL.md or hooks.json

#### For Skills

Create `skills/PLUGIN-NAME/SKILL.md`. See `./references/skill-md.md` for the frontmatter format, description formula, common sections, and examples.

Key points:

- Frontmatter has exactly two fields: `name` and `description`
- The `description` includes trigger phrases for automatic activation
- Use `>-` (folded block scalar) for multi-line descriptions
- Structure the body with a `## Workflow` section using numbered steps

#### For Hooks

Create `hooks/hooks.json`. See `./references/hooks-json.md` for the JSON schema, hook categories, matchers, and examples.

Key points:

- Use `${CLAUDE_PLUGIN_ROOT}` to reference scripts
- Each hook entry has `"type": "command"`

### 6. Add Scripts (if needed)

If the plugin needs executable scripts, create them under `scripts/`. See `./references/scripts.md` for the required structure, conventions, and patterns.

Key points:

- No file extension for executables
- Must be `chmod +x`
- Follow the Bash conventions (shebang, strict mode, main function pattern)
- Prefix implementation functions with `do_`

### 7. Add Reference Files (if needed)

Skills that need supplementary documentation should place it under `references/`:

- **Flat structure**: `references/FILE.md` -- for a small number of reference files
- **Categorized structure**: `references/CATEGORY/FILE.md` -- for many files organized by topic (e.g., `references/essential/` and `references/comprehensive/`)

Reference files are plain Markdown. Point to them from SKILL.md with relative paths.

### 8. Register in marketplace.json

Add a new entry to the `plugins` array in `.claude-plugin/marketplace.json`. See `./references/marketplace-json.md` for the entry format, valid categories, and insertion conventions.

Key points:

- Insert alphabetically by plugin name
- Include `category` and `source` fields (not present in `plugin.json`)
- All shared fields must match `plugin.json` exactly

### 9. Update README.md

Add the new plugin to three places in `README.md`. See `./references/readme-updates.md` for the exact format of each section.

1. **Table of Contents**: Add link alphabetically in the Skills or Hooks line
1. **Installation**: Add `/plugin install` command alphabetically
1. **Description section**: Add H3 subsection alphabetically under Skills or Hooks

### 10. Update CLAUDE.md

Add the new plugin to the directory tree in `CLAUDE.md`, maintaining alphabetical order among plugins. Include all files and directories created for the plugin.

### 11. Verification Checklist

Before finishing, verify:

- [ ] All new files exist with correct structure
- [ ] `plugin.json` fields are alphabetized and `name` matches the directory name
- [ ] `marketplace.json` is valid JSON with the new entry
- [ ] `marketplace.json` entry fields match `plugin.json` (shared fields)
- [ ] `README.md` has the new plugin in ToC, installation, and description sections
- [ ] `CLAUDE.md` directory tree reflects the new plugin structure
- [ ] `SKILL.md` frontmatter has only `name` and `description` fields
- [ ] All reference files are reachable from `SKILL.md` via relative paths
- [ ] Scripts (if any) are executable
- [ ] Hooks (if any) reference scripts via `${CLAUDE_PLUGIN_ROOT}`

## Error Handling

- If the plugin name already exists under `plugins/`, ask the user for a different name
- If `marketplace.json` cannot be parsed as valid JSON, fix the syntax before proceeding
- If the user is unsure about the plugin type, default to a skills plugin (the most common type)
- If the user wants to add a skill to an existing plugin instead of creating a new one, bump the minor version in both `plugin.json` and `marketplace.json`
