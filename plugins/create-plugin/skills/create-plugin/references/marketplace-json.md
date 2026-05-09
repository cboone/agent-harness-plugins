# marketplace.json Reference

The root `.claude-plugin/marketplace.json` is the canonical plugin registry for this repository. It lists all available plugins so Claude Code can discover and install them, and it is the source for the generated Codex marketplace.

## File Location

```text
.claude-plugin/marketplace.json
```

Codex uses the generated file at `.agents/plugins/marketplace.json`, which points at generated plugin roots under `dist/codex/plugins/`. Do not edit the generated Codex marketplace or generated plugin roots directly. Update the canonical plugin files, then run:

```bash
bin/build-codex-marketplace
```

## Top-Level Structure

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "metadata": {
    "description": "Claude Code skills and hooks from Christopher Boone (cboone.github.io)",
    "version": "catalog-M55-m101-p44-n49"
  },
  "name": "agent-harness-plugins",
  "owner": {
    "name": "Christopher Boone"
  },
  "plugins": [...]
}
```

The generated Codex marketplace keeps the same plugin set, versions, and catalog metadata, but each entry's `source` points at `./dist/codex/plugins/PLUGIN-NAME`.

## Marketplace Versioning

The `metadata.version` stores a catalog state tag derived from the individual plugin versions. It is not SemVer.

- Format: `catalog-M<major-sum>-m<minor-sum>-p<patch-sum>-n<plugin-count>`
- `M`: sum of all plugin major versions
- `m`: sum of all plugin minor versions
- `p`: sum of all plugin patch versions
- `n`: number of marketplace plugins
- Do not normalize or carry between components.
- Recompute it from `.plugins[].version` whenever any marketplace plugin version changes.

## Plugin Entry Fields

Each entry in the `plugins` array has these fields, alphabetized:

| Field         | Type   | Description                                                            |
| ------------- | ------ | ---------------------------------------------------------------------- |
| `author`      | object | `{ "name": "Christopher Boone" }`                                      |
| `category`    | string | One of the valid categories listed below.                              |
| `description` | string | One-sentence summary. Must match `plugin.json`.                        |
| `homepage`    | string | `"https://github.com/cboone/agent-harness-plugins"`                    |
| `keywords`    | array  | Must match `plugin.json`.                                              |
| `license`     | string | `"MIT"`                                                                |
| `name`        | string | Plugin name. Must match `plugin.json`.                                 |
| `repository`  | string | `"https://github.com/cboone/agent-harness-plugins"`                    |
| `source`      | string | Relative path to the plugin directory (e.g., `"./plugins/my-plugin"`). |
| `version`     | string | Must match `plugin.json`.                                              |

## Valid Categories

Categories currently used in this repository. Each marketplace category corresponds to a category table in the root `README.md`:

- `"agents"` -- meta-tools for the agent ecosystem (e.g., `clean-up-agent-config`, `create-plugin`)
- `"ci-and-release"` -- CI workflows, installers, release automation, repo audits (e.g., `set-up-ci`, `add-goreleaser-homebrew`, `set-up-secret-scanning`)
- `"code-quality"` -- style guides for code, linting, formatting, language-specific testing (e.g., `lint-and-fix`, `write-go-code`)
- `"code-review"` -- responding to external review feedback (e.g., `address-review`, `resolve-copilot-pr-feedback`)
- `"git"` -- the commit-to-PR pipeline (e.g., `commit`, `pr`, `merge-main`, `release`, `review-branch`, `use-git`)
- `"issues-and-worktrees"` -- issue management and multi-agent worktree workflows (e.g., `create-issue`, `create-worktree`, `suggest-next-issue`)
- `"scaffolding"` -- project and repository scaffolding (e.g., `scaffold-go-cli`, `scaffold-new-repo`, `bootstrap-project`, `refresh-project-scaffolding`)
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
  "homepage": "https://github.com/cboone/agent-harness-plugins",
  "keywords": ["KEYWORD1", "KEYWORD2"],
  "license": "MIT",
  "name": "PLUGIN-NAME",
  "repository": "https://github.com/cboone/agent-harness-plugins",
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
- Generated Codex skill descriptions come from each plugin's concise marketplace `description`; the richer canonical `SKILL.md` descriptions remain unchanged for Claude Code.
