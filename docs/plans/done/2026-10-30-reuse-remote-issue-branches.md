# Reuse remote issue branches

Fix [issue 415](https://github.com/cboone/agent-harness-plugins/issues/415) on `fix/415-reuse-remote-issue-branch`.
Current `origin/main` at `5205fada` still calls `existing_branch_for_issue` for generated-name launches and fan-out preflight after the naming redesign in PR 443; only local heads are scanned.

## Prior art and design

- A disposable Git probe confirmed that `switch --guess` creates a tracking branch for a unique remote match. Explicit `git branch --track` avoids guessing across remotes and leaves the caller's checkout alone.
- Installed workmux 0.1.277 advertises remote-ref arguments. Upstream `src/workflow/pr.rs` resolves explicit remote refs, rejects `--base` with them, and may fetch missing refs. Bare local names do not take that remote path. Use the existing launcher and Git tracking support rather than add a dependency or remote-resolution tool.
- Read full ref names in local heads and cached `origin` refs, strip namespaces, skip `origin/HEAD`, and deduplicate identical names with local heads first. Distinct matching names remain ambiguous. No fetch is added.
- Before launching a reused remote-only branch, create its local tracking branch explicitly, then pass its local name to workmux. A supplied base cannot replace the reused branch's history. Preflight remains read-only.

## Implementation and validation

1. Extend lookup and tracking setup, update help, and bump workmux patch version. Issue 424's open branch also bumps workmux; mention that coordination in the PR.
2. Cover stub lookup, ambiguity, local preference and tracking failures, plus real disposable repositories with a bare remote, distinct remote history, and tracking assertions. Run touched Scrut documents only, at most two jobs. Plant lookup/tracking defects and verify failure.
3. Run the full local review order, recording rounds and findings in a ledger. Use the small-change path only if the final diff qualifies; this plan assumes the full order.
4. After TOOLING grants the full-suite slot, acquire the documented directory lock with an owner and cleanup trap; run `SCRUT_JOBS=2 make test-all` once before push. Record the known baseline fixture failures separately. Run check-versions, tidy signed commits with identical trees, push, and open a ready PR. TOOLING merges; no live configuration changes.

## Outcome

Implemented cached-origin lookup and tracking for generated and explicit branch choices. Focused tests pass, including native Bash 3.2 and defect plants. The locked full suite completed with 1893 passing cases and one brief-excluded baseline fixture assertion; no cases skipped. Review, trim and coverage details are in `docs/reviews/2026-10-30-remote-issue-branch-reuse.md`. ShellCheck passes under the recorded Semgrep partial-parsing exception.
