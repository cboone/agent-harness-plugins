# Trim Setup Skill Descriptions

## Context

Seven scaffolding/setup skills are always explicitly invoked (via `/skill-name`) and used at most once per project. Their SKILL.md `description` fields include verbose "Use when the user says..." trigger phrases that consume context in every session despite never being needed for auto-discovery. Trimming these descriptions to just the core functionality statement cuts context usage roughly in half for each skill while preserving the skill format and references directory structure.

## Approach

For each of the 7 skills, edit the `description` field in the SKILL.md frontmatter to remove the "Use when the user says..." trigger phrases, keeping only the first sentence that describes what the skill does.

## Changes

### 1. `plugins/scaffold-new-repo/skills/scaffold-new-repo/SKILL.md`

**Before:**

```yaml
description: >-
  Scaffold the universal boilerplate for a new repository: LICENSE, README,
  .gitignore, agent config files, and a plans directory. Use when the user says
  "scaffold a new repo", "new repo", "start a new project", "create a repo",
  "initialize a project", "set up a new repository", or asks to generate the
  standard boilerplate files for a fresh project.
```

**After:**

```yaml
description: >-
  Scaffold the universal boilerplate for a new repository: LICENSE, README,
  .gitignore, agent config files, and a plans directory.
```

### 2. `plugins/scaffold-go-cli/skills/scaffold-go-cli/SKILL.md`

**Before:**

```yaml
description: >-
  Scaffold a complete Go CLI project with Cobra, GoReleaser, GitHub Actions CI/CD,
  Homebrew tap, and Makefile. Use when the user says "scaffold go cli", "new go cli",
  "create go cli", "scaffold go project", "new go project", "start a go cli", or asks
  to generate boilerplate for a Go command-line tool.
```

**After:**

```yaml
description: >-
  Scaffold a complete Go CLI project with Cobra, GoReleaser, GitHub Actions
  CI/CD, Homebrew tap, and Makefile.
```

### 3. `plugins/scaffold-go-library/skills/scaffold-go-library/SKILL.md`

**Before:**

```yaml
description: >-
  Scaffold a Go library project with GoReleaser changelog releases, golangci-lint,
  GitHub Actions CI/CD, and Makefile. Use when the user says "scaffold go library",
  "new go library", "create go library", "scaffold go package", "new go package",
  "start a go library", or asks to generate boilerplate for a Go library or package.
```

**After:**

```yaml
description: >-
  Scaffold a Go library project with GoReleaser changelog releases,
  golangci-lint, GitHub Actions CI/CD, and Makefile.
```

### 4. `plugins/add-goreleaser-homebrew/skills/add-goreleaser-homebrew/SKILL.md`

**Before:**

```yaml
description: >-
  Add GoReleaser configuration and a GitHub Actions release workflow to an
  existing Go CLI project with Homebrew tap publishing. Use when the user says
  "add goreleaser", "add homebrew", "add release workflow", "set up goreleaser",
  "set up homebrew tap", "add goreleaser homebrew", "configure releases",
  "add release pipeline", or asks to add automated releases or Homebrew
  distribution to an existing Go project.
```

**After:**

```yaml
description: >-
  Add GoReleaser configuration and a GitHub Actions release workflow to an
  existing Go CLI project with Homebrew tap publishing.
```

### 5. `plugins/add-scrut-cli-tests/skills/add-scrut-cli-tests/SKILL.md`

**Before:**

```yaml
description: >-
  Set up scrut snapshot-based CLI integration testing for a CLI project.
  Use when the user says "add scrut tests", "add CLI tests", "set up scrut",
  "add e2e tests", "add integration tests", "scrut cli tests",
  "add snapshot tests", or asks to set up CLI integration testing with scrut
  for any CLI project.
```

**After:**

```yaml
description: >-
  Set up scrut snapshot-based CLI integration testing for a CLI project.
```

### 6. `plugins/setup-gitleaks/skills/setup-gitleaks/SKILL.md`

**Before:**

```yaml
description: >-
  Set up gitleaks secret scanning with a GitHub Actions workflow and optional
  configuration. Use when the user says "set up gitleaks", "add gitleaks",
  "add secret scanning", "set up secret scanning", "gitleaks scanning",
  "setup gitleaks", or asks to add secret detection to a repository's CI
  pipeline.
```

**After:**

```yaml
description: >-
  Set up gitleaks secret scanning with a GitHub Actions workflow and optional
  configuration.
```

### 7. `plugins/setup-linters/skills/setup-linters/SKILL.md`

**Before:**

```yaml
description: >-
  Detect project languages, recommend appropriate linters and formatters,
  install them, and generate config files. Use when the user says "set up
  linters", "add linting", "set up eslint", "add prettier", "set up ruff",
  "add formatting", "configure linters", "add code quality
  tools", "setup linters", or asks to add linting or formatting to a project.
```

**After:**

```yaml
description: >-
  Detect project languages, recommend appropriate linters and formatters,
  install them, and generate config files.
```

## Verification

1. Run `git diff` to confirm only the 7 SKILL.md frontmatter `description` fields changed
2. Verify each trimmed description ends with a period and reads as a complete sentence
3. Start a new Claude Code session and confirm the 7 skills still appear in the skills listing with their shortened descriptions
4. Invoke one skill (e.g., `/setup-gitleaks`) to confirm it still loads and works correctly
