# Shell CI Workflow

Use this template for shell script projects. Uses the `cboone/gh-actions` reusable workflow, which handles ShellCheck and shfmt installation and execution internally.

```yaml
name: CI

on:
  push:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"
  pull_request:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "LICENSE"
      - ".editorconfig"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  lint:
    uses: cboone/gh-actions/.github/workflows/lint-shell.yml@91f9abd25d4f82354c0f950dfc8b6d7525b0f5b5 # v3.0.0
```

## Notes

- The reusable workflow handles ShellCheck and shfmt installation, checkout, and execution internally
- ShellCheck and shfmt configuration (scan directories, formatting options) is managed by the reusable workflow
