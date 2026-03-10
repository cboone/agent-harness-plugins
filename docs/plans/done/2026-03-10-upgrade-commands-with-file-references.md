# Update create-plugin for Commands and Extract Command Templates

## Context

The `create-plugin` skill (v1.1.7) only covers skills and hooks plugins. It completely omits command plugins, despite this repo having 10 of them. Meanwhile, the official `plugin-dev` plugin from `claude-plugins-official` documents rich command features we don't use: `@${CLAUDE_PLUGIN_ROOT}/references/file.md` for including external files, `$ARGUMENTS`/`$1` positional arguments, and full frontmatter options. Our largest commands inline all templates in single files (up to 1,057 lines). This plan updates `create-plugin` to cover all three plugin types and extracts templates from large commands into reference files.

## Phase 1: Verify `@${CLAUDE_PLUGIN_ROOT}` File References

Before extracting templates from commands, confirm the `@${CLAUDE_PLUGIN_ROOT}/path` pattern actually works at runtime. The official docs describe it but no live plugin uses it.

### 1.1 Create a minimal test command

Pick the smallest command with a reference section (e.g., `setup-secret-scanning` at 246 lines). Extract one reference section (the gitleaks workflow template) into `plugins/setup-secret-scanning/references/gitleaks-workflow.md`. Replace the inline content with `@${CLAUDE_PLUGIN_ROOT}/references/gitleaks-workflow.md`. Invoke `/setup-secret-scanning` and verify the template content is available to Claude.

### 1.2 Evaluate results

- If it works: proceed with Phases 2-4 using `@${CLAUDE_PLUGIN_ROOT}` references.
- If it doesn't work: fall back to keeping templates inline. Phase 2 (create-plugin updates) still proceeds, but Phase 3 (template extraction) gets descoped or uses an alternative approach (e.g., `Read` tool calls, or `!cat` bash execution).

## Phase 2: Update create-plugin Skill for Command Plugins

### 2.1 Create `references/command-md.md` (new file)

Path: `plugins/create-plugin/skills/create-plugin/references/command-md.md`

Cover:
- File location: `plugins/PLUGIN-NAME/commands/COMMAND-NAME.md`
- Frontmatter fields: `description`, `disable-model-invocation`, `argument-hint`, `allowed-tools`, `model`
- Our convention: `disable-model-invocation: true` for all commands in this repo
- `$ARGUMENTS` (full string) and `$1`/`$2`/`$3` (positional) with examples from our commands
- `@${CLAUDE_PLUGIN_ROOT}/references/file.md` for external file inclusion
- Body structure: `# Title`, `## Workflow` with numbered steps, `## Error Handling`, then `## Reference:` sections or external file references
- When to extract: command exceeds ~400 lines, templates are independently referenceable
- Cross-reference to the official `plugin-dev` `command-development` skill for advanced patterns

### 2.2 Update `references/plugin-json.md`

- Add `commands` field to the fields table: `"./commands"`, conditional, include only if the plugin provides commands
- Add **Command Plugin Template** (with `"commands": "./commands"`, no `"skills"` field)

### 2.3 Update `references/readme-updates.md`

- Add **Commands Section** with ToC format (same one-entry-per-line pattern with subcategories)
- Add H3 description section format for commands
- Add per-plugin README template for commands (parallel to skills and hooks templates)

### 2.4 Update main `SKILL.md` workflow

File: `plugins/create-plugin/skills/create-plugin/SKILL.md`

Changes across existing steps:

- **Step 1 (Determine Plugin Type)**: Add "Command plugin" as third type. Update inference heuristic for "create a command", "add a slash command", etc.
- **Step 3 (Create Directory Structure)**: Add Command Plugin section with `commands/` and optional `references/`
- **Step 4 (Write plugin.json)**: Note `"commands": "./commands"` for command plugins. Reference new Command Plugin Template.
- **Step 5**: Rename to "Write SKILL.md, hooks.json, or Command .md". Add "For Commands" sub-section referencing `./references/command-md.md`.
- **Step 7 (Add Reference Files)**: Extend to cover command reference files with `@${CLAUDE_PLUGIN_ROOT}/references/` pattern.
- **Step 9 (Update README.md)**: Add "Adding a New Command" parallel to existing skill/hook instructions.
- **Step 11 (Verification Checklist)**: Add command-specific checks (frontmatter, filename, commands field, external references, $ARGUMENTS handling).
- **Frontmatter description**: Add command-related trigger phrases.

### 2.5 Version bump and sync

- `create-plugin` plugin.json: `1.1.7` -> `1.2.0` (new capability)
- `marketplace.json` entry: match to `1.2.0`
- `CLAUDE.md` structure tree: add `command-md.md` to create-plugin entry

## Phase 3: Extract Templates from Large Commands

Apply to the 5 largest commands, starting with `setup-ci` as proof of concept. Each command gets:
- A `references/` directory alongside `commands/`
- Templates moved from inline `## Reference:` sections to individual reference files
- `@${CLAUDE_PLUGIN_ROOT}/references/file.md` references in the command file
- Workflow prose stays in the command file

### 3.1 setup-ci (1,057 lines, target ~175 lines)

Extract 15 reference files into `plugins/setup-ci/references/`:

CI workflows (8 files): `ci-go-cli.md`, `ci-go-library.md`, `ci-javascript.md`, `ci-python.md`, `ci-rust.md`, `ci-ruby.md`, `ci-shell.md`, `ci-multi-language.md`

Makefile templates (7 files): `makefile-go-cli.md`, `makefile-go-library.md`, `makefile-javascript.md`, `makefile-python.md`, `makefile-rust.md`, `makefile-ruby.md`, `makefile-shell.md`

Version: `1.3.0` -> `1.4.0`

### 3.2 scaffold-go-cli (881 lines, target ~260 lines)

Extract 12 reference files into `plugins/scaffold-go-cli/references/`:

`main-go.md`, `root-go-without-viper.md`, `root-go-with-viper.md`, `go-mod.md`, `makefile.md`, `gitignore.md`, `goreleaser.md`, `ci-workflow.md`, `release-workflow.md`, `license.md`, `readme.md`, `homebrew-tap-token.md`

Version: `2.5.0` -> `2.6.0`

### 3.3 scaffold-go-library (827 lines, target ~245 lines)

Extract 12 reference files into `plugins/scaffold-go-library/references/`:

`go-mod.md`, `package-file.md`, `doc-go.md`, `makefile.md`, `gitignore.md`, `goreleaser.md`, `golangci.md`, `editorconfig.md`, `ci-workflow.md`, `release-workflow.md`, `license.md`, `readme.md`

Version: `1.6.0` -> `1.7.0`

### 3.4 scaffold-new-repo (754 lines, target ~195 lines)

Extract 6 reference files into `plugins/scaffold-new-repo/references/`:

`license.md`, `readme.md`, `changelog.md`, `gitignore-templates.md` (all language variants in one file), `agents-md.md`, `copilot-instructions.md`

Version: `1.5.0` -> `1.6.0`

### 3.5 add-goreleaser-homebrew (710 lines, target ~200 lines)

Extract into `plugins/add-goreleaser-homebrew/references/`:

`goreleaser-base.md`, `goreleaser-completions.md`, `goreleaser-manpages.md`, `release-workflow.md`, `makefile-targets.md`, `homebrew-tap-token.md`

Version: `2.1.0` -> `2.2.0`

## Phase 4: Finalize

### 4.1 Update CLAUDE.md

Add `references/` directory listings to the structure tree for all refactored command plugins (setup-ci, scaffold-go-cli, scaffold-go-library, scaffold-new-repo, add-goreleaser-homebrew) and create-plugin.

### 4.2 Update marketplace.json

Sync all 6 version bumps (create-plugin + 5 commands). `metadata.version` stays at `1.23.0` (no plugins added or removed).

### 4.3 Run check-versions

Use the `check-versions` skill to verify all plugin.json and marketplace.json versions match.

## Files to Modify

### Phase 2 (create-plugin updates)
- `plugins/create-plugin/skills/create-plugin/SKILL.md`
- `plugins/create-plugin/skills/create-plugin/references/command-md.md` (new)
- `plugins/create-plugin/skills/create-plugin/references/plugin-json.md`
- `plugins/create-plugin/skills/create-plugin/references/readme-updates.md`
- `plugins/create-plugin/.claude-plugin/plugin.json`

### Phase 3 (template extraction, per command)
- Command `.md` file (shrink)
- New `references/*.md` files (extracted templates)
- `.claude-plugin/plugin.json` (version bump)

### Phase 4 (finalize)
- `CLAUDE.md`
- `.claude-plugin/marketplace.json`

## Commit Strategy

One commit per logical unit:
1. Phase 1: verify `@${CLAUDE_PLUGIN_ROOT}` (may be reverted if it doesn't work)
2. Phase 2: one commit per reference file created, one for SKILL.md updates, one for version bump
3. Phase 3: one commit per command extraction (includes references + command update + version bump)
4. Phase 4: CLAUDE.md update, marketplace sync, version check

## Verification

1. After Phase 1: invoke `/setup-secret-scanning` and confirm template content is available
2. After each Phase 3 extraction: invoke the command and confirm templates are available
3. After Phase 4: run `check-versions` skill
4. Final: review all modified commands to ensure no template content was lost
