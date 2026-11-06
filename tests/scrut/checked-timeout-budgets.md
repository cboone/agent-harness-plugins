# Checked supervision budgets

```scrut {output_stream: stderr}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
> uv run --no-project "${REPO_ROOT}/tests/run_checked_budget.py" checked-timeout-budgets.md \
>   uv run --no-project "${REPO_ROOT}/tests/checked_timeout_budget_test.py" -q
----------------------------------------------------------------------
Ran 23 tests in *s (glob)

OK
```
