# Python plant bytecode review

Small-change path: bounded tooling guidance and a standalone regression, under about 100 changed lines including records and generated mirrors. No helper or live configuration changes. Merge base: `5205fada80635f7d9dd4a1967c94a256e60a99cb`, verified against the captured scope and `origin/main`.

## Codex round 1, Nit

`review-pr-with-codex` ran code, tests and comments through installed `codex-aspects`: `gpt-6.1-sol`, high effort, 872000 context, read-only sandbox, approval never, web search disabled, external working directory and prompts. Each exited zero with nonempty schema-valid JSON for snapshot `507fec21cd50887375130d6e4a30c4c6b41bda9c`. No lasting changes found; scope unchanged. Errors omitted because error handling did not change; types omitted because no types changed; simplify and structural scans replaced by the small-change path.

| Reviewer's label                                                                        | Our severity                                                                                                                          | Take or record                                                            | Review again                                     |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------ |
| tests: `suggestion`, “The prefix case does not verify restoration with a fresh prefix.” | Nit: the existing test bypassed the contaminated prefix after restoring, leaving the fresh-prefix guidance without a direct assertion | Take: add stale reused-prefix control and restored fresh-prefix assertion | No: tests only; ended: fixes changed no behavior |

Code and comments had no findings. No Important/Critical findings, downgrades or design changes. Full structural, trim and Semgrep rounds are not required on this path.

## Verification

The manual regression passed: `uv run --no-project tests/fixtures/plant-defects-bytecode.py`. The repository does not declare a Python runtime in its Scrut setup. Judge plants removing cleanup, allowing plant writes and reusing the plant prefix all failed by the intended assertion. An earlier proposed plant merely relocated the isolated prefix; it stayed green because it preserved isolation and was discarded as invalid.

`make build`, `make validate`, and `check-versions` passed: only `plant-defects` changed, 1.0.4 to 1.0.5; marketplace coverage and manifest version ownership match. `make test-all` ran without quiet flags and stopped at the known base fixture lint failure. Final `lint-and-fix --no-push` ran broad Markdown fixers in check mode because Scrut snapshots are protected: Markdown, Prettier, ShellCheck, shfmt and separately run actionlint passed; the fixture validity check still fails on `tests/fixtures/review-submodule-fixture`. No lint fixes or lint commit were needed. Lint status: failure (known base failure), not a clean result; the brief explicitly keeps that failure outside scope.

Full `make test-scrut` finished: 55 of 56 documents passed. `environment-isolation.md` had 50 successful cases and one failed assertion, “Review fixture manifest satisfies its operand contract”, with the same six known diagnostics from `review-submodule-fixture` at lines 132, 133, 134 and 254. Both files are unchanged from the merge base. No additional failures or skipped cases were reported.

Tidy retains a local pre-tidy backup and rebuilds logical signed commits from the verified merge base; the handoff records the exact-tree comparison. TOOLING merges; no Copilot review requested and no live configuration changed.

## Main synchronization, 2026-11-02

TOOLING relayed the tl27 drain go-ahead and limited tests to owned/conflicted documents plus the error-output and environment-isolation documents, at most two concurrently. The remote branch already contained main `7817cab667d625bce777ad808a327d8e72f1b502` through merge `81e375f967a1ee5e1bf7d173570bc3af39120900`, whose signature GitHub verified. The local checkout fast-forwarded to that branch; merging `origin/main` then reported already up to date. No conflicts, history rewrite or additional merge commit were needed; the branch has no changed Scrut documents relative to main.

The new checker initially rejected the Python regression as non-Bash source without a named exclusion. Added that exact filename to `bin/lib/error-output-policy.json`, with the reason that it is Python, keeps subprocess stderr live and propagates unsuccessful exits. No diagnostics rule changed. The initial environment-isolation run failed on that missing entry; both requested documents were rerun after the fix.

Final checks passed: `check-fixture-environments`, its `--review-paths` mode, the manual Python regression, error-output guard (102 cases) and environment isolation (51 cases), with zero failures or skipped cases. `check-versions` confirmed main's 1.0.4 to branch's 1.0.5 remains forward, generated manifest agrees, and marketplace coverage/version ownership match. No additional bump was needed. No full suite or other merge-changed documents were run for this synchronization, per the go-ahead and thermal limit. Original review round counts and end state remain unchanged.
