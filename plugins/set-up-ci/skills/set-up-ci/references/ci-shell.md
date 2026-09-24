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
    uses: cboone/gh-actions/.github/workflows/lint-shell.yml@bbe15187a1a8c60caded9295d1d2d90338a0bb93 # v4.1.0
```

## Notes

- The reusable workflow handles ShellCheck and shfmt installation, checkout, and execution internally
- ShellCheck and shfmt configuration (scan directories, formatting options) is managed by the reusable workflow
- The workflow installs a pinned, checksum-verified ShellCheck 0.11.0 rather than using the runner image's, which is 0.9.0 on `ubuntu-latest`. A first run can report findings from checks added in 0.10.0 and 0.11.0, SC2327 to SC2332 among them. Fix them, add a `# shellcheck disable=` directive, or pin `shellcheck-version` together with that release's `shellcheck-checksums` while working through them.
- The workflow fetches its installer using the `job.workflow_repository` and `job.workflow_sha` context properties, which GitHub Enterprise Server does not populate. On GHES, run the linters in a job of your own with the `set-up-shellcheck`, `set-up-shfmt` and `set-up-actionlint` composite actions instead.
