# Test instructions

`scrut/` exercises plugin helpers and repository tooling. Executable stubs live in `fixtures/`; JSON inputs live in `data/`.

- Use the `write-scrut-tests` skill when changing snapshot tests.
- Register helper paths in both `../Makefile` (`SCRUT_ENV`) and `../.github/workflows/ci.yml` (`scrut-env`). A local-only registration leaves CI testing a different environment.
- Preserve checks that the three worktree helpers are identical across their two shipping plugins.
- Run `make test-scrut` from the repository root and observe its final result before reporting success.
