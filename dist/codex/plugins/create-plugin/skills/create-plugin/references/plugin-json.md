# plugin.json Reference

Every plugin has a `.claude-plugin/plugin.json` file that declares metadata and tells Claude Code what the plugin provides.

## Fields

All fields are alphabetized in the JSON file.

| Field         | Type   | Required    | Description                                                                        |
| ------------- | ------ | ----------- | ---------------------------------------------------------------------------------- |
| `author`      | object | Yes         | `{ "name": "Christopher Boone" }`                                                  |
| `description` | string | Yes         | One-sentence summary of what the plugin does. Start with a verb or noun phrase.    |
| `homepage`    | string | Yes         | `"https://github.com/cboone/agent-harness-plugins"`                                |
| `keywords`    | array  | Yes         | Lowercase, alphabetized tags for discoverability.                                  |
| `license`     | string | Yes         | `"MIT"`                                                                            |
| `name`        | string | Yes         | Plugin directory name, kebab-case. Must match the directory name under `plugins/`. |
| `repository`  | string | Yes         | `"https://github.com/cboone/agent-harness-plugins"`                                |
| `commands`    | string | Conditional | `"./commands"` -- include only if the plugin provides commands.                    |
| `skills`      | string | Conditional | `"./skills"` -- include only if the plugin provides skills.                        |
| `version`     | string | Yes         | Semver version. See versioning rules below.                                        |

## Versioning Rules

- **New plugins**: start at `1.0.0`
- **New skills** (added to an existing plugin): bump the **minor** version (e.g., `1.0.0` -> `1.1.0`)
- **Skill updates** (changes to existing skills): bump the **patch** version (e.g., `1.1.0` -> `1.1.1`)
- The version in `plugin.json` and the corresponding entry in `marketplace.json` must stay in sync

## Skills Plugin Template

```json
{
  "author": {
    "name": "Christopher Boone"
  },
  "description": "DESCRIPTION",
  "homepage": "https://github.com/cboone/agent-harness-plugins",
  "keywords": ["KEYWORD1", "KEYWORD2"],
  "license": "MIT",
  "name": "PLUGIN-NAME",
  "repository": "https://github.com/cboone/agent-harness-plugins",
  "skills": "./skills",
  "version": "1.0.0"
}
```

## Hooks Plugin Template

Hooks plugins omit the `skills` field. They do not declare hooks in `plugin.json`; hooks are defined in a separate `hooks/hooks.json` file.

```json
{
  "author": {
    "name": "Christopher Boone"
  },
  "description": "DESCRIPTION",
  "homepage": "https://github.com/cboone/agent-harness-plugins",
  "keywords": ["KEYWORD1", "KEYWORD2"],
  "license": "MIT",
  "name": "PLUGIN-NAME",
  "repository": "https://github.com/cboone/agent-harness-plugins",
  "version": "1.0.0"
}
```

## Command Plugin Template

Command plugins use a `commands` field instead of `skills`. They do not declare commands in `plugin.json`; commands are defined as individual `.md` files in the `commands/` directory.

```json
{
  "author": {
    "name": "Christopher Boone"
  },
  "commands": "./commands",
  "description": "DESCRIPTION",
  "homepage": "https://github.com/cboone/agent-harness-plugins",
  "keywords": ["KEYWORD1", "KEYWORD2"],
  "license": "MIT",
  "name": "PLUGIN-NAME",
  "repository": "https://github.com/cboone/agent-harness-plugins",
  "version": "1.0.0"
}
```

## Notes

- The `name` field must exactly match the plugin's directory name under `plugins/`.
- Keywords should be lowercase, alphabetized, and relevant to the plugin's purpose.
- The `description` should match between `plugin.json` and the corresponding `marketplace.json` entry.
- A plugin can include both `"commands"` and `"skills"` fields if it provides both types.
