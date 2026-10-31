# Resolve the worktree stub's real Git from PATH

Fix [issue 440](https://github.com/cboone/agent-harness-plugins/issues/440) without changing live configuration.

- Prior art: `cache-lock-handoff` and `check-notifications` capture real tools with `command -v` before prepending stubs. This stub already runs inside the modified PATH, so enumerate executable Git candidates with Bash `type -aP` and skip its own file identity, including symlinks.
- The sibling search found no other `/usr/bin/git` reference under `tests/`.
- Add a constrained-PATH Scrut document with a committed wrapper definition, resolution guards, delegation/status assertions, and missing-Git coverage. Commit it before planting the original hard-coded delegation.
- Use the small-change review path: under 100 changed lines of tooling/tests and process documentation, outside security. Run one Codex review round, then lint, version checks and exact-tree tidy.
- No plugin source changes are planned, so plugin versions need no bump unless scope changes.
- Run affected documents during iteration. Run `make test-all` once with `SCRUT_JOBS=2` under the shared TOOLING lock before push. Record the known unrelated `review-submodule-fixture` failures separately.

## Plant evidence

| Defect                        | Instrument       | Observed result                                 | Regression coverage    |
| ----------------------------- | ---------------- | ----------------------------------------------- | ---------------------- |
| Restore hard-coded system Git | Wrapper call log | Failed: wrapper log absent; 3 of 5 cases failed | `git-worktree-stub.md` |
