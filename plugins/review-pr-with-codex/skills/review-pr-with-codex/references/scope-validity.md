# Review scope validity

Resolve the caller's base, including a symbolic ref, to a commit and then its
merge-base SHA with HEAD at each capture. Compare captured review inputs only.
The identity includes the merge-base SHA, HEAD SHA, normalized and raw disk
trees, semantic index entries, file inventory, canonical bucket-labelled
membership and recursive submodule records. The helper's `snapshot` digest
addresses that record; `codex-aspects changes` also compares membership.

The reported `base_ref` and `base_tip` are informational. Ref names and tip
movement never decide validity. Equal captured inputs preserve the round;
changed captured inputs invalidate it. Re-resolve the selected base on recapture
so a real merge-base change is detected. Do not substitute a comparison of ref
names or remote-ref inventories, and do not maintain exceptions for aliases.

Capture immediately after the reviewer returns. A report-only review with
changed inputs has unreliable findings and cannot authorize edits. An editing
review records an edit round and requires review of the resulting snapshot;
it cannot report clean for the earlier inputs. A HEAD rewrite also fails the
workflow's ancestry check. Observed prohibited pushes, fetches or API writes
fail the workflow independently of scope validity. Ref movement alone does not
identify who changed it and is not proof of such an action.

The snapshot excludes ignored untracked files and index stat-cache timestamps.
Repeated settled captures and spelling the same resolved input with another
ref preserve identity. Staging, unstaging, intent-to-add, raw edits normalized
away by Git, membership changes and recursive submodule changes remain review
inputs. Edits reverted between captures are undetectable. An unchanged result
means no lasting change to captured inputs was found, never that nothing was
written. Content addressing assumes Git object-hash collision resistance.
