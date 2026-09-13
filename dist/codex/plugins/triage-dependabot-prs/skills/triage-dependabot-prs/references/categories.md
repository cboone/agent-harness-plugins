# Categories

Every PR in scope gets exactly one category. Evaluate them in the order below and take the first that matches. The order is deliberate: a PR whose change the default branch already has is Superseded however green its checks are, and a PR the repository has chosen to hold is Hold however stale its branch is.

| Order | Category      | In one line                                                   | Recommended action                                               |
| ----- | ------------- | ------------------------------------------------------------- | ---------------------------------------------------------------- |
| 1     | Superseded    | Something else already delivers this change, or a newer one   | Close, naming the replacement                                    |
| 2     | Outdated      | The thing the PR updates, or the branch it targets, is gone   | Close and delete the branch; fix the config if it would reappear |
| 3     | Hold          | The repository has deliberately deferred this upgrade         | Leave open, or ignore the version on the user's decision         |
| 4     | Needs refresh | The change is wanted, but the PR's state is out of date       | `@dependabot rebase` (or `recreate`), then re-triage             |
| 5     | Needs work    | The change cannot merge as it stands                          | Tracking issue, migration PR, or ignore                          |
| 6     | Needs testing | Current and conflict-free, but the evidence is not yet enough | The specific verification it needs                               |
| 7     | Safe to merge | Current, exercised by CI, conflict-free, and nothing breaking | Merge, in the computed order                                     |

## 1. Superseded

The change is already delivered or replaced. Any one of these matches:

- **The base branch (usually the default branch) is at or beyond every target version.** Read the manifest, lockfile, or workflow at `origin/BASE`. Merging would be a no-op or, worse, a downgrade, and `MERGEABLE` does not rule that out: a lockfile regenerated wholesale on the default branch can still merge cleanly with a stale PR.
- **A newer open PR updates the same dependency, in the same directory, to a higher version, and that PR can land.** It targets the base branch this PR targets, and is not itself Outdated. A replacement that will never merge replaces nothing. The same dependency in a different directory is a separate install tree, not a duplicate.
- **A human PR or commit consolidates the change**, for example one branch that applied several upgrades through the package manager.

Deciding evidence names the replacement: a PR number, or the default-branch commit and the version it holds.

Action: close with a comment naming the replacement, with a "This PR / On `DEFAULT`" version table. See `./actions.md`.

## 2. Outdated

The premise of the PR is gone. Any one of these matches:

- **The manifest, lockfile, or workflow it updates no longer exists** on the default branch.
- **The ecosystem was migrated away**, such as a `pip` PR in a project that moved to `uv`, or an `npm` PR after a switch to `pnpm` workspaces where the old lockfile is gone.
- **The directory is out of scope**: excluded in `dependabot.yml`, vendored, or a subtree whose dependencies another repository manages.
- **The base branch is not the default branch**, and no `target-branch` in `dependabot.yml` names it. A PR against a branch nobody merges to will never land.

Action: close and delete the branch. If `dependabot.yml` would regenerate the PR, say so and hand the fix to the `review-dependabot-config` skill.

## 3. Hold

A deliberate deferral, backed by evidence in the repository. Any one of these matches:

- **A held-major comment** on the pinned reference, such as `# v2.3.4, held at v2 pending v3 migration`.
- **An open tracking issue** for this upgrade.
- **A freeze documented** in the agent config or in `dependabot.yml` comments.
- **An explicit decision by the user** earlier in the session.

A hunch that an upgrade is risky is not a hold. Without evidence, the PR belongs in Needs testing or Needs work.

Action: leave the PR open, or, on the user's decision, use the `@dependabot ignore` command the PR currently advertises. Under a held major, patch and minor updates within the held line are still welcome.

## 4. Needs refresh

The change is wanted, but the PR's state is out of date. Any one of these matches:

- **`mergeStateStatus` is `DIRTY`** (conflicts with the base).
- **The checks ran against an old base.** `compare.behindBy` is above zero and the base branch has changed files that matter to this PR since the merge base, such as its lockfile, its workflow, or the code its dependency is used in.
- **`rebasesDisabled` is true** and the base branch has changed files that matter to this PR, since Dependabot will not refresh the PR on its own.
- **The title, branch, and diff disagree** (`branchAgrees` false, and the diff differs from the title).
- **`compare.nonDependabotCommits` is above zero** and the commits are not ones the user asked for in this session. Dependabot refuses to rebase an edited branch, so the refresh is `recreate`, which needs the user to confirm the edits can go. A commit pushed at the user's request (a corrected version comment, say) is an intended edit: it leaves the PR in the category it had.

A PR that is only `BEHIND` on unrelated files, with checks that still exercise the change, is not stale. It can still be Safe to merge.

Action: `@dependabot rebase`, or `@dependabot recreate` for an edited branch after confirmation, then re-triage once Dependabot has pushed and the checks have concluded.

## 5. Needs work

The change cannot merge as it stands. Any one of these matches:

- **A check failure the change caused.** Read the log before concluding this. Failures from secrets a Dependabot run cannot read, or from a flaky job that also fails on the default branch, are not caused by the change: see Needs testing.
- **A documented breaking change that requires code edits**, such as a removed API the repository calls, or a config format the repository uses and the new version rejects.
- **A peer or engine conflict**, such as a new major that requires a newer runtime than the repository pins, or a peer range the repository's other dependencies cannot satisfy.
- **An install failure** with the frozen lockfile.

Action: a tracking issue through the `create-issue` skill (one issue per outstanding upgrade), a separate migration PR, or, on the user's decision, an ignore command. The triage does not write the migration.

## 6. Needs testing

The PR is current and conflict-free, and nothing known breaks, but the evidence is not yet enough to call it safe. Any one of these matches:

- **A major update**, or `semverBreaking` true in an ecosystem whose ranges treat it as breaking (npm and Cargo carets do not cross a 0.x minor).
- **A runtime dependency whose behavior CI does not exercise**, such as a web server, a database driver, or a proxy-header parser.
- **A grouped PR containing any major.** Grouping does not dilute the risk of its riskiest member.
- **Vacuous CI.** The checks pass without touching the change: the changed files are ignored by the tool, the workflow pins its own tool version in `env:` and ignores the manifest, or the repository has no CI.
- **Uninformative CI.** The checks fail only because a Dependabot run cannot read a secret: `Input required and not supplied: token`, a cloud credential that comes back empty, an OIDC exchange that is refused.
- **Consumers carry the risk.** The repository publishes actions or reusable workflows, and a new major changes behavior downstream.
- **An action's `runs.using` runtime changes**, such as `node20` to `node24`, which self-hosted runners must support.
- **The release notes are truncated** in the body and have not yet been read at the source.

Action: name the specific verification it needs, from `./verification.md` or the evidence checklist. A PR that passes moves to Safe to merge; a PR that fails moves to Needs work.

## 7. Safe to merge

Every one of these holds:

- **Current against the base branch**, or behind it only on files unrelated to this PR.
- **The checks pass and exercise the change**, or verification has.
- **No conflict with the base branch.** A conflict with another open PR does not disqualify it; it only sets the merge order, and the later PR is expected to need a rebase.
- **The release notes show no breaking change that affects this repository.** A major can qualify, for example when the only break is a runtime bump the repository's runners already support.
- **For a GitHub Action pinned to a commit SHA**, the SHA resolves to the tagged commit, and the version comments beside it name the new version. An action pinned to a tag (`@v7`) has no SHA to check.

Action: merge with a method the repository and its rules allow, in the computed order.

## Flags

Flags are recorded beside the category, never instead of it. They set priority within a category and appear in the report:

- **security**: `kind` is `security`, or `alerts` is non-empty. Record the highest severity.
- **group** or **multi**: the PR updates several dependencies together.
- **major**: any update is a major, or is `semverBreaking`.
- **stale checks**: the newest check completed before the base branch last changed relevant files.
- **secret-starved CI**: failures trace to secrets a Dependabot run cannot read.
- **version comment drift**: a SHA-pinned action whose comment still names the old version. Dependabot updates a full `# vX.Y.Z` comment, but a major-only comment such as `# v6` can be left behind.

Within each category, sort security PRs first, by severity, then majors, then the rest by age.

## Grouped and multi-dependency PRs

A grouped or multi-dependency PR takes the category of its riskiest member. When one member holds back an otherwise safe group, a group PR advertises per-dependency ignore commands, such as `@dependabot ignore <dependency name> major version`. That command closes the group PR and stops Dependabot proposing that dependency's major version, so the next group update arrives without it. Closing the PR is the user's decision, so it belongs in the action offer rather than in the classification.
