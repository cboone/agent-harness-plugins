# Uncited review findings ledger

## Scope and authority

Issue 500, branch `fix/500-review-config-uncited-findings`, merge base
`7a6997e7414d590b61f14ee8b9e9fc06cb7f5f71`. Authorized through a ready PR by
Chris's October 28 tooling overnight batch at 9:16 PM ET. TOOLING merges.
Full local review order applies. Hooks and user configuration are out of scope.

## Validation

- Prompt-contract Scrut document: 3 passed, 0 failed, 0 skipped.
- Removal plants: independently removed citation fallback, shared severity/cap,
  and deduplication wording from each of three templates and three installed
  blocks. All 18 runs failed as expected; original bytes restored each time.
- Tests assert the written contract, not model compliance.
- Scoped Markdown lint and formatting passed. Generated mirrors rebuilt.
- Locked dependencies restored with network and scripts disabled.

## Review rounds

Local review completed after the October 30 restart. Structural and focused
loops each ended clean at Nit. Trims, baseline Semgrep, final lint, full tests
and version checks passed. Tidy and publication receipts follow by mailbox.

## Stop: code-mode negotiation failure

Both first-round runs failed before reading review material, with
`timed out negotiating with the code-mode host` in their logs. Anti-patterns
reported the error at 5:43:36 PM ET on October 29; simplify at 5:43:39 PM ET.
Each used `codex exec`, `gpt-6.1-sol`, high effort, context window 872000,
read-only sandbox, approval policy `never`, web search disabled, stdin closed.
No retry or fallback was attempted, as the brief explicitly requires stopping.
No review result is clean; no completed round or finding is claimed.

Both owned processes (31140 and 31141) were stopped with TERM after the errors;
both commands exited 143. Captures remain outside the worktree at
`/tmp/review-500.ZrMAVn/`, including prompts and logs, with no valid final replies.
Implementation commit: `f77cc8b8` (signed). The worktree was unchanged by review.

Not run: focused Codex review, trims, Semgrep, final lint-and-fix,
`make test-all`, version audit, tidy, push or PR creation. Plugin version is
bumped from 1.0.3 to 1.0.4, but final version checks remain outstanding.

Resume requires TOOLING's restart/go-ahead once the code-mode host works, then
start the local review order at step 1. Contract tests and removal plants were
completed before the stop. No claim that all local checks pass is made.

## Restart

TOOLING relayed the ramp go-ahead on October 30 at 3:10:45 PM ET, authorizing
restart at full review step 1 through a ready PR. The original timeout stop
condition still applies. Issue 500's in-progress label restored. Repository
verified unarchived, owned by cboone and not a fork; worktree clean at restart.

## Completed local reviews

Reviewed HEAD `8bce6903` against the fixed merge base above. Step 1's Nit round
ran anti-patterns and report-only simplify in parallel through read-only
`codex exec`, model `gpt-6.1-sol`, high effort, window 872000. Both exited 0 with
nonempty complete replies. Anti-patterns JSON passed its schema check: success,
complete, zero findings, no unread files. Five generated mirror files excluded.
Simplify covered all four cleanup angles inline and found no proposals.
Step 1: clean at Nit. No behavior fixes, so no next round.

Step 2's Nit round used installed `codex-aspects` 2.3.1, historical instructions
and `CLAUDE.md` fallback guidance. Code, tests and comments ran in parallel at
the same model/effort/window, in read-only sandboxes. All exited 0 and passed
schema and snapshot checks with zero findings. Errors and types did not apply.
The before/after normalized tree was
`121275a0c94caffabbef3324d3896048ba81d1b6`; scope unchanged, no lasting changes
found. Step 2: clean at Nit. Parent verified GitHub metadata; runtime checks
remain separate from static reviews.

Step 3 ran trim-comments and trim-text in one read-only Codex round, model
`gpt-6.1-sol`, low effort, window 872000. Exit 0, complete nonempty report.
No eligible code comments. One active-voice rewrite taken in the skill overview:
"Combine repeats of one defect, listing their affected paths." Meaning preserved;
no behavior changed, no additional review round required.

There were no correctness findings requiring four-call dispositions, no
severity downgrades, design changes, or deferred findings. Review artifacts:
`/tmp/review-500-resume.sjZUUv/` (prompts, replies, logs, schemas and snapshots).

## Baseline Semgrep

Disposable shared clone: `/tmp/review-500-resume.sjZUUv/semgrep-repo`,
HEAD `1bd6ccc4`. Ran `semgrep scan --config auto --baseline-commit` with the
fixed merge base and `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`.
Exit 0, 128 rules, 10 targets, 0 findings, approximately 100% parsed lines.
Six files excluded by Semgrep ignore patterns. JSON errors empty; no shell
parsing exception needed. Baseline-aware scan, no full-scan substitute.
Raw JSON and log: `semgrep.json` and `semgrep.log` in the review capture folder.

## Final lint mode

`lint-and-fix --no-push`: repository-documented Markdown/Prettier aggregate
fixers reach protected `tests/scrut/` documents, which project rules forbid
reformatting. Those fixers are downgraded to check mode under the skill's
protected-path rule. Verification uses `make lint`: Markdownlint, Prettier,
ShellCheck, shfmt diff and actionlint. No other tool configurations detected.
Scoped Markdown fixes and formatting already passed on the edited prose.
The full `make test-all` is still required before tidy and publication.

## Final verification

`make lint` passed, with no fixes needed. `lint-and-fix --no-push` result:
success, no lint commit beyond the process record; no unresolved or skipped
checks. Markdown/Prettier used check mode by protected-path policy; ShellCheck,
shfmt diff and actionlint are check-only tools. The subsequent `make test-all`
exited 0: lint, JSON, fixtures, plugin manifests, catalog and cross-references
passed, followed by all 53 Scrut documents. Total: 1,826 testcases passed,
0 failed, 0 skipped. The known notify rollout flake did not occur locally.

`check-versions` passed against freshly fetched `origin/main`; merge base
unchanged. Only changed plugin: `set-up-review-config`, 1.0.3 to 1.0.4,
a forward patch bump. All 60 catalog entries have valid manifest-only version
ownership and matching Codex manifests where present. Repository instruction
chain maximum: 10,597 bytes (root plus bin), below 32 KiB.

The trim proposal's four calls: reviewer label "one proposed rewrite";
our severity Nit (active voice only); take the local rewrite; no review again
because wording and meaning stayed the same.

| Planted defect, each of six surfaces | Expected instrument     | Actual result       | Regression coverage                        |
| ------------------------------------ | ----------------------- | ------------------- | ------------------------------------------ |
| Remove uncited citation fallback     | Citation contract block | All six runs failed | First block in review-config-reporting.md  |
| Remove uncited shared cap            | Severity contract block | All six runs failed | Second block in review-config-reporting.md |
| Remove cross-file deduplication      | Repeat contract block   | All six runs failed | Third block in review-config-reporting.md  |

All 18 plants restored original bytes before validation. Generated mirrors
were rebuilt after the trim; validation passed on that content.

Tidy and publication receipts, including final commit hashes, exact-tree
comparison and PR URL, go in the TOOLING mailbox handoff after execution.
The review capture directory is disposable and will be removed after handoff;
the findings, completion checks and measured outcomes are recorded here.
TOOLING owns merging. No user-scope config or hooks changed.
