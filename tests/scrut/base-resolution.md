# Base resolution outcomes

## An absent symbolic target reports not found

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${work}" \
>   && git init -q --template= . && git checkout -qb feature \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm feature --allow-empty \
>   && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/integration \
>   && for helper in "${REVIEW_SCOPE_BIN}" "${REVIEW_PR_WITH_CODEX_REVIEW_SCOPE_BIN}"; do \
>     "${helper}" | jq -c '{base_ref, committed_covered}'; \
>   done
{"base_ref":null,"committed_covered":false}
{"base_ref":null,"committed_covered":false}
```

## A valid ref reports its verified commit for inferred and explicit callers

```scrut
$ cd "${work}" && git update-ref refs/remotes/origin/integration HEAD \
>   && for helper in "${REVIEW_SCOPE_BIN}" "${REVIEW_PR_WITH_CODEX_REVIEW_SCOPE_BIN}"; do \
>     for mode in inferred explicit object qualified relative; do \
>       args=(); \
>       case "${mode}" in explicit) args=(--base origin/integration);; object) args=(--base "$(git rev-parse HEAD)");; qualified) args=(--base 'refs/remotes/origin/integration^{commit}');; relative) args=(--base refs/remotes/origin/integration~0);; esac; \
>       result="$("${helper}" ${args[@]+"${args[@]}"})" || exit; \
>       jq -e --arg head "$(git rev-parse HEAD)" '.base == $head and .committed_covered' <<< "${result}" || exit; \
>     done; \
>   done
true
true
true
true
true
true
true
true
true
true
```

## A real missing base object is an error for both callers

Each fixture creates its own loose base object, then moves that exact object
aside while leaving the remote-tracking ref intact. The feature HEAD has
independent history, so checking HEAD cannot detect the missing base object.

```scrut
$ broken="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && cd "${broken}" \
>   && git init -q --template= . && git checkout -qb base \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm base --allow-empty \
>   && base_oid="$(git rev-parse HEAD)" \
>   && git update-ref refs/remotes/origin/integration "${base_oid}" \
>   && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/integration \
>   && git checkout -q --orphan feature \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm feature --allow-empty \
>   && mv ".git/objects/${base_oid:0:2}/${base_oid:2}" missing-base-object \
>   && for helper in "${REVIEW_SCOPE_BIN}" "${REVIEW_PR_WITH_CODEX_REVIEW_SCOPE_BIN}"; do \
>     for mode in inferred explicit; do \
>       args=(); [[ "${mode}" == explicit ]] && args=(--base origin/integration); \
>       code=0; "${helper}" ${args[@]+"${args[@]}"} > out 2> err || code=$?; \
>       [[ "${code}" == 128 ]] && test ! -s out || exit 1; \
>       printf '%s exit=%s\n' "${mode}" "${code}"; cat err; \
>     done; \
>   done # error-output-allow: testcase asserts retained diagnostics: A real missing base object is an error for both callers
inferred exit=128
fatal: git show-ref: bad ref refs/remotes/origin/HEAD (*) (glob)
review-scope: could not resolve base (exit 128)
explicit exit=128
fatal: git show-ref: bad ref refs/remotes/origin/integration (*) (glob)
review-scope: could not resolve base (exit 128)
inferred exit=128
fatal: git show-ref: bad ref refs/remotes/origin/HEAD (*) (glob)
review-scope: could not resolve base (exit 128)
explicit exit=128
fatal: git show-ref: bad ref refs/remotes/origin/integration (*) (glob)
review-scope: could not resolve base (exit 128)
```

## An unexpected existence-query failure preserves its status and message

The committed Git function stub is exported only in the subshell and refuses
to run unless Git resolves to that function.

```scrut
$ cd "${work}" \
>   && ( function git() { \
>          if [[ "${1:-}" == show-ref ]]; then echo 'sample ref lookup failure' >&2; return 73; fi; \
>          command git "$@"; \
>        }; export -f git; \
>        [[ "$(type -t git)" == function ]] || exit 1; \
>        for helper in "${REVIEW_SCOPE_BIN}" "${REVIEW_PR_WITH_CODEX_REVIEW_SCOPE_BIN}"; do \
>          code=0; "${helper}" > out 2> err || code=$?; \
>          [[ "${code}" == 73 ]] && test ! -s out || exit 1; \
>          printf 'exit=%s\n' "${code}"; cat err; \
>        done ) # error-output-allow: testcase asserts retained diagnostics: An unexpected existence-query failure preserves its status and message
exit=73
sample ref lookup failure
review-scope: could not resolve base (exit 73)
exit=73
sample ref lookup failure
review-scope: could not resolve base (exit 73)
```

## A ref to a non-commit object preserves the commit check's diagnostic

```scrut
$ cd "${work}" && blob="$(printf 'sample blob\n' | git hash-object -w --stdin)" \
>   && git update-ref refs/remotes/origin/integration "${blob}" \
>   && for helper in "${REVIEW_SCOPE_BIN}" "${REVIEW_PR_WITH_CODEX_REVIEW_SCOPE_BIN}"; do \
>     code=0; "${helper}" > out 2> err || code=$?; \
>     [[ "${code}" == 128 ]] && test ! -s out || exit 1; cat err; \
>   done # error-output-allow: testcase asserts retained diagnostics: A ref to a non-commit object preserves the commit check's diagnostic
error: * expected commit type, but the object dereferences to blob type (glob)
fatal: Needed a single revision
review-scope: could not resolve base (exit 128)
error: * expected commit type, but the object dereferences to blob type (glob)
fatal: Needed a single revision
review-scope: could not resolve base (exit 128)
```

## The closing check uses the same error contract

```scrut
$ cd "${work}" && git update-ref refs/remotes/origin/integration HEAD \
>   && ( function git() { \
>          if [[ "${1:-}" == show-ref && "${4:-}" == refs/remotes/origin/integration ]]; then \
>            echo 'sample closing lookup failure' >&2; return 73; \
>          fi; \
>          command git "$@"; \
>        }; export -f git; \
>        [[ "$(type -t git)" == function ]] || exit 1; \
>        for helper in "${REVIEW_SCOPE_BIN}" "${REVIEW_PR_WITH_CODEX_REVIEW_SCOPE_BIN}"; do \
>          code=0; "${helper}" > out 2> err || code=$?; \
>          [[ "${code}" == 73 ]] && test ! -s out || exit 1; cat err; \
>        done ) # error-output-allow: testcase asserts retained diagnostics: The closing check uses the same error contract
sample closing lookup failure
review-scope: could not recheck base (exit 73)
sample closing lookup failure
review-scope: could not recheck base (exit 73)
```
