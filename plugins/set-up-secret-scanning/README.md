# Set-Up Secret Scanning

Set up secret scanning in a repository with gitleaks and TruffleHog GitHub Actions workflows and optional gitleaks configuration.

**Type:** Skill
**Trigger:** `/set-up-secret-scanning`

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Sets up complementary secret scanning with two tools: gitleaks for fast pattern matching, and TruffleHog for deeper verification-based scanning that confirms whether detected credentials are still live. Both run on pushes to `main`, on every pull request, and on manual `workflow_dispatch`. Lets you choose both tools (recommended), gitleaks only, or TruffleHog only. For gitleaks, optionally creates a starter `.gitleaks.toml`.

## Usage

```text
/set-up-secret-scanning
```

## Examples

- "set up secret scanning": generates workflow(s) and optional config
- "add secret scanning": same behavior
- "set up gitleaks and TruffleHog": same behavior
- "add trufflehog": same behavior

## See Also

- [Scaffold New Repo](../scaffold-new-repo/README.md): scaffold a full repo (then add secret scanning)
- [Handle Secrets](../handle-secrets/README.md): best practices for handling secrets in CLI tools
- [All plugins](../../README.md)
