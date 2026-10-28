# Reviewer completion

The skill calls the same completion gate exercised here before transcription.
A passing gate is not a clean review: semantic completion, schema, mode and
snapshot checks remain the caller's responsibility. Every backend invocation
resolves to the committed stub, with a fail-fast setup and an invocation guard.

## Setup

```scrut {fail_fast: true}
$ fixture="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && mkdir "${fixture}/bin" \
>   && ln -s "${REVIEWER_STUB_BIN}" "${fixture}/bin/reviewer" \
>   && export PATH="${fixture}/bin:${PATH}" FIXTURE="${fixture}" \
>   && function review_case() { \
>     test "$(command -v reviewer)" = "${FIXTURE}/bin/reviewer" \
>       && test "$(readlink "$(command -v reviewer)")" = "${REVIEWER_STUB_BIN}" || return 99; \
>     local reply="${FIXTURE}/${1}.txt" reviewer_status=0; \
>     reviewer "$1" "${reply}" < /dev/null > "${FIXTURE}/stdout" 2> "${FIXTURE}/stderr" || reviewer_status=$?; \
>     if test "$1" = silent; then reply="${FIXTURE}/stdout"; fi; \
>     "${REVIEW_COMPLETION_BIN}" "${reviewer_status}" "${reply}" "${2:-json}"; \
>   }
```

## Finished JSON with no findings passes the gate

```scrut
$ review_case ok
Reviewer completion: passed
```

## Mixed JSON and prose reports use text mode

The caller still validates the original structured portion separately under
its reviewer's contract; the mechanical gate preserves the full raw report.

```scrut
$ review_case mixed text
Reviewer completion: passed
```

## Zero exit and empty stdout fails

```scrut
$ review_case silent text 2>&1
Review-until-clean status: failed
check-completion: the output file has no review text
[1]
```

## Missing reply with stderr progress fails

```scrut
$ review_case missing 2>&1
Review-until-clean status: failed
check-completion: no output file was written
[1]
```

## Empty output file fails

```scrut
$ review_case empty 2>&1
Review-until-clean status: failed
check-completion: the output file has no review text
[1]
```

## Whitespace-only text fails

```scrut
$ review_case whitespace text 2>&1
Review-until-clean status: failed
check-completion: the output file has no review text
[1]
```

## Malformed JSON fails

```scrut
$ review_case malformed 2>&1
Review-until-clean status: failed
check-completion: the output is not exactly one JSON value
*parse error* (glob)
[1]
```

## Multiple JSON values fail

```scrut
$ review_case multiple 2>&1
Review-until-clean status: failed
check-completion: the output is not exactly one JSON value
[1]
```

## Non-zero exit fails even with valid output

```scrut
$ review_case nonzero 2>&1
Review-until-clean status: failed
check-completion: reviewer exited with status 7
[1]
```

## A missing stub refuses to run

```scrut
$ (PATH=/usr/bin:/bin review_case ok)
[99]
```

## Reruns preserve the earlier ledger and reserve a distinct filename

```scrut
$ printf '# Earlier run\n' > "${FIXTURE}/branch-until-clean.md" \
>   && printf '# New run\n' > "${FIXTURE}/temporary.md" \
>   && "${SAVE_REVIEW_LEDGER_BIN}" "${FIXTURE}/temporary.md" "${FIXTURE}" branch-until-clean \
>   && cat "${FIXTURE}/branch-until-clean.md" "${FIXTURE}/branch-until-clean-2.md"
*/branch-until-clean-2.md (glob)
# Earlier run
# New run
```

## An empty reservation is also preserved

```scrut
$ : > "${FIXTURE}/branch-until-clean-3.md" \
>   && "${SAVE_REVIEW_LEDGER_BIN}" "${FIXTURE}/temporary.md" "${FIXTURE}" branch-until-clean \
>   && test ! -s "${FIXTURE}/branch-until-clean-3.md" \
>   && cat "${FIXTURE}/branch-until-clean-4.md"
*/branch-until-clean-4.md (glob)
# New run
```

## A dangling symlink is a taken name

```scrut
$ ln -s absent "${FIXTURE}/link.md" \
>   && "${SAVE_REVIEW_LEDGER_BIN}" "${FIXTURE}/temporary.md" "${FIXTURE}" link \
>   && test ! -e "${FIXTURE}/absent" && cat "${FIXTURE}/link-2.md"
*/link-2.md (glob)
# New run
```

## Concurrent runs reserve different names and retain both complete ledgers

The Bash DEBUG trap pauses each writer immediately before its first reservation
redirection. Both reach that point before either is released. This also exposes
a separate existence check followed by an unprotected create.

```scrut
$ timeout 15 "${LEDGER_CONCURRENCY_BIN}" "${FIXTURE}"
writers: 0 0
distinct paths; both ledgers intact
```

## Reservation failure stops and preserves the underlying error and source

The mkdir stub leaves the directory absent, so the real reservation fails.
The deadline also detects a loop that treats every error as a collision.

```scrut
$ mkdir "${FIXTURE}/reserve-bin" \
>   && ln -s "${LEDGER_COMMAND_STUB_BIN}" "${FIXTURE}/reserve-bin/mkdir" \
>   && (export PATH="${FIXTURE}/reserve-bin:${PATH}" LEDGER_STUB_MODE=reserve; \
>     test "$(readlink "$(command -v mkdir)")" = "${LEDGER_COMMAND_STUB_BIN}" || exit 99; \
>     timeout 5 "${SAVE_REVIEW_LEDGER_BIN}" "${FIXTURE}/temporary.md" "${FIXTURE}/absent" run \
>       > "${FIXTURE}/reserve.out" 2> "${FIXTURE}/reserve.err"; \
>     result=$?; test "${result}" = 1 && test ! -s "${FIXTURE}/reserve.out" \
>       && grep 'cannot reserve .*temporary ledger retained at' "${FIXTURE}/reserve.err" \
>       && grep -E 'No such file or directory|no such file or directory' "${FIXTURE}/reserve.err" \
>       && cat "${FIXTURE}/temporary.md")
save-ledger: cannot reserve */absent/run.md; temporary ledger retained at */temporary.md (glob)
*No such file or directory* (glob)
# New run
```

## Copy failure never prints a successful destination

```scrut
$ mkdir "${FIXTURE}/copy-bin" \
>   && ln -s "${LEDGER_COMMAND_STUB_BIN}" "${FIXTURE}/copy-bin/cat" \
>   && (export PATH="${FIXTURE}/copy-bin:${PATH}" LEDGER_STUB_MODE=copy; \
>     test "$(readlink "$(command -v cat)")" = "${LEDGER_COMMAND_STUB_BIN}" || exit 99; \
>     "${SAVE_REVIEW_LEDGER_BIN}" "${FIXTURE}/temporary.md" "${FIXTURE}" copy \
>       > "${FIXTURE}/copy.out" 2> "${FIXTURE}/copy.err"; \
>     result=$?; test "${result}" = 19 && test ! -s "${FIXTURE}/copy.out") \
>   && cat "${FIXTURE}/copy.err" "${FIXTURE}/temporary.md"
save-ledger: cannot write */copy.md; temporary ledger retained at */temporary.md (glob)
sample copy failure
# New run
```

## Changed helpers and stubs never discard outcome-deciding stderr

The guard rejects both direct stderr-to-null and a merge into discarded stdout.
Capture to a variable is allowed because the failure path reports it.

```scrut
$ if grep -nE '2[[:space:]]*>[[:space:]]*/dev/null|>[[:space:]]*/dev/null[[:space:]]+2>&1|&>[[:space:]]*/dev/null' \
>     "${REVIEW_COMPLETION_BIN}" "${SAVE_REVIEW_LEDGER_BIN}" "${REVIEWER_STUB_BIN}" \
>     "${LEDGER_COMMAND_STUB_BIN}" "${LEDGER_CONCURRENCY_BIN}" "${LEDGER_BARRIER_ENV}"; then \
>     echo 'discarded diagnostics'; exit 1; \
>   else result=$?; test "${result}" = 1 && echo 'diagnostics guard passed'; fi
diagnostics guard passed
```

## A failing jq preserves stderr after the reason and leaves the verdict failed

```scrut
$ mkdir "${FIXTURE}/jq-bin" \
>   && ln -s "${LEDGER_COMMAND_STUB_BIN}" "${FIXTURE}/jq-bin/jq" \
>   && (export PATH="${FIXTURE}/jq-bin:${PATH}" LEDGER_STUB_MODE=validate; \
>     test "$(readlink "$(command -v jq)")" = "${LEDGER_COMMAND_STUB_BIN}" || exit 99; \
>     "${REVIEW_COMPLETION_BIN}" 0 "${FIXTURE}/ok.txt" json \
>       > "${FIXTURE}/jq.out" 2> "${FIXTURE}/jq.err"; \
>     result=$?; test "${result}" = 1 \
>       && test "$(cat "${FIXTURE}/jq.out")" = 'Review-until-clean status: failed') \
>   && cat "${FIXTURE}/jq.out" "${FIXTURE}/jq.err"
Review-until-clean status: failed
check-completion: the output is not exactly one JSON value
sample jq failure
```

## A failing grep preserves stderr after the reason and leaves the verdict failed

```scrut
$ mkdir "${FIXTURE}/grep-bin" \
>   && ln -s "${LEDGER_COMMAND_STUB_BIN}" "${FIXTURE}/grep-bin/grep" \
>   && (export PATH="${FIXTURE}/grep-bin:${PATH}" LEDGER_STUB_MODE=validate; \
>     test "$(readlink "$(command -v grep)")" = "${LEDGER_COMMAND_STUB_BIN}" || exit 99; \
>     "${REVIEW_COMPLETION_BIN}" 0 "${FIXTURE}/ok.txt" text \
>       > "${FIXTURE}/grep.out" 2> "${FIXTURE}/grep.err"; \
>     result=$?; test "${result}" = 1 \
>       && test "$(cat "${FIXTURE}/grep.out")" = 'Review-until-clean status: failed') \
>   && cat "${FIXTURE}/grep.out" "${FIXTURE}/grep.err"
Review-until-clean status: failed
check-completion: the output file has no review text
sample grep failure
```

## A failing mkdir preserves stderr after the reason and leaves no destination verdict

```scrut
$ mkdir "${FIXTURE}/mkdir-bin" \
>   && ln -s "${LEDGER_COMMAND_STUB_BIN}" "${FIXTURE}/mkdir-bin/mkdir" \
>   && (export PATH="${FIXTURE}/mkdir-bin:${PATH}" LEDGER_STUB_MODE=create; \
>     test "$(readlink "$(command -v mkdir)")" = "${LEDGER_COMMAND_STUB_BIN}" || exit 99; \
>     "${SAVE_REVIEW_LEDGER_BIN}" "${FIXTURE}/temporary.md" "${FIXTURE}/mkdir-failure" run \
>       > "${FIXTURE}/mkdir.out" 2> "${FIXTURE}/mkdir.err"; \
>     result=$?; test "${result}" = 25 && test ! -s "${FIXTURE}/mkdir.out") \
>   && cat "${FIXTURE}/mkdir.err" "${FIXTURE}/temporary.md"
save-ledger: cannot create */mkdir-failure; temporary ledger retained at */temporary.md (glob)
sample mkdir failure
# New run
```
