# Add Dependabot PR triage and Dependabot config review skills

## Context

Dependabot PRs pile up across the user's repositories: 71 open under `cboone` and 123 under `swing-left` as of 2026-09-13. Past sessions show the same investigation repeated by hand each time, with the same traps:

- a green tick reporting on a base that no longer exists
- a `MERGEABLE` PR that would downgrade what the default branch already has
- CI that fails only because Dependabot runs cannot read repository secrets
- grouped PRs hiding a production-server major
- `@dependabot` commands that change over time
- the gap between a PR title, its branch name, and its actual diff

Configuration has matching drift:

- labels that do not exist
- uncovered manifests
- ecosystems left over after a migration
- no config at all in about 30 repos that have workflows or manifests

Nothing in the marketplace detects any of this. `pin-everything` is the only skill that writes `.github/dependabot.yml`, and neither `bootstrap-project` (#389) nor `refresh-project-scaffolding` (#388) consults it.

Intended outcome:

1. **`triage-dependabot-prs`**: gathers evidence on every open Dependabot PR in the current repository, puts each PR in exactly one category, and acts on the dispositions the user approves.
1. **`review-dependabot-config`**: reviews `dependabot.yml` together with the repository settings Dependabot depends on, and applies the fixes the user selects.
1. **Integrations** (all four chosen by the user): `monitor-pr` learns to handle Dependabot PRs, `refresh-project-scaffolding` detects Dependabot gaps (closes #388), `bootstrap-project` emits a Dependabot config (closes #389), and `upgrade-everything` checks for open Dependabot PRs before proposing an upgrade. `pin-everything` gets cross-references and a `uv` ecosystem fix.

The repository is `cboone/agent-harness-plugins`, not a fork and not archived. Plans are committed and kept here.

## Design decisions

- **Two plugins, both in the `ci-and-release` category.** Their closest siblings live there: `pin-everything`, `upgrade-everything`, `monitor-pr`, `optimize-runner-usage`.
- **A bundled script for the triage skill only.** Dependabot PR bodies reach 65 KB each, and one past session overflowed at 216 KB. The parsing heuristics (ecosystem, security versus version update, group shape, from/to versions, update type, flags) are fragile enough to deserve scrut coverage. The script follows the `resolve-copilot-threads` shape: a network `fetch` and a pure `summarize` over stdin, so tests feed recorded JSON with no `gh` stub. The config reviewer runs inline `gh` calls, because its checks are judgment-heavy and small.
- **The skills hold no private context.** Examples use generic names (`example-org/example-repo`). Nothing cites `swing-left` repositories or PR numbers, since the marketplace is public.
- **Actions are always gated.** Both skills report first, then ask. Writes that reach outside the working tree (merge, close, comment, approve, label creation, settings changes) happen only after the user selects them. Approvals on the user's behalf happen only when the user asks for that. The skills never use `--admin`, never push to a Dependabot branch without an explicit request, and never set secret values.
- **Codex CLI and OpenCode fallbacks** follow house precedent:
  - the unsubstituted `${CLAUDE_PLUGIN_ROOT}` falls back to the `**/triage-dependabot-prs/**/scripts/dependabot-prs` locator, as in `resolve-copilot-pr-feedback`
  - `ScheduleWakeup` falls back to `sleep`, as in `monitor-pr`
  - `AskUserQuestion` falls back to a numbered question in plain text

## 1. Script: `plugins/triage-dependabot-prs/scripts/dependabot-prs`

Bash, no extension, executable, `#!/usr/bin/env bash`, `set -euo pipefail`, with the `usage`, `die`, `do_*` and `main` layout of `plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads`. Invoke the `write-bash-scripts` skill before writing it.

### `fetch --repo OWNER/REPO [--limit N] [--raw]`

Requires `gh` (authenticated) and `jq`. It builds one bundle object and pipes it to `summarize`, or prints the bundle as-is under `--raw`. The bundle holds:

- `dependabot`: `gh pr list --repo R --author app/dependabot --state open --limit N --json number,title,url,headRefName,headRefOid,baseRefName,body,createdAt,updatedAt,labels,isDraft,mergeable,mergeStateStatus,reviewDecision,autoMergeRequest,statusCheckRollup,files`.
- `open`: every open PR (`--json number,title,author,headRefName,files`), for overlap detection with human PRs.
- `defaultBranch` and `isArchived`, from `gh repo view R --json defaultBranchRef,isArchived`.
- `compare[number]`: `gh api repos/R/compare/<default>...<headRefOid>`, reduced to `status`, `ahead_by`, `behind_by`, and commit authors (`.author.login // .commit.author.name`).
  - This is the reliable test for non-Dependabot commits. When GitHub has a stale base, `gh pr view --json commits,files` shows other authors' commits that are not really on the branch.
- `alerts`: `gh api --paginate --slurp 'repos/R/dependabot/alerts?state=open&per_page=100'`. A 403 or 404 records `{"available": false, "reason": ...}` instead of failing.
- `fetchedAt` and `limit`. When either list returns exactly `limit` items, a warning goes to stderr.

### `summarize [--now ISO8601]`

Reads the bundle on stdin and emits a compact JSON document with no bodies:

```json
{
  "repo": "", "defaultBranch": "", "isArchived": false, "fetchedAt": "", "count": 0,
  "limit": 200, "limitReached": false, "alertsAvailable": true, "alertsReason": null,
  "unmatchedAlerts": [{ "package": "", "manifest": "", "count": 0, "highestSeverity": "", "patched": [], "numbers": [] }],
  "prs": [{
    "number": 0, "title": "", "url": "", "branch": "", "base": "", "baseIsDefault": true,
    "ecosystem": "github_actions", "kind": "security|version|unknown", "shape": "single|group|multi",
    "group": null,
    "updates": [{ "name": "", "from": "", "to": "", "type": "major|minor|patch|digest|unknown", "semverBreaking": true }],
    "updatesExpected": null, "branchAgrees": true, "commandsFooter": true, "bodyTruncated": false,
    "rebasesDisabled": false, "draft": false, "labels": [],
    "ageDays": 0, "updatedDaysAgo": 0,
    "mergeable": "", "mergeStateStatus": "", "reviewDecision": "", "autoMerge": false,
    "checks": { "total": 0, "success": 0, "failure": 0, "pending": 0, "skipped": 0, "neutral": 0, "failing": [], "newestCompletedAt": null },
    "files": [],
    "overlaps": [{ "number": 0, "author": "", "sharedFiles": [] }],
    "compare": { "status": "", "aheadBy": 0, "behindBy": 0, "nonDependabotCommits": 0 },
    "alerts": [{ "number": 0, "package": "", "severity": "", "ghsa": "", "manifest": "", "patched": "" }]
  }]
}
```

Parsing rules, each covered by a test:

- **`ecosystem`**: the second segment of `dependabot/<ecosystem>/...`.
- **`kind`**: `security` when the body contains `disable automated security fix PRs`, `version` when it has the commands footer without that line, and `unknown` when the footer is gone. A rebase can rewrite the body without its footer (observed on a live PR during implementation), so an absent footer is never evidence of a version update.
- **`shape`**:
  - `group` when the title matches `the <name> group` (the name goes into `group`)
  - `multi` when the last branch segment is `multi-<10 hex>`
  - otherwise `single`
- **`updates`** come from the first source that yields results:
  1. body lines ``Updates `name` from A to B``
  1. the title `bump NAME from A to B`
  1. the body `Bumps [NAME](...) from A to B`

  If none matches, `updates` is empty, and the skill tells the agent to read the diff.

- **`type`**:
  - strip a leading `v` from both versions
  - `digest` when both values are hex SHAs
  - otherwise the position that changed: `major`, `minor`, or `patch`
  - `unknown` when the versions do not parse, or only a suffix changed
- **`semverBreaking`**: true for a major, a 0.x minor, or a 0.0.x patch; null for digests and unparseable versions. Reported beside `type` rather than folded into it, because some ecosystems (Go x/ modules, for one) ship stable 0.x releases and a folded `major` would over-flag them.
- **`updatesExpected`**: the count a grouped title announces (`with N updates`). A parsed list shorter than it means the body was truncated.
- **`branchAgrees`**: `false` when the version suffix on a single-dependency branch differs from the title's target version. A title updated in place leaves a stale branch name, so the diff is the truth.
- **`commandsFooter`** and **`bodyTruncated`**: whether `You can trigger Dependabot actions` survived, and whether the body contains `_Description has been truncated_`.
- **`rebasesDisabled`**: the body contains `Automatic rebases have been disabled`.
- **`checks`**: CheckRun entries map through `status` and `conclusion`. `FAILURE`, `TIMED_OUT`, `CANCELLED`, `ACTION_REQUIRED` and `STARTUP_FAILURE` count as failures. StatusContext entries map through `state`.
- **`overlaps`**: other open PRs, of any author, whose file paths intersect this PR's.
- **`alerts`**: open alerts whose package name matches an update name and whose manifest path is in `files` or shares a directory with one. Alerts that match no PR go to `unmatchedAlerts`, grouped by package and manifest with a count and the highest severity, since a repository can carry dozens of alerts for a handful of packages.

### Errors

Unknown subcommand, malformed JSON, or a missing required field exits 1 with a message on stderr. `--help` prints usage. `fetch` validates its arguments before checking for `gh`, so usage errors are testable without credentials.

## 2. Plugin: `triage-dependabot-prs` (1.0.0)

```text
plugins/triage-dependabot-prs/
├── .claude-plugin/plugin.json
├── README.md
├── scripts/dependabot-prs
└── skills/triage-dependabot-prs/
    ├── SKILL.md
    └── references/
        ├── categories.md
        ├── evidence.md
        ├── verification.md
        └── actions.md
```

### SKILL.md frontmatter

`name` plus a folded `description`: what the skill does, then the trigger phrases, then the requirements. Trigger phrases come from the user's real prompts:

- "triage dependabot PRs"
- "review the open Dependabot PRs"
- "are the Dependabot PRs safe to merge"
- "assess their merge safety"
- "review the newly opened Dependabot PRs"
- "clean up stale Dependabot PRs"
- "is this Dependabot PR safe to merge"

The description ends with "Requires the gh CLI to be installed and authenticated, and jq." The marketplace description stays under 320 characters.

### Options

- **`[<pr-number>...]`**: restrict the run to these PRs.
- **`--repo OWNER/REPO`**: required in a fork (see step 1).
- **`--verify`**: run local verification for every Needs testing PR before reporting.
- **`--report-only`**: report and stop; offer no actions.

### Workflow

1. **Pre-flight.**
   - Run `date`.
   - Resolve `OWNER/REPO` from the `origin` remote unless `--repo` is given. An `upstream` remote means `gh` would resolve to the third-party project, so pass `--repo` on every call.
   - Run `gh repo view --json isArchived,isFork,parent,defaultBranchRef,viewerDefaultMergeMethod`. An archived repository gets a read-only report and no actions.
   - Run `git fetch origin`.
1. **Gather.**
   - Run the script's `fetch` into a scratch file.
   - Read `.github/dependabot.yml` from `origin/<default>`.
   - Read repository merge settings: `gh api repos/O/R` fields `allow_merge_commit`, `allow_squash_merge`, `allow_rebase_merge`, `allow_auto_merge`, `delete_branch_on_merge`.
   - Read rules on the default branch: `gh api repos/O/R/rules/branches/<default>`. Branch protection can 404 while rulesets still block merges.
   - Read agent config for held-major or freeze policy.
   - With zero Dependabot PRs: report, list `unmatchedAlerts`, suggest the `review-dependabot-config` skill if no config exists, and stop.
1. **Collect evidence per PR** using `./references/evidence.md`. Independent API calls run in parallel.
   - Every PR gets the baseline checks: freshness, target versus default branch, overlap, and CI meaningfulness.
   - Majors, grouped PRs, runtime dependencies, security PRs, and `github_actions` PRs also get the deeper checks.
1. **Classify** each PR into exactly one category using `./references/categories.md`, plus orthogonal flags. Compute the merge order and check for predicted conflicts:
   - `git fetch origin pull/N/head:dependabot-pr-N`
   - `git merge-tree --write-tree origin/<default> dependabot-pr-N`, and pairwise for PRs that overlap
1. **Report** in the terminal. Include:
   - a counts line
   - one table per non-empty category: `| PR | Update | Type | Security | Evidence | Recommended action |`
   - the merge order
   - verification suggestions
   - config observations, handed to the `review-dependabot-config` skill

   Assert that the categories account for every fetched PR exactly once.

1. **Offer actions** unless `--report-only`. Use batch options built from the categories, as in past sessions: "Merge the 4 safe PRs in order and close the 3 superseded (Recommended)", "Merge only", "Close only", "Leave as is", plus free-form selection by PR number.
1. **Execute** the approved actions per `./references/actions.md`, re-checking state before each write.
1. **Wrap up.**
   - Re-query open alerts. A merge can introduce a new vulnerable transitive dependency.
   - Summarize under Merged, Rebase requested, Closed, Issues created, Held, Left for the user, and Failed, with links.

### `references/categories.md`: precedence, first match wins

| #   | Category          | Matches when                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Recommended action                                                                                                                             |
| --- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Superseded**    | The change is already delivered or replaced. The default branch is at or beyond every target version, so merging is a no-op or a downgrade even when `MERGEABLE`. Or a newer open PR updates the same dependency in the same directory to a higher version. Or a human PR or commit consolidated it.                                                                                                                                                                                                                                                                          | Close with a comment naming the replacement and a "This PR / On `<default>`" version table                                                     |
| 2   | **Outdated**      | The premise is gone. The manifest, lockfile, or workflow was deleted. Or the ecosystem was migrated (`pip` to `uv`). Or the directory is excluded or managed elsewhere. Or the base branch is not the default and no `target-branch` names it.                                                                                                                                                                                                                                                                                                                                | Close and delete the branch. If the config would regenerate the PR, hand off to the `review-dependabot-config` skill                           |
| 3   | **Hold**          | A deliberate deferral with evidence: a held-major comment (`# v2.3.4, held at v2 ...`), an open tracking issue for this upgrade, or a freeze documented in agent config or `dependabot.yml` comments.                                                                                                                                                                                                                                                                                                                                                                         | Leave open, or run a currently advertised `@dependabot ignore ...` command on the user's decision                                              |
| 4   | **Needs refresh** | The change is wanted, but the PR state is out of date:<br>• `DIRTY`<br>• checks ran on a base that is behind the default branch where the intervening changes touch relevant files<br>• `rebasesDisabled`<br>• `branchAgrees: false` with a diff that differs from the title<br>• confirmed non-Dependabot commits<br>• another PR must land first                                                                                                                                                                                                                            | `@dependabot rebase`. Use `@dependabot recreate` when the branch has edits, only after the user confirms they can be discarded. Then re-triage |
| 5   | **Needs work**    | Cannot merge as-is: a CI failure caused by the change (not secret starvation), a documented breaking change requiring code edits, a peer or engine conflict, or an install failure.                                                                                                                                                                                                                                                                                                                                                                                           | A tracking issue via the `create-issue` skill (one issue per outstanding upgrade), a separate migration PR, or an ignore command               |
| 6   | **Needs testing** | Current and conflict-free, but the evidence is insufficient:<br>• a major bump<br>• a runtime dependency that CI does not exercise<br>• a grouped PR containing any major<br>• CI that is vacuous: ignored paths, the tool version pinned elsewhere, no CI at all<br>• CI failures that are only secret starvation (`Input required and not supplied: token` and the like)<br>• action or reusable-workflow repositories where consumers carry the risk<br>• a change in an action's `runs.using` runtime<br>• release notes that are truncated and not fetched from upstream | Specific verification steps from `./references/verification.md`. A PR that passes is promoted to Safe to merge                                 |
| 7   | **Safe to merge** | All of these hold:<br>• current against the default branch, or behind only on unrelated files<br>• checks pass and exercise the change<br>• no unresolved conflicts<br>• release notes show no breaking change that affects the repository<br>• for Actions, the SHA resolves to the tagged commit and the version comments are correct                                                                                                                                                                                                                                       | Merge with the repository's method, in the computed order                                                                                      |

The precedence has two consequences:

- **A grouped PR takes its riskiest member's category.** The file says so, and names `@dependabot ignore <dependency name> major version` as the way to split a member out.
- **Flags stay separate from categories.** `security` (with severity), `group`, `major`, `stale checks`, `secret-starved CI`, and `version comment drift` affect priority within a category, never the category itself. Security PRs sort first, by severity.

### `references/evidence.md`: checklist with commands

- **Freshness.**
  - Use `compare.behindBy`.
  - Check whether the files changed on the default branch since the merge base overlap this PR's files.
  - Compare the newest check completion time against the default branch tip.
  - Treat `mergeable: UNKNOWN` as not yet computed and re-query.
  - Check the timeline for `head_ref_force_pushed`, which shows Dependabot rebased.
  - A push that happened while Dependabot was cloning shows up as unrelated commits, and `@dependabot rebase` fixes it.
- **Target versus default branch.** Read the manifest, lockfile, or workflow at `origin/<default>` for every update and compare versions. This is the downgrade check.
- **Overlap.** Use `overlaps` from the script, plus `git merge-tree` for pairs.
  - Same lockfile or same workflow file means sequential merges with rebases in between.
  - The same dependency in different directories is not a duplicate.
- **CI meaningfulness.**
  - Do the checks exercise the changed files? Look at `.prettierignore` and similar ignore files, and at tool versions pinned in workflow `env:` that override the manifest.
  - Read failing logs with `gh run view <id> --log-failed`, taking the run id from the segment after `/runs/`.
  - Classify secret-starvation signatures.
  - A repository with no CI at all counts as vacuous.
- **Change content.**
  - Release notes and changelog from the body. When the body is truncated, fetch `gh api repos/X/releases/tags/<tag>`.
  - Breaking changes and migration notes.
  - For dependencies used in production, grep the consumers of the changed APIs.
- **GitHub Actions specifics.**
  - Resolve tag to SHA, dereferencing annotated tags through `git/tags/<sha>`.
  - `runs.using` from `action.yml` at the new SHA.
  - Version comments in the diff: Dependabot updates full `# vX.Y.Z` comments but not reliably major-only `# v6` ones.
  - Triggers such as `pull_request_target` and `workflow_run` that a new major restricts.
  - In a reusable-workflow repository, the consumer impact.
- **Security.**
  - The alerts matched to the PR and their severity.
  - Whether the PR bumps a direct dependency that the title does not name.
  - `unmatchedAlerts`.
- **Supply chain (optional depth).** Commit verification, and npm provenance via `npm view pkg@ver dist.attestations`.

### `references/verification.md`: local runs in a detached worktree under the scratch directory

- **Build the would-be merge result.** `git worktree add --detach <dir> dependabot-pr-N`, then `git -C <dir> merge --no-edit origin/<default>`.
- **Install without changing the lockfile:**

  | Package manager | Command                               |
  | --------------- | ------------------------------------- |
  | npm             | `npm ci --ignore-scripts`             |
  | Yarn Berry      | `yarn install --immutable`            |
  | Yarn classic    | `yarn install --frozen-lockfile`      |
  | pnpm            | `pnpm install --frozen-lockfile`      |
  | uv              | `uv sync --locked`                    |
  | Go              | `go build ./... && go test ./...`     |
  | Cargo           | `cargo test --locked`                 |
  | Bundler         | `bundle install` with frozen settings |

- **Run the checks.** Run the project's own `make test` or `make lint` targets after reading its agent config. Run the same commands on `origin/<default>` as a control.
- **Guard against vacuous passes.** Include a positive control where a linter might pass vacuously (a planted violation).
- **Clean up.** Remove the worktree afterwards.

### `references/actions.md`

- **Merge.**
  - Merge one PR at a time in the computed order.
  - Re-query `mergeable,mergeStateStatus,headRefOid,statusCheckRollup` before each merge.
  - Use the repository's allowed method (`viewerDefaultMergeMethod` when several are allowed).
  - Pass `--delete-branch` only when `delete_branch_on_merge` is off.
  - Never use `--admin`. Report `BLOCKED` with the unmet rule.
  - After each merge, re-query the remaining PRs and request rebases only for the ones that turned `DIRTY`.
- **Rebase or recreate.**
  - `gh pr comment N --repo O/R --body "@dependabot rebase"`.
  - Wait with `ScheduleWakeup` (fallback `sleep`) for `headRefOid` to change and checks to conclude, then re-triage those PRs.
  - Read Dependabot's reply comments for refusals, such as a branch edited by someone else.
  - For one PR the user wants watched until it is ready, invoke the `monitor-pr` skill with a Parent continuation block.
- **Close.**
  - Write the comment with the Write tool to a `mktemp -u` path, then `gh pr comment N --body-file <path>`, then `gh pr close N --delete-branch`, following the `use-git` skill's tmpfile rules.
  - Comment templates: Superseded (replacement link plus version table), Outdated (what disappeared and where), and consolidated replacement.
- **Ignore.** Use only the commands advertised by current PRs.
  - Single-dependency PRs: `@dependabot ignore this major version`, `ignore this minor version`, `ignore this dependency`.
  - Group PRs: `@dependabot ignore <dependency name> [major|minor] version` and `unignore`.
  - `merge`, `squash and merge`, `close`, and `reopen` are no longer advertised.
  - Ignore commands close the PR, so each one needs the user's decision.
- **Consolidate.** When several PRs touch one lockfile, or the security fixes are transitive-only, offer a single branch that applies the upgrades through the package manager (`npm audit fix`, `yarn up`, `pnpm update`, `uv lock --upgrade-package`). Point to the `upgrade-everything` skill for a broader pass. After that branch merges, close the PRs as Superseded.
- **Tracking issues.** Invoke the `create-issue` skill.
- **Approve.** Only when explicitly asked: `gh pr review N --approve --body-file <path>`.
- **Never** push to a Dependabot branch unless the user asks for it. Pushing stops Dependabot from rebasing the branch. If the user does ask, rebase first, then push, and warn that `recreate` discards the push.

### README and permissions

`README.md` follows the house anatomy:

- a first paragraph matching the marketplace description exactly
- `**Type:** Skill`, `**Trigger:** /triage-dependabot-prs`, and `**Requires:**` `gh` (authenticated) and `jq`
- Installation, What It Does (the category table), Usage with an options table, Recommended Permissions, Examples, and See Also

See Also lists Review Dependabot Config, Monitor PR, Upgrade Everything, Create Issue, and All plugins.

The permissions block lists every command the skill runs, write commands included:

- `Bash(bash "*/dependabot-prs" *)`
- `gh pr list`, `view`, `checks`, `diff`, `comment`, `close`, `merge`, `review`
- `gh api repos/*` and `gh api --paginate --slurp repos/*`
- `gh repo view`, `gh run view`, `gh run list`
- `git fetch`, `git merge-tree`, `git show`, `git worktree add` and `remove`

## 3. Plugin: `review-dependabot-config` (1.0.0)

```text
plugins/review-dependabot-config/
├── .claude-plugin/plugin.json
├── README.md
└── skills/review-dependabot-config/
    ├── SKILL.md
    └── references/
        ├── checklist.md
        ├── ecosystems.md
        └── repository-settings.md
```

### Frontmatter triggers

- "review dependabot config"
- "review dependabot settings"
- "audit dependabot.yml"
- "check the Dependabot configuration"
- "do we have Dependabot checks on everything"
- "why isn't Dependabot opening PRs"
- "stop Dependabot from updating a directory"

The description ends with "Requires the gh CLI to be installed and authenticated."

### Options

- `--repo OWNER/REPO`
- `--report-only`

### Workflow

1. **Pre-flight.**
   - `date`, repository resolution, and the fork and archived checks, as in the triage skill.
   - Read the config from both the working tree and `origin/<default>`, and report any drift between them.
   - Having both `.yml` and `.yaml` is an Error.
1. **No config.**
   - Report the ecosystems a config would cover.
   - Report any security-update-only PR activity.
   - Offer to invoke the `pin-everything` skill with `--scope dependabot` to write the house baseline, then stop.
1. **Inventory the repository** per `./references/ecosystems.md`:
   - manifests and lockfiles, and the directories that hold them
   - workflows
   - composite actions with external `uses:` (these need their own `directories` entries)
   - separate install trees versus workspace members
   - subtrees managed elsewhere
   - the style of version comments on SHA pins

   Exclude `node_modules/`, `vendor/`, `dist/`, `.venv/`, and `target/`.

1. **Review** against `./references/checklist.md`. Each finding gets a severity (Error, Warning, or Suggestion), evidence, and a fix. The checklist areas follow.
   - **Coverage.**
     - Ecosystems present but not configured.
     - Manifest directories not covered.
     - Entries whose manifests are gone, including legacy `pip` after a `uv` migration.
     - Composite action directories.
     - `docker`, `devcontainers`, `gitsubmodule`, and `terraform` when present.
   - **Validity.**
     - `version: 2`.
     - Schema validation with `uvx check-jsonschema --builtin-schema vendor.dependabot` when `uv` is available. Confirm the builtin name during implementation, and treat an unknown-key error on a recently added key as schema lag.
     - Never call a key invalid without checking current GitHub docs. `directories`, `exclude-paths`, `cooldown`, `multi-ecosystem-groups`, and group `applies-to` are valid, and a past session wrongly removed `exclude-paths`.
     - `directory` and `directories` must not both appear.
     - No duplicate ecosystem, directory, and target-branch combinations.
     - Retired keys, such as `reviewers` in favor of CODEOWNERS. Verify against the docs at run time.
     - Every label named exists (`gh label list --json name --limit 500`). Recent Dependabot "labels could not be found" comments count as evidence.
   - **Grouping and volume.**
     - Groups present. The minor-and-patch versus major split is the house baseline from `pin-everything`.
     - Overlapping group patterns.
     - Grouping of security updates.
     - `open-pull-requests-limit`: 0 disables version updates, and SHA pins need headroom.
     - A consistent schedule: interval, day, time, and timezone.
     - `cooldown` as a supply-chain suggestion.
     - PR volume against CI minutes, pointing to the `optimize-runner-usage` skill.
   - **Update behavior.**
     - `versioning-strategy` for applications versus libraries (for example, `increase` keeps exact pins exact).
     - A `commit-message` prefix consistent with the repository's Conventional Commits and any PR-title check workflow. With no config, titles come out as `build(deps):` or `Bump`.
     - Stale or overly broad `ignore` rules.
     - `exclude-paths` and excluded-directory patterns. Note that security updates have still opened for excluded paths, and verify the current behavior against the docs.
     - `target-branch` exists.
     - `registries` whose secrets exist in Dependabot scope.
   - **Repository settings**, per `./references/repository-settings.md`.
     - Alerts enabled: `gh api -i repos/O/R/vulnerability-alerts` returns 204 when on and 404 when off.
     - `gh api repos/O/R/automated-security-fixes`, for enabled and paused.
     - Dependabot secrets (`gh api repos/O/R/dependabot/secrets`) against `secrets.*` used by jobs that run on `pull_request`. Recommend mirroring read-only secrets into Dependabot scope, or gating the job with `if: github.actor != 'dependabot[bot]'`.
     - Rulesets (`rules/branches/<default>`), including required reviews and strict up-to-date requirements that cause rebase churn.
     - Allowed merge methods, `allow_auto_merge`, and `delete_branch_on_merge`.
     - Existing Dependabot automation workflows: `dependabot/fetch-metadata`, `pull_request_target`, and auto-merge steps that rulesets make fail.
     - Open alerts with no PR, meaning transitive dependencies exact-pinned by a parent, with the resolution options.
     - A 403 is reported as "not visible with current permissions", never as a pass.
   - **Surfaces Dependabot does not cover.** `.tool-versions`, `packageManager`, tool versions pinned in workflow `env:`, install commands, action refs in Markdown, and checksums. Point to the `pin-everything` skill's version-audit step and the `upgrade-everything` skill.
1. **Report.**
   - A coverage matrix: `| Ecosystem | Directories present | Configured | Status |`.
   - A settings table.
   - Findings grouped by severity: `| # | Severity | Area | Finding | Evidence | Fix |`.
   - Observations about open Dependabot PRs, suggesting the `triage-dependabot-prs` skill.
1. **Ask which fixes to apply**, unless `--report-only`. Local file edits and outward-facing changes are offered separately:
   - Label creation and repository settings are confirmed individually.
   - Secrets are never written by the skill. Tell the user to run `gh secret set NAME --app dependabot` themselves.
1. **Apply.**
   - Merge edits into `dependabot.yml`, preserving comments and the user's own groups, and show the diff before writing (the merge rule from `pin-everything`).
   - Re-validate.
   - Create labels on approval.
   - Invoke the `lint-and-fix` skill.
   - Summarize under Applied, Skipped, Needs user action, and Follow-up, and suggest `/commit` or `/pr`.

README: `**Requires:**` `gh` (authenticated). Recommended Permissions lists `gh api repos/*`, `gh api -i repos/*`, `gh label list`, `gh label create`, `gh repo view`, `gh pr list`, `git show`, `git fetch`, and `uvx check-jsonschema *`. See Also lists Triage Dependabot PRs, Pin Everything, Refresh Project Scaffolding, Optimize Runner Usage, and All plugins.

## 4. Changes to existing skills

| Plugin                        | Version        | Change                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ----------------------------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `monitor-pr`                  | 1.1.2 to 1.2.0 | Add `author` to the step 1 snapshot. A PR authored by `app/dependabot` (or with a `dependabot/` head branch) is a Dependabot PR.<br><br>New subsection with its rules:<br>• **Copilot axis.** Not applicable unless a Copilot review already exists at the head. Never request one.<br>• **Step 5 sync.** Post `@dependabot rebase` once per head SHA instead of invoking `merge-main`, then wait for the head to move. On a refusal, escalate and offer `@dependabot recreate`.<br>• **Step 6 failing checks.** Never push. Report secret-starved failures as an environment issue that points to the `review-dependabot-config` skill. Escalate real breakage and point to the `triage-dependabot-prs` skill.<br><br>Also: update Ready Criteria, Error Handling, the README (What It Does, See Also, `gh pr comment` permission), and the description if it fits.                                                                                                                                                                                                                                                                      |
| `refresh-project-scaffolding` | 2.0.3 to 2.1.0 | Closes #388.<br><br>• **Step 2 table.** Add a `pin-everything` row with `.github/dependabot.yml` (or `.yaml`).<br>• **Missing file.** Unlike other tools, a missing file is actionable when the repository has workflows or a supported manifest: report `Needs update` naming `pin-everything`.<br>• **New reference section, "Dependabot Config Checks (pin-everything)".** Checks that the file is present, that it has `version: 2`, and that each common manifest has its ecosystem: `package.json` to `npm`, `go.mod` to `gomod`, `Cargo.toml` to `cargo`, `uv.lock` to `uv`, `pyproject.toml` or `requirements*.txt` to `pip`, `Gemfile` to `bundler`, `composer.json` to `composer`, `Dockerfile` to `docker`, workflows to `github-actions`.<br>• **Step 6 strategies.** Missing config is a full re-run: `pin-everything --scope dependabot`. Coverage gaps or anything deeper: invoke `review-dependabot-config`.<br>• **Execution order and skill list.** Add `pin-everything` after `set-up-installers` and `add-scrut-cli-tests`, before `optimize-runner-usage`. Add both skills to the skill list.<br><br>README updated. |
| `bootstrap-project`           | 1.3.1 to 1.4.0 | Closes #389.<br><br>• **Step 2 table.** Add a `.github/dependabot.yml` row provided by `pin-everything`.<br>• **Execution order.** `pin-everything`, scoped down to `--scope dependabot`, runs **last**, after `add-scrut-cli-tests`. The issue proposed placing it after `set-up-secret-scanning`, but its own reasoning (run once every workflow and manifest exists) argues for last, since installers and scrut tests can add workflows.<br>• **Steps 3 and 5.** Add a key overlap rule and a step 5 list entry with the scope-down instruction.<br>• **`references/overlap-rules.md`.** Scope-Down Details: the scaffolders already SHA-pin actions, and a full pinning pass is a separate decision. Applicability row: any project with workflows or a Dependabot-supported manifest.<br>• **Existing config.** Report `Already set up`, and the step 6 summary suggests `/review-dependabot-config`.<br><br>README updated.                                                                                                                                                                                                        |
| `upgrade-everything`          | 1.0.1 to 1.1.0 | • **Steps 4 and 5.** Run `gh pr list --author app/dependabot --state open --json number,title,headRefName` and match candidates by dependency name and target version.<br>• **Step 6 matrix.** Add an `Open PR` column.<br>• **Recommendation.** A candidate already proposed by an open Dependabot PR at or beyond the latest version recommends triaging that PR with the `triage-dependabot-prs` skill rather than applying it locally.<br>• **Step 9.** When a local upgrade makes open Dependabot PRs redundant, list them as Superseded follow-ups.<br><br>README See Also updated.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `pin-everything`              | 1.1.0 to 1.1.1 | • **Step 9 and Error Handling.** Point to the `review-dependabot-config` skill for auditing an existing config.<br>• **`references/dependabot.md`.** Add the missing `uv` ecosystem row (`uv.lock` to `uv`). A `pip` entry for a `uv` project fails on every run.<br><br>README See Also adds both new skills.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |

Write cross-references as ``the `name` skill`` or `` `/name` `` so `bin/check-cross-references` validates them. Bare names in descriptions are not checked, so keep those accurate by hand.

## 5. Repository wiring

- **`.claude-plugin/marketplace.json`.**
  - Insert `review-dependabot-config` after `review-branch`, and `triage-dependabot-prs` between `suggest-next-issue` and `upgrade-everything`.
  - Mirror each edited plugin's version.
  - Recompute `metadata.version` with `bin/compute-catalog-state`. Starting from `catalog-M67-m92-p156-n54`, the expected result is `catalog-M69-m96-p150-n56`. Trust the script, since another branch may bump versions first.
- **Root `README.md`, CI and Release table.**
  - Add "Review Dependabot Config" between Pin Everything and Set-Up CI.
  - Add "Triage Dependabot PRs" between Set-Up Secret Scanning and Upgrade Everything.
  - Add the matching `**External tools:**` bullets.
- **`AGENTS.md`.** Add `triage-dependabot-prs` to the list of plugins that bundle `scripts/`.
- **Tests.**
  - `tests/scrut/dependabot-prs.md`, following `tests/scrut/resolve-copilot-threads.md`. Invoke the `write-scrut-tests` skill first.
  - `tests/data/dependabot-prs/` holds synthetic bundles:
    - a single SHA-pinned Actions major
    - a group spanning two directories
    - a security group of Go modules with matched alerts
    - a SHA-to-SHA digest
    - a non-default base with rebases disabled, `DIRTY`, and an overlapping duplicate
    - a truncated group body with no commands footer
    - a title and branch that disagree
    - a `0.x` minor bump classified as `major`
    - alerts unavailable
    - an empty list
    - the limit reached
    - malformed input
- **`Makefile` and `.github/workflows/ci.yml`.** Add `DEPENDABOT_PRS_BIN` and `DEPENDABOT_PRS_DATA_DIR` to `SCRUT_ENV` and to the literal `scrut-env` list, in alphabetical position. `bin/list-shell-scripts` picks up the script automatically.
- **Mirrors.** Run `bin/build-codex-marketplace` and `bin/build-opencode-mirror` in every commit that touches plugin sources, so each commit validates on its own.

## 6. Commit sequence

Conventional Commits, GPG-signed, via the `commit` skill:

1. `docs: plan Dependabot triage and config review skills`
1. `feat: add triage-dependabot-prs and review-dependabot-config skills`, together with the script and its scrut coverage. The two skills name each other as skills, which `bin/check-cross-references` resolves, and the script lives inside the triage plugin, which rule 1 requires to have a manifest, so no smaller split validates on its own.
1. `feat: handle Dependabot PRs in monitor-pr`
1. `feat: detect Dependabot config gaps in refresh-project-scaffolding` (`Closes #388`)
1. `feat: add Dependabot config to bootstrap-project` (`Closes #389`)
1. `feat: check open Dependabot PRs in upgrade-everything`
1. `fix: add uv ecosystem and config review pointer to pin-everything`

## 7. Verification

- **Repository gates:**
  - `bin/check-cross-references` while editing
  - `make test-all` (lint, validate, scrut) before each commit that changes a plugin
  - the `check-versions` skill before any PR
- **Script against real data (read-only).**
  - `plugins/triage-dependabot-prs/scripts/dependabot-prs fetch --repo cboone/gh-actions` and `--repo cboone/bopca`.
  - Confirm the summary's shape: ecosystem, kind, update type, alert matches for the Go security group, and `compare` counts for PRs that look like they carry foreign commits.
- **Triage skill, report-only.** Load the worktree copy with `claude --plugin-dir ./plugins/triage-dependabot-prs` (confirm the flag), then run `/triage-dependabot-prs --report-only`.
  - In `cboone/bopca`, expect:
    - reusable-workflow bumps already replaced on the default branch: Superseded or Outdated
    - the tag-pinned majors: Needs testing
    - the security group: security-flagged and prioritized
    - the PR with a failing scrut check: Needs work or Needs refresh, depending on the evidence
  - In `cboone/catamount-hardware`, expect the non-default `staging` base and duplicate `maplibre-gl` PRs to resolve to Superseded and Outdated.
  - Post no comments.
- **Config review, report-only**, with expected findings:
  - `cboone/ke`: a missing `dependencies` label and inconsistent labels
  - `cboone/bopca`: `benchmarks/go.mod` not covered
  - `cboone/fosforo`: no false positive for a composite action with no external `uses:`
  - a repository with no config and security-only PRs: offers `pin-everything --scope dependabot`
- **`refresh-project-scaffolding`** (#388 acceptance): reports the gap and names `pin-everything` in a repository without a config, and reports no false positive in this repository.
- **`bootstrap-project`** (#389 acceptance): plan presentation only, stopping at approval.
  - A scratch Go CLI repository and a scratch repository whose only manifest is a `package.json` both show the scoped-down `pin-everything` row.
  - A repository with a config shows `Already set up`.
- **`monitor-pr`**: `/monitor-pr <n> --no-fix` on a `DIRTY` Dependabot PR reports that it would comment `@dependabot rebase` instead of invoking `merge-main`, and shows the Copilot axis as not applicable.

## Out of scope (possible follow-up issues)

- A `publish-report-board` board type for Dependabot triage.
- A multi-repository sweep mode, which would need fork and archived filtering. There are 40 open Dependabot PRs in archived repositories today.
- Qualifying the claim that "Dependabot bumps the SHA and the comment together" in `set-up-linters` (`references/tools/github-actions-ci.md`) and `set-up-installers`. It holds for full `# vX.Y.Z` comments only.
- Auto-merge wiring for minor and patch groups.
