# Repository Settings

Dependabot's behavior depends on settings outside `dependabot.yml`. Each section gives the call, how to read the answer, and what to report. `OWNER/REPO` and `DEFAULT` stand for the repository and its default branch.

Several of these endpoints need repository admin rights, and the alerts endpoint also accepts the `security_events` scope. A 403, or a 404 on an endpoint that exists, usually means missing permission. Report the check as not visible, never as passing.

## Dependabot alerts

```bash
gh api -i repos/OWNER/REPO/vulnerability-alerts
```

- **`204 No Content`**: alerts are enabled.
- **`404`**: alerts are disabled, or the caller cannot see the setting. Security updates cannot run without alerts. Report an Error when the caller has admin permission, otherwise "not visible".

## Security updates

```bash
gh api repos/OWNER/REPO/automated-security-fixes
```

- **`{"enabled": true, "paused": false}`**: security update PRs are opened when an alert has a fix, whether or not a `dependabot.yml` exists.
- **`"paused": true`**: GitHub paused them, usually after a run of PRs nobody merged. Report a Warning: alerts keep arriving and no PRs follow.
- **`"enabled": false`**: report a Suggestion to enable them, unless the repository's policy says otherwise.

Security updates follow some of the config and ignore the rest: `open-pull-requests-limit`, `cooldown`, and `exclude-paths` apply to version updates only. Say this whenever a finding depends on it.

## Open alerts with no fix path

```bash
gh api --paginate --slurp 'repos/OWNER/REPO/dependabot/alerts?state=open&per_page=100' |
  jq '[.[][] | {number, package: .dependency.package.name, manifest: .dependency.manifest_path, relationship: .dependency.relationship, severity: .security_advisory.severity, patched: .security_vulnerability.first_patched_version.identifier}]'
```

Compare against open Dependabot PRs. An alert with no PR usually means one of these:

- **The package is a transitive dependency that its parent pins exactly**, so no version satisfies both the fix and the parent. Only an upgrade of the parent, or an override in the manifest, resolves it.
- **The ecosystem gets version updates only**, so no security PR is ever opened (see `./ecosystems.md`).
- **No patched version exists yet** (`patched` is null).
- **Security updates are disabled or paused.**

Report these as Warnings with the likely cause. Fixing the dependency is outside a config review; the `triage-dependabot-prs` skill reports the same alerts alongside the PRs.

## Dependabot secrets

Workflows triggered by a Dependabot PR receive Dependabot secrets, not Actions secrets. A job that needs an Actions secret fails on every Dependabot PR.

```bash
gh api repos/OWNER/REPO/dependabot/secrets --jq '[.secrets[].name]'
gh api repos/OWNER/REPO/actions/secrets --jq '[.secrets[].name]'
```

Then find the jobs that run on Dependabot PRs and use secrets:

```bash
grep -rn 'secrets\.' .github/workflows/
```

For each secret a `pull_request` or `pull_request_target` job references, other than `GITHUB_TOKEN`:

- **Present in Dependabot secrets**: fine.
- **Missing, and the job will fail without it**: a Warning, with two fixes to offer. Mirror a read-only credential into Dependabot secrets (the user runs `gh secret set NAME --repo OWNER/REPO --app dependabot`), or skip the job on Dependabot runs with `if: github.actor != 'dependabot[bot]'`. Never mirror a credential that can write to production.
- **Missing, and the job handles its absence**: note it and move on.

Evidence from open PRs strengthens the finding: a check that fails on Dependabot PRs and passes on the default branch, with a log line such as `Input required and not supplied: token`.

Organization-level secrets (`gh api orgs/ORG/dependabot/secrets`) need organization admin rights. When that call is refused, say the organization's Dependabot secrets were not checked.

Also check `registries` in `dependabot.yml`: every `${{secrets.NAME}}` it references must be a Dependabot secret.

## Labels

```bash
gh label list --repo OWNER/REPO --limit 500 --json name --jq '[.[].name]'
```

Compare with every `labels` value in the config. When a label is missing, Dependabot opens the PR without it and comments that the label could not be found. Read the comments on recent Dependabot PRs for that message as evidence:

```bash
gh api --paginate --slurp repos/OWNER/REPO/issues/N/comments |
  jq -r '.[][] | select(.user.login == "dependabot[bot]") | .body' | grep -A 2 'could not be found'
```

When `labels` is not set, Dependabot applies `dependencies` (and an ecosystem label) on its own, creating them if needed.

## Merge rules

```bash
gh api repos/OWNER/REPO/rules/branches/DEFAULT
gh repo view OWNER/REPO --json mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed,deleteBranchOnMerge
gh api repos/OWNER/REPO --jq '{allow_auto_merge, allow_update_branch}'
```

Read the rules, not only branch protection: `branches/DEFAULT/protection` can return 404 while a ruleset still requires reviews or checks.

Report, as settings context rather than findings unless they cause harm:

- **Required approving reviews**: every Dependabot PR needs a person. Fine, but it rules out unattended auto-merge.
- **Strict required status checks** (branches must be up to date): each merge makes the other open Dependabot PRs behind, so every merge triggers a round of rebases and CI runs. Worth a Suggestion when many Dependabot PRs are open.
- **`allowed_merge_methods`** in the `pull_request` rule, against the repository's allowed methods. A mismatch makes merges fail with a confusing message.
- **`deleteBranchOnMerge` off**: merged Dependabot branches linger. A Suggestion.

## Dependabot automation workflows

```bash
grep -rln -e 'dependabot/fetch-metadata' -e "github.actor == 'dependabot\[bot\]'" -e 'pull_request_target' .github/workflows/
```

For each workflow found:

- **Auto-merge steps** (`gh pr merge --auto`) fail when a ruleset requires an approving review, and the error GitHub returns can blame the merge method instead. Check the rules above before trusting the step, and report a Warning when the two cannot both succeed.
- **`pull_request_target`** runs with write permissions and secrets on code from the PR. A workflow that checks out the PR head under `pull_request_target` is an Error.
- **`permissions:`** should be the minimum the job needs.

## Code owners

When `reviewers` appears in the config, check `.github/CODEOWNERS`, `CODEOWNERS`, or `docs/CODEOWNERS` for entries covering the manifests and lockfiles, since code owners are now the way Dependabot PRs get reviewers.
