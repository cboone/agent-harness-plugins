# Notification fixture load contracts

A backend held at a startup barrier must still deliver before the fixture clock
advances. The grace-period checks count injected ticks instead of elapsed time.
The driver retains detached failures, and snapshot prefix readers drain a writer
that continues beyond the displayed lines.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

```scrut
$ uv run --no-project "${NOTIFICATION_LOAD_TESTS_BIN}" 2>&1 | sed -E 's/Ran [0-9]+ tests in [0-9.]+s/Ran tests/' # error-output-allow: testcase asserts unittest diagnostics and normalizes measured runtime
......................
----------------------------------------------------------------------
Ran tests

OK
```
