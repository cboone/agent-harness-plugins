# Aspect group anchor

Close [issue 716](https://github.com/cboone/agent-harness-plugins/issues/716)
on `fix/716-aspects-group-anchor`, based on `origin/main` at
`2a694d7048750199ce8d292043156a6046299fd6`.

Extend the existing child-side Perl wrapper and ownership-checking signal helper.
The wrapper forks an idle anchor after setpgid, preserving the exec leader PID.
A private locked file proves anchor continuity independently of recycled PIDs.
Only helper cleanup ends a locked anchor, including after failed setup. The
anchor ignores TERM until bounded escalation or immediate group KILL when it is
the only known active member. Cleanup never signals an unanchored leaderless group;
remaining members without continuity evidence produce incomplete cancellation.
No job control or parent-side group setup is added. Preserve Bash 3.2 support.

Update invocation guidance and bump review-pr-with-codex from 2.3.3 to 2.3.4.
Regenerate mirrors. Extend the committed ps/kill fixture to cover anchored
identity, normal release and recycled leaderless groups. Add an actual-wrapper
lifecycle check, and plant the old leaderless signalling path in a disposable
clone to verify sensitivity.

Run only affected Scrut documents plus error-output-guard and
environment-isolation during iteration, at most two concurrently. Hold tests on
a thermal warning. Run the full local review order, recording findings and
plants in a ledger. Before the single full suite, wait for competing suites,
take the designated directory lock, and run `SCRUT_JOBS=2 make test-all`.
Finish with version checks, signed logical commits, an identical-tree tidy,
push and a ready PR; report to TOOLING, which merges.
