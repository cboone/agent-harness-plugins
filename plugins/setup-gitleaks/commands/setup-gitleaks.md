---
description: Set up gitleaks secret scanning with a GitHub Actions workflow and optional configuration.
disable-model-invocation: true
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

Create `.github/workflows/gitleaks.yml` using the appropriate workflow template below:

- Use the **Personal Repository** template if the repo is personally owned.
- Use the **Organization Repository** template if the repo is organization-owned (includes the `GITLEAKS_LICENSE` env var).

Write the file using the Write tool. The `.github/workflows/` directory will be created automatically if it does not exist.

### 4. Optionally Generate Configuration

Ask the user whether they want a `.gitleaks.toml` configuration file.

If yes, create `.gitleaks.toml` in the repository root using the configuration template below. Adapt the allowlist paths to the project:

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

---

## Reference: GitHub Actions Workflow Templates

Choose the template matching the repository ownership. Organization-owned repos require a gitleaks license; personal repos do not.

### Personal Repository

```yaml
name: gitleaks

on:
  push:
  pull_request:
  workflow_dispatch:
  schedule:
    - cron: "0 4 * * *"

jobs:
  scan:
    name: gitleaks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Organization Repository

```yaml
name: gitleaks

on:
  push:
  pull_request:
  workflow_dispatch:
  schedule:
    - cron: "0 4 * * *"

jobs:
  scan:
    name: gitleaks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
```

### Workflow Notes

- `fetch-depth: 0` clones the full git history so gitleaks can scan all commits, not just the latest.
- The `schedule` trigger runs a daily scan at 4 AM UTC to catch secrets introduced outside of PR workflows (e.g., direct pushes).
- `workflow_dispatch` allows manual triggering from the GitHub Actions UI.
- `GITHUB_TOKEN` is automatically provided by GitHub and enables PR comments when secrets are detected.
- `GITLEAKS_LICENSE` is required for organization-owned repositories. Free licenses are available at [gitleaks.io](https://gitleaks.io). Personal account repositories do not need a license.

---

## Reference: .gitleaks.toml Configuration Template

A starter configuration that extends the built-in rules and adds common allowlist entries.

### Template

```toml
[extend]
# Use the default gitleaks rules as a base.
useDefault = true

# Example: custom rule (uncomment and adapt as needed)
# [[rules]]
# id = "custom-api-key"
# description = "Custom API key pattern"
# regex = '''(?i)custom[_-]?api[_-]?key\s*[=:]\s*['"]?([a-zA-Z0-9]{32,})['"]?'''
# keywords = ["custom_api_key", "custom-api-key"]

[allowlist]
# Paths to exclude from scanning.
# Add lockfiles, vendored dependencies, and test fixtures that trigger false positives.
paths = [
  '''go\.sum''',
  '''package-lock\.json''',
  '''yarn\.lock''',
  '''pnpm-lock\.yaml''',
  '''Gemfile\.lock''',
  '''vendor/''',
]
```

### Customization Guide

#### Adding Custom Rules

Define rules to detect project-specific secret patterns:

```toml
[[rules]]
id = "rule-id"
description = "What this rule detects"
regex = '''pattern_here'''
keywords = ["keyword"]
```

The `keywords` field is a pre-filter: gitleaks only applies the regex to lines containing at least one keyword, which improves performance.

#### Expanding the Allowlist

Suppress false positives with additional allowlist entries:

- **paths**: File path patterns (regexes) to skip entirely
- **regexes**: Content patterns to ignore when matched
- **commits**: Specific commit SHAs to exclude (useful for known-rotated secrets in history)

```toml
[allowlist]
paths = [
  '''test/fixtures/''',
  '''\.md$''',
]
regexes = [
  '''EXAMPLE_KEY_PLACEHOLDER''',
]
commits = [
  "abc123def456",
]
```

#### Disabling Built-in Rules

If a default rule produces too many false positives, disable it by ID:

```toml
[extend]
useDefault = true
disabledRules = ["generic-api-key"]
```

Find built-in rule IDs in the [gitleaks default config](https://github.com/gitleaks/gitleaks/blob/master/config/gitleaks.toml).
