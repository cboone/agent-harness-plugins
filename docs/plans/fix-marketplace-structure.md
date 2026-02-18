# Fix Claude Code Plugins Marketplace Structure

## Summary

Update the plugins marketplace to conform to current Claude Code standards (January 2026). This involves fixing the marketplace.json schema, restructuring the skills plugin, and cleaning up plugin.json files.

## Issues Found

### marketplace.json

1. Duplicate `description` at root level and in `metadata`
1. Plugin entries contain `author.url` (not in official schema)
1. Plugin entries have `hooks` and `skills` fields (should be auto-discovered)
1. Duplicate data in `tags` and `keywords` arrays
1. Missing `$schema` field
1. Keywords not alphabetized

### plugin.json files

1. Both contain `author.url` (not in official schema)
1. Keywords not alphabetized

### Skill structure

1. `SKILL.md` at plugin root level should be in `skills/<skill-name>/SKILL.md`

## Implementation

### Phase 1: Restructure write-shell-scripts Plugin

Create proper skills directory structure:

```text
plugins/write-shell-scripts/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── write-shell-scripts/
        ├── SKILL.md
        └── references/
            └── BASH.md
```

**Commands:**

```bash
mkdir -p plugins/write-shell-scripts/skills/write-shell-scripts
mv plugins/write-shell-scripts/SKILL.md plugins/write-shell-scripts/skills/write-shell-scripts/
mv plugins/write-shell-scripts/references plugins/write-shell-scripts/skills/write-shell-scripts/
```

### Phase 2: Update plugin.json Files

**File:** `plugins/notify/.claude-plugin/plugin.json`

- Remove `author.url`
- Alphabetize `keywords`: `["alerts", "macos", "notifications"]`

**File:** `plugins/write-shell-scripts/.claude-plugin/plugin.json`

- Remove `author.url`
- Alphabetize `keywords`: `["bash", "format", "scripts", "shell", "style"]`

### Phase 3: Update marketplace.json

**File:** `.claude-plugin/marketplace.json`

Changes:

1. Add `$schema` field
1. Remove root-level `description` (keep only in `metadata`)
1. Remove `author.url` from plugin entries
1. Remove `hooks` field from notify plugin (auto-discovered)
1. Remove `skills` field from write-shell-scripts plugin (auto-discovered)
1. Remove `tags` arrays (redundant with `keywords`)
1. Alphabetize `keywords` arrays
1. Bump `metadata.version` to `1.0.3`

**Target structure:**

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "metadata": {
    "description": "Claude Code skills and hooks from Christopher Boone (cboone.github.io)",
    "version": "1.0.3"
  },
  "name": "cboone-cc-plugins",
  "owner": {
    "name": "Christopher Boone"
  },
  "plugins": [
    {
      "author": { "name": "Christopher Boone" },
      "category": "productivity",
      "description": "Notifies you when Claude finishes a task or needs your attention.",
      "homepage": "https://github.com/cboone/cboone-cc-plugins",
      "keywords": ["alerts", "macos", "notifications"],
      "license": "MIT",
      "name": "notify",
      "repository": "https://github.com/cboone/cboone-cc-plugins",
      "source": "./plugins/notify",
      "version": "1.0.2"
    },
    {
      "author": { "name": "Christopher Boone" },
      "category": "code-quality",
      "description": "Applies Bash style conventions when creating or editing shell scripts.",
      "homepage": "https://github.com/cboone/cboone-cc-plugins",
      "keywords": ["bash", "format", "scripts", "shell", "style"],
      "license": "MIT",
      "name": "write-shell-scripts",
      "repository": "https://github.com/cboone/cboone-cc-plugins",
      "source": "./plugins/write-shell-scripts",
      "version": "1.0.2"
    }
  ]
}
```

### Phase 4: Update Documentation

**File:** `CLAUDE.md`

Update the structure section to reflect new skills directory layout.

## Files to Modify

| File                                                     | Action                                    |
| -------------------------------------------------------- | ----------------------------------------- |
| `plugins/write-shell-scripts/SKILL.md`                   | Move to `skills/write-shell-scripts/`     |
| `plugins/write-shell-scripts/references/`                | Move to `skills/write-shell-scripts/`     |
| `plugins/notify/.claude-plugin/plugin.json`              | Remove `author.url`, alphabetize keywords |
| `plugins/write-shell-scripts/.claude-plugin/plugin.json` | Remove `author.url`, alphabetize keywords |
| `.claude-plugin/marketplace.json`                        | Schema fixes, remove redundant fields     |
| `CLAUDE.md`                                              | Update structure documentation            |

## Verification

1. Validate the marketplace:

   ```bash
   claude plugin validate .
   ```

1. Test plugin installation:

   ```text
   /plugin marketplace add ./
   /plugin install notify@cboone-cc-plugins
   /plugin install write-shell-scripts@cboone-cc-plugins
   ```

1. Test skill invocation:

   ```text
   /write-shell-scripts
   ```

## Sources

- [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference)
- [Extend Claude with skills](https://code.claude.com/docs/en/skills)
