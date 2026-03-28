# GitHub Actions CI

CI workflow templates for running linters on push and pull request events. Adapt to the project's language and tool stack.

All templates include runner usage optimizations: `paths-ignore` skips CI for documentation and agent configuration changes, concurrency groups cancel superseded runs, and timeout limits prevent runaway jobs. The `*.md` pattern only matches root-level Markdown; nested `.md` files (e.g., Scrut CLI tests in `tests/scrut/`) are NOT ignored. Remove `*.md` from `paths-ignore` if your project treats Markdown as source code.

## Workflow File

Create `.github/workflows/lint.yml` (or add lint steps to an existing CI workflow).

## Per-Language Templates

### JavaScript / TypeScript

```yaml
name: Lint

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

jobs:
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "npm"

      - run: npm ci

      - name: ESLint
        run: npx eslint .

      - name: Prettier
        run: npx prettier --check .
```

### Go

Uses the `cboone/gh-actions` reusable workflow, which handles Go setup, golangci-lint installation with SHA-256 verification, and formatting checks internally.

```yaml
name: Lint

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

jobs:
  lint:
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@v2
    with:
      go-version-file: go.mod
      run-lint: true
      run-format-check: true
```

### Python

```yaml
name: Lint

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

jobs:
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v6

      - uses: astral-sh/setup-uv@v5

      - name: Ruff lint
        run: uvx ruff check .

      - name: Ruff format
        run: uvx ruff format --check .
```

### Rust

Uses the `cboone/gh-actions` reusable workflow, which handles Rust toolchain setup, clippy, rustfmt, cargo-deny, cargo-audit, and typos internally. To use it for lint-only (disabling tests), set `run-test: false`:

```yaml
name: Lint

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

jobs:
  lint:
    uses: cboone/gh-actions/.github/workflows/rust-ci.yml@v2
    with:
      run-test: false
```

If the project already uses `rust-ci.yml` for full CI (which includes all lint checks by default), a separate lint workflow is redundant.

### Ruby

```yaml
name: Lint

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

jobs:
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v6

      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: "3.3"
          bundler-cache: true

      - name: RuboCop
        run: bundle exec rubocop
```

### Shell

Uses the `cboone/gh-actions` reusable workflow, which handles ShellCheck and shfmt installation and execution internally.

```yaml
name: Lint

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

jobs:
  lint:
    uses: cboone/gh-actions/.github/workflows/shell-lint.yml@v1
```

### Zsh

No `cboone/gh-actions` reusable workflow exists for zsh checking. This inline job installs the additional tools not preinstalled on `ubuntu-latest` and runs the generated check script.

```yaml
name: Lint

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
        env:
          SKIP_SETOPT_CHECK: "1"
        run: make check-zsh
```

### Swift

```yaml
name: Lint

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

jobs:
  lint:
    # macOS runner required for Swift toolchain
    runs-on: macos-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v6

      - name: Install tools
        run: brew install swiftlint swiftformat

      - name: SwiftLint
        run: swiftlint lint --strict

      - name: SwiftFormat
        run: swiftformat --lint .
```

### Markdown

```yaml
- name: markdownlint
  run: npx markdownlint-cli2@0.21.0 "**/*.md"
```

## Cross-Language Steps

These steps can be added to any language workflow:

### Actionlint

As an inline step:

```yaml
- name: Actionlint
  uses: raven-actions/actionlint@v2
```

Or as a reusable workflow job:

```yaml
github-lint:
  uses: cboone/gh-actions/.github/workflows/github-lint.yml@v1
```

### Hadolint

```yaml
- name: Hadolint
  uses: hadolint/hadolint-action@v3.1.0
  with:
    dockerfile: Dockerfile
```

### Knip (JS/TS projects)

```yaml
- name: Knip
  run: npx knip@5.85.0
```

### Prettier (non-JS projects)

```yaml
- name: Prettier
  run: npx prettier@3.8.1 --check .
```

### Stylelint

```yaml
- name: Stylelint
  run: npx stylelint@17.3.0 "**/*.{css,scss,less}"
```

### Taplo

```yaml
- name: Taplo
  run: npx @taplo/cli@0.7.0 fmt --check
```

### yamllint

```yaml
- name: yamllint
  run: pipx run yamllint .
```

### cspell

As an inline step:

```yaml
- name: cspell
  uses: streetsidesoftware/cspell-action@v6
```

Or as a reusable workflow job (also covers markdownlint, prettier, yamllint):

```yaml
text-lint:
  uses: cboone/gh-actions/.github/workflows/text-lint.yml@v1
  with:
    run-cspell: true
```

## Combined Multi-Language Workflow

For monorepos or projects with multiple languages, combine into a single workflow. Go and Rust use reusable workflow calls; other languages use inline jobs:

```yaml
name: Lint

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

jobs:
  go-lint:
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@v2
    with:
      go-version-file: go.mod
      run-lint: true
      run-format-check: true

  rust-lint:
    uses: cboone/gh-actions/.github/workflows/rust-ci.yml@v2
    with:
      run-test: false

  javascript:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "npm"
      - run: npm ci
      - run: npx eslint .
      - run: npx prettier --check .
```

## Caching Strategies

| Language | Cache Action                        | Cache Key           |
| -------- | ----------------------------------- | ------------------- |
| Node.js  | `actions/setup-node` `cache: "npm"` | `package-lock.json` |
| Go       | Handled by reusable workflow        | `go.sum`            |
| Python   | `astral-sh/setup-uv` (built-in)     | `uv.lock`           |
| Rust     | Handled by reusable workflow        | `Cargo.lock`        |
| Ruby     | `ruby/setup-ruby` `bundler-cache`   | `Gemfile.lock`      |
| Swift    | _(none needed for lint-only CI)_    | _(N/A)_             |

## Notes

- Workflow file naming: use `.github/workflows/lint.yml` for a dedicated lint workflow.
- If the project already has a CI workflow (e.g., `ci.yml`), offer to add lint steps to it rather than creating a separate file.
- Go, Rust, and Shell templates use `cboone/gh-actions` reusable workflows. Other language templates use `actions/checkout@v6` and the latest stable setup actions.
- For Node.js projects, adjust the `cache` option to match the detected package manager (`npm`, `yarn`, `pnpm`).
- `ubuntu-latest` is the default runner. macOS or Windows runners are only needed for platform-specific linting.
- Pin all `npx` tool versions to exact versions (e.g., `npx tool@X.Y.Z`) for CI reproducibility. Update versions periodically. This applies to tools invoked via `npx` without a prior `npm ci` step; tools installed as project dependencies (after `npm ci`) use the locked version automatically.
