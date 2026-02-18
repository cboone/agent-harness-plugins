# Add setup-gitleaks Skill

## Context

This repository needs a skill that sets up [gitleaks](https://github.com/gitleaks/gitleaks) secret scanning in a target repository. Gitleaks is the most widely adopted open-source secret scanner (19k+ GitHub stars, 20M+ Docker downloads). The skill will generate a GitHub Actions workflow file and optionally a `.gitleaks.toml` configuration file, making it trivial to add secret scanning to any repo.

## Files to Create

### 1. `plugins/setup-gitleaks/.claude-plugin/plugin.json`

Standard plugin manifest:

```json
{
  "author": {
    "name": "Christopher Boone"
  },
  "description": "Set up gitleaks secret scanning with a GitHub Actions workflow and optional configuration.",
  "homepage": "https://github.com/cboone/cboone-cc-plugins",
  "keywords": ["gitleaks", "github-actions", "scanning", "secrets", "security"],
  "license": "MIT",
  "name": "setup-gitleaks",
  "repository": "https://github.com/cboone/cboone-cc-plugins",
  "skills": "./skills",
  "version": "1.0.0"
}
```

### 2. `plugins/setup-gitleaks/skills/setup-gitleaks/SKILL.md`

The skill workflow:

1. **Check prerequisites** -- Verify the repo has a `.github/` directory (or create it). Check if a gitleaks workflow already exists.
1. **Ask about license** -- Gitleaks Action v2 requires a `GITLEAKS_LICENSE` secret for organization-owned repos. Ask the user whether this is an org repo (needs license) or personal (no license needed).
1. **Generate the workflow** -- Write `.github/workflows/gitleaks.yml` using the template from `./references/workflow.md`. Adjust based on whether a license is needed.
1. **Optionally generate config** -- Ask if the user wants a `.gitleaks.toml`. If yes, write it using the template from `./references/config.md`.
1. **Summary** -- Print what was created and next steps (e.g., adding the `GITLEAKS_LICENSE` secret if needed).

Trigger phrases: "set up gitleaks", "add gitleaks", "add secret scanning", "set up secret scanning", "gitleaks scanning", "setup gitleaks".

### 3. `plugins/setup-gitleaks/skills/setup-gitleaks/references/workflow.md`

Two workflow templates:

- **Personal repo** (no license needed) -- simpler version without `GITLEAKS_LICENSE` env var
- **Organization repo** (license needed) -- includes `GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}`

Both templates include:

- Triggers: `push`, `pull_request`, `workflow_dispatch`, `schedule` (daily at 4 AM UTC)
- `actions/checkout@v4` with `fetch-depth: 0`
- `gitleaks/gitleaks-action@v2`
- `GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}`

### 4. `plugins/setup-gitleaks/skills/setup-gitleaks/references/config.md`

A starter `.gitleaks.toml` template with:

- `[extend]` section using default rules
- Example custom `[[rules]]` (commented out)
- Example `[allowlist]` for common false positives (paths like `go.sum`, `package-lock.json`, test fixtures)
- Notes on how to customize

## Files to Modify

### 5. `.claude-plugin/marketplace.json`

- Add a new entry for `setup-gitleaks` (alphabetically between `scaffold-new-repo` and `suggest-next-issue`)
- Category: `"code-quality"` (security scanning fits alongside the other code-quality plugins)
- Bump `metadata.version` from `1.7.0` to `1.8.0` (adding a plugin)

### 6. `README.md`

**ToC**: Add under Skills > Workflow (alphabetically between `Scaffold New Repo` and `Suggest Next Issue`):

```markdown
∙ [Setup Gitleaks](#setup-gitleaks)
```

**Description section**: Add between Scaffold New Repo and Suggest Next Issue:

```markdown
### Setup Gitleaks

Set up gitleaks secret scanning in a repository with a GitHub Actions workflow
and optional `.gitleaks.toml` configuration. Detects whether the repository is
organization-owned (requires a gitleaks license secret) or personal, and
generates the appropriate workflow. Optionally creates a starter `.gitleaks.toml`
with sensible defaults and example allowlist entries.

> **Trigger:** `/setup-gitleaks`
```

### 7. `CLAUDE.md`

Add `setup-gitleaks/` to the directory structure tree (alphabetically between `scaffold-new-repo/` and `suggest-next-issue/`).

## Verification

1. Validate JSON: Ensure `plugin.json` and updated `marketplace.json` are valid JSON
1. Version sync: Confirm `plugin.json` version (`1.0.0`) matches the marketplace entry
1. Marketplace version: Confirm `metadata.version` bumped to `1.8.0`
1. README ordering: Confirm ToC and description sections are alphabetically correct
1. CLAUDE.md structure: Confirm the new entry matches the existing directory tree format
1. Skill description: Confirm SKILL.md frontmatter `description` matches `plugin.json` and `marketplace.json` descriptions
