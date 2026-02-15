# marketplace.json Reference

The root `.claude-plugin/marketplace.json` is the plugin registry for this repository. It lists all available plugins so Claude Code can discover and install them.

## File Location

```
.claude-plugin/marketplace.json
```

## Top-Level Structure

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "metadata": {
    "description": "Claude Code skills and hooks from Christopher Boone (cboone.github.io)",
    "version": "1.1.0"
  },
  "name": "cboone-cc-plugins",
  "owner": {
    "name": "Christopher Boone"
  },
  "plugins": [...]
}
```

The `metadata.version` is for the registry itself, not individual plugins. It does not need to be bumped when adding new plugins.

## Plugin Entry Fields

Each entry in the `plugins` array has these fields, alphabetized:

| Field | Type | Description |
|-------|------|-------------|
| `author` | object | `{ "name": "Christopher Boone" }` |
| `category` | string | One of the valid categories listed below. |
| `description` | string | One-sentence summary. Must match `plugin.json`. |
| `homepage` | string | `"https://github.com/cboone/cboone-cc-plugins"` |
| `keywords` | array | Must match `plugin.json`. |
| `license` | string | `"MIT"` |
| `name` | string | Plugin name. Must match `plugin.json`. |
| `repository` | string | `"https://github.com/cboone/cboone-cc-plugins"` |
| `source` | string | Relative path to the plugin directory (e.g., `"./plugins/my-plugin"`). |
| `version` | string | Must match `plugin.json`. |

## Valid Categories

Categories currently used in this repository:

- `"code-quality"` -- style guides, code review tools, linting
- `"productivity"` -- workflow automation, scaffolding, issue management

## Plugin Entry Template

```json
{
  "author": {
    "name": "Christopher Boone"
  },
  "category": "CATEGORY",
  "description": "DESCRIPTION",
  "homepage": "https://github.com/cboone/cboone-cc-plugins",
  "keywords": ["KEYWORD1", "KEYWORD2"],
  "license": "MIT",
  "name": "PLUGIN-NAME",
  "repository": "https://github.com/cboone/cboone-cc-plugins",
  "source": "./plugins/PLUGIN-NAME",
  "version": "1.0.0"
}
```

## Insertion Order

When adding a new plugin, insert its entry into the `plugins` array in alphabetical order by the `name` field.

## Notes

- The `category` and `source` fields are present in `marketplace.json` but not in `plugin.json`.
- The `skills` field is present in `plugin.json` but not in `marketplace.json`.
- All other shared fields (`author`, `description`, `homepage`, `keywords`, `license`, `name`, `repository`, `version`) must match between the two files.
