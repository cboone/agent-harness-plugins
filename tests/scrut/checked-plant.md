# Checked plant runner

## Real plants, negative restart check and publication gate

The committed behavior suite checks each runner phase and refuses failed,
unrun, stale or incomplete evidence without changing existing records.

```scrut {output_stream: stderr}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
> CHECKED_PLANT_GUARD_PART=1 "${CHECKED_PLANT_TESTS_BIN}" -q
----------------------------------------------------------------------
Ran 43 tests in *s (glob)

OK
```
