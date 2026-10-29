# Raw snapshots and sparse checkouts

## Approved direction

TOOLING selected option 1, preserving sparse-checkout support under the user's decision to keep current behavior and add raw bytes. The call permits implementation, the four Nit takes and continuation at structural Important 1. The alternatives below are retained as the decision record.

The structural Nit review found a confirmed regression in the new raw collector. A sparse checkout containing `src/a` but intentionally omitting tracked `docs/b` collects successfully on fixed base `7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71`. This branch exits 1 because the raw pass requires `docs/b` to exist. Git lists that entry as skip-worktree. No real checkout configuration was changed; the reproduction uses a local fixture.

The proposed representation currently promises the same inventory for normalized and raw trees. Sparse absence requires qualifying that promise; substituting the indexed blob as raw bytes would obscure whether the file was actually available.

## Options

1. **Recommended: represent actual disk availability.** Keep normalized `tree`, semantic index and `files` compatibility behavior. Read skip-worktree status with the temporary inventory; omit intentionally absent ordinary files and symlinks from `raw_tree`. Preserve gitlink pointer behavior and recursive records. A present skip-worktree file is still hashed from raw disk bytes. A missing ordinary entry without skip-worktree still fails. Materializing or removing a sparse file changes the raw tree, even when its bytes would equal the indexed blob. Document unavailable sparse paths as normalized/index metadata, with no raw-byte claim until present. Extend the existing collector; no new scanner or dependency.
2. **Declare sparse checkouts unsupported.** Fail explicitly before collecting raw inputs and document that restriction. This drops previously working review-scope behavior, so it requires a product decision.

For option 1, add a Scrut case covering sparse absence, present-file edits, materialization, symlink entries and sparse-index mode. Plant unconditional existence checks and omission of present-file raw hashing. Preserve the existing normalized and raw mutation-report union.

The structural loop has used Nit round 1 only. Its next threshold is Important round 1 after this behavior fix.
