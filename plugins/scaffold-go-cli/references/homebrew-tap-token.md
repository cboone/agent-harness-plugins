# HOMEBREW_TAP_TOKEN Setup

<!-- sync: this section is duplicated in plugins/add-goreleaser-homebrew/commands/add-goreleaser-homebrew.md -->

The release workflow needs a `HOMEBREW_TAP_TOKEN` repository secret so GoReleaser can push cask updates to the Homebrew tap repository. This section walks through creating the token and setting the secret.

## 1. Check for the Homebrew Tap Repository

Verify the tap repository exists:

```bash
gh repo view GITHUB-USERNAME/homebrew-tap
```

If the repository does not exist, offer to create it:

```bash
gh repo create GITHUB-USERNAME/homebrew-tap --public --description "Homebrew tap for GITHUB-USERNAME's tools"
```

Replace `GITHUB-USERNAME` with the user's actual GitHub username throughout this section.

## 2. Check for an Existing Secret

Check whether the secret is already configured:

```bash
gh secret list | grep HOMEBREW_TAP_TOKEN || true
```

If the secret already exists, skip to step 5 (Verify) to confirm it is still configured.

## 3. Create a Fine-Grained Personal Access Token

Direct the user to create a fine-grained PAT:

1. Open <https://github.com/settings/personal-access-tokens/new>
1. **Token name**: something descriptive, e.g., `homebrew-tap-token`
1. **Expiration**: choose an appropriate duration (90 days, 1 year, or custom)
1. **Repository access**: select "Only select repositories", then choose `GITHUB-USERNAME/homebrew-tap`
1. **Permissions**: under "Repository permissions", set **Contents** to **Read and write**; leave everything else at the defaults
1. Click "Generate token" and copy the token value

Explain that this token allows GoReleaser to push cask updates to the tap repository during releases. The fine-grained PAT is preferred because it limits access to a single repository with minimal permissions.

## 4. Set the Repository Secret

Offer to set the secret using the `gh` CLI:

```bash
gh secret set HOMEBREW_TAP_TOKEN
```

This command reads the token from stdin (no echo), so the user can paste the token value securely. The secret is set on the current repository.

## 5. Verify

Confirm the secret is configured:

```bash
gh secret list | grep HOMEBREW_TAP_TOKEN || true
```

If the secret appears in the output, the setup is complete. If not, re-run step 4.

## Notes

- **No remote yet?** If the repository has not been pushed to GitHub yet (common for brand-new projects), `gh secret` commands (`gh secret set`, `gh secret list`) will fail because there is no associated GitHub repository. In that case, note the token value securely and set/verify the secret after creating the GitHub remote and pushing for the first time.
- **Classic PATs also work.** A classic personal access token with `repo` scope can be used instead of a fine-grained PAT, but classic tokens grant broader access than necessary. Fine-grained PATs scoped to the single tap repository are the recommended approach.
