# GitHub Actions CI

CI workflow templates for running linters on push and pull request events. Adapt to the project's language and tool stack.

## Workflow File

Create `.github/workflows/lint.yml` (or add lint steps to an existing CI workflow).

## Per-Language Templates

### JavaScript / TypeScript

```yaml
name: Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

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

```yaml
name: Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod

      - name: golangci-lint
        uses: golangci/golangci-lint-action@v9

      - name: Check formatting
        run: test -z "$(gofmt -l .)"
```

### Python

```yaml
name: Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v5

      - name: Ruff lint
        run: uvx ruff check .

      - name: Ruff format
        run: uvx ruff format --check .
```

### Rust

```yaml
name: Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy, rustfmt

      - name: Clippy
        run: cargo clippy -- -D warnings

      - name: Rustfmt
        run: cargo fmt -- --check
```

### Ruby

```yaml
name: Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: "3.3"
          bundler-cache: true

      - name: RuboCop
        run: bundle exec rubocop
```

### Shell

```yaml
name: Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: ShellCheck
        uses: ludeeus/action-shellcheck@2.0.0
        with:
          scandir: scripts

      - name: Set up shfmt
        uses: mfinelli/setup-shfmt@v4

      - name: shfmt
        run: shfmt -d .
```

### Swift

```yaml
name: Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

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

```yaml
- name: Actionlint
  uses: raven-actions/actionlint@v2
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

```yaml
- name: cspell
  uses: streetsidesoftware/cspell-action@v6
```

## Combined Multi-Language Workflow

For monorepos or projects with multiple languages, combine steps into a single workflow with separate jobs:

```yaml
name: Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  javascript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "npm"
      - run: npm ci
      - run: npx eslint .
      - run: npx prettier --check .

  go:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      - uses: golangci/golangci-lint-action@v9
```

## Caching Strategies

| Language | Cache Action                        | Cache Key           |
| -------- | ----------------------------------- | ------------------- |
| Node.js  | `actions/setup-node` `cache: "npm"` | `package-lock.json` |
| Go       | `actions/setup-go` (built-in cache) | `go.sum`            |
| Python   | `astral-sh/setup-uv` (built-in)     | `uv.lock`           |
| Rust     | `Swatinem/rust-cache@v2`            | `Cargo.lock`        |
| Ruby     | `ruby/setup-ruby` `bundler-cache`   | `Gemfile.lock`      |
| Swift    | _(none needed for lint-only CI)_    | _(N/A)_             |

## Notes

- Workflow file naming: use `.github/workflows/lint.yml` for a dedicated lint workflow.
- If the project already has a CI workflow (e.g., `ci.yml`), offer to add lint steps to it rather than creating a separate file.
- All templates use `actions/checkout@v4` and the latest stable setup actions.
- For Node.js projects, adjust the `cache` option to match the detected package manager (`npm`, `yarn`, `pnpm`).
- `ubuntu-latest` is the default runner. macOS or Windows runners are only needed for platform-specific linting.
- Pin all `npx` tool versions to exact versions (e.g., `npx tool@X.Y.Z`) for CI reproducibility. Update versions periodically. This applies to tools invoked via `npx` without a prior `npm ci` step; tools installed as project dependencies (after `npm ci`) use the locked version automatically.
