# Evidence

The checks that decide a PR's category. The summary from `dependabot-prs fetch` answers part of each one; the commands below answer the rest. `OWNER/REPO` and `N` stand for the repository and the PR number. `DEFAULT` stands for the branch the PR targets: the default branch for nearly every Dependabot PR, or the configured `target-branch` for one aimed elsewhere. The PR heads were fetched into `refs/dependabot-triage/N` at the start of step 3.

Every PR gets sections 1 to 4. Sections 5 to 8 apply to the PRs listed in step 3 of the skill.

## 1. Freshness

The question: do the PR's checks and mergeability describe its base branch as it is now?

- **`compare.behindBy`** counts the base-branch commits the PR head lacks. Zero means current.
- **When it is above zero, look at what changed** since the merge base, and whether any of it matters to this PR:

  ```bash
  git diff --name-only "$(git merge-base origin/DEFAULT refs/dependabot-triage/N)" origin/DEFAULT
  ```

  A changed lockfile, manifest, or workflow that this PR also touches, or code that uses the updated dependency, makes the checks stale.

- **`checks.newestCompletedAt`** against the default branch's latest commit date (`git log -1 --format=%cI origin/DEFAULT`) is a first signal. The file comparison above is the deciding one.
- **`mergeStateStatus`**: `DIRTY` conflicts, `BEHIND` lacks commits a rule requires, `BLOCKED` fails a rule (usually a required review), `UNSTABLE` has failing non-required checks, `CLEAN` is mergeable. `UNKNOWN` is not computed yet: re-query.
- **Did Dependabot rebase recently?** The timeline records it:

  ```bash
  gh api --paginate --slurp repos/OWNER/REPO/issues/N/timeline |
    jq '[.[][] | select(.event == "head_ref_force_pushed")] | last | {actor: .actor.login, created_at}'
  ```

- **Commits that do not belong to the PR.** When a push landed on the default branch while Dependabot was preparing the PR, the PR can show that push's commits and files. The compare API's `nonDependabotCommits` is the reliable count; `gh pr view --json commits,files` is not. A `@dependabot rebase` clears the artifact.

## 2. Target versus default branch

The question: does the default branch already have this change, or something newer?

Read the version the default branch holds for every update, and compare it with `to`:

| Ecosystem        | Where to read it on `origin/DEFAULT`                                                                              |
| ---------------- | ----------------------------------------------------------------------------------------------------------------- |
| `github_actions` | `git grep -n "uses: NAME@" origin/DEFAULT -- .github/ '*action.yml' '*action.yaml'`, and the `# vX.Y.Z` comment   |
| `npm_and_yarn`   | `package.json` for the declared range, and the lockfile for the resolved version (`yarn why NAME`, `npm ls NAME`) |
| `go_modules`     | `go.mod` (`git show origin/DEFAULT:go.mod`)                                                                       |
| `uv`, `pip`      | `uv.lock`, or `requirements*.txt` and `pyproject.toml`                                                            |
| `cargo`          | `Cargo.lock`                                                                                                      |
| `bundler`        | `Gemfile.lock`                                                                                                    |
| `docker`         | The `FROM` line in the Dockerfile the PR touches                                                                  |

Run the lockfile commands in a worktree on `origin/DEFAULT` (see `./verification.md`), not in the user's working tree.

If the default branch is at or beyond `to` for every update, the PR is Superseded. If it is beyond `to` for some updates and behind for others, the PR is Needs refresh, because a rebase regenerates it against the current versions.

## 3. Overlap

The question: which PRs must land in a particular order, and which will conflict?

- **`overlaps`** lists every open PR, any author, that shares a file with this one.
- **Predict conflicts** with the base branch and between overlapping PRs. Step 3 of the skill runs these before anything else:

  ```bash
  git fetch origin "pull/N/head:refs/dependabot-triage/N"
  git merge-tree --write-tree origin/DEFAULT refs/dependabot-triage/N
  git merge-tree --write-tree refs/dependabot-triage/N refs/dependabot-triage/M
  ```

  Exit status 1 means a conflict. Two PRs touching one lockfile usually conflict. Two action bumps on different lines of one workflow usually do not, but each merge still makes the other PR behind.

- **The same dependency in two PRs** is a duplicate only when the directory matches too. Branch names insert the directory when it is not the root (`dependabot/npm_and_yarn/web/NAME-VERSION`), and the files show it.
- **A human PR in `overlaps`** may need to land first, or may already contain the upgrade. Read its title and diff.

## 4. Does CI exercise the change?

The question: would these checks fail if the update broke something?

- **Failing checks: read the log before judging.**

  ```bash
  gh pr checks N --repo OWNER/REPO --json name,state,link,workflow
  gh run view RUN_ID --repo OWNER/REPO --log-failed
  ```

  The run id is the path segment after `/runs/` in the check's `link`, not the trailing job id. `gh pr checks` exits non-zero for pending checks as well as failing ones, so classify from the JSON.

- **Secret starvation.** A workflow that Dependabot triggers through `push`, `pull_request`, `pull_request_review`, or `pull_request_review_comment` runs like a fork PR: a read-only `GITHUB_TOKEN`, and only Dependabot secrets, not Actions secrets. (`pull_request_target` runs are not restricted this way.) These failures say nothing about the update:
  - `Input required and not supplied: token`
  - a cloud or deploy credential that is empty or rejected
  - an OIDC or workload identity exchange that is refused
  - a checkout of a private repository or submodule that fails authentication

  Confirm by checking whether the same job passes on the default branch. Mark the PR's CI as uninformative, and pass the finding to the `review-dependabot-config` skill.

- **Vacuous passes.** The checks run but cannot see the change:
  - the changed files are excluded by the tool's ignore file (`.prettierignore`, `.markdownlintignore`, `.eslintignore`)
  - the workflow installs its own pinned tool version in `env:` or an action input, so bumping the manifest changes nothing CI runs
  - the workflow's `paths:` filter skipped the job for this PR
  - the only checks are lint jobs, and the update is a runtime dependency

- **No checks at all.** `checks.total` is 0 and the repository has no workflows for pull requests. Nothing has been verified.

## 5. Change content

The question: what does the update actually change, and does any of it reach this repository?

- **Read the release notes and changelog for every version skipped**, not just the target. When the body is truncated (`bodyTruncated`, or `updates` shorter than `updatesExpected`), read them at the source:

  ```bash
  gh api repos/UPSTREAM_OWNER/UPSTREAM_REPO/releases/tags/vX.Y.Z --jq .body
  gh api --paginate 'repos/UPSTREAM_OWNER/UPSTREAM_REPO/compare/vA...vB?per_page=100' --jq '.commits[].commit.message | split("\n")[0]'
  ```

- **Look for**: removed or renamed APIs, changed defaults, dropped runtime or platform support, new peer requirements, changed config formats, security fixes, and migration guides.
- **Find the consumers.** For each breaking change, grep the repository for the affected API or option. A breaking change the repository never touches does not block the PR.
- **Direct versus transitive.** A security PR titled for a transitive package can raise a direct dependency to get there. The diff of the manifest, not the title, says which packages moved.
- **Dependency scope.** A `deps-dev` prefix or a `devDependencies` entry does not prove development-only use; check where the package is imported.

## 6. GitHub Actions

Applies when `ecosystem` is `github_actions`.

- **The SHA matches the tag.** Resolve the tag and compare with the SHA in the diff. Annotated tags need a second hop:

  ```bash
  gh api repos/ACTION_OWNER/ACTION_REPO/git/ref/tags/vX.Y.Z --jq '.object | {sha, type}'
  gh api repos/ACTION_OWNER/ACTION_REPO/git/tags/TAG_OBJECT_SHA --jq .object.sha
  ```

  Or `gh api repos/ACTION_OWNER/ACTION_REPO/commits/vX.Y.Z --jq .sha`, which dereferences for you.

- **The version comment moved with the SHA.** Dependabot rewrites a full `# vX.Y.Z` comment, but a major-only comment such as `# v6` can survive a bump to v7. Check every occurrence in the diff. A stale comment is version comment drift: flag it, and mention it in the action offer, because fixing it means a push to the branch or a follow-up PR.
- **The runtime.** Read `runs.using` at the new SHA:

  ```bash
  gh api 'repos/ACTION_OWNER/ACTION_REPO/contents/action.yml?ref=NEW_SHA' --jq .content | base64 --decode | grep -A 2 '^runs:'
  ```

  A change such as `node20` to `node24` matters for self-hosted runners.

- **Trigger restrictions.** A new major can change behavior under `pull_request_target`, `workflow_run`, or fork PRs. Check whether the repository uses those triggers with this action.
- **Branch-pinned actions.** A SHA-to-SHA update with `type: digest` has no semver and no compatibility score. Read the commits between the two SHAs.
- **Reusable workflows and published actions.** When the repository publishes actions or reusable workflows, the update changes what consumers run. Note which inputs, outputs, or permissions change.

## 7. Security

Applies when `kind` is `security` or `alerts` is non-empty.

- **Which advisories the PR clears**: `alerts[]` with severity, patched version, and `cleared`. Only a `cleared: true` alert counts as fixed by this PR. `cleared: null` means the versions could not be compared (a digest, a pre-release, no patched version, different targets in different directories, or a body cut short), so compare them by hand. `directoryConfirmed: false` means a group across directories does not say the package updates in the alert's directory: read the diff for that directory's lockfile before counting the alert as addressed at all.
- **Whether the PR introduces a new vulnerable package.** A bump can pull in a new transitive dependency with its own advisory. After merging, the wrap-up re-fetch catches it; before merging, a local audit in a worktree can (`npm audit`, `yarn npm audit`, `pip-audit`, `govulncheck ./...`, `cargo audit`).
- **`unclearedAlerts`** are advisories no open PR is known to clear. An entry whose `prs` is non-empty has a PR that updates the package without reaching the patched version, or without the evidence to say so: compare by hand. An entry with empty `prs` has no PR at all. The usual cause is a transitive dependency its parent pins exactly, leaving no version Dependabot can move to. Report them. Fixing them is an override or an upstream upgrade, outside this triage.

## 8. Supply chain (optional depth)

Worth the extra calls for a new major of a widely used package, a maintainer change, or a package with a recent incident:

- **Commit verification** on the release commit: `gh api repos/UPSTREAM_OWNER/UPSTREAM_REPO/commits/SHA --jq .commit.verification`.
- **npm provenance**: `npm view NAME@VERSION dist.attestations --json`.
- **Publisher change**: `npm view NAME@VERSION _npmUser maintainers --json` against the previous version.
