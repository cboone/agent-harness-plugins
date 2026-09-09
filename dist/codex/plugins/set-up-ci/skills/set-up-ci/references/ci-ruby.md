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
        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1

      - name: Set up Ruby
        uses: ruby/setup-ruby@95ef2b042f9d7a56d8268cba8559e2842e2ad01b # v1.321.0
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
        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1

      - name: Set up Ruby
        uses: ruby/setup-ruby@95ef2b042f9d7a56d8268cba8559e2842e2ad01b # v1.321.0
        with:
          ruby-version-file: ".tool-versions"
          bundler-cache: true

      - name: Run RuboCop
        run: bundle exec rubocop
```

## Notes

- Uses `ruby/setup-ruby@95ef2b042f9d7a56d8268cba8559e2842e2ad01b # v1.321.0` with `bundler-cache: true` for automatic Bundler caching
- Detect the Ruby version from `.ruby-version` if it exists and use that instead of `"3.3"`
- If the project uses RSpec instead of Minitest, use `bundle exec rspec` for the test command
- If the project uses `standardrb` instead of RuboCop, adjust the lint command accordingly
