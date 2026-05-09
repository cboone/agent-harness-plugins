# Handle Secrets

Best practices for handling user-provided secrets in CLI tools.

**Type:** Skill
**Trigger:** `/handle-secrets`

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Provides security best practices for accepting secrets (API keys, tokens, passwords) from users in CLI tools. Covers the security hierarchy of input methods, credential storage patterns with OS keychains and config files, secret masking in output, and language-specific libraries for Rust, Go, Python, Node.js, and Ruby.

Organized into a quick-review checklist and deep-dive references by topic.

## Usage

```text
/handle-secrets
```

The skill also activates automatically when Claude Code detects work involving user-provided secrets in CLI tools.

## Examples

- Building a CLI that accepts an API key: the skill provides the secure input hierarchy
- "review this code for secret handling": checks against the security checklist
- "/handle-secrets": loads the full best practices guide explicitly

## See Also

- [Write Go Code](../write-go-code/README.md): Go-specific libraries for credential handling
- [Set-Up Secret Scanning](../set-up-secret-scanning/README.md): prevent secrets from being committed to repositories
- [All plugins](../../README.md)
