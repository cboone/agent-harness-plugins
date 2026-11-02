# Monitor PR client mode

Implement the Nov 1 six-answer policy in both monitor-pr entry points, using the
existing intake and dispatcher. TOOLING owns the merge; this worker builds,
reviews, pushes and opens a ready PR under the supplied brief.

## Sources and prior art

The design report at
`~/.local/state/conductor/codex-answers/2026-11-01-monitor-pr-copilot/report.md`,
lines 185-199, recommends shared intake, durable private dispositions and policy
revalidation on every entry. Its earlier pause and separate-approval proposals
are superseded by the brief's client answers.

[GitHub's code-review documentation](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-code-review)
exposes reply and resolve separately and warns that reviews may repeat findings.
Keep those operations separate from disposition identity. The installed
`resolve-copilot-pr-feedback` skill requires public summaries and closes no-fix
categories; reuse the bundled monitor-pr intake instead of adopting that policy.
The existing watch-policy restrictions already govern reads, dispatch and helper
entry, so extend them rather than adding another workflow or watcher.

## Implementation

1. Share repository selection, intake coverage, round ledger, conductor decisions
   and factual fixed-only publication rules between both skills. Automatically
   select clients by `swing-left` identity; independently pause `cboone` Copilot.
1. Extend prepared policy for client restrictions and per-round authority. Preserve
   stricter pauses, no-fix, lifecycle rules and unknown-evidence handling.
1. Test policy selection, resume, intake and mutation gates with committed gh
   stubs that verify PATH. Plant defects in the new boundaries.
1. Bump monitor-pr minor, rebuild mirrors and update documentation.

## Validation and handoff

Run affected Scrut documents plus error-output-guard and environment-isolation,
at most two concurrently. Follow the full local review order, signed logical
commits and exact-tree tidy. Run the full suite once with SCRUT_JOBS=2 only after
TOOLING grants the shared lock. Check versions, push, open ready and send TOOLING
the review précis. No merge or live client PR operations belong to this work.
