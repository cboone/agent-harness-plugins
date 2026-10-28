# Monitor background watch

Implementation and local verification are complete. Publication and CI outcomes
are recorded in the workstream handoff.

Approved scope: monitor-pr background watch, issue 637. Extend `merge-flow`
rather than add a second poller. Preserve milestone 2 policy preparation,
lifecycle dispatch and Codex scheduler/foreground fallbacks.

1. Add `watch-changes` using the existing watch loop, backoff and bounds.
   Compare frozen snapshot/review metadata, ignore running/UNKNOWN transitions,
   and preserve finite quiet-tick decisions as a bounded poll count.
2. Update the skill, checkpoint and README; retain task IDs and fresh-policy
   entry after completion. Bump monitor-pr to 3.4.0 and rebuild mirrors.
3. Add committed stub-only Scrut cases and plant each guarded boundary.
4. Complete the full local review order, baseline Semgrep, lint, test-all,
   version check and signed tidy. Push and open a ready PR; TOOLING merges.

No live configuration, software installation or merge is authorized here.
