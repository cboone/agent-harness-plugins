---
name: setup-secret-scanning
description: >-
  Set up secret scanning with gitleaks and TruffleHog GitHub Actions workflows
  and optional gitleaks configuration. Use when the user says "add secret
  scanning", "set up secret scanning", "set up gitleaks", "set up trufflehog",
  "scan for secrets in CI", or wants to detect leaked credentials in a
  repository. Both tools run on pushes to `main`, on pull requests, and on
  `workflow_dispatch`; gitleaks does fast pattern matching, TruffleHog adds
  verification-based scanning. Pairs with handle-secrets for
  application-level secret hygiene.
---

# Setup Secret Scanning

Set up secret scanning in a repository with [gitleaks](https://github.com/gitleaks/gitleaks) and [TruffleHog](https://github.com/trufflesecurity/trufflehog) GitHub Actions workflows and optional `.gitleaks.toml` configuration.

The two tools are complementary:

- **Gitleaks** performs fast pattern matching.
- **TruffleHog** performs deeper verification-based scanning that confirms whether detected credentials are still live.

Both run on pushes to `main`, on every pull request, and on manual `workflow_dispatch`.

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

If the user specified a tool selection in their request (`gitleaks`, `trufflehog`, or `both`), use it directly instead of asking.

Ask the user which tools to set up:

- **Both gitleaks and TruffleHog** (recommended): complementary coverage with fast pattern matching and deep verification
- **Gitleaks only**: fast pattern matching on every push and PR
- **TruffleHog only**: verification-based scanning on pushes to main

### 3. Generate Gitleaks Workflow

If gitleaks was selected, read `./references/gitleaks-workflow.md` for the workflow template and create `.github/workflows/gitleaks.yml` from it.

Write the file using the Write tool. The `.github/workflows/` directory will be created automatically if it does not exist.

### 4. Generate TruffleHog Workflow

If TruffleHog was selected, read `./references/trufflehog-workflow.md` for the workflow template and create `.github/workflows/trufflehog.yml` from it.

Write the file using the Write tool.

### 5. Optionally Generate Gitleaks Configuration

If gitleaks was selected, ask the user whether they want a `.gitleaks.toml` configuration file.

If yes, read `./references/gitleaks-config.md` for the configuration template and create `.gitleaks.toml` in the repository root from it. Adapt the allowlist paths to the project:

- **Go projects** (have `go.mod`): include `go.sum`
- **JavaScript projects** (have `package.json`): include `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- **Ruby projects** (have `Gemfile`): include `Gemfile.lock`
- Remove lockfile entries that do not apply to the project.

If no, skip this step.

### 6. Summary

Print a summary of what was created:

- List every file generated
- Note that both workflows run on pushes to `main`, pull requests, and `workflow_dispatch`
- Mention that gitleaks will automatically comment on PRs when secrets are detected

## Error Handling

- If any workflow file already exists, ask before overwriting
- If `.github/workflows/` cannot be created, check that the current directory is a git repository root

## Reference Templates

- `./references/gitleaks-workflow.md` -- gitleaks GitHub Actions workflow
- `./references/trufflehog-workflow.md` -- TruffleHog GitHub Actions workflow
- `./references/gitleaks-config.md` -- `.gitleaks.toml` configuration
