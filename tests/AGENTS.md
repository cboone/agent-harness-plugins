# Test instructions

`scrut/` exercises plugin helpers and repository tooling. Executable stubs live in `fixtures/`; JSON inputs live in `data/`.

- Use the `write-scrut-tests` skill when changing snapshot tests.
- Register helper paths in both `../Makefile` (`SCRUT_ENV`) and `../.github/workflows/ci.yml` (`scrut-env`). A local-only registration leaves CI testing a different environment.
- Preserve checks that the three worktree helpers are identical across their two shipping plugins.
- Run `make test-scrut` from the repository root and observe its final result before reporting success.

## Runtime budget

- The CI scrut job stops at 10 minutes, and the suite should finish within half of that on `ubuntu-latest`. When it outgrows the half, cut runtime or shard the job across test directories. Do not raise the ceiling.
- Time one document with `make test-scrut SCRUT_TEST_DIR=tests/scrut/NAME.md`. A case that needs a repository or a fixture tree pays for every process it starts, so prefer one prepared fixture per document to one per case, and keep tooling the suite runs repeatedly, such as `bin/validate-plugins`, free of per-item process starts.
- scrut runs documents one after another and gives each a 15-minute total timeout. `timeout in execution` with no stdout or stderr means a document ran out of that budget, not that an assertion failed; the named case is only where execution happened to be, and the rest of the document is skipped. Split or speed up the document.
