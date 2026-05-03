---
name: create-plugin
description: >-
  Guide for creating new plugins in this repository with consistent structure
  and conventions.
---

# Create Plugin

Create a new plugin for this repository following established conventions.

## Workflow

### 1. Determine Plugin Type

Infer the plugin type from the user's request:

- **Skills plugin**: Provides instructions and workflows that Claude Code follows (e.g., style guides, multi-step procedures). Most plugins are this type.
- **Command plugin**: Provides slash commands that users invoke explicitly (e.g., `/setup-ci`, `/scaffold-go-cli`). Commands are structured Markdown files with frontmatter, a workflow, and optional reference templates.
- **Hooks plugin**: Provides event-driven shell commands that run automatically in response to Claude Code lifecycle events (e.g., notifications on task completion).
- **Combinations**: A plugin can provide any combination of skills, commands, and hooks.

Inference heuristic: "create a command", "add a slash command", "add a `/something` command" implies a command plugin. "create a skill", "add a style guide", "add a workflow" implies a skills plugin. "create a hook", "add a notification" implies a hooks plugin.

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

#### Command Plugin

```text
plugins/PLUGIN-NAME/.claude-plugin/
plugins/PLUGIN-NAME/commands/
```

Add a `references/` directory if the command has large templates to extract:

```text
plugins/PLUGIN-NAME/references/
```

#### Hooks Plugin

```text
plugins/PLUGIN-NAME/.claude-plugin/
plugins/PLUGIN-NAME/hooks/
plugins/PLUGIN-NAME/scripts/
```

#### Combinations

Combine structures under the same plugin directory as needed. A plugin can have any combination of `skills/`, `commands/`, `hooks/`, `scripts/`, and `references/`.

### 4. Write plugin.json

Create `.claude-plugin/plugin.json` with alphabetized fields. See `./references/plugin-json.md` for the full field list, versioning rules, and templates for each plugin type (Skills, Commands, Hooks).

Key points:

- New plugins start at version `1.0.0`
- Include `"skills": "./skills"` only if the plugin provides skills
- Include `"commands": "./commands"` only if the plugin provides commands
- The `name` field must match the directory name

### 5. Write SKILL.md, hooks.json, or Command .md

#### For Skills

Create `skills/PLUGIN-NAME/SKILL.md`. See `./references/skill-md.md` for the frontmatter format, description formula, common sections, and examples.

Key points:

- Frontmatter has exactly two fields: `name` and `description`
- The `description` includes trigger phrases for automatic activation
- Use `>-` (folded block scalar) for multi-line descriptions
- Structure the body with a `## Workflow` section using numbered steps

#### For Commands

Create `commands/COMMAND-NAME.md`. See `./references/command-md.md` for the frontmatter fields, argument handling, external file references, and body structure.

Key points:

- Frontmatter includes `description` and `disable-model-invocation: true`
- Add `argument-hint` if the command accepts arguments
- Use `$ARGUMENTS` and `$1`/`$2` for argument access in the body
- Structure the body with `## Workflow` numbered steps, `## Error Handling`, and `## Reference:` sections
- For large commands, extract templates into `references/` files using `@${CLAUDE_PLUGIN_ROOT}/references/file.md`

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

Skills and commands that need supplementary documentation or templates should place them under `references/`:

- **Flat structure**: `references/FILE.md` -- for a small number of reference files
- **Categorized structure**: `references/CATEGORY/FILE.md` -- for many files organized by topic (e.g., `references/essential/` and `references/comprehensive/`)

**For skills**: Reference files are plain Markdown. Point to them from SKILL.md with relative paths (e.g., `./references/checklist.md`).

**For commands**: Reference files contain templates that the command uses at runtime. Include them in the command file using the `@${CLAUDE_PLUGIN_ROOT}/references/file.md` pattern. Place `references/` alongside `commands/` (not inside it). See `./references/command-md.md` for the extraction guidelines and file format.

### 8. Register in marketplace.json

Add a new entry to the `plugins` array in `.claude-plugin/marketplace.json`. See `./references/marketplace-json.md` for the entry format, valid categories, and insertion conventions.

Key points:

- Insert alphabetically by plugin name
- Include `category` and `source` fields (not present in `plugin.json`)
- All shared fields must match `plugin.json` exactly
- Do not hand-edit `.agents/plugins/marketplace.json` or `dist/codex/`; regenerate them with `bin/build-codex-marketplace`

### 9. Update README.md

Add the new plugin to two places in `README.md`. See `./references/readme-updates.md` for the exact format of each section.

1. **Table of Contents**: Add link alphabetically in the Skills, Commands, or Hooks line
1. **Description section**: Add H3 subsection alphabetically under Skills, Commands, or Hooks

No individual install commands are needed in the Installation section; the marketplace flow handles installation.

### 10. Update CLAUDE.md

Add the new plugin to the directory tree in `CLAUDE.md`, maintaining alphabetical order among plugins. Include all files and directories created for the plugin.

### 11. Verification Checklist

Before finishing, verify:

- [ ] All new files exist with correct structure
- [ ] `plugin.json` fields are alphabetized and `name` matches the directory name
- [ ] `marketplace.json` is valid JSON with the new entry
- [ ] `marketplace.json` entry fields match `plugin.json` (shared fields)
- [ ] `bin/build-codex-marketplace` has regenerated `.agents/plugins/marketplace.json` and `dist/codex/`
- [ ] `README.md` has the new plugin in ToC, installation, and description sections
- [ ] `CLAUDE.md` directory tree reflects the new plugin structure
- [ ] `SKILL.md` frontmatter has only `name` and `description` fields (skills only)
- [ ] All reference files are reachable from `SKILL.md` via relative paths (skills only)
- [ ] Command `.md` has `description` and `disable-model-invocation: true` in frontmatter (commands only)
- [ ] Command filename matches the intended slash command name (commands only)
- [ ] `plugin.json` includes `"commands": "./commands"` (commands only)
- [ ] External file references use `@${CLAUDE_PLUGIN_ROOT}/references/` pattern (commands with extracted templates only)
- [ ] `$ARGUMENTS` handling is documented in the workflow if `argument-hint` is set (commands only)
- [ ] Scripts (if any) are executable
- [ ] Hooks (if any) reference scripts via `${CLAUDE_PLUGIN_ROOT}`

## Error Handling

- If the plugin name already exists under `plugins/`, ask the user for a different name
- If `marketplace.json` cannot be parsed as valid JSON, fix the syntax before proceeding
- If the user is unsure about the plugin type, default to a skills plugin (the most common type)
- If the user wants to add a skill to an existing plugin instead of creating a new one, bump the minor version in both `plugin.json` and `marketplace.json`
- If generated Codex files drift, run `bin/build-codex-marketplace` instead of editing generated files directly
