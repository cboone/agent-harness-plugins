# Triage Dependabot PRs

Triage a repository's open Dependabot pull requests into safe to merge, needs refresh, needs testing, needs work, hold, superseded, or outdated, backed by evidence, then merge, rebase, or close them as the user approves.

**Type:** Skill
**Trigger:** `/triage-dependabot-prs [<pr-number>...]`
**Requires:** [`gh`](https://cli.github.com/) (authenticated), [`jq`](https://jqlang.org/)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Dependabot PRs look uniform and are not. A green check can be reporting on a base that no longer exists. A `MERGEABLE` PR can downgrade a dependency the default branch has already moved past. A grouped PR can carry a production-server major among a handful of patches. CI can fail only because Dependabot runs cannot read the repository's secrets, or pass only because nothing it runs touches the changed files. This skill gathers the evidence that separates those cases, puts every open Dependabot PR into exactly one category, and then acts only on what you approve.

A bundled `dependabot-prs` script does the gathering. It lists the open Dependabot PRs and every other open PR, compares each Dependabot head against its base branch through the compare API, reads open Dependabot alerts, and reduces all of it to a compact summary without the PR bodies. It parses what the bodies and titles carry (ecosystem, security or version update, group shape, versions, update type), and flags the layouts that make them unreliable: a body truncated at the size limit, a commands footer removed by a rebase, a title updated in place that no longer matches its branch.

The skill then checks each PR for freshness, whether the default branch already has the change, overlap with other PRs, and whether CI actually exercises the change. Majors, grouped PRs, runtime dependencies, security updates, and GitHub Actions bumps also get their release notes, breaking changes, SHA-to-tag resolution, and version comments read.

### Categories

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

### It asks before it writes

The report comes first. Merging, closing, commenting, approving, and opening issues all wait for you to pick them. The skill never merges with `--admin`, never enables auto-merge unless asked, never approves a PR on your behalf unless you ask for approval specifically, and never pushes to a Dependabot branch unless you ask for exactly that, since a push by anyone else stops Dependabot from rebasing the branch.

## Usage

```text
/triage-dependabot-prs
/triage-dependabot-prs 107 110
/triage-dependabot-prs --verify
/triage-dependabot-prs --report-only
/triage-dependabot-prs --repo octocat/hello-world
```

| Option              | Description                                                                             |
| ------------------- | --------------------------------------------------------------------------------------- |
| `<pr-number>...`    | Triage only these PRs                                                                   |
| `--repo OWNER/REPO` | Triage this repository instead of the one `origin` points at                            |
| `--verify`          | Run the repository's checks locally in a worktree for every PR headed for Needs testing |
| `--report-only`     | Report and stop, with no action offer                                                   |

## Recommended Permissions

This skill runs the bundled script, git, and GitHub CLI commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(bash \"*/dependabot-prs\" *)", "Bash(date)", "Bash(git remote -v)", "Bash(gh repo view *)", "Bash(gh pr view *)", "Bash(gh pr checks *)", "Bash(gh pr comment *)", "Bash(gh pr close *)", "Bash(gh pr merge *)", "Bash(gh pr review *)", "Bash(gh run view *)", "Bash(gh api repos/*)", "Bash(gh api 'repos/*)", "Bash(gh api --paginate --slurp repos/*)", "Bash(gh api --paginate 'repos/*)", "Bash(git fetch *)", "Bash(git show *)", "Bash(git diff *)", "Bash(git log *)", "Bash(git grep *)", "Bash(git merge-base *)", "Bash(git merge-tree *)", "Bash(git worktree add *)", "Bash(git worktree prune)", "Bash(git -C * merge *)", "Bash(git for-each-ref *)", "Bash(git update-ref --stdin)", "Bash(mktemp *)", "Bash(rm -f *)", "Bash(rm -rf *)", "Bash(grep *)", "Bash(base64 *)", "Bash(npm view *)", "Bash(jq *)", "Bash(sleep *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

The `gh pr comment`, `close`, `merge`, and `review` rules allow writes to your repositories, and so does `gh api repos/*`, which also matches `-X POST` and `-X DELETE` calls. The skill only issues writes after you select an action, but leave those rules out if you want a second prompt for every write. `rm -rf *` is broad: the skill uses it only on the `mktemp -d` directories it creates for verification, so drop it if you would rather confirm each removal. The quoted `gh api 'repos/*` form covers endpoints with a query string, which have to be quoted in the shell. `sleep` is only needed off Claude Code, where the wait for a Dependabot rebase falls back to a blocking poll.

`--verify` stays interactive. It runs the repository's own install, build, and test commands in a worktree (`npm ci`, `yarn`, `pnpm`, `uv`, `go`, `cargo`, `bundle`, `make`, `npx`, and whatever the workflows call), and the security evidence can run `pip-audit` or `govulncheck`. Those commands execute code from the PR under test, so none are in the list above: each prompts unless you add rules for the tool families your projects use.

## Examples

- "triage the dependabot PRs": gathers, classifies, and reports every open Dependabot PR, then offers actions
- "review the open Dependabot PRs and assess their merge safety": same behavior
- "are the Dependabot PRs safe to merge?": same behavior; the report answers, and the action offer follows
- "is PR 107 safe to merge?": triages that PR alone when it is a Dependabot PR
- "clean up the stale Dependabot PRs": same triage, with Superseded and Outdated PRs as the likely action

## See Also

- [Review Dependabot Config](../review-dependabot-config/README.md): review the `dependabot.yml` and repository settings behind these PRs
- [Monitor PR](../monitor-pr/README.md): watch a single refreshed Dependabot PR until it is ready to merge
- [Upgrade Everything](../upgrade-everything/README.md): replace several PRs that fight over one lockfile with a single package-manager upgrade
- [Create Issue](../create-issue/README.md): track a Needs work or Hold upgrade
- [All plugins](../../README.md)
