# Embedded Bash routing review

Changed detection and installation instructions so embedded Bash receives the Bash checklist in Copilot, Codex and Claude review guidance. No installed live review configuration changed.

## Local review

- Small-change path: 28 authored plugin lines plus the plan, all prompt/configuration changes outside security. Structural, simplify, trimming and semgrep steps are replaced by the one focused round under the project's small-change rule.
- One Nit round through installed `review-pr-with-codex`, standalone `codex exec`, parallel `code` and `comments` aspects; `gpt-6.1-sol`, `high`, 872000-token window, read-only sandbox, approval never, web search disabled, stdin closed. External startup and historical repository guidance isolate checkout instructions; global policy and user configuration remain active.
- Both processes exited zero and produced nonempty, schema-valid JSON for snapshot `300df84b853324af0d89f92af753be80e6451ecc`. Both findings arrays were empty. Reviewer label, our severity, take/record and re-review: none. End state: **clean at Nit**.
- Before/after normalized tree `d42f0d2419f08fbf0a4027f2431b67e39a042d4e`; scope unchanged, no lasting changes found. Reviewed head `5e20bf55`, merge base `5205fada80635f7d9dd4a1967c94a256e60a99cb`.
- Errors and types aspects omitted because no executable error handling or type definitions changed; tests aspect omitted because these are instructions without an executable installer. No new boundary tests or plants. String snapshots would measure wording delivery, not model adherence.

## Validation

- `make build`: passed; generated Codex mirror committed. `make validate`: passed, including manifests, catalog coverage, versions and cross-references.
- Targeted `SCRUT_JOBS=2 make test-scrut SCRUT_TEST_DIR=tests/scrut/build-review-checklists.md`: 27/27 passed.
- `lint-and-fix --no-push`: scoped Markdown fix/format made no changes; Markdown lint, Prettier, ShellCheck and shfmt passed. `make lint` failed only on the brief's known `review-submodule-fixture` operand failures (lines 132 to 134 and 254). Standalone `actionlint` passed because make stopped before invoking it. No lint commit needed.
- `check-versions`: default branch `main`; only `set-up-review-config` changed, patch 1.0.3 to 1.0.5, generated manifest matches; no new or removed plugins, catalog registration unchanged. PR 692 has 1.0.4; TOOLING confirmed it remains open and owns integration and any later re-bump.
- Instruction inspection: workflow-only implicit/explicit Bash selects the checklist; Windows PowerShell, container `sh` and unresolved shells do not; Bash-selected Make recipes qualify, default POSIX recipes do not; tracked Bash hooks follow their shebang. All three templates share the content boundary and diagnostic-specific CI suppression. This is instruction inspection, not a live installation or model-adherence test.
- Full run: acquired `~/Work/projects/.locks/tooling-full-suite.d` atomically, wrote the handle into `owner`, and released it by EXIT trap. `SCRUT_JOBS=2 make test-all` exited 2 at the known lint failure; completed its remaining prerequisites under the same lock with `make validate` (passed) and `SCRUT_JOBS=2 make test-scrut`. All 56 documents ran once: 55 passed; only `environment-isolation.md` failed, with 50/51 cases passing and its known operand-contract assertion failing. `run-scrut-documents.md` passed. Tests, fixture helpers, validators and Makefile are unchanged from the merge base.
- Tidy: preserve `fix/502-review-config-embedded-shell-pre-tidy`, rebuild from the fixed merge base as two logical signed commits, and require an empty exact-tree diff against the backup before pushing. TOOLING owns merging and integration with PR 692.

## Main integration, 2026-11-02

- TOOLING relayed the tl27 drain go-ahead from CONDUCTOR's October 31 window decision, recorded November 2: signed merge, resolve conflicts and versions, targeted checks, then push. No rebase, force push or full suite.
- Signed merge `f6732a59` incorporates `origin/main` at `7817cab667d625bce777ad808a327d8e72f1b502`. Only the canonical and generated plugin manifests conflicted. Main has 1.0.4; 1.0.5 remains its next patch. Regenerated the mirror with `make build`; preserved both main's uncited-finding guidance and this branch's embedded-shell guidance.
- `check-versions`: sole changed plugin `set-up-review-config`, 1.0.4 to 1.0.5; generated manifest agrees, registration and version ownership valid. `bin/validate-json` and `bin/validate-plugins` passed.
- `bin/check-fixture-environments` passed with the error-output AST guard; `bin/check-fixture-environments --review-paths` passed. No branch-owned error-output annotation changes were needed. Scoped Markdown lint and Prettier checks passed.
- Each selected document ran through `make test-scrut` with `SCRUT_JOBS=2`, at most two Scrut processes total: `review-config-reporting.md` 3/3, `build-review-checklists.md` 27/27, `error-output-guard.md` 102/102, `environment-isolation.md` 51/51. All passed. Other incoming main documents and the full suite were not run, following TOOLING's thermal restriction; CI covers those changes.
- No behavior change beyond integrating main, no new review findings or review round. The original local review ended clean at Nit; these integration checks do not constitute a fresh review.
