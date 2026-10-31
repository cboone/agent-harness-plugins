# Copilot thread resolution reasons

Implement issue [463](https://github.com/cboone/agent-harness-plugins/issues/463) in `monitor-pr`.

## Evidence and prior art

Read-only GitHub GraphQL introspection on 2026-10-30 confirmed `resolveReviewThread(input: ResolveReviewThreadInput!)` accepts optional `resolutionReason: PullRequestReviewThreadResolutionReason`. Its values are `ADDRESSED`, `WONT_FIX`, and `INVALID`. Mutation enumeration found no newer resolution mutation. No PR or thread was written during investigation.

- [GitHub's pr-address-feedback skill](https://awesome-copilot.github.com/skill/pr-address-feedback/) uses `resolveReviewThread` without a reason in its CLI fallback. Retain the existing helper and extend that mutation.
- [gh-pr-reviews](https://github.com/k1LoW/gh-pr-reviews) classifies and reports resolution evidence; it does not provide the required reason-writing workflow. No new dependency is needed.
- The existing bundled helper and committed reply fixture already cover reply ordering and failures. Extend those paths and their stubs.

## Implementation

1. Add optional `--reason ADDRESSED|WONT_FIX|INVALID` to `resolve` and `reply-and-resolve`, validating before a reply. Preserve callers that omit it.
1. Require the skill to pass a reason for every resolution, including recovery: fixed and outdated concerns are Addressed; valid declined/deferred concerns and unchanged nitpicks are Won't fix; factually incorrect concerns are Incorrect, with an explanatory reply. Pending decisions remain open. Record reasons in output dispositions, excluding review bodies that have no thread.
1. Document mapping in the README, bump `monitor-pr` for the new capability, and regenerate mirrors. Record the schema result on the issue.

## Validation and handoff

Use committed `gh` stubs with executable-resolution guards for reason payloads, both commands, omitted reasons, rejected options, reply failures and resolution failures. Plant defects in the reason boundary checks. Run only touched Scrut documents during iteration, with at most two jobs.

Use the full local review order: structural anti-patterns plus report-only simplify, focused aspects, trims, baseline Semgrep, lint, exact-tree signed tidy. The small-change exception does not apply to this helper input-validation change. Run `make test-all` once after TOOLING grants the full-suite lock, recording the known baseline fixture failure separately. Check versions, push, open a ready PR, and report to TOOLING. TOOLING merges; no live configuration changes or live thread tests.
