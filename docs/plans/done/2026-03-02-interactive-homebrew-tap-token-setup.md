# Interactive HOMEBREW_TAP_TOKEN Setup

Addresses [issue #158](https://github.com/cboone/cboone-cc-plugins/issues/158).

## Context

Three plugins generate GoReleaser configs and release workflows that reference `HOMEBREW_TAP_TOKEN`, but the token setup is only a text reminder in the summary step. This caused failed releases (e.g., snappy's first two releases failed because the secret was never created). The fix replaces passive reminders with an interactive workflow step that checks for the tap repo, checks for the secret, walks the user through PAT creation, and offers to set the secret via `gh secret set`.

## Changes

### 1. Create a shared "HOMEBREW_TAP_TOKEN Setup" reference section

Write a reference section with these sub-steps:

1. **Check for the homebrew-tap repo** via `gh repo view GITHUB-USERNAME/homebrew-tap`; offer to create it if missing
1. **Check for the existing secret** via `gh secret list | grep HOMEBREW_TAP_TOKEN`; skip to verification if found
1. **Walk through fine-grained PAT creation**: link to `https://github.com/settings/personal-access-tokens/new`, specify exact settings (scope to `GITHUB-USERNAME/homebrew-tap`, Contents: Read and write), explain why it's needed
1. **Offer to set the secret** via `gh secret set HOMEBREW_TAP_TOKEN` (reads from stdin, no echo)
1. **Verify** by re-running `gh secret list | grep HOMEBREW_TAP_TOKEN`

Include a note about the no-remote case (new repos without a GitHub remote yet) and a note that classic PATs with `repo` scope also work but are broader than necessary.

This section is appended as "Reference: HOMEBREW_TAP_TOKEN Setup" at the bottom of both `add-goreleaser-homebrew.md` and `scaffold-go-cli.md`. Each copy includes a sync comment pointing to the other file.

### 2. Edit `add-goreleaser-homebrew.md`

File: `plugins/add-goreleaser-homebrew/commands/add-goreleaser-homebrew.md`

- **Insert new Step 11** ("Set Up HOMEBREW_TAP_TOKEN") between current Step 10 (Verify Configuration) and Step 11 (Summary). The step says to follow the reference section, asks the user if they want to set up the token now or defer.
- **Renumber** current Step 11 (Summary) to Step 12.
- **Update Summary** (new Step 12): replace the `HOMEBREW_TAP_TOKEN` reminder with a conditional note ("If `HOMEBREW_TAP_TOKEN` setup was deferred: add it as a repository secret before the first release").
- **Update inline notes** in the .goreleaser.yml Template notes and Release Workflow Template notes to cross-reference the new reference section instead of describing the token setup inline.
- **Append** the HOMEBREW_TAP_TOKEN Setup reference section at the end of the file.

### 3. Edit `scaffold-go-cli.md`

File: `plugins/scaffold-go-cli/commands/scaffold-go-cli.md`

- **Insert new Step 19** ("Set Up HOMEBREW_TAP_TOKEN") between current Step 18 (Create Initial Commit) and Step 19 (Summary). Includes a note that `gh secret set` requires a remote, which may not exist yet for brand-new projects.
- **Renumber** current Step 19 (Summary) to Step 20.
- **Update Summary** (new Step 20): replace the generic reminder with a conditional note.
- **Update inline notes** in the .goreleaser.yml Template notes and Release Workflow Template notes to cross-reference the new reference section.
- **Append** the HOMEBREW_TAP_TOKEN Setup reference section at the end of the file.

### 4. Edit `setup-installers.md`

File: `plugins/setup-installers/commands/setup-installers.md`

Lighter touch, since this plugin doesn't generate goreleaser brews config directly:

- **Modify Step 5** ("Set Up Homebrew"), specifically the "GoReleaser exists with a `brews:` section" path: after noting Homebrew is handled by GoReleaser, check for the `HOMEBREW_TAP_TOKEN` secret. If missing, warn the user and suggest running `/add-goreleaser-homebrew` for guided setup or manually adding the secret.
- **Add a summary note** in Step 9 for the case where the token was missing.

No full reference section needed in this file since it delegates to `/add-goreleaser-homebrew`.

### 5. Bump versions

| Plugin                    | Current | New   | Reason                       |
| ------------------------- | ------- | ----- | ---------------------------- |
| `add-goreleaser-homebrew` | 1.1.0   | 1.2.0 | New interactive capability   |
| `scaffold-go-cli`         | 1.3.3   | 1.4.0 | New interactive capability   |
| `setup-installers`        | 1.0.0   | 1.1.0 | New token detection behavior |

Update in both `plugin.json` and `.claude-plugin/marketplace.json` for each. No marketplace `metadata.version` bump (no plugins added or removed).

## Files to modify

- `plugins/add-goreleaser-homebrew/commands/add-goreleaser-homebrew.md`
- `plugins/add-goreleaser-homebrew/.claude-plugin/plugin.json`
- `plugins/scaffold-go-cli/commands/scaffold-go-cli.md`
- `plugins/scaffold-go-cli/.claude-plugin/plugin.json`
- `plugins/setup-installers/commands/setup-installers.md`
- `plugins/setup-installers/.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`

## Verification

1. Read each modified command file and confirm the new step is correctly placed, numbered, and references the appended section
1. Confirm the reference section content is identical in both `add-goreleaser-homebrew.md` and `scaffold-go-cli.md`
1. Confirm the old summary reminders have been replaced with conditional notes
1. Confirm version numbers match between each `plugin.json` and its `marketplace.json` entry
1. Run `check-versions` skill to validate version consistency
