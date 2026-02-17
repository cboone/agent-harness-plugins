# Secret Handling Checklist

Condensed, actionable rules for quick code reviews.

## Input

- [ ] Secrets are **never** accepted as command-line arguments (`--password`, `--token`, `--api-key`)
- [ ] Environment variables are parsed once at startup, then removed from the process environment
- [ ] Interactive prompts suppress echo when a TTY is available
- [ ] Stdin/pipe input is supported for automation (`--password-file`, reading from `-`)
- [ ] TTY detection chooses between interactive prompt and pipe reading

## Storage

- [ ] Credential files are created atomically with 0600 permissions (not create-then-chmod)
- [ ] Config and credentials are in **separate files** (like `~/.aws/config` vs `~/.aws/credentials`)
- [ ] File paths follow XDG Base Directory conventions
- [ ] OS keychain integration is offered when available (macOS Keychain, Linux Secret Service, Windows Credential Manager)
- [ ] The tool warns when falling back to plaintext storage

## Output

- [ ] Secret values are **never** echoed in confirmation messages
- [ ] Debug/verbose logs redact `Authorization`, `Cookie`, `X-Api-Key`, `Token`, and `Secret` headers
- [ ] Error messages do not include secret values
- [ ] `--help` output does not display environment variable values (use `hide_env_values` or equivalent)

## Lifecycle

- [ ] Logout/revoke commands delete stored credentials from keychain and config files
- [ ] Logout revokes tokens server-side when supported
- [ ] Short-lived, scoped tokens are preferred over long-lived full-access tokens
- [ ] Token refresh is handled automatically when possible

## Type Safety

- [ ] Secret values use a wrapper type that redacts on `Debug`/`Display`/`String()` (language-dependent)
- [ ] Accessing the secret value requires an explicit call (e.g., `expose_secret()`, `Expose()`)
- [ ] Memory containing secrets is zeroed after use (where the language allows)
