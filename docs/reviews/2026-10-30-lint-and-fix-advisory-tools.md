# Advisory lint tools review

## Scope and decisions

Base: `5205fada80635f7d9dd4a1967c94a256e60a99cb` (`origin/main` merge base). Reviewed head: `b3a01977`. Snapshot: `154b49f5695d98a031aec365dcfa265a46254cad`. Canonical implementation plus plan: about 90 changed lines of tooling/docs outside security; generated mirrors excluded from that count. Small-change path applies.

Extend the existing prompt; no executable classifier or new orchestrator. Keep inferred-only tools check-only and non-blocking even when unavailable. Tool filters do not promote enforcement. Preserve CI-only exclusions, project command scopes, allowlists, policy precedence and the No-Write Rule. Patch version: `1.5.0` to `1.5.1`.

## Review rounds

`review-pr-with-codex`, one Nit round: `code` and `comments`, independent read-only `codex exec` runs, `gpt-6.1-sol`, `high`, window `872000`. Both exited 0 with non-empty schema-valid replies, correct snapshot and zero findings. No findings required severity, take/record or re-review decisions. End state: **clean at Nit**. Post-review scope comparison found no lasting changes, scope movement or outside-scope changes. Reviewers could not reach GitHub; repository ownership and issue metadata were checked by the worker.

Errors, tests and types aspects were omitted because no executable error handling, testable code or type definitions changed. Structural review/simplify, trims and Semgrep were replaced by this round under the small-change path. No failed aspect was counted clean. The first helper invocation rejected its in-repository location before starting reviewers; the installed helper then ran both aspects successfully.

## Static acceptance walkthrough

- Shell files without enforcement: shellcheck/shfmt remain inferred only; no fixer or hand remediation; findings and unavailable/unsafe checks stay advisory, with `Unresolved or skipped: none` when required checks pass.
- Tool config, pre-commit hook, CI selection, Makefile/package/project script, agent instruction or executing test: record enforced status and evidence; preserve wrappers, exclusions and allowlists. Merge CI evidence before deduplication.
- Mixed results: required findings, missing tools or unsafe checks fail; advisory findings never mask required failures or block an otherwise successful push/parent continuation.
- `--tool` only filters; `--check` uses non-writing commands and returns the classified parent result. Policy downgrades and protected paths remain constraints on both categories.

These are static instruction checks, not live agent execution tests. No new Scrut document or assertion was added; text matching would not verify the requested agent behavior. Planted defects are not applicable because no executable boundary test was added.

## Validation

- Final `lint-and-fix --no-push`: scoped Markdown fix/format commands changed nothing; all Markdown, Prettier, ShellCheck and shfmt checks passed. Required lint status remains **failure** because `bin/check-fixture-environments --review-paths` rejects existing operands in `tests/fixtures/review-submodule-fixture` at lines 132, 133, 134 and 254. This is the known baseline failure explicitly excluded from the brief, not an advisory tool or a clean lint result. No unrelated fixture was changed. Separately run actionlint passed because the failed prerequisite prevented Make from reaching it.
- Ran `make test-all SCRUT_JOBS=2` once under the atomic TOOLING full-suite lock, owner `532-lint-and-fix-advisory`; exit 2 at the known lint failure. Then ran its unreached targets separately under the same lock: `make validate` passed; `make test-scrut SCRUT_JOBS=2` exited 2. The trap removed the owner file and lock directory after completion.
- Scrut completed every document: 55 passed; only `environment-isolation.md` failed, with 50 of its 51 cases passing. Its failed operand-contract assertion reports the same known fixture errors as lint. No cases were skipped. `run-scrut-documents.md` passed; the macOS issue 697 failure did not reproduce. No full-suite retry was run.
- `make build` passed. `check-versions` passed against the fixed base: all 60 marketplace entries covered, no marketplace-owned versions, manifest and generated version agreement. Fetching `main` before publication left the merge base unchanged.
- The brief authorizes completion through a ready PR and explicitly excludes these baseline failures from remediation. They remain disclosed for TOOLING's merge decision. Copilot was neither requested nor awaited. PR body trim: no-op; no flagged claims or cut material.
