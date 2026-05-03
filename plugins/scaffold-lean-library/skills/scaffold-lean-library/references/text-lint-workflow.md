# Text Lint Workflow Template

Use this template for `.github/workflows/text-lint.yml`. Refresh `CBOONE-GH-ACTIONS-SHA` and `CBOONE-GH-ACTIONS-TAG` before emitting the workflow.

```yaml
name: Text lint

on:
  push:
    branches: [main]
    paths:
      - "**/*.md"
      - "**/*.yml"
      - "**/*.yaml"
      - ".markdownlint-cli2.jsonc"
      - "cspell.jsonc"
      - "cspell-words.txt"
      - ".github/workflows/text-lint.yml"
  pull_request:
    branches: [main]
    paths:
      - "**/*.md"
      - "**/*.yml"
      - "**/*.yaml"
      - ".markdownlint-cli2.jsonc"
      - "cspell.jsonc"
      - "cspell-words.txt"
      - ".github/workflows/text-lint.yml"
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  text-lint:
    uses: cboone/gh-actions/.github/workflows/lint-text.yml@CBOONE-GH-ACTIONS-SHA # CBOONE-GH-ACTIONS-TAG
    with:
      run-cspell: true
      run-markdownlint: true
      run-prettier: true
      run-yamllint: false
```

## Notes

- The reusable workflow installs markdownlint-cli2, Prettier, and cspell from the pinned `cboone/gh-actions` lockfile.
- Keep YAML linting disabled unless the generated repository adds a `.yamllint.yml` config and a matching local target.
