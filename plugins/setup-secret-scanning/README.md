# Setup Secret Scanning

Set up secret scanning in a repository with gitleaks and TruffleHog GitHub Actions workflows and optional gitleaks configuration.

**Type:** Command
**Trigger:** `/setup-secret-scanning`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Setup Secret Scanning** from the available plugins.

## What It Does

Sets up complementary secret scanning with two tools: gitleaks for fast pattern matching on every push and PR (with daily scheduled scans), and TruffleHog for deeper verification-based scanning on pushes to main (with weekly scheduled scans). Lets you choose both tools (recommended), gitleaks only, or TruffleHog only. For gitleaks, detects organization vs. personal repositories and optionally creates a starter `.gitleaks.toml`.

## Usage

```text
/setup-secret-scanning
```

## Examples

- "set up secret scanning": generates workflow(s) and optional config
- "add secret scanning": same behavior
- "setup gitleaks and trufflehog": same behavior
- "add trufflehog": same behavior

## See Also

- [Scaffold New Repo](../scaffold-new-repo/README.md): scaffold a full repo (then add secret scanning)
- [Handle Secrets](../handle-secrets/README.md): best practices for handling secrets in CLI tools
- [All plugins](../../README.md)
