# Command .md Reference

Each command plugin has a Markdown file that defines a slash command Claude Code can execute. Commands are user-invoked (via `/command-name`) and run a structured workflow.

## File Location

```text
plugins/PLUGIN-NAME/commands/COMMAND-NAME.md
```

The command filename (without `.md`) becomes the slash command name. The command name usually matches the plugin name (e.g., `plugins/setup-ci/commands/setup-ci.md` becomes `/setup-ci`).

## Frontmatter

The file starts with YAML frontmatter:

```yaml
---
description: One-sentence summary of what the command does.
disable-model-invocation: true
argument-hint: "[arg-name]"
---
```

### Fields

| Field                      | Required    | Description                                                                                        |
| -------------------------- | ----------- | -------------------------------------------------------------------------------------------------- |
| `description`              | Yes         | One-sentence summary shown in the command list. Start with a verb.                                 |
| `disable-model-invocation` | Conditional | Set to `true` to prevent Claude from invoking this command automatically. Convention in this repo.  |
| `argument-hint`            | Optional    | Hint shown after the command name in autocomplete (e.g., `"[project-name]"`, `"[go-cli\|python]"`) |
| `allowed-tools`            | Optional    | Comma-separated list of tools the command may use. Omit to allow all tools.                        |
| `model`                    | Optional    | Override the model for this command (e.g., `"sonnet"`). Omit to use the default.                   |

### Conventions in This Repo

- All commands set `disable-model-invocation: true` to prevent accidental automatic execution
- Use `argument-hint` when the command accepts arguments to improve discoverability

## Arguments

Commands can access user-provided arguments via special variables:

| Variable     | Description                                          |
| ------------ | ---------------------------------------------------- |
| `$ARGUMENTS` | The full argument string after the command name      |
| `$1`         | First positional argument (space-delimited)          |
| `$2`         | Second positional argument                           |
| `$3`         | Third positional argument (and so on for `$4`, etc.) |

### Examples from This Repo

**Single argument** (`/scaffold-go-cli my-tool`):

```markdown
If `$ARGUMENTS` is provided, use it as the project name and skip asking for it.
```

**Argument with options** (`/scaffold-new-repo my-project --type go-cli`):

```markdown
If `$ARGUMENTS` is provided, parse it for a project name (first positional word)
and/or a `--type TYPE` flag.
```

**Enum argument** (`/setup-secret-scanning both`):

```markdown
If `$ARGUMENTS` specifies a tool selection (`gitleaks`, `trufflehog`, or `both`),
use it directly instead of asking the user.
```

## External File References

Commands can include content from external files using the `@${CLAUDE_PLUGIN_ROOT}` pattern:

```markdown
@${CLAUDE_PLUGIN_ROOT}/references/template-name.md
```

At runtime, Claude Code resolves `${CLAUDE_PLUGIN_ROOT}` to the plugin's root directory and injects the referenced file's content into the command context.

### When to Extract

Extract inline templates into reference files when:

- The command file exceeds ~400 lines
- Templates are independently referenceable (e.g., different CI workflow templates for different languages)
- Multiple sections share the same template content

### Reference File Location

```text
plugins/PLUGIN-NAME/references/FILE-NAME.md
```

Place reference files alongside the `commands/` directory, not inside it:

```text
plugins/PLUGIN-NAME/
  .claude-plugin/
    plugin.json
  commands/
    command-name.md
  references/
    template-a.md
    template-b.md
```

### Reference File Format

Each reference file is standalone Markdown. Use an H1 title, then the template content in a fenced code block, followed by a Notes section:

```markdown
# Template Name

Description of what this template is for.

## Template

\`\`\`yaml
template content here
\`\`\`

## Notes

- Key details about the template
```

## Body Structure

After the frontmatter, the body follows this pattern:

### H1 Title

A human-readable title for the command (title case).

### Opening Line

One sentence summarizing the command's purpose.

### `## Workflow` Section

Step-by-step numbered process using `### N. Step Name` subheadings. Include bash code blocks for commands the agent should run. Reference `$ARGUMENTS` in early steps for argument handling.

### `## Error Handling` Section

Bullet list of failure modes and recovery steps.

### `## Reference:` Sections (inline) or File References

For smaller commands, include templates inline using `## Reference: Template Name` sections with a horizontal rule (`---`) separator between sections.

For larger commands, replace inline sections with `@${CLAUDE_PLUGIN_ROOT}/references/file.md` file references.

## Advanced Patterns

For advanced command features (interactive user prompts, bash execution blocks, multi-step argument parsing), see the official `plugin-dev` plugin's `command-development` skill.
