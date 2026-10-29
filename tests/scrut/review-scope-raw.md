# Raw review snapshots

Each fixture keeps scope captures outside the repository. Normalized trees
remain comparable with Git, while snapshots must distinguish raw review input.

## Setup

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash" \
>   && fixture="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && mkdir "${fixture}/repo" && cd "${fixture}/repo" \
>   && git init -q --template= . && git checkout -q -b base \
>   && git config user.email test@example.invalid && git config user.name Test \
>   && printf 'one\n' > f.txt && git add f.txt \
>   && git -c commit.gpgsign=false commit -qm init
```

## Staged blobs invalidate review with identical disk and buckets

Staged blobs are independent reviewer inputs even when working-file content
and bucket membership stay unchanged.

```scrut
$ printf 'two\n' > f.txt && git add f.txt && printf 'one\n' > f.txt \
>   && "${REVIEW_SCOPE_BIN}" --base base > "${fixture}/before" \
>   && printf 'three\n' > f.txt && git add f.txt && printf 'one\n' > f.txt \
>   && "${REVIEW_SCOPE_BIN}" --base base > "${fixture}/after" \
>   && jq -n -e --slurpfile a "${fixture}/before" --slurpfile b "${fixture}/after" \
>     '$a[0].tree == $b[0].tree and $a[0].raw_tree == $b[0].raw_tree
>      and $a[0].membership == $b[0].membership
>      and $a[0].index != $b[0].index and $a[0].snapshot != $b[0].snapshot'
true
```

## EOL normalization cannot conceal a raw edit

```scrut
$ git reset -q -- f.txt && printf 'f.txt text eol=lf\n' > .gitattributes \
>   && git add .gitattributes && git -c commit.gpgsign=false commit -qm attributes \
>   && git config core.safecrlf false \
>   && "${REVIEW_SCOPE_BIN}" --base base > "${fixture}/before" \
>   && printf 'one\r\n' > f.txt \
>   && "${REVIEW_SCOPE_BIN}" --base base > "${fixture}/after" \
>   && jq -n -e --slurpfile a "${fixture}/before" --slurpfile b "${fixture}/after" \
>     '$a[0].tree == $b[0].tree and $a[0].membership == $b[0].membership
>      and $a[0].snapshot != $b[0].snapshot'
true
```

## Raw-only edits report their paths outside the original membership

```scrut
$ "${CODEX_ASPECTS_BIN}" changes --before "${fixture}/before" --after "${fixture}/after" \
>   | jq -c '{changed, outside_scope, scope_changed}'
{"changed":["f.txt"],"outside_scope":["f.txt"],"scope_changed":true}
```

## Clean filters cannot conceal consecutive raw edits

The fixture-local Git clean filter removes digits from input without using
an external service or changing user configuration.

```scrut
$ printf 'f.txt filter=digits\n' > .gitattributes \
>   && git config filter.digits.clean "tr -d '0-9'" \
>   && git config filter.digits.required true \
>   && printf 'two1\n' > f.txt && git add .gitattributes f.txt \
>   && "${REVIEW_SCOPE_BIN}" --base base > "${fixture}/before" \
>   && printf 'two2\n' > f.txt \
>   && "${REVIEW_SCOPE_BIN}" --base base > "${fixture}/after" \
>   && jq -n -e --slurpfile a "${fixture}/before" --slurpfile b "${fixture}/after" \
>     '$a[0].tree == $b[0].tree and $a[0].index == $b[0].index
>      and $a[0].membership == $b[0].membership
>      and $a[0].snapshot != $b[0].snapshot'
true
```

## Raw-only edits inside membership are accepted paths

```scrut
$ "${CODEX_ASPECTS_BIN}" changes --before "${fixture}/before" --after "${fixture}/after" \
>   | jq -c '{changed, outside_scope, scope_changed}'
{"changed":["f.txt"],"outside_scope":[],"scope_changed":true}
```

## Raw tree blobs contain the exact file bytes and bind the stored record

```scrut
$ raw_tree="$(jq -r '.raw_tree' "${fixture}/after")" \
>   && git cat-file blob "${raw_tree}:f.txt" | cmp f.txt - \
>   && snapshot="$(jq -r '.snapshot' "${fixture}/after")" \
>   && git cat-file blob "${snapshot}" | jq -e --arg raw "${raw_tree}" '.raw_tree == $raw'
true
```

## Repeated scans and stat-cache refreshes preserve both trees and snapshot

```scrut
$ saved="$(git ls-files --stage -z | git hash-object --stdin)" \
>   && touch f.txt && "${REVIEW_SCOPE_BIN}" --base base > "${fixture}/repeat" \
>   && jq -n -e --slurpfile a "${fixture}/after" --slurpfile b "${fixture}/repeat" \
>     '$a[0].snapshot == $b[0].snapshot and $a[0].raw_tree == $b[0].raw_tree' \
>   && test "${saved}" = "$(git ls-files --stage -z | git hash-object --stdin)"
true
```

## Older captured scopes still report actual normalized edits

```scrut
$ printf 'ordinary\n' > f.txt && printf 'new\n' > added.txt \
>   && "${REVIEW_SCOPE_BIN}" --base base > "${fixture}/normalized-after" \
>   && jq 'del(.raw_tree)' "${fixture}/after" > "${fixture}/old-before" \
>   && jq 'del(.raw_tree)' "${fixture}/normalized-after" > "${fixture}/old-after" \
>   && "${CODEX_ASPECTS_BIN}" changes --before "${fixture}/old-before" --after "${fixture}/old-after" \
>   | jq -c '{changed, outside_scope}'
{"changed":["added.txt","f.txt"],"outside_scope":["added.txt"]}
```

## Mixed old and new captures still report normalized edits

```scrut
$ "${CODEX_ASPECTS_BIN}" changes --before "${fixture}/old-before" --after "${fixture}/normalized-after" \
>   | jq -c '{changed, outside_scope}'
{"changed":["added.txt","f.txt"],"outside_scope":["added.txt"]}
```

## Restore the raw-only stability fixture

```scrut
$ rm added.txt && printf 'two2\n' > f.txt
```

## Raw-only changes during collection refuse inconsistent output

The exported Git function is a committed fixture stub. Its marker proves the
edit occurred after the opening capture and before the closing capture.

```scrut
$ export REVIEW_RAW_MUTATION_ROOT="${fixture}/repo" REVIEW_RAW_MUTATION_MARKER="${fixture}/fired" \
>   && function git() { local arg raw=false; for arg in "$@"; do \
>        if [[ "${arg}" == --raw ]]; then raw=true; fi; done; \
>        if [[ "${raw}" == true && ! -e "${REVIEW_RAW_MUTATION_MARKER}" ]]; then \
>          printf 'two3\n' > "${REVIEW_RAW_MUTATION_ROOT}/f.txt" || return; \
>          touch "${REVIEW_RAW_MUTATION_MARKER}" || return; fi; command git "$@"; } \
>   && export -f git && test "$(type -t git)" = function \
>   && code=0 && "${REVIEW_SCOPE_BIN}" --base base > "${fixture}/out" 2> "${fixture}/err" || code=$?; \
>   test "${code}" = 1 && test -e "${REVIEW_RAW_MUTATION_MARKER}" && test ! -s "${fixture}/out" \
>   && cat "${fixture}/err"; unset -f git
review-scope: the working tree changed while the scope was being read, so the file lists and the snapshot may describe different states; rerun once it has settled
```

## Nested raw edits propagate through snapshots and mutation paths

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" raw-nested
true
true
```

## Normalized-only filter output remains in the mutation-path union

```scrut
$ git add .gitattributes f.txt && git -c commit.gpgsign=false commit -qm normalized-baseline \
>   && "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/normalized-before" \
>   && git config filter.digits.clean "tr -d '0-9o'" \
>   && "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/filter-after" \
>   && jq -n -e --slurpfile a "${fixture}/normalized-before" --slurpfile b "${fixture}/filter-after" \
>     '$a[0].raw_tree == $b[0].raw_tree and $a[0].tree != $b[0].tree
>      and $a[0].snapshot != $b[0].snapshot' \
>   && "${CODEX_ASPECTS_BIN}" changes --before "${fixture}/normalized-before" --after "${fixture}/filter-after" \
>   | jq -c '{changed, outside_scope}'
true
{"changed":["f.txt"],"outside_scope":["f.txt"]}
```
