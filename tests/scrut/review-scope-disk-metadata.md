# Raw filesystem metadata

The normalized sparse index retains old modes. The raw tree must measure disk
type and the owner-execute bit even when Git settings ignore those changes.

## Setup

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash" \
>   && fixture="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && mkdir -p "${fixture}/repo/src" "${fixture}/repo/docs" \
>   && cd "${fixture}/repo" && git init -q --template= . \
>   && git config user.name Test && git config user.email test@example.invalid \
>   && git config core.symlinks true && git config core.filemode false \
>   && printf 'one\n' > src/file && printf 'same' > docs/file \
>   && chmod 644 src/file docs/file && ln -s original docs/link \
>   && git add . && git -c commit.gpgsign=false commit -qm init \
>   && git sparse-checkout init --cone --sparse-index && git sparse-checkout set src \
>   && git config advice.sparseIndexExpanded false \
>   && mkdir docs && printf 'same' > docs/file && ln -s changed-target docs/link \
>   && "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/before"
```

## Same-byte symlink-to-regular replacement invalidates the snapshot

```scrut
$ rm docs/link && printf 'changed-target' > docs/link && chmod 644 docs/link \
>   && "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/regular" \
>   && jq -n -e --slurpfile a "${fixture}/before" --slurpfile b "${fixture}/regular" \
>     '$a[0].tree == $b[0].tree and $a[0].membership == $b[0].membership
>      and $a[0].snapshot != $b[0].snapshot and $a[0].raw_tree != $b[0].raw_tree' \
>   && git ls-tree "$(jq -r .raw_tree "${fixture}/regular")" docs/link | cut -d ' ' -f 1
true
100644
```

## Same-byte regular-to-symlink replacement invalidates the snapshot

```scrut
$ rm docs/file && ln -s same docs/file \
>   && "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/linked" \
>   && jq -n -e --slurpfile a "${fixture}/regular" --slurpfile b "${fixture}/linked" \
>     '$a[0].tree == $b[0].tree and $a[0].snapshot != $b[0].snapshot
>      and $a[0].raw_tree != $b[0].raw_tree' \
>   && git ls-tree "$(jq -r .raw_tree "${fixture}/linked")" docs/file | cut -d ' ' -f 1
true
120000
```

## Sparse executable-bit changes invalidate review despite core.filemode

```scrut
$ chmod 744 docs/link \
>   && "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/executable" \
>   && jq -n -e --slurpfile a "${fixture}/linked" --slurpfile b "${fixture}/executable" \
>     '$a[0].tree == $b[0].tree and $a[0].snapshot != $b[0].snapshot' \
>   && git ls-tree "$(jq -r .raw_tree "${fixture}/executable")" docs/link | cut -d ' ' -f 1
true
100755
```

## In-cone executable-bit changes also ignore core.filemode

```scrut
$ chmod 744 src/file \
>   && "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/in-cone" \
>   && jq -n -e --slurpfile a "${fixture}/executable" --slurpfile b "${fixture}/in-cone" \
>     '$a[0].tree == $b[0].tree and $a[0].snapshot != $b[0].snapshot'
true
```

## Raw type and mode changes report their actual paths

```scrut
$ "${CODEX_ASPECTS_BIN}" changes --before "${fixture}/before" --after "${fixture}/in-cone" \
>   | jq -c '.changed'
["docs/file","docs/link","src/file"]
```

## A pseudo-link is regular disk content with core.symlinks disabled

```scrut
$ git config core.symlinks false \
>   && "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/pseudo" \
>   && git ls-tree "$(jq -r .raw_tree "${fixture}/pseudo")" docs/link | cut -d ' ' -f 1 \
>   && git ls-tree "$(jq -r .tree "${fixture}/pseudo")" docs/link | cut -d ' ' -f 1
100755
120000
```

## A full index preserves the same captured filesystem state

```scrut
$ git sparse-checkout reapply --no-sparse-index \
>   && "${REVIEW_SCOPE_BIN}" --base HEAD > "${fixture}/full-index" \
>   && jq -n -e --slurpfile a "${fixture}/pseudo" --slurpfile b "${fixture}/full-index" \
>     '$a[0].raw_tree == $b[0].raw_tree'
true
```
