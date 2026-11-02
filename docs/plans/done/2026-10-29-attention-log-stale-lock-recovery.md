# Attention-log stale-lock recovery

Issue: [stale reclaim](https://github.com/cboone/agent-harness-plugins/issues/673).
Base: the exclusive owner-file helper from the merged
[resource-writer fix](https://github.com/cboone/agent-harness-plugins/pull/677).

## Prior art and decision

- [Git lockfiles](https://git-scm.com/docs/api-lockfile) use exclusive creation
  and owner cleanup. Reuse the existing exclusive reservations rather than add
  another locking dependency.
- [BashFAQ locking](https://mywiki.wooledge.org/BashFAQ/045) explains atomic
  acquisition and signal cleanup. Directory acquisition is unsuitable here
  because the base fix established a uutils mkdir failure; keep the owner files.
- [proper-lockfile](https://github.com/moxystudio/node-proper-lockfile/blob/master/lib/lockfile.js)
  checks age before removing a stale lock. That check and removal are separate;
  copying this policy would preserve the successor race.
- Renaming aside is atomic but vacates the acquisition path before validating
  the moved owner. Bash 3.2 provides no conditional unlink or rename by inode.
  A reclaim guard would require every acquisition and release to participate
  and would itself need a recovery policy. Do not extend the shared helper.

Never automatically remove a contended owner file. Report a stopped-PID or aged PID-less session owner and skip its
state update; report aged rotation ownership and append without rotating.
Diagnostics describe an observation, not proof of current ownership, and require
all attention-log writers to stop before manual recovery. Ordinary live session
contention retains bounded retries. Hooks still exit zero and print no stdout.

## Implementation and validation

1. Replace both automatic reclaim paths with diagnostics. Preserve pending
   events before rotation diagnostics, and leave hooks and shared helpers alone.
2. Add committed deterministic Bash fixtures that pause stale observation,
   replace the stale file with a live successor reservation, then resume it.
   Cover session PID and rotation age paths, plus PID-less session ownership.
3. Plant the original read-then-remove paths and confirm the regression checks
   fail. Restore and run the attention-log Scrut document under system Bash.
4. Patch-bump attention-log manifests and regenerate with `make build`.
5. Run the full local review order, baseline Semgrep in a disposable clone,
   version checks and `make test-all`; record coverage, rounds and plants.
6. Tidy into signed logical commits with an exact-tree comparison, push and open
   a ready PR. Report to TOOLING and stop; TOOLING merges.

The overnight go-ahead covers work through the PR. Stop on the specified Codex
host-negotiation failure, a recurring review defect, an unrun baseline scan or
any required change outside scope. The notify concurrent CI flake is report-only.
