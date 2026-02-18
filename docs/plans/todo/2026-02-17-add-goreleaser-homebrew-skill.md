# Plan: Add GoReleaser Homebrew Skill

## Context

Issue #27 requests a new skill that adds GoReleaser configuration and a GitHub Actions release workflow to an **existing** Go CLI project, with Homebrew tap publishing. This pattern is virtually identical across 4 repos (jm, gh-problemas, bopca, right-round) and is error-prone to configure manually. Unlike `scaffold-go-cli` (which creates new projects from scratch), this skill targets projects that already have Go code, a `go.mod`, and possibly a Makefile.

The skill introduces one new pattern not present in any reference repo or in `scaffold-go-cli`: **conventional commit changelog grouping** (using `changelog.groups` instead of simple `sort+filters`).

## Files to Create (6 new files)

### 1. `plugins/add-goreleaser-homebrew/.claude-plugin/plugin.json`

Standard plugin manifest at version `1.0.0`. Keywords: `github-actions`, `go`, `golang`, `goreleaser`, `homebrew`.

### 2. `plugins/add-goreleaser-homebrew/skills/add-goreleaser-homebrew/SKILL.md`

Main skill file following the `scaffold-go-cli` workflow pattern (numbered `### N. Step Name` subsections). Workflow steps:

1. **Verify the Project** -- Check `go.mod` exists; read module path; check for existing `.goreleaser.yml`/`.goreleaser.yaml` and `.github/workflows/release.yml`; warn if either exists and ask whether to overwrite
2. **Detect User Identity** -- `gh api user -q .login` and `git config user.name` (same pattern as `scaffold-go-cli`)
3. **Gather Project Information** -- Short description (infer from README first), Homebrew dependencies
4. **Detect Project Features** -- Three conditionals:
   - **Completions**: check for `cmd/completion.go` or grep for `"completion"` cobra command registration
   - **Man pages**: check for `cmd/man.go` or grep for `"man"` cobra command, and for `cobra/doc` or `mango` imports
   - **macOS-only**: check for GOOS=darwin constraints in Makefile or build tags, or ask the user
   - Present detected features for user confirmation
5. **Determine ldflags Target** -- Find where `var version` is declared (typically `main` or `cmd` package) and detect the correct `-X` path
6. **Determine Build Entry Point** -- Check if `main()` is in the repo root or a subdirectory like `./cmd/project-name`
7. **Generate .goreleaser.yml** -- Base template from `./references/goreleaser.md` + conditional modifications from `./references/conditional-features.md`
8. **Generate Release Workflow** -- Template from `./references/release-workflow.md` (use `macos-latest` if macOS-only)
9. **Optionally Update Makefile** -- Append `release-dry-run` target from `./references/makefile-target.md`
10. **Verify Configuration** -- Run `goreleaser check` if installed
11. **Summary** -- List created/modified files, applied conditionals, remind about `HOMEBREW_TAP_TOKEN` secret

### 3. `plugins/add-goreleaser-homebrew/skills/add-goreleaser-homebrew/references/goreleaser.md`

Base `.goreleaser.yml` template (GoReleaser v2). Key contents:

- `version: 2`
- `builds:` with `CGO_ENABLED=0`, cross-platform (`linux`, `darwin`, `windows` / `amd64`, `arm64`), ldflags `-s -w -X`
- `archives:` with `tar.gz` default, `zip` for Windows, `name_template` with version
- `checksum:` with `checksums.txt`
- `release:` with `prerelease: auto`
- **`changelog:` with conventional commit groups** -- This is the new pattern:
  - Features (feat), Bug Fixes (fix), Performance (perf), Refactoring (refactor), Documentation (docs), Build (build/ci), Other (catch-all order 999)
  - Filters excluding `chore:`, `test:`, `style:`
- `brews:` with `GITHUB-USERNAME/homebrew-tap`, `HOMEBREW_TAP_TOKEN`, `Formula` directory, basic version test
- Placeholders: `PROJECT-NAME`, `PROJECT-DESCRIPTION`, `GITHUB-USERNAME`
- `## Notes` section explaining each design decision (following `scaffold-go-cli/references/goreleaser.md` convention)

### 4. `plugins/add-goreleaser-homebrew/skills/add-goreleaser-homebrew/references/release-workflow.md`

Release workflow template using latest action versions:

- `actions/checkout@v6` with `fetch-depth: 0`
- `actions/setup-go@v6` with `go-version-file: go.mod`
- `goreleaser/goreleaser-action@v6` with `version: "~> v2"`, `args: release --clean`
- `GITHUB_TOKEN` and `HOMEBREW_TAP_TOKEN` environment variables
- Default `runs-on: ubuntu-latest`
- A `## macOS-Only Variant` section showing `runs-on: macos-latest`
- `## Notes` section

### 5. `plugins/add-goreleaser-homebrew/skills/add-goreleaser-homebrew/references/makefile-target.md`

Small snippet for the optional `release-dry-run` target:

```makefile
release-dry-run: ## Run GoReleaser in dry-run mode (no publish)
	goreleaser release --snapshot --clean
```

With notes on how to merge into an existing Makefile (add to `.PHONY`, append the target).

### 6. `plugins/add-goreleaser-homebrew/skills/add-goreleaser-homebrew/references/conditional-features.md`

Documents all three conditional feature modifications with detection logic and YAML/Ruby snippets to apply:

- **Shell Completions**: Detection heuristics + `generate_completions_from_executable(bin/"BINARY", "completion")` in brews install
- **Man Pages**: Detection heuristics + `before.hooks` (`go run . man man/man1`), `archives.files` mapping, `man1.install Dir["man/man1/*"]` in brews install
- **macOS Only**: Detection heuristics + restrict `goos: [darwin]`, optionally `goarch: [arm64]`, `custom_block: depends_on :macos`, `runs-on: macos-latest` in workflow
- **Combining Features**: How to merge multiple conditionals into a single config (with bopca as a real-world example)

## Files to Modify (3 existing files)

### 7. `.claude-plugin/marketplace.json`

- Bump `metadata.version` from `"1.9.0"` to `"1.10.0"` (adding a plugin)
- Insert new entry as **first** in `plugins` array (alphabetically before `address-review`)
- Entry fields: `category: "productivity"`, `version: "1.0.0"`, matching description/keywords from `plugin.json`

### 8. `README.md`

**ToC** (line 9-10 area): Insert before the current first Workflow entry. "Address Review" gets a `∙` prefix:

```markdown
<br>Workflow:
[Add GoReleaser Homebrew](#add-goreleaser-homebrew)
∙ [Address Review](#address-review)
```

**Description section** (before line 48 "### Address Review"): Insert new H3 section:

```markdown
### Add GoReleaser Homebrew

Add GoReleaser configuration and a GitHub Actions release workflow to an
existing Go CLI project with Homebrew tap publishing to
`cboone/homebrew-tap`. Detects project features (shell completions, man page
generation, macOS-only constraints) and generates appropriate configuration
with conventional commit changelog grouping. Optionally adds a
`release-dry-run` Makefile target.

> **Trigger:** `/add-goreleaser-homebrew`
```

### 9. `CLAUDE.md`

Insert new entry in the directory tree as the **first** plugin under `plugins/` (alphabetically before `address-review/`):

```text
    ├── add-goreleaser-homebrew/     # GoReleaser + Homebrew tap setup skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   └── skills/
    │       └── add-goreleaser-homebrew/
    │           ├── SKILL.md
    │           └── references/
    │               ├── conditional-features.md
    │               ├── goreleaser.md
    │               ├── makefile-target.md
    │               └── release-workflow.md
```

## Key Design Decisions

1. **Conventional commit changelog groups** (new pattern): The issue explicitly asks for this. None of the 4 reference repos currently use it -- they use simple `sort+filters` or `github-native`. This skill introduces a better pattern that groups commits under headings (Features, Bug Fixes, Refactoring, etc.).

2. **4 reference files in a single directory** (not 6): Conditional features (completions, man pages, macOS-only) are documented together in one file since they modify the same goreleaser config and are interrelated. The base templates (goreleaser, workflow, Makefile target) get their own files.

3. **Detection-then-confirm workflow**: The skill detects existing project features automatically, then presents findings for user confirmation before generating configs. This avoids both false positives and unnecessary questioning.

4. **`go-version-file: go.mod`** (not hardcoded): Best practice for the release workflow, matching `scaffold-go-cli` convention.

5. **Latest action versions** (`@v6` for checkout, setup-go, goreleaser-action): Consistent with the most recent reference repo configs.

## Implementation Order

Implement in this order, committing at each logical boundary:

1. Create `plugin.json`
2. Create reference files (`goreleaser.md`, `release-workflow.md`, `makefile-target.md`, `conditional-features.md`)
3. Create `SKILL.md`
4. Update `marketplace.json`
5. Update `README.md`
6. Update `CLAUDE.md`

## Verification

1. Run `/check-versions` to verify version consistency between `plugin.json` and `marketplace.json`
2. Run `/lint-and-fix` to check formatting
3. Verify alphabetical ordering in marketplace.json, README ToC, README descriptions, and CLAUDE.md tree
4. Verify all placeholder names are consistent across templates (`PROJECT-NAME`, `GITHUB-USERNAME`, etc.)
5. Verify YAML templates are syntactically valid
