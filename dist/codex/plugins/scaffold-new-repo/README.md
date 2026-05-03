# Scaffold New Repo

Scaffold the universal boilerplate for any new repository, regardless of language.

**Type:** Skill
**Trigger:** `/scaffold-new-repo`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Scaffold New Repo** from the available plugins.

## What It Does

Generates LICENSE (MIT), README.md, a project-type-specific `.gitignore`, agent config files (`AGENTS.md`, `CLAUDE.md` symlink, `.claude/settings.json`, `.github/copilot-instructions.md`), and a `docs/plans/` directory. Infers the project type from an existing `.gitignore` when possible. Supports Go CLI, Go library, Shell, JavaScript, Ruby, Zig CLI, and generic project types.

## Usage

```text
/scaffold-new-repo
```

The skill prompts for project name, description, and type during setup.

## Examples

- "scaffold a new repo": starts the interactive scaffolding process
- "new repo": same behavior
- "start a new project": same behavior

## See Also

- [Scaffold Go CLI](../scaffold-go-cli/README.md): Go CLI-specific scaffolding (includes this boilerplate)
- [Setup Secret Scanning](../setup-secret-scanning/README.md): add secret scanning after scaffolding
- [All plugins](../../../../README.md)
