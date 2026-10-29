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

`review-git.bash` builds one canonical `membership` list of path records and their bucket labels, including exact initialized-child gitlink transitions and child-local changes. The four top-level bucket arrays are compatibility views of that list, checked for equality by the common validator. The digest, output, prompt, validation, changes, gate and link discovery all read the same list.

`review-scope` reports a `snapshot` digest of HEAD, the resolved base tip and merge base, disk content, semantic index entries (paths, blob identifiers, modes and merge stages), and the four bucket lists. It excludes index stat-cache timestamps. The exact hashed JSON record is stored as an unreferenced Git blob at the snapshot identifier, including canonical membership. Git garbage collection may remove that diagnostic record; recomputation still uses the same content-addressed identifier. The broader file inventory and content trees detect new edits outside the original review membership; they do not grant editing permission for unchanged files. `tree` measures this repository's disk content using a Git tree built in a temporary index. Each initialized submodule has a recursive scope record in `submodules`, with its own HEAD, tree, index, snapshot and buckets. Gitlinks from both the real index and the temporary disk index are collected, so retained checkouts staged for deletion and untracked embedded repositories also receive recursive records. Internal staged, unstaged and untracked paths also enter the parent buckets with their submodule prefix. Git submodule ignore settings do not suppress these inputs. The shared `review-git.bash` module owns canonical membership calculation and supplies explicit call-local config and diff options to both scope collection and prompt rendering, including when no submodule remains.

Reviewers inspect staged and unstaged diffs separately, so index-only edits must invalidate review. Staging, unstaging and intent-to-add move `snapshot` even when `tree` stays unchanged.

## Authorized coverage preparation

A reviewer that reads only the diff needs intent-to-add entries to see untracked files. Prepare them before snapshot capture and retain them through validity checks and consecutive confirming rounds. Restore only this run's entries afterward or on failure/cancellation. Preserve pre-existing entries and concurrently staged content. Report the reviewed snapshot separately from subsequent index restoration.

## What moves it

- Disk content, file modes, additions and deletions.
- Indexed content and bucket membership, including staging and intent-to-add.
- HEAD, the resolved base tip or the merge base.
- Initialized submodule content, semantic index entries, HEAD and bucket membership, recursively.

A change outside the ignore rules invalidates the prior review even if it affects only indexed content. Ignored untracked files, edits reverted between scans and byte changes normalized away by Git remain outside these checks.

An uninitialized submodule with an absent or empty checkout contributes only its indexed gitlink, not unavailable files. Its record has `initialized: false`; initialization changes the snapshot. An uninitialized checkout containing files fails collection rather than silently excluding them. No fetch or initialization runs. A checkout replaced by a regular file is parent file content, not an initialized child. A symlink replacement contributes only its link text, even when its target is a Git repository; no target is traversed. Ignored untracked files inside initialized submodules follow the same exclusion rule as other ignored files.

The required `files` inventory is an array of repository-relative path strings, including symlink paths and pointer-only entries for empty uninitialized gitlinks. Link text is returned separately by `--symlinks`. An untracked retained or embedded checkout expands to these individual paths. No bare directory entry or trailing slash enters a bucket. `--membership <scope.json>` reads canonical records without recapturing state; `--symlinks <scope.json>` describes links from those records using rooted operands and without following targets. The common consumer validator requires every untracked entry to belong to this inventory. Prompts, changes and the gate consume the emitted paths. Aspect validation checks scope consistency and reports membership_paths; finding locations are checked for safe relative syntax, not membership. There is no directory-wide editing allowance.

Committed, staged and unstaged gitlink transitions add their exact changed child-file paths to the matching parent buckets, recursively through captured initialized checkouts. Child objects are compared directly, without substituting a child merge base. Gitlink paths remain pointer metadata. Missing required objects in an initialized checkout fail with Git's diagnostic. Uninitialized checkouts retain their documented pointer-only behavior. A file shown in an inline gitlink diff is editable in that scope; unrelated child files remain outside it.

`tree` remains a Git tree in its own repository; it does not embed child objects. Consumers that compare disk content must compare the recursive submodule trees too. `codex-aspects changes` does this and reports repository-relative internal paths.

## One run reports one state

The file lists and the digest come from different git invocations, and a tree that changes between them would make a single `review-scope` run self-inconsistent. That is worse than it sounds. A file created after the lists were read but before the digest was written would be covered by the snapshot and named in no list, so the reviewer would never be shown it, and step 8 would find the snapshot exactly where it left it. The round would report clean over code nobody read, which is the one result the whole design exists to prevent.

The helper brackets the lists with disk-tree and semantic-index reads and rechecks HEAD and the base tip. It also brackets the recursive submodule records; a changed child scope fails collection. Matching inputs show no lasting change between reads. Changed inputs fail the run rather than emit an inconsistent scope. Rerun once the tree has settled; a formatter on save or another session may be changing it.

## What it costs

The digest is built by copying the repository index to a temporary path and adding the whole working tree to the copy, so it hashes every file git tracks or would track. The caller's real index is never touched, which is what makes the loop safe to run on a partly staged tree. The scrut suite asserts that, because a helper that quietly restaged someone's work would be worse than no helper.

Two details of that are load-bearing, and each has a scrut case standing over it.

- **The copy starts from the index, not from `HEAD`.** Which paths are tracked is a property of the index, not of the commit. A path matched by `.gitignore` and force-added with `git add -f` is tracked and in the scope, and `git add --all` will not re-add it, so seeding from `HEAD` drops it: rewriting that file would not move the snapshot, and a stale clean result would stand over it.
- **The copy's stat cache is not trusted.** `git add` skips hashing a file its cache calls unchanged, and that cache can be wrong: a file staged and then edited back to the same size keeps its recorded stat, so the staged blob goes into the tree in place of the bytes on disk. The snapshot then describes content no reviewer was given. So the add runs twice, `--all` to settle which paths the tree covers and `--all --renormalize` to re-hash every tracked entry whatever its stat says. Neither pass replaces the other: `--renormalize` acts on tracked entries alone, so by itself it leaves every untracked file out of the tree.

Each repository uses two hashing passes for each half of the stability check, against separate temporary indexes. Recursive inventories and exact gitlink transitions add work for initialized submodules. On a very large repository it is the slowest part of a round, and still far cheaper than the review it guards, let alone than a clean result that covered less than it claimed.

## Checking it by hand

Capture `tree` and `snapshot`, stage an existing disk change, then recapture both. `tree` must hold while `snapshot` moves. The same must happen when an indexed blob changes without a disk edit. Unchanged scans must preserve both identifiers. Scrut covers these cases and the authorized intent-to-add lifecycle.

## When there is no base

Without an explicit `--base`, an absent `origin/HEAD` or symbolic target produces a null base. Existing refs with unreadable or non-commit objects, and other Git failures, stop collection with a nonzero status and diagnostic. It never guesses conventional names or substitutes local branches. Ask for `--base` before claiming full coverage. A missing base is reported, along with `committed_covered: false`. That is not an error, and it is not an empty committed bucket either: nothing was measured, so whether the branch has committed work is unknown. The working-tree buckets remain exact and worth reviewing. The round's coverage is partial. Do not read the empty `committed` list as "nothing is committed", and do not report plain `clean` from such a round. When `empty` is also true the working tree is clean, which makes any commits the only unreviewed work and a reason to ask for a `--base` rather than to report nothing to review.

An explicit `--base` always wins, and a ref that does not resolve is an error rather than a silent fallback, because quietly reviewing the wrong range is how a scope gap gets past the first invariant.

A third case sits between those two: a base ref exists but shares no history with HEAD, so there is no merge base and the committed bucket cannot be computed. That is reported, never hidden.

- **An explicit `--base` fails.** The caller named the ref, so the answer is wrong rather than unavailable.
- **An inferred candidate sets `base_unrelated` to true** and leaves `base_ref` in place with a null `base`. The caller is told which ref was tried.

That distinction matters because the two look identical in the output otherwise, and clearing the ref silently would drop a branch's whole commit history from the scope while the run still looked complete, which is the first invariant failing quietly.

**`committed_covered` is the field to read, not the length of the `committed` list.** It is false for both unmeasurable cases, no candidate ref and an unrelated one, and `base_unrelated` says which. The list is empty either way, so the list alone cannot tell "nothing is committed" from "the commits were never reached".
