# Workmux harness and resource matrix

These tests cover both harness identities and the documented Bash launch path
plus direct executable invocation. The fixture refuses to invoke any helper
unless workmux, tmux, gh and git resolve to its committed stubs. Live sandbox
matching results are recorded separately in the sandbox exclusions ledger.

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

## A real tool in place of a stub is refused

```scrut
$ "${WORKMUX_SANDBOX_CASE_BIN}" Codex bash guard 2>&1
matrix: refusing to run: gh is not the fixture stub
[1]
```

## Workmux log denial identifies Claude Code and the configured path

```scrut
$ "${WORKMUX_SANDBOX_CASE_BIN}" 'Claude Code' bash log 2>&1
Generated branch name: feature/42-test
initializing rolling file appender failed: failed to create initial log file: PermissionDenied
launch-workmux: Claude Code: access failed for workmux log FIXTURE/state/workmux/workmux.log; check the active sandbox and filesystem/socket permissions. Use the host approval flow for this command only when authorized; do not exclude bash or change user settings.
launch-workmux: workmux add for feature/42-test failed with status 101
exit: 1
```

## Socket denial retains the resource and names Codex

```scrut
$ "${WORKMUX_SANDBOX_CASE_BIN}" Codex executable socket 2>&1
Generated branch name: feature/42-test
error connecting to FIXTURE/tmux/socket (Operation not permitted)
launch-workmux: Codex: access failed for tmux socket named in the command output; check the active sandbox and filesystem/socket permissions. Use the host approval flow for this command only when authorized; do not exclude bash or change user settings.
launch-workmux: workmux add for feature/42-test failed with status 1
exit: 1
```

## A gh config failure is identified separately

```scrut
$ "${WORKMUX_SANDBOX_CASE_BIN}" 'Claude Code' executable config 2>&1
Generated branch name: feature/42-test
failed to read configuration: open FIXTURE/gh/hosts.yml: operation not permitted
launch-workmux: Claude Code: access failed for GitHub CLI config named in the command output; check the active sandbox and filesystem/socket permissions. Use the host approval flow for this command only when authorized; do not exclude bash or change user settings.
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
manage-resource-claims: Codex: access failed for claim lock FIXTURE/claims.json.lock; check the active sandbox and filesystem/socket permissions. Use the host approval flow for this command only when authorized; do not exclude bash or change user settings.
manage-resource-claims: cannot create FIXTURE/claims.json.lock; check that FIXTURE is writable and that nothing else occupies that path
exit: 1
```
