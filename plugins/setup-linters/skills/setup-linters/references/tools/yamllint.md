# yamllint

YAML linter that checks syntax, formatting, and common issues in YAML files.

## When to Offer

When the project has many YAML files (`*.yaml`, `*.yml`), beyond the typical few config files.

## Install

```bash
# uv (preferred)
uv tool install yamllint

# pip (alternative)
pip install 'yamllint==1.38.0'

# Homebrew (alternative)
brew install yamllint
```

## Config

Create `.yamllint.yml` in the project root:

```yaml
extends: default

rules:
  line-length:
    max: 120
    allow-non-breakable-inline-mappings: true
  truthy:
    forbid-implicit-yes-no: true
  document-start: disable
  comments:
    min-spaces-from-content: 1
```

## Commands

```bash
# Lint all YAML files
yamllint .

# Lint a specific file
yamllint .github/workflows/ci.yml

# Strict mode (treat warnings as errors)
yamllint -s .
```

## Common Rule Customizations

| Rule             | Description                  | Default | Common Override          |
| ---------------- | ---------------------------- | ------- | ------------------------ |
| `line-length`    | Max line length              | 80      | `120` or `disable`       |
| `truthy`         | Bare yes/no/on/off values    | Warning | `forbid-implicit-yes-no` |
| `document-start` | Require `---` at file start  | Warning | `disable`                |
| `comments`       | Space before comment content | 2       | `1`                      |
| `indentation`    | Indent size                  | 2       | Keep default             |

## Notes

- yamllint has no auto-fix mode. All issues must be resolved manually.
- The `truthy` rule catches common YAML gotchas where `yes`, `no`, `on`, `off` are interpreted as booleans instead of strings.
- `document-start: disable` removes the requirement for `---` at the top of every YAML file, which most projects do not use.
- yamllint is a Python tool. Use `uv tool install` per project conventions when available.
- For projects with only a few YAML files (e.g., just CI workflows), yamllint may be overkill. Actionlint covers GitHub Actions YAML specifically.
