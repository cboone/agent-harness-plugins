# Python CI Workflow

Use this template for Python projects. Uses `uv` for dependency management and `ruff` for linting and formatting.

3 parallel jobs: test, lint, format.

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
  test:
    name: Test
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up uv
        uses: astral-sh/setup-uv@v5

      - name: Run tests
        run: uv run pytest

  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up uv
        uses: astral-sh/setup-uv@v5

      - name: Run ruff lint
        run: uvx ruff check .

  format:
    name: Format
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up uv
        uses: astral-sh/setup-uv@v5

      - name: Check formatting
        run: uvx ruff format --check .
```

## Notes

- Uses `astral-sh/setup-uv@v5` for fast Python tooling
- `uvx ruff` runs ruff without installing it into the project
- `uv run pytest` uses the project's virtual environment for testing
- If the project uses a different test runner, adjust accordingly
