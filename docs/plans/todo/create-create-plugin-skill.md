# Plan: Create a create-plugin Skill

## Context

This repository has six plugins following consistent patterns, but the conventions are implicit -- spread across CLAUDE.md's four-step checklist, existing plugin files, and undocumented norms. A new "create-plugin" skill consolidates all these practices into an authoritative guide that Claude can follow when creating new plugins for this repository.

## Files to Create

```text
plugins/create-plugin/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── create-plugin/
        ├── SKILL.md
        └── references/
            ├── hooks-json.md
            ├── marketplace-json.md
            ├── plugin-json.md
            ├── readme-updates.md
            ├── scripts.md
            └── skill-md.md
```

## Files to Modify

- `.claude-plugin/marketplace.json` -- add new plugin entry
- `README.md` -- add ToC link, install command, and Skills subsection
- `CLAUDE.md` -- add new plugin to directory tree

## Implementation

### 1. Create directory structure

```bash
mkdir -p plugins/create-plugin/.claude-plugin
mkdir -p plugins/create-plugin/skills/create-plugin/references
```

### 2. Write `plugins/create-plugin/.claude-plugin/plugin.json`

Standard plugin.json for a skills plugin. Fields alphabetized, `"skills": "./skills"` included, version `"1.0.0"`, keywords: `["claude-code", "hooks", "plugins", "scaffolding", "skills"]`, category will be `"productivity"`.

### Versioning Convention

Both `plugin.json` and `marketplace.json` include a `version` field. The versioning rules for this repository:

- **New plugins**: start at `1.0.0`
- **New skills** (added to an existing plugin): bump the **minor** version (e.g., `1.0.0` -> `1.1.0`)
- **Skill updates** (changes to existing skills): bump the **patch** version (e.g., `1.1.0` -> `1.1.1`)
- Both `plugin.json` and `marketplace.json` versions must stay in sync
- The marketplace `metadata.version` is for the registry itself, not individual plugins

### 3. Write the six reference files

Each reference file documents one artifact type with exact formats, field descriptions, and templates derived from existing plugins:

| File                  | Covers                            | Key content                                                                                       |
| --------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------- |
| `plugin-json.md`      | `.claude-plugin/plugin.json`      | Field list, skill vs hooks difference (`skills` field), versioning rules, templates for each type |
| `marketplace-json.md` | `.claude-plugin/marketplace.json` | Extra fields (`category`, `source`), valid categories, versioning rules, entry template           |
| `skill-md.md`         | `skills/*/SKILL.md`               | Frontmatter format, description formula, common sections, examples from existing skills           |
| `hooks-json.md`       | `hooks/hooks.json`                | JSON schema, hook categories, matchers, `${CLAUDE_PLUGIN_ROOT}` usage                             |
| `scripts.md`          | Bash scripts in `scripts/`        | Header, strict mode, function patterns, `main "$@"`, shellcheck directives                        |
| `readme-updates.md`   | `README.md`                       | ToC format, Skills/Hooks section format, install command placement                                |

### 4. Write `plugins/create-plugin/skills/create-plugin/SKILL.md`

The main skill file with:

- Frontmatter: `name: create-plugin`, `description` with trigger phrases ("create a plugin", "add a new skill", "add a new hook", "new plugin", "scaffold plugin")
- Workflow steps:
  1. Determine plugin type (skill vs hooks)
  1. Choose a name (kebab-case, verb-noun preferred)
  1. Create directory structure (with templates for each type)
  1. Write plugin.json with correct version (points to `references/plugin-json.md`)
  1. Write SKILL.md or hooks.json (points to `references/skill-md.md` or `references/hooks-json.md`)
  1. Add scripts if needed (points to `references/scripts.md`)
  1. Add reference files if needed (skills only, flat vs categorized patterns)
  1. Register in marketplace.json (points to `references/marketplace-json.md`)
  1. Update README.md (points to `references/readme-updates.md`)
  1. Update CLAUDE.md directory tree
  1. Verification checklist
- Error handling section

### 5. Update `marketplace.json`

Add new entry with `"category": "productivity"`, `"source": "./plugins/create-plugin"`. Insert alphabetically (before `create-worktree-from-issue`).

### 6. Update `README.md`

- ToC: add `[Create Plugin](#create-plugin)` before "Create Worktree from Issue"
- Installation: add `/plugin install create-plugin@cboone/cboone-cc-plugins` (alphabetical)
- Skills section: add new H3 subsection before "Create Worktree from Issue"

### 7. Update `CLAUDE.md`

Add the new plugin to the directory tree, before `create-worktree-from-issue`.

## Verification

- All new files exist with correct structure
- plugin.json fields are alphabetized and match directory name
- marketplace.json is valid JSON with new entry
- README.md has new plugin in ToC, installation, and Skills sections
- CLAUDE.md directory tree reflects new plugin structure
- SKILL.md frontmatter has only `name` and `description`
- All reference files are reachable from SKILL.md via relative paths
