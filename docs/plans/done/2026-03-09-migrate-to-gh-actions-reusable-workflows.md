# Migrate Workflow Templates to cboone/gh-actions Reusable Workflows

Issue: #197

## Context

Multiple plugins generate GitHub Actions workflow templates that reference third-party actions directly (golangci-lint-action, goreleaser-action, gitleaks-action, etc.). The `cboone/gh-actions` repository now provides reusable workflows that wrap these tools with pinned versions, SHA-256 checksum verification, and centralized maintenance. This migration eliminates version drift, reduces template complexity, and improves supply-chain security.

## Design Decisions

### 1. Parallel jobs to single reusable workflow

Current Go templates use 3-5 parallel jobs. A reusable workflow call is a single job with sequential steps. This tradeoff is accepted per the issue's design intent ("Generated workflow files shrink from 50-100+ lines to a single `uses:` call with a few inputs"). Each template's Notes section will document this tradeoff.

### 2. Go Library version matrix

Use two reusable workflow calls: one for `MINIMUM-GO-VERSION` (runs all checks) and one for `stable` (tests only). If `go-ci.yml` does not support two calls in the same workflow, file a companion issue on `cboone/gh-actions`.

### 3. Makefile references

Current Go CLI templates use `make test`, `make vet`, `make fmt`. The reusable workflows run Go commands directly. Templates no longer reference `make` targets in CI. The Makefile templates remain unchanged (they are for local development).

### 4. Gitleaks org vs personal

Consolidate personal and organization templates into one using `secrets: inherit`. The GITLEAKS_LICENSE secret is forwarded when present. Update documentation to note that org repos still need to set the secret.

### 5. macOS variant for release workflows

If `go-release.yml` supports a `runs-on` input, use it. Otherwise, keep the macOS-only variant as an inline template with a note.

### 6. Copilot instructions in scaffold plugins

Replace `golangci-lint-action handles its own caching` and `go-version-file: go.mod is valid` with a note about `cboone/gh-actions` managing tool versions internally.

## Changes by Plugin

### 1. setup-ci (`plugins/setup-ci/commands/setup-ci.md`)

Version: 1.0.2 -> 1.1.0

**Go CLI template (lines 135-221):** Replace 3-job (test, lint, vulncheck) template with:

```yaml
jobs:
  ci:
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@v1
    with:
      go-version-file: go.mod
      run-lint: false
      run-format-check: true
```

Keep the `on:` triggers, `concurrency:`, and `permissions:` blocks unchanged in the calling workflow.

**Go Library template (lines 238-361):** Replace 5-job template with two calls:

```yaml
jobs:
  ci-minimum:
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@v1
    with:
      go-version: "MINIMUM-GO-VERSION"
      run-lint: true
      run-format-check: true
      run-build: true

  ci-stable:
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@v1
    with:
      go-version: "stable"
```

**Shell template (lines 821-872):** Replace `ludeeus/action-shellcheck@master` + `mfinelli/setup-shfmt@v4` with:

```yaml
jobs:
  lint:
    uses: cboone/gh-actions/.github/workflows/shell-lint.yml@v1
```

**Multi-language template (lines 886-996):** Replace Go portion with reusable workflow call; keep JS portion inline.

**JS/TS, Python, Rust, Ruby templates:** Stay as-is (no gh-actions equivalents).

**Other updates:**

- Update step 4 prose to reference reusable workflows instead of `actions/checkout@v6`
- Remove the Makefile dependency note (line 67) since reusable workflows run Go commands directly
- Update Notes sections throughout to remove third-party action references and explain centralized maintenance

### 2. setup-secret-scanning (`plugins/setup-secret-scanning/commands/setup-secret-scanning.md`)

Version: 2.0.2 -> 2.1.0

**Gitleaks templates (lines 115-180):** Consolidate personal/org into one template:

```yaml
jobs:
  scan:
    uses: cboone/gh-actions/.github/workflows/secret-scan.yml@v1
    with:
      tool: gitleaks
    secrets: inherit
```

Keep the `on:` triggers (push, pull_request, workflow_dispatch, schedule).

**TruffleHog template (lines 199-228):** Replace with:

```yaml
jobs:
  scan:
    uses: cboone/gh-actions/.github/workflows/secret-scan.yml@v1
    with:
      tool: trufflehog
    secrets: inherit
```

**Workflow changes:**

- Remove step 5's TruffleHog version lookup (reusable workflow handles versioning)
- Simplify step 3 (Determine Repository Ownership): keep the question for documentation purposes but note that the workflow template is the same for both; org repos just need the GITLEAKS_LICENSE secret
- Update all Notes sections to remove references to `gitleaks/gitleaks-action@v2`, `trufflesecurity/trufflehog@VERSION`, `fetch-depth: 0`

### 3. scaffold-go-cli (`plugins/scaffold-go-cli/commands/scaffold-go-cli.md`)

Version: 2.2.0 -> 2.3.0

**CI template (lines 632-721):** Replace 3-job template with:

```yaml
jobs:
  ci:
    uses: cboone/gh-actions/.github/workflows/go-ci.yml@v1
    with:
      go-version-file: go.mod
      run-lint: true
      run-format-check: true
```

**Release template (lines 738-773):** Replace with:

```yaml
jobs:
  release:
    uses: cboone/gh-actions/.github/workflows/go-release.yml@v1
    with:
      go-version-file: go.mod
    secrets:
      HOMEBREW_TAP_TOKEN: ${{ secrets.HOMEBREW_TAP_TOKEN }}
```

**Copilot instructions (step 19, lines 206-213):**

- Remove `go-version-file: go.mod is valid` note
- Remove `golangci-lint-action handles its own caching` note
- Add: `cboone/gh-actions reusable workflows manage tool versions, caching, and installation internally. Do not suggest replacing reusable workflow calls with inlined third-party actions.`

### 4. scaffold-go-library (`plugins/scaffold-go-library/commands/scaffold-go-library.md`)

Version: 1.3.0 -> 1.4.0

**CI template (lines 640-763):** Replace 5-job template with two calls (same pattern as setup-ci Go Library).

**Release template (lines 781-820):** Replace with:

```yaml
jobs:
  release:
    uses: cboone/gh-actions/.github/workflows/go-release.yml@v1
    secrets: inherit
```

No `HOMEBREW_TAP_TOKEN` needed for libraries.

**Copilot instructions (step 23, lines 213-220):** Same changes as scaffold-go-cli.

### 5. add-goreleaser-homebrew (`plugins/add-goreleaser-homebrew/commands/add-goreleaser-homebrew.md`)

Version: 2.0.0 -> 2.1.0

**Release template (lines 270-305):** Replace with:

```yaml
jobs:
  release:
    uses: cboone/gh-actions/.github/workflows/go-release.yml@v1
    with:
      go-version-file: go.mod
    secrets:
      HOMEBREW_TAP_TOKEN: ${{ secrets.HOMEBREW_TAP_TOKEN }}
```

**macOS-only variant (lines 308-318):** If `go-release.yml` supports `runs-on`, use `runs-on: macos-latest`. Otherwise, keep inline template with a note explaining reusable workflows cannot customize the runner.

### 6. setup-linters (`plugins/setup-linters/skills/setup-linters/references/tools/github-actions-ci.md`)

Version: 1.5.0 -> 1.6.0

**Go template (lines 96-112):** Replace with `go-ci.yml` reusable workflow call.

**Shell template (lines 258-305):** Replace with `shell-lint.yml` reusable workflow call.

**Actionlint step (lines 369-371):** Replace `raven-actions/actionlint@v2` with `github-lint.yml` reusable workflow call.

**cspell step (lines 419-423):** Replace `streetsidesoftware/cspell-action@v6` with `text-lint.yml` reusable workflow call (with `run-cspell: true`).

**Text lint tools (markdownlint, prettier, yamllint):** Replace standalone `npx`/`pipx` commands with `text-lint.yml` references where applicable.

**Combined multi-language workflow (lines 426-481):** Update Go portion to reusable workflow; keep JS inline.

**Version fixes:** Update remaining inline `actions/checkout@v4` to `@v6` and `actions/setup-go@v5` to `@v6`.

**JS/TS, Python, Rust, Ruby, Swift templates:** Stay as-is (no gh-actions equivalents). Fix `@v4` checkout references to `@v6`.

### 7. lint-and-fix (`plugins/lint-and-fix/skills/lint-and-fix/SKILL.md`)

Version: 1.3.0 -> 1.3.1

**CI workflow tool detection (line 220):** Update the error handling note to mention both `cboone/gh-actions` and legacy third-party action references.

**CI Workflow Detection section (lines 57-83):** Add awareness that reusable workflow calls (`uses: cboone/gh-actions/.github/workflows/*.yml@v1`) indicate CI tools are in use but are not locally executable. Note which tools they imply but skip adding them as CI-specific tools.

## Version Summary

| Plugin                  | Current | New   | Bump  |
| ----------------------- | ------- | ----- | ----- |
| setup-ci                | 1.0.2   | 1.1.0 | minor |
| setup-secret-scanning   | 2.0.2   | 2.1.0 | minor |
| scaffold-go-cli         | 2.2.0   | 2.3.0 | minor |
| scaffold-go-library     | 1.3.0   | 1.4.0 | minor |
| add-goreleaser-homebrew | 2.0.0   | 2.1.0 | minor |
| setup-linters           | 1.5.0   | 1.6.0 | minor |
| lint-and-fix            | 1.3.0   | 1.3.1 | patch |

Marketplace `metadata.version` stays at 1.23.0 (no plugins added or removed).

## Implementation Order

1. lint-and-fix (smallest change, patch-level)
1. setup-secret-scanning (straightforward, no matrix complexity)
1. add-goreleaser-homebrew (one template)
1. setup-ci: Go CLI template, then Go Library, then Shell
1. scaffold-go-cli (CI + release + copilot instructions)
1. scaffold-go-library (CI + release + copilot instructions)
1. setup-linters (most templates, version fixes)
1. Version bumps across all plugin.json and marketplace.json

## Commit Strategy

One commit per logical change (per the issue checklist items), using `feat(<scope>):` prefix since the issue is classified as `enhancement`.

## Items to Verify During Implementation

1. Confirm `go-ci.yml` supports two calls in the same workflow (for Go Library matrix)
1. Confirm `go-release.yml` supports `runs-on` input (for macOS-only variant)
1. Confirm `secrets: inherit` works for forwarding GITLEAKS_LICENSE
1. Confirm `go-ci.yml` runs standard Go commands (not `make` targets)
1. Confirm `text-lint.yml` covers markdownlint, prettier, cspell, and yamllint

If any of these cannot be confirmed from documentation, verify by reading the reusable workflow source files in the `cboone/gh-actions` repository.

## Verification

After all changes:

1. Run `check-versions` skill to verify version consistency
1. Review each modified template for correct YAML syntax (proper indentation, `with:` and `secrets:` under `uses:`)
1. Verify no third-party actions remain that have gh-actions replacements (grep for the eliminated action names)
1. Verify all `on:` trigger blocks are preserved in calling workflows
1. Confirm the issue checklist items are all addressed
