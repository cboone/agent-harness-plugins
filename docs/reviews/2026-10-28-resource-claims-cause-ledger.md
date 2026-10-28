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
