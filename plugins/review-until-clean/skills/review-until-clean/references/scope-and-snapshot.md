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

`review-scope` reports a `snapshot`: a digest over the head commit, the resolved base, and a git tree object built from the entire working tree in a temporary index. The tree object is git's own content address, so the snapshot is a function of file content and nothing else.

## Why it is content-addressed

The obvious implementations are wrong in the same way. A digest of `git status` output, or of `git diff HEAD`, changes when a file moves between buckets even though not one byte of it changed:

- `git add <path>` moves a path from unstaged to staged.
- `git add -N <path>` moves a path from untracked to tracked, which is how an untracked file becomes visible to a reviewer that only reads the diff.
- `git reset -- <path>` moves it back.

Every one of those is something this loop does, or asks the user to do, in the ordinary course of a round. A snapshot that moved for any of them would throw away clean results that are still perfectly good, and would do it most often on exactly the runs that had to stage an untracked file to get full coverage. Building the digest from a tree object sidesteps all of it: identical content yields an identical tree, whatever the index says.

The same property covers deletions, symlinks, the executable bit, and file names holding newlines, none of which a path-parsing implementation handles without effort.

## What moves it, and what does not

| Action                                      | Snapshot |
| ------------------------------------------- | -------- |
| `git add`, `git add -N`, `git reset` a path | Holds    |
| Editing one byte of a file in scope         | Moves    |
| Creating or deleting a file in scope        | Moves    |
| Committing the working tree                 | Moves    |
| Changing the base ref                       | Moves    |
| Another session editing the tree            | Moves    |

The last row is the reason step 8 recomputes the snapshot instead of trusting the value from step 1. A worktree is not private, and a clean result is a claim about the code on disk now.

## What it costs

The digest is built by reading `HEAD` into a temporary index and adding the whole working tree, so it stats every file git tracks or would track. The caller's real index is never touched, which is what makes the loop safe to run on a partly staged tree. The scrut suite asserts that, because a helper that quietly restaged someone's work would be worse than no helper.

On a very large repository the stat pass is the slowest part of a round. It is still far cheaper than the review it guards.

## Checking it by hand

The invariant worth re-checking after any change to the helper:

```bash
printf 'new\n' > fresh.txt
review-scope --base main | jq -r '.snapshot'
git add -N fresh.txt
review-scope --base main | jq -r '.snapshot'   # the same value
printf 'x' >> fresh.txt
review-scope --base main | jq -r '.snapshot'   # a different value
```

If the second value differs from the first, the snapshot is tracking representation rather than content and the loop will discard good clean results. If the third matches the second, it is not tracking content at all and the loop will report clean for code that changed, which is the worse of the two.

## When there is no base

A repository with no `origin/HEAD`, no `main` and no `master` reports a null base. That is not an error: the committed bucket is then empty and the scope is the working tree alone. An explicit `--base` always wins, and a ref that does not resolve is an error rather than a silent fallback, because quietly reviewing the wrong range is how a scope gap gets past the first invariant.

A third case sits between those two: a base ref exists but shares no history with HEAD, so there is no merge base and the committed bucket cannot be computed. That is reported, never hidden.

- **An explicit `--base` fails.** The caller named the ref, so the answer is wrong rather than unavailable.
- **An inferred candidate sets `base_unrelated` to true** and leaves `base_ref` in place with a null `base`. The committed bucket is empty because it could not be computed, not because there is nothing in it, and the caller is told which ref was tried.

That distinction matters because the two look identical in the output otherwise. Clearing the ref silently would drop a branch's whole commit history from the scope while the run still looked complete, which is the first invariant failing quietly. `empty` being true alongside `base_unrelated` means the working tree is clean and the commits are simply unreachable from the base, so it is a reason to ask for a better `--base`, not a reason to report nothing to review.
