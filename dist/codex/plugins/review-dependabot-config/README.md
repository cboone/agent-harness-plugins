# Review Dependabot Config

Review a repository's Dependabot setup (dependabot.yml coverage and validity, grouping, labels, commit messages, and the repository settings and secrets Dependabot depends on), then apply the fixes the user selects.

**Type:** Skill
**Trigger:** `/review-dependabot-config`
**Requires:** [`gh`](https://cli.github.com/) (authenticated), [`jq`](https://jqlang.org/)

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

A Dependabot config fails quietly. An ecosystem nobody listed gets no updates and no warning. A label that does not exist is dropped from every PR. A directory added after the config was written is never scanned. A job that needs a secret fails on every Dependabot PR, which teaches everyone to ignore red checks on those PRs. This skill goes looking for all of it.

It inventories the repository first: every manifest and lockfile with its directory, every workflow and composite action, separate install trees, and the version pins Dependabot cannot see. It then reviews the default-branch `dependabot.yml` against that inventory and against current GitHub behavior, and reads the repository settings Dependabot depends on.

| Area                | Checks                                                                                                                                                |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Coverage            | Ecosystems and directories with no entry, composite actions with external `uses:`, entries left behind by a migration                                 |
| Validity            | YAML and schema validation, `directory` versus `directories`, duplicate entries, the retired `reviewers` key, labels and milestones that do not exist |
| Grouping and volume | Groups, overlapping patterns, `open-pull-requests-limit`, schedules, `cooldown`, PR volume against CI cost                                            |
| Update behavior     | `versioning-strategy`, commit messages against the repository's convention and PR-title checks, stale or broad `ignore` rules, `exclude-paths` limits |
| Repository settings | Alerts, security updates, Dependabot secrets for jobs that run on Dependabot PRs, merge rules, labels, automation workflows, alerts with no fix path  |
| Untracked surfaces  | Runtime version files, `packageManager`, tool versions in workflow `env:`, install commands, action references in Markdown                            |

Findings come back as Errors, Warnings, and Suggestions, each with evidence and a concrete fix, alongside a coverage matrix and a settings table.

With no config at all, it reports what a config would cover and offers to write the house baseline through [Pin Everything](../pin-everything/README.md) (`--scope dependabot`).

### It verifies before it calls something wrong

Dependabot gains options regularly. The skill checks the current GitHub documentation before reporting a key as invalid, validates with the SchemaStore schema through `check-jsonschema` when `uv` is available, and treats a schema error on a documented option as schema lag rather than a defect.

### It asks before it changes anything

Local edits to `dependabot.yml` are merged into the existing file, keeping comments and your own groups, with the diff shown before anything is written. Outward-facing changes, such as creating a label or changing a repository setting, are confirmed one at a time. The skill never handles secret values; when a Dependabot secret is missing it gives you the `gh secret set --app dependabot` command to run.

## Usage

```text
/review-dependabot-config
/review-dependabot-config --report-only
/review-dependabot-config --repo octocat/hello-world
```

| Option              | Description                                                             |
| ------------------- | ----------------------------------------------------------------------- |
| `--repo OWNER/REPO` | Review this repository's settings instead of the one `origin` points at |
| `--report-only`     | Report and stop, with no fixes offered                                  |

## Recommended Permissions

This skill runs git and GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(date)", "Bash(git remote -v)", "Bash(gh repo view *)", "Bash(gh pr list *)", "Bash(gh label list *)", "Bash(gh label create *)", "Bash(gh api repos/*)", "Bash(gh api 'repos/*)", "Bash(gh api -i repos/*)", "Bash(gh api --paginate --slurp repos/*)", "Bash(gh api --paginate --slurp 'repos/*)", "Bash(gh api orgs/*)", "Bash(gh api --paginate --slurp 'orgs/*)", "Bash(gh api --paginate 'repos/*)", "Bash(git fetch *)", "Bash(git ls-tree *)", "Bash(git grep *)", "Bash(git show *)", "Bash(git diff *)", "Bash(grep *)", "Bash(uvx check-jsonschema *)", "Bash(jq *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

`gh label create` writes to your repository; the skill only runs it after you confirm that label. `gh api repos/*` also matches write calls such as `-X POST`, which the skill does not make, so narrow it if you prefer. The quoted `'repos/*` forms cover endpoints with a query string, which have to be quoted in the shell. `uvx check-jsonschema` is optional, and the review skips schema validation without `uv`.

## Examples

- "review the dependabot config": inventories the repository, reviews the config and settings, and offers fixes
- "do we have Dependabot checks on everything?": same review, with the coverage matrix answering the question
- "why isn't Dependabot opening PRs for the web app?": same review; a missing directory or a zero `open-pull-requests-limit` shows up under Coverage or Grouping and volume
- "stop Dependabot from updating the vendored templates": same review, with the fix scoped to that directory

## See Also

- [Triage Dependabot PRs](../triage-dependabot-prs/README.md): work through the open Dependabot PRs this config produces
- [Pin Everything](../pin-everything/README.md): write the baseline config, and audit the version pins Dependabot cannot see
- [Refresh Project Scaffolding](../refresh-project-scaffolding/README.md): detect a missing or incomplete config among other scaffolding drift
- [Optimize Runner Usage](../optimize-runner-usage/README.md): cut the CI cost of Dependabot PR volume
- [All plugins](../../../../README.md)
