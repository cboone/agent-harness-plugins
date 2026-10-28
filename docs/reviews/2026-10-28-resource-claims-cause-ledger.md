# Resource claims cause ledger

## Authority and scope

- Issue: [Concurrent resource claims lose an update](https://github.com/cboone/agent-harness-plugins/issues/656).
- Go-ahead: Chris, Inbox, 2026-10-28 at 7:38 PM ET, thread "Tooling next batch, Oct 28 evening": build through a ready PR. TOOLING merges.
- Branch: `fix/656-resource-claims-cause`, based on main at `a2e56c53`.
- Full local review order required; no review rounds started.
- Nighttime checkpoint: approximately 9:45 PM ET.

## Initial evidence

Ownership verified: origin is `cboone/agent-harness-plugins`, neither archived nor a fork. Read issue body and all six comments. `corepack yarn install --immutable` passed.

The source never breaks stale locks, exits on its bounded wait timeout, reads only after acquiring the lock, and creates its temporary file beside the destination. No source cause is established yet. Existing Docker images checked locally lack jq; no software installed.

The original parallel case now validates both resource names in the final JSON before declaring success. On any missing claim or writer failure it prints each writer's status and retained output, and the final file contents. Affected Scrut document: 100 succeeded, 0 failed, 0 skipped on macOS.

The brief explicitly permits a temporary Linux CI debug job. A temporary branch-push workflow runs 1,000 pairs across ten isolated jobs against the unchanged production writer, retains Bash traces on loss, and sets TMPDIR to `/dev/shm` while claims live on the runner's normal temporary filesystem. Remove this workflow before the PR. This diagnostic push precedes local review under that explicit exception; subsequent history stays intact.

## Linux reproduction

[Baseline run](https://github.com/cboone/agent-harness-plugins/actions/runs/40789830676), diagnostic commit `757a4310`: 368 lost claims in 1,000 pairs (36.8%), zero writer errors in 2,000 writers. Per-shard losses: 46, 14, 8, 44, 30, 18, 45, 43, 54, 66. Every shard completed normally and reported losses.

The retained trace for shard 5, pair 0, shows both writers successfully executing plain `mkdir` on the identical lock path, immediately installing the EXIT trap and reading an absent claim file. Neither enters the retry body. Both serialize a single resource and return 0; final JSON holds only `logic`. This narrows the next experiment to direct competing mkdir calls, with utility versions recorded. It does not yet establish which utility behavior causes both apparent acquisitions.

## Confirmed cause and design gate

[Primitive run](https://github.com/cboone/agent-harness-plugins/actions/runs/40790111891), commit `064b86c1`, shard 1: Bash 5.3.9, `mkdir (uutils coreutils) 0.10.0`, `mv (GNU coreutils) 9.7`. Directly racing plain mkdir on one path gave 98 double-success results in 1,000 pairs. Resource-writer stress in that shard lost 48/100 claims with zero writer errors. An existing local Linux image with GNU mkdir 8.32 gave zero double-success results in 1,000 direct pairs.

The [uutils 0.10.0 source](https://github.com/uutils/coreutils/blob/0.10.0/src/uu/mkdir/src/mkdir.rs) confirms the failure: `create_single_dir` handles `Err(_) if path.is_dir()` as success without checking `config.recursive`. If both commands pass the earlier existence check, one creates the directory and the other gets a creation error, sees that directory and returns success. The current upstream source adds the missing recursive guard. No third-party issue or other write was made.

The primitive is unsafe on this runner, so the existing correct placement of read/modify/write inside the directory lock cannot serialize writers. Stale-lock removal and lock timeout do not cause this reproduction. TMPDIR is on a separate filesystem, but the source still creates its temporary file beside the destination; GNU mv is not needed to reproduce the primitive failure.

Stop: design decision required before changing the lock protocol. Proposed direction for TOOLING: retain the bounded wait and directory/owner diagnostics, but require exclusive Bash noclobber creation of the owner file before entering the critical section. Cleanup must remove only the owner's file and use rmdir, rather than recursive removal that could remove a succeeding owner. This needs a deterministic stub that reports mkdir success to both writers, including acquisition/release interleavings, and a plant restoring the old protocol. No production edit, regression implementation, review round, Semgrep, full suite, version bump or PR exists yet.

The branch has two diagnostic commits already pushed. Preserve their history; tidy must not rewrite them. The temporary workflow remains available for the post-fix Linux run and must be deleted before the PR. Next steps after a relayed design decision: implement the selected protocol, deterministic regression and plants; obtain an after-fix Linux loss rate; remove the workflow; run the full review order and required checks; open a ready PR and report to TOOLING. TOOLING merges.

## Local artifacts and processes

Created artifacts: `/tmp/656-resource-claims-ci-watch.log`, `/tmp/656-resource-claims-linux-job.log`, `/tmp/656-resource-claims-linux-baseline.log`, `/tmp/656-resource-claims-primitive-watch.log`, `/tmp/656-resource-claims-linux-primitive.log`. CI watch sessions `97541` and `85923` observe the two diagnostic runs; the first completed with exit 1 as expected. Test session `48479` and push sessions `15839`, `89019` completed. No local child processes stopped. No software installed or real user config changed.
