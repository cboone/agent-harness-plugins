---
name: setup-gitleaks
description: >-
  Set up gitleaks secret scanning with a GitHub Actions workflow and optional
  configuration. Use when the user says "set up gitleaks", "add gitleaks",
  "add secret scanning", "set up secret scanning", "gitleaks scanning",
  "setup gitleaks", or asks to add secret detection to a repository's CI
  pipeline.
---

# Setup Gitleaks

Set up [gitleaks](https://github.com/gitleaks/gitleaks) secret scanning in a repository with a GitHub Actions workflow and optional `.gitleaks.toml` configuration.

## Workflow

### 1. Check for Existing Setup

Look for an existing gitleaks workflow:

```bash
ls .github/workflows/gitleaks.yml

ls .github/workflows/gitleaks.yaml
```

If a gitleaks workflow already exists, inform the user and ask whether to overwrite it or abort. Also check for an existing `.gitleaks.toml`:

```bash
ls .gitleaks.toml
```

### 2. Determine Repository Ownership

Ask the user whether this is a personal or organization-owned repository:

- **Personal** -- no gitleaks license needed. The action works out of the box.
- **Organization** -- requires a `GITLEAKS_LICENSE` repository secret. Free licenses are available at [gitleaks.io](https://gitleaks.io).

### 3. Generate the Workflow

Create `.github/workflows/gitleaks.yml` using the appropriate template from `./references/workflow.md`:

- Use the **Personal Repository** template if the repo is personally owned.
- Use the **Organization Repository** template if the repo is organization-owned (includes the `GITLEAKS_LICENSE` env var).

Write the file using the Write tool. The `.github/workflows/` directory will be created automatically if it does not exist.

### 4. Optionally Generate Configuration

Ask the user whether they want a `.gitleaks.toml` configuration file.

If yes, create `.gitleaks.toml` in the repository root using the template from `./references/config.md`. Adapt the allowlist paths to the project:

- **Go projects** (have `go.mod`): include `go.sum`
- **JavaScript projects** (have `package.json`): include `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- **Ruby projects** (have `Gemfile`): include `Gemfile.lock`
- Remove lockfile entries that do not apply to the project.

If no, skip this step.

### 5. Summary

Print a summary of what was created:

- List every file generated
- If the repository is organization-owned, remind the user to add the `GITLEAKS_LICENSE` secret in Settings > Secrets and variables > Actions
- Note that the workflow runs on pushes, pull requests, and daily at 4 AM UTC
- Mention that gitleaks will automatically comment on PRs when secrets are detected

## Error Handling

- If `.github/workflows/gitleaks.yml` already exists, ask before overwriting
- If the user is unsure about personal vs. organization ownership, suggest checking the repository URL: `github.com/USERNAME/repo` is personal, `github.com/ORG-NAME/repo` is an organization
- If `.github/workflows/` cannot be created, check that the current directory is a git repository root
