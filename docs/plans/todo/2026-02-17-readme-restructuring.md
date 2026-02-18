# README Restructuring: Per-Plugin READMEs and Better Grouping

## Context

The root README has grown unwieldy — it contains detailed descriptions of all 20 plugins in a single file, with subcategories ("Agents", "Workflow", "Languages") that don't meaningfully distinguish plugins. The "Workflow" bucket alone holds 12 plugins. No plugin has its own README, so users must scroll through one long document to find what they need.

This plan creates per-plugin READMEs with richer user-facing documentation, simplifies the root README to concise summaries with links, and reorganizes plugins into thematic groups that reflect how they're actually used together.

## New Thematic Groupings

**Skills:**

| Subcategory | Plugins | Rationale |
|---|---|---|
| **Git** | commit, merge-main, pr, review-branch | The core commit-to-PR pipeline |
| **Issues and Worktrees** | create-worktree, create-worktree-from-issue, suggest-next-issue | Multi-agent and issue-driven work |
| **Code Review** | address-review, resolve-copilot-pr-feedback | Responding to external feedback |
| **Code Quality** | lint-and-fix, write-go-code, write-markdown, write-shell-scripts | Proactive style and lint enforcement |
| **Scaffolding** | scaffold-go-cli, scaffold-new-repo, setup-gitleaks | Project and repo setup |
| **Agents** | clean-up-agent-config, create-plugin | Meta-tools for the agent ecosystem |

**Hooks** (unchanged):

| Subcategory | Plugins |
|---|---|
| **Security** | block-rm-rf |
| **Workflow** | notify |

## Per-Plugin README Template

Each `plugins/<name>/README.md` is user-facing documentation (distinct from the agent-facing SKILL.md). Structure:

```markdown
# Plugin Name

One-sentence description.

**Type:** Skill | Hook
**Trigger:** `/plugin-name` [(also activates automatically)]

## What It Does

2-4 sentences describing the outcome for the user. Focus on what the user
gets, not internal agent workflow.

## Requirements

(Only if external dependencies exist.)

- [`dependency`](URL) — install via Homebrew: `brew install dependency`

## Usage

For skills: the trigger command and any flags/options.
For hooks: what events fire it and what happens.

## Examples

Trigger phrases or usage scenarios.

## See Also

- [All plugins](../../README.md)
```

Variations:
- **Hooks** (block-rm-rf, notify): No trigger/options. "Usage" becomes "When It Fires".
- **Style guides** (write-go-code, write-markdown, write-shell-scripts): Note automatic activation. Mention the reference structure.
- **Simple skills** with no options: Omit the options from Usage.

## Root README Changes

1. **ToC** — New subcategories replacing Agents/Workflow/Languages
2. **Descriptions** — Shrink from 3-8 sentences to 1-2 sentences
3. **Details links** — Each entry gets a link to its per-plugin README
4. **Structure** — Keep Installation section as-is; keep License as-is

Each plugin entry in the root README becomes:

```markdown
### Plugin Name

One-to-two sentence summary.

> **Trigger:** `/plugin-name`
> **Requires:** [`dep`](URL)
> **Details:** [README](./plugins/plugin-name/README.md)
```

## Files to Create (20)

- `plugins/address-review/README.md`
- `plugins/block-rm-rf/README.md`
- `plugins/clean-up-agent-config/README.md`
- `plugins/commit/README.md`
- `plugins/create-plugin/README.md`
- `plugins/create-worktree/README.md`
- `plugins/create-worktree-from-issue/README.md`
- `plugins/lint-and-fix/README.md`
- `plugins/merge-main/README.md`
- `plugins/notify/README.md`
- `plugins/pr/README.md`
- `plugins/resolve-copilot-pr-feedback/README.md`
- `plugins/review-branch/README.md`
- `plugins/scaffold-go-cli/README.md`
- `plugins/scaffold-new-repo/README.md`
- `plugins/setup-gitleaks/README.md`
- `plugins/suggest-next-issue/README.md`
- `plugins/write-go-code/README.md`
- `plugins/write-markdown/README.md`
- `plugins/write-shell-scripts/README.md`

## Files to Modify (3)

- **`README.md`** — New groupings, shorter descriptions, details links
- **`plugins/create-plugin/skills/create-plugin/references/readme-updates.md`** — Add per-plugin README template; update ToC subcategory names from Agents/Workflow/Languages to the new six groups; add step for creating the per-plugin README
- **`CLAUDE.md`** — Update ToC subcategory names in the "README ToC Format" section; add `README.md` to the plugin directory tree entries

## Implementation Order

1. Write all 20 per-plugin READMEs (parallelizable — these are independent)
2. Rewrite root `README.md` with new groupings and condensed descriptions
3. Update `create-plugin` reference (`readme-updates.md`) with new template and subcategories
4. Update `CLAUDE.md` with new ToC format and directory tree

## Verification

- Every plugin directory contains a `README.md`
- Root README links to each per-plugin README (all 20 relative paths valid)
- Root README ToC follows CLAUDE.md format rules (one entry per line, middle dots, `<br>Name:` subcategories)
- `create-plugin` reference documentation matches the new patterns
- CLAUDE.md directory tree includes `README.md` in each plugin entry
- Run `write-markdown` lint skill to verify Markdown conventions
