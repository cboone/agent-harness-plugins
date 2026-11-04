# Checked plant guards, partition 4

Seven declared mutations run through the checked runner. The suite verifies
that all four partitions cover the complete mutation list exactly once.

```scrut {output_stream: stderr}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
> CHECKED_PLANT_GUARD_PART=4 "${CHECKED_PLANT_TESTS_BIN}" \
>   RunnerTests.test_runner_guards_detect_their_own_plants -q
----------------------------------------------------------------------
Ran 1 test in *s (glob)

OK
```
