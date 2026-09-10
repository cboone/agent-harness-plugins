# Add a Contents section to the root README

## Context

The root `README.md` is 225 lines covering 51 plugins across nine categories, four top-level prose sections, and two harness-specific guides. A reader landing on it gets the intro paragraph and then drops straight into `## Install` with no map of what the file holds. Only two intra-document links exist today (`#using-with-codex-cli` and `#using-with-opencode`, both inline prose cross-references), so there is no way to jump to a section without scrolling.

This adds a compact `## Contents` navigation block between the intro paragraph and `## Install`.

### Why this contradicts existing guidance, and why it is still correct

The README previously had a table of contents. Commit `5bc0daec` ("docs: rewrite README as compact catalog tables") removed it, taking the file from 562 lines to 215. That old TOC was a flat list of all 51 plugin names linking to per-plugin H4 anchors, so it duplicated the category tables outright and went stale on every plugin addition. Three places now record a rule against re-adding it:

- `plugins/create-plugin/skills/create-plugin/SKILL.md:170`
- `plugins/create-plugin/skills/create-plugin/references/readme-updates.md:3`
- `AGENTS.md`, `## README catalog format` (lines 136-152), by omission

The `readme-updates.md` wording carries an explicit escape hatch: "unless the root README is intentionally redesigned again." This is that redesign, and the new section is a different artifact from the one that was removed: it navigates **sections**, not plugins. Nothing in it changes when a plugin is added, which was the whole failure mode of the old TOC. The guardrails get rewritten in this same change so they forbid the plugin-level list while requiring the section-level one, rather than being left to contradict the file they describe.

### Decisions already made

- **Form**: compact bullet list, one line per H2, with `Install` and `Skills` naming their H3s inline.
- **No counts.** No "51 plugins", no per-category totals. Adding a plugin must not require touching this section, and without counts it does not.
- **Scope includes the guardrails**, which means a `create-plugin` version bump and a mirror rebuild.

## Constraints discovered during exploration

These are the real limits on the change; everything else in the repo is indifferent to the root README.

1. **Nothing programmatically parses the root README.** `bin/validate-plugins` (18 rules) only checks that each `plugins/<name>/README.md` _exists_ (lines 31-38); it never opens the root file. `bin/validate-json` walks JSON only. `bin/build-codex-marketplace` rewrites link prefixes inside _plugin_ READMEs only. `bin/build-opencode-mirror` ignores READMEs entirely. No script counts rows, checks section order, or requires a row per plugin.

2. **Do not rename or duplicate three headings.** 53 plugin READMEs link into the root README's headings, validated by the `markdownlint-rule-relative-links` custom rule wired up in `cli.markdownlint-cli2.jsonc:34`:
   - `../../README.md#install` × 51
   - `../../README.md#using-with-opencode` × 1
   - `../../README.md#codex-cli-known-limitations` × 1

   Adding a second heading that slugifies to `install` would push the real one to `install-1` and fail all 51 at once. `## Contents` collides with nothing.

3. **MD051 is enabled at default** (not configured in `.markdownlint.jsonc`). Every `](#anchor)` must match a real heading slug in the same file, case-sensitively. This is the rule that will catch a typo'd anchor, and it is the primary automated check on this change.

4. **The root README is Prettier-formatted and CI-checked.** It is not in `.prettierignore`; `.github/workflows/ci.yml:34-35` runs `yarn lint` → `markdownlint-cli2` + `prettier --check .`. With `printWidth: 10000` and `proseWrap: "preserve"`, Prettier will not rewrap the long `Skills` line, but the committed form must match Prettier's exact output.

5. **MD004 requires `-` list markers**; MD032 requires blank lines around the list. MD024 is `siblings_only`, so `## Contents` is safe.

6. **`tests/scrut/repo-tooling.md:87`** greps `README.md` for space-padded angle-bracket placeholders (`< foo >`). Irrelevant here, but do not introduce that pattern.

## Changes

### 1. `README.md`

Insert between the intro paragraph (line 3) and `## Install` (line 5), verbatim:

```markdown
## Contents

- [Install](#install): [Claude Code](#claude-code), [Codex CLI](#codex-cli), [OpenCode](#opencode)
- [Skills](#skills): [Git](#git), [Issues and Worktrees](#issues-and-worktrees), [Code Review](#code-review), [Code Quality](#code-quality), [Writing](#writing), [Scaffolding](#scaffolding), [CI and Release](#ci-and-release), [Agents](#agents)
- [Hooks](#hooks)
- [Using with Codex CLI](#using-with-codex-cli), [Using with OpenCode](#using-with-opencode)
- [License](#license)
```

Every anchor above was checked against the current heading inventory and resolves. No existing heading is renamed, moved, or removed, so all 53 inbound cross-links keep working.

The two existing prose cross-references at lines 23 and 31 stay as they are. They say "below" and serve a different purpose (pointing a reader mid-install at the caveats), so they are not redundant with the Contents block.

### 2. `plugins/create-plugin/skills/create-plugin/SKILL.md:170`

Replace:

> Do not add a root README table of contents, H3 plugin-description section, or individual install command. The root README now uses category tables, and the marketplace flow handles installation.

With wording that preserves the real prohibition while protecting the new section. The replacement must say: do not add H3 plugin-description sections or per-plugin install commands; do not list individual plugins in the root README's `## Contents` section, because it navigates headings rather than plugins; a new plugin therefore never changes it.

### 3. `plugins/create-plugin/skills/create-plugin/references/readme-updates.md:3`

Replace the second sentence of the opening paragraph the same way. Keep the first sentence ("When adding a new plugin, update the compact category table...") intact. State positively that a new plugin does not touch `## Contents`, and that adding a whole new _category_ does.

### 4. `AGENTS.md`, `## README catalog format`

Add a paragraph after line 138 (the paragraph describing the category tables) covering:

- A `## Contents` section sits between the intro paragraph and `## Install`; it is section-level navigation, one bullet per H2, with `Install` and `Skills` naming their H3s inline.
- It never lists individual plugins, so adding a plugin does not touch it. Update it only when an H2 or a skills category is added, renamed, or removed.
- Every anchor must resolve, because MD051 checks them.
- **Do not rename `## Install`, `## Using with OpenCode`, or `### Codex CLI known limitations`.** 53 plugin READMEs link to those three slugs and `markdownlint-rule-relative-links` fails the build if they move. This is load-bearing repo knowledge that is currently written down nowhere.

`AGENTS.md` is symlinked as `CLAUDE.md`, so edit `AGENTS.md` only. `.github/copilot-instructions.md` has no README-catalog section and needs no change; confirmed by grep.

### 5. Version and catalog bookkeeping

Editing anything under `plugins/create-plugin/` requires the standard sequence from `AGENTS.md`:

1. Bump `plugins/create-plugin/.claude-plugin/plugin.json` version `1.2.9` → `1.2.10` (patch: wording change to skill instructions).
1. Set the matching `create-plugin` entry in `.claude-plugin/marketplace.json` to `1.2.10`. The two must agree; `bin/validate-plugins` enforces it.
1. Recompute `metadata.version` by running `bin/compute-catalog-state` and writing its output into `.claude-plugin/marketplace.json`. Current value is `catalog-M63-m93-p142-n51`; the patch sum should advance by one, but take the script's output as authoritative rather than hand-computing.
1. Regenerate both mirrors and commit the results: `bin/build-codex-marketplace` and `bin/build-opencode-mirror`. This refreshes `dist/codex/plugins/create-plugin/skills/create-plugin/{SKILL.md,references/readme-updates.md}` and `.agents/plugins/marketplace.json`.

Never hand-edit anything under `dist/` or `.agents/`.

The root README itself is not mirrored anywhere, so change 1 on its own would need none of this. The bookkeeping exists solely because of changes 2 and 3.

## Verification

Run from the worktree root, in order:

```bash
make format      # normalize to Prettier's exact output before checking
make lint        # markdownlint (MD051 anchors + the 53 cross-file fragments) + prettier --check + shellcheck + shfmt + actionlint
make validate    # bin/validate-json + bin/validate-plugins (version agreement, catalog state tag)
make build       # regenerate both mirrors
make test-all    # lint + validate + scrut
```

Then confirm the generated trees are committed and not drifting:

```bash
git status --porcelain dist/ .agents/    # must be empty after committing the rebuild
```

Targeted checks beyond the make targets:

- **Anchor resolution**: `make lint` is authoritative here. MD051 fails on any `](#anchor)` with no matching heading, so a green Markdown lint proves all 17 new links resolve. For a manual cross-check, compare `grep -n '](#' README.md` against `grep -n '^#\{1,3\} ' README.md`.
- **Inbound cross-links intact**: also covered by `make lint` via `markdownlint-rule-relative-links`. A regression here shows up as ~51 simultaneous failures in `plugins/*/README.md`, which is unmistakable.
- **Rendered output**: view the README on the PR page and click through each Contents link. GitHub's slugger and MD051's agree, but this is the only check that catches a link that resolves yet points somewhere surprising.
- **Versions**: run the repo-local `check-versions` skill after the bump and before opening the PR, since another branch may have already moved `create-plugin`.

## Commit sequence

Two logical commits, per the repo's small-commit convention:

1. `docs: add a Contents section to the root README` (change 1).
1. `docs: document the README Contents section in create-plugin and AGENTS.md` (changes 2-5, including the version bump and regenerated mirrors, since the bump exists only to carry the skill edits).

This repo is a `cboone` repo, so this plan file is committed and kept.
