---
name: handle-secrets
description: >-
  Best practices for handling user-provided secrets in CLI tools. Use when:
  (1) building CLI tools that accept API keys, tokens, or passwords from users,
  (2) reviewing secret-handling code for security issues,
  (3) choosing between input methods (env vars, stdin, keychains, config files),
  (4) implementing credential storage or retrieval.
  Covers the security hierarchy of input methods, credential storage patterns,
  secret masking, and language-specific libraries.
---

# Handle Secrets

Best practices for handling secrets that **users pass to your CLI tool** (API keys, tokens, passwords), not secrets used during development.

## Core Principles

1. **Never accept secrets as command-line arguments** - Arguments are visible via `ps aux`, recorded in shell history, and captured by audit logs
2. **Make the secure path the default** - Users who do nothing special should get the safest behavior
3. **Separate config from credentials** - Non-sensitive settings and secret material belong in different files
4. **Mask secrets in all output** - Debug logs, error messages, HTTP traces, and verbose output must redact secret values
5. **Warn loudly about insecure behavior** - If users opt into something dangerous, tell them explicitly

## Security Hierarchy (Safest to Most Dangerous)

| Method | Safety | Use when |
|--------|--------|----------|
| OS keychain / credential helper | Safest | Persistent storage for interactive users |
| Secret references (`op://`, vault URIs) | Safe | Storing pointers instead of secrets |
| Stdin / pipes / file descriptors | Safe | Automation and scripting |
| Interactive TTY prompt | Safe | Human users at a terminal |
| Config files (0600 permissions) | Acceptable | Persistent storage without keychain |
| Environment variables | Acceptable | CI/CD pipelines and containers |
| Command-line arguments | **Never** | - |

## Workflow

1. **Quick reviews:** Check against `references/checklist.md`
2. **Choosing an input method:** Read `references/security-hierarchy.md`
3. **Designing credential flows:** Read `references/design-patterns.md`
4. **Avoiding known pitfalls:** Read `references/anti-patterns.md`
5. **Language-specific code:** Read `references/language-libraries.md`

## Reference Navigation

**Quick reviews (default):**
- `references/checklist.md` - Condensed, actionable rules

**Deep dives by topic:**
- `references/security-hierarchy.md` - Ranked input methods with attack surfaces and mitigations
- `references/design-patterns.md` - Credential fallback chains, OAuth device flow, token hygiene, masking
- `references/anti-patterns.md` - Real CVEs and incidents from insecure secret handling
- `references/language-libraries.md` - Rust, Go, Python, Node.js, Ruby libraries and code patterns

## Credential Resolution Fallback Chain

Tools should resolve credentials in this order:

1. Environment variable (for CI/CD)
2. Credential helper / OS keychain (for persistent storage)
3. Config file with 0600 permissions (fallback)
4. Interactive TTY prompt (for humans)

Never fall through to accepting `--password <value>` as an argument.

## Sources

- [Building CLI tools that handle user secrets responsibly](https://www.macchaffee.com/blog/2025/cli-secret-handling/) - Mac Chaffee
- GitHub CLI, Docker, AWS CLI, kubectl, and 1Password CLI implementations
