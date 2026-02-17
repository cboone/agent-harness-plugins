# Anti-Patterns That Cause Real Security Incidents

Known mistakes in secret handling with real-world examples.

## Accepting secrets as command-line arguments

**The single most dangerous anti-pattern.** Every argument is:

- Visible to all users via `ps aux` (world-readable `/proc/<pid>/cmdline`)
- Recorded in shell history files
- Captured by audit logs and monitoring tools

### Real incidents

- **CVE-2022-45868** (H2 Database): Accepted `-webAdminPassword` as a CLI argument
- **CVE-2006-5659** (PAM_extern): Sent passwords as CLI arguments, harvested via `ps`
- **FreeRDP Issue #3639**: Race condition between process start and argv overwrite

## Base64 "encryption"

Docker's canonical anti-pattern: storing `base64(username:password)` in `~/.docker/config.json`. Base64 is **encoding, not encryption** — it decodes trivially — yet it creates a false sense of security.

**Rule:** If you store plaintext, tell users it's plaintext. Docker now warns: *"WARNING! Your password will be stored unencrypted."*

## Leaking credentials into command output

**CVE-2023-36052** (Azure CLI, CVSS 8.6): The CLI exposed credentials in standard output without any redaction. Those values propagated through GitHub Actions and Azure Pipelines logs.

**Rule:** All output that might reach logs must be redacted before emission.

## Logging HTTP requests with Authorization headers

A debug mode that dumps `Authorization: Bearer sk_live_xxxxx` to a log file creates a persistent credential leak.

**Sanitize headers before logging:**

- `Authorization`
- `Cookie`
- `X-Api-Key`
- `Token`
- `Secret`
- Any custom header carrying credentials

## The command substitution trap

```bash
# DANGEROUS: $(</dev/stdin) expands into curl's argument list, visible via ps
echo "secret" | curl -d "$(</dev/stdin)" https://api.example.com
```

```bash
# SAFE: @- reads directly from the pipe, never enters argv
echo "secret" | curl -d @- https://api.example.com
```

The dangerous version expands stdin contents into `curl`'s argv, making the secret visible to every user on the system. The safe version uses `@-` to read the request body directly from stdin.

## The inline environment variable trap

```bash
# DANGEROUS: $TOKEN expands into curl's argv, visible via ps
TOKEN=secret curl -H "Authorization: Bearer $TOKEN" https://api.example.com
```

```bash
# SAFE: export separately, then use in a subshell or read from env in code
export TOKEN=secret
curl -H "Authorization: Bearer ${TOKEN}" https://api.example.com
```

With inline variable assignment, the shell expands `$TOKEN` into the argument list of the `curl` process, making the value visible in `/proc/<pid>/cmdline`.

## The create-then-chmod race condition

```python
# WRONG: file briefly exists with default permissions (often 0644)
with open(cred_path, 'w') as f:
    f.write(credentials)
os.chmod(cred_path, 0o600)
```

```python
# CORRECT: permissions set atomically at creation time
fd = os.open(cred_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, 'w') as f:
    f.write(credentials)
```

Between file creation and `chmod`, another process can read the file with its insecure default permissions.

## Not clearing credentials on logout

Leaving orphaned secrets on disk after logout means:

- Old tokens remain valid and accessible
- Users believe they've logged out when they haven't fully
- Compromised machines retain access even after "logout"

A `logout` command must revoke tokens server-side, delete stored credentials, and zero in-memory copies.

## Silent fallback to insecure storage

GitHub CLI issue #7757: When the OS keyring fails, `gh` silently falls back to plaintext storage. Users believe their credentials are encrypted when they aren't.

**Rule:** If falling back to a less secure method, **always warn the user explicitly**.
