# Add shfmt to check-zsh skill

## Context

shfmt has gained some zsh support. It should be added as the 8th tool in the check-zsh skill, alongside beautysh as another formatter with auto-fix capability. The plugin hasn't been pushed yet, so no version bump is needed.

## Changes

### 1. Create `plugins/check-zsh/skills/check-zsh/references/tools/shfmt.md`

New reference file documenting shfmt's zsh support, commands, installation, and limitations.

### 2. Update `plugins/check-zsh/skills/check-zsh/SKILL.md`

- Add shfmt as tool #8 in the Tool Overview table (after beautysh, as another formatter)
- Add step 3h in the workflow for running `shfmt -d <file>` (check) / `shfmt -w <file>` (fix)
- Update step 5 (Fix Issues) to include shfmt alongside beautysh for auto-fixing
- Add shfmt to the description frontmatter tool list

### 3. Update `plugins/check-zsh/README.md`

- Add shfmt to the "What It Does" description
- Add shfmt to the Requirements section
- Add `Bash(shfmt *)` to the Recommended Permissions section

### 4. Update `plugins/check-zsh/.claude-plugin/plugin.json`

- Add "shfmt" to keywords array (alphabetically)

### 5. Update `.claude-plugin/marketplace.json`

- Add "shfmt" to the check-zsh entry's keywords array (alphabetically)

### 6. Update `AGENTS.md` (via CLAUDE.md symlink)

- Add `shfmt.md` to the check-zsh directory tree (alphabetically between `shellharden.md` and `zcompile.md`)

### 7. Update `README.md`

- Add shfmt to the check-zsh description section's Requires line

### 8. Commit staged lint fixes first

There are staged but uncommitted lint fixes from the previous `lint-and-fix` run that need to be committed first.

## Verification

- `jq . < plugins/check-zsh/.claude-plugin/plugin.json` parses
- `jq . < .claude-plugin/marketplace.json` parses
- Keywords match between plugin.json and marketplace.json
- shfmt.md exists in references/tools/
- SKILL.md references shfmt.md
