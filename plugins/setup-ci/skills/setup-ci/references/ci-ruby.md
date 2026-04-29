# Ruby CI Workflow

Use this template for Ruby projects.

2 parallel jobs: test, lint.

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
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2

      - name: Set up Ruby
        uses: ruby/setup-ruby@c4e5b1316158f92e3d49443a9d58b31d25ac0f8f # v1.306.0
        with:
          ruby-version-file: ".tool-versions"
          bundler-cache: true

      - name: Run tests
        run: bundle exec rake test

  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout code
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2

      - name: Set up Ruby
        uses: ruby/setup-ruby@c4e5b1316158f92e3d49443a9d58b31d25ac0f8f # v1.306.0
        with:
          ruby-version-file: ".tool-versions"
          bundler-cache: true

      - name: Run RuboCop
        run: bundle exec rubocop
```

## Notes

- Uses `ruby/setup-ruby@c4e5b1316158f92e3d49443a9d58b31d25ac0f8f # v1.306.0` with `bundler-cache: true` for automatic Bundler caching
- Detect the Ruby version from `.ruby-version` if it exists and use that instead of `"3.3"`
- If the project uses RSpec instead of Minitest, use `bundle exec rspec` for the test command
- If the project uses `standardrb` instead of RuboCop, adjust the lint command accordingly
