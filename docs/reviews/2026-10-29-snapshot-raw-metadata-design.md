# Raw filesystem metadata recurrence

## Confirmed recurrence

Structural Important 1 found a second sparse metadata instance after Nit 1 fixed absent sparse paths. With `core.symlinks=true`, capture an already-dirty sparse-excluded symlink `docs/link -> changed-target`. Replace it with a regular file containing those exact bytes. The source collector succeeds twice with identical snapshot, normalized tree, raw tree, semantic index and membership. The raw tree still records mode `120000` although the disk path is regular. A local-only signed fixture confirms this; no real configuration changed.

The class is retaining normalized-index metadata as if it described present raw disk state. Another local conditional for the symlink case would leave regular-to-symlink and executable-mode boundaries to be rediscovered separately.

## Approved direction

TOOLING selected option 1: raw trees record actual disk type and regular-file executable bits, never retained index modes. Pseudo-links under core.symlinks=false are regular raw files, and raw executable bits ignore core.filemode. Normalized tree/index/files remain compatible. Continue at structural Important 2 after tests and plants.

## Structural options

1. **Recommended: one raw filesystem-state capture.** Use the existing temporary-index/Git machinery to obtain current type and executable mode for every present raw path, independently of stale sparse index modes. Let the normalized index supply inventory and intentionally absent skip-worktree status, while preserving normalized tree/index/files compatibility. Hash current regular bytes or current link text according to that disk kind. Keep the regular link-text exception explicitly tied to `core.symlinks=false`, and state how `core.filemode` affects executable modes. Preserve gitlink and recursive behavior. This extends the current collector without adding a scanner or runtime dependency; validate the temporary-index metadata-refresh mechanism before choosing its commands.
2. **Conservative refusal.** Fail collection when a present sparse path's type or mode cannot be measured consistently, rather than reuse a normalized mode as raw metadata. Document the resulting supported-input restriction.

Test both same-byte type transitions, executable-mode changes, full and sparse indexes, materialization, the link-text exception and caller-index preservation. Plant stale indexed type/mode reuse against those tests.

The recurrence gate is resolved by that call. Used rounds: structural Nit 1 and Important 1; the next round after an approved behavior fix is Important 2.
