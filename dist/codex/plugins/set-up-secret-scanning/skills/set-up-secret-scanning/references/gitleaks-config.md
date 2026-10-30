# .gitleaks.toml Configuration Template

A starter configuration that extends the built-in rules without adding exclusions. Lockfiles and vendored paths remain in scope, subject to Gitleaks' built-in rules and allowlists.

## Inherited Coverage Limit

Extending defaults also inherits their exclusions. In the checked version, [Gitleaks 8.30.1's default configuration](https://github.com/gitleaks/gitleaks/blob/v8.30.1/config/gitleaks.toml) excludes `go.sum`, `package-lock.json`, `yarn.lock` and `pnpm-lock.yaml`. It also excludes `vendor/modules.txt`, the `vendor/` subtrees for `github.com`, `golang.org/x`, `google.golang.org`, `gopkg.in`, `istio.io`, `k8s.io`, `sigs.k8s.io`, `bundle` and `ruby`. Other built-in exclusions apply too; check the configuration shipped with the scanner version in use.

Removing the starter's added exclusions restores coverage only for paths the defaults do not already exclude, such as `Gemfile.lock` and other vendor paths. A project that needs inherited exclusions scanned must maintain a full configuration without `useDefault`, retaining the required detection rules while removing the relevant exclusions and testing the resulting coverage. This starter does not supply that separate configuration.

## Template

```toml
[extend]
# Use the default gitleaks rules without project-specific exclusions.
useDefault = true
```

## Reviewing False Positives

Scan before adding suppressions. Review the finding's rule, matched content, path and commit to establish why it is not a credential. A dependency hash can resemble a token, but its presence in a lockfile does not establish that it is harmless. Treat a real credential as an exposure requiring remediation, even if it has been revoked.

Record the reason for each suppression. Prefer the narrowest scope that covers the reviewed false positive:

- For an isolated finding, copy its exact `Fingerprint` from the Gitleaks report into `.gitleaksignore` only after checking every match it covers. Fingerprints match path, rule and starting line, plus commit when present; they do not distinguish content or columns. Multiple same-rule matches on one line share the suppression. A fingerprint without a commit also applies across commits. If an unrelated credential shares that scope, use a rule-specific content pattern instead. Recheck when the file or finding changes. See [Gitleaks ignore support](https://github.com/gitleaks/gitleaks#gitleaksignore).
- For a repeated known non-secret value, add an anchored content pattern to the affected rule's allowlist. Match only the reviewed value or format, and keep the rule enabled. If a path constraint is also necessary, combine it with the content constraint using `condition = "AND"`; the default OR condition can suppress either criterion independently.

Do not exclude whole lockfiles, vendor directories, fixture directories or file extensions to resolve individual findings. Do not disable a built-in rule or exclude entire commits to silence false positives. These suppressions can hide unrelated credentials, including in Git history.

After customizing, rescan and confirm the reviewed finding is suppressed while other synthetic credentials in the same file or directory remain detectable. See [Gitleaks configuration](https://github.com/gitleaks/gitleaks#configuration) for syntax supported by the scanner version in use.

## Adding Custom Rules

Add rules only for project-specific secret patterns that the defaults do not cover:

```toml
[[rules]]
id = "rule-id"
description = "What this rule detects"
regex = '''pattern_here'''
keywords = ["keyword"]
```

The `keywords` field is a pre-filter: gitleaks only applies the regex to lines containing at least one keyword.

## Pull Request Configuration Trust

The reusable workflow currently scans the PR checkout using its configuration, including an automatically discovered `.gitleaks.toml` even when `allowlist-config` is not supplied. A PR can therefore weaken its own scan by changing that configuration. A starter with no added exclusions does not enforce a trusted scanning policy.

Loading configuration from the trusted base revision on pull requests is tracked in [cboone/gh-actions issue 157](https://github.com/cboone/gh-actions/issues/157). Review scanner configuration changes as security-sensitive until that workflow boundary is enforced.
