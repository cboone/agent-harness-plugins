---
description: Set up secret scanning with gitleaks and TruffleHog GitHub Actions workflows and optional gitleaks configuration.
disable-model-invocation: true
---

# Setup Secret Scanning

Set up secret scanning in a repository with [gitleaks](https://github.com/gitleaks/gitleaks) and [TruffleHog](https://github.com/trufflesecurity/trufflehog) GitHub Actions workflows and optional `.gitleaks.toml` configuration.

The two tools are complementary:

- **Gitleaks** performs fast pattern matching on every push and PR, plus a daily scheduled scan.
- **TruffleHog** performs deeper verification-based scanning on pushes to main, with a weekly scheduled scan.

## Workflow

### 1. Check for Existing Setup

Look for existing secret scanning workflows and configuration:

```bash
ls .github/workflows/gitleaks.yml
ls .github/workflows/gitleaks.yaml
ls .github/workflows/trufflehog.yml
ls .github/workflows/trufflehog.yaml
```

Also check for an existing `.gitleaks.toml`:

```bash
ls .gitleaks.toml
```

If any workflows already exist, inform the user and ask whether to overwrite each one or skip it.

### 2. Choose Scanning Tools

Ask the user which tools to set up:

- **Both gitleaks and TruffleHog** (recommended): complementary coverage with fast pattern matching and deep verification
- **Gitleaks only**: fast pattern matching on every push and PR
- **TruffleHog only**: verification-based scanning on pushes to main

### 3. Determine Repository Ownership (Gitleaks Only)

If gitleaks was selected, ask the user whether this is a personal or organization-owned repository:

- **Personal**: no gitleaks license needed. The action works out of the box.
- **Organization**: requires a `GITLEAKS_LICENSE` repository secret. Free licenses are available at [gitleaks.io](https://gitleaks.io).

Skip this step if only TruffleHog was selected.

### 4. Generate Gitleaks Workflow

If gitleaks was selected, create `.github/workflows/gitleaks.yml` using the appropriate workflow template below:

- Use the **Personal Repository** template if the repo is personally owned.
- Use the **Organization Repository** template if the repo is organization-owned (includes the `GITLEAKS_LICENSE` env var).

Write the file using the Write tool. The `.github/workflows/` directory will be created automatically if it does not exist.

### 5. Generate TruffleHog Workflow

If TruffleHog was selected, create `.github/workflows/trufflehog.yml` using the TruffleHog workflow template below.

Write the file using the Write tool.

### 6. Optionally Generate Gitleaks Configuration

If gitleaks was selected, ask the user whether they want a `.gitleaks.toml` configuration file.

If yes, create `.gitleaks.toml` in the repository root using the configuration template below. Adapt the allowlist paths to the project:

- **Go projects** (have `go.mod`): include `go.sum`
- **JavaScript projects** (have `package.json`): include `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- **Ruby projects** (have `Gemfile`): include `Gemfile.lock`
- Remove lockfile entries that do not apply to the project.

If no, skip this step.

### 7. Summary

Print a summary of what was created:

- List every file generated
- For gitleaks: note that it runs on pushes, pull requests, and daily at 4 AM UTC
- For TruffleHog: note that it runs on pushes to main and weekly on Saturdays at 4 AM UTC
- If the repository is organization-owned and gitleaks was selected, remind the user to add the `GITLEAKS_LICENSE` secret in Settings > Secrets and variables > Actions
- Mention that gitleaks will automatically comment on PRs when secrets are detected

## Error Handling

- If any workflow file already exists, ask before overwriting
- If the user is unsure about personal vs. organization ownership, suggest checking the repository URL: `github.com/USERNAME/repo` is personal, `github.com/ORG-NAME/repo` is an organization
- If `.github/workflows/` cannot be created, check that the current directory is a git repository root

---

## Reference: Gitleaks GitHub Actions Workflow Templates

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
    permissions:
      contents: read
      pull-requests: read
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
    permissions:
      contents: read
      pull-requests: read
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
```

### Gitleaks Workflow Notes

- `fetch-depth: 0` clones the full git history so gitleaks can scan all commits, not just the latest.
- The `schedule` trigger runs a daily scan at 4 AM UTC to catch secrets introduced outside of PR workflows (e.g., direct pushes).
- `workflow_dispatch` allows manual triggering from the GitHub Actions UI.
- `GITHUB_TOKEN` is automatically provided by GitHub and enables PR comments when secrets are detected.
- `GITLEAKS_LICENSE` is required for organization-owned repositories. Free licenses are available at [gitleaks.io](https://gitleaks.io). Personal account repositories do not need a license.
- `permissions` grants `contents: read` for repository access and `pull-requests: read` for PR context. Without explicit permissions, repos with restricted default permissions will get 403 errors.

---

## Reference: TruffleHog GitHub Actions Workflow Template

A single template that works for all repository types (no license distinction).

### Template

```yaml
name: trufflehog

on:
  push:
    branches: [main]
  workflow_dispatch:
  schedule:
    - cron: "0 4 * * 6"

jobs:
  scan:
    name: trufflehog
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: trufflesecurity/trufflehog@v3
        with:
          extra_args: --results=verified,unknown
```

### TruffleHog Workflow Notes

- `trufflesecurity/trufflehog@v3` is the stable major version tag from the official TruffleHog GitHub Action.
- `--results=verified,unknown` reports confirmed-active and unknown-status secrets while filtering out confirmed false positives.
- `fetch-depth: 0` clones the full git history for thorough scanning.
- The `schedule` trigger runs a weekly scan on Saturdays at 4 AM UTC, complementing gitleaks' daily scans.
- `workflow_dispatch` allows manual triggering from the GitHub Actions UI.
- Runs on pushes to `main` only (post-merge), since gitleaks already covers per-push and per-PR pattern matching.
- No `.trufflehog.yml` config file is needed; all configuration is passed via `extra_args`.

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
