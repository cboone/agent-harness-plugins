# Run scrut documents in parallel locally (#573)

## Context

Issue #573: CI runs each document under `tests/scrut/` as its own matrix job (from #549), so its suite takes as long as the slowest document. `make test-scrut` still makes one `scrut --shell bash test tests/scrut/` call, which runs the 18 documents one after another, and a full local run now exceeds 10 minutes. Most of that time is in `validate-plugins-skills.md` and `validate-plugins-catalog.md`. The goal is local wall-clock time near the slowest document, with readable per-document output and a clear failure summary.

## Approach

Put the runner in a new Bash script, `bin/run-scrut-documents`, instead of inline Makefile shell. A script can be linted by `make lint-shell` (picked up automatically by `bin/list-shell-scripts`), tested by scrut, and shared with CI's document listing.

### 1. Add `bin/run-scrut-documents`

Follows the `write-bash-scripts` skill, with bash 3.2 compatibility (no `wait -n`, no `mapfile`).

- **Usage:** `run-scrut-documents [--list] [PATH]`. `PATH` defaults to `tests/scrut/` and may be a directory or a single document.
- **Discovery:** for a directory, the `find` expression CI used (`-type f -o -type l`; `*.md`, `*.markdown`, `*.scrut`, `*.t`, `*.cram`) with `-H`, so a symlinked PATH is followed, sorted under `LC_ALL=C`. A file path is used as is. The list is captured by command substitution, so a `find` error, such as an unreadable directory, stops the run with exit 2 instead of leaving a partial list. An empty list is also exit 2.
- **`--list`:** print the sorted documents, one per line, and exit. CI's `scrut-documents` job uses this, so local and CI discovery cannot drift.
- **Parallel run:** one `scrut --shell bash test DOCUMENT` per document through `xargs -0 -n 2 -P "${SCRUT_JOBS}"`, each writing stdout and stderr to its own log and its exit status to a status file in a `mktemp -d` directory removed by an `EXIT` trap. A one-line `finished` notice is printed as each document completes. The environment (`SCRUT_UNSET`, `SCRUT_ENV`) is inherited from the Makefile's `env` call, so the script needs no knowledge of it.
- **Job count:** `SCRUT_JOBS` overrides; the default is the CPU count (`getconf _NPROCESSORS_ONLN`, then `sysctl -n hw.ncpu`, then 1), confirmed by the measurements in step 5. `SCRUT_JOBS=1` gives a sequential run for debugging, so no separate target is needed.
- **Output:** once every document finishes, print each log in document order under a header line naming the document and its result. Then a summary: documents passed, and every failing document by name. Exit 1 when any document failed, 2 for usage errors, a missing path, a listing error, no documents or a missing scrut.
- **Single document:** with one document, run scrut directly in the foreground, so `make test-scrut SCRUT_TEST_DIR=tests/scrut/NAME.md` behaves exactly as today, live output included.
- **xargs stopping early:** a worker stopped by a signal, or one exiting 255, makes xargs stop starting documents. The runner records xargs's status, warns, and still prints the summary, where every document without a result counts as failed, and exits 1.
- **Signals:** xargs runs in its own process group under job control. SIGINT, SIGTERM and SIGHUP traps send SIGTERM to that group, so no scrut or testcase keeps running after the runner stops, and exit with 128 plus the signal number.

### 2. Wire the Makefile

- `test-scrut`: `env $(SCRUT_UNSET) $(SCRUT_ENV) bin/run-scrut-documents "$(SCRUT_TEST_DIR)"`, keeping the `command -v scrut` check. `SCRUT_JOBS` needs no wiring: make exports a command-line variable to recipes, and `SCRUT_UNSET` leaves it alone.
- `test-scrut-update` stays one sequential `scrut update --replace` call, so the rewritten expectations come back in a single stream to review.
- `test-all` keeps depending on `test-scrut`, so it runs in parallel by default.
- Update `help` text to mention `SCRUT_JOBS`.

### 3. Use the script in CI's listing

In `.github/workflows/ci.yml`'s `scrut-documents` job, replace the inline `find` with `bin/run-scrut-documents --list | jq -Rcs ...`. A failed listing, including an empty one, fails the step with an `::error::` annotation. The matrix jobs are unchanged.

### 4. Cover the script with scrut

Add `tests/scrut/run-scrut-documents.md` and a `tests/fixtures/scrut-stub`, with `RUN_SCRUT_DOCUMENTS_BIN` and `SCRUT_STUB_BIN` registered in both `SCRUT_ENV` and CI's `scrut-env`. Cases build small passing and failing documents in a `mktemp -d` directory (not under `tests/scrut/`, so discovery never picks them up), covering:

- help text;
- `--list` ordering, the extension and symlink filter, the default PATH and a symlinked PATH;
- an all-pass run: output in document order and exit 0;
- one progress line per document;
- a mixed run: each failing document's scrut diff printed and every failing document named, exit 1;
- removal of the temporary directory;
- a single document run directly, returning scrut's own status;
- xargs stopping early: documents without a result reported as failed;
- SIGTERM: every running document stopped and the temporary directory removed;
- a listing error, an empty directory, a missing path, more than one PATH, an invalid `SCRUT_JOBS` and an unknown option: error and exit 2.

### 5. Measure and check for interference

- Time `SCRUT_JOBS=1` and the default parallel run on this Mac, the full suite each time, and record both in the PR and in this plan.
- Exploration found no shared fixed paths: cases use their own `mktemp` directories, launcher cases override `TMPDIR` or key names on `BASHPID`, fixture builders copy the repository, and real-repository cases only read. Confirm empirically by running the parallel suite at least twice clean. If the two validator documents slow each other enough to matter, set the default job count from the measurements.

### 6. Documentation

- `tests/AGENTS.md` runtime budget: describe the local parallel run beside the CI matrix, `SCRUT_JOBS`, that each document still gets scrut's 15-minute timeout, and that `test-scrut-update` stays sequential.
- `bin/AGENTS.md`: one line saying `make test-scrut` runs through `run-scrut-documents`, whose `--list` also builds the CI matrix.
- Root `AGENTS.md` test command list: note `SCRUT_JOBS=1` for a sequential run, only if it stays within the size budget.

No plugin files change, so no version bumps and no `make build` output changes.

## Commits

1. `docs: plan parallel local scrut runs (#573)`: this plan.
2. `feat: run scrut documents in parallel locally (#573)`: script, Makefile, scrut document, env registration.
3. `ci: list scrut documents with bin/run-scrut-documents (#573)`.
4. `test: spell scrut fixture fences as escapes for Prettier (#573)`.
5. `test: give launch-workmux cases a 3-second launch wait (#573)`.
6. `docs: describe the local parallel scrut run (#573)`, with the measurements.
7. Review fixes: listing errors, a run xargs stops early, signal handling, the scrut stub and its cases, and comment and documentation corrections.

## Verification

- `make lint`, `make validate`.
- `make test-scrut SCRUT_TEST_DIR=tests/scrut/run-scrut-documents.md` and one other single document.
- `time make test-scrut SCRUT_JOBS=1` and `time make test-scrut`, both passing; record the times.
- Plant a failure in a scratch copy (or a temporary edit, reverted) to see the per-document failure summary and nonzero exit.
- `make test-all` passes, observing the final result.

## Outcome

### Measurements (2026-10-07, Apple M5 Max, 18 CPUs, on AC, full `make test-scrut`)

| Run                        | Wall clock | Result                                      |
| -------------------------- | ---------- | ------------------------------------------- |
| Sequential, `SCRUT_JOBS=1` | 714s       | 19 of 19 passed                             |
| Parallel, 18 jobs          | 317s       | 18 of 19 passed; `launch-workmux.md` failed |
| Parallel, 18 jobs          | 271s       | 19 of 19 passed                             |

Two further parallel runs passed but are excluded from timing because the machine slept during them. The two validator documents remain the critical path. `validate-plugins-catalog.md` and `validate-plugins-skills.md` took 226s and 260s in the sequential run, 237s and 267s in the passing 271s parallel run, and 280s and 313s in the 317s run that failed, so contention varies from run to run. A later `make test-all` on the same machine passed in 285s, lint and validation included. The default job count stays at the CPU count: with fewer slots, the validator documents, which sort last, would start late and lengthen the run. With 19 documents and 18 slots, the last one already waits for the first slot to free, which happens within seconds; if documents keep being added, starting the slowest ones first would keep that wait short.

### Interference

No document shares state with another. The one failure was a timing assumption in `launch-workmux.md`: without `--await-completion`, the launcher prints the workmux log after a fixed `WORKMUX_LAUNCH_WAIT_SECONDS` sleep, which the cases set to 1 second, and on a fully loaded machine the stub finished writing after that. The cases now wait 3 seconds, which takes that document from 62s to 121s alone, below both the local critical path and CI's 5-minute half-budget. A deterministic wait in the launcher itself would remove the race entirely; that is a change to two plugins and was left out of scope.
