# Run scrut documents

Tests for `bin/run-scrut-documents`, which `make test-scrut` uses to run one
scrut process per document and CI uses to list the documents for its matrix.

Each case builds its documents in a temporary directory, outside
`tests/scrut/`, so the runner's own discovery never picks them up. The fixture
documents are written with `printf` and a `fence` variable holding three
backticks, because a literal fence line inside this document would end the
enclosing test block. Cases `cd` into the directory so reported paths are
relative and stable. Documents finish in no fixed order, so the per-document
`finished` progress lines are filtered out; the ordered section that follows
them is what the cases pin.

## Help

```scrut
$ "${RUN_SCRUT_DOCUMENTS_BIN}" --help
Usage: run-scrut-documents [PATH]
       run-scrut-documents --list [PATH]

Run every scrut document under PATH, one scrut process per document and up
to SCRUT_JOBS at a time, then print each document's output in order and
name every failing document. PATH may be a directory or a single document,
which runs in the foreground with live output. PATH defaults to tests/scrut/

Options:
  --list      Print the documents that would run, one per line, and exit
  -h, --help  Show this help

Environment:
  SCRUT_JOBS  Documents to run at once (default: the CPU count); 1 runs them
              one after another
```

## List documents in sorted order, following symlinks and skipping other files

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

## Run passing documents and print each one's output in document order

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${dir}" && mkdir docs && fence='```' \
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

## Name every failing document and exit 1

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${dir}" && mkdir docs && fence='```' \
>   && printf '# A\n\n%sscrut\n$ echo a\nnot a\n%s\n' "${fence}" "${fence}" > docs/a.md \
>   && printf '# B\n\n%sscrut\n$ echo b\nb\n%s\n' "${fence}" "${fence}" > docs/b.md \
>   && printf '# C\n\n%sscrut\n$ echo c\nnot c\n%s\n' "${fence}" "${fence}" > docs/c.md \
>   && "${RUN_SCRUT_DOCUMENTS_BIN}" docs | grep -E '^(==>|[0-9]+ of|  docs/)'; exit "${PIPESTATUS[0]}"
==> docs/a.md: FAILED, exit 50 (*s) (glob)
==> docs/b.md: passed (*s) (glob)
==> docs/c.md: FAILED, exit 50 (*s) (glob)
2 of 3 scrut documents failed:
  docs/a.md
  docs/c.md
[1]
```

## Run a single document directly, with scrut's own output and status

```scrut
$ dir="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${dir}" && fence='```' \
>   && printf '# A\n\n%sscrut\n$ echo a\nnot a\n%s\n' "${fence}" "${fence}" > a.md \
>   && "${RUN_SCRUT_DOCUMENTS_BIN}" a.md 2>&1 | tail -1; exit "${PIPESTATUS[0]}"
Result: 1 document(s) with 1 testcase(s): 0 succeeded, 1 failed and 0 skipped
[50]
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
