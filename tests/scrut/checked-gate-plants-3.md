# Checked gate restart plants, partition 3

## Real source plants exercise restart boundaries through checked-plant

```scrut {output_stream: stderr}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash" &&
> CHECKED_GATE_GUARD_PART=3 uv run --no-project "${REPO_ROOT}/tests/checked_gate_test.py" PlantTests -q
----------------------------------------------------------------------
Ran 1 test in *s (glob)

OK
```
