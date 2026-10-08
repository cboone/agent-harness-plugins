# Run scrut documents in parallel locally (#573)

## Context

Issue #573: CI runs each document under `tests/scrut/` as its own matrix job (from #549), so its suite takes as long as the slowest document. `make test-scrut` still makes one `scrut --shell bash test tests/scrut/` call, which runs the 18 documents one after another, and a full local run now exceeds 10 minutes. Most of that time is in `validate-plugins-skills.md` and `validate-plugins-catalog.md`. The goal is local wall-clock time near the slowest document, with readable per-document output and a clear failure summary.

## Approach

Put the runner in a new Bash script, `bin/run-scrut-documents`, instead of inline Makefile shell. A script can be linted by `make lint-shell` (picked up automatically by `bin/list-shell-scripts`), tested by scrut, and shared with CI's document listing.

### 1. Add `bin/run-scrut-documents`

Follows the `write-bash-scripts` skill, with bash 3.2 compatibility (no `wait -n`, no `mapfile`).

- **Usage:** `run-scrut-documents [--list] [PATH]`. `PATH` defaults to `tests/scrut/` and may be a directory or a single document.
- **Discovery:** for a directory, the same `find` expression as CI (`-type f -o -type l`; `*.md`, `*.markdown`, `*.scrut`, `*.t`, `*.cram`), sorted. A file path is used as is. An empty list is an error, as in CI.
- **`--list`:** print the sorted documents, one per line, and exit. CI's `scrut-documents` job uses this, so local and CI discovery cannot drift.
- **Parallel run:** one `scrut --shell bash test DOCUMENT` per document through `xargs -0 -P "${SCRUT_JOBS}"`, each writing stdout and stderr to its own log and its exit status to a status file in a `mktemp -d` directory removed by an `EXIT` trap. The environment (`SCRUT_UNSET`, `SCRUT_ENV`) is inherited from the Makefile's `env` call, so the script needs no knowledge of it.
- **Job count:** `SCRUT_JOBS` overrides; the default is the CPU count (`getconf _NPROCESSORS_ONLN`, falling back to 1), adjusted after measuring in step 5. `SCRUT_JOBS=1` gives a sequential run for debugging, so no separate target is needed.
- **Output:** once every document finishes, print each log in document order under a header line naming the document and its result. Then a summary: documents passed, and every failing document by name. Exit 1 when any document failed, 2 for usage errors.
- **Single document:** with one document, run scrut directly in the foreground, so `make test-scrut SCRUT_TEST_DIR=tests/scrut/NAME.md` behaves exactly as today, live output included.

### 2. Wire the Makefile

- `test-scrut`: `env $(SCRUT_UNSET) $(SCRUT_ENV) bin/run-scrut-documents "$(SCRUT_TEST_DIR)"`, keeping the `command -v scrut` check. Pass `SCRUT_JOBS` through when set.
- `test-scrut-update` stays a single sequential `scrut update --replace` call, since it rewrites files.
- `test-all` keeps depending on `test-scrut`, so it runs in parallel by default.
- Update `help` text to mention `SCRUT_JOBS`.

### 3. Use the script in CI's listing

In `.github/workflows/ci.yml`'s `scrut-documents` job, replace the inline `find` with `bin/run-scrut-documents --list | jq -Rcs ...`, keeping the empty-list error. The matrix jobs are unchanged.

### 4. Cover the script with scrut

Add `tests/scrut/run-scrut-documents.md`, with `RUN_SCRUT_DOCUMENTS_BIN` registered in both `SCRUT_ENV` and CI's `scrut-env`. Cases build small passing and failing documents in a `mktemp -d` directory (not under `tests/scrut/`, so discovery never picks them up), covering:

- `--list` ordering and the extension and symlink filter;
- an all-pass run: output in document order and exit 0;
- a mixed run: both failing documents named in the summary, exit 1;
- an empty directory and a missing path: error and exit 2;
- `SCRUT_JOBS` validation (non-numeric or zero rejected).

### 5. Measure and check for interference

- Time `SCRUT_JOBS=1` and the default parallel run on this Mac, the full suite each time, and record both in the PR and in this plan.
- Exploration found no shared fixed paths: cases use their own `mktemp` directories, launcher cases override `TMPDIR` or key names on `BASHPID`, fixture builders copy the repository, and real-repository cases only read. Confirm empirically by running the parallel suite at least twice clean. If the two validator documents slow each other enough to matter, set the default job count from the measurements.

### 6. Documentation

- `tests/AGENTS.md` runtime budget: describe the local parallel run beside the CI matrix, `SCRUT_JOBS`, that each document still gets scrut's 15-minute timeout, and that `test-scrut-update` stays sequential.
- `bin/AGENTS.md`: one line saying `run-scrut-documents` owns scrut document discovery for local runs and CI.
- Root `AGENTS.md` test command list: note `SCRUT_JOBS=1` for a sequential run, only if it stays within the size budget.

No plugin files change, so no version bumps and no `make build` output changes.

## Commits

1. `feat: run scrut documents in parallel locally (#573)`: script, Makefile, scrut document, env registration.
2. `ci: list scrut documents with bin/run-scrut-documents (#573)`.
3. `docs: describe the local parallel scrut run (#573)`, plus this plan.

## Verification

- `make lint`, `make validate`.
- `make test-scrut SCRUT_TEST_DIR=tests/scrut/run-scrut-documents.md` and one other single document.
- `time make test-scrut SCRUT_JOBS=1` and `time make test-scrut`, both passing; record the times.
- Plant a failure in a scratch copy (or a temporary edit, reverted) to see the per-document failure summary and nonzero exit.
- `make test-all` passes, observing the final result.
