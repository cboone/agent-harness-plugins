# Plan: Create `update-everything` Command

## Context

The `bootstrap-project` skill handles initial project setup by detecting what's needed and running tools in the right order. But there's no equivalent for **maintenance**: checking whether previously-set-up files have drifted from current templates. When a plugin updates its templates (new action versions, improved CI patterns, updated community file formats), existing repos have no way to discover what's stale.

This plan creates an `update-everything` command that audits a repo against the latest plugin templates, identifies what's outdated, and applies targeted updates after user confirmation.

## Approach

Create a new **command** plugin (not a skill). The command file contains inline reference sections with structured comparison checklists (following the same pattern as `setup-ci.md` and `scaffold-go-cli.md`, which inline their templates as H2 Reference sections). The command reads those checklists, audits the target repo's files, presents findings, and applies confirmed updates.

**Scope: update-only.** The command focuses exclusively on auditing and updating files that already exist. Tools that were never set up are noted as "Not detected" with no action offered. Users should run `/bootstrap-project` or individual tools to add new capabilities.

**Why a command, not a skill:**

- The user explicitly requested a command (branch: `create-update-everything-command`)
- Should never auto-trigger from casual conversation (too disruptive)
- Matches the pattern of other setup/scaffolding tools in the repo, which are all commands
- Creates clear symmetry: `bootstrap-project` (skill) sets things up, `update-everything` (command) keeps them current

**Why structural checklists, not byte-for-byte diffs:**

- Templates contain placeholders (`PROJECT-NAME`, `GITHUB-USERNAME`) that are substituted during setup, so diffs would show 100% difference
- Semantic checks ("uses actions/checkout@v6", "has timeout-minutes") are more meaningful
- Checklists are human-readable and maintainable
- Claude can execute checks using Read and Grep natively

## File Structure

```text
plugins/update-everything/
  .claude-plugin/
    plugin.json
  README.md
  commands/
    update-everything.md
```

No separate `references/` directory. The comparison checklists are inlined as Reference sections at the bottom of the command file, following the established pattern (e.g., `setup-ci.md` has 1,228 lines with inline reference/template sections).

## Files to Create

### 1. `plugins/update-everything/commands/update-everything.md`

The main command file. Frontmatter:

```yaml
---
description: Audit a repository against the latest plugin templates and update anything out of date.
disable-model-invocation: true
---
```

Workflow steps:

#### Step 1: Detect Project Type

Same detection table as `bootstrap-project` step 1. Scan for `go.mod`, `package.json`, `Cargo.toml`, etc. to classify the project.

#### Step 2: Detect Which Tools Have Been Used

Check for signature artifacts of each tool:

| Tool                    | Key artifacts                                                                              |
| ----------------------- | ------------------------------------------------------------------------------------------ |
| scaffold-new-repo       | LICENSE, README.md, CHANGELOG.md, AGENTS.md                                                |
| scaffold-go-cli         | go.mod + cmd/, .goreleaser.yml, release workflow                                           |
| scaffold-go-library     | go.mod (no cmd/), .golangci.yml, CI workflow                                               |
| setup-ci                | .github/workflows/ci.yml, Makefile                                                         |
| setup-linters           | .editorconfig, .prettierrc.json, linter configs                                            |
| setup-secret-scanning   | gitleaks.yml, trufflehog.yml                                                               |
| add-goreleaser-homebrew | .goreleaser.yml, release workflow                                                          |
| add-community-files     | CONTRIBUTING.md, CODE_OF_CONDUCT.md, .github/SECURITY.md, .github/PULL_REQUEST_TEMPLATE.md |
| add-scrut-cli-tests     | tests/scrut/                                                                               |
| setup-installers        | install.sh, Formula/                                                                       |
| optimize-runner-usage   | concurrency groups in workflows                                                            |
| clean-up-agent-config   | AGENTS.md, CLAUDE.md symlink, .claude/settings.json                                        |

For each tool, record: detected (yes/no), which artifacts found, which missing.

#### Step 3: Compare Against Latest Templates

For each detected tool, run through its checklist (from the Reference sections at the bottom of this command file) by reading the target repo's files and checking for the specified patterns. Skip tools marked "Not detected" or "Not applicable".

For each failed check, record: the file, what's wrong, and the recommended fix.

#### Step 4: Build and Present the Update Plan

Present a table:

```text
| # | Tool                  | Status         | Issues Found                                  | Action          |
|---|-----------------------|----------------|-----------------------------------------------|-----------------|
| 1 | setup-ci              | Needs update   | actions/checkout@v4 (current: v6), no timeout | Update workflow |
| 2 | setup-linters         | Up to date     |                                               | None            |
| 3 | setup-secret-scanning | Partially set  | TruffleHog workflow missing                   | Add workflow    |
| 4 | add-community-files   | Needs update   | CoC is v2.1, current is v3.0                  | Update CoC      |
| 5 | add-scrut-cli-tests   | Not detected   |                                               | None            |
| 6 | setup-installers      | Not applicable |                                               | None            |
```

Status values:

- **Up to date**: all checks pass
- **Needs update**: files exist but fail some checks
- **Partially set up**: some expected files are missing entirely
- **Not detected**: tool was never used (use `/bootstrap-project` or the individual tool to set it up)
- **Not applicable**: tool doesn't apply to this project type

#### Step 5: User Confirmation

Ask the user which items to act on. Only items with status "Needs update" or "Partially set up" are actionable. They can:

- Confirm all actionable items
- Skip specific items
- Select individual items

#### Step 6: Execute Updates

Two strategies depending on the scope:

| Scenario                                               | Strategy                                                                                                                  |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| Action version outdated                                | **Targeted**: find and replace the version string in the workflow file                                                    |
| Missing config entry (e.g., .gitignore line)           | **Targeted**: add the missing entry                                                                                       |
| Missing file from a detected tool ("Partially set up") | **Full tool re-run**: invoke the original skill (via Skill tool) or read the original command .md and follow its workflow |
| Structural mismatch (e.g., wrong CoC version)          | **Targeted replacement** or full re-run depending on scope                                                                |

For full tool re-runs:

- **Skills** (add-community-files, setup-linters): invoke via the Skill tool
- **Commands** (setup-ci, setup-secret-scanning, etc.): use Glob to find the command .md file path, Read it, and follow its workflow instructions directly

#### Step 7: Summary

Report what was updated, what was skipped, and any issues. Suggest next steps:

- Run `/lint-and-fix` to check formatting
- Commit the changes
- Push and verify CI passes

### 2. Inline Reference Sections (at the bottom of `update-everything.md`)

The command file ends with H2 Reference sections containing the comparison checklists. These are the "brain" of the comparison logic. The command's workflow Step 3 instructs Claude to consult these sections.

Sections to include:

**Reference: Action Versions** (shared table of current expected versions, extracted from the latest command templates during implementation):

| Action                        | Current Version                   |
| ----------------------------- | --------------------------------- |
| actions/checkout              | (from setup-ci.md)                |
| actions/setup-go              | (from setup-ci.md)                |
| golangci/golangci-lint-action | (from setup-ci.md)                |
| gitleaks/gitleaks-action      | (from setup-secret-scanning.md)   |
| trufflesecurity/trufflehog    | (from setup-secret-scanning.md)   |
| goreleaser/goreleaser-action  | (from add-goreleaser-homebrew.md) |
| (etc.)                        |                                   |

**Reference: Per-tool Checklists** -- one section per tool, each listing:

- Files to check
- Specific attributes to verify per file
- What a failure looks like vs. what the fix is

Tools to cover: scaffold-new-repo, setup-ci, setup-linters, setup-secret-scanning, add-community-files, add-goreleaser-homebrew, optimize-runner-usage, clean-up-agent-config, add-scrut-cli-tests, setup-installers.

Example checklist for setup-ci:

- ci.yml: uses current action versions, has `permissions:` block, has `concurrency:` group, has `timeout-minutes:` on all jobs, Go projects use `go-version-file: go.mod`, has `paths-ignore:`, has `workflow_dispatch:` trigger
- Makefile: has expected targets (test, lint, fmt, vet for Go; test, lint for JS; etc.)

Example checklist for scaffold-new-repo:

- LICENSE: is MIT, copyright year is current
- .gitignore: has common entries (.DS_Store, .claude/settings.local.json, .env, etc.)
- Agent config: CLAUDE.md is a symlink to AGENTS.md, .claude/settings.json exists, .github/copilot-instructions.md exists

Example checklist for add-community-files:

- CODE_OF_CONDUCT.md: is Contributor Covenant v3.0 (not older versions)
- CONTRIBUTING.md: references correct build/test/lint commands, has Conventional Commits section
- .github/SECURITY.md: uses GitHub private vulnerability reporting
- .github/PULL_REQUEST_TEMPLATE.md: exists

### 3. `plugins/update-everything/.claude-plugin/plugin.json`

```json
{
  "author": {
    "name": "Christopher Boone"
  },
  "commands": "./commands",
  "description": "Audit a repository against the latest plugin templates and update anything out of date.",
  "homepage": "https://github.com/cboone/cboone-cc-plugins",
  "keywords": ["audit", "ci", "linters", "scaffolding", "templates", "update"],
  "license": "MIT",
  "name": "update-everything",
  "repository": "https://github.com/cboone/cboone-cc-plugins",
  "version": "1.0.0"
}
```

### 4. `plugins/update-everything/README.md`

Standard per-plugin README with:

- Type: Command
- Trigger: `/update-everything`
- What It Does: describes the audit-compare-confirm-update flow
- Usage section
- See Also: links to bootstrap-project, optimize-runner-usage

## Files to Modify

### 5. `.claude-plugin/marketplace.json`

- Add `update-everything` entry (alphabetically after `use-git`)
- Bump `metadata.version` from `1.20.0` to `1.21.0`

### 6. Root `README.md`

**ToC**: Add under **Commands** > **Scaffolding**, after Setup Installers (since U > S alphabetically):

```markdown
∙ [Update Everything](#update-everything)
```

**Description section**: Add under `## Commands` > `### Scaffolding`, after Setup Installers:

```markdown
#### Update Everything

Audit a repository against the latest plugin templates and update anything out of date. The maintenance companion to Bootstrap Project: bootstrap sets things up, this keeps them current. Detects which tools have been used, compares files against current templates, presents a plan, and applies confirmed updates.

> **Trigger:** `/update-everything`
> **Details:** [README](./plugins/update-everything/README.md)
```

### 7. `CLAUDE.md`

Add `update-everything/` to the directory tree in the project structure section, with the correct file listing.

## Implementation Order

1. Read all command templates to extract current action versions and checklist data
2. Create `plugins/update-everything/.claude-plugin/plugin.json`
3. Create `plugins/update-everything/commands/update-everything.md` (main command with inline reference sections)
4. Create `plugins/update-everything/README.md`
5. Update `.claude-plugin/marketplace.json`
6. Update root `README.md` (ToC + description)
7. Update `CLAUDE.md` (directory tree)

## Key Files to Reference During Implementation

- `plugins/bootstrap-project/skills/bootstrap-project/SKILL.md` -- primary pattern for detection tables, plan presentation, execution dispatch
- `plugins/bootstrap-project/skills/bootstrap-project/references/overlap-rules.md` -- overlap rules to respect during full tool re-runs
- `plugins/setup-secret-scanning/commands/setup-secret-scanning.md` -- representative command with inline templates to extract current action versions from
- `plugins/setup-ci/commands/setup-ci.md` -- CI templates with action versions
- `plugins/scaffold-go-cli/commands/scaffold-go-cli.md` -- Go CLI templates
- `plugins/add-community-files/skills/add-community-files/references/` -- community file templates
- `plugins/setup-linters/skills/setup-linters/references/` -- linter config templates
- `plugins/create-plugin/skills/create-plugin/references/` -- plugin creation conventions

## Verification

1. **Structure check**: Run the `/check-versions` skill to verify plugin.json and marketplace.json are consistent
2. **Dry run**: In a test repo that has been bootstrapped with these plugins, run `/update-everything` and verify it:
   - Correctly detects the project type
   - Identifies which tools have been used
   - Runs comparison checklists without errors
   - Presents a clear, accurate plan table
   - Respects user selections during confirmation
   - Applies targeted updates correctly
   - Produces a useful summary
3. **Lint**: Run `/lint-and-fix` on the new files

## Maintenance Consideration

The inline Reference sections in `update-everything.md` must be kept in sync with template changes across other plugins. When a command or skill template changes (new action version, new best practice), the corresponding checklist entry should be updated. A note about this should be added to the command file itself, and ideally to the `create-plugin` skill's documentation.
