# LLM Coding Agent Configuration Files: Complete Comparison & Recommendations

Last updated: February 15, 2026

_Companion to: [Agent Instruction Files Comparison](agent-instruction-files.md)_

## Overview

Beyond the instruction/context files (CLAUDE.md, AGENTS.md, etc.), every AI coding agent has its own configuration system for things like model selection, permissions, sandboxing, MCP servers, and tool policies. These config files control the _behavior_ of the tool itself, whereas instruction files control the _context_ the LLM receives. This document maps out where every config file lives, what it controls, which files should be committed to version control, and how it all fits together.

---

## The Root Directory Footprint

| Tool               | Files at project root        | Files in hidden directories                                                                                                                                                | Total project-level files                |
| ------------------ | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| **Claude Code**    | `CLAUDE.md`, `.mcp.json`     | `.claude/settings.json`, `.claude/settings.local.json`, `.claude/rules/*.md`, `.claude/skills/*/SKILL.md`, `.claude/commands/*.md`                                         | 2 root + many in `.claude/`              |
| **OpenAI Codex**   | `AGENTS.md`                  | `.codex/config.toml`, `.agents/skills/*/SKILL.md`                                                                                                                          | 1 root + few in `.codex/` and `.agents/` |
| **GitHub Copilot** | _(none)_                     | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `.github/chatmodes/*.chatmode.md`, `.github/agents/*.agent.md`, `.github/prompts/*.prompt.md` | 0 root, all in `.github/`                |
| **OpenCode**       | `AGENTS.md`, `opencode.json` | _(none)_                                                                                                                                                                   | 2 root                                   |

With the symlink strategy (CLAUDE.md to AGENTS.md), your realistic root footprint across all four tools is: `AGENTS.md`, `CLAUDE.md` (symlink), `.mcp.json` (if using MCP servers), and `opencode.json` (if using OpenCode). Three or four visible files.

---

## Detailed Breakdown by Tool

### Claude Code

Claude Code has the most layered configuration system of any tool in this space. There are five distinct levels of precedence, from highest to lowest:

1. **Managed settings** (enterprise IT) -- `managed-settings.json` and `managed-mcp.json` deployed to system directories (`/etc/claude-code/`, `/Library/Application Support/ClaudeCode/`, etc.). Requires admin privileges. Constrains what users and projects can override.
1. **User settings** -- `~/.claude/settings.json`. Personal defaults that apply to all projects.
1. **Project shared settings** -- `.claude/settings.json` in the project directory. Checked into version control. Shared with the team.
1. **Project local settings** -- `.claude/settings.local.json` in the project directory. Auto-gitignored by Claude Code. Personal overrides for this project.
1. **CLI flags and `/config` commands** -- runtime overrides for the current session.

All levels combine; they don't replace each other. More specific settings override on conflicts.

#### Project-level files

```text
your-project/
+-- CLAUDE.md                          # Instructions (or symlink to AGENTS.md)
+-- .mcp.json                          # MCP server config (version-controlled)
+-- .claude/
    +-- settings.json                  # Team config: permissions, hooks, env vars
    +-- settings.local.json            # Personal config (gitignored)
    +-- rules/
    |   +-- code-style.md              # Auto-loaded instruction rules
    |   +-- testing.md
    |   +-- security.md
    +-- skills/
    |   +-- deploy/
    |       +-- SKILL.md               # On-demand skill
    +-- commands/
        +-- review.md                  # Custom /review slash command
```

#### User-level files

```text
~/.claude/
+-- settings.json                      # Global settings (all projects)
+-- settings.local.json                # Global personal overrides
+-- CLAUDE.md                          # Global instructions
+-- skills/                            # Global skills
+-- commands/                          # Global slash commands

~/.claude.json                         # Legacy: onboarding state, API key trust, theme
```

#### What goes in settings.json

The `settings.json` files accept these key settings:

**Permissions** -- allow/deny/ask rules for tools. Rules follow the format `Tool` or `Tool(specifier)` and are evaluated in order: deny first, then ask, then allow.

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Read", "Grep", "Bash(npm test*)"],
    "deny": ["Edit(/secrets/*)"]
  }
}
```

**Environment variables** -- set for every session. Useful for telemetry control, model overrides, etc.

```json
{
  "env": {
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY": "1"
  }
}
```

**Hooks** -- custom commands that run before/after tool execution. Can block operations by exiting with code 2.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'jq -r .input.command | grep -qE \"rm\\s+-rf\" && echo \"Use trash instead of rm -rf\" >&2 && exit 2 || exit 0'"
          }
        ]
      }
    ]
  }
}
```

**Other settings:**

- `mcpServers` -- MCP server configuration (alternatively in `.mcp.json` at project root).
- `attribution` -- control Co-Authored-By in commits and Claude Code footer in PRs: `{"commits": true, "pullRequests": true}`.
- `spinnerTipsEnabled` -- toggle loading tips.
- `disallowedTools` -- block specific tools entirely.

The `$schema` key enables autocomplete and validation in VS Code and other editors that support JSON Schema.

#### MCP configuration

MCP servers can be configured in two places:

- `.mcp.json` at project root -- intended for version control, shared with the team.
- Inside `settings.json` under the `mcpServers` key -- for personal or project-local servers.

The `.mcp.json` format:

```json
{
  "mcpServers": {
    "shadcn": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/shadcn-mcp"]
    }
  }
}
```

---

### OpenAI Codex

Codex uses TOML for configuration instead of JSON, and has a clean two-tier system with an additional admin enforcement layer.

#### Configuration precedence (highest to lowest)

1. **CLI flags** (`-c key=value`, `--model`, `--sandbox`, etc.)
1. **Project config** -- `.codex/config.toml` files, walked from project root to cwd (closest wins). Only loaded if the project is trusted.
1. **User config** -- `~/.codex/config.toml`.
1. **Admin requirements** -- `requirements.toml` in system directories. Constrains security-sensitive settings (e.g., can forbid `approval_policy = "never"`).
1. **Built-in defaults**.

#### Project-level files

```text
your-project/
+-- AGENTS.md                          # Instructions (primary)
+-- AGENTS.override.md                 # Temporary overrides (optional)
+-- .codex/
    +-- config.toml                    # Project config (trusted projects only)

# Skills can live in .agents/ at any level:
+-- .agents/
    +-- skills/
        +-- deploy/
            +-- SKILL.md
            +-- agents/openai.yaml     # UI metadata and tool dependencies
```

#### User-level files

```text
~/.codex/
+-- config.toml                        # Global config
+-- AGENTS.md                          # Global instructions
+-- AGENTS.override.md                 # Global temporary overrides
+-- auth.json                          # Cached credentials (or OS keyring)
+-- log/                               # Session logs
```

#### Key config.toml settings

```toml
#:schema https://developers.openai.com/codex/config-schema.json

# Core model selection
model = "gpt-5.2-codex"
model_provider = "openai"
model_reasoning_effort = "medium"     # minimal | low | medium | high | xhigh

# Approval and sandboxing
approval_policy = "on-request"        # untrusted | on-failure | on-request | never
sandbox_mode = "workspace-write"      # read-only | workspace-write | danger-full-access

[sandbox_workspace_write]
network_access = false
writable_roots = ["/Users/YOU/.pyenv/shims"]

# Web search
web_search = "cached"                 # disabled | cached | live

# Instruction file discovery
project_doc_max_bytes = 32768         # Max combined AGENTS.md size (default 32 KiB)
project_doc_fallback_filenames = ["CLAUDE.md", "TEAM_GUIDE.md"]

# MCP servers
[mcp_servers.puppeteer]
command = "docker"
args = ["run", "-i", "--rm", "mcp/puppeteer"]

# Named profiles
[profiles.deep-review]
model = "gpt-5-pro"
model_reasoning_effort = "high"
approval_policy = "never"

[profiles.lightweight]
model = "gpt-4.1"
approval_policy = "untrusted"

# Feature flags
[features]
shell_snapshot = true

# Per-skill enablement
[[skills.config]]
path = "/path/to/skill/SKILL.md"
enabled = false
```

The `#:schema` comment at the top enables autocomplete in editors with the "Even Better TOML" extension.

#### Notable unique features

- **Profiles** -- define named config profiles (`[profiles.<name>]`) and switch with `codex --profile deep-review`. Excellent for having a "fast and loose" profile vs. a "careful review" profile.
- **`project_doc_fallback_filenames`** -- lets Codex treat other filenames (e.g., `CLAUDE.md`, `TEAM_GUIDE.md`) as instruction files when `AGENTS.md` is not present. Use this when you don't want a `CLAUDE.md -> AGENTS.md` symlink; if `CLAUDE.md` is already a symlink to `AGENTS.md`, omit it here to avoid redundant reads.
- **`requirements.toml`** -- admin-enforced constraints that users can't override. Deployed to system directories by IT.
- **Trust model** -- project-scoped `.codex/config.toml` is only loaded when the project is trusted. If untrusted, Codex falls back to user/system defaults only.
- **Sandbox granularity** -- `[sandbox_workspace_write]` allows fine-grained control: specific writable roots, network access toggle, tmpdir exclusion.

---

### GitHub Copilot

Copilot's configuration is split between in-editor settings (VS Code/JetBrains `settings.json`) and GitHub.com organization-level settings. There are no standalone config files in the project directory -- everything project-level goes in `.github/`.

#### Project-level files

```text
your-project/
+-- .github/
    +-- copilot-instructions.md                  # Repo-wide instructions
    +-- instructions/
    |   +-- frontend.instructions.md             # Path-scoped (applyTo: "src/frontend/**")
    |   +-- backend.instructions.md              # Path-scoped (applyTo: "src/backend/**")
    +-- chatmodes/
    |   +-- dba.chatmode.md                      # Custom chat mode (persona + tools)
    +-- agents/
    |   +-- test-agent.agent.md                  # Custom agent definition
    +-- prompts/
        +-- refactor.prompt.md                   # Reusable prompt file
```

#### Editor-level settings (VS Code settings.json)

Copilot's tool behavior is configured through VS Code's settings framework, not through project-level config files:

```json
{
  "github.copilot.chat.codeGeneration.useInstructionFiles": true,
  "github.copilot.chat.reviewSelection.instructions": [{ "file": "guidance/backend-review-guidelines.md" }, { "file": "guidance/frontend-review-guidelines.md" }],
  "github.copilot.chat.pullRequestDescriptionGeneration.instructions": [{ "text": "Always include a list of key changes." }]
}
```

These settings can reference external files in the workspace via the `file` property, or inline text via the `text` property.

#### Priority order

1. Personal instructions (user-level, highest priority)
1. Repository instructions (`.github/copilot-instructions.md` or `AGENTS.md`)
1. Path-specific instructions (`.github/instructions/*.instructions.md`)

Copilot also reads `AGENTS.md` (at root and subdirectories) and `CLAUDE.md` at root as fallbacks. If both `AGENTS.md` and `copilot-instructions.md` exist, instructions from both are used.

#### Path-specific instruction file format

```markdown
---
applyTo: "src/**/*.tsx"
excludeAgent: copilot-code-review
---

Use functional React components with hooks.
Always use TypeScript strict mode.
```

The `applyTo` glob determines which files trigger these instructions. The optional `excludeAgent` field can exclude instructions from specific Copilot features (e.g., code review vs. coding agent).

#### Notable unique features

- **Auto-generation** -- Copilot's coding agent will suggest generating `copilot-instructions.md` on your first PR in a repository.
- **Chat modes** (`.chatmode.md`) -- define custom personas with specific tool access, beyond simple instructions.
- **Agent definitions** (`.agent.md`) -- custom agent configurations for specialized tasks.
- **Prompt files** (`.prompt.md`) -- reusable prompt templates with `#file:path` references.
- **Organization-level instructions** -- enterprise teams can set instructions at the GitHub org level that apply to all repos.
- **Zero root footprint** -- everything lives in `.github/`, which already exists in most repos.

---

### OpenCode

OpenCode uses a JSON config file and follows the AGENTS.md convention for instructions. It's the most straightforward config setup.

#### Project-level files

```text
your-project/
+-- AGENTS.md                          # Instructions (primary)
+-- opencode.json                      # Project configuration
```

#### User-level files

```text
~/.config/opencode/
+-- opencode.json                      # Global configuration
+-- AGENTS.md                          # Global instructions
```

#### Key opencode.json options

```json
{
  "instructions": ["docs/development-standards.md", "test/testing-guidelines.md", "packages/*/AGENTS.md"],
  "provider": "anthropic",
  "model": "claude-sonnet-4.5",
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/github-mcp"]
    }
  }
}
```

#### Notable unique features

- **Custom instruction file paths with globs** -- the `instructions` array in `opencode.json` can point to any Markdown files, including glob patterns. This is how you reference instruction files tucked away in `docs/` or spread across a monorepo without needing them at root.
- **Provider-agnostic** -- supports 75+ models from Claude, OpenAI, Gemini, and local models via Ollama/LM Studio. Configuration switches between them.
- **LSP integration** -- configurable Language Server Protocol servers give the LLM typed feedback from your codebase.
- **Instruction file precedence** -- if you have both `AGENTS.md` and `CLAUDE.md`, only `AGENTS.md` is used. Similarly, `~/.config/opencode/AGENTS.md` takes precedence over `~/.claude/CLAUDE.md`.

---

## Cross-Tool Configuration Comparison

### What each config system controls

| Capability                      | Claude Code                                  | Codex                                             | Copilot                         | OpenCode                           |
| ------------------------------- | -------------------------------------------- | ------------------------------------------------- | ------------------------------- | ---------------------------------- |
| **Config format**               | JSON                                         | TOML                                              | JSON (VS Code settings)         | JSON                               |
| **Config location (project)**   | `.claude/settings.json`                      | `.codex/config.toml`                              | _(VS Code settings only)_       | `opencode.json` (root)             |
| **Config location (user)**      | `~/.claude/settings.json`                    | `~/.codex/config.toml`                            | VS Code user settings           | `~/.config/opencode/opencode.json` |
| **Model selection**             | `env` vars in settings.json                  | `model` in config.toml                            | VS Code settings                | `model` in opencode.json           |
| **Permissions / approvals**     | `permissions` rules (allow/deny/ask)         | `approval_policy` (4 levels)                      | N/A (cloud-managed)             | N/A                                |
| **Sandboxing**                  | Permission rules + sandbox config            | `sandbox_mode` + granular `[sandbox_*]`           | N/A                             | N/A                                |
| **MCP servers**                 | `.mcp.json` or `mcpServers` in settings.json | `[mcp_servers]` in config.toml                    | N/A                             | `mcpServers` in opencode.json      |
| **Hooks / lifecycle**           | `hooks` in settings.json (pre/post tool use) | `notify` in config.toml (completion notification) | N/A                             | N/A                                |
| **Custom instruction paths**    | `@path` imports in CLAUDE.md                 | `project_doc_fallback_filenames`                  | `file` refs in VS Code settings | `instructions` array with globs    |
| **Schema validation**           | Yes (`$schema` key)                          | Yes (`#:schema` comment)                          | Via VS Code                     | No                                 |
| **Named profiles**              | No                                           | Yes (`[profiles.*]`)                              | No                              | No                                 |
| **Admin enforcement**           | `managed-settings.json` in system dirs       | `requirements.toml` in system dirs                | GitHub org-level settings       | No                                 |
| **Git-ignored personal config** | `.claude/settings.local.json` (auto)         | N/A (project config is all-or-nothing)            | N/A                             | N/A                                |

### Version control decisions

| File                                     | Commit to git?           | Why                                                                                             |
| ---------------------------------------- | ------------------------ | ----------------------------------------------------------------------------------------------- |
| `.claude/settings.json`                  | **Yes**                  | Team-shared permissions, hooks, env vars                                                        |
| `.claude/settings.local.json`            | **No** (auto-gitignored) | Personal API keys, experiments                                                                  |
| `.mcp.json`                              | **Yes**                  | Team-shared MCP server config                                                                   |
| `.codex/config.toml`                     | **Depends**              | Team-shared if it only has sandbox/approval defaults; skip if it has personal model preferences |
| `AGENTS.md` / `CLAUDE.md`                | **Yes**                  | Core project instructions                                                                       |
| `.github/copilot-instructions.md`        | **Yes**                  | Team-shared Copilot instructions                                                                |
| `.github/instructions/*.instructions.md` | **Yes**                  | Team-shared path-scoped instructions                                                            |
| `opencode.json`                          | **Yes** (if no secrets)  | Team-shared OpenCode config                                                                     |
| `~/.claude/settings.json`                | **No** (user-level)      | Personal global preferences                                                                     |
| `~/.codex/config.toml`                   | **No** (user-level)      | Personal global preferences                                                                     |

---

## Recommendations

### 1. Keep the root directory clean

With the symlink strategy from the companion document (AGENTS.md as source of truth, CLAUDE.md as symlink), your root-level footprint is:

```text
your-project/
+-- AGENTS.md                  # Single source of truth for all tools
+-- CLAUDE.md -> AGENTS.md     # Symlink for Claude Code
+-- .mcp.json                  # MCP servers (if any)
+-- opencode.json              # OpenCode config (if using)
+-- .claude/                   # Claude Code config + rules + skills
+-- .codex/                    # Codex config (if using)
+-- .github/                   # Copilot instructions (already exists)
```

### 2. Use .claude/settings.json for shared team policies

If you're working with others (or with yourself across machines), commit a `.claude/settings.json` with:

- Permission rules for common tool patterns.
- Hooks to enforce team conventions (e.g., block `rm -rf`, require feature branches).
- Environment variables for telemetry/attribution preferences.

Keep personal overrides in `.claude/settings.local.json` -- Claude Code auto-gitignores this file.

### 3. For Codex, set up fallback filenames

If `CLAUDE.md` is your primary instruction file, add this to `~/.codex/config.toml`:

```toml
project_doc_fallback_filenames = ["CLAUDE.md"]
```

This makes Codex read your CLAUDE.md without needing symlinks or a separate AGENTS.md. Combine it with a profile for your preferred workflow:

```toml
model = "gpt-5.2-codex"
approval_policy = "on-request"
sandbox_mode = "workspace-write"

project_doc_fallback_filenames = ["CLAUDE.md"]

[profiles.yolo]
approval_policy = "never"
sandbox_mode = "danger-full-access"

[profiles.review]
model = "gpt-5-pro"
model_reasoning_effort = "high"
```

### 4. MCP servers: .mcp.json for team, settings.local.json for personal

Use `.mcp.json` at the project root for MCP servers the whole team needs (Shadcn, database tools, project-specific APIs). Use `.claude/settings.local.json` (Claude Code) or user-level config (Codex `~/.codex/config.toml`) for personal MCP servers you don't want to impose on the team.

### 5. Global config sync via dotfiles

For personal preferences that span all projects and all tools, maintain a dotfiles repo:

```bash
# In your dotfiles repo:
agents/
+-- AGENTS.md                  # Global instructions (all tools)
+-- claude-settings.json       # symlinked to ~/.claude/settings.json
+-- codex-config.toml          # symlinked to ~/.codex/config.toml

# Install script:
mkdir -p ~/.claude ~/.codex ~/.config/opencode
ln -sfn ~/dotfiles/agents/AGENTS.md ~/.claude/CLAUDE.md
ln -sfn ~/dotfiles/agents/AGENTS.md ~/.codex/AGENTS.md
ln -sfn ~/dotfiles/agents/AGENTS.md ~/.config/opencode/AGENTS.md
ln -sfn ~/dotfiles/agents/claude-settings.json ~/.claude/settings.json
ln -sfn ~/dotfiles/agents/codex-config.toml ~/.codex/config.toml
```

One place to edit, version-controlled, portable across machines.

### 6. What goes in each config file -- a decision framework

| Setting type                          | Where to put it                                                  |
| ------------------------------------- | ---------------------------------------------------------------- |
| Model selection (personal preference) | User-level config for each tool                                  |
| Team permission/sandbox policies      | `.claude/settings.json`, `.codex/config.toml` (project-level)    |
| MCP servers (team-shared)             | `.mcp.json` at project root                                      |
| MCP servers (personal)                | `.claude/settings.local.json` or `~/.codex/config.toml`          |
| Custom instruction file references    | `opencode.json` `instructions` array, or `@imports` in CLAUDE.md |
| Codex fallback filenames              | `~/.codex/config.toml` `project_doc_fallback_filenames`          |
| Pre/post tool hooks                   | `.claude/settings.json` `hooks`                                  |
| Copilot code review config            | VS Code `settings.json` or `.github/instructions/`               |
| Path-scoped instructions              | `.github/instructions/*.instructions.md` (Copilot)               |
| Telemetry/privacy controls            | User-level `settings.json` or `config.toml` `env` vars           |

---

## Summary

The instruction file ecosystem is converging around AGENTS.md. The configuration file ecosystem is not -- and probably won't. Each tool's config manages fundamentally different capabilities: Claude Code's hook system has no equivalent in Codex, Codex's named profiles have no equivalent in Claude Code, and Copilot's configuration lives entirely in VS Code's settings framework rather than standalone files.

The pragmatic approach: accept tool-specific config in hidden directories while converging on shared instruction files at the root. Hidden directories keep the clutter invisible. Each tool's config is independent enough that they don't conflict with each other. The global dotfiles strategy (section 5) keeps your personal preferences in sync across tools and machines.
