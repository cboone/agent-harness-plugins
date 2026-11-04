# Heavy suite locking

The fixture refuses to run unless suite-lock and Scrut resolve to its private
stubs. No case takes the machine's real lock or runs the full suite.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

## Default full run takes the lock

```scrut
$ "${HEAVY_SUITE_CASE_BIN}" full
ran tests/scrut/a.md
Result: 1 document(s) with 1 testcase(s): 1 succeeded, 0 failed and 0 skipped
lock calls: 1
```

## Directory spelling takes the lock

```scrut
$ "${HEAVY_SUITE_CASE_BIN}" directory
ran */tests/scrut/../scrut/a.md (glob)
Result: 1 document(s) with 1 testcase(s): 1 succeeded, 0 failed and 0 skipped
lock calls: 1
```

## Empty path selects the default full run

```scrut
$ "${HEAVY_SUITE_CASE_BIN}" empty
ran tests/scrut/a.md
Result: 1 document(s) with 1 testcase(s): 1 succeeded, 0 failed and 0 skipped
lock calls: 1
```

## Named document stays direct

```scrut
$ "${HEAVY_SUITE_CASE_BIN}" named
ran tests/scrut/a.md
Result: 1 document(s) with 1 testcase(s): 1 succeeded, 0 failed and 0 skipped
lock calls: 0
```

## Listing stays direct

```scrut
$ "${HEAVY_SUITE_CASE_BIN}" list
tests/scrut/a.md
lock calls: 0
```

## Help stays direct

```scrut
$ "${HEAVY_SUITE_CASE_BIN}" help | tail -1
lock calls: 0
```

## Missing override falls back

```scrut
$ "${HEAVY_SUITE_CASE_BIN}" missing
ran tests/scrut/a.md
Result: 1 document(s) with 1 testcase(s): 1 succeeded, 0 failed and 0 skipped
lock calls: 0
```

## Installed default is discovered

```scrut
$ "${HEAVY_SUITE_CASE_BIN}" default
ran tests/scrut/a.md
Result: 1 document(s) with 1 testcase(s): 1 succeeded, 0 failed and 0 skipped
lock calls: 1
```

## Missing installation falls back

```scrut
$ "${HEAVY_SUITE_CASE_BIN}" missing-default
ran tests/scrut/a.md
Result: 1 document(s) with 1 testcase(s): 1 succeeded, 0 failed and 0 skipped
lock calls: 0
```

## Locked command preserves output, status, arguments and environment

```scrut
$ "${HEAVY_SUITE_CASE_BIN}" passthrough 2>&1
stdout: argument with spaces, inherited value
stderr
lock calls: 1
[7]
```

## Direct fallback preserves output and status

```scrut
$ "${HEAVY_SUITE_CASE_BIN}" fallback-output 2>&1
stdout: argument with spaces, inherited value
stderr
lock calls: 0
[7]
```

## Stdout and stderr remain separate

```scrut
$ "${HEAVY_SUITE_CASE_BIN}" streams
stdout: out
stderr: err
lock calls: 1
```

## Nested full runner delegates ownership to suite-lock

```scrut
$ "${HEAVY_SUITE_CASE_BIN}" nested
ran tests/scrut/a.md
Result: 1 document(s) with 1 testcase(s): 1 succeeded, 0 failed and 0 skipped
lock calls: 2
```

## Aggregate target wraps all checks

Replacing the recursive Make command with echo checks the public target's lock
and selected goals without running another suite.

```scrut
$ "${HEAVY_SUITE_CASE_BIN}" make
bin/run-heavy-suite echo lint validate test-scrut
lint validate test-scrut
lock calls: 1
```

## Directory snapshot updates and verification take the lock

```scrut
$ "${HEAVY_SUITE_CASE_BIN}" update-full
update and verification ran
lock calls: 2
```

## Named snapshot updates stay direct

```scrut
$ "${HEAVY_SUITE_CASE_BIN}" update-named
update and verification ran
lock calls: 0
```
