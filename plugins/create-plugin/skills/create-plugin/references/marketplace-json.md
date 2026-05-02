# marketplace.json Reference

The root `.claude-plugin/marketplace.json` is the plugin registry for this repository. It lists all available plugins so Claude Code can discover and install them.

## File Location

```text
.claude-plugin/marketplace.json
```

## Top-Level Structure

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "metadata": {
    "description": "Claude Code skills and hooks from Christopher Boone (cboone.github.io)",
    "version": "1.3.0"
  },
  "name": "cboone-cc-plugins",
  "owner": {
    "name": "Christopher Boone"
  },
  "plugins": [...]
}
```

## Marketplace Versioning

The `metadata.version` tracks changes to the plugin catalog itself — bump it when the set of plugins changes, not when individual plugin content changes.

- Bump **minor** when adding or removing a plugin (e.g., `1.3.0` -> `1.4.0`)
- Do NOT bump for changes to existing plugin content (those are tracked by each plugin's own version)

## Plugin Entry Fields

Each entry in the `plugins` array has these fields, alphabetized:

| Field         | Type   | Description                                                            |
| ------------- | ------ | ---------------------------------------------------------------------- |
| `author`      | object | `{ "name": "Christopher Boone" }`                                      |
| `category`    | string | One of the valid categories listed below.                              |
| `description` | string | One-sentence summary. Must match `plugin.json`.                        |
| `homepage`    | string | `"https://github.com/cboone/cboone-cc-plugins"`                        |
| `keywords`    | array  | Must match `plugin.json`.                                              |
| `license`     | string | `"MIT"`                                                                |
| `name`        | string | Plugin name. Must match `plugin.json`.                                 |
| `repository`  | string | `"https://github.com/cboone/cboone-cc-plugins"`                        |
| `source`      | string | Relative path to the plugin directory (e.g., `"./plugins/my-plugin"`). |
| `version`     | string | Must match `plugin.json`.                                              |

## Valid Categories

Categories currently used in this repository. Each marketplace category corresponds to a subcategory in the root `README.md` table of contents:

- `"agents"` -- meta-tools for the agent ecosystem (e.g., `clean-up-agent-config`, `create-plugin`)
- `"ci-and-release"` -- CI workflows, installers, release automation, repo audits (e.g., `setup-ci`, `add-goreleaser-homebrew`, `setup-secret-scanning`, `update-everything`)
- `"code-quality"` -- style guides for code, linting, formatting, language-specific testing (e.g., `lint-and-fix`, `write-go-code`)
- `"code-review"` -- responding to external review feedback (e.g., `address-review`, `resolve-copilot-pr-feedback`)
- `"git"` -- the commit-to-PR pipeline (e.g., `commit`, `pr`, `merge-main`, `release`, `review-branch`, `use-git`)
- `"issues-and-worktrees"` -- issue management and multi-agent worktree workflows (e.g., `create-issue`, `create-worktree`, `suggest-next-issue`)
- `"scaffolding"` -- project and repository scaffolding (e.g., `scaffold-go-cli`, `scaffold-new-repo`, `bootstrap-project`)
- `"workflow"` -- general workflow utility hooks (e.g., `notify`, `update-docs-reminder`)
- `"writing"` -- style and structure guides for prose and document artifacts (e.g., `write-markdown`, `write-pandoc-markdown`, `write-math`, `write-formalization-roadmap`)

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
