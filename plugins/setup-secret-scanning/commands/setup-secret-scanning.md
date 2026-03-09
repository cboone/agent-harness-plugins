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

### 3. Generate Gitleaks Workflow

If gitleaks was selected, create `.github/workflows/gitleaks.yml` using the gitleaks workflow template below.

Write the file using the Write tool. The `.github/workflows/` directory will be created automatically if it does not exist.

### 4. Generate TruffleHog Workflow

If TruffleHog was selected, create `.github/workflows/trufflehog.yml` using the TruffleHog workflow template below.

Write the file using the Write tool.

### 5. Optionally Generate Gitleaks Configuration

If gitleaks was selected, ask the user whether they want a `.gitleaks.toml` configuration file.

If yes, create `.gitleaks.toml` in the repository root using the configuration template below. Adapt the allowlist paths to the project:

- **Go projects** (have `go.mod`): include `go.sum`
- **JavaScript projects** (have `package.json`): include `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- **Ruby projects** (have `Gemfile`): include `Gemfile.lock`
- Remove lockfile entries that do not apply to the project.

If no, skip this step.

### 6. Summary

Print a summary of what was created:

- List every file generated
- For gitleaks: note that it runs on pushes, pull requests, and daily at 4 AM UTC
- For TruffleHog: note that it runs on pushes to main and weekly on Saturdays at 4 AM UTC
- Mention that gitleaks will automatically comment on PRs when secrets are detected

## Error Handling

- If any workflow file already exists, ask before overwriting
- If `.github/workflows/` cannot be created, check that the current directory is a git repository root

---

## Reference: Gitleaks GitHub Actions Workflow Template

A single template that works for all repository types. Uses the `cboone/gh-actions` reusable workflow, which runs the gitleaks CLI directly (no license required).

### Template

```yaml
name: gitleaks

on:
  push:
  pull_request:
  workflow_dispatch:
  schedule:
    - cron: "0 4 * * *"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  scan:
    uses: cboone/gh-actions/.github/workflows/secret-scan.yml@v1
    with:
      tool: gitleaks
```

### Gitleaks Workflow Notes

- The reusable workflow uses the gitleaks CLI directly, not `gitleaks/gitleaks-action`. The CLI works without a license for both personal and organization repositories.
- The `schedule` trigger runs a daily scan at 4 AM UTC to catch secrets introduced outside of PR workflows (e.g., direct pushes).
- `workflow_dispatch` allows manual triggering from the GitHub Actions UI.
- The reusable workflow handles checkout with `fetch-depth: 0`, permissions, and tool installation internally.

---

## Reference: TruffleHog GitHub Actions Workflow Template

A single template that works for all repository types. Uses the `cboone/gh-actions` reusable workflow.

### Template

```yaml
name: trufflehog

on:
  push:
    branches: [main]
  workflow_dispatch:
  schedule:
    - cron: "0 4 * * 6"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  scan:
    uses: cboone/gh-actions/.github/workflows/secret-scan.yml@v1
    with:
      tool: trufflehog
```

### TruffleHog Workflow Notes

- The reusable workflow handles TruffleHog version pinning, checkout with `fetch-depth: 0`, and configuration internally.
- The `schedule` trigger runs a weekly scan on Saturdays at 4 AM UTC, complementing gitleaks' daily scans.
- `workflow_dispatch` allows manual triggering from the GitHub Actions UI.
- Runs on pushes to `main` only (post-merge), since gitleaks already covers per-push and per-PR pattern matching.

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
