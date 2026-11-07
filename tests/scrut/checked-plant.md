# Checked plant runner

Behavior checks run once under the document backstop. Each supervised call has
its own inclusive limit.

```scrut {output_stream: stderr}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
> uv run --no-project "${REPO_ROOT}/tests/run_checked_budget.py" checked-plant.md \
>   "${CHECKED_PLANT_TESTS_BIN}" -q
----------------------------------------------------------------------
Ran 45 tests in *s (glob)

OK
```
