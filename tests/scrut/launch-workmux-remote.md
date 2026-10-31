# Remote issue branch reuse

Use cached origin refs without fetching. The workmux and tmux commands are stubs;
real Git repositories verify tracking and commit selection independently of the Git stub.

## Helpers

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
> function prepare_remote_stubs() {
>   state="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
>   mkdir "${state}/bin"
>   cp "${WORKMUX_STUB_BIN}" "${state}/bin/workmux"
>   cp "${TMUX_STUB_BIN}" "${state}/bin/tmux"
>   cp "${WORKTREE_GIT_STUB_BIN}" "${state}/bin/git"
>   local tool
>   for tool in workmux tmux git; do
>     [[ "$(PATH="${state}/bin:${PATH}" command -v "${tool}")" == "${state}/bin/${tool}" ]] || return 1
>   done
> }
```

## Remote-only preflight strips the prefix and skips origin HEAD

```scrut
$ prepare_remote_stubs && env PATH="${state}/bin:${PATH}" STUB_GIT_REMOTE_BRANCHES=$'HEAD\nfeature/415-existing' bash "${LAUNCH_WORKMUX_BIN}" --resolve-issue-branch 415
feature/415-existing
```

## Local and remote copies of the same name count once

```scrut
$ env PATH="${state}/bin:${PATH}" STUB_GIT_BRANCHES='feature/415-existing' STUB_GIT_REMOTE_BRANCHES='feature/415-existing' bash "${LAUNCH_WORKMUX_BIN}" --resolve-issue-branch 415
feature/415-existing
```

## Different local and remote names remain ambiguous

```scrut
$ env PATH="${state}/bin:${PATH}" STUB_GIT_BRANCHES='fix/415-local' STUB_GIT_REMOTE_BRANCHES='feature/415-existing' bash "${LAUNCH_WORKMUX_BIN}" --resolve-issue-branch 415 2>&1
launch-workmux: issue 415 matches more than one branch:
  fix/415-local
  feature/415-existing
launch-workmux: pass an explicit branch name instead
[3]
```

## Remote-only launch creates tracking before workmux starts

```scrut
$ printf 'Body\n' | env PATH="${state}/bin:${PATH}" STUB_STATE="${state}" STUB_GIT_REMOTE_BRANCHES='feature/415-existing' bash "${LAUNCH_WORKMUX_BIN}" --generated-name fix/new --issue 415 --base main
Reusing branch feature/415-existing for issue 415
tracking: feature/415-existing -> origin/feature/415-existing
workmux add
branch: feature/415-existing
open-if-exists: true
base: main
prompt:
Body
prompt-file-exists: yes
```

## Explicit choice of a remote-only branch also tracks it

```scrut
$ prepare_remote_stubs && printf 'Body\n' | env PATH="${state}/bin:${PATH}" STUB_STATE="${state}" STUB_GIT_REMOTE_BRANCHES='feature/415-existing' bash "${LAUNCH_WORKMUX_BIN}" feature/415-existing
tracking: feature/415-existing -> origin/feature/415-existing
workmux add
branch: feature/415-existing
open-if-exists: true
prompt:
Body
prompt-file-exists: yes
```

## Tracking failure stops before workmux and cleans the prompt

```scrut
$ prepare_remote_stubs && mkdir "${state}/tmp" && status=0; printf 'Body\n' | env PATH="${state}/bin:${PATH}" TMPDIR="${state}/tmp" STUB_STATE="${state}" STUB_GIT_REMOTE_BRANCHES='feature/415-existing' STUB_GIT_FAIL=branch-track bash "${LAUNCH_WORKMUX_BIN}" --generated-name fix/new --issue 415 2>&1 || status=$?; test "${status}" = 1 && test ! -e "${state}/workmux_called" && test -z "$(ls -A "${state}/tmp")" && echo 'stopped and cleaned'
Reusing branch feature/415-existing for issue 415
git: fatal: cannot create tracking branch
stopped and cleaned
```

## Local ref inspection errors stop before workmux

```scrut
$ status=0; printf 'Body\n' | env PATH="${state}/bin:${PATH}" STUB_STATE="${state}" STUB_GIT_REMOTE_BRANCHES='feature/415-existing' STUB_GIT_FAIL=show-ref bash "${LAUNCH_WORKMUX_BIN}" --generated-name fix/new --issue 415 2>&1 || status=$?; test "${status}" = 128 && test ! -e "${state}/workmux_called" && echo stopped
Reusing branch feature/415-existing for issue 415
git: fatal: cannot read refs
stopped
```

## Real Git fixture has remote history distinct from main

```scrut {fail_fast: true}
$ real="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && git init --quiet --bare "${real}/origin.git" && git init --quiet --initial-branch=main "${real}/seed" && git -C "${real}/seed" config user.name Fixture && git -C "${real}/seed" config user.email fixture@example.invalid && git -C "${real}/seed" commit --quiet --allow-empty -m base && git -C "${real}/seed" remote add origin "${real}/origin.git" && git -C "${real}/seed" push --quiet origin main && git -C "${real}/origin.git" symbolic-ref HEAD refs/heads/main && git -C "${real}/seed" switch --quiet -c feature/415-existing && git -C "${real}/seed" commit --quiet --allow-empty -m remote && git -C "${real}/seed" push --quiet origin feature/415-existing && git clone --quiet "${real}/origin.git" "${real}/local" && git -C "${real}/local" remote add other "${real}/origin.git" && git -C "${real}/local" fetch --quiet other && git -C "${real}/local" update-ref refs/remotes/other/feature/415-existing refs/remotes/origin/main && echo ready
ready
```

## Preflight reads cached origin without creating a branch

```scrut
$ (cd "${real}/local" && bash "${LAUNCH_WORKMUX_BIN}" --resolve-issue-branch 415 && test "$(git for-each-ref --format='%(refname)' refs/heads/feature/415-existing)" = '' && echo 'no local branch')
feature/415-existing
no local branch
```

## Launch tracks origin despite another remote and an explicit base

The origin becomes unreachable after fetching, so any implicit fetch would fail.
Only workmux and tmux are stubbed, and the workmux stub opens a real worktree
using the branch prepared by the launcher.

```scrut
$ mkdir "${real}/bin" && cp "${WORKMUX_STUB_BIN}" "${real}/bin/workmux" && cp "${TMUX_STUB_BIN}" "${real}/bin/tmux" && test "$(PATH="${real}/bin:${PATH}" command -v workmux)" = "${real}/bin/workmux" && test "$(PATH="${real}/bin:${PATH}" command -v tmux)" = "${real}/bin/tmux" && git -C "${real}/local" remote set-url origin "${real}/unreachable.git" && (cd "${real}/local" && printf 'Body\n' | env -u TMUX PATH="${real}/bin:${PATH}" STUB_WORKMUX_REAL_WORKTREE="${real}/worktree" bash "${LAUNCH_WORKMUX_BIN}" --generated-name fix/new --issue 415 --base main --await-completion > "${real}/launch.log") && git -C "${real}/worktree" rev-parse --abbrev-ref '@{upstream}' && test "$(git -C "${real}/worktree" rev-parse HEAD)" = "$(git -C "${real}/local" rev-parse refs/remotes/origin/feature/415-existing)" && test "$(git -C "${real}/worktree" rev-parse HEAD)" != "$(git -C "${real}/local" rev-parse main)" && echo 'remote commit retained'
origin/feature/415-existing
remote commit retained
```

## Local branch wins over a remote copy with different history

```scrut
$ git -C "${real}/local" branch feature/416-local main && git -C "${real}/local" update-ref refs/remotes/origin/feature/416-local refs/remotes/origin/feature/415-existing && (cd "${real}/local" && printf 'Body\n' | env -u TMUX PATH="${real}/bin:${PATH}" STUB_WORKMUX_REAL_WORKTREE="${real}/local-worktree" bash "${LAUNCH_WORKMUX_BIN}" --generated-name fix/new --issue 416 --await-completion > "${real}/local.log") && test "$(git -C "${real}/local-worktree" rev-parse HEAD)" = "$(git -C "${real}/local" rev-parse main)" && test "$(git -C "${real}/local" config --get branch.feature/416-local.remote || test "$?" = 1)" = '' && echo 'local commit and configuration retained'
local commit and configuration retained
```

## Cleanup

```scrut
$ rm -r -- "${real}" "${state}"
```
