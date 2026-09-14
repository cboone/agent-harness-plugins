# Repository Settings

Dependabot's behavior depends on settings outside `dependabot.yml`. Each section gives the call, how to read the answer, and what to report. `OWNER/REPO` and `DEFAULT` stand for the repository and its default branch.

Workflow files are read from the default branch, since that is what runs, and from `OWNER/REPO` rather than whatever the working directory holds. In a checkout that matches `OWNER/REPO` (step 1 of the skill), search `origin/DEFAULT` with `git grep`. Without one, list the workflows through the contents API and search each file's raw content:

```bash
gh api 'repos/OWNER/REPO/contents/.github/workflows?ref=DEFAULT' --jq '.[].path'
gh api 'repos/OWNER/REPO/contents/PATH?ref=DEFAULT' -H 'Accept: application/vnd.github.raw+json' | grep -nE 'PATTERN'
```

Several of these endpoints need repository admin rights, and the alerts endpoint also accepts the `security_events` scope. A 403, or a 404 on an endpoint that exists, usually means missing permission. Report the check as not visible, never as passing.

## Dependabot alerts

```bash
gh api -i repos/OWNER/REPO/vulnerability-alerts
```

- **`204 No Content`**: alerts are enabled.
- **`404`**: alerts are disabled, or the caller cannot see the setting. Security updates cannot run without alerts. Report an Error when the caller has admin permission, otherwise "not visible".

## Security updates

```bash
gh api -i repos/OWNER/REPO/automated-security-fixes
```

- **`404`**: security updates are not enabled, when the caller has admin permission on the repository. Without admin permission the same 404 can mean the setting is not visible, so report it as "not visible" in that case. Report a Suggestion to enable them, unless the repository's policy says otherwise.
- **`{"enabled": true, "paused": false}`**: security update PRs are opened when an alert has a fix, whether or not a `dependabot.yml` exists.
- **`"paused": true`**: GitHub paused them, usually after a run of PRs nobody merged. Report a Warning: alerts keep arriving and no PRs follow.
- **`"enabled": false`**: treat like the 404 above.

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

A workflow Dependabot triggers through `push`, `pull_request`, `pull_request_review`, or `pull_request_review_comment` runs like a fork PR: its `GITHUB_TOKEN` is read-only, and it receives Dependabot secrets, not Actions secrets. A job on one of those events that needs an Actions secret fails on every Dependabot PR. `pull_request_target` runs are not restricted this way.

```bash
gh api --paginate --slurp 'repos/OWNER/REPO/dependabot/secrets?per_page=100' | jq '[.[].secrets[].name]'
gh api --paginate --slurp 'repos/OWNER/REPO/actions/secrets?per_page=100' | jq '[.[].secrets[].name]'
```

Then find the jobs that run on Dependabot PRs and use secrets:

```bash
git grep -nE 'secrets(\.|\[)' origin/DEFAULT -- .github/workflows/
```

For each secret referenced by a job that runs on `push`, `pull_request`, `pull_request_review`, or `pull_request_review_comment`, other than `GITHUB_TOKEN`:

- **Present in Dependabot secrets**: fine.
- **Missing, and the job will fail without it**: a Warning, with two fixes to offer. Mirror a read-only credential into Dependabot secrets (the user runs `gh secret set NAME --repo OWNER/REPO --app dependabot`), or skip the job on Dependabot runs. For `push` and `pull_request` jobs, `if: github.actor != 'dependabot[bot]'` does it. For `pull_request_review` and `pull_request_review_comment` jobs, `github.actor` is whoever reviewed, so guard on the PR author as well: `if: github.actor != 'dependabot[bot]' && github.event.pull_request.user.login != 'dependabot[bot]'`. Never mirror a credential that can write to production.
- **Missing, and the job handles its absence**: note it and move on.

Evidence from open PRs strengthens the finding: a check that fails on Dependabot PRs and passes on the default branch, with a log line such as `Input required and not supplied: token`.

Organization-level secrets (`gh api --paginate --slurp 'orgs/ORG/dependabot/secrets?per_page=100' | jq '[.[].secrets[].name]'`) need organization admin rights. When that call is refused, say the organization's Dependabot secrets were not checked.

Also check `registries` in `dependabot.yml`: every `${{secrets.NAME}}` it references must be a Dependabot secret.

## Labels

```bash
gh api --paginate 'repos/OWNER/REPO/labels?per_page=100' --jq '.[].name'
```

Compare with every `labels` value in the config. GitHub documents that a label missing from the repository is ignored, so the PR opens without it, and Dependabot has also been seen commenting that the label could not be found. The comparison is the finding; a comment like that on a recent Dependabot PR is supporting evidence:

```bash
gh api --paginate --slurp repos/OWNER/REPO/issues/N/comments |
  jq -r '.[][] | select(.user.login == "dependabot[bot]") | .body' | grep -A 2 'could not be found'
```

When `labels` is not set, Dependabot applies `dependencies` on its own, plus an ecosystem label when more than one ecosystem is configured, creating them if needed.

## Merge rules

```bash
gh api --paginate 'repos/OWNER/REPO/rules/branches/DEFAULT?per_page=100' --jq '.[]'
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
git grep -ln -e 'dependabot/fetch-metadata' -e "github.actor == 'dependabot\[bot\]'" -e 'pull_request_target' origin/DEFAULT -- .github/workflows/
```

For each workflow found:

- **Auto-merge steps** (`gh pr merge --auto`) fail when a ruleset requires an approving review, and the error GitHub returns can blame the merge method instead. Check the rules above before trusting the step, and report a Warning when the two cannot both succeed.
- **`pull_request_target`** runs the workflow from the base branch with a write-capable token and the repository's secrets. That is safe only while the workflow never runs code from the PR. A workflow that checks out the PR head under `pull_request_target` and builds or runs it is an Error.
- **`permissions:`** should be the minimum the job needs.

## Code owners

When `reviewers` appears in the config, check `.github/CODEOWNERS`, `CODEOWNERS`, or `docs/CODEOWNERS` on the default branch, read the same way as the workflows, for entries covering the manifests and lockfiles, since code owners are now the way Dependabot PRs get reviewers.
