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
    uses: cboone/gh-actions/.github/workflows/run-go-ci.yml@bbe15187a1a8c60caded9295d1d2d90338a0bb93 # v4.1.0
    with:
      go-version-file: go.mod
      run-format-check: true

  rust-ci:
    uses: cboone/gh-actions/.github/workflows/run-rust-ci.yml@bbe15187a1a8c60caded9295d1d2d90338a0bb93 # v4.1.0

  js-test:
    name: "JS: Test"
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1

      - name: Set up Node.js
        uses: actions/setup-node@820762786026740c76f36085b0efc47a31fe5020 # v7.0.0
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
        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1

      - name: Set up Node.js
        uses: actions/setup-node@820762786026740c76f36085b0efc47a31fe5020 # v7.0.0
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
- The Go call passes no `run-lint`, which defaults to true, so golangci-lint runs here. `run-lint` installs golangci-lint 2.13.2, up from 2.11.4 before v4.1.0. A first run on the newer release can report findings the older one did not. Pin `golangci-lint-version` to a known release while working through them.
- Non-reusable languages (JS/TS, Python, Ruby) use inline jobs with language-prefixed IDs (e.g., `js-test`, `js-lint`)
- Prefix job display names with the language (e.g., `"JS: Test"`, `"JS: Lint"`)
- Only include jobs relevant to each detected language
- For Zig, pass `zig-version-file: build.zig.zon` to make the wrapped `mlugg/setup-zig` read `minimum_zig_version` from `build.zig.zon`. Go and Rust work with defaults.
