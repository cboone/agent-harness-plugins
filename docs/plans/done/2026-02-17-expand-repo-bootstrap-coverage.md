# Expand scaffold-new-repo Project Type Coverage

## Context

The scaffold-new-repo skill currently supports 6 project types (Go CLI, Go library, Shell, JavaScript, Ruby, Generic), but the Ruby template is broken (uses `*.code-workspace`, a VS Code artifact, not Ruby) and several popular languages are missing entirely. This plan fixes Ruby, enriches JavaScript, adds 5 new language types, and introduces a dynamic GitHub fallback for any unlisted language.

## Changes

### 1. Fix Ruby template and detection heuristic

**File:** `plugins/scaffold-new-repo/skills/scaffold-new-repo/references/gitignore.md` (Ruby section)

Replace `*.code-workspace` with proper Ruby entries curated from GitHub's Ruby.gitignore:

```gitignore
*.gem
*.rbc
.bundle/
vendor/bundle
pkg/
coverage/
spec/reports/
.byebug_history
```

**File:** `plugins/scaffold-new-repo/skills/scaffold-new-repo/SKILL.md` (line 26)

Change detection heuristic from `*.code-workspace` to `*.gem` or `.bundle/`.

### 2. Enrich JavaScript template

**File:** `references/gitignore.md` (JavaScript section)

Add to existing `node_modules/` and `*.tgz`:

```gitignore
*.tsbuildinfo
coverage/
dist/
.next
.nuxt
*.log
```

### 3. Add 5 new project types

**File:** `references/gitignore.md` -- add sections before Generic, in this order: Python, Rust, Swift, Pascal, Nim.

| Type       | Curated entries                                                                                                                  | Source                                                        |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Python** | `__pycache__/`, `*.pyc`, `*.pyo`, `.venv/`, `dist/`, `build/`, `*.egg-info/`, `.pytest_cache/`, `*.egg`, `.coverage`, `htmlcov/` | GitHub Python.gitignore                                       |
| **Rust**   | `target/`, `*.pdb`, `**/*.rs.bk`                                                                                                 | GitHub Rust.gitignore                                         |
| **Swift**  | `xcuserdata/`, `.build/`, `*.ipa`, `*.dSYM.zip`, `*.dSYM`, `Carthage/Build/`, `Package.resolved`                                 | GitHub Swift.gitignore                                        |
| **Pascal** | `*.o`, `*.ppu`, `*.compiled`, `*.exe`, `*.dll`, `*.so`, `lib/`, `backup/`, `*.lps`, `*.bak`                                      | Free Pascal / Lazarus conventions (no GitHub template exists) |
| **Nim**    | `nimcache/`, `nimblecache/`, `htmldocs/`                                                                                         | GitHub Nim.gitignore (used verbatim)                          |

Each template prefixed with the common block (`.DS_Store`, `.env`, `.claude/settings.local.json`).

**File:** `references/readme.md` -- add installation placeholders (same order):

| Type       | Install placeholder                    |
| ---------- | -------------------------------------- |
| **Python** | `uv run PROJECT-NAME`                  |
| **Rust**   | `cargo install PROJECT-NAME`           |
| **Swift**  | `Package.swift` dependency declaration |
| **Pascal** | `git clone` (same as Shell)            |
| **Nim**    | `nimble install PROJECT-NAME`          |

**File:** `SKILL.md` -- update project type options list (line 29) to include all 11 types.

### 4. Update detection heuristics with priority ordering

**File:** `SKILL.md` (lines 23-28)

Replace current heuristic list with priority-ordered checks (first match wins):

1. `go.work` or `*.test` → Go CLI / Go library
1. `node_modules/` → JavaScript
1. `__pycache__/` or `*.pyc` → Python
1. `*.gem` or `.bundle/` → Ruby
1. `nimcache/` → Nim
1. `*.ppu` or `*.compiled` → Pascal
1. `xcuserdata/` alone, or `.build/` + `*.ipa` together → Swift
1. `target/` with no other language markers matched → Rust
1. Minimal or macOS-only entries → Shell or Generic

Key conflict resolutions:

- Go vs Pascal `*.exe` overlap: Go detected by `go.work`/`*.test`, not `*.exe` alone
- Rust `target/` ambiguity: lowest-priority detection, only when nothing else matched
- Swift `.build/` ambiguity: requires pairing with `*.ipa` (or unambiguous `xcuserdata/`)

### 5. Add GitHub fallback for unlisted language types

**File:** `SKILL.md` -- new subsection within Step 6 (Generate .gitignore)

When the user explicitly specifies a type NOT in our curated list:

1. Fetch `https://raw.githubusercontent.com/github/gitignore/main/{Language}.gitignore` via WebFetch (title-cased language name)
1. If successful: merge fetched entries with common entries, avoiding duplicates
1. If 404 or failure: fall back to Generic, inform the user

This fallback is ONLY for user-specified types, never for auto-detection.

Update error handling section (line 138) to reference the fallback.

### 6. Version bumps

| File                                                                  | Current | New       |
| --------------------------------------------------------------------- | ------- | --------- |
| `plugins/scaffold-new-repo/.claude-plugin/plugin.json`                | 1.0.1   | 1.1.0     |
| `.claude-plugin/marketplace.json` (scaffold-new-repo entry, line 192) | 1.0.1   | 1.1.0     |
| `.claude-plugin/marketplace.json` (metadata.version, line 5)          | 1.7.0   | no change |

Minor bump: new capabilities added to existing plugin.

### 7. Update README.md description

**File:** `README.md` (line 113)

Update the project type list in the Scaffold New Repo description to include the expanded set and mention the GitHub fallback.

## File List

1. `plugins/scaffold-new-repo/skills/scaffold-new-repo/references/gitignore.md`
1. `plugins/scaffold-new-repo/skills/scaffold-new-repo/references/readme.md`
1. `plugins/scaffold-new-repo/skills/scaffold-new-repo/SKILL.md`
1. `plugins/scaffold-new-repo/.claude-plugin/plugin.json`
1. `.claude-plugin/marketplace.json`
1. `README.md`

## Verification

- Read each modified file after editing to confirm formatting and no duplicate entries
- Verify all 11 project types appear consistently across SKILL.md, gitignore.md, and readme.md
- Verify plugin.json version matches marketplace.json entry version
- Confirm no detection heuristic markers overlap between language types
