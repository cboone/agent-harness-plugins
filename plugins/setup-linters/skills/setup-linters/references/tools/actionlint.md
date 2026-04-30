# Actionlint

GitHub Actions workflow linter. Catches syntax errors, type mismatches, invalid expressions, and deprecated features in workflow files.

## When to Offer

When `.github/workflows/` directory is detected.

## Install

```bash
# Homebrew (recommended)
brew install actionlint

# Go install (alternative)
go install github.com/rhysd/actionlint/cmd/actionlint@v1.7.12
```

## Usage

```bash
# Lint all workflows in .github/workflows/
actionlint

# Lint a specific workflow file
actionlint .github/workflows/ci.yml
```

No config file is needed. Actionlint auto-detects `.github/workflows/` and validates all YAML files in it.

## What It Catches

- Invalid workflow syntax (missing required fields, bad indentation)
- Type errors in expressions (`${{ }}` blocks)
- References to undefined actions or invalid action versions
- Deprecated features (e.g., `set-output`, `save-state`)
- Invalid cron expressions in `schedule` triggers
- Shell script errors in `run:` steps (via ShellCheck integration)
- Inconsistent matrix configurations

## Notes

- Actionlint has no auto-fix mode. All issues must be resolved manually.
- Actionlint integrates with ShellCheck to validate inline shell scripts in `run:` steps. If ShellCheck is installed, these checks are automatic.
- No config file is needed for most projects. Actionlint supports a `actionlint.yaml` config for ignoring specific rules, but this is rarely necessary.
- Actionlint is very fast. It can lint dozens of workflow files in milliseconds.
