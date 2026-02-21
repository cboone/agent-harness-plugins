# Setup GitHub Actions CI

## Context

This repository has 21 Claude Code plugins with Markdown, JSON, and shell scripts, but no automated CI. Markdown linting is configured locally (`markdownlint-cli2` via `yarn lint`) but nothing runs on push or PR. Plugin/marketplace structural consistency is only checked manually via the `check-versions` skill. Adding CI catches structural errors, lint violations, and version mismatches before they reach `main`.

## Files to Create

### 1. `.github/workflows/ci.yml`

Single-job workflow with 5 steps (runs in under a minute, so parallelizing into separate jobs adds overhead without benefit):

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  ci:
    name: Lint and validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "yarn"
      - run: yarn install --immutable
      - name: Lint Markdown
        run: yarn lint
      - name: ShellCheck
        run: shellcheck -S warning plugins/*/scripts/*
      - name: Validate JSON syntax
        run: bin/validate-json
      - name: Validate plugin structure
        run: bin/validate-plugins
```

Key choices:

- **Single job**: everything finishes in seconds; separate runners would add more overhead than they save
- **`yarn install --immutable`**: fails if `yarn.lock` is out of sync (Yarn Berry equivalent of `npm ci`)
- **`-S warning`**: skips info-level ShellCheck notes (SC2016 false positives on GraphQL `$vars` in single-quoted strings)
- **`permissions: contents: read`**: minimal permissions
- **Node 22**: current LTS; `markdownlint-cli2` v0.20 requires Node 18+
- **ShellCheck and `jq`**: both preinstalled on `ubuntu-latest`, no extra actions needed

### 2. `bin/validate-json`

Shell script that finds all `.json` files (excluding `node_modules/`) and validates each with `jq empty`. Uses `::error file=` GitHub Actions annotations for inline error display.

### 3. `bin/validate-plugins`

Shell script performing these checks (accumulates all errors before failing, so a single run surfaces everything):

1. Every `plugins/*/` directory has `.claude-plugin/plugin.json`
1. Every `plugins/*/` directory has `README.md`
1. `plugin.json` `name` field matches its directory name
1. Required fields present in `plugin.json`: `author`, `description`, `homepage`, `keywords`, `license`, `name`, `repository`, `version`
1. Every plugin directory is registered in `.claude-plugin/marketplace.json`
1. Every marketplace entry points to an existing `plugins/*/` directory
1. Required fields present in each marketplace entry: `author`, `category`, `description`, `homepage`, `keywords`, `license`, `name`, `repository`, `source`, `version`
1. Version in each `plugin.json` matches its marketplace entry
1. Marketplace `plugins` array is in alphabetical order by `name`

## Files to Modify

### 4. `package.json`

- Add `"packageManager": "yarn@4.12.0"` so `actions/setup-node` uses corepack to install the correct Yarn version
- Add `"validate"` script pointing to `bin/validate-plugins` for local convenience

## Implementation Steps

1. Update `package.json` (add `packageManager` field and `validate` script)
1. Create `bin/validate-json`, make executable
1. Create `bin/validate-plugins`, make executable
1. Create `.github/workflows/ci.yml`
1. Run `bin/validate-json` locally to confirm it passes
1. Run `bin/validate-plugins` locally to confirm it passes
1. Run `shellcheck -S warning plugins/*/scripts/*` locally to confirm clean
1. Run `yarn lint` locally to confirm clean
1. Commit

## Verification

- Run each check locally before committing
- Push branch and observe CI run on the PR
- Intentionally break something (e.g., rename a plugin.json field) to verify CI catches it
