# Rename write-shell-scripts to write-bash-scripts

## Context

A `write-zsh-scripts` skill is being added in a parallel worktree. The current `write-shell-scripts` plugin is Bash-specific, so renaming it to `write-bash-scripts` clarifies which shell dialect it targets and avoids confusion with the new Zsh skill.

Descriptions will also be updated from "shell scripts" to "Bash scripts" where the text refers to what this plugin covers, reinforcing the distinction.

## Changes

### 1. Rename plugin directory

```text
plugins/write-shell-scripts/ -> plugins/write-bash-scripts/
```

This is a `git mv` of the entire directory tree.

### 2. Rename skill subdirectory

```text
plugins/write-bash-scripts/skills/write-shell-scripts/ -> plugins/write-bash-scripts/skills/write-bash-scripts/
```

Second `git mv` after the parent rename.

### 3. Update plugin metadata

**`plugins/write-bash-scripts/.claude-plugin/plugin.json`**

- `"name"`: `write-shell-scripts` -> `write-bash-scripts`
- `"description"`: "...editing shell scripts" -> "...editing Bash scripts"
- Bump `"version"`: `1.0.5` -> `2.0.0` (breaking: renamed plugin)

**`.claude-plugin/marketplace.json`** (lines 539-541)

- `"name"`: `write-shell-scripts` -> `write-bash-scripts`
- `"source"`: `./plugins/write-shell-scripts` -> `./plugins/write-bash-scripts`
- `"version"`: `1.0.5` -> `2.0.0`

### 4. Update skill definition

**`plugins/write-bash-scripts/skills/write-bash-scripts/SKILL.md`**

- Frontmatter `name`: `write-shell-scripts` -> `write-bash-scripts`
- Frontmatter `description`: "...editing shell scripts" -> "...editing Bash scripts"
- Use-when clause: "editing existing scripts in /bin/" can stay (generic enough)

### 5. Update plugin README

**`plugins/write-bash-scripts/README.md`**

- Title: "Write Shell Scripts" -> "Write Bash Scripts"
- Subtitle: "...editing shell scripts" -> "...editing Bash scripts"
- Trigger: `/write-shell-scripts` -> `/write-bash-scripts`
- Select text: "Write Shell Scripts" -> "Write Bash Scripts"
- Body text: "shell scripts" -> "Bash scripts" where referring to what this skill covers
- Examples: update trigger text and description references

### 6. Update root README

**`README.md`** (lines 30, 228-233)

- ToC: `[Write Shell Scripts](#write-shell-scripts)` -> `[Write Bash Scripts](#write-bash-scripts)`
- Section heading: `#### Write Shell Scripts` -> `#### Write Bash Scripts`
- Description: "...editing shell scripts" -> "...editing Bash scripts"
- Trigger: `/write-shell-scripts` -> `/write-bash-scripts`
- Details link: `./plugins/write-shell-scripts/README.md` -> `./plugins/write-bash-scripts/README.md`

### 7. Update project structure docs

**`CLAUDE.md`** (lines 314, 319-320)

- Directory tree entries: `write-shell-scripts/` -> `write-bash-scripts/`
- Comment: already says "Bash style guide skill", no change needed

**`AGENTS.md`** (same lines as CLAUDE.md)

- Same directory tree entries

### 8. Update cross-references in other plugins

**`plugins/setup-linters/skills/setup-linters/references/languages/shell.md`** (lines 22, 58, 98)

- `write-shell-scripts` -> `write-bash-scripts` (3 occurrences)

**`plugins/create-plugin/skills/create-plugin/references/readme-updates.md`** (line 214)

- `write-shell-scripts` -> `write-bash-scripts`

**`plugins/create-plugin/skills/create-plugin/references/scripts.md`** (line 15)

- `write-shell-scripts` -> `write-bash-scripts`

**`plugins/create-plugin/skills/create-plugin/references/skill-md.md`** (lines 84, 88)

- `write-shell-scripts` -> `write-bash-scripts`

### 9. Update .shellcheckrc

**`.shellcheckrc`** (line 1)

- Comment: "write-shell-scripts style guide" -> "write-bash-scripts style guide"

### 10. Update user's global CLAUDE.md (outside repo)

**`~/.claude/CLAUDE.md`** (line 101)

- `write-shell-scripts` -> `write-bash-scripts`

### 11. Version bump rationale

- Plugin version: `1.0.5` -> `2.0.0` (major: renamed plugin is a breaking change for existing users)
- Marketplace `metadata.version`: no bump needed (no plugin added or removed, just renamed)

### Not changing

- **Plan docs in `docs/plans/done/`**: archival, left as-is
- **BASH.md reference file**: no name references to update
- **SKILL.md heading "# Bash Style Guide"**: already accurate

## Verification

1. `git diff --stat` to confirm all expected files changed and directories renamed
1. `grep -r "write-shell-scripts" .` should return zero results (excluding `docs/plans/done/`)
1. Run `/check-versions` skill to verify plugin.json and marketplace.json versions match
1. Confirm the skill directory structure is correct: `plugins/write-bash-scripts/skills/write-bash-scripts/SKILL.md`
