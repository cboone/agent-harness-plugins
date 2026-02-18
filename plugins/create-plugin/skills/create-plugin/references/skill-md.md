# SKILL.md Reference

Each skill has a `SKILL.md` file that defines how Claude Code should behave when the skill is triggered.

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
  One-paragraph description of what the skill does and when to use it.
  Include trigger phrases so Claude Code knows when to activate the skill
  automatically. Use the YAML folded block scalar (>-) for multi-line
  descriptions.
---
```

### Name

- Must match the skill directory name
- Kebab-case

### Description

The description serves as the skill's trigger mechanism. It should include:

1. **What the skill does** (first sentence)
1. **When to use it** -- list trigger phrases the user might say (e.g., "create a plugin", "add a new skill")
1. **Prerequisites** if any (e.g., "Requires the gh CLI to be installed")

#### Examples from Existing Skills

**Workflow skill:**

```yaml
description: >-
  Find a GitHub issue in the current repository and create a new git worktree,
  branch, and tmux window for working on it using workmux. Use when the user
  says "start issue", "work on issue", "create worktree from issue",
  "create worktree for issue", or references starting work on a GitHub issue
  by number (e.g., "#42") or by description (e.g., "the dark mode issue").
  Requires the gh CLI and workmux to be installed.
```

**Style guide skill:**

```yaml
description: >-
  Applies Bash style conventions when creating or editing shell scripts.
  Use when: (1) creating new shell scripts, (2) editing existing scripts in /bin/,
  or (3) reviewing Bash code for bugs or style issues.
```

## Body Structure

After the frontmatter, the body follows this general pattern:

### H1 Title

A human-readable title for the skill (title case).

### Opening Line

One sentence summarizing the skill's purpose.

### Common Sections

Skills in this repository use these sections as applicable:

| Section                   | Purpose                                            | Used by                            |
| ------------------------- | -------------------------------------------------- | ---------------------------------- |
| `## Options`              | User-configurable parameters                       | suggest-next-issue                 |
| `## Workflow`             | Step-by-step numbered process (`### 1. Step Name`) | All workflow skills                |
| `## Key Conventions`      | Summary of rules (for style guide skills)          | write-shell-scripts, write-go-code |
| `## Reference Navigation` | Pointers to reference files by topic               | write-go-code                      |
| `## Example Output`       | Sample output in a code block                      | suggest-next-issue                 |
| `## Error Handling`       | Bullet list of failure modes and recovery          | All skills                         |
| `## Sources`              | Attribution links                                  | write-go-code, write-shell-scripts |

### Workflow Steps

Number steps with `### N. Step Name` under a `## Workflow` section. Include bash code blocks where commands are needed:

````markdown
### 1. Gather Context

Run these commands to build a complete picture:

```bash
gh issue list --state open --json number,title,labels
```
````

### Reference File Pointers

When the skill has reference files, point to them with relative paths:

```markdown
Read `./references/BASH.md` for the complete guide.
```

Or with a navigation table:

```markdown
- `references/essential/checklist.md` - Condensed, actionable rules
- `references/comprehensive/naming.md` - Package names, identifiers, receivers
```

## Notes

- Skills can have a flat `references/` directory or a categorized one (e.g., `references/essential/`, `references/comprehensive/`)
- Keep the SKILL.md focused on workflow and orchestration; put detailed reference material in separate files under `references/`
- All paths in SKILL.md are relative to the skill directory
