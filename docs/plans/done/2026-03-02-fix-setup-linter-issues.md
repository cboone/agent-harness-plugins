# Fix setup-linters Issues (#117, #125, #126, #128, #140, #141, #150)

## Context

Seven open issues report bugs, missing features, and inconsistencies in the `setup-linters` plugin. All stem from real-world usage on Swift and Go projects. The issues fall into three categories: a new language reference (Swift), tool version/configuration mismatches, and CI workflow generation gaps. Fixing them together makes sense because several issues overlap (e.g., #125 and #126 both create the Swift reference; #140 and #150 both touch CI templates).

## Changes

### 1. Add Swift language reference (#125, #126, #141)

Create `plugins/setup-linters/skills/setup-linters/references/languages/swift.md` covering:

- **Tools**: SwiftLint (linter) + SwiftFormat (formatter)
- **Install**: `brew install swiftlint swiftformat`
- **Config files**: `.swiftlint.yml`, `.swiftformat`, `.swift-version`
- **`.swiftlint.yml` template**: Include `trailing_comma: mandatory_comma: true` to resolve the SwiftLint/SwiftFormat trailing comma conflict (#126)
- **`.swiftformat` template**: Sensible defaults
- **Makefile targets**:
  - `lint`: `swiftlint lint --strict` and `swiftformat --lint .`
  - `lint-fix`: `swiftlint lint --fix` followed by `swiftlint lint --strict` (#141), then `swiftformat .`
  - `fmt`: `swiftformat .`
- **Notes section**: Document the trailing comma conflict and its resolution (#126), document the lint-fix verification pattern (#141)

### 2. Update SKILL.md detection table (#125)

File: `plugins/setup-linters/skills/setup-linters/SKILL.md`

Add Swift row to the detection table (Step 1):

```text
| `Package.swift`, `*.xcodeproj`, `*.xcworkspace` | Swift |
```

### 3. Update checklist.md (#125)

File: `plugins/setup-linters/skills/setup-linters/references/checklist.md`

Add Swift row to the Language-Specific Linters table:

```text
| Swift | SwiftLint + SwiftFormat | `brew install swiftlint swiftformat` | `.swiftlint.yml`, `.swiftformat` | `lint`, `fmt`, `lint-fix` | `./languages/swift.md` |
```

### 4. Update Go CI template to golangci-lint-action v9 (#117)

File: `plugins/setup-linters/skills/setup-linters/references/tools/github-actions-ci.md`

- Change `golangci/golangci-lint-action@v6` to `golangci/golangci-lint-action@v9` in the Go template (line 64)
- Change `golangci/golangci-lint-action@v6` to `golangci/golangci-lint-action@v9` in the Combined Multi-Language Workflow (line 271)

File: `plugins/setup-linters/skills/setup-linters/references/languages/go.md`

- Add a note in the Notes section: "The `fmt` subcommand (`golangci-lint fmt`) and the `formatters` config section are golangci-lint v2 features. The CI action `golangci/golangci-lint-action@v9` natively supports v2."

### 5. Pin npx tool versions in CI workflows (#140)

File: `plugins/setup-linters/skills/setup-linters/references/tools/github-actions-ci.md`

Pin all `npx` invocations to specific versions. Look up current latest stable versions during implementation for:

- `markdownlint-cli2` (currently unpinned: `npx markdownlint-cli2`)
- `prettier` (currently unpinned in non-JS template: `npx prettier --check .`)
- `knip` (currently unpinned: `npx knip`)
- `stylelint` (currently unpinned: `npx stylelint`)
- `@taplo/cli` (currently unpinned: `npx @taplo/cli fmt --check`)

Format: `npx tool@X.Y.Z` (exact version).

Also add a note in the Notes section: "Pin all npx tool versions to exact versions for CI reproducibility. Update versions periodically."

### 6. Update Prettier Makefile guidance (#128)

File: `plugins/setup-linters/skills/setup-linters/references/tools/prettier.md`

- Add a "Makefile Targets" section (currently missing) recommending `prettier --write .` and `prettier --check .` with a note that `.prettierignore` handles exclusions
- Add a note: "Prefer `prettier --write .` over explicit glob patterns (e.g., `**/*.md **/*.yml`) in Makefile targets. Explicit patterns error when no files match. The `.prettierignore` file already handles exclusions, and Prettier respects `.gitignore` by default."

### 7. Add CI tool dependency verification to SKILL.md (#150)

File: `plugins/setup-linters/skills/setup-linters/SKILL.md`

Add a verification sub-step to Step 8 ("Set Up CI"):

> **Tool dependency verification**: For every tool referenced in Makefile targets, confirm the CI workflow includes a corresponding setup/install step. Common tool-to-action mappings:
>
> | Tool          | CI Setup                                                                  |
> | ------------- | ------------------------------------------------------------------------- |
> | shfmt         | `mfinelli/setup-shfmt@v4` or `go install mvdan.cc/sh/v3/cmd/shfmt@latest` |
> | shellcheck    | `ludeeus/action-shellcheck@master`                                        |
> | golangci-lint | `golangci/golangci-lint-action@v9`                                        |
> | swiftlint     | `brew install swiftlint` (macOS runner)                                   |
> | swiftformat   | `brew install swiftformat` (macOS runner)                                 |
> | hadolint      | `hadolint/hadolint-action@v3.1.0`                                         |
> | actionlint    | `raven-actions/actionlint@v2`                                             |

### 8. Add Swift CI template (#125)

File: `plugins/setup-linters/skills/setup-linters/references/tools/github-actions-ci.md`

Add a Swift section to the Per-Language Templates:

```yaml
### Swift

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

Add Swift to the Caching Strategies table (no caching needed, or note that SPM caching can be added if build step exists).

### 9. Bump version

- `plugins/setup-linters/.claude-plugin/plugin.json`: `1.2.2` -> `1.3.0` (minor: new Swift language support)
- `.claude-plugin/marketplace.json`: update setup-linters version to `1.3.0`

## Files to modify

1. **New**: `plugins/setup-linters/skills/setup-linters/references/languages/swift.md`
1. `plugins/setup-linters/skills/setup-linters/SKILL.md` (detection table + Step 8 verification)
1. `plugins/setup-linters/skills/setup-linters/references/checklist.md` (Swift row)
1. `plugins/setup-linters/skills/setup-linters/references/tools/github-actions-ci.md` (golangci-lint v9, Swift template, pinned npx versions)
1. `plugins/setup-linters/skills/setup-linters/references/languages/go.md` (v2 note)
1. `plugins/setup-linters/skills/setup-linters/references/tools/prettier.md` (Makefile targets section)
1. `plugins/setup-linters/.claude-plugin/plugin.json` (version bump)
1. `.claude-plugin/marketplace.json` (version bump)

## Verification

1. Read all modified files end-to-end to confirm consistency
1. Run `check-versions` skill to verify plugin version matches marketplace version
1. Confirm every issue's specific concern is addressed:
   - #117: Go CI template uses `golangci-lint-action@v9`, go.md notes v2
   - #125: Swift reference exists with SwiftLint + SwiftFormat, detection table and checklist updated, CI template added
   - #126: `.swiftlint.yml` template includes `trailing_comma: mandatory_comma: true`
   - #128: Prettier reference recommends `prettier --write .` for Makefile targets
   - #140: All npx invocations in CI templates are pinned to exact versions
   - #141: Swift lint-fix target runs `--fix` then `--strict`
   - #150: Step 8 includes tool dependency verification table
