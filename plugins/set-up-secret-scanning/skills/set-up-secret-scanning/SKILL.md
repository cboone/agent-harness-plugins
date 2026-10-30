---
name: set-up-secret-scanning
description: >-
  Add gitleaks and TruffleHog secret scanning to GitHub Actions. Use for "add
  secret scanning" or "set up gitleaks"; for app code, use handle-secrets.
---

# Set-Up Secret Scanning

Set up secret scanning in a repository with [gitleaks](https://github.com/gitleaks/gitleaks) and [TruffleHog](https://github.com/trufflesecurity/trufflehog) GitHub Actions workflows and optional `.gitleaks.toml` configuration.

The two tools are complementary:

- **Gitleaks** performs fast pattern matching.
- **TruffleHog** performs deeper verification-based scanning that confirms whether detected credentials are still live.

Both run on pushes to `main`, on every pull request, and on manual `workflow_dispatch`.

## Workflow

### 1. Check for Existing Setup

Look for existing secret scanning workflows and configuration:

```bash
ls .github/workflows/gitleaks.yml
ls .github/workflows/gitleaks.yaml
ls .github/workflows/trufflehog.yml
ls .github/workflows/trufflehog.yaml
```

Also check for an existing `.gitleaks.toml`:

```bash
ls .gitleaks.toml
```

If any workflows already exist, inform the user and ask whether to overwrite each one or skip it.

### 2. Choose Scanning Tools

If the user specified a tool selection in their request (`gitleaks`, `trufflehog`, or `both`), use it directly instead of asking.

Ask the user which tools to set up:

- **Both gitleaks and TruffleHog** (recommended): complementary coverage with fast pattern matching and deep verification
- **Gitleaks only**: fast pattern matching on every push and PR
- **TruffleHog only**: verification-based scanning on pushes to main

### 3. Generate Gitleaks Workflow

If gitleaks was selected, read `./references/gitleaks-workflow.md` for the workflow template and create `.github/workflows/gitleaks.yml` from it.

Write the file using the Write tool. The `.github/workflows/` directory will be created automatically if it does not exist.

### 4. Generate TruffleHog Workflow

If TruffleHog was selected, read `./references/trufflehog-workflow.md` for the workflow template and create `.github/workflows/trufflehog.yml` from it.

Write the file using the Write tool.

### 5. Optionally Generate Gitleaks Configuration

If gitleaks was selected, ask the user whether they want a `.gitleaks.toml` configuration file.

If yes, read `./references/gitleaks-config.md` and create `.gitleaks.toml` in the repository root from its starter template. Keep the default rules enabled without adding exclusions. Do not exclude whole lockfiles or vendor directories based on the project language or file category.

Explain the inherited coverage limit in the reference. Default rules also include built-in path exclusions, so this starter does not guarantee that every lockfile or vendor path is scanned. Projects requiring that coverage need a separately maintained full configuration without `useDefault`.

Add a suppression only after reviewing a concrete finding and confirming it is a false positive. Use the narrowest scope possible: a finding fingerprint or a rule-specific content pattern. Before using a fingerprint, check all matches sharing its path, rule and starting line, and its commit when present; it does not distinguish content or columns. Use a content pattern when an unrelated credential shares that scope. Document the reason and rescan to confirm unrelated secrets remain detectable. A real credential, even if revoked, is not a false positive.

Explain the PR configuration trust limitation in the reference: the reusable workflow currently scans with configuration from the PR checkout, including automatically discovered `.gitleaks.toml`. This starter does not prevent a PR from weakening its own scan; trusted-base configuration is tracked separately in [cboone/gh-actions issue 157](https://github.com/cboone/gh-actions/issues/157).

If no, skip this step.

### 6. Summary

Print a summary of what was created:

- List every file generated
- Note that both workflows run on pushes to `main`, pull requests, and `workflow_dispatch`
- Mention that gitleaks will automatically comment on PRs when secrets are detected

## Error Handling

- If any workflow file already exists, ask before overwriting
- If `.github/workflows/` cannot be created, check that the current directory is a git repository root

## Reference Templates

- `./references/gitleaks-workflow.md` -- gitleaks GitHub Actions workflow
- `./references/trufflehog-workflow.md` -- TruffleHog GitHub Actions workflow
- `./references/gitleaks-config.md` -- `.gitleaks.toml` configuration

## Refresh `cboone/gh-actions` SHAs before scaffolding

The `cboone/gh-actions` reusable-workflow refs in this skill's templates are SHA-pinned with a `# vX.Y.Z` comment that was current when the template was authored. New releases of `cboone/gh-actions` rot those SHAs. Before emitting a workflow into a user's repo, refresh both the SHA and the comment to current latest:

```bash
TAG="$(gh release view --repo cboone/gh-actions --json tagName --jq '.tagName')"
SHA="$(gh api "repos/cboone/gh-actions/commits/${TAG}" --jq '.sha')"
echo "${SHA} # ${TAG}"
```

Replace each `cboone/gh-actions/.../<workflow>.yml@<old-sha> # <old-tag>` in the emitted workflow with the new SHA and tag. Dependabot in the user's repo keeps them in sync afterwards.
