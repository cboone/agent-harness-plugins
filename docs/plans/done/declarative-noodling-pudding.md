# 2026-02-18 Improve READMEs

## Context

The root README and per-plugin READMEs need three improvements:

1. **Group blurbs in root README**: The skills section lists 18 plugins as flat H3 entries with no group-level context. The ToC already organizes plugins into subcategories (Git, Issues and Worktrees, Code Review, Code Quality, Scaffolding, Agents), but the content section does not mirror this grouping. Adding H3 group headers with workflow blurbs, and demoting plugin entries to H4, gives readers orientation before diving into individual plugins.

1. **Em dash removal**: 142 em dashes across README files (root + 20 per-plugin). The user preference forbids em dashes. Replace with colons, commas, periods, or rephrasing.

1. **Plugin installation instructions**: No per-plugin README explains how to install the plugin. Each needs a short Installation section pointing to the marketplace.

1. **Missing content**: The `handle-secrets` plugin has no README at all. It is also missing from the root README's ToC and skills listing.

## Changes

### 1. Root README (`README.md`)

**Structure change**: Add H3 group headers with blurbs, demote plugin entries to H4.

```text
## Skills                        (stays H2)
### Git                          (new H3 with blurb)
#### Commit                      (was H3, now H4)
#### Merge Main                  (was H3, now H4)
#### PR                          (was H3, now H4)
#### Review Branch               (was H3, now H4)
### Issues and Worktrees         (new H3 with blurb)
#### Create Worktree             (was H3, now H4)
...
## Hooks                         (stays H2)
### Security                     (new H3 with blurb)
#### Block rm -rf                (was H3, now H4)
### Workflow                     (new H3 with blurb)
#### Notify (macOS)              (was H3, now H4)
```

GFM anchors are derived from heading text regardless of level, so all existing ToC links (e.g., `#commit`) remain valid.

**Group blurbs** (draft content, will refine during implementation):

- **Git**: Skills for the commit-to-PR pipeline. Stage, commit, merge, review, and open pull requests without leaving the conversation.
- **Issues and Worktrees**: Parallel development with git worktrees. Pick an issue, spin up an isolated worktree with its own agent session, and let each agent work independently.
- **Code Review**: Process feedback from human reviewers and automated tools. Parse review documents, triage Copilot suggestions, and resolve comments systematically.
- **Code Quality**: Style guides, linters, and security practices. These skills activate automatically when working with their target languages and file types.
- **Scaffolding**: Bootstrap new projects with consistent structure. Generate boilerplate, CI/CD pipelines, and security scanning from templates.
- **Agents**: Meta-tools for the agent ecosystem. Audit agent configuration files and create new plugins.
- **Security** (Hooks): Prevent destructive operations before they happen.
- **Workflow** (Hooks): Stay informed about agent activity.

**Add Handle Secrets**: Insert into the Code Quality group (ToC + content).

**Em dashes**: 2 instances on lines 186 and 193 (Requires lines for hooks). Replace `— install via` with `. Install via`.

### 2. Per-Plugin READMEs (21 files)

For all 20 existing READMEs, plus creating `handle-secrets/README.md`:

**Add Installation section** after the Type/Trigger/Requires metadata block, before "What It Does":

````markdown
## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Plugin Name** from the available plugins.
````

**Remove em dashes** with these substitutions:

| Pattern                                | Replacement                                        |
| -------------------------------------- | -------------------------------------------------- |
| `"command" — description` (Examples)   | `"command": description`                           |
| `[Link](url) — description` (See Also) | `[Link](url): description`                         |
| `— install via` (Requires)             | `. Install via`                                    |
| Prose em dashes                        | Rewrite with colons, commas, or separate sentences |

**Create `plugins/handle-secrets/README.md`** following the existing per-plugin template:

- Title: Handle Secrets
- Type: Skill
- Trigger: `/handle-secrets`
- What It Does: Best practices for handling user-provided secrets in CLI tools (env vars, stdin, keychains, config files)
- Installation section
- Usage, Examples, See Also

### 3. Update Template Reference (`plugins/create-plugin/skills/create-plugin/references/readme-updates.md`)

Remove em dashes from the templates that generate future READMEs:

- Line 107: `— install via` in hook Requires template
- Line 134: `— install via` in Requirements section template
- Line 146: `— brief reason` in See Also template
- Line 158: `— install via` in hook Requires template

Add the Installation section to both the skill and hook README templates.

## Files to Modify

- `README.md` (root)
- `plugins/address-review/README.md`
- `plugins/block-rm-rf/README.md`
- `plugins/clean-up-agent-config/README.md`
- `plugins/commit/README.md`
- `plugins/create-plugin/README.md`
- `plugins/create-worktree/README.md`
- `plugins/create-worktree-from-issue/README.md`
- `plugins/handle-secrets/README.md` (create new)
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
- `plugins/create-plugin/skills/create-plugin/references/readme-updates.md`

Total: 23 files (22 edits + 1 new)

## Not in Scope

- SKILL.md files and other non-README markdown (em dashes exist but are agent-facing, not user-facing)
- Plan files in `docs/plans/` (historical documents)
- Reference files outside the README template (`BASH.md`, `security-hierarchy.md`, etc.)

## Verification

1. Grep for em dashes across all README files: `rg '—' --glob '*/README.md'` should return zero matches
1. Verify no broken links: each See Also link should resolve
1. Verify ToC anchors still work: each `#anchor` in the ToC should match an H3 or H4 heading
1. Run `markdownlint-cli2` on all modified files
1. Verify handle-secrets appears in root README ToC and content
