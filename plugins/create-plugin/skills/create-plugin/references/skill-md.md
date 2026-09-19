# SKILL.md Reference

<!-- The bin/ and docs/ paths below name files in this repository, not in a project a skill runs against. -->
<!-- validate-plugins: repository-paths -->

<!-- The reference paths below illustrate how a skill being authored points at its own material; they are not this skill's reference files. -->
<!-- validate-plugins: ignore ./references/BASH.md ./references/languages/go.md ./references/tools/actionlint.md -->

Each skill has a canonical `SKILL.md` file that defines the workflow an agent follows when the skill is triggered, shared by Claude Code, Codex CLI, and OpenCode. Codex consumes generated copies under `dist/codex/plugins/*`; do not edit those copies by hand. Write steps with the conventions in the "Cross-harness workflow adapters" section of `docs/plugin-development.md`.

## File Location

```text
plugins/PLUGIN-NAME/skills/SKILL-NAME/SKILL.md
```

The skill directory name usually matches the plugin name (e.g., `plugins/suggest-next-issue/skills/suggest-next-issue/SKILL.md`).

## Frontmatter

The file starts with YAML frontmatter containing exactly two fields:

```yaml
---
name: skill-name
description: >-
  The primary action first, then the trigger phrases that should activate
  the skill. Use the YAML folded block scalar (>-) for multi-line
  descriptions.
---
```

### Name

- Must match the skill directory name
- Kebab-case

### Description

The description is the skill's routing description: harnesses use it to decide when to activate the skill, and selectors show it beside the skill's name. It is separate from the catalog summary in `marketplace.json`, which is written for people browsing the catalog (see "Routing descriptions and catalog summaries" in `docs/plugin-development.md`). It should:

1. **Open with the primary action**, so a description shortened from the end still routes
1. **Name the trigger phrases** a user might say (e.g., "create a plugin", "add a new skill"), preferring those that distinguish the skill from adjacent skills
1. **State a negative boundary** when an adjacent skill would otherwise activate instead
1. **Mention a prerequisite** only when it affects selection (e.g., "Requires the gh CLI")

Keep it short, because every installed skill's description shares Codex's discovery budget.

Every harness routes on this description: `bin/build-codex-marketplace` copies `SKILL.md` into `dist/codex/` unchanged, and the OpenCode mirror links to it. Change it here. The plugin `description` in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` is the separate catalog summary and does not affect routing.

#### Examples from Existing Skills

**Workflow skill:**

```yaml
description: >-
  Merge the base branch into the current branch, resolve conflicts, and push.
  Use for "merge main" or "sync with main"; to rebase, use rebase-onto-main.
```

**Style guide skill:**

```yaml
description: >-
  Apply Bash style conventions when creating, editing, or reviewing Bash
  scripts. Not for zsh; use write-zsh-scripts.
```

## Body Structure

After the frontmatter, the body follows this general pattern:

### H1 Title

A human-readable title for the skill (title case).

### Opening Line

One sentence summarizing the skill's purpose.

### Common Sections

Skills in this repository use these sections as applicable:

| Section                   | Purpose                                            | Used by                             |
| ------------------------- | -------------------------------------------------- | ----------------------------------- |
| `## Options`              | User-configurable parameters                       | suggest-next-issue                  |
| `## Skill dependencies`   | Required and optional skills the workflow invokes  | Workflow skills that compose others |
| `## Workflow`             | Step-by-step numbered process (`### 1. Step Name`) | All workflow skills                 |
| `## Key Conventions`      | Summary of rules (for style guide skills)          | write-bash-scripts, write-go-code   |
| `## Reference Navigation` | Pointers to reference files by topic               | write-go-code                       |
| `## Example Output`       | Sample output in a code block                      | suggest-next-issue                  |
| `## Error Handling`       | Bullet list of failure modes and recovery          | All skills                          |
| `## Sources`              | Attribution links                                  | write-go-code, write-bash-scripts   |

### Workflow Steps

Number steps with `### N. Step Name` under a `## Workflow` section. Include bash code blocks where commands are needed:

````markdown
### 1. Gather Context

Run these commands to build a complete picture:

```bash
gh issue list --state open --json number,title,labels
```
````

### Skill Dependencies

When a step uses another skill, write it as "Invoke the `NAME` skill", pass its arguments, and name the step to resume from when it returns. Declare every skill the workflow invokes, including from reference files, in a section placed before `## Workflow`:

```markdown
## Skill dependencies

- **Required:** `NAME`
- **Optional:** None
```

A required skill is one the workflow cannot honestly complete the dependent step without; an optional one has a documented fallback or omission. Write `None` for an empty category, and list every candidate as optional when the user selects which skills run. Before a step that needs a required skill, confirm the skill is available. If it is not, report the skill and how to install it, and stop before any dependent side effect instead of substituting another workflow. The "Skill dependencies" section of `docs/plugin-development.md` has copyable examples.

### Reference File Pointers

When the skill has reference files, point to them with relative paths:

```markdown
Read `./references/BASH.md` for the complete guide.
```

Or with a navigation table:

```markdown
- `./references/languages/go.md` - Go-specific setup guidance
- `./references/tools/actionlint.md` - actionlint installation and usage
```

## Notes

- Workflow skills use flat `references/` with topic-named files by default. When a workflow skill needs subdirectories, use topical names such as `languages/`, `tools/`, or `scripts/`, not `essential/` plus `comprehensive/`
- Style-guide skills, primarily `write-*`, may use a single canonical topic document such as `BASH.md` or split reference material into `essential/` plus `comprehensive/`. That split is for quick-reference versus deep-reference reading modes, not file count
- Keep the SKILL.md focused on workflow and orchestration; put detailed reference material in separate files under `references/`
- All paths in SKILL.md are relative to the skill directory
