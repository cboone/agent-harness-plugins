# Update Go Templates for go-ci.yml v2

## Context

`go-ci.yml` v2 in `cboone/gh-actions` removes the `use-makefile` and `build-flags` inputs and requires all consuming repos to provide Makefile targets (`vet`, `test`, `lint`, `build`, `fmt`). This plan addresses three related issues:

- **#199**: Update scaffold-go-cli Makefile template (`test` target needs `-v -race` flags)
- **#200**: Update all CI workflow templates from `@v1` to `@v2`, remove `use-makefile` input
- **#201**: Document Makefile target conventions in write-go-code and scaffold-go-cli

## Changes

### 1. scaffold-go-cli (2.3.0 -> 2.4.0) [#199, #200, #201]

**File**: `plugins/scaffold-go-cli/commands/scaffold-go-cli.md`

Makefile template (lines 466-467):

- Change `go test ./...` to `go test -v -race ./...`

CI workflow template (lines 665-682):

- Change `go-ci.yml@v1` to `go-ci.yml@v2`
- Remove `use-makefile: true` line
- Update notes: remove `use-makefile` explanation, note that v2 always uses Makefile targets

Makefile notes section (lines 495-502):

- Add note about Makefile target conventions for go-ci.yml v2

### 2. setup-ci (1.1.0 -> 1.2.0) [#200]

**File**: `plugins/setup-ci/commands/setup-ci.md`

Step 3 / Makefile check text (line 67):

- Remove `use-makefile: true` mention, update to say v2 always uses Makefile targets

Go CLI CI template (lines 167-182):

- Change `go-ci.yml@v1` to `go-ci.yml@v2`
- Remove `use-makefile: true` line
- Update notes: remove `use-makefile` explanation

Go Library CI template (lines 222-244):

- Change both `go-ci.yml@v1` to `go-ci.yml@v2`

Multi-language template (lines 776-779):

- Change `go-ci.yml@v1` to `go-ci.yml@v2`
- Remove `use-makefile: true` line

Go CLI Makefile template (lines 851-852):

- Change `go test ./...` to `go test -v -race ./...`

Go Library Makefile template (lines 905-907, 928-930):

- Change `fmt` from `go fmt ./...` to check pattern: `@test -z "$$(gofmt -l .)" || { gofmt -l . && exit 1; }`
- Update `fmt` comment from "Format code" to "Check formatting (exits non-zero if files need formatting)"
- Add `format` target: `go fmt ./...` (write-mode formatting for local development)
- Change `test` from `go test -race ./...` to `go test -v -race ./...`
- Update help text to reflect `fmt` is now a check and add `format` entry

### 3. scaffold-go-library (1.4.0 -> 1.5.0) [#200]

**File**: `plugins/scaffold-go-library/commands/scaffold-go-library.md`

CI workflow template (lines 672, 680):

- Change both `go-ci.yml@v1` to `go-ci.yml@v2`

Makefile template (lines 341-343, 367-369):

- Change `fmt` from `go fmt ./...` to check pattern
- Update `fmt` comment from "Format code" to "Check formatting (exits non-zero if files need formatting)"
- Add `format` target: `go fmt ./...`
- Change `test` from `go test -race ./...` to `go test -v -race ./...`
- Update help text to reflect `fmt` is now a check and add `format` entry
- Add `format` to `.PHONY` declarations

### 4. setup-linters (1.6.0 -> 1.6.1) [#200]

**File**: `plugins/setup-linters/skills/setup-linters/references/tools/github-actions-ci.md`

- Line 100: Change `go-ci.yml@v1` to `go-ci.yml@v2`
- Line 461: Change `go-ci.yml@v1` to `go-ci.yml@v2`

### 5. lint-and-fix (1.3.1 -> 1.3.2) [#200]

**File**: `plugins/lint-and-fix/skills/lint-and-fix/SKILL.md`

- Line 64: Change `go-ci.yml@v1` to `go-ci.yml@v2`
- Line 221: Change `go-ci.yml@v1` to `go-ci.yml@v2`

### 6. write-go-code (1.0.2 -> 1.1.0) [#201]

**File**: `plugins/write-go-code/skills/write-go-code/SKILL.md`

- Add `references/comprehensive/makefile-conventions.md` to the Reference Navigation deep dives list

**New file**: `plugins/write-go-code/skills/write-go-code/references/comprehensive/makefile-conventions.md`

- Document `make fmt` must be a format check (not write), with the pattern
- Document `make lint` must run only `golangci-lint run ./...` (not an umbrella)
- Document `make format` is the write-mode target name
- Document `make lint-all` is the umbrella lint target name
- Document all five required targets: `vet`, `test`, `lint`, `build`, `fmt`

### 7. Version bumps

Update `plugin.json` and matching `marketplace.json` entries:

| Plugin              | Old   | New   | Bump  | Reason                                  |
| ------------------- | ----- | ----- | ----- | --------------------------------------- |
| scaffold-go-cli     | 2.3.0 | 2.4.0 | minor | New test flags, CI v2, conventions docs |
| setup-ci            | 1.1.0 | 1.2.0 | minor | CI v2, updated Makefile templates       |
| scaffold-go-library | 1.4.0 | 1.5.0 | minor | CI v2, fmt check pattern                |
| write-go-code       | 1.0.2 | 1.1.0 | minor | New Makefile conventions reference      |
| setup-linters       | 1.6.0 | 1.6.1 | patch | Version reference update only           |
| lint-and-fix        | 1.3.1 | 1.3.2 | patch | Version reference update only           |

Marketplace `metadata.version` stays at 1.23.0 (no plugins added or removed).

## Commit Strategy

Use `--commit-per-change` with one commit per issue:

1. `feat: update Makefile template with -v -race test flags (#199)` (scaffold-go-cli Makefile + setup-ci Go CLI Makefile)
1. `feat: update Go CI workflow templates for go-ci.yml@v2 (#200)` (all @v1 -> @v2 changes, use-makefile removal, library Makefile fmt updates across all six plugins)
1. `docs: document Makefile target conventions for go-ci.yml v2 (#201)` (write-go-code new reference file, scaffold-go-cli notes)
1. `chore: bump versions for go-ci.yml v2 migration` (all version bumps in plugin.json and marketplace.json)

## Verification

1. Search for any remaining `go-ci.yml@v1` references: `grep -r "go-ci.yml@v1"` should return zero results
1. Search for any remaining `use-makefile` references: `grep -r "use-makefile"` should return zero results
1. Search for any remaining `build-flags` references: `grep -r "build-flags"` should return zero results (already zero)
1. Verify all `plugin.json` versions match their `marketplace.json` entries: run `check-versions` skill
1. Verify the new `makefile-conventions.md` file is referenced from `SKILL.md`
