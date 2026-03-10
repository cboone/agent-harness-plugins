# Make add-scrut-cli-tests Language-Agnostic

## Context

The `add-scrut-cli-tests` skill currently assumes it is setting up tests for a Go CLI project. It checks for `go.mod`, derives binary names from Go module paths, hardcodes `actions/setup-go` in the CI template, and references `scaffold-go-cli` in error messages. Scrut itself is completely language-agnostic: it tests CLI binaries by running commands and comparing output. The skill should reflect this and work for any CLI project, including Swift, Rust, Python, Ruby, and shell scripts.

The companion `write-scrut-tests` skill has minor Go-specific wording in its reference guide and keywords that should also be cleaned up.

## Plan

### 1. SKILL.md: Replace Go-specific logic with language detection

**File:** `plugins/add-scrut-cli-tests/skills/add-scrut-cli-tests/SKILL.md`

**Frontmatter:** Change "Go CLI project" to "CLI project" in description. Remove "for a Go project" from trigger phrases.

**Prerequisites:** Replace "A Go CLI project with a `Makefile` and a `build` target that produces a binary" with a general statement: "A CLI project that produces a binary or has an executable entry point." Keep the CI workflow line. Remove the Makefile as a hard prerequisite (it becomes recommended, and the skill can create one).

**Step 1 (Verify the Project):** Replace the `go.mod` check with a language detection step using a manifest-to-language table:

| Marker(s)                        | Language |
| -------------------------------- | -------- |
| `go.mod`                         | Go       |
| `Package.swift`                  | Swift    |
| `Cargo.toml`                     | Rust     |
| `pyproject.toml`, `setup.py`     | Python   |
| `Gemfile`, `*.gemspec`           | Ruby     |
| Executable scripts (no manifest) | Shell    |

If no manifest is found, ask the user. Keep the existing `tests/scrut/` check.

**Step 2 (Gather Project Information):** Replace Go-specific binary name derivation with per-language detection:

- **Go:** Makefile `-o` flag or last segment of module path in `go.mod`
- **Swift:** executable target names in `Package.swift` or Makefile
- **Rust:** `[[bin]]` entries or `[package].name` in `Cargo.toml`
- **Python:** `[project.scripts]` in `pyproject.toml`
- **Ruby:** `executables` in gemspec or files in `bin/`/`exe/`
- **Shell:** the script filename itself

Add a "build required" field: yes for compiled languages (Go, Swift, Rust), no for interpreted languages (Python, Ruby, Shell).

**Step 5 (Add Makefile Targets):** Add handling for projects without a Makefile: offer to create a minimal one. For interpreted languages, remove the `build` dependency from `test-scrut` and `test-scrut-update` targets.

**Step 6 (Update CI Workflow):** Replace "Detect the Go version from the existing workflow's `go-version` field" with "Copy the language setup step(s) from the existing CI workflow." This is better than maintaining per-language CI templates because:

- Projects vary in how they configure language versions, caching, and matrix builds
- The existing workflow already has the correct setup
- It is what the current skill conceptually does for Go (copies the `go-version`)

**Error Handling:** Replace `go.mod`-specific abort messages with generic "no recognized project manifest found, ask the user" logic. Replace `scaffold-go-cli` suggestion with language-appropriate suggestion (e.g., suggest `scaffold-go-cli` only if the project is Go).

### 2. ci-job.md: Generic language setup placeholder

**File:** `plugins/add-scrut-cli-tests/skills/add-scrut-cli-tests/references/ci-job.md`

Replace the hardcoded `actions/setup-go@v6` step with a `LANGUAGE_SETUP_STEPS` placeholder. Update the placeholder table to replace `GO_VERSION` with `LANGUAGE_SETUP_STEPS` and add notes listing common setup actions by language:

- **Go:** `actions/setup-go`
- **Swift:** preinstalled on macOS runners; setup action or install step for Ubuntu
- **Rust:** `dtolnay/rust-toolchain`
- **Python:** `actions/setup-python`
- **Ruby:** `ruby/setup-ruby`
- **Shell:** no setup step needed

Replace "Match the `go-version`..." note with "Match the `runs-on` value and language setup steps to the project's existing CI configuration."

### 3. makefile-targets.md: Conditional build dependency note

**File:** `plugins/add-scrut-cli-tests/skills/add-scrut-cli-tests/references/makefile-targets.md`

Add a note: "For interpreted languages (shell scripts, Python, Ruby) where no build step is needed, remove the `: build` dependency from `test-scrut` and `test-scrut-update`. The binary path points directly to the executable script."

### 4. Plugin metadata (add-scrut-cli-tests)

**`plugins/add-scrut-cli-tests/.claude-plugin/plugin.json`:**

- Description: "Go CLI project" -> "CLI project"
- Keywords: remove "go" and "golang", keep `["cli", "scrut", "testing"]`
- Version: `1.1.0` -> `1.2.0` (minor: new language support capability, not breaking)

**`plugins/add-scrut-cli-tests/README.md`:**

- Line 3: "Go CLI project" -> "CLI project"
- Line 20: "existing Go CLI project" -> "existing CLI project"
- See Also: remove "Write Go Code" link. Change "Scaffold Go CLI" parenthetical to "(includes build targets compatible with this skill)".

### 5. Plugin metadata (write-scrut-tests)

**`plugins/write-scrut-tests/.claude-plugin/plugin.json`:**

- Keywords: remove "go" and "golang", keep `["cli", "scrut", "style", "testing"]`
- Version: `1.0.1` -> `1.0.2` (patch: keyword/wording cleanup)

**`plugins/write-scrut-tests/skills/write-scrut-tests/references/SCRUT.md`:**

- Line 3: "production Go CLI repositories" -> "production CLI repositories"
- Line 337: "Error messages from Cobra-based CLIs" -> "Error messages from CLI frameworks (e.g., Cobra for Go, Swift Argument Parser, clap for Rust)"

**`plugins/write-scrut-tests/README.md`:**

- Line 38: "Go CLI project" -> "CLI project"
- Line 39: remove the "Write Go Code" link

### 6. Registry and root README

**`.claude-plugin/marketplace.json`:**

- `add-scrut-cli-tests` entry: description "CLI project", keywords remove "go"/"golang", version `1.2.0`
- `write-scrut-tests` entry: keywords remove "go"/"golang", version `1.0.2`
- `metadata.version`: no change (no plugins added or removed)

**`README.md` (root):**

- Line 149: "Go CLI project" -> "CLI project"

## Files unchanged

These files are already language-agnostic and need no modifications:

- `plugins/add-scrut-cli-tests/skills/add-scrut-cli-tests/references/help-test.md`
- `plugins/add-scrut-cli-tests/skills/add-scrut-cli-tests/references/version-test.md`
- `plugins/add-scrut-cli-tests/skills/add-scrut-cli-tests/references/test-format.md`
- `plugins/write-scrut-tests/skills/write-scrut-tests/SKILL.md`

## Verification

1. Read through every modified file and confirm no Go-specific language remains (except where contextually appropriate, e.g., the per-language detection table listing Go as one option)
1. Invoke `/check-versions` to verify version consistency across `plugin.json` and `marketplace.json`
1. Run `/lint-and-fix` to check formatting
1. Invoke `/add-scrut-cli-tests` in a Go project to confirm Go detection still works as before
1. Invoke `/add-scrut-cli-tests` in a non-Go project (Swift or shell) to confirm the new language detection works
