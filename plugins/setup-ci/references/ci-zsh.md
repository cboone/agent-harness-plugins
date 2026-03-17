# Zsh CI Workflow

Use this template for zsh script projects. No `cboone/gh-actions` reusable workflow exists for zsh checking, so this inline job installs the additional tools not preinstalled on `ubuntu-latest` and runs the generated check script via `make check-zsh`.

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
  zsh-check:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v6

      - name: Install zsh
        run: sudo apt-get update && sudo apt-get install -y zsh

      - name: Install checkbashisms
        run: sudo apt-get install -y devscripts

      - uses: mfinelli/setup-shfmt@v4

      - name: Install shellharden
        run: cargo install --locked shellharden

      - name: Run zsh checks
        run: make check-zsh
```

## Notes

- ShellCheck is pre-installed on `ubuntu-latest` runners
- `zsh` is installed via `apt-get` (not pre-installed on Ubuntu runners)
- `devscripts` provides `checkbashisms`
- `shellharden` is installed via `cargo install` (Rust toolchain is pre-installed on `ubuntu-latest`)
- `shfmt` is installed via the `mfinelli/setup-shfmt@v4` action
- The `make check-zsh` target runs `./scripts/check-zsh.zsh`, which executes the 7-tool pipeline
