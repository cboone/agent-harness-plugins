---
name: create-tmux-plugin
description: >-
  Scaffold a tmux plugin with TPM Redux conventions: entry point, helpers, scripts
  directory, and README with install sections. Use when the user says "create tmux
  plugin", "new tmux plugin", "scaffold tmux plugin", "start a tmux plugin", or asks
  to generate boilerplate for a tmux plugin.
---

# Create Tmux Plugin

Generate the full boilerplate for a new tmux plugin following TPM Redux conventions.

## Workflow

### 1. Gather Project Information

Ask the user for these parameters:

- **Plugin name** -- kebab-case, `tmux-` prefix suggested but not required (e.g., `tmux-my-plugin`)
- **Short description** -- one sentence, used in the README heading area
- **Configurable options** -- a list of logical option names (without the `@PLUGIN-NAME-` prefix), their defaults, and a brief description of what each controls. The skill constructs the full tmux option key as `@PLUGIN-NAME-<option>` automatically.

If the user already provided some or all of these in their initial request, do not re-ask. Derive what you can from context.

If the user does not specify any configurable options, generate a single example option: `@PLUGIN-NAME-enabled` with default `on` and description "Enable or disable the plugin. Set to `off` to disable." This ensures the helpers and option-reading pattern is demonstrated, not inert.

### 2. Detect User Identity

Detect the user's GitHub username and full name for use in templates:

```bash
# GitHub username (for repository URLs, install instructions)
gh api user -q .login
```

```bash
# Full name (for LICENSE copyright)
git config user.name
```

If either command fails or produces no output, ask the user to provide the value. Use the GitHub username wherever templates reference `GITHUB-USERNAME` and the full name wherever they reference `COPYRIGHT-HOLDER`.

### 3. Verify the Target Directory

The project should be scaffolded in a directory named after the plugin. If the current directory is already named after the plugin and is empty (or nearly empty), use it. Otherwise, create a subdirectory.

If the directory already contains `.tmux` files, warn the user before proceeding.

### 4. Initialize Git

Skip if already inside a git repository.

```bash
git init
```

### 5. Generate Entry Point

Create `PLUGIN-NAME.tmux` in the project root using the template from `./references/entry-point.md`.

- Replace `PLUGIN-NAME` with the plugin name
- Replace `OPTION-NAME` and `OPTION-DEFAULT` with the first configurable option's logical name and default value (or the generated example option). The template's `@PLUGIN-NAME-OPTION-NAME` placeholder produces the full tmux option key.

Mark the file executable:

```bash
chmod +x PLUGIN-NAME.tmux
```

### 6. Generate helpers.sh

Create `scripts/helpers.sh` using the template from `./references/helpers.md`.

This file is identical across all tmux plugins. Use it verbatim with no replacements.

### 7. Generate Main Script

Create `scripts/PLUGIN-NAME.sh` using the template from `./references/main-script.md`.

- Replace `PLUGIN-NAME` with the plugin name

Mark the file executable:

```bash
chmod +x scripts/PLUGIN-NAME.sh
```

### 8. Generate LICENSE

Create `LICENSE` using the template from `./references/license.md`.

- Replace `YEAR` with the current year (run `date +%Y` to get it)
- Replace `COPYRIGHT-HOLDER` with the detected full name

### 9. Generate README.md

Create `README.md` using the template from `./references/readme.md`.

- Replace `PLUGIN-NAME` with the plugin name (kebab-case)
- Replace `PLUGIN-TITLE` with the plugin name in title case
- Replace `PLUGIN-DESCRIPTION` with the short description
- Replace `GITHUB-USERNAME` with the detected GitHub username
- Replace `OPTIONS-TABLE` with a Markdown table of all configurable options

### 10. Ask About Optional Features

Ask the user whether they want any of these optional additions:

- **Scrut test skeleton** -- creates a `Makefile` with test targets and a `tests/` directory with a starter test file
- **GitHub Actions CI** -- creates `.github/workflows/scrut.yml` for running scrut tests in CI (implies scrut test skeleton)
- **Workmux layout** -- creates a `.workmux.yaml` file for workmux-based development

### 11. Generate Optional Files

Based on the user's choices in step 10:

**Scrut test skeleton** (or implied by GitHub Actions CI):

- Create `Makefile` with `test` and `test-update` targets that run scrut
- Create `tests/` directory with a starter `help.md` test file

**GitHub Actions CI**:

- Create `.github/workflows/scrut.yml` with a workflow that installs scrut and runs `make test`

**Workmux layout**:

- Create `.workmux.yaml` with the plugin name as the session name and a single pane

If the user declines all optional features, skip this step entirely.

### 12. Create Initial Commit

Stage all generated files and create the initial commit:

```bash
git add -A
git commit -S -m "feat: scaffold tmux plugin"
```

### 13. Summary

Print a summary of what was created:

- List every file generated
- Show the configurable options table
- Remind the user to:
  - Implement the plugin logic in `scripts/PLUGIN-NAME.sh`
  - Create a GitHub repository and push to enable TPM Redux installs
  - Add more options by extending the entry point and README
  - Test locally with `tmux source-file ~/.tmux.conf` after adding the plugin to their config

## Error Handling

- If the plugin name does not start with `tmux-`, warn the user that the convention is to prefix tmux plugin names with `tmux-`, but allow them to proceed
- If the target directory already contains `.tmux` files, ask the user before overwriting
- If `git init` fails, continue generating files but warn the user
- If `gh api user` fails, fall back to asking the user for their GitHub username
- If `git config user.name` fails, fall back to asking the user for their full name
