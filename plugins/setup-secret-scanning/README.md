# Setup Gitleaks

Set up gitleaks secret scanning in a repository with a GitHub Actions workflow and optional configuration.

**Type:** Skill
**Trigger:** `/setup-gitleaks`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Setup Gitleaks** from the available plugins.

## What It Does

Detects whether the repository is organization-owned (requires a gitleaks license secret) or personal, and generates the appropriate GitHub Actions workflow. Optionally creates a starter `.gitleaks.toml` with sensible defaults and example allowlist entries.

## Usage

```text
/setup-gitleaks
```

## Examples

- "set up gitleaks": generates the workflow and optional config
- "add secret scanning": same behavior
- "setup gitleaks": same behavior

## See Also

- [Scaffold New Repo](../scaffold-new-repo/README.md): scaffold a full repo (then add gitleaks)
- [All plugins](../../README.md)
