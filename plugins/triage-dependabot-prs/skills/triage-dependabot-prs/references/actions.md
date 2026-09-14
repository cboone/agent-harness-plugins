# Actions

How to carry out the dispositions the user selected. Everything here is a write to a shared repository, so each one happens only after the user chose it, and each one starts by re-checking the PR:

```bash
gh pr view N --repo OWNER/REPO --json state,headRefOid,baseRefName,mergeable,mergeStateStatus,statusCheckRollup,reviewDecision
```

If the PR closed, merged, or changed head since the triage, re-triage it before acting.

## Merge

1. **Pick the method.** Use one the repository allows (`mergeCommitAllowed`, `squashMergeAllowed`, `rebaseMergeAllowed`) and the rules allow (`allowed_merge_methods` in the `pull_request` rule from `gh api repos/OWNER/REPO/rules/branches/BASE`, where `BASE` is the PR's `baseRefName`, since a PR aimed at a configured `target-branch` answers to that branch's rules). When several remain, follow the repository's agent config, then `viewerDefaultMergeMethod`.
1. **Merge one PR at a time, in the computed order:**

   ```bash
   gh pr merge N --repo OWNER/REPO --squash --match-head-commit HEAD_SHA
   ```

   Use `--merge` or `--rebase` in place of `--squash` as step 1 decided. `HEAD_SHA` is the `headRefOid` from the re-check just before, so the merge is refused if Dependabot or anyone else pushed in between. Add `--delete-branch` only when `deleteBranchOnMerge` is false.

1. **After each merge, re-query the remaining PRs** in the set. Request a rebase only for those that turned `DIRTY`, or that a rule requires to be up to date (`BEHIND`). `mergeable` reads `UNKNOWN` for a short while after a merge; wait and re-query rather than acting on it.

Never:

- pass `--admin`, or use any bypass a ruleset offers
- enable auto-merge (`--auto`) unless the user asked for it
- merge a `BLOCKED` PR by any route: report the unmet rule (usually a required review) instead

## Rebase and recreate

```bash
gh pr comment N --repo OWNER/REPO --body "@dependabot rebase"
```

- **`@dependabot rebase`** asks Dependabot to rebase the branch onto its base and push. It works on PRs whose automatic rebases were disabled after 30 days. Dependabot refuses when someone else has pushed to the branch.
- **`@dependabot recreate`** rebuilds the PR from scratch, discarding any commits on the branch that Dependabot did not make. Ask the user before posting it whenever `compare.nonDependabotCommits` is above zero.

Post one comment per PR, then wait for Dependabot:

- Poll `gh pr view N --repo OWNER/REPO --json headRefOid,mergeStateStatus,statusCheckRollup` until the head SHA changes and the checks conclude. Prefer `ScheduleWakeup` between polls, falling back to a blocking `sleep` where it is unavailable.
- Read Dependabot's replies on the PR for a refusal or a closure: `gh api --paginate --slurp repos/OWNER/REPO/issues/N/comments | jq '[.[][] | select(.user.login == "dependabot[bot]") | {created_at, body}] | last'`.
- When Dependabot closes the PR as no longer needed or superseded, it names what replaced it. Triage the replacement.

Then return to step 3 of the skill for the refreshed PRs.

## Close

Keep the comment body out of the command line, so it survives quoting intact:

1. Run `mktemp -u` and note the path it prints. Call it `BODY_PATH`.
1. Write the comment body to `BODY_PATH` with the Write tool.
1. Re-check the PR as the top of this page describes, immediately before the next command, and stop if its state or head changed.
1. Post the comment and close the PR in one command, with the literal path, chained so the close only happens once the comment is posted. The two writes stay chained rather than split around a second re-check: a change landing between them would leave an explanation of a close that never happened, and the chain keeps that window to two consecutive API calls.

   ```bash
   gh pr comment N --repo OWNER/REPO --body-file BODY_PATH && gh pr close N --repo OWNER/REPO --delete-branch
   ```

1. Remove the file: `rm -f BODY_PATH`.

A PR closed without its explanation leaves the next reader guessing, so if the comment fails, stop and report rather than closing anyway.

Closing a single-dependency PR manually makes Dependabot stop proposing that exact version. Closing a group PR does not ignore anything. Neither is a substitute for an ignore command when the user wants future updates suppressed.

### Superseded

```markdown
Superseded by #M, which updates `NAME` to X.Y.Z.

| Dependency | This PR | On `main` |
| ---------- | ------- | --------- |
| `NAME`     | 4.1.2   | 4.1.3     |

Merging this PR now would downgrade `NAME`.
```

When the replacement is the default branch itself, name the commit or PR that landed the newer version instead of `#M`.

### Outdated

```markdown
Closing: `web/package.json` no longer exists on `main`. The web app moved to `apps/web` in #M, and Dependabot covers that directory separately.
```

State what disappeared and where its replacement lives. If the config would regenerate the PR, add that the config is being reviewed.

### Replaced by a consolidated upgrade

```markdown
Closing: #M upgraded these dependencies together with the package manager, including `NAME` to X.Y.Z.
```

## Ignore

Ignore commands close the PR and stop Dependabot proposing the version or dependency, so each one is the user's decision. Post only a command the PR currently advertises. The list has changed over time, and `merge`, `squash and merge`, `cancel merge`, `reopen`, and `close` are no longer offered.

A single-dependency PR advertises:

- `@dependabot ignore this major version`
- `@dependabot ignore this minor version`
- `@dependabot ignore this dependency`
- `@dependabot show <dependency name> ignore conditions`

A group PR advertises per-dependency forms instead:

- `@dependabot ignore <dependency name> major version`
- `@dependabot ignore <dependency name> minor version`
- `@dependabot ignore <dependency name>`
- `@dependabot unignore <dependency name>`
- `@dependabot unignore <dependency name> <ignore condition>`

When the body lost its commands footer (`commandsFooter` false), this PR no longer shows what Dependabot accepts. Take the wording from the footer of another open Dependabot PR of the same `shape` in this repository, and with none to copy from, post no ignore command: offer the `ignore` rule below instead. When the user wants the suppression to be visible in the repository, an `ignore` rule in `dependabot.yml` is the durable alternative: hand that to the `review-dependabot-config` skill.

## Consolidate

When several PRs fight over one lockfile, or the security fixes are transitive-only and Dependabot cannot express them as one PR, offer a single branch that applies the upgrades through the package manager (`npm audit fix`, `yarn up NAME`, `pnpm update NAME`, `uv lock --upgrade-package NAME`, `go get NAME@VERSION`). The `upgrade-everything` skill covers the broader version of that pass. After the consolidated PR merges, close the Dependabot PRs it replaced with the consolidated comment above.

## Tracking issues

For each Needs work or Hold PR the user wants tracked, invoke the `create-issue` skill with one issue per outstanding upgrade: the dependency, current and target versions, the deciding evidence, the breaking changes found, and a link to the PR.

## Approve

Only when the user explicitly asks for approval. Write the body to a `mktemp -u` path as in [Close](#close), then:

```bash
gh pr review N --repo OWNER/REPO --approve --body-file BODY_PATH
```

The body states what was verified, in one or two sentences. Approval posts under the user's identity, so a request to merge is not a request to approve.

## Pushing to a Dependabot branch

Only when the user asks for it, for example to fix a stale version comment on a PR about to merge:

1. Request `@dependabot rebase` first, and wait for it, so the push lands on a current branch.
1. Push the fix as a new, signed commit.
1. Tell the user that Dependabot will no longer rebase this branch, and that `@dependabot recreate` would discard the fix.
1. Record the pushed commit in the triage notes. On a later pass, `compare.nonDependabotCommits` counts it, and an approved commit is an intended edit, not a reason to recreate.

A separate follow-up PR avoids these costs, and is the better offer when the fix is not urgent.
