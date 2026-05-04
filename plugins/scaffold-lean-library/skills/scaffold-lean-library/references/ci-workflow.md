# Lean CI Workflow Template

Use this template for `.github/workflows/ci.yml`. Refresh `CHECKOUT-SHA`, `CHECKOUT-TAG`, `LEAN-ACTION-SHA`, and `LEAN-ACTION-TAG` before emitting the workflow.

```yaml
name: CI

on:
  push:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "references/**"
      - "LICENSE"
      - ".editorconfig"
      - ".markdownlint-cli2.jsonc"
      - "cspell.jsonc"
      - "cspell-words.txt"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"
  pull_request:
    branches: [main]
    paths-ignore:
      - "*.md"
      - "docs/**"
      - "references/**"
      - "LICENSE"
      - ".editorconfig"
      - ".markdownlint-cli2.jsonc"
      - "cspell.jsonc"
      - "cspell-words.txt"
      - ".claude/**"
      - "**/CLAUDE.md"
      - "**/AGENTS.md"
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  lean:
    name: Lean build, lint, and test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@CHECKOUT-SHA # CHECKOUT-TAG

      - name: Build, lint, and test
        uses: leanprover/lean-action@LEAN-ACTION-SHA # LEAN-ACTION-TAG
        with:
          build: true
          lint: true
          test: true
          use-mathlib-cache: true
```

## Notes

- `leanprover/lean-action` detects the toolchain from `lean-toolchain` and runs `lake exe cache get` for Mathlib-downstream projects.
- Explicit `build`, `lint`, and `test` inputs make CI fail if any of those phases cannot run.
- Keep documentation-only changes on the text-lint workflow unless the project intentionally type-checks Markdown-derived Lean snippets.
