# GitHub Actions Workflow Templates

Choose the template matching the repository ownership. Organization-owned repos require a gitleaks license; personal repos do not.

## Personal Repository

```yaml
name: gitleaks

on:
  push:
  pull_request:
  workflow_dispatch:
  schedule:
    - cron: "0 4 * * *"

jobs:
  scan:
    name: gitleaks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Organization Repository

```yaml
name: gitleaks

on:
  push:
  pull_request:
  workflow_dispatch:
  schedule:
    - cron: "0 4 * * *"

jobs:
  scan:
    name: gitleaks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
```

## Notes

- `fetch-depth: 0` clones the full git history so gitleaks can scan all commits, not just the latest.
- The `schedule` trigger runs a daily scan at 4 AM UTC to catch secrets introduced outside of PR workflows (e.g., direct pushes).
- `workflow_dispatch` allows manual triggering from the GitHub Actions UI.
- `GITHUB_TOKEN` is automatically provided by GitHub and enables PR comments when secrets are detected.
- `GITLEAKS_LICENSE` is required for organization-owned repositories. Free licenses are available at [gitleaks.io](https://gitleaks.io). Personal account repositories do not need a license.
