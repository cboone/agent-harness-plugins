# Review until clean: feature/add-wtaf-skill

Base: main (10fe5f677ab6761a7b6bef92cc90f99cf563de46)
Reviewer: codex
Rounds: 4 (3, then 1 more on request)
Status: stopped

## Round 1

Snapshot: 63f92ce7ccb3c2b07e03b32ca1d8bc4c4a882699
Invocation: `codex exec --sandbox read-only --ephemeral --output-schema <tmp>/schema.json -o <tmp>/findings.json "<review prompt>" < /dev/null` (codex-cli 0.159.3)
Coverage: full (committed changes; staged, unstaged and untracked buckets empty)

- [x] **F1** Important. `plugins/wtaf/skills/wtaf/references/sources.md:25`. Branch comparisons use the repository default instead of the PR base.
      Detail: for a feature branch whose PR targets a release branch while the repository default is main, ahead and behind counts, the commit list, the diff summary and plan compliance include unrelated release-branch changes. Use the PR's `baseRefName` when a PR exists.
      Evidence: `sources.md` selects the base with `gh repo view ... defaultBranchRef` and compares against `origin/$base`; the PR read already requests `baseRefName` but it is never used for the comparison.

Round 1 outcome: F1 fixed in e753ee7b.

## Round 2

Snapshot: 23100857a723392b68479ef56b53bf00e475123e
Invocation: same as round 1, against head e753ee7b
Coverage: full (committed changes; other buckets empty)

- [x] **F2** Important. `plugins/wtaf/skills/wtaf/references/sources.md:29`. The fallback base ref produces invalid Git comparisons.
      Detail: `git rev-parse --abbrev-ref origin/HEAD` returns `origin/main`, which the comparison commands prefix with `origin/` again.
      Evidence: `git rev-list --left-right --count origin/origin/main...HEAD` exited 128 with an unknown-revision error.
- [x] **F3** Important. `plugins/wtaf/skills/wtaf/SKILL.md:46`. Fork PR status is queried from the wrong repository.
      Detail: a fork branch whose PR targets the upstream repository reports no PR when every `gh` read is directed at the fork.
      Evidence: the skill requires an explicit fork `--repo` for every `gh` command while the PR lookup is `gh pr view`; PRs belong to their base repository.

Round 2 outcome: F2 and F3 fixed in 6122106f.

## Round 3

Snapshot: 3fb4c167d387202f04ba7f4830a4a9d241464bfe
Invocation: same as round 1, against head 6122106f
Coverage: full (committed changes; other buckets empty)

- [x] **F4** Important. `plugins/wtaf/skills/wtaf/references/sources.md:73`. Branch-name PR lookup can select an earlier merged PR.
      Detail: when a fork has an older merged PR for a reused branch name and the current PR targets the parent, the fork lookup succeeds with the old PR and the parent lookup is skipped.
      Evidence: the fork lookup used `gh pr view "$branch" --repo FORK_OWNER/REPO` before checking the parent; create-deferred-issues documents the same hazard.

Round 3 outcome: F4 fixed in c4739b0d. The round limit was reached, so no round reviewed that fix.

## Round 4

Snapshot: 5fda481b9651801a0a7a451678a4c9ebce42575f
Invocation: same as round 1, against head e7d2701b, run as one further round on request
Coverage: full (committed changes; other buckets empty)

- [x] **F5** Important. `plugins/wtaf/skills/wtaf/references/sources.md:73`. PR discovery misses upstream repositories without GitHub parent metadata.
      Detail: a repository that began as a fork but has `isFork: false` has no `parent`, so a PR in its `upstream` remote is never found.
      Evidence: the second PR repository was discovered only through `gh repo view ... --json parent`.
- [x] **F6** Important. `plugins/wtaf/skills/wtaf/references/sources.md:38`. Branch comparisons fail for parent-targeted PRs when the parent has no local remote.
      Detail: a fork with only `origin` can have a PR targeting its parent, but `$base_ref` requires a local remote naming the parent.
      Evidence: every branch comparison used `$base_ref`, built only from a local remote.

Round 4 outcome: F5 and F6 fixed in 57bd44dd. No further round reviewed that fix.

## Result

Stopped after round 4. All six findings (F1 to F6) were fixed and none was declined. The last snapshot reviewed was 5fda481b9651801a0a7a451678a4c9ebce42575f, covering the full scope; the F5 and F6 fix in 57bd44dd has not been reviewed.
