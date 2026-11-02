# Distinct secret-scanning caller names

Issue: [distinct caller job names](https://github.com/cboone/agent-harness-plugins/issues/432).
Base: `5205fada80635f7d9dd4a1967c94a256e60a99cb`, the merge base with fetched `origin/main`.
Implementation: `71a1cd07`; prose corrections: `8586c17a`.

## Change and scope

The two templates use `gitleaks` and `trufflehog` caller IDs. Each carries a comment explaining check-name prefixes. The skill lists distinct check names and explains required-check migration. Plugin version advances from `3.0.4` to `3.0.5`; generated mirrors come from `make build`. No scanner inputs, permissions, workflow pins or live configuration changed.

Prior art: fosforo's local workflow comments record the duplicate validation rows and use these tool names. Savera's workflows, read through GitHub's contents API, follow the same convention. The pinned reusable workflow was read through that API to confirm inner job names and conditional scanner jobs.

Other template survey: the multi-language CI and lint templates use distinct callers; Go library CI uses minimum/stable callers. Repeated `ci`, `lint` and `release` IDs occur in alternative single-language or release scaffolds, not another pair intended to be installed together. No additional co-installed collision identified; no other plugin changed.

The small-change exception excludes secrets/security configuration, so the full review order applies.

## Review rounds

All review runs used read-only Codex sandboxes, approval policy `never`, web search disabled and stdin closed. Models/settings were explicit. No review run changed repository files. Network metadata lookups inside sandboxes failed; ownership, archive status, PR absence and reusable-workflow content were verified in the parent session.

1. Structural loop: anti-patterns and report-only simplify in parallel, `gpt-6.1-sol`, high effort, 872000-token window. One Nit round, no findings: **clean at Nit**. Anti-pattern JSON passed its result checker. Simplify covered reuse, simplification, efficiency and abstraction altitude inline, without an editing stage.
2. Aspect loop: installed `codex-aspects`, code/tests/comments in parallel, same model/settings. All three exit and schema checks passed. Errors skipped because no error-handling change; types skipped because no type change. One finding, below. **ended: fixes changed no behavior**.
3. Trims: one combined read-only run of both skills, `gpt-6.1-sol`, low effort, 872000-token window. No eligible code comments outside template fences. Text trim proposed replacing “source canaries guard” with “tests check” in the test introduction; taken.

### Finding disposition

- Reviewer's label: `suggestion`, comments aspect, “write-markdown: Factual accuracy: The check-row list omits skipped scanner jobs.”
- Assessed severity: Nit. Both invocation prefixes and required-check migration were correct; only the apparent exhaustiveness of the examples was inaccurate.
- Take or record: taken. Changed “the rows are” to “distinct check names include”, because the pinned workflow also creates skipped rows for the unselected scanner.
- Review again: no. Prose only, no behavior change. No downgrade from an Important/Critical label, recurring defect or design call.

Reviewed snapshot: `53dd3d7ea9d2f9bf2034c87cceeffe06b3c72a97`. The first post-review scope capture was invalidated by starting the intentional prose edit before capture completed; discarded. A settled capture succeeded. Its comparison shows exactly the two intentional prose edits and the generated skill mirror, with no outside-scope changes. This is not an unchanged-snapshot claim. The changed prose was inspected and does not require another round under the project rules.

## Planted defects

The tests were committed before planting. Each template mutation was restored before the next. Logs are retained under `/tmp/432-plant-*.log` and `/tmp/432-judge-*.log` for this run.

| Claim                                     | Instrument                | Plant or control                                   | Observed result                               |
| ----------------------------------------- | ------------------------- | -------------------------------------------------- | --------------------------------------------- |
| Gitleaks keeps its tool-specific caller   | Gitleaks Scrut snapshot   | Restore `scan` in its canonical template           | Only Gitleaks assertion fails; make exits 2   |
| TruffleHog keeps its tool-specific caller | TruffleHog Scrut snapshot | Restore `scan` in its canonical template           | Only TruffleHog assertion fails; make exits 2 |
| Gitleaks expected output is checked       | Gitleaks Scrut snapshot   | Change expected caller to `scan` on correct source | Assertion fails; make exits 2                 |
| TruffleHog expected output is checked     | TruffleHog Scrut snapshot | Change expected caller to `scan` on correct source | Assertion fails; make exits 2                 |
| Restored templates pass                   | Both Scrut snapshots      | Unmodified templates and expectations              | Two succeeded, zero failed or skipped         |

These are source-template assertions, not live GitHub execution tests. They guard the caller IDs emitted by the references. They do not establish remote check delivery or recursively protect their own assertions against arbitrary weakening.

## Validation

- `make build`: passed; generated mirrors committed.
- Scoped Scrut document: two tests passed, including restoration after all plants.
- `check-versions`: fetched default branch `main`; patch bump is forward against the merge base. Coverage and version ownership passed for all 60 marketplace plugins; optional Codex manifests agree. No marketplace version fields.
- Scoped Markdown lint fixes and Prettier: passed, no remaining edits.
- Baseline Semgrep: exit 0 in disposable shared clone `/tmp/432-semgrep-repo`, head `8586c17a`, `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`, `--config auto --baseline-commit 5205fada80635f7d9dd4a1967c94a256e60a99cb`. 128 rules, five scanned targets, zero findings, zero errors, approximately 100% parsed. Five paths excluded by ignore policy, including tests and generated files. Raw result `/tmp/432-semgrep-clone.json`; log `/tmp/432-semgrep-clone-scan.log`. An initial invocation mistakenly retained the original worktree directory; its result was discarded, then the required scan ran in the clone. Worktree remained clean.
- `lint-and-fix --no-push`: scoped autofix commands completed without changes. Markdown/Prettier, ShellCheck and shfmt passed. The fixture operand checker failed on the known main defect below. Actionlint was skipped by the aggregate target after its failed prerequisite, then run separately and passed.
- Full suite: exactly one locked `make -k test-all SCRUT_JOBS=2` run, exit 2. All 57 documents completed: 1883 cases, 1881 succeeded, two failed, zero skipped. The new secret-scanning document passed. The owned lock was released by trap; the next worker acquired it. Full log: `/tmp/432-test-all.log`. The `-k` preserved failures while allowing independent targets to finish.
- Tidy, push and ready PR: authorized under TOOLING's conditional instruction below; final commit/tree and publication identifiers are reported in the mailbox handoff.

## Baseline-failure decision

At 2026-10-30 20:49:31 EDT, TOOLING confirmed proceeding through tidy, push and ready PR with main's known fixture failure recorded in this ledger and the PR body. TOOLING reported that its fix is on a separate branch awaiting approval. This follows the original brief's scope; no fixture changes are authorized here. The worker reported the process stop rather than silently treating failed lint as passing.

## Full-suite failures

- Known main failure: `check-fixture-environments --review-paths` rejects Git operands at `tests/fixtures/review-submodule-fixture:132-134` and move operands at line 254. The same failure causes `environment-isolation.md:39` to fail. No fixture changes were made.
- Additional failure: `workmux-sandbox.md:202`, “Workmux log denial identifies Claude Code and the configured path”, expected exit 0 and received 1. The fixture printed its simulated `PermissionDenied` error, followed by `workmux add` still running after five seconds, no worktree yet, and an uncertain-launch retention notice. Those launcher/test files are untouched. A single targeted rerun was requested by TOOLING and passed all 23 cases, including line 202: `make test-scrut SCRUT_TEST_DIR=tests/scrut/workmux-sandbox.md SCRUT_JOBS=1`, exit 0, log `/tmp/432-workmux-rerun.log`. The initial failure is treated as a load-sensitive timing failure outside this branch, consistent with the passing rerun; no base reproduction was run. Both results remain recorded rather than replacing the failed full-suite result.

At 2026-10-30 21:08:35 EDT, TOOLING requested exactly one targeted workmux rerun and authorized proceeding through tidy, push and ready PR only if it passed. All 23 cases passed, satisfying that condition. The full suite was not repeated. No launcher/test fixes or timing overrides were made.
