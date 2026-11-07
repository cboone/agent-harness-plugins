# Finish supervision fixes with main's verdict reader

TOOLING native000035 relays the “Split it out” decision, q-3317daad, on gate
6f62aceb. Restore verdict reading exactly to origin/main and move its redesign
to the structured-result follow-up, cboone/agent-harness-plugins#739. Version
stays 1.3.0. Another timing or deadline defect requires a stop.

## Implementation

- Remove framework-line and final-summary reading, their tests, plants and
  product docs. Prove matches and expectation are identical to main. Keep the
  nine captured compatibility verdicts and assertion-message hygiene.
- Keep independent inclusive per-call limits, active allocation/parent reads,
  one guarded launch point, static nested/document fit checks and git_timeout.
  Keep serial checked-runner documents and conservative process containment.
- Keep restart assertion diagnostics free of nested runner output. Test and
  plant that boundary so main's whole-output reader cannot collide there.
- Regenerate mirrors and commit each logical change without rewriting history.

## Review and handoff

Continue structural counts at round 5 against fixed merge-base
302c0d91a77097f1ae66e39bd996253e4bbb17d8. Use the sanctioned aspect runner and
worktree-based manual anti-pattern invocation with stdin closed. Then trims,
baseline Semgrep and lint. Merge current origin/main if needed with a signed
merge commit, then signed exact-tree tidy. Run all final plants from the start,
the heavy-lock default-parallel restart suite on that head and survivor checks.
All check-pass posts use checked gates. The head must include current main;
TOOLING retains the merge hold. Finish at the ready PR, mentioning the follow-up.
