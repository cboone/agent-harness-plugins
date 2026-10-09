# Run scrut documents

Tests for `bin/run-scrut-documents`, which `make test-scrut` uses to run one
scrut process per document and CI uses to list the documents for its matrix.

Each case builds its documents in a temporary directory, outside
`tests/scrut/`, so the runner's own discovery never picks them up. The fixture
documents are written with `printf` and a `fence` variable holding three
backticks, spelled as `\x60` escapes so this document's own fences stay three
backticks long. Cases `cd` into the directory so reported paths are relative
and stable. Documents finish in no fixed order, so cases that pin output filter
out the per-document `finished` progress lines and pin the ordered section that
follows them.

Cases about an interrupted or aborted run put `tests/fixtures/scrut-stub` on
`PATH` as `scrut`, so a document's name decides whether it passes, stops its
worker or stays running until signalled.

## Help

```scrut
$ "${RUN_SCRUT_DOCUMENTS_BIN}" --help
Usage: run-scrut-documents [PATH]
       run-scrut-documents --list [PATH]

Run every scrut document under PATH, one scrut process per document and up
to SCRUT_JOBS at a time, then print each document's output in order and
name every failing document. PATH may be a directory or a single document,
and defaults to tests/scrut/. When PATH holds only one document, it runs in
the foreground with live output.

Options:
  --list      Print the documents that would run, one per line, and exit
  -h, --help  Show this help

Environment:
  SCRUT_JOBS  Documents to run at once (default: the CPU count); 1 runs them
              one after another
```

## List documents in sorted order, including symlinks and skipping other files

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${dir}" \
>   && mkdir -p docs/sub && touch docs/b.md docs/a.md docs/sub/c.scrut docs/d.t docs/notes.txt \
>   && ln -s a.md docs/link.md \
>   && "${RUN_SCRUT_DOCUMENTS_BIN}" --list docs
docs/a.md
docs/b.md
docs/d.t
docs/link.md
docs/sub/c.scrut
```

## List documents under tests/scrut/ when no PATH is given

CI builds its matrix from this form.

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${dir}" \
>   && mkdir -p tests/scrut && touch tests/scrut/b.md tests/scrut/a.md \
>   && "${RUN_SCRUT_DOCUMENTS_BIN}" --list
tests/scrut/a.md
tests/scrut/b.md
```

## List documents through a symlinked PATH

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${dir}" \
>   && mkdir docs && touch docs/a.md && ln -s docs link \
>   && "${RUN_SCRUT_DOCUMENTS_BIN}" --list link
link/a.md
```

## Run passing documents and print each one's output in document order

`a.md` sleeps, so `b.md` usually finishes first; the output still lists `a.md`
first.

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${dir}" && mkdir docs && fence=$'\x60\x60\x60' \
>   && printf '# A\n\n%sscrut\n$ sleep 1 && echo a\na\n%s\n' "${fence}" "${fence}" > docs/a.md \
>   && printf '# B\n\n%sscrut\n$ echo b\nb\n%s\n' "${fence}" "${fence}" > docs/b.md \
>   && SCRUT_JOBS=2 "${RUN_SCRUT_DOCUMENTS_BIN}" docs | grep -v '^finished '
Running 2 scrut documents, 2 at a time

==> docs/a.md: passed (*s) (glob)
Result: 1 document(s) with 1 testcase(s): 1 succeeded, 0 failed and 0 skipped

==> docs/b.md: passed (*s) (glob)
Result: 1 document(s) with 1 testcase(s): 1 succeeded, 0 failed and 0 skipped

All 2 scrut documents passed.
```

## Print one progress line per document as it finishes

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${dir}" && mkdir docs && fence=$'\x60\x60\x60' \
>   && printf '# A\n\n%sscrut\n$ echo a\na\n%s\n' "${fence}" "${fence}" > docs/a.md \
>   && printf '# B\n\n%sscrut\n$ echo b\nnot b\n%s\n' "${fence}" "${fence}" > docs/b.md \
>   && "${RUN_SCRUT_DOCUMENTS_BIN}" docs | grep '^finished ' | sort; exit "${PIPESTATUS[0]}"
finished docs/a.md: passed (*s) (glob)
finished docs/b.md: FAILED, exit 50 (*s) (glob)
[1]
```

## Name every failing document, print its scrut output and exit 1

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${dir}" && mkdir docs && fence=$'\x60\x60\x60' \
>   && printf '# A\n\n%sscrut\n$ echo a\nnot a\n%s\n' "${fence}" "${fence}" > docs/a.md \
>   && printf '# B\n\n%sscrut\n$ echo b\nb\n%s\n' "${fence}" "${fence}" > docs/b.md \
>   && printf '# C\n\n%sscrut\n$ echo c\nnot c\n%s\n' "${fence}" "${fence}" > docs/c.md \
>   && "${RUN_SCRUT_DOCUMENTS_BIN}" docs | grep -E '^(==>|Result:|[0-9]+ of|  docs/|.*[-+] (not )?[ac]$)'; exit "${PIPESTATUS[0]}"
==> docs/a.md: FAILED, exit 50 (*s) (glob)
1     | - not a
   1  | + a
Result: 1 document(s) with 1 testcase(s): 0 succeeded, 1 failed and 0 skipped
==> docs/b.md: passed (*s) (glob)
Result: 1 document(s) with 1 testcase(s): 1 succeeded, 0 failed and 0 skipped
==> docs/c.md: FAILED, exit 50 (*s) (glob)
1     | - not c
   1  | + c
Result: 1 document(s) with 1 testcase(s): 0 succeeded, 1 failed and 0 skipped
2 of 3 scrut documents failed:
  docs/a.md
  docs/c.md
[1]
```

## Remove its temporary directory after a run

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${dir}" && mkdir docs tmp && fence=$'\x60\x60\x60' \
>   && printf '# A\n\n%sscrut\n$ echo a\na\n%s\n' "${fence}" "${fence}" > docs/a.md \
>   && printf '# B\n\n%sscrut\n$ echo b\nb\n%s\n' "${fence}" "${fence}" > docs/b.md \
>   && TMPDIR="${dir}/tmp" "${RUN_SCRUT_DOCUMENTS_BIN}" docs > /dev/null \
>   && ls -A tmp && echo "temp cleanup: yes"
temp cleanup: yes
```

## Run a single document directly, with scrut's own output and status

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${dir}" && fence=$'\x60\x60\x60' \
>   && printf '# A\n\n%sscrut\n$ echo a\nnot a\n%s\n' "${fence}" "${fence}" > a.md \
>   && "${RUN_SCRUT_DOCUMENTS_BIN}" a.md 2>&1 | tail -1; exit "${PIPESTATUS[0]}"
Result: 1 document(s) with 1 testcase(s): 0 succeeded, 1 failed and 0 skipped
[50]
```

## Report documents that never ran when xargs stops early

The stub stops the worker for `b-kill.md`, so xargs starts no further
documents. The runner still prints the summary and counts both documents
without a result as failed.

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${dir}" && mkdir docs stub \
>   && cp "${SCRUT_STUB_BIN}" stub/scrut && touch docs/a.md docs/b-kill.md docs/c.md \
>   && PATH="${dir}/stub:${PATH}" SCRUT_JOBS=1 "${RUN_SCRUT_DOCUMENTS_BIN}" docs 2> stderr \
>     | grep -E '^(==>|ran |\(not run\)|[0-9]+ of|  docs/)'; status="${PIPESTATUS[0]}"; grep -c 'run was cut short' stderr; exit "${status}"
==> docs/a.md: passed (*s) (glob)
ran docs/a.md
==> docs/b-kill.md: FAILED, exit missing (?s)
==> docs/c.md: FAILED, exit missing (?s)
(not run)
2 of 3 scrut documents failed:
  docs/b-kill.md
  docs/c.md
1
[1]
```

## Stop every running document when the runner receives SIGTERM

The case waits until both stub processes have recorded their PIDs, so the
signal always arrives while documents are running.

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${dir}" && mkdir docs stub tmp \
>   && cp "${SCRUT_STUB_BIN}" stub/scrut && touch docs/a-slow.md docs/b-slow.md \
>   && { PATH="${dir}/stub:${PATH}" STUB_SCRUT_PIDS="${dir}/pids" TMPDIR="${dir}/tmp" "${RUN_SCRUT_DOCUMENTS_BIN}" docs > /dev/null & } \
>   && runner=$! \
>   && for ((attempt = 0; attempt < 100; attempt++)); do [[ "$(wc -l < pids 2> /dev/null || echo 0)" -ge 2 ]] && break; sleep 0.1; done \
>   && kill -TERM "${runner}"; status=0; wait "${runner}" || status=$?; echo "exit: ${status}" \
>   && sleep 0.5 && still_running=0 && while read -r pid; do kill -0 "${pid}" 2> /dev/null && still_running=$((still_running + 1)); done < pids; echo "still running: ${still_running}" \
>   && ls -A tmp && echo "temp cleanup: yes"
exit: 143
still running: 0
temp cleanup: yes
```

## Stop with a listing error instead of running a partial list

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${dir}" && mkdir -p docs/open docs/closed \
>   && touch docs/open/a.md docs/closed/b.md && chmod 000 docs/closed \
>   && { "${RUN_SCRUT_DOCUMENTS_BIN}" --list docs 2>&1; status=$?; chmod 755 docs/closed; exit "${status}"; }
find: *docs/closed*: Permission denied (glob)
run-scrut-documents: could not list scrut documents under docs
[2]
```

## Reject a directory with no documents

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${dir}" && mkdir docs && touch docs/notes.txt \
>   && "${RUN_SCRUT_DOCUMENTS_BIN}" docs 2>&1
run-scrut-documents: no scrut documents found under docs
[2]
```

## Reject a missing path

```scrut
$ "${RUN_SCRUT_DOCUMENTS_BIN}" /nonexistent/run-scrut-documents 2>&1
run-scrut-documents: no such file or directory: /nonexistent/run-scrut-documents
Run run-scrut-documents --help for usage.
[2]
```

## Reject more than one PATH

```scrut
$ "${RUN_SCRUT_DOCUMENTS_BIN}" tests tests 2>&1
run-scrut-documents: expected at most one PATH
Run run-scrut-documents --help for usage.
[2]
```

## Reject a job count that is not a positive integer

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${dir}" \
>   && SCRUT_JOBS=0 "${RUN_SCRUT_DOCUMENTS_BIN}" . 2>&1
run-scrut-documents: SCRUT_JOBS must be a positive integer, got: 0
Run run-scrut-documents --help for usage.
[2]
```

## Reject an unknown option

```scrut
$ "${RUN_SCRUT_DOCUMENTS_BIN}" --jobs 2 2>&1
run-scrut-documents: unknown option: --jobs
Run run-scrut-documents --help for usage.
[2]
```
