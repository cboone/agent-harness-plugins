# Installed checklist drift gate

Extend rule 20 of `bin/validate-plugins`, as TOOLING selected for issue
[cboone/agent-harness-plugins#499](https://github.com/cboone/agent-harness-plugins/issues/499).
The existing bundled-checklist generator supplies expected source bytes.
The installer names `.github/skills/code-review/<guide>.md` by guide, so use
that filename mapping. Exclude the entry `SKILL.md`, compare after the managed
first line and blank line, and ignore pin content. Name stale and orphaned
files and direct repair through `/set-up-review-config`. An absent directory
passes. Keep build outputs unchanged.

Installed checklist bodies match their source bytes; no
refresh or mirror rebuild is needed. Add fixture cases for a current copy,
absent directory, source rule rename after rebuilding bundled copies, orphan,
and stale pin with a current body. Plant removal of the body comparison.

The complete diff includes committed plant fixtures and exceeds the brief's
approximate small-change limit. Use the full local review order on frozen SHAs,
then `lint-and-fix --no-push`, signed logical tidy, version checks and the
heavy-locked full suite.
Keep receipts and helper snapshots outside the checkout in the workstream's
evidence directory. Open a ready PR; TOOLING owns the merge.
