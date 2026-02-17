---
name: scaffold-new-repo
description: >-
  Scaffold the universal boilerplate for a new repository: LICENSE, README,
  .gitignore, and optional CLAUDE.md. Use when the user says "scaffold a new
  repo", "new repo", "start a new project", "create a repo", "initialize a
  project", "set up a new repository", or asks to generate the standard
  boilerplate files for a fresh project.
---

# Scaffold New Repo

Generate the language-agnostic foundation files that every new repository starts with.

## Workflow

### 1. Gather Project Information

Collect these parameters from the user (ask for any that are missing):

- **Project name** -- the repository/directory name (kebab-case)
- **Short description** -- one sentence describing the project
- **Project type** -- determines the `.gitignore` contents:
  - Go CLI
  - Go library
  - Shell
  - JavaScript
  - Ruby
  - Generic
- **Include CLAUDE.md?** -- defaults to yes
- **Include docs/plans/?** -- defaults to yes

### 2. Prepare the Directory

If the current directory is empty or the user specifies a directory name:

```bash
mkdir -p PROJECT-NAME
cd PROJECT-NAME
```

If the current directory already has files, confirm with the user before adding boilerplate alongside existing content.

### 3. Initialize Git

Skip if already inside a git repository.

```bash
git init
```

### 4. Generate LICENSE

Create a `LICENSE` file using the MIT license template from `./references/license.md`.

- Set the year to the current year (use `date +%Y`)
- Copyright holder is always **Christopher Boone**

### 5. Generate README.md

Create a `README.md` using the template from `./references/readme.md`.

- Replace the heading with the project name (title case)
- Insert the short description
- Tailor the Installation section placeholder to the project type

### 6. Generate .gitignore

Create a `.gitignore` using the appropriate template from `./references/gitignore.md`, based on the project type selected in step 1.

### 7. Generate CLAUDE.md (Optional)

If the user opted to include CLAUDE.md (the default), create it using the template from `./references/claude-md.md`.

- Replace the heading with the project name (title case)
- Insert the short description in the Project Overview section

### 8. Create docs/plans/ (Optional)

If the user opted to include the plans directory (the default):

```bash
mkdir -p docs/plans
touch docs/plans/.gitkeep
```

### 9. Create Initial Commit

Stage all generated files and create the initial commit:

```bash
git add -A
git commit -S -m "feat: scaffold new repository"
```

### 10. Summary

Print a summary of what was created:

- List every file generated
- Note the project type used for `.gitignore`
- Mention any optional files that were skipped

## Error Handling

- If the target directory already contains a `LICENSE`, `README.md`, or `.gitignore`, ask the user before overwriting
- If `git init` fails, continue generating files but warn the user
- If the user provides an unrecognized project type, fall back to Generic and mention it
