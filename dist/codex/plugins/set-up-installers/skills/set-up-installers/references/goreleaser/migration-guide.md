# Migrating Existing Projects from Formula to Cask

For projects that previously used `brews:` in their `.goreleaser.yml` and want to migrate to `homebrew_casks:`, follow these steps:

## 1. Update `.goreleaser.yml`

Replace the `brews:` section with `homebrew_casks:` per the base template above. Key changes:

- `brews:` becomes `homebrew_casks:`
- Remove `directory: Formula` (casks default to `Casks/`)
- Remove the `test:` block (casks do not support it)
- Remove the `install:` block; add `binaries:` array instead
- Add the quarantine removal `hooks.post.install` (see the base template)
- If using completions: switch from `generate_completions_from_executable` to pre-generated files with `before.hooks`, `archives.files`, and `completions:` (see the Shell Completions section)
- If using man pages: switch from `man1.install` to `manpages:` array (see the Man Pages section)

**Important**: The `hooks.post.install` field must be a **string**, not a YAML list. Using a list causes `yaml: unmarshal errors` and release failures.

## 2. Create `tap_migrations.json`

In the root of the tap repository (e.g., `GITHUB-USERNAME/homebrew-tap`), create a `tap_migrations.json` file so existing formula users automatically migrate to the cask:

```json
{
  "PROJECT-NAME": "PROJECT-NAME"
}
```

This tells Homebrew to redirect `brew install GITHUB-USERNAME/tap/PROJECT-NAME` from the old formula to the new cask.

## 3. Clean Up the Old Formula

After the first release with `homebrew_casks:` succeeds and the cask is published to the tap repository:

1. Verify the cask works: `brew install GITHUB-USERNAME/tap/PROJECT-NAME`
1. Delete the old formula file from the tap repository (e.g., `Formula/PROJECT-NAME.rb`)
1. Keep `tap_migrations.json` permanently so users with the old formula installed can upgrade
