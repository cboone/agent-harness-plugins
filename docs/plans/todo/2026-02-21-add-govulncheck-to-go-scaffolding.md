# Add govulncheck to Go scaffolding CI workflows

## Context

Neither Go scaffolding skill (`scaffold-go-cli`, `scaffold-go-library`) includes dependency vulnerability scanning in its CI workflow template. Projects scaffolded from these templates have no automated way to detect known vulnerabilities in their Go dependencies.

The `govulncheck` tool from the Go team (`golang.org/x/vuln/cmd/govulncheck`) scans Go binaries and source for known vulnerabilities listed in the Go vulnerability database. Adding it to the CI templates means every scaffolded project gets vulnerability scanning from day one.

### Approach: DIY (run govulncheck directly) rather than a GitHub Action wrapper

Three options were evaluated:

1. **golang/govulncheck-action** (official, v1.0.4): Extensive configuration, SARIF output support, but adds a third-party composite action to templates that currently use only `actions/checkout` and `actions/setup-go`.
2. **imjasonh/govulncheck-action** (community, v0.1): Nice PR annotations, but pre-1.0 and community-maintained.
3. **DIY**: `go install golang.org/x/vuln/cmd/govulncheck@latest && govulncheck ./...`. No action dependency. Same scanning engine as option 1. Consistent with the existing pattern of running tools directly.

The DIY approach wins because:

- Both templates follow a "checkout, setup-go, run command" pattern. The CLI template uses zero third-party actions; the library template's only one is `golangci-lint-action`.
- The scanning engine is identical regardless of wrapper. `govulncheck` itself is the Go team's official tool.
- No SARIF/Code Scanning integration is needed for starter templates. Projects that want it can add it later.
- `go install` with `@latest` is the established pattern in the library Makefile's `tools` target.

## Changes

### 1. CI workflow template: scaffold-go-cli

**File:** `plugins/scaffold-go-cli/skills/scaffold-go-cli/references/ci-workflow.md`

Two changes: (a) normalize existing jobs to use explicit step names and add a `permissions` block, and (b) add the new `vulncheck` job.

The existing `test` and `lint` jobs have unnamed `checkout` and `setup-go` steps. Normalize them to match the library template's explicit style. Also add `permissions: contents: read` (least privilege) and descriptive job-level `name:` fields.

Complete updated workflow YAML:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version-file: go.mod

      - name: Run tests
        run: make test

  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version-file: go.mod

      - name: Run vet
        run: make vet

      - name: Check formatting
        run: make fmt

  vulncheck:
    name: Vulnerability check
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version-file: go.mod

      - name: Install govulncheck
        run: go install golang.org/x/vuln/cmd/govulncheck@latest

      - name: Run govulncheck
        run: govulncheck ./...
```

Update the Notes section to reflect the new structure (three parallel jobs, explicit step names, permissions block).

### 2. CI workflow template: scaffold-go-library

**File:** `plugins/scaffold-go-library/skills/scaffold-go-library/references/ci-workflow.md`

Add a `vulncheck` job following the library template's conventions (explicit step names, `"MINIMUM-GO-VERSION"` for non-matrix jobs):

```yaml
  vulncheck:
    name: Vulnerability check
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "MINIMUM-GO-VERSION"

      - name: Install govulncheck
        run: go install golang.org/x/vuln/cmd/govulncheck@latest

      - name: Run govulncheck
        run: govulncheck ./...
```

Update the Notes section: "Four parallel jobs" becomes "Five parallel jobs".

### 3. Makefile template: scaffold-go-cli

**File:** `plugins/scaffold-go-cli/skills/scaffold-go-cli/references/makefile.md`

- Add `vuln` to the `.PHONY` line
- Add a `vuln` target:

  ```makefile
  vuln: ## Run govulncheck
  	govulncheck ./...
  ```

### 4. Makefile template: scaffold-go-library

**File:** `plugins/scaffold-go-library/skills/scaffold-go-library/references/makefile.md`

- Add `vuln` target (alphabetically between `vet` and the end):

  ```makefile
  .PHONY: vuln
  vuln:
  	govulncheck ./...
  ```

- Add `vuln` to the `all` target chain: `all: fmt vet lint vuln test build`
- Add govulncheck to the `tools` target:

  ```makefile
  tools:
  	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
  	go install github.com/goreleaser/goreleaser/v2@latest
  	go install golang.org/x/vuln/cmd/govulncheck@latest
  ```

- Update the `help` target to include the `vuln` entry

### 5. Version bumps

Adding vulnerability scanning is a new capability (minor bump).

- `plugins/scaffold-go-cli/.claude-plugin/plugin.json`: 1.1.0 to 1.2.0
- `plugins/scaffold-go-library/.claude-plugin/plugin.json`: 1.0.0 to 1.1.0
- `.claude-plugin/marketplace.json`: update both entries to match
- Marketplace `metadata.version`: do NOT bump (no plugins added or removed)

### 6. Run `check-versions` skill

Verify all version numbers are correct and consistent.

## Verification

1. Read back all modified files and confirm the YAML is valid and follows each template's conventions
2. Run `check-versions` to verify version consistency
3. Visually confirm:
   - CLI template: three parallel jobs (test, lint, vulncheck), `permissions: contents: read`, explicit step names, `go-version-file: go.mod`
   - Library template: five parallel jobs (test, lint, build, format, vulncheck), `permissions: contents: read`, explicit step names
   - CLI Makefile: `vuln` target present, listed in `.PHONY` and `help`
   - Library Makefile: `vuln` target present, in `all` chain, govulncheck in `tools`, listed in `help`
