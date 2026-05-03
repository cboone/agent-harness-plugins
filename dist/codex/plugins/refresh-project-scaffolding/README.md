# Refresh Project Scaffolding

Refresh existing project scaffolding against the latest plugin templates.

**Type:** Skill
**Trigger:** `/refresh-project-scaffolding`

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Scans the current repository for files created by other plugins in this ecosystem (CI workflows, linter configs, community files, secret scanning, agent config, etc.), compares them against current templates, and identifies what's outdated. Presents a plan table showing the status of each tool, then applies targeted refreshes after user confirmation.

The maintenance companion to [Bootstrap Project](../bootstrap-project/README.md): bootstrap asks "what needs to be set up?", this asks "what needs to be updated?"

**Scope**: This command audits tools already in use and refreshes their files to match current templates. For tools that are partially configured, it can restore missing expected files. It does not set up tools that were never used; for initial setup, use `/bootstrap-project` or the individual tool.

## Usage

```text
/refresh-project-scaffolding
```

## What It Checks

- **Action versions**: Verifies all GitHub Actions use current versions
- **CI best practices**: Permissions, concurrency groups, timeout-minutes, paths-ignore
- **Linter configs**: EditorConfig, Prettier, markdownlint, language-specific linters
- **Secret scanning**: Gitleaks and TruffleHog workflow currency
- **Community files**: Contributor Covenant version, CONTRIBUTING.md commands, SECURITY.md, PR template
- **Foundation files**: LICENSE year, .gitignore entries, agent config symlinks
- **GoReleaser**: Release workflow and config currency
- **Runner optimization**: Concurrency, timeouts, paths-ignore across all workflows

## See Also

- [Bootstrap Project](../bootstrap-project/README.md): initial project setup
- [Optimize Runner Usage](../optimize-runner-usage/README.md): CI optimization only
- [Clean Up Agent Config](../clean-up-agent-config/README.md): agent config audit only
- [All plugins](../../../../README.md)
