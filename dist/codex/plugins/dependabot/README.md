# Dependabot

Review Dependabot configuration and triage open Dependabot pull requests, applying configuration fixes or PR actions as approved.

**Type:** Skills

See the [installation instructions](../../../../README.md#install).

## dependabot:review-config

Review a repository's Dependabot setup (dependabot.yml coverage and validity, grouping, labels, commit messages, and the repository settings and secrets Dependabot depends on), then apply the fixes the user selects.

**Type:** Skill
**Trigger:** `/dependabot:review-config`
**Requires:** [`gh`](https://cli.github.com/) (authenticated), [`jq`](https://jqlang.org/)

### Installation

See the [marketplace install instructions](../../../../README.md#install).

### What It Does

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

#### It verifies before it calls something wrong

Dependabot gains options regularly. The skill checks the current GitHub documentation before reporting a key as invalid, validates with the SchemaStore schema through `check-jsonschema` when `uv` is available, and treats a schema error on a documented option as schema lag rather than a defect.

#### It asks before it changes anything

Local edits to `dependabot.yml` are merged into the existing file, keeping comments and your own groups, with the diff shown before anything is written. Outward-facing changes, such as creating a label or changing a repository setting, are confirmed one at a time. The skill never handles secret values; when a Dependabot secret is missing it gives you the `gh secret set --app dependabot` command to run.

### Usage

```text
/dependabot:review-config
/dependabot:review-config --report-only
/dependabot:review-config --repo octocat/hello-world
```

| Option              | Description                                                             |
| ------------------- | ----------------------------------------------------------------------- |
| `--repo OWNER/REPO` | Review this repository's settings instead of the one `origin` points at |
| `--report-only`     | Report and stop, with no fixes offered                                  |

### Recommended Permissions

This skill runs git and GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(date)", "Bash(git remote -v)", "Bash(gh repo view *)", "Bash(gh pr list *)", "Bash(gh label list *)", "Bash(gh label create *)", "Bash(gh api repos/*)", "Bash(gh api 'repos/*)", "Bash(gh api -i repos/*)", "Bash(gh api -X PUT repos/*)", "Bash(gh api --paginate --slurp repos/*)", "Bash(gh api --paginate --slurp 'repos/*)", "Bash(gh api orgs/*)", "Bash(gh api --paginate --slurp 'orgs/*)", "Bash(gh api --paginate 'repos/*)", "Bash(git fetch *)", "Bash(git ls-tree *)", "Bash(git grep *)", "Bash(git show *)", "Bash(git diff *)", "Bash(grep *)", "Bash(uvx check-jsonschema *)", "Bash(jq *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

`gh label create` and `gh api -X PUT` write to your repository; the skill runs them only after you confirm that label or that setting change. `gh api repos/*` also matches write calls such as `-X POST`, which the skill does not make, so narrow it if you prefer. The quoted `'repos/*` forms cover endpoints with a query string, which have to be quoted in the shell. `uvx check-jsonschema` is optional, and the review skips schema validation without `uv`.

### Examples

- "review the dependabot config": inventories the repository, reviews the config and settings, and offers fixes
- "do we have Dependabot checks on everything?": same review, with the coverage matrix answering the question
- "why isn't Dependabot opening PRs for the web app?": same review; a missing directory or a zero `open-pull-requests-limit` shows up under Coverage or Grouping and volume
- "stop Dependabot from updating the vendored templates": same review, with the fix scoped to that directory

### See Also

- [Triage Dependabot PRs](../dependabot/README.md): work through the open Dependabot PRs this config produces
- [Pin Everything](../pin-everything/README.md): write the baseline config, and audit the version pins Dependabot cannot see
- [Refresh Project Scaffolding](../refresh-project-scaffolding/README.md): detect a missing or incomplete config among other scaffolding drift
- [Optimize Runner Usage](../set-up-ci/README.md): cut the CI cost of Dependabot PR volume
- [All plugins](../../../../README.md)

## dependabot:triage-prs

Triage a repository's open Dependabot pull requests into safe to merge, needs refresh, needs testing, needs work, hold, superseded, or outdated, backed by evidence, then merge, rebase, or close them as the user approves.

**Type:** Skill
**Trigger:** `/dependabot:triage-prs [<pr-number>...]`
**Requires:** [`gh`](https://cli.github.com/) (authenticated), [`jq`](https://jqlang.org/)

### Installation

See the [marketplace install instructions](../../../../README.md#install).

### What It Does

Dependabot PRs look uniform and are not. A green check can be reporting on a base that no longer exists. A `MERGEABLE` PR can downgrade a dependency the default branch has already moved past. A grouped PR can carry a production-server major among a handful of patches. CI can fail only because Dependabot runs cannot read the repository's secrets, or pass only because nothing it runs touches the changed files. This skill gathers the evidence that separates those cases, puts every open Dependabot PR into exactly one category, and then acts only on what you approve.

A bundled `dependabot-prs` script does the gathering. It lists the open Dependabot PRs and every other open PR, compares each Dependabot head against its base branch through the compare API, reads open Dependabot alerts, and reduces all of it to a compact summary without the PR bodies. It parses what the bodies and titles carry (ecosystem, security or version update, group shape, versions, update type), and flags the layouts that make them unreliable: a body truncated at the size limit, a commands footer removed by a rebase, a title updated in place that no longer matches its branch.

The skill then checks each PR for freshness, whether the default branch already has the change, overlap with other PRs, and whether CI actually exercises the change. Majors, grouped PRs, runtime dependencies, security updates, and GitHub Actions bumps also get their release notes, breaking changes, SHA-to-tag resolution, and version comments read.

#### Categories

Evaluated in this order; the first match wins:

| Category      | Means                                                         | Recommended action                                 |
| ------------- | ------------------------------------------------------------- | -------------------------------------------------- |
| Superseded    | Something else already delivers this change, or a newer one   | Close, naming the replacement                      |
| Outdated      | The thing the PR updates, or the branch it targets, is gone   | Close and delete the branch                        |
| Hold          | The repository has deliberately deferred this upgrade         | Leave open, or ignore the version                  |
| Needs refresh | The change is wanted, but the PR's state is out of date       | `@dependabot rebase` or `recreate`, then re-triage |
| Needs work    | The change cannot merge as it stands                          | Tracking issue, migration PR, or ignore            |
| Needs testing | Current and conflict-free, but the evidence is not yet enough | The specific verification it needs, or `--verify`  |
| Safe to merge | Current, exercised by CI, conflict-free, nothing breaking     | Merge, in a computed order                         |

Security updates sort first within each category, by the severity of the alerts they clear. Alerts that no open PR addresses are reported separately.

#### It asks before it writes

The report comes first. Merging, closing, commenting, approving, and opening issues all wait for you to pick them. The skill never merges with `--admin`, never enables auto-merge unless asked, never approves a PR on your behalf unless you ask for approval specifically, and never pushes to a Dependabot branch unless you ask for exactly that, since a push by anyone else stops Dependabot from rebasing the branch.

### Usage

```text
/dependabot:triage-prs
/dependabot:triage-prs 107 110
/dependabot:triage-prs --verify
/dependabot:triage-prs --report-only
/dependabot:triage-prs --repo octocat/hello-world
```

| Option              | Description                                                                             |
| ------------------- | --------------------------------------------------------------------------------------- |
| `<pr-number>...`    | Triage only these PRs                                                                   |
| `--repo OWNER/REPO` | Triage this repository instead of the one `origin` points at                            |
| `--verify`          | Run the repository's checks locally in a worktree for every PR headed for Needs testing |
| `--report-only`     | Report and stop, with no action offer                                                   |

### Recommended Permissions

This skill runs the bundled script, git, and GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(bash \"*/dependabot-prs\" *)", "Bash(date)", "Bash(git remote -v)", "Bash(gh repo view *)", "Bash(gh pr view *)", "Bash(gh pr checks *)", "Bash(gh pr comment *)", "Bash(gh pr close *)", "Bash(gh pr merge *)", "Bash(gh pr review *)", "Bash(gh run view *)", "Bash(gh api repos/*)", "Bash(gh api 'repos/*)", "Bash(gh api --paginate --slurp repos/*)", "Bash(gh api --paginate 'repos/*)", "Bash(git fetch *)", "Bash(git show *)", "Bash(git diff *)", "Bash(git log *)", "Bash(git grep *)", "Bash(git merge-base *)", "Bash(git merge-tree *)", "Bash(git worktree add *)", "Bash(git worktree prune)", "Bash(git -C * merge *)", "Bash(git for-each-ref *)", "Bash(git update-ref --stdin)", "Bash(mktemp *)", "Bash(rm -f *)", "Bash(rm -rf *)", "Bash(grep *)", "Bash(npm view *)", "Bash(jq *)", "Bash(sleep *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

The `gh pr comment`, `close`, `merge`, and `review` rules allow writes to your repositories, and so does `gh api repos/*`, which also matches `-X POST` and `-X DELETE` calls. The skill only issues writes after you select an action, but leave those rules out if you want a second prompt for every write. `rm -rf *` is broad: the skill uses it only on the `mktemp -d` directories it creates for verification, so drop it if you would rather confirm each removal. The quoted `gh api 'repos/*` form covers endpoints with a query string, which have to be quoted in the shell. `sleep` is only needed off Claude Code, where the wait for a Dependabot rebase falls back to a blocking poll.

`--verify` stays interactive. It runs the repository's own install, build, and test commands in a worktree (`npm ci`, `yarn`, `pnpm`, `uv`, `go`, `cargo`, `bundle`, `make`, `npx`, and whatever the workflows call), and the security evidence can run `pip-audit` or `govulncheck`. Those commands execute code from the PR under test, so none are in the list above: each prompts unless you add rules for the tool families your projects use.

### Examples

- "triage the dependabot PRs": gathers, classifies, and reports every open Dependabot PR, then offers actions
- "review the open Dependabot PRs and assess their merge safety": same behavior
- "are the Dependabot PRs safe to merge?": same behavior; the report answers, and the action offer follows
- "is PR 107 safe to merge?": triages that PR alone when it is a Dependabot PR
- "clean up the stale Dependabot PRs": same triage, with Superseded and Outdated PRs as the likely action

### See Also

- [Review Dependabot Config](../dependabot/README.md): review the `dependabot.yml` and repository settings behind these PRs
- [Monitor PR](../monitor-pr/README.md): watch a single refreshed Dependabot PR until it is ready to merge
- [Upgrade Everything](../upgrade-everything/README.md): replace several PRs that fight over one lockfile with a single package-manager upgrade
- [Create Issue](../use-git/README.md): track a Needs work or Hold upgrade
- [All plugins](../../../../README.md)
