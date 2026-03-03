# Add cspell to Lint Setup and Running

## Context

Spell checking is a universal code quality concern that applies to all projects, yet the `setup-linters` and `lint-and-fix` plugins currently have no cspell support. Adding cspell as a cross-language tool (alongside Prettier, EditorConfig, markdownlint) lets projects catch spelling errors in source code, comments, strings, and documentation.

## Changes

### 1. New file: `plugins/setup-linters/skills/setup-linters/references/tools/cspell.md`

Create a tool reference following the pattern of `markdownlint.md`, `yamllint.md`, `knip.md`:

- **When to Offer**: All projects (spelling errors are universal)
- **Install**: npm/yarn/pnpm/bun (`npm install -D cspell`)
- **Config**: `cspell.json` template with sensible `ignorePaths` defaults (node_modules, vendor, dist, lock files, etc.)
- **Optional**: `cspell-words.txt` pattern for project-specific dictionary
- **Commands**: `npx cspell .`, `npx cspell . --unique --words-only --no-progress` (for building word lists)
- **package.json scripts**: `spell`, `spell:list`
- **Configuration options table**: language, words, ignorePaths, ignoreWords, flagWords, dictionaries, enabledFileTypes
- **Notes**: No auto-fix mode; built-in language dictionaries; no conflict with Prettier; monorepo override support

### 2. Edit: `plugins/setup-linters/skills/setup-linters/references/checklist.md`

Add cspell row to the "Cross-Language and File-Type Tools" table (after yamllint):

| Tool | Scope | When to Offer | Install Command | Config Files | Reference |
| --- | --- | --- | --- | --- | --- |
| cspell | Spelling in code/docs | All projects | `npm install -D cspell` | `cspell.json` | `./tools/cspell.md` |

### 3. Edit: `plugins/setup-linters/skills/setup-linters/SKILL.md`

Three additions:

- **Step 2 detection table** (after Taplo row): Add `cspell.json`, `.cspell.json`, `cspell.config.*` to cspell detection
- **Step 3 recommendations** (after yamllint bullet): Add `cspell` as a cross-language spell checker for all projects
- **Step 8 CI tool dependency table** (after actionlint row): Add `cspell | streetsidesoftware/cspell-action@v6`

### 4. Edit: `plugins/lint-and-fix/skills/lint-and-fix/SKILL.md`

Two additions:

- **Detection table** (after knip row, before package.json row): Add cspell row with no auto-fix and `npx cspell .` as check command
- **Step 3a tool-specific notes** (after knip note): Add cspell note explaining no auto-fix, users fix typos or add words to dictionary

### 5. Edit: `plugins/setup-linters/skills/setup-linters/references/tools/github-actions-ci.md`

Add cspell to the "Cross-Language Steps" section (after yamllint, before "Combined Multi-Language Workflow"):

```yaml
- name: cspell
  uses: streetsidesoftware/cspell-action@v6
```

### 6. Version bumps and keyword updates

| File | Version change | Keyword addition |
| --- | --- | --- |
| `plugins/setup-linters/.claude-plugin/plugin.json` | 1.3.0 -> 1.4.0 | Add `"cspell"` |
| `plugins/lint-and-fix/.claude-plugin/plugin.json` | 1.2.1 -> 1.3.0 | Add `"cspell"` |
| `.claude-plugin/marketplace.json` setup-linters entry | 1.3.0 -> 1.4.0 | Add `"cspell"` |
| `.claude-plugin/marketplace.json` lint-and-fix entry | 1.2.1 -> 1.3.0 | Add `"cspell"` |

Both are minor bumps (new capability). The marketplace `metadata.version` stays at 1.18.0 (no plugins added or removed).

### 7. Edit: `plugins/lint-and-fix/README.md`

- **"What It Does"** (line 20): Add cspell to the tool list
- **Recommended Permissions** (line 46): Add `"Bash(npx cspell*)"` to the allow array

### 8. Edit: `README.md` (root)

- **Lint and Fix description** (line 180): Add cspell to the supported tools list
- **Setup Linters description** (line 215): Add cspell to the cross-language tools parenthetical

## Key design decisions

- **All projects scope**: Like Prettier and EditorConfig, cspell applies universally
- **No auto-fix**: cspell joins shellcheck, knip, and yamllint as a check-only tool in lint-and-fix
- **npm-based install**: cspell is a Node.js tool; non-Node projects can use `npx cspell .` without installing
- **GitHub Action**: `streetsidesoftware/cspell-action@v6` (official action from cspell maintainers), consistent with the pattern of using dedicated actions

## Files touched

| File | Action |
| --- | --- |
| `plugins/setup-linters/skills/setup-linters/references/tools/cspell.md` | Create |
| `plugins/setup-linters/skills/setup-linters/references/checklist.md` | Edit |
| `plugins/setup-linters/skills/setup-linters/SKILL.md` | Edit |
| `plugins/lint-and-fix/skills/lint-and-fix/SKILL.md` | Edit |
| `plugins/setup-linters/skills/setup-linters/references/tools/github-actions-ci.md` | Edit |
| `plugins/setup-linters/.claude-plugin/plugin.json` | Edit |
| `plugins/lint-and-fix/.claude-plugin/plugin.json` | Edit |
| `.claude-plugin/marketplace.json` | Edit |
| `plugins/lint-and-fix/README.md` | Edit |
| `README.md` | Edit |

## Verification

1. Confirm cspell.json detection patterns match what cspell actually uses (verify against cspell docs)
2. Run `check-versions` skill to verify version consistency between plugin.json and marketplace.json
3. Verify all markdown files pass markdownlint (table alignment, heading levels)
4. Verify the new cspell.md reference file follows the same structure as existing tool references
5. Check that the detection table entries in lint-and-fix SKILL.md maintain consistent column alignment
