# Review until clean: feature/add-wtaf-skill

Base: main (10fe5f677ab6761a7b6bef92cc90f99cf563de46)
Reviewer: codex
Rounds: 16 (3, then 1 more, then resumed until clean)
Status: clean

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

## Round 5

Snapshot: 9c6009af85ee32171805874a067e2efd2c7387e6
Invocation: same as round 1, against head 0885afee; the loop was resumed on request to run until clean
Coverage: full (committed changes; other buckets empty)

- [x] **F7** Important. `plugins/wtaf/skills/wtaf/references/sources.md:47`. The upstream comparison cannot establish whether a branch has been pushed.
      Detail: a branch created with `--track origin/main` has an upstream before any push, so it read as pushed.
      Fixed in 07c26a0e.

## Round 6

Snapshot: 045fcac509249e7c0d6ce20846310a284de90356
Coverage: full

- [x] **F8** Important. `plugins/wtaf/skills/wtaf/references/sources.md:74`. PR discovery can select another repository's branch.
      Detail: filtering on head owner alone accepts a same-named branch from another repository of the same owner.
      Fixed in baa65e85.
- [x] **F9** Important. `plugins/wtaf/skills/wtaf/references/sources.md:82`. Thorough-mode GitHub reads can target the wrong repository.
      Detail: issue-comment and run commands omitted `--repo`.
      Fixed in baa65e85.

## Round 7

Snapshot: 790325351a0a751c891965ac50bebac2bf97d6af
Coverage: full

- [x] **F10** Important. `plugins/wtaf/skills/wtaf/references/sources.md:48`. Push status misclassifies branches published without a configured push destination.
      Detail: `@{push}` depends on push configuration, so a branch pushed with an explicit refspec read as unpushed.
      Fixed in ca34c112.

## Round 8

Snapshot: 2efd12874372732b662f861570de841d948c48c6 (reviewed at head ca34c112)
Coverage: full

- [x] **F11** Important. `plugins/wtaf/skills/wtaf/references/sources.md:79`. PR discovery has no valid lookup for detached HEAD.
      Fixed in 97cdbd36.
- [x] **F12** Important. `plugins/wtaf/skills/wtaf/references/sources.md:79`. PR discovery can miss matches beyond the default result limit of 30.
      Fixed in 97cdbd36.
- [x] **F13** Important. `plugins/wtaf/skills/wtaf/references/sources.md:89`. Thorough mode omits review threads after the first page.
      Fixed in 97cdbd36.

## Round 9

Snapshot: 2efd12874372732b662f861570de841d948c48c6
Coverage: full

- [x] **F14** Important. `plugins/wtaf/skills/wtaf/references/sources.md:67`. Closing issues are resolved in the wrong repository when a reference names another one.
      Fixed in 760049df.

## Round 10

Snapshot: 6ba69e87bdceefbddc4bf9d7701460844773b38f
Coverage: full

- [x] **F15** Important. `plugins/wtaf/skills/wtaf/references/sources.md:38`. Later fetches can replace the PR base in `FETCH_HEAD`.
      Fixed in 1d1394d7.

## Round 11

Snapshot: 267f7fb2b531ff35f59d4760d19dfe0ff73d15d1
Coverage: full

- [x] **F16** Important. `plugins/wtaf/skills/wtaf/references/sources.md:36`. PR discovery uses the fetch repository as the branch's head identity.
      Fixed in a1ad43a6.

## Round 12

Snapshot: 2a04889941b39f830bbf30bf8dfb50db37817188
Coverage: full

- [x] **F17** Important. `plugins/wtaf/skills/wtaf/references/sources.md:48`. A same-named remote branch can produce a false pushed status.
      Fixed in ba918b96.
- [x] **F18** Important. `plugins/wtaf/skills/wtaf/references/sources.md:83`. Detached checkouts at earlier PR commits lose their PR status.
      Fixed in ba918b96.

## Round 13

Snapshot: 427073a269e7dd1acebcbee7967601233fbfea88
Coverage: full

- [x] **F19** Important. `plugins/wtaf/skills/wtaf/references/sources.md:38`. Repository commands require a remote for a local repository.
      Fixed in 2ebfa3d0.
- [x] **F20** Important. `plugins/wtaf/skills/wtaf/references/sources.md:90`. Thorough-mode API commands omit the repository host.
      Fixed in 2ebfa3d0.

## Round 14

Snapshot: 49fd8371227874981b44936a2213872d994a8e41
Coverage: full

- [x] **F21** Important. `plugins/wtaf/skills/wtaf/references/sources.md:36`. PR discovery misses fork PRs when `origin` fetches from the upstream.
      Fixed in 0ed680d1.
- [x] **F22** Important. `plugins/wtaf/skills/wtaf/references/sources.md:36`. Reading the raw origin URL can expose embedded credentials.
      Fixed in 0ed680d1.

## Round 15

Snapshot: af67b123d2c59f60e6a24fec1fd38159fb03e843
Coverage: full

- [x] **F23** Important. `plugins/wtaf/skills/wtaf/references/sources.md:25`. Remote parsing misidentifies SSH ports and host aliases.
      Fixed in 4d5b3881.

## Round 16

Snapshot: 3a4f5a0bae6b95fe4560b3b5ff454943c7ab084e
Coverage: full

No findings. The output was well formed, `reviewed` matched the snapshot, and the snapshot was unchanged when the round was checked.

## Result

No findings at or above Important from codex over snapshot 3a4f5a0bae6b95fe4560b3b5ff454943c7ab084e, covering the full scope (committed changes from main; staged, unstaged and untracked buckets empty). All 23 findings across 16 rounds were fixed; none was declined.
