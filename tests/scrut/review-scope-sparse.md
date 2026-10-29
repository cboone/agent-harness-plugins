# Sparse raw snapshots

These local fixtures exercise full and sparse indexes, absent regular files
and symlinks, materialization and present paths outside the sparse cone.

## Setup

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash" \
>   && fixture="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && mkdir -p "${fixture}/repo/src" "${fixture}/repo/docs" \
>   && cd "${fixture}/repo" && git init -q --template= . \
>   && git config user.name Test && git config user.email test@example.invalid \
>   && git config core.safecrlf false && git config advice.sparseIndexExpanded false \
>   && printf 'one\n' > src/a && printf 'one\n' > docs/file \
>   && ln -s $'target\n\n' docs/link \
>   && printf 'docs/file text eol=lf\n' > .gitattributes \
>   && git add . && git -c commit.gpgsign=false commit -qm init \
>   && git sparse-checkout init --cone && git sparse-checkout set src
```

## Intentionally absent ordinary and symlink entries have no raw blobs

```scrut
$ "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/absent" \
>   && raw_tree="$(jq -r .raw_tree "${fixture}/absent")" \
>   && git ls-tree -r --name-only "${raw_tree}" \
>   && jq -c '{files, empty}' "${fixture}/absent"
.gitattributes
src/a
{"files":[".gitattributes","docs/file","docs/link","src/a"],"empty":true}
```

## A sparse index has identical captured content

```scrut
$ git sparse-checkout reapply --sparse-index \
>   && "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/sparse-index" \
>   && jq -n -e --slurpfile a "${fixture}/absent" --slurpfile b "${fixture}/sparse-index" \
>     '$a[0].snapshot == $b[0].snapshot and $a[0].files == $b[0].files'
true
```

## Materialization changes raw availability without changing stored content

```scrut
$ mkdir docs && git show HEAD:docs/file > docs/file && ln -s $'target\n\n' docs/link \
>   && "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/present" \
>   && jq -n -e --slurpfile a "${fixture}/absent" --slurpfile b "${fixture}/present" \
>     '$a[0].tree == $b[0].tree and $a[0].files == $b[0].files
>      and $a[0].raw_tree != $b[0].raw_tree and $a[0].snapshot != $b[0].snapshot'
true
```

## Present sparse files include raw-only EOL edits

```scrut
$ printf 'one\r\n' > docs/file \
>   && "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/eol" \
>   && jq -n -e --slurpfile a "${fixture}/present" --slurpfile b "${fixture}/eol" \
>     '$a[0].tree == $b[0].tree and $a[0].raw_tree != $b[0].raw_tree
>      and $a[0].snapshot != $b[0].snapshot' \
>   && "${CODEX_ASPECTS_BIN}" changes --before "${fixture}/present" --after "${fixture}/eol" \
>   | jq -c '{changed, outside_scope}'
true
{"changed":["docs/file"],"outside_scope":["docs/file"]}
```

## Present sparse symlinks hash exact link text without following targets

```scrut
$ raw_tree="$(jq -r .raw_tree "${fixture}/present")" \
>   && printf 'target\n\n' | git hash-object --stdin > "${fixture}/expected-link" \
>   && git rev-parse "${raw_tree}:docs/link" > "${fixture}/actual-link" \
>   && cmp "${fixture}/expected-link" "${fixture}/actual-link" \
>   && rm docs/link && ln -s changed-target docs/link \
>   && "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/link-edit" \
>   && "${CODEX_ASPECTS_BIN}" changes --before "${fixture}/eol" --after "${fixture}/link-edit" \
>   | jq -c '.changed'
["docs/link"]
```

## Non-normalized present sparse bytes still enter the raw tree

```scrut
$ printf 'different\n' > docs/file \
>   && "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/ordinary-edit" \
>   && "${CODEX_ASPECTS_BIN}" changes --before "${fixture}/link-edit" --after "${fixture}/ordinary-edit" \
>   | jq -c '.changed'
["docs/file"]
```

## A regular link-text file works with core.symlinks disabled

```scrut
$ git config core.symlinks false && rm docs/link && printf 'link-text\n' > docs/link \
>   && "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/link-file" \
>   && raw_tree="$(jq -r .raw_tree "${fixture}/link-file")" \
>   && git cat-file blob "${raw_tree}:docs/link" | cmp docs/link - \
>   && echo 'link-text bytes preserved'
link-text bytes preserved
```

## Scope capture leaves the caller's sparse index bytes untouched

```scrut
$ index_path="$(git rev-parse --git-path index)" \
>   && saved_index="$(git hash-object "${index_path}")" \
>   && "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/unchanged" \
>   && test "${saved_index}" = "$(git hash-object "${index_path}")" \
>   && echo 'sparse index untouched'
sparse index untouched
```

## A normally tracked path disappearing during raw capture still fails

The committed exported Git stub removes only this fixture's src/a, after the
temporary normalized index is captured. The marker proves the event occurred.

```scrut
$ export REVIEW_SPARSE_ROOT="${fixture}/repo" REVIEW_SPARSE_MARKER="${fixture}/fired" \
>   && function git() { local arg tagged=false; for arg in "$@"; do \
>        if [[ "${arg}" == -t ]]; then tagged=true; fi; done; command git "$@" || return; \
>        if [[ "${tagged}" == true && ! -e "${REVIEW_SPARSE_MARKER}" ]]; then \
>          rm "${REVIEW_SPARSE_ROOT}/src/a" || return; touch "${REVIEW_SPARSE_MARKER}"; fi; } \
>   && export -f git && test "$(type -t git)" = function \
>   && code=0 && "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/out" 2> "${fixture}/err" || code=$?; \
>   test "${code}" = 1 && test -e "${REVIEW_SPARSE_MARKER}" && test ! -s "${fixture}/out" \
>   && cat "${fixture}/err"; unset -f git
review-scope: raw working-tree file changed type or disappeared: src/a
```
