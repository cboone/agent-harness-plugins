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
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2

      - uses: actions/setup-node@48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e # v6.4.0
        with:
          node-version-file: ".tool-versions"
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
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@f69487c36f4e217afe28ea631de39edf17d35238 # v2.1.4
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
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2

      - uses: astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b # v8.1.0

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
    uses: cboone/gh-actions/.github/workflows/rust-ci.yml@f69487c36f4e217afe28ea631de39edf17d35238 # v2.1.4
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
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2

      - uses: ruby/setup-ruby@c4e5b1316158f92e3d49443a9d58b31d25ac0f8f # v1.306.0
        with:
          ruby-version-file: ".tool-versions"
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
    uses: cboone/gh-actions/.github/workflows/shell-lint.yml@e4e9f34f54041223e72f0d6241efede27a698fa1 # v1.0.0
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
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2

      - name: Install zsh
        run: sudo apt-get update && sudo apt-get install -y zsh

      - name: Install checkbashisms
        run: sudo apt-get install -y devscripts

      - uses: mfinelli/setup-shfmt@a25fda4c1fe115aec0f85e04126610841bc3141d # v4.0.1

      - name: Install shellharden
        run: cargo install --locked --version 4.3.1 shellharden

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
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2

      - name: Install tools
        run: brew install swiftlint swiftformat

      - name: SwiftLint
        run: swiftlint lint --strict

      - name: SwiftFormat
        run: swiftformat --lint .
```

### Lean

Lean projects use `leanprover/lean-action`, which runs `lake build`, `lake test`, and (with `lint: true`) `lake lint` in a single composite action. There is no separate "Lean lint" workflow; the lint step is one input to the same action that handles build and test.

This skill does not synthesize a Lean CI workflow from scratch; that is the Lean scaffolder's job. The patch this skill makes is enabling the `lint: true` input on an already-present `leanprover/lean-action` step:

```yaml
- uses: leanprover/lean-action@<sha> # <tag>
  with:
    test: true
    lint: true
```

If the project deliberately splits build, test, and lint into separate jobs, recommend a dedicated step instead of toggling `lint: true`:

```yaml
- name: Lean lint
  run: lake lint
```

The `lake lint` step requires Mathlib's prebuilt artifacts to be on disk, so the bootstrap step (`bin/bootstrap-worktree` or the equivalent `lake exe cache get` invocation) must run first. `leanprover/lean-action` handles this internally; a hand-rolled split workflow has to handle it explicitly.

Refresh the SHA and tag for `leanprover/lean-action` to current latest before emitting:

```bash
TAG="$(gh release view --repo leanprover/lean-action --json tagName --jq '.tagName')"
SHA="$(gh api "repos/leanprover/lean-action/commits/${TAG}" --jq '.sha')"
echo "${SHA} # ${TAG}"
```

### Markdown

```yaml
- name: markdownlint
  run: npx markdownlint-cli2@0.22.1 "**/*.md"
```

## Cross-Language Steps

These steps can be added to any language workflow:

### Actionlint

As an inline step:

```yaml
- name: Actionlint
  uses: raven-actions/actionlint@205b530c5d9fa8f44ae9ed59f341a0db994aa6f8 # v2.1.2
```

Or as a reusable workflow job:

```yaml
github-lint:
  uses: cboone/gh-actions/.github/workflows/github-lint.yml@e4e9f34f54041223e72f0d6241efede27a698fa1 # v1.0.0
```

### Hadolint

```yaml
- name: Hadolint
  uses: hadolint/hadolint-action@2332a7b74a6de0dda2e2221d575162eba76ba5e5 # v3.3.0
  with:
    dockerfile: Dockerfile
```

### Knip (JS/TS projects)

```yaml
- name: Knip
  run: npx knip@6.9.0
```

### Prettier (non-JS projects)

```yaml
- name: Prettier
  run: npx prettier@3.8.3 --check .
```

### Stylelint

```yaml
- name: Stylelint
  run: npx stylelint@17.9.1 "**/*.{css,scss,less}"
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
  uses: streetsidesoftware/cspell-action@de2a73e963e7443969755b648a1008f77033c5b2 # v8.4.0
```

Or as a reusable workflow job (also covers markdownlint, prettier, yamllint):

```yaml
text-lint:
  uses: cboone/gh-actions/.github/workflows/text-lint.yml@e4e9f34f54041223e72f0d6241efede27a698fa1 # v1.0.0
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
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@f69487c36f4e217afe28ea631de39edf17d35238 # v2.1.4
    with:
      go-version-file: go.mod
      run-lint: true
      run-format-check: true

  rust-lint:
    uses: cboone/gh-actions/.github/workflows/rust-ci.yml@f69487c36f4e217afe28ea631de39edf17d35238 # v2.1.4
    with:
      run-test: false

  javascript:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
      - uses: actions/setup-node@48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e # v6.4.0
        with:
          node-version-file: ".tool-versions"
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
- Go, Rust, and Shell templates use `cboone/gh-actions` reusable workflows. Other language templates use `actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2` and the latest stable setup actions.
- For Node.js projects, adjust the `cache` option to match the detected package manager (`npm`, `yarn`, `pnpm`).
- `ubuntu-latest` is the default runner. macOS or Windows runners are only needed for platform-specific linting.
- Pin all `npx` tool versions to exact versions (e.g., `npx tool@X.Y.Z`) for CI reproducibility. Update versions periodically. This applies to tools invoked via `npx` without a prior `npm ci` step; tools installed as project dependencies (after `npm ci`) use the locked version automatically.
- Pin every `uses:` ref to a 40-character commit SHA with a `# vX.Y.Z` comment that matches the upstream tag (the leading `v` is optional when upstream omits it, as with `ludeeus/action-shellcheck`'s `2.0.0` tag). This applies to third-party actions and to `cboone/gh-actions` reusable workflows alike. Tags are mutable; SHAs are not. Dependabot bumps the SHA and the comment together. Refresh the `cboone/gh-actions` SHAs at scaffold time using the snippet in this skill's `SKILL.md`. A small number of actions release through moving channel aliases instead of versioned tags (e.g., `dtolnay/rust-toolchain@<sha> # stable`); use the channel name in the comment for those refs and accept that `bin/version-audit` cannot track drift on them.
