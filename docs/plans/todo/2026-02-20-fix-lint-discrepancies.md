# Fix Lint Discrepancies

## Context

Two open issues and a broader style guide audit reveal inconsistencies between what the project's linter/formatter configs enforce and what the code style guides teach. This plan addresses:

- **Issue #101**: Broken shellcheck disable directives in `resolve-copilot-threads`
- **Issue #100**: shfmt vs prettier-plugin-sh conflict in lint skills
- **Style alignment**: BASH.md and MARKDOWN.md examples and recommendations out of sync with linter/formatter enforcement

Guiding principle: adjust linters/formatters to match the guides when possible; adjust guides to match linters/formatters when no config option exists.

---

## 1. Fix shellcheck directive placement (issue #101)

**File:** `plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads`

**Root cause:** `# shellcheck disable=SC2016` applies to the next command only. At lines 159 and 270, `local response` sits between the directive and `response="$("`, so the directive covers the harmless `local` instead.

**Fix:** At both locations, move `local response` above the directive:

```bash
# Before (broken):
  # shellcheck disable=SC2016
  # $variables in the query are GraphQL references, not shell variables
  local response
  response="$(

# After (fixed):
  local response

  # shellcheck disable=SC2016
  # $variables in the query are GraphQL references, not shell variables
  response="$(
```

**Version bump:** `resolve-copilot-pr-feedback` 1.1.6 -> 1.1.7 (patch)

---

## 2. Add prettier-plugin-sh conflict detection (issue #100)

### 2a. `plugins/lint-and-fix/skills/lint-and-fix/SKILL.md`

- **Detection table** (line 39): Add footnote `(*)` to shfmt row. After the table, add note: skip shfmt when `prettier-plugin-sh` is in the project's dependencies.
- **Detection step 3** (line 49): Note that shfmt is conditional on prettier-plugin-sh not being present.
- **Error handling** (line 175): Expand "Conflicting tools" bullet to include shfmt/prettier-plugin-sh case.

**Version bump:** `lint-and-fix` 1.0.1 -> 1.1.0 (minor: new capability)

### 2b. `plugins/setup-linters/skills/setup-linters/references/languages/shell.md`

- **Tools section** (line 6): Add `prettier-plugin-sh` as a third tool option.
- **Notes section** (end): Add warning not to use both formatters together.
- **New section** at end: "prettier-plugin-sh (Alternative to shfmt)" with when-to-choose guidance, install, config example, and explicit "do not use both" warning.

### 2c. `plugins/setup-linters/skills/setup-linters/references/tools/prettier.md`

- **Plugins list** (line 112): Expand `prettier-plugin-sh` entry with conflict warning and cross-reference.

### 2d. `plugins/setup-linters/skills/setup-linters/references/checklist.md`

- **Shell row** (line 15): Update "ShellCheck + shfmt" to "ShellCheck + shfmt (or prettier-plugin-sh)".

**Version bump:** `setup-linters` 1.0.0 -> 1.1.0 (minor: new content)

### 2e. `plugins/write-shell-scripts/README.md`

- **See Also** (line 40): Update "run ShellCheck and shfmt" to "run ShellCheck and shfmt (or prettier-plugin-sh)".

**Version bump:** `write-shell-scripts` 1.0.5 -> 1.0.6 (patch: wording tweak)

---

## 3. Align BASH.md with prettier-plugin-sh formatting

**File:** `plugins/write-shell-scripts/skills/write-shell-scripts/references/BASH.md`

prettier-plugin-sh (as configured in `.prettierrc.json5`) enforces specific formatting that some BASH.md examples don't reflect. Discrepancies and fixes:

### 3a. Heredoc spacing (no config option available)

prettier-plugin-sh adds a space after `<<`. There is no option to disable this.

**Heredoc quoting** (lines 131-133): Change `<<'EOF'` to `<< 'EOF'` and `<<EOF` to `<< EOF`.
**Heredoc naming** (lines 141-143): Change `<<'SQL_QUERY'` to `<< 'SQL_QUERY'` and `<<'EOF'` to `<< 'EOF'`.

### 3b. Multi-line operator placement (`binaryNextLine: true`)

When expressions wrap to multiple lines, prettier-plugin-sh places binary operators (`|`, `&&`, `||`) at the start of the next line. Short one-liners that fit within `printWidth` are not affected.

Current BASH.md examples are all short enough to stay inline, so no existing examples need reformatting. However, the guide lacks guidance on multi-line style. **Add a new subsection** (after "Simple conditionals", around line 697) covering multi-line continuation:

````markdown
### Multi-line continuation

When a pipeline or logical expression spans multiple lines, place the operator at the start of the continuation line:

| Use                                | Avoid                            |
| ---------------------------------- | -------------------------------- |
| `command \`<br>`  \| next_command` | `command \|`<br>`  next_command` |

\```bash

# Use: operator at start of continuation line

result="$(
generate_data \
 | filter \
 | transform
)"

# Avoid: operator at end of line

result="$(
generate_data |
filter |
transform
)"
\```
````

**Version bump:** `write-shell-scripts` 1.0.6 -> 1.1.0 (minor: new guidance section). Combined with the 2e patch bump, the net change from main is 1.0.5 -> 1.1.0.

---

## 4. Align MARKDOWN.md with markdownlint config

### 4a. Enable MD049 enforcement

**File:** `.markdownlint.jsonc`

The guide recommends `_italic_` (underscores for emphasis) but MD049 is disabled, so nothing enforces it. Enable it:

```jsonc
"MD049": { "style": "underscore" },
```

This aligns the linter with the guide. No change to MARKDOWN.md needed (it already recommends `_italic_`).

### 4b. Document custom markdownlint rules

**File:** `plugins/write-markdown/skills/write-markdown/references/MARKDOWN.md`

The markdownlint-cli2 config enforces three custom rules not mentioned in the style guide. Add a new section (near the end, before Sources) documenting:

- **`@github/markdownlint-github`**: GitHub-specific Markdown rules (accessible images, no generic link text, etc.)
- **`markdownlint-rule-force-align-table-columns`**: Enforces aligned table columns (already described in Table column alignment section, but the custom rule should be cross-referenced)
- **`markdownlint-rule-relative-links`**: Validates that relative links point to existing files

**Version bump:** `write-markdown` 1.1.1 -> 1.2.0 (minor: new content)

---

## Discrepancies reviewed and found aligned (no changes needed)

- **Redirection spacing**: BASH.md shows `< file` (space), matches `spaceRedirects: true`
- **Case indentation**: BASH.md indents case arms, matches `switchCaseIndent: true`
- **2-space indent**: All BASH.md examples use 2-space indent, matches `indent: 2`
- **Bold emphasis**: MARKDOWN.md says `**bold**`, matches MD050 `"style": "asterisk"`
- **Heading style**: MARKDOWN.md says ATX (`#`), matches MD003 `"style": "atx"`
- **List markers**: MARKDOWN.md says dashes, matches MD004 `"style": "dash"`
- **Ordered lists**: MARKDOWN.md says all `1.`, matches MD029 `"style": "one"`
- **Horizontal rules**: MARKDOWN.md says `---`, matches MD035 `"style": "---"`
- **Code fences**: MARKDOWN.md says backticks, matches MD048 `"style": "backtick"`
- **SCRUT.md**: No discrepancies found. Scrut blocks use the `scrut` language tag, which Prettier doesn't recognize, so no formatting conflicts.

---

## Version bumps (all files)

| Plugin                      | Old   | New   | Reason                        |
| --------------------------- | ----- | ----- | ----------------------------- |
| resolve-copilot-pr-feedback | 1.1.6 | 1.1.7 | Patch: bug fix                |
| lint-and-fix                | 1.0.1 | 1.1.0 | Minor: new conflict detection |
| setup-linters               | 1.0.0 | 1.1.0 | Minor: new content            |
| write-shell-scripts         | 1.0.5 | 1.1.0 | Minor: new guidance + wording |
| write-markdown              | 1.1.1 | 1.2.0 | Minor: new content            |

Each bumped in both `plugin.json` and `.claude-plugin/marketplace.json`. Marketplace `metadata.version` stays unchanged (no plugins added or removed).

---

## Commit strategy

Four commits:

1. `fix: correct shellcheck disable directive placement in resolve-copilot-threads`
1. `fix: detect prettier-plugin-sh to avoid shfmt conflicts in lint skills`
1. `docs: align BASH.md examples with prettier-plugin-sh formatting`
1. `docs: enable MD049 underscore enforcement and document custom markdownlint rules`

---

## Verification

1. `shellcheck plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads` produces zero output
1. `yarn lint` passes (Markdown + Prettier checks)
1. `bin/validate-plugins` passes
1. `bin/validate-json` passes
