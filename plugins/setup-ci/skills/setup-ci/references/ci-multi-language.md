# Multi-Language CI Workflow

For projects with multiple detected languages, combine language-specific jobs into one workflow file. Go, Rust, and Zig use reusable workflow calls; other languages use inline jobs.

Example combining Go, Rust, and JavaScript:

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
  go-ci:
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@f69487c36f4e217afe28ea631de39edf17d35238 # v2.1.4
    with:
      go-version-file: go.mod
      run-format-check: true

  rust-ci:
    uses: cboone/gh-actions/.github/workflows/rust-ci.yml@f69487c36f4e217afe28ea631de39edf17d35238 # v2.1.4

  js-test:
    name: "JS: Test"
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2

      - name: Set up Node.js
        uses: actions/setup-node@48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e # v6.4.0
        with:
          node-version-file: ".tool-versions"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

  js-lint:
    name: "JS: Lint"
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2

      - name: Set up Node.js
        uses: actions/setup-node@48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e # v6.4.0
        with:
          node-version-file: ".tool-versions"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run ESLint
        run: npx eslint .
```

## Notes

- Go, Rust, and Zig use reusable workflow calls that create their own parallel jobs internally
- Non-reusable languages (JS/TS, Python, Ruby) use inline jobs with language-prefixed IDs (e.g., `js-test`, `js-lint`)
- Prefix job display names with the language (e.g., `"JS: Test"`, `"JS: Lint"`)
- Only include jobs relevant to each detected language
- For Zig, pass `zig-version-file: build.zig.zon` to make the wrapped `mlugg/setup-zig` read `minimum_zig_version` from `build.zig.zon`. Go and Rust work with defaults.
