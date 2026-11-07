# Checked plant guards, partition 15

Each mutation has its own baseline, named detector and restored check.

```scrut {output_stream: stderr}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
> uv run --no-project "${REPO_ROOT}/tests/run_checked_budget.py" checked-plant-guards-15.md \
>   "${CHECKED_PLANT_TESTS_BIN}" \
>   RunnerTests.test_runner_guards_detect_their_own_plants -q
----------------------------------------------------------------------
Ran 1 test in *s (glob)

OK
```
