# Swift

## Tools

- **SwiftLint**: Linter that enforces Swift style and conventions. Supports auto-correction for some rules.
- **SwiftFormat**: Opinionated code formatter for Swift. Handles whitespace, braces, and other formatting concerns.

## Install

```bash
# Homebrew (recommended)
brew install swiftlint swiftformat
```

## Config

### .swiftlint.yml

Create `.swiftlint.yml` in the project root:

```yaml
opt_in_rules:
  - empty_count
  - empty_string
  - fatal_error_message
  - first_where
  - force_unwrapping
  - implicitly_unwrapped_optional
  - last_where
  - missing_docs
  - modifier_order
  - overridden_super_call
  - private_action
  - private_outlet
  - prohibited_super_call
  - sorted_first_last
  - toggle_bool
  - trailing_comma
  - unneeded_parentheses_in_closure_argument
  - vertical_parameter_alignment_on_call

trailing_comma:
  mandatory_comma: true

excluded:
  - .build
  - Packages
  - DerivedData
```

### .swiftformat

Create `.swiftformat` in the project root:

```text
--indent 4
--wraparguments before-first
--wrapcollections before-first
--maxwidth 120
--trailingCommas always
--stripunusedargs closure-only
--exclude .build,Packages,DerivedData
```

### .swift-version

Create `.swift-version` in the project root to pin the Swift language version:

```text
6.0
```

Adjust to match the project's minimum Swift version.

## Commands

```bash
# SwiftLint (lint)
swiftlint lint --strict

# SwiftLint (auto-fix then verify)
swiftlint lint --fix && swiftlint lint --strict

# SwiftFormat (check)
swiftformat --lint .

# SwiftFormat (format in place)
swiftformat .
```

## Makefile Targets

```makefile
.PHONY: lint lint-fix fmt

lint: ## Lint Swift code
	swiftlint lint --strict
	swiftformat --lint .

lint-fix: ## Auto-fix then verify
	swiftlint lint --fix
	swiftlint lint --strict
	swiftformat .

fmt: ## Format Swift code
	swiftformat .
```

## Notes

- **Trailing comma conflict**: SwiftLint and SwiftFormat disagree on trailing commas by default. SwiftLint's `trailing_comma` rule warns against trailing commas, while SwiftFormat's `trailingCommas` rule adds them. To resolve this, set `mandatory_comma: true` in `.swiftlint.yml` and `--trailingCommas always` in `.swiftformat`. This makes both tools agree that trailing commas are required.
- **Lint-fix verification pattern**: The `lint-fix` target runs `swiftlint lint --fix` followed by `swiftlint lint --strict`. The first pass auto-corrects fixable violations; the second pass verifies that no unfixable violations remain. Without the verification pass, unfixable lint errors would go unnoticed.
- SwiftLint uses `--strict` to treat warnings as errors, ensuring CI catches all violations.
- SwiftFormat handles all formatting concerns (indentation, braces, whitespace), while SwiftLint focuses on style rules and code quality checks.
- The `.swift-version` file is read by both SwiftLint and SwiftFormat to determine the target Swift language version.
- Excluded directories (`.build`, `Packages`, `DerivedData`) should be configured in both tools to avoid linting generated or cached code.
