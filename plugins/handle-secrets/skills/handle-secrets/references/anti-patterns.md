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

**Rule:** If you store plaintext, tell users it's plaintext. Docker now warns: _"WARNING! Your password will be stored unencrypted."_

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

## Shell expansion of secrets into command arguments

Any time a secret is expanded via `$VAR` or `${VAR}` into a command's argument list, the shell performs the expansion **before** launching the process. The expanded value becomes part of the process's argv, visible via `ps` and `/proc/<pid>/cmdline`.

```bash
# DANGEROUS: shell expands $TOKEN into curl's argv, visible via ps
export TOKEN=secret
curl -H "Authorization: Bearer ${TOKEN}" https://api.example.com
```

```bash
# ALSO DANGEROUS (and misleading): with inline assignment, $TOKEN is expanded
# BEFORE the assignment takes effect — so $TOKEN uses its previous value
# (or empty if unset), not "secret"
TOKEN=secret curl -H "Authorization: Bearer $TOKEN" https://api.example.com
```

```bash
# SAFE: tool reads the environment variable internally, no shell expansion
export API_TOKEN=secret
my-cli-tool --token-env API_TOKEN    # Tool calls os.Getenv("API_TOKEN") internally
```

**The safe pattern:** Pass the **name** of the environment variable to the tool (or rely on a well-known variable name convention), and have the tool read the value from its own process environment. This keeps the secret out of argv entirely.

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
