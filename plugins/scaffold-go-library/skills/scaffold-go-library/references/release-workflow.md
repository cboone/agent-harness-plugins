# Release Workflow Template

Use this template for `.github/workflows/release.yml`. Uses the `cboone/gh-actions` reusable workflow. No replacements needed.

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: false

permissions:
  contents: write

jobs:
  release:
    uses: cboone/gh-actions/.github/workflows/go-release.yml@e4e9f34f54041223e72f0d6241efede27a698fa1 # v1.0.0
```

## Notes

- Triggers on version tags (e.g., `v0.1.0`, `v1.0.0`)
- Concurrency uses `cancel-in-progress: false` to avoid interrupting active releases
- The reusable workflow handles checkout with `fetch-depth: 0`, Go setup, GoReleaser installation, and the release command internally
- `GITHUB_TOKEN` is provided automatically by GitHub Actions and its permissions are controlled by the caller workflow's `permissions:` block (no `HOMEBREW_TAP_TOKEN` needed since libraries have no Homebrew formula)
- `permissions: contents: write` is required for GoReleaser to create the GitHub release
- GoReleaser will skip the build step (configured in `.goreleaser.yml`) and only generate the changelog and release
