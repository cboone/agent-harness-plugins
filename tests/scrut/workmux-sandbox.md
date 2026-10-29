# Workmux harness and resource matrix

These tests cover both harness identities and the documented Bash launch path
plus direct executable invocation. The fixture refuses to invoke any helper
unless workmux, tmux, gh and git resolve to its committed stubs. Live sandbox
matching results are recorded separately in the sandbox exclusions ledger.

## Test environment

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

## Both harnesses can compose, launch and record claims

```scrut
$ for harness in 'Claude Code' Codex; do for invocation in bash executable; do "${WORKMUX_SANDBOX_CASE_BIN}" "${harness}" "${invocation}" success || exit 1; done; done
Claude Code bash: compose, launch and claim passed
Claude Code executable: compose, launch and claim passed
Codex bash: compose, launch and claim passed
Codex executable: compose, launch and claim passed
```

## Both harness identities retain every resource failure through either launch form

```scrut
$ for harness in 'Claude Code' Codex; do for invocation in bash executable; do for resource in log socket config claim; do "${WORKMUX_SANDBOX_CASE_BIN}" "${harness}" "${invocation}" "${resource}" check || exit 1; done; done; done
Claude Code bash log: resource, harness and failure retained
Claude Code bash socket: resource, harness and failure retained
Claude Code bash config: resource, harness and failure retained
Claude Code bash claim: resource, harness and failure retained
Claude Code executable log: resource, harness and failure retained
Claude Code executable socket: resource, harness and failure retained
Claude Code executable config: resource, harness and failure retained
Claude Code executable claim: resource, harness and failure retained
Codex bash log: resource, harness and failure retained
Codex bash socket: resource, harness and failure retained
Codex bash config: resource, harness and failure retained
Codex bash claim: resource, harness and failure retained
Codex executable log: resource, harness and failure retained
Codex executable socket: resource, harness and failure retained
Codex executable config: resource, harness and failure retained
Codex executable claim: resource, harness and failure retained
```

## Alternate failure forms retain context without prescribing approval

```scrut
$ for scenario in log-home log-relative log-no-home config-load generic generic-lower generic-typed auth disk occupied temp-prompt temp-raw temp-state temp-read temp-render; do "${WORKMUX_SANDBOX_CASE_BIN}" Codex bash "${scenario}" check || exit 1; done
Codex bash log-home: resource, harness and failure retained
Codex bash log-relative: resource, harness and failure retained
Codex bash log-no-home: resource, harness and failure retained
Codex bash config-load: resource, harness and failure retained
Codex bash generic: resource, harness and failure retained
Codex bash generic-lower: resource, harness and failure retained
Codex bash generic-typed: resource, harness and failure retained
Codex bash auth: resource, harness and failure retained
Codex bash disk: resource, harness and failure retained
Codex bash occupied: resource, harness and failure retained
Codex bash temp-prompt: resource, harness and failure retained
Codex bash temp-raw: resource, harness and failure retained
Codex bash temp-state: resource, harness and failure retained
Codex bash temp-read: resource, harness and failure retained
Codex bash temp-render: resource, harness and failure retained
```

## Completed standalone fixtures remove their own directories

```scrut
$ (control="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"; TMPDIR="${control}" "${WORKMUX_SANDBOX_CASE_BIN}" Codex bash success || exit 1; trap 'rm -r -- "${control}"' EXIT; test -z "$(ls -A "${control}")" && echo 'fixture cleanup passed')
Codex bash: compose, launch and claim passed
fixture cleanup passed
```

## Harness labels handle unknown, nested and explicit callers

```scrut
$ env -u CODEX_THREAD_ID -u CLAUDECODE -u WORKMUX_CALLER_HARNESS bash -c 'source "$1"; workmux_caller_harness; printf "\n"' fixture "${WORKMUX_RESOURCE_DIAGNOSTICS_BIN}"
unidentified harness
```

```scrut
$ env CODEX_THREAD_ID=fixture CLAUDECODE=1 bash -c 'source "$1"; workmux_caller_harness; printf "\n"' fixture "${WORKMUX_RESOURCE_DIAGNOSTICS_BIN}"
Claude Code/Codex (nested environment)
```

```scrut
$ env CLAUDECODE=1 WORKMUX_CALLER_HARNESS=Codex bash -c 'source "$1"; workmux_caller_harness; printf "\n"' fixture "${WORKMUX_RESOURCE_DIAGNOSTICS_BIN}"
Codex
```

```scrut
$ env CODEX_THREAD_ID=fixture WORKMUX_CALLER_HARNESS='Claude Code' bash -c 'source "$1"; workmux_caller_harness; printf "\n"' fixture "${WORKMUX_RESOURCE_DIAGNOSTICS_BIN}"
Claude Code
```

```scrut
$ env CODEX_THREAD_ID=fixture WORKMUX_CALLER_HARNESS=invalid bash -c 'source "$1"; workmux_caller_harness; printf "\n"' fixture "${WORKMUX_RESOURCE_DIAGNOSTICS_BIN}"
Codex
```

## Unknown check modes are refused

```scrut
$ "${WORKMUX_SANDBOX_CASE_BIN}" Codex bash success typo 2>&1
matrix: unknown mode
[1]
```

## A failed matrix assertion retains child diagnostics before cleanup

```scrut
$ "${WORKMUX_SANDBOX_CASE_BIN}" Codex bash ordinary check 2>&1
Generated branch name: feature/42-test
workmux: unsupported configuration
launch-workmux: workmux add for feature/42-test failed with status 2
matrix: unknown denial scenario
[1]
```

## A tool outside the expected stub directory is refused

```scrut
$ "${WORKMUX_SANDBOX_CASE_BIN}" Codex bash guard 2>&1
matrix: refusing to run: gh is not the fixture stub
[1]
```

## Unknown harness, invocation and scenario values are refused

```scrut
$ "${WORKMUX_SANDBOX_CASE_BIN}" unknown bash success 2>&1
matrix: unknown harness
[1]
```

```scrut
$ "${WORKMUX_SANDBOX_CASE_BIN}" Codex unknown success 2>&1
matrix: unknown invocation
[1]
```

```scrut
$ "${WORKMUX_SANDBOX_CASE_BIN}" Codex bash unknown 2>&1
matrix: unknown scenario
[1]
```

## Workmux log denial identifies Claude Code and the configured path

```scrut
$ "${WORKMUX_SANDBOX_CASE_BIN}" 'Claude Code' bash log 2>&1
Generated branch name: feature/42-test
initializing rolling file appender failed: failed to create initial log file: PermissionDenied
launch-workmux: Claude Code: operation failed for workmux log FIXTURE/state/workmux/workmux.log; see the original error for the cause.
launch-workmux: workmux add for feature/42-test failed with status 101
exit: 1
```

## Socket denial retains the resource and names Codex

```scrut
$ "${WORKMUX_SANDBOX_CASE_BIN}" Codex executable socket 2>&1
Generated branch name: feature/42-test
error connecting to FIXTURE/tmux/socket (Operation not permitted)
launch-workmux: Codex: operation failed for tmux socket named in the command output; see the original error for the cause.
launch-workmux: workmux add for feature/42-test failed with status 1
exit: 1
```

## A gh config failure is identified separately

```scrut
$ "${WORKMUX_SANDBOX_CASE_BIN}" 'Claude Code' executable config 2>&1
Generated branch name: feature/42-test
failed to read configuration: open FIXTURE/gh/hosts.yml: operation not permitted
launch-workmux: Claude Code: operation failed for GitHub CLI config named in the command output; see the original error for the cause.
launch-workmux: workmux add for feature/42-test failed with status 1
exit: 1
```

## An unrelated launch failure is not labeled a resource denial

```scrut
$ "${WORKMUX_SANDBOX_CASE_BIN}" Codex bash ordinary 2>&1
Generated branch name: feature/42-test
workmux: unsupported configuration
launch-workmux: workmux add for feature/42-test failed with status 2
exit: 1
```

## Claim failures retain the path and harness

```scrut
$ "${WORKMUX_SANDBOX_CASE_BIN}" Codex bash claim 2>&1
manage-resource-claims: Codex: operation failed for claim lock FIXTURE/claims.json.lock; see the original error for the cause.
manage-resource-claims: cannot create FIXTURE/claims.json.lock; check that FIXTURE is writable and that nothing else occupies that path
exit: 1
```
