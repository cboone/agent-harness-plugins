# Design Patterns for Secure Secret Handling

Patterns that push users toward security by making the secure path the default.

## The credential resolution fallback chain

The core design pattern for CLI tools. Resolve credentials in this order:

1. **Environment variable** (serves CI/CD — systems like GitHub Actions and Kubernetes inject secrets this way)
1. **Credential helper / OS keychain** (serves interactive users with persistent, encrypted storage)
1. **Config file** with 0600 permissions (fallback when keychains are unavailable)
1. **Interactive TTY prompt** (safest default for humans — echo-suppressed, never stored)

Never fall through to accepting `--password <value>` as a command-line argument.

## OAuth Device Authorization Grant (RFC 8628)

The modern standard for CLI login flows that eliminates password handling entirely:

1. The CLI displays a URL and a one-time code
1. The user authenticates in their browser
1. The CLI receives tokens without ever handling a password
1. Tokens are stored in the OS keychain with automatic refresh

### Adopters

GitHub CLI, Stripe CLI, Docker Hub, and Cloudflare Wrangler all use this pattern.

## Token hygiene

### Prefer short-lived, scoped tokens

Stripe CLI exemplifies this: `stripe login` generates a **restricted API key** (not the full secret key) valid for only **90 days** with limited permissions. This follows the principle of least privilege.

### Automatic refresh

When tokens have an expiration, the CLI should:

1. Check expiry before each request
1. Refresh automatically using a refresh token
1. Store the refreshed token back to the credential store
1. Prompt for re-authentication only when refresh fails

## Warn loudly about insecure behavior

### Warn on insecure argument usage

Docker's example:

```text
WARNING! Using --password via the CLI is insecure. Use --password-stdin.
```

### Refuse insecure file permissions

SSH's example:

```text
Permissions 0644 for '/home/user/.ssh/id_rsa' are too open.
It is required that your private key files are NOT accessible by others.
```

### Warn on plaintext fallback

GitHub CLI uses `--insecure-storage` to explicitly opt into plaintext storage, making the insecure choice a deliberate act rather than a silent default.

## Mask secrets in all output channels

Register every secret value with a masking function and apply it to:

- Debug logs
- Error messages
- HTTP request/response logs
- Verbose output
- Confirmation messages

### Type-level enforcement

Rust's `secrecy` crate prints `[[REDACTED]]` via `Debug` and `Display`, making accidental leakage a **compile-time error** rather than a runtime bug.

### 1Password CLI's approach

`op run` wraps a subprocess with secrets injected as environment variables and **automatically masks any secret values** that appear in stdout/stderr.

## Config file architecture

### Separate config from credentials

| File                               | Contains                           | Version-controllable |
| ---------------------------------- | ---------------------------------- | -------------------- |
| `~/.config/<app>/config`           | Region, output format, preferences | Yes                  |
| `~/.local/share/<app>/credentials` | API keys, tokens, passwords        | **No**               |

### Atomic file creation with correct permissions

```python
# Correct: permissions set at creation time
fd = os.open(cred_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, 'w') as f:
    f.write(credentials)
```

```go
// Correct: permissions set at creation time
f, err := os.OpenFile(credPath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0o600)
```

```rust
// Correct: permissions set at creation time
use std::os::unix::fs::OpenOptionsExt;
let f = std::fs::OpenOptions::new()
    .write(true)
    .create(true)
    .truncate(true)
    .mode(0o600)
    .open(cred_path)?;
```

**Never** use create-then-chmod:

```python
# WRONG: race condition — file briefly has default permissions
with open(cred_path, 'w') as f:
    f.write(credentials)
os.chmod(cred_path, 0o600)
```

### Encrypted config files

SOPS (a CNCF project) encrypts only values while preserving structure, supporting AWS KMS, GCP KMS, Azure Key Vault, and age encryption. This enables version-controlling encrypted secrets with meaningful diffs.

## Credential cleanup on logout

A `logout` command should:

1. **Revoke** the token server-side (if supported)
1. **Delete** stored credentials from keychain and config files
1. **Zero** any in-memory copies
1. Confirm to the user what was cleaned up
