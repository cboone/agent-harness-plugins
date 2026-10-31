# Worktree stub Git delegation

## Constrained PATH setup

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash" \
>   && root="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && mkdir "${root}/stub" "${root}/alias" "${root}/real" \
>   && cp "${WORKTREE_GIT_STUB_BIN}" "${root}/stub/git" \
>   && ln -s "${root}/stub/git" "${root}/alias/git" \
>   && ln -s "$(command -v bash)" "${root}/stub/bash" \
>   && ln -s "$(command -v basename)" "${root}/stub/basename" \
>   && printf '%s\n' '#!/usr/bin/env bash' 'printf "%s\n" "$*" >> "$0.calls"' '[[ "$*" == "check-ref-format --branch feature/valid" ]] || exit 23' > "${root}/real/git" \
>   && chmod +x "${root}/real/git" \
>   && stub_path="${root}/stub:${root}/alias" \
>   && [[ "$(PATH="${stub_path}:${root}/real" command -v git)" == "${root}/stub/git" ]]
```

## PATH wrapper receives the ref validation call after stub aliases

```scrut
$ PATH="${stub_path}:${root}/real" "${root}/stub/git" check-ref-format --branch feature/valid \
>   && cat "${root}/real/git.calls"
check-ref-format --branch feature/valid
```

## Wrapper rejection status survives delegation

```scrut
$ PATH="${stub_path}:${root}/real" "${root}/stub/git" check-ref-format --branch 'invalid name'
[23]
```

## Missing real Git reports a clear failure

```scrut
$ PATH="${stub_path}" "${root}/stub/git" check-ref-format --branch feature/valid 2>&1
git: no real Git executable found in PATH
[127]
```

## Forced rejection does not require real Git

```scrut
$ STUB_GIT_INVALID_REF=1 PATH="${stub_path}" "${root}/stub/git" check-ref-format --branch feature/valid
[1]
```
