# Test instructions

`scrut/` exercises plugin helpers and repository tooling. Executable stubs live in `fixtures/`; JSON inputs live in `data/`.

- Use the `write-scrut-tests` skill when changing snapshot tests.
- Register helper paths in `../Makefile` (`SCRUT_ENV`), shared by local runs and CI. Route every Scrut process through `../bin/run-scrut` to apply the shared Git and budget reset before testcase shells start.
- Keep fixture-owned variables outside Git's reserved `GIT_*` namespace. Use `capture_child` from `../bin/lib/capture-child.bash` for retained child diagnostics. Keep stderr live for stdout-only data queries. Keep intentional `/dev/null` probes separate.
- Preserve the copy-drift checks for helpers that still ship in separate plugins.
- Run `make test-scrut` from the repository root and observe its final result before reporting success.

## Runtime budget

- Full suites use `~/Work/sl-vf/bin/suite-lock run heavy --` automatically when
  that executable is installed. `make test-all` locks its complete run; Scrut
  directory runs and snapshot updates take the same lock, including the default
  `tests/scrut/` tree.
  Named document runs, `--list` and help run directly. Nested calls rely on
  suite-lock's validated ownership, so a locked `make test-all` does not deadlock.
  CI and machines without that executable run directly. `HEAVY_SUITE_LOCK_BIN`
  overrides its path for isolated tests. Do not check `pgrep` before a full
  suite; the shared heavy lock queues the run. Keep `SCRUT_JOBS=2` locally and
  run at most two affected documents during iteration.

- CI runs each document under `tests/scrut/` as its own job, listed from the tree. Each job stops at 10 minutes, and every document should finish within half of that on `ubuntu-latest`. When one outgrows the half, cut its runtime or split it into two documents. Do not raise the ceiling.
- Time one document with `time make test-scrut SCRUT_TEST_DIR=tests/scrut/NAME.md`; scrut's own summary reports no duration. A case that needs a repository or a fixture tree pays for every process it starts. Where cases do not mutate the tree, prefer one prepared fixture per document to one per case. Keep tooling the suite runs repeatedly, such as `bin/validate-plugins`, free of per-item process starts.
- Locally, `make test-scrut` runs each document as its own scrut process through `../bin/run-scrut-documents`, up to `SCRUT_JOBS` at a time (default: the CPU count). The header in `../bin/lib/run-scrut-documents` describes how it lists documents, orders output and exits. `SCRUT_JOBS=1` runs them one after another for debugging; `make test-scrut-update` stays one sequential scrut call, so the rewritten expectations come back in a single stream to review. A run stopped by Ctrl-C or SIGTERM stops every running document with it. Documents share the machine, so a parallel run times each one higher than it runs alone; time a document on its own, as above.
- Scrut gives each document a 15-minute total timeout. `timeout in execution` with no stdout or stderr means a document ran out of that budget, not that an assertion failed; the named case is only where execution happened to be, and the rest of the document is skipped. Split or speed up the document. In CI the 10-minute job timeout stops a slow document first, so an overrun shows as a cancelled job instead.
