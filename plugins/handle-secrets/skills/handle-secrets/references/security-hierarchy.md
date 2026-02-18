# Security Hierarchy for Accepting Secrets

Input methods ranked from most to least dangerous, with concrete technical reasons and mitigations.

## Command-line arguments: never do this

Arguments passed to a process are visible to **every user on the system** through three distinct attack surfaces:

1. **`ps aux`** reads from `/proc/<pid>/cmdline`, which is **world-readable** regardless of file permissions
2. **Shell history** records commands to persistent files (`~/.bash_history`, `~/.zsh_history`)
3. **Audit logs** and monitoring tools often capture full command lines

### Real CVEs

- **CVE-2022-45868** (H2 Database): Accepted `-webAdminPassword` as a CLI argument. The vendor's response: *"Passwords should never be passed on the command line and every qualified DBA or system administrator is expected to know that."*
- **CVE-2006-5659** (PAM_extern): Sent passwords as CLI arguments, letting local users harvest them via `ps`
- **FreeRDP Issue #3639**: Accepted `/p:<password>`, then attempted to overwrite it with asterisks in `argv`, but a race condition left the password visible

### The argv overwrite fallacy

Some tools (`curl`, `mysql`) overwrite `argv` in memory after reading secrets. This is fundamentally flawed:

- There is always a **race condition window** between process creation and the overwrite
- The password **length** remains discoverable
- It creates a false sense of security

## Environment variables: acceptable with caveats

Environment variables are significantly safer than CLI arguments:

- `/proc/<pid>/environ` is readable **only by the process owner** (unlike world-readable `/proc/<pid>/cmdline`)
- They don't appear in `ps aux` output
- They aren't recorded in shell history (when set in a parent process)

### Risks

- **Child process inheritance**: All exported environment variables propagate to subprocesses
- **Container inspection**: `docker inspect` exposes all environment variables
- **Core dumps**: Can contain environment data
- **Shell expansion trap**: Expanding secrets via `$VAR` into command arguments (e.g., `curl -H "Authorization: Bearer $TOKEN"`) puts the value into the process's argv, visible via `ps`. Have the tool read the environment variable internally instead

### Best practice

Parse environment variables once at startup, then remove them from the process environment to prevent further leakage. Environment variables are the right choice for CI/CD pipelines and container orchestration.

## Config files with strict permissions

Storing credentials in files works when permissions are correct.

### Critical rules

- **Create credential files with 0600 permissions from the start** using atomic file creation (e.g., `os.open()` with explicit mode bits)
- **Never create-then-chmod** — this introduces a race condition where the file briefly has insecure permissions
- **Refuse to use files with insecure permissions** (SSH's model: *"Permissions 0644 for '/home/user/.ssh/id_rsa' are too open."*)

### Separate config from credentials

Follow the AWS CLI pattern:

- `~/.aws/config` for non-sensitive settings (region, output format) — safe to version-control
- `~/.aws/credentials` for access keys — never shared

### XDG Base Directory conventions

- Non-secret config: `$XDG_CONFIG_HOME/<app>/` (`~/.config/<app>/`)
- Credentials: `$XDG_DATA_HOME/<app>/` (`~/.local/share/<app>/`) with 0600 permissions
- Ephemeral session tokens: `$XDG_RUNTIME_DIR/<app>/` (mode 0700, not surviving reboot, never swapped to disk)

## Stdin, pipes, and file descriptors: the secure choice for automation

Pipe contents exist only in kernel memory, have exactly two endpoints, and never appear in process listings or shell history.

### Patterns

**`--password-file` pattern:**

```bash
# Process substitution: secret never touches disk or process listing
step-ca --password-file <(echo -n "$STEP_CA_PASSWORD") config.json

# Pipe from a password manager
op read "op://vault/item/field" | mytool --password-file /dev/stdin
```

**`--password-fd` pattern** (pioneered by GnuPG):

```bash
gpg --passphrase-fd 3 3< passphrase-file --decrypt file.gpg
```

**Interactive prompts** with echo suppression:

```python
if sys.stdin.isatty():
    password = getpass.getpass("Password: ")   # Echo suppressed
else:
    password = sys.stdin.readline().rstrip()    # Read from pipe
```

## Secret references and vault URIs: the modern approach

Store **pointers** to secrets, not secrets themselves.

- **1Password**: `op://vault-name/item-name/[section-name/]field-name`
- **HashiCorp Vault**: `vault kv get -field=password secret/myapp/db`
- **AWS Secrets Manager**: ARN-based references

These references are safe to commit to version control because they contain zero secret material.

### Resolution commands

- `op read` outputs a single secret to stdout
- `op run` injects secrets as environment variables (destroyed on exit)
- `op inject` replaces references in template files

## Keychain and credential helper integration: the gold standard

OS-level keychains offer encrypted storage with access control and biometric authentication.

### Platform keystores

| Platform | Keystore | CLI access |
|----------|----------|-----------|
| macOS | Keychain | `security` command |
| Linux | Secret Service API (D-Bus) | GNOME Keyring, KDE Wallet, KeePassXC |
| Windows | Credential Manager | `cmdkey`, WinCred API |

### Git's credential helper protocol

The seminal pattern adopted by Docker, `gh`, and others:

- Simple stdin/stdout text protocol with three operations: `get`, `store`, `erase`
- Users plug in their preferred backend
- Any program implementing this protocol can serve as a credential helper
- Infinitely extensible without modifying the core tool

## How major CLI tools handle credentials

| Tool | Storage method | Default location | Auth flow |
|------|---------------|-----------------|-----------|
| **gh** | OS keyring (since v2.24) | `~/.config/gh/hosts.yml` (fallback) | OAuth device flow |
| **AWS CLI** | INI file (plaintext) | `~/.aws/credentials` | `aws configure` / SSO |
| **Docker** | Base64 in JSON (not encryption) | `~/.docker/config.json` | `docker login --password-stdin` |
| **kubectl** | YAML (plaintext tokens) | `~/.kube/config` | Exec credential plugins |
| **git** | Credential helper protocol | Varies by helper | Helper-dependent |
| **1Password** | Encrypted vault | N/A | `op://` URIs |
