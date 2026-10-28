# Signed commit advice review

Reviewed through `80f87917`, based on `06a529a3b2508b138913d6ff6f058ed4930c7fff` (`origin/main`). The brief authorizes the small-change path for issue [650](https://github.com/cboone/agent-harness-plugins/issues/650).

## Changes and live verification

All three canonical signing instructions and the original completed plan now require trying `git commit -S` in the current host before considering escalation. An actual signing failure is required before following the host's escalation rules or reporting failure. No harness-specific sandbox claim was added. The plugin patch version is 1.3.3; `make build` regenerated the mirror.

Codex CLI 0.164.0 ran `git commit -S -m 'fix: try signed commits before escalating'` successfully in this worktree on the first attempt, using the session's existing full-access configuration without escalation or permission overrides. `git cat-file -p HEAD` showed `gpgsig -----BEGIN PGP SIGNATURE-----` on `80f87917`. This verifies signing in this session; no restricted-sandbox test was performed.

## Review round

One Nit round of `review-pr-with-codex`, using standalone read-only `codex exec` runs in parallel: `gpt-6.1-sol`, high effort, 872000-token window, base `origin/main`, fallback guide `CLAUDE.md`.

| Aspect   | Result                                         |
| -------- | ---------------------------------------------- |
| code     | Successful; no findings                        |
| comments | Successful; no findings                        |
| errors   | Skipped: no executable error handling changed  |
| tests    | Skipped: documentation-only change             |
| types    | Skipped: no types changed                      |
| simplify | Skipped: not selected on the small-change path |

Both outputs were nonempty, schema-valid, and exited successfully. The scope comparison found no lasting changes: tree `2cdc478d0552d5602314ff30fda1e054e50b39d8` before and after. Reviewers could not reach GitHub; repository ownership and archive status were verified by the parent session before editing.

Reviewer labels, severity judgments, take-or-record decisions and review-again decisions: none, because neither aspect reported findings. End state: **clean at Nit**. No full review loop, semgrep scan or planted defects were required by this docs-only small-change brief.

## Validation

- `corepack yarn install --immutable`: passed.
- `make build`: passed; only the expected `use-git` mirror changed.
- `make test-all`: passed in full, including all 32 Scrut documents.
- `check-versions`: passed against the actual `origin/main` merge base. Only `use-git` changed, with the appropriate patch bump from 1.3.2 to 1.3.3. Marketplace coverage and version ownership are consistent; no separate canonical Codex manifest exists for this plugin.
- `lint-and-fix --no-push`: success. `make format` ran Markdown and shell fixers without changing existing tracked files. `make lint` and `make validate` passed; `make build` left generated files unchanged. Check-only by project policy: none. Unresolved or skipped required tools: none. Parent continuation: tidy, then push and open the PR.
