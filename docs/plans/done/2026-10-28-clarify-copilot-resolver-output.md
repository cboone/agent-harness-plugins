# Clearer Copilot resolver output

Port the design from `feature/596-clarify-copilot-feedback-output` onto the moved
`monitor-pr:resolve-copilot-feedback` skill, closing
[cboone/agent-harness-plugins#596](https://github.com/cboone/agent-harness-plugins/issues/596)
and [the consistency and sibling fixes](https://github.com/cboone/agent-harness-plugins/issues/613).
The old branch and worktree remain unchanged.

## Design

- Lead summaries with a verdict, review count and reviewed head. Group linked
  findings by outcome; collapse the full findings table and bookkeeping.
- Recognize both the first-line hidden marker and the legacy heading. Preserve
  review identities, read-review ids, pending work and no-op idempotency.
- Reply before resolving every completed thread. Link pushed commits and files;
  reuse a prior decision only after checking its disposition and remote links.
- Preserve the current review, consistency, sibling-chain and late-round controls.
  Keep the exact `Deferred to follow-up` heading for the caller's batch workflow.
- Check consistency-sweep reads explicitly; a failed diff or PR-body read records
  a workflow failure and blocks push. Pending siblings remain unresolved.
- Bump monitor-pr to 3.2.0 and regenerate mirrors.

## Verification and finish

Commit scrut coverage and stubs, then plant each guarded defect and restore it.
Run structural anti-pattern and report-only simplify reviews in parallel, the
focused Codex review loop, and one read-only trim pass. Review settings are
`gpt-6.1-sol`, `high`, window `872000`, explicitly set on each run. Trims use the
skills' `low` effort with the same model and window.
Run the baseline semgrep scan in a disposable clone, then lint-and-fix without
push, full `make test-all` and repository check-versions. Tidy into logical signed
commits while preserving the exact tree. Push and open a ready PR, observe green
checks, report the review précis to TOOLING and stop. TOOLING merges.

The go-ahead is the brief's Inbox authorization from 2026-10-27 at 8:54 PM ET.
Stop at recurrence, a blocked baseline, missing tool, lint failure, closed gate
or scope question. The ledger records review counts and outstanding work.
