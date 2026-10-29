# Sandbox exclusion assumptions

## Authority and outcome

TOOLING worker `512-sandbox-exclusions`; base `main`. The go-ahead in Inbox,
2026-10-28 at 7:38 PM ET, permits building through a ready PR. TOOLING merges.
Close [the workmux sandbox failure](https://github.com/cboone/agent-harness-plugins/issues/512)
and [catalog exemption assumptions](https://github.com/cboone/agent-harness-plugins/issues/472)
together, including both issues' 2026-10-28 parity amendments.

## Approach

1. Confirm each harness's matching and resource behavior through isolated live
   probes or open questions to a fresh session. Record versions, commands,
   results and limitations in the review ledger. Do not change real settings,
   install software or grant permissions.
2. Extend the existing `workmux` helpers and tests. Preserve authorized launches
   under both harnesses without excluding a shell. Report denied resources and
   the calling harness, retaining the original failure and launch status.
   Keep Bash 3.2 compatibility and existing timeout/delivery semantics.
3. Sweep canonical skills, references and scripts for exemption assumptions.
   Correct each active occurrence or record why it remains. Regenerate mirrors
   with `make build`; patch-bump every changed plugin.
4. Commit a launch/resource matrix with guarded stubs for workmux, tmux and gh.
   Cover both harness launch paths for all three helpers. Document live-only
   checks separately and plant every diagnostic regression.
5. Run the full local review order: structural/simplify, focused Codex reviews,
   trims, baseline Semgrep in a disposable shared clone, and lint without push.
   Run `make test-all`, `check-versions`, and exact-tree signed-commit tidy.
   Push, open a ready PR closing both issues, observe green checks and report
   the review précis to TOOLING. Never merge.

## Stops

Follow the process stops for recurring findings, unavailable Semgrep baseline,
unresolved lint or missing tools, closed gates and scope questions. Stop before
any real settings change. At about 9:40 PM ET on 2026-10-28, commit the current
work, record its resume point and report to TOOLING for nighttime parking.
