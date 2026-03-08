# Scaffold Follow-Up Issues and Copilot False Positives

Addresses [#114](https://github.com/cboone/cc-plugins/issues/114) and [#116](https://github.com/cboone/cc-plugins/issues/116).

## Context

After scaffolding a new project, two problems occur:

1. **Lost reminders (#114):** `scaffold-go-cli` prints a reminder about adding `HOMEBREW_TAP_TOKEN` as a repository secret when the user defers setup. This reminder is easy to lose once the conversation ends. The fix is to create a GitHub issue for the deferred item so it becomes trackable.

1. **Copilot false positives (#116):** On the first PR, GitHub Copilot flags several scaffold-generated patterns as issues (golangci-lint v2 config, Prettier `printWidth: 10000`, `go-version-file: go.mod`, golangci-lint-action caching). The fix is to have each scaffold/setup skill append "do not flag" entries to `.github/copilot-instructions.md` for patterns it generates.

## Changes

### 1. `scaffold-go-cli` (issue creation + copilot entries)

**File:** `plugins/scaffold-go-cli/commands/scaffold-go-cli.md`

Add a new **step 19: Update Copilot Instructions** between steps 18 (Create Initial Commit) and the current step 19 (Set Up HOMEBREW_TAP_TOKEN). Renumber current steps 19-20 to 20-21.

New step 19 content: If `.github/copilot-instructions.md` exists, append these entries to the `## PR Review` section (checking each bold key does not already exist before appending):

- **`go-version-file: go.mod` is valid**: The `actions/setup-go` action supports `go-version-file: go.mod` to read the Go version from the module file. This is the preferred approach. Do not suggest replacing it with a hardcoded version.
- **golangci-lint-action handles its own caching**: The `golangci/golangci-lint-action` manages golangci-lint installation and caching automatically. Do not suggest adding manual cache steps or replacing it with a manual install.

If the file does not exist, skip the step.

Modify step 21 (formerly step 20, Summary): Change the deferred HOMEBREW_TAP_TOKEN bullet. Instead of printing a reminder, check for a GitHub remote (`git remote get-url origin`). If a remote exists, create a follow-up issue:

```bash
gh issue create \
  --title "Set up HOMEBREW_TAP_TOKEN repository secret" \
  --body "The release workflow needs a HOMEBREW_TAP_TOKEN secret so GoReleaser can push Homebrew cask updates to the tap repository.

See the HOMEBREW_TAP_TOKEN Setup reference in the scaffold-go-cli documentation for step-by-step instructions."
```

Report the created issue URL in the summary. If no remote exists, fall back to a printed reminder noting the user should create the issue after pushing to GitHub.

Update the "deferred in step 19" cross-reference to say "step 20".

### 2. `scaffold-go-library` (copilot entries)

**File:** `plugins/scaffold-go-library/commands/scaffold-go-library.md`

Add a new **step 23: Update Copilot Instructions** between steps 22 (Create Initial Commit) and the current step 23 (Summary). Renumber current step 23 to 24.

New step 23 content: If `.github/copilot-instructions.md` exists, append these entries to the `## PR Review` section (checking each bold key does not already exist):

- **golangci-lint v2 config format is intentional**: This project uses golangci-lint v2 configuration which includes `formatters:` as a top-level key and supports `golangci-lint fmt`. These are correct v2 features. Do not suggest reverting to v1 format.
- **golangci-lint-action handles its own caching**: (same text as scaffold-go-cli)

### 3. `setup-linters` (copilot entries)

**File:** `plugins/setup-linters/skills/setup-linters/SKILL.md`

Add a new **step 8: Update Copilot Instructions** between steps 7 (Add Package Manager Scripts) and the current step 8 (Set Up CI). Renumber current steps 8-10 to 9-11.

New step 8 content: If `.github/copilot-instructions.md` exists, append entries for tools that were actually installed (not skipped or already present). Check each bold key does not already exist before appending.

If **Prettier** was installed:

- **Prettier `printWidth: 10000` is intentional**: This project uses a high `printWidth` in `.prettierrc.json` to prevent Prettier from wrapping lines. Combined with `proseWrap: preserve` for Markdown, this preserves author line breaks. Do not suggest reducing it.

If **golangci-lint** config (`.golangci.yml`) was created:

- **golangci-lint v2 config format is intentional**: (same text as scaffold-go-library)

### 4. `scaffold-new-repo` (documentation note only)

**File:** `plugins/scaffold-new-repo/commands/scaffold-new-repo.md`

Add a note to the "Reference: Copilot Instructions Template" Notes section (after line 747) documenting the append pattern:

- **Per-skill false positive entries:** Other scaffold and setup tools (`scaffold-go-cli`, `scaffold-go-library`, `setup-linters`) append PR review entries to this file for patterns they generate that Copilot commonly flags. This file serves as the append target.

### 5. Version bumps

| Plugin                | File                                                     | Current | New   | Reason                                                |
| --------------------- | -------------------------------------------------------- | ------- | ----- | ----------------------------------------------------- |
| `scaffold-go-cli`     | `plugins/scaffold-go-cli/.claude-plugin/plugin.json`     | 2.1.0   | 2.2.0 | Minor: new follow-up issue creation + copilot entries |
| `scaffold-go-library` | `plugins/scaffold-go-library/.claude-plugin/plugin.json` | 1.2.4   | 1.3.0 | Minor: new copilot entries step                       |
| `setup-linters`       | `plugins/setup-linters/.claude-plugin/plugin.json`       | 1.4.1   | 1.5.0 | Minor: new copilot entries step                       |
| `scaffold-new-repo`   | `plugins/scaffold-new-repo/.claude-plugin/plugin.json`   | 1.4.4   | 1.4.5 | Patch: documentation note                             |

Mirror each version in `.claude-plugin/marketplace.json`. No marketplace `metadata.version` bump (no plugins added or removed).

## Bootstrap flow interaction

Execution order ensures correctness:

1. `scaffold-new-repo` creates `.github/copilot-instructions.md` (base template with done-plans rule)
1. `scaffold-go-cli` or `scaffold-go-library` appends its entries (go-version-file, golangci-lint-action, or golangci-lint v2)
1. `setup-linters` appends its entries (Prettier, golangci-lint v2 if not already present)

Duplicate prevention: each step checks whether the bold key text already exists in the file before appending.

Standalone execution: if `.github/copilot-instructions.md` does not exist, the copilot-instructions step is skipped.

## Implementation sequence

1. `scaffold-new-repo` (patch: add documentation note)
1. `scaffold-go-cli` (minor: add copilot step, modify summary for issue creation, renumber)
1. `scaffold-go-library` (minor: add copilot step, renumber)
1. `setup-linters` (minor: add copilot step, renumber)
1. `.claude-plugin/marketplace.json` (update four version entries)
1. `plugin.json` files (update four versions)
1. Run `check-versions` skill to verify consistency

## Verification

1. Read each modified file and verify step numbering is consistent
1. Verify cross-references (e.g., "deferred in step 20") are updated
1. Run `/check-versions` to confirm plugin.json and marketplace.json versions match
1. Review the copilot-instructions entries for accuracy against the actual patterns generated by each skill
