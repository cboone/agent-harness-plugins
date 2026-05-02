---
name: clean-up-agent-config
description: >-
  Review and reorganize AI coding agent configuration and instruction files
  across Claude Code, Codex, Copilot, and OpenCode.
---

# Agent Config Cleanup

Review, consolidate, and organize AI coding agent configuration and instruction files across four tools: Claude Code, OpenAI Codex, GitHub Copilot (CLI agent and code review), and OpenCode.

## Reference Documents

Consult the reference files in this skill's `references/` directory for detailed information about each tool's file formats, precedence rules, and unique capabilities:

- `references/agent-instruction-files.md` -- CLAUDE.md, AGENTS.md, copilot-instructions.md, SKILL.md comparison
- `references/agent-config-files.md` -- settings.json, config.toml, opencode.json, VS Code settings comparison

Read these references before starting work. They contain tool-specific details about file precedence, loading behavior, and cross-tool compatibility that inform every decision in this workflow.

---

## Target Structure

The goal is a hub-and-spoke model: shared instructions in one canonical file, tool-specific configuration in each tool's hidden directory.

### Instruction files (the hub)

Pick **one** scoped-instructions layout per repo. The two layouts below are mutually exclusive alternatives, not files that should coexist.

**Flat layout** (convenient for one or two scoped files):

```text
repo/
+-- AGENTS.md                              # Single source of truth (all tools)
+-- CLAUDE.md -> AGENTS.md                 # Symlink for Claude Code
+-- .claude/
|   +-- rules/
|       +-- *.md                           # Claude-specific rules (auto-loaded)
+-- .github/
    +-- copilot-instructions.md            # Copilot repo-wide review rules
    +-- *.instructions.md                  # Copilot path-scoped rules
```

**Nested layout** (scales better when there are many scoped files, or to keep `.github/` uncluttered):

```text
repo/
+-- AGENTS.md                              # Single source of truth (all tools)
+-- CLAUDE.md -> AGENTS.md                 # Symlink for Claude Code
+-- .claude/
|   +-- rules/
|       +-- *.md                           # Claude-specific rules (auto-loaded)
+-- .github/
    +-- copilot-instructions.md            # Copilot repo-wide review rules
    +-- instructions/
        +-- *.instructions.md              # Copilot path-scoped rules
```

Both are read by Copilot and both honor `applyTo` frontmatter. Choose based on how many scoped files the repo needs and stick with that choice; do not mix the two.

### Config files (the spokes)

```text
repo/
+-- .mcp.json                              # Shared MCP servers (Claude Code, OpenCode)
+-- opencode.json                          # OpenCode project config (if used)
+-- .claude/
|   +-- settings.json                      # Team-shared: permissions, hooks, env vars
|   +-- settings.local.json                # Personal: model, telemetry (gitignored)
+-- .codex/
    +-- config.toml                        # Codex project config (if used)
```

### What goes where

| Content type                                   | Location                                                                                 | Reason                                                                    |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Project overview, tech stack, commands         | `AGENTS.md`                                                                              | Read by all four tools                                                    |
| Directory-scoped conventions                   | Subdirectory `AGENTS.md` (Codex, Copilot) and `CLAUDE.md` or symlink per subdir (Claude) | Scoped by directory; Claude requires `CLAUDE.md` in each scoped directory |
| Claude-specific (MCP hints, subagent patterns) | `.claude/rules/*.md`                                                                     | Auto-loaded, Claude-only                                                  |
| Copilot code review rules                      | `.github/copilot-instructions.md`                                                        | Copilot code review agent                                                 |
| File-type-specific review rules                | `.github/*.instructions.md` or `.github/instructions/*.instructions.md`                  | Copilot's `applyTo` glob scoping                                          |
| Team permissions and hooks                     | `.claude/settings.json`                                                                  | Committed, shared with team                                               |
| Personal model/telemetry/privacy               | `.claude/settings.local.json`                                                            | Gitignored, personal                                                      |
| MCP servers (team)                             | `.mcp.json` at project root                                                              | Committed, shared                                                         |
| MCP servers (personal)                         | `.claude/settings.local.json`                                                            | Gitignored                                                                |
| Codex sandbox/approval policy                  | `.codex/config.toml`                                                                     | Codex-specific                                                            |
| OpenCode model/instruction paths               | `opencode.json`                                                                          | OpenCode-specific                                                         |

---

## Workflow

### Phase 1: Audit

Scan the repository for all known agent-related files.

#### Instruction files to check

- `AGENTS.md` (root and subdirectories)
- `AGENTS.override.md` (root and subdirectories)
- `CLAUDE.md` (root and subdirectories)
- `.claude/CLAUDE.md`
- `.claude/rules/*.md`
- `.github/copilot-instructions.md`
- `.github/*.instructions.md` (flat path-scoped layout)
- `.github/instructions/*.instructions.md` (nested path-scoped layout)
- `.github/prompts/*.prompt.md`
- `.github/chatmodes/*.chatmode.md`
- `.github/agents/*.agent.md`

#### Config files to check

- `.claude/settings.json`
- `.claude/settings.local.json`
- `.mcp.json`
- `.codex/config.toml`
- `opencode.json`

#### Also check

- **Symlinks:** Run `ls -la CLAUDE.md AGENTS.md` to detect symlinks and their targets.
- **Gitignore:** Verify `.claude/settings.local.json` is gitignored (Claude Code does this automatically, but confirm).
- **Project characteristics:** Note the primary languages, directory structure, build tools, and monorepo indicators. These inform AGENTS.md content and Copilot path-scoped instructions.

Report which files exist, which are missing, which are symlinks, and what each file contains at a high level.

### Phase 2: Analyze

Read each found file and categorize its contents into:

1. **Shared instructions** -- project overview, tech stack, commands, coding conventions that all tools should know
1. **Claude-specific instructions** -- MCP server usage hints, subagent patterns, `@import` references, Claude-only tool restrictions
1. **Copilot-specific instructions** -- code review rules, PR description conventions, `excludeAgent` scoping
1. **Tool config** -- permissions, hooks, model settings, environment variables, sandbox policies
1. **Personal config** -- settings that belong in gitignored files, not shared config
1. **Duplicated content** -- instructions repeated across multiple files
1. **Misplaced content** -- team settings in personal files or personal settings in team files

#### Settings split analysis (Claude Code)

For `.claude/settings.json` and `.claude/settings.local.json`, specifically classify each setting:

**Belongs in settings.json (team-shared, committed):**

- `$schema` reference
- `permissions.allow` rules for team-standard tool patterns
- `permissions.deny` rules for protecting sensitive paths
- `hooks` definitions (pre/post tool use enforcement)
- `env` vars for team conventions (`attribution`, survey suppression, etc.)
- `attribution` settings

**Belongs in settings.local.json (personal, gitignored):**

- Model override env vars (`ANTHROPIC_MODEL`, `CLAUDE_CODE_MAX_TURNS`)
- Telemetry/privacy env vars (`DISABLE_TELEMETRY`, `DISABLE_ERROR_REPORTING`)
- Personal MCP servers in `mcpServers`
- Personal permission overrides
- `spinnerTipsEnabled` and similar personal preferences
- Experimental settings being tested before proposing to the team

Note: Claude Code writes to `settings.local.json` by default when users change settings interactively. This means team-appropriate settings often end up in the local file and need to be moved to `settings.json`.

#### Scoped Copilot instructions analysis

For each `.github/*.instructions.md` and `.github/instructions/*.instructions.md` file, check:

1. **Frontmatter present.** Each scoped file MUST start with YAML frontmatter containing `applyTo: "<glob>"`. Flag files missing the frontmatter or the `applyTo` key.
1. **Top-level heading matches scope.** Each scoped file should have a top-level heading naming what it scopes to (e.g., `# Lean PR Review Instructions`, `# TypeScript Frontend Instructions`). Flag files with no top-level heading or one that does not reflect the scope.
1. **Glob is non-empty.** Run a glob match against the repo (e.g., via `git ls-files` or a Glob tool call) to confirm the `applyTo` pattern matches at least one tracked file. Flag scoped files whose glob matches nothing as **stale**: either the code they targeted has been removed, the glob was mistyped, or the file was copied from another repo without being updated.
1. **No silent overlap with sibling scoped files.** Compare each `applyTo` glob to every other scoped file's `applyTo`. If two scoped files match the same file (e.g., one has `**/*.ts` and another has `**/*.tsx`, but a `.ts` file matches the first only -- fine; but two files both globbing `**/*.lean` is a conflict). Flag overlaps where two files would both apply to the same source file without a clear separation of concerns.
1. **Cross-references with the general file.** The general `.github/copilot-instructions.md` should mention the scoped files (so a contributor reading the general file discovers them); each scoped file should reference the general file for repo-wide context. Flag missing cross-references.
1. **Layout consistency.** If the repo uses both `.github/*.instructions.md` (flat) and `.github/instructions/*.instructions.md` (nested), flag the inconsistency and propose consolidating on one layout.

### Phase 3: Propose Changes

Present the user with a concrete plan before making any changes:

1. **New files** -- what will be created, with a summary of contents
1. **Content moves** -- what content is moving between files, with before/after locations
1. **Consolidations** -- duplicated content being merged into one location
1. **Symlinks** -- what symlinks will be created or updated
1. **Deletions** -- files being replaced by symlinks or removed
1. **Config split** -- settings moving between settings.json and settings.local.json

Show the proposed final file tree and get explicit user approval before proceeding.

#### Symlink strategy

Recommend `CLAUDE.md -> AGENTS.md` (AGENTS.md is the real file) when:

- AGENTS.md already exists, or
- Starting fresh (AGENTS.md is the cross-tool standard), or
- The team uses multiple AI tools

Recommend keeping CLAUDE.md as the real file (no symlink) when:

- The team exclusively uses Claude Code and the user prefers the CLAUDE.md name
- CLAUDE.md has extensive Claude-specific `@import` references that other tools wouldn't understand

Follow whichever recommendation applies. The Phase 3 plan approval gives the user a chance to override the choice.

### Phase 4: Implement

Execute the approved plan in this order:

#### 4a. AGENTS.md

Create or update AGENTS.md with shared instructions consolidated from all sources. Structure with clear headings:

```markdown
# Project Name

## Overview

Brief project description and key architectural decisions.

## Development Environment

- Package manager and runtime versions
- Key commands: build, test, lint, dev server

## Code Conventions

- Language-specific patterns and preferences
- Error handling approach
- Testing conventions and location

## Git Workflow

- Branch naming and commit format
- Pre-commit requirements
```

**Keep it under 200 lines.** If more detail is needed, keep it in `.claude/rules/` files (Claude) or reference supporting docs.

**Do not include** code style rules that linters enforce (formatting, indentation). Those belong in `.editorconfig`, `.prettierrc`, etc.

#### 4b. CLAUDE.md symlink

```bash
# If AGENTS.md is the source of truth:
ln -sfn AGENTS.md CLAUDE.md
```

If CLAUDE.md previously had Claude-specific content, extract those sections to `.claude/rules/` files before replacing with the symlink.

#### 4c. .claude/rules/ (Claude-specific)

Move Claude-specific instructions to focused rule files:

```text
.claude/rules/
+-- mcp-servers.md     # How to use project MCP servers
+-- testing.md         # Claude-specific test runner patterns
+-- security.md        # Paths to protect, secrets handling
```

Each file is auto-loaded alongside CLAUDE.md. Keep files focused on one topic.

Only create these if there are genuine Claude-specific instructions. Do not create empty rule files.

#### 4d. .claude/settings.json (team-shared)

Create or update with team-appropriate settings:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [],
    "deny": []
  }
}
```

Move team settings here from settings.local.json. Remove personal settings to settings.local.json.

#### 4e. .claude/settings.local.json (personal)

Move personal settings here from settings.json. Verify it is gitignored.

If settings.local.json does not exist and there are no personal settings to move, do not create an empty file.

#### 4f. .github/copilot-instructions.md

Create or update with Copilot-specific content. This file should NOT duplicate AGENTS.md. Instead, use the pointer pattern: a cross-reference to AGENTS.md plus Copilot-specific PR review rules.

```markdown
# GitHub Copilot Instructions

For full project conventions, see AGENTS.md in the repository root.

## Scoped Instructions

Flat-layout example -- path-scoped Copilot instructions live alongside this file:

- [`lean.instructions.md`](lean.instructions.md) -- Lean source files (`**/*.lean`).
- [`ts.instructions.md`](ts.instructions.md) -- TypeScript files (`**/*.ts`, `**/*.tsx`).

If the repo uses the nested layout under `.github/instructions/`, link to `instructions/lean.instructions.md` and `instructions/ts.instructions.md` instead.

## PR Review

When reviewing pull requests, do not flag the following patterns as issues.
Each is an intentional project convention:

- **Convention name**: Brief explanation of why this is intentional.
```

**Cross-reference the scoped files.** When the repo has any `.github/*.instructions.md` (or `.github/instructions/*.instructions.md`) files, list them in a `## Scoped Instructions` section in the general file with their `applyTo` glob noted. This makes the scoped surface discoverable to humans reading the general file. Omit the section if there are no scoped files.

**Keep concise.** GitHub recommends keeping instruction files short and putting the most important rules first. Start with a focused set of review rules and add more iteratively.

**The "do not flag" pattern.** The PR Review section documents project conventions that Copilot commonly misidentifies as issues during PR reviews. Each item uses the bold-key format (`**Convention name**: explanation`). To populate this section for an existing project:

1. Check the project's PR history for recurring false-positive Copilot review comments
1. Review AGENTS.md, CLAUDE.md, and any existing code review documentation for conventions that an external reviewer might question
1. Look for intentional patterns that deviate from common defaults (e.g., non-standard error handling, unconventional file locations, domain-specific naming)
1. Start with 3-5 items and add more as Copilot flags new false positives over time

**Section heading.** Use `## PR Review` as the heading. Some repos use `## PR Review Checklist (CRITICAL)` or `## Code Review` -- all are acceptable. The key requirement is that PR review rules appear early in the file.

#### 4g. Scoped Copilot instructions (`.github/*.instructions.md`)

Create path-scoped instruction files only when the project structure warrants them. Use Copilot's `applyTo` glob for file-type or directory scoping.

**Layout.** Two locations are valid; pick one per repo:

- **Flat:** `.github/<scope>.instructions.md` -- convenient for one or two scoped files.
- **Nested:** `.github/instructions/<scope>.instructions.md` -- scales better when there are several scoped files.

If both layouts are present, consolidate on one. Do not mix.

**Required structure.** Every scoped file MUST have:

1. YAML frontmatter with `applyTo: "<glob>"`.
1. A top-level Markdown heading naming the scope (e.g., `# Lean PR Review Instructions`, not `# Instructions`).
1. A reference back to the general `copilot-instructions.md` (or `AGENTS.md`) for repo-wide context.

```markdown
---
applyTo: "**/*.lean"
---

# Lean PR Review Instructions

For repo-wide conventions, see [`copilot-instructions.md`](copilot-instructions.md) and `AGENTS.md` at the repository root.

## PR Review

- **Entrypoint manifest**: Each module under `MyLib/` has a sibling test module under `MyLibTest/`. Do not flag the test module as duplicating the source module.
- **No line-length limit**: Mathlib's ~100-char wrap is not enforced. Do not flag long lines.
- **Single-line comment paragraphs**: `--` and `/-- -/` comments are intentionally single long lines per paragraph.
```

**Naming.** Name scoped files by what they scope to: `lean.instructions.md`, `ts.instructions.md`, `frontend.instructions.md`, `tests.instructions.md`. Avoid generic names like `extra.instructions.md` or `more.instructions.md`.

**Good candidates for scoped files:**

- Distinct frontend/backend directories in a monorepo
- Multiple languages in the same repo (Go backend, TypeScript frontend)
- A single language with strong conventions that diverge from generic best-practice (e.g., Lean's `applyTo: "**/*.lean"` carrying Mathlib-aware review rules)
- Test files with different conventions than source files
- Generated code directories that should be treated differently

**Use `excludeAgent`** to control whether instructions apply to the coding agent, code review, or both:

- `excludeAgent: copilot-code-review` -- coding agent only
- `excludeAgent: copilot-coding-agent` -- code review only
- Omit `excludeAgent` -- both

**Validate the glob.** Before committing a scoped file, confirm the `applyTo` pattern matches at least one tracked file in the repo. A glob that matches nothing is a strong signal the file is stale (pasted from another repo, target code removed, or pattern mistyped). Either fix the glob, delete the file, or document why the file is being kept ahead of code that does not yet exist.

**Avoid silent overlap.** Two scoped files whose globs both match the same source file create ambiguous review rules. If overlap is intentional (e.g., one applies broadly, another narrows for a subdirectory), make the relationship explicit in the narrower file's prose.

Do not create path-scoped files if the project has a flat structure or uniform conventions. The general `copilot-instructions.md` is enough.

#### 4h. .codex/config.toml (if applicable)

Only create if the team uses Codex. Include team-appropriate defaults:

```toml
#:schema https://developers.openai.com/codex/config-schema.json

approval_policy = "on-request"
sandbox_mode = "workspace-write"

project_doc_fallback_filenames = ["CLAUDE.md"]
```

The `project_doc_fallback_filenames` line lets Codex fall back to CLAUDE.md when AGENTS.md is not present.
If CLAUDE.md is a symlink to AGENTS.md, omit `project_doc_fallback_filenames` to avoid Codex ingesting the same instructions twice.

#### 4i. opencode.json (if applicable)

Only create if the team uses OpenCode. Reference the instruction files:

```json
{
  "instructions": ["AGENTS.md"]
}
```

Add glob patterns for subdirectory AGENTS.md files in monorepos:

```json
{
  "instructions": ["AGENTS.md", "packages/*/AGENTS.md"]
}
```

### Phase 5: Verify

1. **Symlinks resolve correctly:**

   ```bash
   ls -la CLAUDE.md
   readlink CLAUDE.md
   ```

1. **No duplicated instructions** across AGENTS.md, copilot-instructions.md, and .claude/rules/

1. **Scoped Copilot instructions are well-formed:**
   - Each `.github/*.instructions.md` (or `.github/instructions/*.instructions.md`) starts with `applyTo` frontmatter and a top-level heading naming the scope
   - Each scoped file's `applyTo` glob matches at least one tracked file (no stale files)
   - No two scoped files silently overlap on the same source file
   - The general `copilot-instructions.md` lists the scoped files; each scoped file references the general file
   - Only one layout in use (flat or nested, not both)

1. **Settings split is clean:**
   - settings.json has no personal/local settings
   - settings.local.json has no team-shared settings

1. **Gitignore** covers .claude/settings.local.json

1. **Show final file tree** of all agent-related files with a brief note on each file's purpose

1. **Report summary** as a table:

| File                    | Action          | Notes                       |
| ----------------------- | --------------- | --------------------------- |
| `AGENTS.md`             | Created/Updated | Consolidated from X sources |
| `CLAUDE.md`             | Symlinked       | Points to AGENTS.md         |
| `.claude/settings.json` | Updated         | Moved N settings from local |
| ...                     | ...             | ...                         |

---

## Tool-Specific Behavior Reference

### Claude Code

- **Instruction precedence:** enterprise managed > project `CLAUDE.md` > `.claude/rules/*.md` > user `~/.claude/CLAUDE.md` > subdirectory `CLAUDE.md`
- **Config precedence:** managed > user settings > project shared settings > project local settings > CLI flags
- **@imports:** CLAUDE.md supports `@path/to/file` syntax to pull in other files without copying content
- **.claude/rules/**: All `.md` files auto-loaded alongside CLAUDE.md. Use for Claude-specific instructions that shouldn't pollute the cross-tool AGENTS.md.
- **settings.local.json**: Auto-gitignored by Claude Code. Claude writes here by default when users change settings interactively.

### OpenAI Codex

- **Instruction loading:** Walks from project root down to cwd, reading AGENTS.md at each directory level, concatenating them in order
- **AGENTS.override.md:** Temporary overrides in any directory without modifying the base file. Unique to Codex.
- **Fallback filenames:** `project_doc_fallback_filenames` in config.toml makes Codex read CLAUDE.md or other files as instruction sources
- **32 KiB limit:** Combined AGENTS.md content is capped at `project_doc_max_bytes` (default 32 KiB). Raise in config.toml if needed.
- **Profiles:** Named config profiles (`[profiles.name]`) for switching between careful review and fast iteration. Unique to Codex.
- **Trust model:** Project .codex/config.toml only loads if the project is trusted.

### GitHub Copilot

- **Two agents:** The coding agent (CLI, VS Code) and the code review agent (PR reviews) both read .github/ files but can be targeted separately with `excludeAgent`.
- **Path-scoping:** `.github/instructions/*.instructions.md` with `applyTo` globs offers file-type-level granularity that no other tool matches. This is Copilot's strongest unique feature.
- **Also reads:** AGENTS.md (root + subdirs) and CLAUDE.md (root) as fallbacks. If both AGENTS.md and copilot-instructions.md exist, Copilot uses both.
- **Keep short:** Copilot's review may not read full instruction files. Put critical rules first. Keep each file under ~1,000 lines.
- **Zero root footprint:** Everything lives in .github/, which already exists in most GitHub repos.

### OpenCode

- **Reads AGENTS.md natively.** If both AGENTS.md and CLAUDE.md exist, only AGENTS.md is used.
- **Custom paths:** `instructions` array in opencode.json supports glob patterns (e.g., `packages/*/AGENTS.md`).
- **MCP servers:** Configured in opencode.json under `mcpServers`, same format as Claude Code's .mcp.json.
- **Provider-agnostic:** Supports Claude, OpenAI, Gemini, and local models. Model config is always personal, not team-shared.

---

## Error Handling

- **No agent config files exist at all:** Start fresh with the recommended structure. Analyze the project characteristics (languages, build tools, directory structure) to populate AGENTS.md.
- **CLAUDE.md and AGENTS.md both exist with different content:** Merge them and ask the user which filename becomes the real file (recommend AGENTS.md). The other becomes a symlink.
- **settings.local.json has team settings:** Propose moving them to settings.json with a clear before/after diff.
- **settings.json has personal settings:** Propose moving them to settings.local.json.
- **Symlinks point to wrong targets:** Fix them after confirming with the user.
- **.github/ does not exist:** Create it. Assume the repository is hosted on GitHub.
- **Monorepo detected:** Suggest subdirectory AGENTS.md files and Copilot path-scoped instructions for each major package/module.
- **Large existing CLAUDE.md (over 200 lines):** Propose splitting into AGENTS.md (shared core) + .claude/rules/ (Claude-specific) + tool-specific files.
- **Scoped Copilot file with no `applyTo` frontmatter:** Add the frontmatter using a glob inferred from the file's name and content (e.g., `lean.instructions.md` -- `applyTo: "**/*.lean"`). If the intended scope is unclear, ask.
- **Scoped Copilot file whose `applyTo` glob matches no tracked files:** Flag as stale. Either fix the glob, delete the file, or (rarely) keep it with a comment explaining that it covers code that does not yet exist.
- **Two scoped files with overlapping globs:** Ask whether the overlap is intentional. If not, narrow one of the globs or merge the files. If intentional, document the relationship in the narrower file's prose.
- **Mixed flat (`.github/*.instructions.md`) and nested (`.github/instructions/*.instructions.md`) layouts:** Propose consolidating on one. Default to the layout already used by the majority of the scoped files; if tied, prefer flat for one or two files, nested for three or more.
- **General `copilot-instructions.md` does not reference the scoped files (or vice versa):** Add the cross-references. The general file gets a `## Scoped Instructions` section listing each scoped file with its `applyTo` glob; each scoped file gets a one-line pointer to the general file and `AGENTS.md`.
