---
description: Set up secret scanning with gitleaks and TruffleHog GitHub Actions workflows and optional gitleaks configuration.
disable-model-invocation: true
argument-hint: "[gitleaks|trufflehog|both]"
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

If `$ARGUMENTS` specifies a tool selection (`gitleaks`, `trufflehog`, or `both`), use it directly instead of asking the user.

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

## Reference Templates

@${CLAUDE_PLUGIN_ROOT}/references/gitleaks-workflow.md

@${CLAUDE_PLUGIN_ROOT}/references/trufflehog-workflow.md

@${CLAUDE_PLUGIN_ROOT}/references/gitleaks-config.md
