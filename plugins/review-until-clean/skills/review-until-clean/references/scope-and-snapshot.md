# Scope and snapshot

What the loop reviews, and what binds a clean result to it.

## The four buckets

The scope is everything local that a reviewer could have an opinion about:

| Bucket    | Source                                     |
| --------- | ------------------------------------------ |
| Committed | `<merge-base>..HEAD`                       |
| Staged    | `git diff --cached`                        |
| Unstaged  | `git diff`                                 |
| Untracked | `git ls-files --others --exclude-standard` |

Ignored files are out of scope, because `--exclude-standard` honors `.gitignore` and a reviewer has nothing useful to say about build output.

All four, every round. The failure this prevents is specific and common: the agent fixes a finding, the next round reviews only the fix, the reviewer reports nothing, and the loop declares the branch clean while most of it was read exactly once. Reviewing the whole scope every round costs more and is the only version of the loop whose clean result means anything.

## What the snapshot is

`review-scope` reports a `snapshot`: a digest over HEAD, the resolved base tip and merge base, disk content, semantic index entries (paths, blob identifiers, modes and merge stages), and the four bucket lists. It excludes index stat-cache timestamps. The separate `tree` field is a Git tree built from the working tree in a temporary index, and measures lasting changes to disk content.

Reviewers inspect staged and unstaged diffs separately. An indexed version can change without any disk edit, so a disk-only digest cannot bind the result to everything reviewed. Staging, unstaging and intent-to-add therefore move `snapshot`, even when `tree` stays unchanged.

## Authorized coverage preparation

The Claude backend may need intent-to-add entries to expose untracked files. Prepare them before capturing the review snapshot, retain them through the validity check and consecutive confirming rounds, and restore only this run's entries afterward or on failure/cancellation. Preserve pre-existing entries and leave concurrently staged content alone. Cleanup after the final validity check is an intentional representation change; report the reviewed snapshot and the restoration separately.

## What moves it

- Disk content, file modes, additions and deletions.
- Indexed content and bucket membership, including staging and intent-to-add.
- HEAD, the resolved base tip or the merge base.

A change outside the ignore rules invalidates the prior review even if it affects only indexed content. Ignored untracked files, edits reverted between scans and byte changes normalized away by Git remain outside these checks.

## One run reports one state

The file lists and the digest come from different git invocations, and a tree that changes between them would make a single `review-scope` run self-inconsistent. That is worse than it sounds. A file created after the lists were read but before the digest was written would be covered by the snapshot and named in no list, so the reviewer would never be shown it, and step 8 would find the snapshot exactly where it left it. The round would report clean over code nobody read, which is the one result the whole design exists to prevent.

The helper brackets the lists with disk-tree and semantic-index reads, and rechecks HEAD and the base tip. Equal inputs mean no lasting change was found between those reads. Unequal inputs mean the scope might be inconsistent, and the run fails with `the working tree changed while the scope was being read` rather than emitting a scope it cannot vouch for. Rerun once the tree has settled; a formatter on save or another session in the same worktree is the usual cause.

## What it costs

The digest is built by copying the repository index to a temporary path and adding the whole working tree to the copy, so it hashes every file git tracks or would track. The caller's real index is never touched, which is what makes the loop safe to run on a partly staged tree. The scrut suite asserts that, because a helper that quietly restaged someone's work would be worse than no helper.

Two details of that are load-bearing, and each has a scrut case standing over it.

- **The copy starts from the index, not from `HEAD`.** Which paths are tracked is a property of the index, not of the commit. A path matched by `.gitignore` and force-added with `git add -f` is tracked and in the scope, and `git add --all` will not re-add it, so seeding from `HEAD` drops it: rewriting that file would not move the snapshot, and a stale clean result would stand over it.
- **The copy's stat cache is not trusted.** `git add` skips hashing a file its cache calls unchanged, and that cache can be wrong: a file staged and then edited back to the same size keeps its recorded stat, so the staged blob goes into the tree in place of the bytes on disk. The snapshot then describes content no reviewer was given. So the add runs twice, `--all` to settle which paths the tree covers and `--all --renormalize` to re-hash every tracked entry whatever its stat says. Neither pass replaces the other: `--renormalize` acts on tracked entries alone, so by itself it leaves every untracked file out of the tree.

That is the cost: two hashing passes for each half of the stability check above, against two separate temporary indexes. On this repository, 1,359 tracked files, a run takes about half a second. On a very large repository it is the slowest part of a round, and still far cheaper than the review it guards, let alone than a clean result that covered less than it claimed.

## Checking it by hand

Capture `tree` and `snapshot`, stage an existing disk change, and capture both again. `tree` must hold while `snapshot` moves. Then alter the indexed blob without changing the file on disk: again `tree` must hold and `snapshot` must move. A repeated scan with no change must preserve both identifiers. The scrut suite exercises these cases and the authorized intent-to-add lifecycle.

## When there is no base

A repository with no `origin/HEAD`, no `main` and no `master` reports a null base, along with `committed_covered: false`. That is not an error, and it is not an empty committed bucket either: nothing was measured, so whether the branch has committed work is unknown. The working-tree buckets are still exact and still worth reviewing, and the round's coverage is partial rather than full. Do not read the empty `committed` list as "nothing is committed", and do not report plain `clean` from such a round. When `empty` is also true the working tree is clean, which makes any commits the only unreviewed work and a reason to ask for a `--base` rather than to report nothing to review.

An explicit `--base` always wins, and a ref that does not resolve is an error rather than a silent fallback, because quietly reviewing the wrong range is how a scope gap gets past the first invariant.

A third case sits between those two: a base ref exists but shares no history with HEAD, so there is no merge base and the committed bucket cannot be computed. That is reported, never hidden.

- **An explicit `--base` fails.** The caller named the ref, so the answer is wrong rather than unavailable.
- **An inferred candidate sets `base_unrelated` to true** and leaves `base_ref` in place with a null `base`. The caller is told which ref was tried.

That distinction matters because the two look identical in the output otherwise, and clearing the ref silently would drop a branch's whole commit history from the scope while the run still looked complete, which is the first invariant failing quietly.

**`committed_covered` is the field to read, not the length of the `committed` list.** It is false for both unmeasurable cases, no candidate ref and an unrelated one, and `base_unrelated` says which. The list is empty either way, so the list alone cannot tell "nothing is committed" from "the commits were never reached".
