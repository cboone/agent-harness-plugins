# .gitleaks.toml Configuration Template

A starter configuration that extends the built-in rules and adds common allowlist entries.

## Template

```toml
[extend]
# Use the default gitleaks rules as a base.
useDefault = true

# Example: custom rule (uncomment and adapt as needed)
# [[rules]]
# id = "custom-api-key"
# description = "Custom API key pattern"
# regex = '''(?i)custom[_-]?api[_-]?key\s*[=:]\s*['"]?([a-zA-Z0-9]{32,})['"]?'''
# keywords = ["custom_api_key", "custom-api-key"]

[allowlist]
# Paths to exclude from scanning.
# Add lockfiles, vendored dependencies, and test fixtures that trigger false positives.
paths = [
  '''go\.sum''',
  '''package-lock\.json''',
  '''yarn\.lock''',
  '''pnpm-lock\.yaml''',
  '''Gemfile\.lock''',
  '''vendor/''',
]
```

## Customization Guide

### Adding Custom Rules

Define rules to detect project-specific secret patterns:

```toml
[[rules]]
id = "rule-id"
description = "What this rule detects"
regex = '''pattern_here'''
keywords = ["keyword"]
```

The `keywords` field is a pre-filter: gitleaks only applies the regex to lines containing at least one keyword, which improves performance.

### Expanding the Allowlist

Suppress false positives with additional allowlist entries:

- **paths**: File path patterns (regexes) to skip entirely
- **regexes**: Content patterns to ignore when matched
- **commits**: Specific commit SHAs to exclude (useful for known-rotated secrets in history)

```toml
[allowlist]
paths = [
  '''test/fixtures/''',
  '''\.md$''',
]
regexes = [
  '''EXAMPLE_KEY_PLACEHOLDER''',
]
commits = [
  "abc123def456",
]
```

### Disabling Built-in Rules

If a default rule produces too many false positives, disable it by ID:

```toml
[extend]
useDefault = true
disabledRules = ["generic-api-key"]
```

Find built-in rule IDs in the [gitleaks default config](https://github.com/gitleaks/gitleaks/blob/master/config/gitleaks.toml).
