# LLM Coding Agent Instruction Files: Complete Comparison & Recommendations

Last updated: February 15, 2026

## The Landscape

Every major AI coding agent reads some form of Markdown instruction file from your project. The idea is simple: instead of repeating "we use pnpm, not npm" and "always run tests before committing" in every prompt, you write it once and the agent reads it automatically at session start. The ecosystem has fragmented into several distinct formats with varying degrees of cross-tool compatibility. This document maps the territory across the four tools that matter most -- Claude Code, OpenAI Codex, GitHub Copilot, and OpenCode -- and gives you a concrete strategy.

---

## Comparison Table

| Feature                       | **CLAUDE.md**                                                                    | **AGENTS.md**                                                                                                        | **copilot-instructions.md**                                                                              | **SKILL.md**                                             |
| ----------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| **Primary tool**              | Claude Code                                                                      | Codex, Copilot, OpenCode, and 40+ others                                                                             | GitHub Copilot (chat, agent, code review)                                                                | Claude Code, Codex (open standard)                       |
| **Governance**                | Anthropic                                                                        | Agentic AI Foundation (Linux Foundation)                                                                             | GitHub/Microsoft                                                                                         | Agent Skills open standard                               |
| **File location**             | Repo root, subdirs, `~/.claude/CLAUDE.md`, `.claude/rules/`                      | Repo root, subdirs, `~/.codex/AGENTS.md`, `~/.config/opencode/AGENTS.md`                                             | `.github/copilot-instructions.md`, `.github/*.instructions.md`, `.github/instructions/*.instructions.md` | `.claude/skills/*/SKILL.md`, `.agents/skills/*/SKILL.md` |
| **Format**                    | Plain Markdown                                                                   | Plain Markdown                                                                                                       | Plain Markdown (with optional YAML frontmatter for path-scoped files)                                    | Markdown with YAML frontmatter                           |
| **Hierarchical loading**      | Yes -- global to project root to subdirectory, plus `.claude/rules/` auto-loaded | Yes -- global to project root to walk down to cwd; closest file wins                                                 | Yes -- org-level to repo-level to path-specific `.instructions.md`                                       | No -- loaded on-demand when skill is invoked             |
| **File imports / references** | `@path/to/file` syntax; recursive                                                | Via `opencode.json` `instructions` array or `@` read directives in the file                                          | Prompt files can use `#file:path` references                                                             | Can reference supporting files in skill directory        |
| **Path-scoping**              | Subdirectory `CLAUDE.md` files scope to that dir                                 | Subdirectory files scope to that dir; closest wins                                                                   | `applyTo` glob in `.instructions.md` frontmatter                                                         | Skills loaded only when relevant to the task             |
| **Override mechanism**        | Subdirectory files supplement parent                                             | `AGENTS.override.md` in any dir; later files override earlier                                                        | Path-specific instructions supplement repo-wide                                                          | Invocation control: user-only, model-invokable, or both  |
| **Init command**              | `/init` generates starter file                                                   | `/init` in OpenCode and Codex scans project                                                                          | Copilot coding agent auto-suggests on first PR; `/init` in VS Code                                       | `/skills` or `$skill-installer`                          |
| **Live editing**              | Ask Claude to edit the file directly                                             | Manual editing                                                                                                       | Manual editing                                                                                           | Direct file editing                                      |
| **Cross-tool support**        | Claude Code only (but Copilot reads it as a fallback at root)                    | **Broadest**: Codex, Copilot, OpenCode, plus Gemini CLI, Cursor, Zed, Roo Code, Kilo Code, Amp, Jules, and many more | Copilot ecosystem (VS Code, JetBrains, GitHub.com); also reads `AGENTS.md`                               | Claude Code + Codex (open standard)                      |
| **Recommended length**        | Under 300 lines; fewer is better                                                 | No official limit; same general "keep it lean" advice                                                                | Short, self-contained statements; 10-20 instructions to start                                            | Focused per-skill; reference files loaded on-demand      |
| **Version control**           | Yes, commit to repo                                                              | Yes, commit to repo                                                                                                  | Yes, in `.github/`                                                                                       | Yes, in `.claude/skills/` or `.agents/skills/`           |

---

## Deep Dive: Each Format

### CLAUDE.md (Anthropic -- Claude Code)

This is Claude Code's native instruction file. It's read as part of the system prompt with high priority -- Claude Code treats its contents as authoritative system rules that take precedence over ad-hoc user prompts. The hierarchy is: enterprise policy, then project root `CLAUDE.md`, then subdirectory `CLAUDE.md` files (scoped to that directory), then `.claude/rules/*.md` (all auto-loaded), then user `~/.claude/CLAUDE.md`.

Key strengths: the `@path/to/file` import syntax lets you keep the root file lean while referencing detailed docs elsewhere, and the `.claude/rules/` directory lets you split rules into focused topic files that all load automatically. Skills (see SKILL.md below) extend this further with on-demand loading.

Key limitation: Claude Code-specific. No other tool natively reads `CLAUDE.md` as its primary file, though Copilot will read it as a fallback, and you can configure Codex to read it via `project_doc_fallback_filenames`.

### AGENTS.md (Linux Foundation -- Open Standard)

This is the emerging industry standard, now stewarded by the Agentic AI Foundation under the Linux Foundation. It originated from collaborative efforts by OpenAI (Codex), Google (Jules), Cursor, Amp, and Factory. The format is intentionally minimal: just Markdown with whatever headings you want. No special syntax, no required frontmatter, no schema to validate against.

The adoption is broad and growing. Among the tools covered here: Codex uses it as the primary instruction file (having migrated from `codex.md`), Copilot reads it alongside its own format, and OpenCode uses it natively. Over 40,000 open-source projects already have an `AGENTS.md`.

**Codex's implementation** is the most sophisticated: it walks from the project root down to your current working directory, checking each directory for `AGENTS.override.md` first, then `AGENTS.md`, concatenating them in order. The 32 KiB default limit (`project_doc_max_bytes`) can be raised in config. You can also add fallback filenames in `config.toml` so Codex will read your existing `CLAUDE.md` or `TEAM_GUIDE.md`.

**OpenCode's implementation** reads `AGENTS.md` as its primary instruction file. The first matching file wins in each category -- if you have both `AGENTS.md` and `CLAUDE.md`, only `AGENTS.md` is used. OpenCode also supports custom instruction file paths via the `instructions` array in `opencode.json`, including glob patterns like `packages/*/AGENTS.md`.

**Copilot's implementation** reads `AGENTS.md` files at the root and in subdirectories. If both `AGENTS.md` and `copilot-instructions.md` exist, instructions from both are used. Root-level `AGENTS.md` is treated as primary instructions; other locations are treated as additional.

### .github/copilot-instructions.md (GitHub/Microsoft -- Copilot)

GitHub Copilot's approach is more structured than most. There are three layers:

First, the repo-wide `.github/copilot-instructions.md` applies to all interactions. Second, path-specific `*.instructions.md` files (either at `.github/<scope>.instructions.md` or under `.github/instructions/<scope>.instructions.md`) use YAML frontmatter with an `applyTo` glob to scope instructions to specific file types or directories. Third, organization-level instructions can be set on GitHub.com for enterprise teams.

The two layouts for scoped files are functionally equivalent: both are read by Copilot and both honor the `applyTo` frontmatter. The flat layout (`.github/lean.instructions.md`) is convenient for repos with one or two scoped files; the nested layout (`.github/instructions/lean.instructions.md`) scales better when there are several. Pick one per repo and stick with it. Repos in the wild use both -- e.g., `cboone/shannon-entropy` keeps a flat `.github/lean.instructions.md` alongside the general `.github/copilot-instructions.md`.

A unique feature: Copilot's coding agent will auto-suggest generating a `copilot-instructions.md` on your first PR in a repository. The path-specific `.instructions.md` system is powerful for monorepos -- you can have different rules for your Python backend vs. your React frontend, triggered automatically by file glob matches. It is also valuable in single-language repos that need review rules tighter than the general file: a `lean.instructions.md` with `applyTo: "**/*.lean"` can carry Mathlib-aware conventions (no line-length limit, single-line comment paragraphs, vendored-deps exclusion) that would clutter the general file.

**Cross-reference the scoped files from the general one.** When scoped files exist, list them in the general `copilot-instructions.md` under a `## Scoped Instructions` section so a contributor reading the general file discovers them. Each scoped file should in turn point back to the general file (and `AGENTS.md`) for repo-wide context. Without these cross-references the scoped surface is invisible to humans and easy to forget about during refactors.

**Validate the `applyTo` glob.** A scoped file whose `applyTo` matches no tracked files in the repo is stale -- usually copied from another repo, left over after the targeted code was moved, or mistyped. Either fix the glob, delete the file, or document why it covers code that does not yet exist. Two scoped files with overlapping `applyTo` globs create ambiguous review rules; either narrow one glob or document the intentional layering in the narrower file's prose.

Copilot also supports several related file types in `.github/`:

- **Prompt files** (`.github/prompts/*.prompt.md`) -- reusable prompt templates that can reference files with `#file:path` syntax.
- **Chat modes** (`.github/chatmodes/*.chatmode.md`) -- custom personas with specific tool access.
- **Agent definitions** (`.github/agents/*.agent.md`) -- custom agent configurations.

Limitations: the official docs warn against style/tone instructions and external resource references, as these tend not to work reliably. Keep instructions to factual, project-specific guidance.

### SKILL.md (Open Standard -- Agent Skills)

Skills are a fundamentally different concept from the other instruction files. While CLAUDE.md/AGENTS.md provide always-on or directory-scoped context, Skills are on-demand capabilities that the agent loads only when a task matches the skill's description. Think of them as reusable playbooks rather than persistent configuration.

A SKILL.md file has two parts: YAML frontmatter (with `name`, `description`, and optional configuration like `disable-model-invocation` and `allowed-tools`) and a Markdown body with instructions. The skill directory can also contain supporting scripts, templates, and reference files that the agent reads only when the skill is active.

Claude Code introduced Skills and they follow the Agent Skills open standard that works across tools. OpenAI Codex has adopted the same concept, with skills stored in `.agents/skills/` directories. Codex's implementation adds `agents/openai.yaml` for UI metadata and tool dependencies.

The key design principle is **progressive disclosure**: the agent starts with only each skill's metadata (name + description), then loads the full SKILL.md only when it decides to use that skill. This is how you get around the context bloat problem -- detailed instructions for dozens of workflows exist in your project, but only the relevant ones enter the context window for any given session.

**In Claude Code**, skills live in `.claude/skills/*/SKILL.md` (project-level) or `~/.claude/skills/*/SKILL.md` (global). Custom slash commands in `.claude/commands/` have been merged into the skills system -- both create `/slash-command` invocations.

**In Codex**, skills live in `.agents/skills/` at any level from cwd up to the project root. Codex scans these locations and follows symlinks. Skills can be enabled/disabled in `config.toml` without deleting them.

---

## Where They Overlap and Where They Don't

### Universal overlap

Every format supports plain Markdown for instructions. Every format supports project-root placement. Every format supports some form of global (user-level) instructions. Every format recommends version-controlling the instruction file. And every format's core purpose is the same: give the agent project context so you don't repeat yourself.

### The convergence toward AGENTS.md

The single most important trend is the convergence around `AGENTS.md` as a cross-tool standard. Codex migrated from `codex.md` to `AGENTS.md`. Copilot reads `AGENTS.md` alongside its own format. OpenCode uses `AGENTS.md` natively. Claude Code is the holdout -- it reads `CLAUDE.md` -- but a simple symlink bridges the gap.

### Where they diverge

**Path-scoping granularity.** Copilot's `.instructions.md` with `applyTo` globs offers file-type-level scoping that AGENTS.md and CLAUDE.md don't have natively. You can say "these rules apply only when working on `*.tsx` files." AGENTS.md and CLAUDE.md only scope by directory.

**On-demand loading.** SKILL.md (in both Claude Code and Codex) is the only format that uses progressive disclosure -- loading full instructions only when the task matches. Everything else loads instructions eagerly at session start.

**Override semantics.** Codex's `AGENTS.override.md` is unique -- it lets you temporarily override instructions in any directory without modifying the base file. No other tool has this concept.

**Import mechanisms.** Claude Code uses `@path/to/file` syntax inline in CLAUDE.md. OpenCode uses the `instructions` array in `opencode.json` with glob support. Codex uses `project_doc_fallback_filenames` for alternate filenames. Copilot's prompt files use `#file:path`. Each approach is different and tool-specific.

---

## Concrete Recommendations

### 1. Make AGENTS.md your single source of truth

Put your core project instructions in `AGENTS.md` at the repo root. This is the one file that works across Codex, Copilot, and OpenCode natively. Structure it with clear Markdown headings:

```markdown
# AGENTS.md

## Project Overview

Brief description: what this is, what it does, key architectural decisions.

## Dev Environment

- Package manager: pnpm (not npm, not yarn)
- Runtime: Node 22+ / Rust nightly
- Key commands: `pnpm dev`, `pnpm test`, `cargo test`

## Code Conventions

- TypeScript strict mode; no `any` types
- Error handling: use Result<T, E> pattern, not exceptions
- Tests: colocate with source files as `*.test.ts`

## Git Workflow

- Conventional commits; one issue per PR
- Run `pnpm lint` and `pnpm test` before committing
```

Keep it under 200 lines. If you need more detail, use references or skills.

### 2. Symlink CLAUDE.md to AGENTS.md

Claude Code doesn't natively read `AGENTS.md`, so create a symlink:

```bash
ln -s AGENTS.md CLAUDE.md
```

Claude Code reads it as `CLAUDE.md` while every other tool reads `AGENTS.md`. Both point to the same content. Git preserves symlinks on macOS/Linux.

If you need Claude Code-specific instructions (MCP server hints, subagent patterns), put those in `.claude/rules/claude-specific.md` -- that directory is Claude Code-only and won't pollute your cross-tool instructions.

Alternatively, configure Codex to read `CLAUDE.md` directly by adding to `~/.codex/config.toml`:

```toml
project_doc_fallback_filenames = ["CLAUDE.md"]
```

This approach avoids symlinks entirely if Claude Code is your primary tool.

### 3. Use .claude/rules/ and Skills for Claude Code power features

The `.claude/rules/` directory is auto-loaded alongside `CLAUDE.md`, so put topic-specific rules there:

```text
.claude/
+-- rules/
|   +-- testing.md        # Testing conventions and commands
|   +-- security.md       # Security review checklist
|   +-- mcp-servers.md    # MCP server usage instructions
+-- skills/
    +-- deploy/
        +-- SKILL.md      # On-demand deployment skill
```

Skills are your answer to context bloat. Instead of putting deployment instructions, migration workflows, and release checklists in AGENTS.md (wasting context on every session), create them as skills that load only when relevant.

### 4. Add .github/copilot-instructions.md for Copilot features

If your repo is on GitHub and contributors use Copilot, create a minimal `.github/copilot-instructions.md` that either duplicates key points from AGENTS.md or simply says:

```markdown
See AGENTS.md in the repository root for project conventions and instructions.
```

For monorepos, take advantage of Copilot's path-specific instructions. Both layouts are valid:

```text
# Flat layout (good for one or two scoped files):
.github/
+-- copilot-instructions.md          # Repo-wide
+-- frontend.instructions.md         # applyTo: "src/frontend/**"
+-- backend.instructions.md          # applyTo: "src/backend/**"

# Nested layout (good for several scoped files):
.github/
+-- copilot-instructions.md          # Repo-wide
+-- instructions/
    +-- frontend.instructions.md     # applyTo: "src/frontend/**"
    +-- backend.instructions.md      # applyTo: "src/backend/**"
```

Single-language repos can use scoped files too: a `.github/lean.instructions.md` with `applyTo: "**/*.lean"` is the right home for review conventions that only apply to Lean code (Mathlib-aware naming, no line-length limit, single-line comment paragraphs).

### 5. For OpenCode: configure custom instruction paths

OpenCode reads `AGENTS.md` natively. If you want it to also pull in docs from elsewhere in your project, use the `instructions` array in `opencode.json`:

```json
{
  "instructions": ["docs/development-standards.md", "packages/*/AGENTS.md"]
}
```

### 6. Global (user-level) instructions

For personal cross-project preferences, maintain one canonical file and symlink it:

```bash
mkdir -p ~/.agents
# Write your global instructions in ~/.agents/AGENTS.md

# Claude Code
mkdir -p ~/.claude
ln -sfn ~/.agents/AGENTS.md ~/.claude/CLAUDE.md

# Codex
mkdir -p ~/.codex
ln -sfn ~/.agents/AGENTS.md ~/.codex/AGENTS.md

# OpenCode
mkdir -p ~/.config/opencode
ln -sfn ~/.agents/AGENTS.md ~/.config/opencode/AGENTS.md
```

### 7. What goes where -- a decision framework

| Instruction type                                      | Where to put it                                               |
| ----------------------------------------------------- | ------------------------------------------------------------- |
| Project architecture, tech stack, key commands        | `AGENTS.md` (repo root)                                       |
| Module-specific conventions                           | `AGENTS.md` in that subdirectory                              |
| Claude Code-specific (MCP servers, subagent patterns) | `.claude/rules/*.md`                                          |
| Complex workflows (deploy, release, migrate)          | Skills (`SKILL.md` in a skill directory)                      |
| Copilot code review rules                             | `.github/instructions/*.instructions.md` with `applyTo` globs |
| Personal preferences (all projects)                   | `~/.agents/AGENTS.md` symlinked to each tool                  |
| Temporary overrides                                   | `AGENTS.override.md` (Codex)                                  |

### 8. Things to avoid

**Don't use instruction files for things linters do better.** Code formatting belongs in `.editorconfig`, `.prettierrc`, or `rustfmt.toml`.

**Don't stuff everything into one file.** Instruction-following quality degrades as instruction count increases. Claude Code's system prompt alone contains ~50 instructions. Keep your files focused on what the agent can't infer from the codebase.

**Don't duplicate across formats.** If you maintain both AGENTS.md and CLAUDE.md with different content, they will drift. Use symlinks or a single source of truth.

**Don't include large code examples.** LLMs pick up patterns from your existing codebase via search. Use instruction files for things the agent _can't_ infer: commands to run, workflow rules, business domain context.

---

## Summary

AGENTS.md is winning as the cross-tool standard, with backing from the Linux Foundation and native support in Codex, Copilot, and OpenCode. Claude Code is the one tool that requires its own filename, but a symlink or Codex fallback config bridges the gap trivially.

The practical strategy is a hub-and-spoke model: AGENTS.md is the hub containing core project instructions, and tool-specific locations (`.claude/rules/`, `.github/instructions/`, skills directories) are spokes that add capabilities the hub can't express. Skills handle context bloat by loading detailed instructions on demand rather than eagerly.

The single most impactful thing you can do today: create an AGENTS.md in each of your active repos with your build commands, conventions, and workflow rules. Everything else is optimization on top of that foundation.
