# Add lint-and-fix Skill Plugin

## Context

Issue #13 requests a `lint-and-fix` skill based on analysis of ~7,350 session history entries showing ~140 occurrences of lint/format/fix commands. The user frequently runs eslint, shellcheck, markdownlint, shfmt, prettier, and knip across projects, often combining linting with committing. This skill automates the detect → run → report → fix → commit workflow.

## Approach

Pure skill plugin (SKILL.md only, no hooks or scripts). The SKILL.md guides Claude through detecting linters by checking for config files, running them with auto-fix flags, and resolving remaining issues. This matches the pattern of `commit`, `pr`, and `address-review`.

## Files to Create

### 1. `plugins/lint-and-fix/.claude-plugin/plugin.json`

Standard plugin metadata. Fields alphabetized per convention. Version `1.0.0`. Category will be `code-quality` in marketplace.

### 2. `plugins/lint-and-fix/skills/lint-and-fix/SKILL.md`

The main deliverable. Structured as:

- **Frontmatter**: `name` and `description` (with trigger phrases)
- **Options section**: `--commit`/`--no-commit`, `--tool <name>`, `--check`
- **Workflow** (7 steps):
  1. **Detect available tools** — Check for config files (eslint, prettier, markdownlint, shellcheck, shfmt, knip, package.json scripts, project lint scripts). Build a tool list with detection table mapping config files → tool → fix command → check command.
  1. **Present detected tools** — Show table before running.
  1. **Run each tool** — Execute sequentially with auto-fix flags. Tool-specific exit code handling. Record results.
  1. **Report results** — Summary table (tool, status, fixed count, remaining count).
  1. **Fix remaining issues** — Read errors, understand the specific rule, edit code to comply, re-run tool to verify.
  1. **Final verification** — Re-run all tools in check mode to confirm clean state.
  1. **Commit (optional)** — Controlled by `--commit`/`--no-commit` flags, or ask. Uses `style:` conventional commit type.
- **Error Handling**: No tools detected, tool not installed, execution failures, conflicting tools (package.json scripts vs standalone configs).

## Files to Modify

### 3. `.claude-plugin/marketplace.json`

- Bump `metadata.version` from `1.7.0` → `1.8.0` (minor bump for adding a plugin)
- Insert new entry alphabetically between `create-worktree-from-issue` (line 109) and `merge-main` (line 110)
- Entry fields: `author`, `category` (`code-quality`), `description`, `homepage`, `keywords`, `license`, `name`, `repository`, `source`, `version` — all matching plugin.json where shared

### 4. `README.md`

- **ToC** (line 14): Insert `∙ [Lint and Fix](#lint-and-fix)` between "Create Worktree from Issue" and "Merge Main" in the Workflow subcategory
- **Description section** (between line 81 and line 82): Insert new H3 section with description paragraph and `> **Trigger:** /lint-and-fix` blockquote

### 5. `CLAUDE.md`

- Insert directory tree entry alphabetically between `create-worktree-from-issue/` block (ending line 57) and `merge-main/` block (starting line 58)

## Verification

1. Confirm `plugin.json` fields are alphabetized and `name` matches directory name
1. Confirm `marketplace.json` entry matches `plugin.json` on all shared fields
1. Confirm `marketplace.json` metadata version is `1.8.0`
1. Confirm SKILL.md frontmatter has exactly `name` and `description`
1. Confirm README ToC follows one-link-per-line format with `∙` prefix
1. Confirm README description section is in alphabetical order
1. Confirm CLAUDE.md tree entry uses correct indentation and is alphabetical
1. Validate marketplace.json is valid JSON
