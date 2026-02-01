# Fix Claude Code Plugins Marketplace Structure

## Summary

Update the plugins marketplace to conform to current Claude Code standards (January 2026). This involves fixing the marketplace.json schema, restructuring the skills plugin, and cleaning up plugin.json files.

## Issues Found

### marketplace.json
1. Duplicate `description` at root level and in `metadata`
2. Plugin entries contain `author.url` (not in official schema)
3. Plugin entries have `hooks` and `skills` fields (should be auto-discovered)
4. Duplicate data in `tags` and `keywords` arrays
5. Missing `$schema` field
6. Keywords not alphabetized

### plugin.json files
1. Both contain `author.url` (not in official schema)
2. Keywords not alphabetized

### Skill structure
1. `SKILL.md` at plugin root level should be in `skills/<skill-name>/SKILL.md`

## Implementation

### Phase 1: Restructure writing-shell-scripts Plugin

Create proper skills directory structure:

```
plugins/writing-shell-scripts/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── writing-shell-scripts/
        ├── SKILL.md
        └── references/
            └── BASH.md
```

**Commands:**
```bash
mkdir -p plugins/writing-shell-scripts/skills/writing-shell-scripts
mv plugins/writing-shell-scripts/SKILL.md plugins/writing-shell-scripts/skills/writing-shell-scripts/
mv plugins/writing-shell-scripts/references plugins/writing-shell-scripts/skills/writing-shell-scripts/
```

### Phase 2: Update plugin.json Files

**File:** `plugins/notify/.claude-plugin/plugin.json`
- Remove `author.url`
- Alphabetize `keywords`: `["alerts", "macos", "notifications"]`

**File:** `plugins/writing-shell-scripts/.claude-plugin/plugin.json`
- Remove `author.url`
- Alphabetize `keywords`: `["bash", "format", "scripts", "shell", "style"]`

### Phase 3: Update marketplace.json

**File:** `.claude-plugin/marketplace.json`

Changes:
1. Add `$schema` field
2. Remove root-level `description` (keep only in `metadata`)
3. Remove `author.url` from plugin entries
4. Remove `hooks` field from notify plugin (auto-discovered)
5. Remove `skills` field from writing-shell-scripts plugin (auto-discovered)
6. Remove `tags` arrays (redundant with `keywords`)
7. Alphabetize `keywords` arrays
8. Bump `metadata.version` to `1.0.3`

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
      "name": "writing-shell-scripts",
      "repository": "https://github.com/cboone/cboone-cc-plugins",
      "source": "./plugins/writing-shell-scripts",
      "version": "1.0.2"
    }
  ]
}
```

### Phase 4: Update Documentation

**File:** `CLAUDE.md`

Update the structure section to reflect new skills directory layout.

## Files to Modify

| File | Action |
|------|--------|
| `plugins/writing-shell-scripts/SKILL.md` | Move to `skills/writing-shell-scripts/` |
| `plugins/writing-shell-scripts/references/` | Move to `skills/writing-shell-scripts/` |
| `plugins/notify/.claude-plugin/plugin.json` | Remove `author.url`, alphabetize keywords |
| `plugins/writing-shell-scripts/.claude-plugin/plugin.json` | Remove `author.url`, alphabetize keywords |
| `.claude-plugin/marketplace.json` | Schema fixes, remove redundant fields |
| `CLAUDE.md` | Update structure documentation |

## Verification

1. Validate the marketplace:
   ```bash
   claude plugin validate .
   ```

2. Test plugin installation:
   ```
   /plugin marketplace add ./
   /plugin install notify@cboone-cc-plugins
   /plugin install writing-shell-scripts@cboone-cc-plugins
   ```

3. Test skill invocation:
   ```
   /writing-shell-scripts
   ```

## Sources

- [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference)
- [Extend Claude with skills](https://code.claude.com/docs/en/skills)
