# Ruby

## Tools

- **RuboCop**: The standard Ruby linter and formatter. Supports auto-correction for many rules.

## Install

```bash
# Bundler (recommended)
bundle add rubocop --group development

# Gem (alternative)
gem install rubocop
```

For Rails projects, also add extensions:

```bash
bundle add rubocop-rails --group development
bundle add rubocop-rspec --group development
bundle add rubocop-performance --group development
```

## Config

Create `.rubocop.yml` in the project root:

```yaml
AllCops:
  NewCops: enable
  TargetRubyVersion: 3.4
  SuggestExtensions: false

Style/FrozenStringLiteralComment:
  Enabled: true

Style/StringLiterals:
  EnforcedStyle: double_quotes

Layout/LineLength:
  Max: 120

Metrics/MethodLength:
  Max: 20
```

For Rails projects, add:

```yaml
require:
  - rubocop-rails
  - rubocop-rspec
  - rubocop-performance
```

## Commands

```bash
# Lint (check only)
rubocop

# Lint with auto-correction (safe fixes)
rubocop -a

# Lint with auto-correction (all fixes, including unsafe)
rubocop -A
```

## Notes

- `NewCops: enable` opts into new rules as they are added. This avoids surprises when upgrading.
- `TargetRubyVersion` should match the project's `.ruby-version` or `Gemfile` Ruby constraint.
- `rubocop -a` applies only safe corrections. `rubocop -A` applies all corrections, including those that may change behavior.
- RuboCop extensions (`rubocop-rails`, `rubocop-rspec`, `rubocop-performance`) add domain-specific rules. Only install the ones relevant to the project.
- Generate a todo file for gradual adoption: `rubocop --auto-gen-config` creates `.rubocop_todo.yml`.
