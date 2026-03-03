# Add TruffleHog to Secret Scanning Plugin

## Context

The `setup-gitleaks` plugin currently sets up a single secret scanning tool (gitleaks) via a GitHub Actions workflow. The goal is to broaden it into a general-purpose secret scanning plugin that supports both gitleaks and TruffleHog, with complementary scanning strategies:

- **Gitleaks**: fast pattern matching on every push and PR (current behavior, unchanged)
- **TruffleHog**: deeper verification-based scanning on pushes to main, PRs, and a weekly schedule

This is a breaking change (renamed plugin, new trigger), so the plugin version becomes 2.0.0.

## Approach

### Rename the plugin

Rename `setup-gitleaks` to `setup-secret-scanning`. The trigger changes from `/setup-gitleaks` to `/setup-secret-scanning`. This reflects the broader scope.

- `git mv plugins/setup-gitleaks plugins/setup-secret-scanning`
- `git mv plugins/setup-secret-scanning/commands/setup-gitleaks.md plugins/setup-secret-scanning/commands/setup-secret-scanning.md`

### Scanning strategy

Two separate workflow files (not one combined), matching the existing pattern of one CI concern per file:

| Tool       | Workflow file    | Push         | PR  | Schedule            | Dispatch |
| ---------- | ---------------- | ------------ | --- | ------------------- | -------- |
| Gitleaks   | `gitleaks.yml`   | All branches | Yes | Daily 4 AM UTC      | Yes      |
| TruffleHog | `trufflehog.yml` | `main` only  | Yes | Weekly Sat 4 AM UTC | Yes      |

Gitleaks templates stay unchanged (personal vs org variants). TruffleHog needs only a single template (no license distinction).

### TruffleHog workflow template

```yaml
name: trufflehog

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:
  schedule:
    - cron: "0 4 * * 6"

jobs:
  scan:
    name: trufflehog
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
      issues: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: trufflesecurity/trufflehog@v3
        with:
          extra_args: --results=verified,unknown
```

Key design decisions:

- `trufflesecurity/trufflehog@v3` (stable major version tag, not `@main`)
- `--results=verified,unknown` reports confirmed-active and unknown-status secrets, filters out confirmed false positives
- Explicit permissions block (required by TruffleHog for PR comments)
- Weekly schedule complements gitleaks' daily scans
- No `.trufflehog.yml` config file needed (configuration via CLI flags in `extra_args`)

### Command workflow (setup-secret-scanning.md)

Follows the existing detect-ask-generate-summarize pattern, expanded for two tools:

1. **Check for existing setup**: scan for `gitleaks.yml`, `trufflehog.yml`, and `.gitleaks.toml`
1. **Choose scanning tools**: ask user to pick both (recommended), gitleaks only, or TruffleHog only
1. **Determine repository ownership**: only if gitleaks selected (personal vs org for license)
1. **Generate gitleaks workflow**: if selected, using existing templates
1. **Generate TruffleHog workflow**: if selected, using new template
1. **Optionally generate gitleaks config**: if gitleaks selected, same `.gitleaks.toml` as before
1. **Summary**: list files, note trigger coverage for each tool, remind about license if org

## Changes

### Phase 1: Rename directory and files

Rename via `git mv`, then commit. Doing this in a separate commit helps git track the rename.

- `plugins/setup-gitleaks/` becomes `plugins/setup-secret-scanning/`
- `commands/setup-gitleaks.md` becomes `commands/setup-secret-scanning.md`

### Phase 2: Update plugin files

Rewrite all three files in `plugins/setup-secret-scanning/`:

| File                                | Changes                                                                   |
| ----------------------------------- | ------------------------------------------------------------------------- |
| `.claude-plugin/plugin.json`        | name, description, keywords (+trufflehog), version to 2.0.0               |
| `commands/setup-secret-scanning.md` | Full rewrite with dual-tool workflow, TruffleHog template, expanded steps |
| `README.md`                         | New name, trigger, description covering both tools                        |

### Phase 3: Update marketplace registry

`.claude-plugin/marketplace.json`:

- Replace `setup-gitleaks` entry with `setup-secret-scanning` (name, description, keywords, source, version 2.0.0)
- Bump `metadata.version` from 1.18.0 to 1.19.0

### Phase 4: Update cross-references

14 files reference `setup-gitleaks`. All need `setup-gitleaks` replaced with `setup-secret-scanning`:

**Repo-level docs:**

- `README.md`: ToC entry and description section
- `CLAUDE.md`: directory tree (2 spots)
- `AGENTS.md`: directory tree

**Other plugins (functional references, patch version bumps needed):**

- `plugins/bootstrap-project/skills/bootstrap-project/SKILL.md`: detection table, execution order, task table, reference path (5 edits). Also add TruffleHog to detection table.
- `plugins/bootstrap-project/skills/bootstrap-project/references/overlap-rules.md`: independent tool listing, applicability table
- `plugins/bootstrap-project/README.md`: orchestrated tools list

**Other plugins (See Also / suggestion links):**

- `plugins/setup-ci/commands/setup-ci.md`: suggestion text
- `plugins/setup-ci/README.md`: See Also link
- `plugins/scaffold-new-repo/README.md`: See Also link
- `plugins/handle-secrets/README.md`: See Also link
- `plugins/setup-linters/README.md`: See Also link
- `plugins/create-plugin/skills/create-plugin/references/readme-updates.md`: example in table

**Outside repo:**

- `~/.claude/CLAUDE.md`: "When adding secret scanning, use `setup-secret-scanning`"

### Phase 5: Version bumps for affected plugins

| Plugin                | Current | New      | Reason                           |
| --------------------- | ------- | -------- | -------------------------------- |
| setup-secret-scanning | 1.1.0   | 2.0.0    | Breaking rename + new capability |
| marketplace metadata  | 1.18.0  | 1.19.0   | Catalog changed                  |
| bootstrap-project     | (check) | patch +1 | SKILL.md and references change   |
| setup-ci              | (check) | patch +1 | Command suggestion text changed  |

README-only See Also link changes in scaffold-new-repo, handle-secrets, setup-linters, and create-plugin: patch bump each if the project convention warrants it, or skip if pure link updates are considered cosmetic. Check with `check-versions` skill before PR.

### Stale todo plan

`docs/plans/todo/2026-03-01-trim-setup-skill-descriptions.md` section 6 references `plugins/setup-gitleaks/skills/setup-gitleaks/SKILL.md` (which doesn't exist; setup-gitleaks is a command, not a skill). After this rename, that section should reference `setup-secret-scanning` or be removed. Update during implementation.

## Verification

1. Run `git diff main...HEAD` to confirm all `setup-gitleaks` references are updated (except historical plan files in `docs/plans/done/`)
1. Grep for any remaining `setup-gitleaks` references outside `docs/plans/done/`
1. Verify `plugin.json` version matches `marketplace.json` entry for the renamed plugin
1. Run `check-versions` skill to validate version consistency
1. Test the command trigger by starting a new session and running `/setup-secret-scanning`
1. Verify the generated gitleaks and TruffleHog workflow YAML is valid
