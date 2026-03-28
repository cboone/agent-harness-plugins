# Add Rust CLI Scaffolding and Enhance Rust Support

Issue: #224

## Context

While bootstrapping [cboone/ke](https://github.com/cboone/ke) (a Rust CLI project), significant manual work was needed that the Go equivalents handle automatically. This plan brings Rust support closer to feature parity with Go across the plugin ecosystem: a new scaffold-rust-cli command, enhanced CI/Makefile templates, setup-linters improvements, and bootstrap-project overlap rules.

The ke repository's [bootstrap branch](https://github.com/cboone/ke/compare/main...chore/bootstrap-repo) serves as the canonical reference for what scaffold-rust-cli should generate.

## Scope

Six sub-tasks from the issue. Sub-task 4 (scaffold-rust-library) is deferred to a future issue.

| # | Sub-task                                                   | Priority | Status   |
| - | ---------------------------------------------------------- | -------- | -------- |
| 1 | Add `scaffold-rust-cli` command                            | High     | To do    |
| 2 | Enhance `setup-ci` Rust templates                          | Medium   | To do    |
| 3 | Add platform-aware CI variants                             | Medium   | To do    |
| 4 | Update `bootstrap-project` overlap rules                   | Medium   | To do    |
| 5 | Add cargo-deny and typos to `setup-linters` Rust reference | Lower    | To do    |
| 6 | Add `scaffold-rust-library` command                        | Lower    | Deferred |

## Sub-task 1: Add `scaffold-rust-cli` command

### New plugin: `plugins/scaffold-rust-cli/`

**`.claude-plugin/plugin.json`**

```json
{
  "author": { "name": "Christopher Boone" },
  "description": "Scaffold a complete Rust CLI project with Cargo, cargo-deny, cargo-nextest, git-cliff, GitHub Actions CI/CD, and Makefile.",
  "homepage": "https://github.com/cboone/cboone-cc-plugins",
  "keywords": ["cargo", "cli", "rust", "scaffolding"],
  "license": "MIT",
  "name": "scaffold-rust-cli",
  "repository": "https://github.com/cboone/cboone-cc-plugins",
  "commands": "./commands",
  "version": "1.0.0"
}
```

**`commands/scaffold-rust-cli.md`** (core workflow, ~300 lines)

Frontmatter: `disable-model-invocation: true`, `argument-hint: "[project-name]"`

23-step workflow mirroring scaffold-go-cli:

1. **Gather Project Information**: name (kebab-case), description, include clap? (CLI argument parsing), macOS-only project? (affects CI runners and release targets)
2. **Detect User Identity**: `gh api user -q .login`, `git config user.name`
3. **Verify Target Directory**: same pattern as Go (use current if named correctly and empty, else create subdirectory)
4. **Initialize Git**: skip if already in a repo
5. **Generate Cargo.toml**: from template, replace PROJECT-NAME, PROJECT-DESCRIPTION, GITHUB-USERNAME, COPYRIGHT-HOLDER. Add `clap = { version = "4", features = ["derive"] }` if clap selected.
6. **Generate src/main.rs**: choose template based on clap selection (simple vs clap-derive skeleton)
7. **Generate rust-toolchain.toml**: pin stable channel with clippy + rustfmt components
8. **Generate rustfmt.toml**: edition 2024, max_width 100
9. **Generate deny.toml**: license allowlist (MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Unicode-3.0), vulnerability auditing
10. **Generate typos.toml**: spell checking with project name in extend-words
11. **Generate cliff.toml**: git-cliff conventional commit changelog config
12. **Generate Makefile**: enhanced 16-target version from ke reference
13. **Generate .gitignore**: Rust-specific entries from ke reference
14. **Generate CI Workflow**: choose cross-platform (ubuntu-latest) or macOS-only template based on step 1. 8 jobs: test (nextest), lint, format, build, deny, audit, typos, test-scrut
15. **Generate Release Workflow**: choose cross-platform (linux + darwin targets) or macOS-only (darwin-only). Replace PROJECT-NAME.
16. **Generate LICENSE**: MIT template, replace YEAR and COPYRIGHT-HOLDER
17. **Generate README.md**: Rust-specific template with Homebrew, cargo install, and release install methods
18. **Generate CHANGELOG.md**: standard Keep a Changelog template
19. **Create Directory Stubs**: `docs/plans/{todo,done}`, `tests/`
20. **Verify the Build**: `cargo build`
21. **Create Initial Commit**: `git add -A && git commit -S -m "feat: scaffold Rust CLI project"`
22. **Update Copilot Instructions**: append Rust-specific PR review entries if `.github/copilot-instructions.md` exists
23. **Summary**: list all files, note optional features, suggest next steps (`/setup-installers`, `/add-community-files`, `make help`)

Error handling section covering `cargo build` failures, existing Rust files, missing Rust toolchain.

Reference Templates section at bottom with `@${CLAUDE_PLUGIN_ROOT}/references/...` includes.

### Reference template files (16 files in `references/`)

| File | Content | Placeholders |
| ---- | ------- | ------------ |
| `cargo-toml.md` | Cargo.toml with full [package] metadata | PROJECT-NAME, PROJECT-DESCRIPTION, GITHUB-USERNAME, COPYRIGHT-HOLDER |
| `main-rs.md` | Minimal `fn main() { println!("Hello, world!"); }` | None |
| `main-rs-with-clap.md` | clap::Parser skeleton with Args struct | PROJECT-NAME, PROJECT-DESCRIPTION |
| `rust-toolchain.md` | Stable toolchain with clippy + rustfmt | None |
| `rustfmt.md` | Edition 2024, max_width 100 | None |
| `deny.md` | License + vulnerability auditing config | None |
| `typos.md` | Spell checking config with extend-words | PROJECT-NAME |
| `cliff.md` | git-cliff conventional commit config | None |
| `makefile.md` | 16-target Makefile (test/lint/fmt/build/deny/audit/typos/format/format-check/lint-md/lint-actions/test-scrut/test-scrut-update/test-all/changelog/clean/help) | None |
| `gitignore.md` | System + agent + secrets + Rust-specific entries | None |
| `ci-workflow.md` | 8-job CI on ubuntu-latest (test with nextest, lint, format, build, deny, audit, typos, test-scrut) | None |
| `ci-workflow-macos-only.md` | Same 8 jobs on macos-latest | None |
| `release-workflow.md` | Cross-platform release (linux-gnu + darwin targets, 4 matrix entries) | PROJECT-NAME |
| `release-workflow-macos-only.md` | macOS-only release (darwin targets only, 2 matrix entries) | PROJECT-NAME |
| `license.md` | MIT license text | YEAR, COPYRIGHT-HOLDER |
| `readme.md` | README with Homebrew, cargo install, release install | PROJECT-NAME, PROJECT-DESCRIPTION, GITHUB-USERNAME |

### `README.md`

Per-plugin README following scaffold-go-cli's pattern: title, description, type (Command), trigger (`/scaffold-rust-cli`), installation, what it does, usage examples, see also links.

### Design decisions

- **cliff.toml included**: It is the Rust equivalent of GoReleaser's changelog feature. The ke repo uses it, and the Makefile `changelog` target calls `git cliff`. The issue body lists it among key files.
- **Separate macOS-only CI/release templates** (4 files instead of 2): The differences are pervasive (every job's `runs-on` changes), so separate templates are cleaner than conditional logic. scaffold-go-cli does not need this because GoReleaser handles platform variation internally.
- **clap as optional feature**: Mirrors the Go scaffold's Viper question. clap is the standard CLI parsing library but not every project needs it at scaffold time.
- **No Homebrew formula generation**: `setup-installers` already handles this. The summary directs users to it.
- **16-target Makefile includes cross-language targets**: Matches ke reference. Targets like `format` (Prettier), `lint-md`, `lint-actions` degrade gracefully if tools are not yet installed and integrate with `setup-linters` output.

## Sub-task 2: Enhance `setup-ci` Rust templates

### Files to modify

**`plugins/setup-ci/references/ci-rust.md`**

- Update header: "7 parallel jobs: test, lint, format, build, deny, audit, typos"
- Update test job to use nextest via `taiki-e/install-action@nextest`
- Add deny job: `taiki-e/install-action@cargo-deny`, `cargo deny check`
- Add audit job: `taiki-e/install-action@cargo-audit`, `cargo audit`
- Add typos job: `crate-ci/typos@v1`
- Note: deny and audit jobs do not need Rust cache (they install standalone binaries). Typos job does not need Rust toolchain at all.
- Update Notes section with tool explanations and action pinning conventions

**`plugins/setup-ci/references/makefile-rust.md`**

- Update .PHONY to include: deny, audit, typos, changelog
- Update test target to use nextest with cargo test fallback: `@command -v cargo-nextest >/dev/null 2>&1 && cargo nextest run || cargo test`
- Add 4 targets: deny (`cargo deny check`), audit (`cargo audit`), typos (`typos`), changelog (`git cliff -o CHANGELOG.md`)

**`plugins/setup-ci/.claude-plugin/plugin.json`**: bump version 1.5.0 -> 1.6.0

## Sub-task 3: Add platform-aware CI variants

Add a "macOS-Only Projects" section to the Notes in `plugins/setup-ci/references/ci-rust.md` (modified in sub-task 2). Content:

- Explain when to swap all `runs-on: ubuntu-latest` to `runs-on: macos-latest`
- List indicators: `[target.'cfg(target_os = "macos")']` dependencies, imports of security_framework/core_foundation/cocoa/objc crates, macOS-only compilation
- Note that macOS runners are more expensive

No changes to setup-ci command logic. The template guidance is sufficient for the user or agent to apply.

## Sub-task 4: Update `bootstrap-project` overlap rules

### Files to modify

**`plugins/bootstrap-project/skills/bootstrap-project/references/overlap-rules.md`**

Add to Decision Table (after scaffold-go-library rows):

| Tool A | Tool B | Action | Reason |
| ------ | ------ | ------ | ------ |
| `scaffold-rust-cli` | `setup-ci` | Skip | `scaffold-rust-cli` generates CI workflow and Makefile |
| `scaffold-rust-cli` | `setup-linters` | Scope down | Rust linting configured; add cross-language tools |
| `scaffold-rust-cli` | `scaffold-new-repo` | Scope down | Generates LICENSE, README, .gitignore; still run for agent config files |

Add to Applicability Rules table:

| `scaffold-rust-cli` | Rust CLI project (Cargo.toml + src/main.rs or `[[bin]]` target) |

Add Scope-Down Details sections for `setup-linters after scaffold-rust-cli` and `scaffold-new-repo after scaffold-rust-cli`.

**`plugins/bootstrap-project/skills/bootstrap-project/SKILL.md`**

- Add Rust sub-detection to the Detect Project Type table: `Cargo.toml` + (`src/main.rs` or `[[bin]]` in Cargo.toml) = Rust CLI, `Cargo.toml` without binary targets = Rust library
- Update "Detect Existing Infrastructure" table: add `rustfmt.toml`, `deny.toml`, `typos.toml`, `cliff.toml` as markers
- Add `scaffold-rust-cli` to key overlap rules (step 3) and execution order (step 5)
- Add `scaffold-rust-cli` to the commands list in step 5

**`plugins/bootstrap-project/.claude-plugin/plugin.json`**: bump version 1.1.0 -> 1.2.0, add "rust" to keywords

## Sub-task 5: Add cargo-deny and typos to `setup-linters` Rust reference

### Files to modify

**`plugins/setup-linters/skills/setup-linters/references/languages/rust.md`**

- Add cargo-deny and typos to Tools section
- Add install instructions for both (cargo install + CI action references)
- Add deny.toml config template (from ke reference)
- Add typos.toml config template
- Add `cargo deny check` and `typos` to Commands section
- Add `deny` and `typos` Makefile targets
- Add notes about when each tool is valuable

**`plugins/setup-linters/skills/setup-linters/references/checklist.md`**

Update the Rust row:

- Tools: `clippy + rustfmt + cargo-deny + typos`
- Install: `clippy/rustfmt built-in; cargo install --locked cargo-deny; cargo install typos-cli`
- Config: `rustfmt.toml`, `deny.toml`, `typos.toml` (optional)
- Scripts: `cargo clippy`, `cargo fmt`, `cargo deny check`, `typos`

**`plugins/setup-linters/skills/setup-linters/SKILL.md`**

- Add `deny.toml` and `typos.toml`/`_typos.toml` to the "Detect Existing Linters" table (step 2)
- Add cargo-deny and typos to the tool dependency verification table (step 9)

**`plugins/setup-linters/skills/setup-linters/references/tools/github-actions-ci.md`**

- Add cargo-deny and typos steps to the Rust CI section

**`plugins/setup-linters/.claude-plugin/plugin.json`**: bump version 1.7.0 -> 1.8.0

## Cross-cutting changes

### `README.md` (root)

- Add Scaffold Rust CLI entry to the Commands > Scaffolding section (after Scaffold Go Library)
- Add entry to the ToC under Commands > Scaffolding

### `.claude-plugin/marketplace.json`

- Add scaffold-rust-cli plugin entry (version 1.0.0, category: productivity)
- Update setup-ci version: 1.5.0 -> 1.6.0
- Update setup-linters version: 1.7.0 -> 1.8.0
- Update bootstrap-project version: 1.1.0 -> 1.2.0, add "rust" to keywords
- Bump metadata.version: 1.25.0 -> 1.26.0

### `CLAUDE.md`

- Add `scaffold-rust-cli` to the Structure tree under `plugins/`

## Versioning summary

| Plugin | Current | New | Bump | Reason |
| ------ | ------- | --- | ---- | ------ |
| scaffold-rust-cli | new | 1.0.0 | new | New plugin |
| setup-ci | 1.5.0 | 1.6.0 | minor | New CI jobs (nextest, deny, audit, typos) |
| setup-linters | 1.7.0 | 1.8.0 | minor | New Rust tools (cargo-deny, typos) |
| bootstrap-project | 1.1.0 | 1.2.0 | minor | Rust CLI detection and overlap rules |
| marketplace | 1.25.0 | 1.26.0 | minor | New plugin added |

## Implementation order

Dependencies flow top-down:

1. Sub-tasks 2 + 3 (enhance setup-ci templates, add macOS notes) -- modifies same files
2. Sub-task 5 (setup-linters Rust enhancements) -- independent, can parallel with #1
3. Sub-task 1 (scaffold-rust-cli) -- the new plugin, largest chunk of work
4. Sub-task 4 (bootstrap-project overlap rules) -- depends on scaffold-rust-cli existing
5. Cross-cutting changes (marketplace.json, README, CLAUDE.md) -- after all plugins are updated

Commit strategy: one commit per logical unit (sub-task or closely related group).

## Verification

1. **Version consistency**: run `/check-versions` to verify all version numbers match between plugin.json files and marketplace.json
2. **Template content**: compare scaffold-rust-cli reference templates against the ke repository's bootstrap branch files to confirm accuracy
3. **Overlap rules**: verify the bootstrap-project overlap rules match the patterns established by scaffold-go-cli and scaffold-go-library
4. **README completeness**: verify the root README includes the new scaffold-rust-cli entry with correct formatting
5. **Marketplace registration**: verify the new plugin entry in marketplace.json has all required fields
