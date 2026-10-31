# Edit-mode working tree precondition

The edit-mode helper refuses existing local changes before any fixer runs.
Ignored untracked files do not block it. Refusal leaves content and the index
unchanged; the caller never commits or stashes on the user's behalf.

## Clean working tree

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash" \
>   && fixture="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && export FIXTURE="${fixture}" \
>   && cd "${FIXTURE}" \
>   && git init -q --template= \
>   && git config user.name 'Test User' \
>   && git config user.email 'test@example.com' \
>   && git config commit.gpgsign false \
>   && printf 'original\n' > tracked.txt \
>   && printf 'ignored.txt\n' > .gitignore \
>   && git add tracked.txt .gitignore \
>   && git commit -q -m initial \
>   && "${CHECK_EDIT_WORKTREE_BIN}"
```

## Ignored untracked file

```scrut
$ printf 'ignored\n' > ignored.txt && "${CHECK_EDIT_WORKTREE_BIN}"
```

## Unstaged edit

```scrut
$ printf 'local edit\n' > tracked.txt && "${CHECK_EDIT_WORKTREE_BIN}" 2>&1
check-edit-worktree: --edit requires a clean working tree; commit or stash local changes first
[1]
```

## Refusal preserves unstaged content and the index

```scrut
$ cat tracked.txt && git status --porcelain=v1
local edit
 M tracked.txt
```

## Staged edit

```scrut
$ git add tracked.txt && "${CHECK_EDIT_WORKTREE_BIN}" 2>&1
check-edit-worktree: --edit requires a clean working tree; commit or stash local changes first
[1]
```

## Refusal preserves staged content

```scrut
$ git show :tracked.txt && git status --porcelain=v1
local edit
M  tracked.txt
```

## Untracked file outside a nested invocation directory

```scrut
$ git commit -q -m 'record local edit' \
>   && printf 'untracked\n' > new.txt \
>   && mkdir nested \
>   && cd nested \
>   && "${CHECK_EDIT_WORKTREE_BIN}" 2>&1
check-edit-worktree: --edit requires a clean working tree; commit or stash local changes first
[1]
```

## Refusal preserves untracked content

```scrut
$ cat ../new.txt && git status --porcelain=v1
untracked
?? new.txt
```

## Config cannot hide untracked files

```scrut
$ git config status.showUntrackedFiles no && "${CHECK_EDIT_WORKTREE_BIN}" 2>&1
check-edit-worktree: --edit requires a clean working tree; commit or stash local changes first
[1]
```

## Clean assume-unchanged entry

```scrut
$ cd "${FIXTURE}" \
>   && rm -- new.txt \
>   && git config --unset status.showUntrackedFiles \
>   && git update-index --assume-unchanged tracked.txt \
>   && "${CHECK_EDIT_WORKTREE_BIN}" 2>&1
check-edit-worktree: --edit cannot verify hidden index flags; clear assume-unchanged or skip-worktree first
[1]
```

## Modified assume-unchanged entry

```scrut
$ printf 'hidden edit\n' > tracked.txt && "${CHECK_EDIT_WORKTREE_BIN}" 2>&1
check-edit-worktree: --edit cannot verify hidden index flags; clear assume-unchanged or skip-worktree first
[1]
```

## Hidden parent entry from a nested invocation

```scrut
$ (cd nested && "${CHECK_EDIT_WORKTREE_BIN}") 2>&1
check-edit-worktree: --edit cannot verify hidden index flags; clear assume-unchanged or skip-worktree first
[1]
```

## Refusal preserves hidden content and flags

```scrut
$ cat tracked.txt && git ls-files -v -- tracked.txt
hidden edit
h tracked.txt
```

## Clean skip-worktree entry

```scrut
$ printf 'local edit\n' > tracked.txt \
>   && git update-index --no-assume-unchanged tracked.txt \
>   && git update-index --skip-worktree tracked.txt \
>   && "${CHECK_EDIT_WORKTREE_BIN}" 2>&1
check-edit-worktree: --edit cannot verify hidden index flags; clear assume-unchanged or skip-worktree first
[1]
```

## Modified skip-worktree entry

```scrut
$ printf 'hidden edit\n' > tracked.txt && "${CHECK_EDIT_WORKTREE_BIN}" 2>&1
check-edit-worktree: --edit cannot verify hidden index flags; clear assume-unchanged or skip-worktree first
[1]
```

## Refusal preserves skip-worktree content and flags

```scrut
$ cat tracked.txt && git ls-files -v -- tracked.txt
hidden edit
S tracked.txt
```

## Combined hidden flags

```scrut
$ git update-index --assume-unchanged tracked.txt && "${CHECK_EDIT_WORKTREE_BIN}" 2>&1
check-edit-worktree: --edit cannot verify hidden index flags; clear assume-unchanged or skip-worktree first
[1]
```

## Change introduced after before-capture

```scrut
$ git update-index --no-assume-unchanged tracked.txt \
>   && git update-index --no-skip-worktree tracked.txt \
>   && printf 'local edit\n' > tracked.txt \
>   && capture="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && export CAPTURE="${capture}" \
>   && "${CHECK_EDIT_WORKTREE_BIN}" \
>   && "${REVIEW_SCOPE_BIN}" --base HEAD > "${CAPTURE}" \
>   && printf 'concurrent edit\n' > tracked.txt \
>   && "${CHECK_EDIT_WORKTREE_BIN}" 2>&1
check-edit-worktree: --edit requires a clean working tree; commit or stash local changes first
[1]
```

## The earlier clean capture does not authorize discarding concurrent edits

```scrut
$ jq -c '[.staged, .unstaged, .untracked] | map(length)' "${CAPTURE}" \
>   && cat tracked.txt \
>   && git status --porcelain=v1
[0,0,0]
concurrent edit
 M tracked.txt
```

## Ordinary tracked filenames with newlines

```scrut
$ printf 'local edit\n' > tracked.txt \
>   && printf 'unusual name\n' > $'line\nbreak.txt' \
>   && git add tracked.txt $'line\nbreak.txt' \
>   && git commit -q -m 'record unusual filename' \
>   && "${CHECK_EDIT_WORKTREE_BIN}"
```

## Gitlink fixtures

The fixtures create local initialized checkouts directly. No transport, clone,
submodule initialization or network access is needed.

```scrut {fail_fast: true}
$ function gitlink_fixture() {
>   local parent="${FIXTURE}/${1}" registration="${2}" child_head;
>   mkdir -p "${parent}/module path" \
>     && git -C "${parent}" init -q --template= \
>     && git -C "${parent}" config user.name 'Test User' \
>     && git -C "${parent}" config user.email 'test@example.com' \
>     && git -C "${parent}" config commit.gpgsign false \
>     && git -C "${parent}/module path" init -q --template= \
>     && git -C "${parent}/module path" config user.name 'Test User' \
>     && git -C "${parent}/module path" config user.email 'test@example.com' \
>     && git -C "${parent}/module path" config commit.gpgsign false \
>     && printf 'original\n' > "${parent}/module path/child.txt" \
>     && git -C "${parent}/module path" add child.txt \
>     && git -C "${parent}/module path" commit -q -m child \
>     && child_head="$(git -C "${parent}/module path" rev-parse HEAD)" \
>     && git -C "${parent}" update-index --add --cacheinfo "160000,${child_head},module path" || return;
>   if test "${registration}" = registered; then
>     git config --file "${parent}/.gitmodules" submodule.sample.path 'module path' \
>       && git config --file "${parent}/.gitmodules" submodule.sample.url ./local-unused \
>       && git -C "${parent}" add .gitmodules || return;
>   fi;
>   git -C "${parent}" commit -q -m parent;
> }
```

## Registered initialized gitlink

```scrut
$ gitlink_fixture registered registered \
>   && (cd "${FIXTURE}/registered" && "${CHECK_EDIT_WORKTREE_BIN}") 2>&1
check-edit-worktree: --edit does not support gitlinks: module path
[1]
```

## Registered child with hidden edits

```scrut
$ git -C "${FIXTURE}/registered/module path" update-index --assume-unchanged child.txt \
>   && printf 'hidden child edit\n' > "${FIXTURE}/registered/module path/child.txt" \
>   && parent_state="$(git -C "${FIXTURE}/registered" status --porcelain=v1 --ignore-submodules=none)" \
>   && test -z "${parent_state}" \
>   && (cd "${FIXTURE}/registered" && "${CHECK_EDIT_WORKTREE_BIN}") 2>&1
check-edit-worktree: --edit does not support gitlinks: module path
[1]
```

## Gitlink outside a nested invocation directory

```scrut
$ mkdir "${FIXTURE}/registered/nested" \
>   && (cd "${FIXTURE}/registered/nested" && "${CHECK_EDIT_WORKTREE_BIN}") 2>&1
check-edit-worktree: --edit does not support gitlinks: module path
[1]
```

## Embedded initialized gitlink

```scrut
$ gitlink_fixture embedded embedded \
>   && (cd "${FIXTURE}/embedded" && "${CHECK_EDIT_WORKTREE_BIN}") 2>&1
check-edit-worktree: --edit does not support gitlinks: module path
[1]
```

## Embedded child with hidden edits

```scrut
$ git -C "${FIXTURE}/embedded/module path" update-index --assume-unchanged child.txt \
>   && printf 'hidden child edit\n' > "${FIXTURE}/embedded/module path/child.txt" \
>   && parent_state="$(git -C "${FIXTURE}/embedded" status --porcelain=v1 --ignore-submodules=none)" \
>   && test -z "${parent_state}" \
>   && (cd "${FIXTURE}/embedded" && "${CHECK_EDIT_WORKTREE_BIN}") 2>&1
check-edit-worktree: --edit does not support gitlinks: module path
[1]
```

## Refusal preserves both child indexes and content

```scrut
$ git -C "${FIXTURE}/registered/module path" ls-files -v -- child.txt \
>   && cat "${FIXTURE}/registered/module path/child.txt" \
>   && git -C "${FIXTURE}/embedded/module path" ls-files -v -- child.txt \
>   && cat "${FIXTURE}/embedded/module path/child.txt"
h child.txt
hidden child edit
h child.txt
hidden child edit
```

## Uninitialized registered gitlink

```scrut
$ gitlink_fixture empty registered \
>   && rm -r -- "${FIXTURE}/empty/module path" \
>   && mkdir -- "${FIXTURE}/empty/module path" \
>   && (cd "${FIXTURE}/empty" && "${CHECK_EDIT_WORKTREE_BIN}") 2>&1
check-edit-worktree: --edit does not support gitlinks: module path
[1]
```

## Gitlink path remains visible with a hidden parent-index flag

```scrut
$ git -C "${FIXTURE}/embedded" update-index --assume-unchanged 'module path' \
>   && (cd "${FIXTURE}/embedded" && "${CHECK_EDIT_WORKTREE_BIN}") 2>&1
check-edit-worktree: --edit does not support gitlinks: module path
[1]
```

## Unknown argument

```scrut
$ "${CHECK_EDIT_WORKTREE_BIN}" --edit 2>&1
Usage: check-edit-worktree
[2]
```

## Git failure never means clean

```scrut
$ cd "${FIXTURE}/.." && "${CHECK_EDIT_WORKTREE_BIN}" > "${FIXTURE}/failure.log" 2>&1
[1]
```

## Git failure explains the missing validity check

```scrut
$ tail -1 "${FIXTURE}/failure.log"
check-edit-worktree: could not read tracked-file flags
```

## Cleanup

```scrut
$ rm -r -- "${FIXTURE}" && rm -- "${CAPTURE}"
```
