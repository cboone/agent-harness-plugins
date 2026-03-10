# Upgrade Commands with Argument Hints

## Context

The Ralph Wiggum plugin in the official Claude Code repository demonstrates two command features we underutilize: `argument-hint` (which shows ghost text inline at the prompt when typing a command) and `$ARGUMENTS`/`$1` positional argument handling. Of our 10 command plugins, only `setup-installers` uses `argument-hint`. This plan adds argument hints and corresponding `$ARGUMENTS` support to the 5 commands where arguments add genuine value, following the pattern already established by `setup-installers`.

Two other Ralph features were evaluated and deemed not applicable:

- **`allowed-tools`**: Ralph restricts tools because its commands are thin wrappers around scripts. Our commands need broad tool access (Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion). Listing everything provides no restriction benefit and adds maintenance cost.
- **Scripts (`scripts/` directory)**: Ralph's commands execute bash scripts. Our commands are long prompt-driven workflows that guide Claude through complex multi-step procedures. The reasoning and decision-making cannot be extracted to scripts. No scripts are added.

## Changes

### 5 commands get `argument-hint` + `$ARGUMENTS` handling

#### 1. scaffold-new-repo (v1.4.5 -> v1.5.0)

**Files:**

- `plugins/scaffold-new-repo/commands/scaffold-new-repo.md`
- `plugins/scaffold-new-repo/.claude-plugin/plugin.json`

**Frontmatter addition:**

```yaml
argument-hint: "[project-name] [--type TYPE]"
```

**Content change** in step 1 ("Gather Project Information"), add before the bullet list:

> If `$ARGUMENTS` is provided, parse it for a project name (first positional word) and/or a `--type TYPE` flag. If a project name is present, use it directly instead of detecting from git remote or README. If `--type` is present, use the specified type instead of inferring from `.gitignore`. Valid types: `go-cli`, `go-library`, `javascript`, `pascal`, `python`, `ruby`, `rust`, `shell`, `swift`, `generic`. Any remaining parameters should still be gathered normally.

#### 2. scaffold-go-cli (v2.4.0 -> v2.5.0)

**Files:**

- `plugins/scaffold-go-cli/commands/scaffold-go-cli.md`
- `plugins/scaffold-go-cli/.claude-plugin/plugin.json`

**Frontmatter addition:**

```yaml
argument-hint: "[project-name]"
```

**Content change** in step 1 ("Gather Project Information"), add before the bullet list:

> If `$ARGUMENTS` is provided, use it as the project name and skip asking for it. Still ask for the remaining parameters (description, Viper, Charmbracelet TUI) unless already provided in the user's initial request.

#### 3. scaffold-go-library (v1.5.0 -> v1.6.0)

**Files:**

- `plugins/scaffold-go-library/commands/scaffold-go-library.md`
- `plugins/scaffold-go-library/.claude-plugin/plugin.json`

**Frontmatter addition:**

```yaml
argument-hint: "[project-name]"
```

**Content change** in step 1 ("Gather Project Information"), add before the bullet list:

> If `$ARGUMENTS` is provided, use it as the project name and skip asking for it. Still ask for the remaining parameters (description, minimum Go version, example tests) unless already provided in the user's initial request.

#### 4. setup-ci (v1.2.0 -> v1.3.0)

**Files:**

- `plugins/setup-ci/commands/setup-ci.md`
- `plugins/setup-ci/.claude-plugin/plugin.json`

**Frontmatter addition:**

```yaml
argument-hint: "[go-cli|go-library|javascript|python|rust|ruby|shell]"
```

**Content change** in step 1 ("Detect Project Type"), add before the table:

> If `$ARGUMENTS` specifies a language (e.g., `go-cli`, `go-library`, `javascript`, `python`, `rust`, `ruby`, `shell`), use it directly instead of scanning for markers. Still perform sub-detection steps as needed (e.g., JS package manager detection for `javascript`, or verifying `main.go`/`cmd/` for `go-cli` vs `go-library`).

#### 5. setup-secret-scanning (v2.1.0 -> v2.2.0)

**Files:**

- `plugins/setup-secret-scanning/commands/setup-secret-scanning.md`
- `plugins/setup-secret-scanning/.claude-plugin/plugin.json`

**Frontmatter addition:**

```yaml
argument-hint: "[gitleaks|trufflehog|both]"
```

**Content change** in step 2 ("Choose Scanning Tools"), add before the bullet list:

> If `$ARGUMENTS` specifies a tool selection (`gitleaks`, `trufflehog`, or `both`), use it directly instead of asking the user.

### 5 commands get no changes

These commands don't have meaningful arguments to expose:

- **add-goreleaser-homebrew**: always adds GoReleaser + Homebrew to Go CLI projects, no parameterization needed
- **add-scrut-cli-tests**: auto-detects project type and binary; nothing to parameterize
- **optimize-runner-usage**: scans all workflows; the point is comprehensive coverage
- **update-everything**: audits everything; selective auditing would undermine the purpose
- **setup-installers**: already has `argument-hint` and `$ARGUMENTS` support

### Marketplace and version sync

- Update `marketplace.json` version entries for the 5 modified plugins to match their new `plugin.json` versions
- Marketplace `metadata.version` stays at `1.23.0` (no plugins added or removed)

### Frontmatter field ordering

Follow the existing `setup-installers` convention:

```yaml
---
description: ...
disable-model-invocation: true
argument-hint: "..."
---
```

## Implementation sequence

1. Update `scaffold-new-repo` (frontmatter + content + plugin.json)
1. Update `scaffold-go-cli` (frontmatter + content + plugin.json)
1. Update `scaffold-go-library` (frontmatter + content + plugin.json)
1. Update `setup-ci` (frontmatter + content + plugin.json)
1. Update `setup-secret-scanning` (frontmatter + content + plugin.json)
1. Update `marketplace.json` (5 version entries)
1. Run `check-versions` skill to verify consistency

## Files to modify

- `plugins/scaffold-new-repo/commands/scaffold-new-repo.md`
- `plugins/scaffold-new-repo/.claude-plugin/plugin.json`
- `plugins/scaffold-go-cli/commands/scaffold-go-cli.md`
- `plugins/scaffold-go-cli/.claude-plugin/plugin.json`
- `plugins/scaffold-go-library/commands/scaffold-go-library.md`
- `plugins/scaffold-go-library/.claude-plugin/plugin.json`
- `plugins/setup-ci/commands/setup-ci.md`
- `plugins/setup-ci/.claude-plugin/plugin.json`
- `plugins/setup-secret-scanning/commands/setup-secret-scanning.md`
- `plugins/setup-secret-scanning/.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`

## Verification

1. After each command update, invoke the command in Claude Code (e.g., `/scaffold-new-repo`) and confirm the ghost text appears inline at the prompt
1. Test with arguments (e.g., `/scaffold-new-repo my-project --type go-cli`) and verify the argument is used to skip detection
1. Test without arguments and verify the interactive flow still works as before
1. Run `check-versions` to verify all plugin.json and marketplace.json versions match
