# Handle Secrets

Best practices for handling user-provided secrets in CLI tools: secure input methods, credential storage, secret masking, and language-specific libraries.

**Type:** Skill
**Trigger:** `/handle-secrets`

## What It Does

Provides a security hierarchy of input methods (OS keychain, stdin, TTY prompts, config files, environment variables) ranked from safest to most dangerous, with design patterns for credential fallback chains, secret masking, and language-specific libraries for Rust, Go, Python, Node.js, and Ruby.

## Usage

```text
/handle-secrets
```

## Examples

- "handle secrets" — loads the full security hierarchy and checklist
- "review this CLI's secret handling" — audits existing code against best practices
- "how should I accept an API key from users?" — recommends the safest input method

## See Also

- [Setup Gitleaks](../setup-gitleaks/README.md) — secret scanning for repositories
- [All plugins](../../README.md)
