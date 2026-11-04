# Checked gate runner

## Ordered checks, refusal receipts, strict pipelines and verification

```scrut {output_stream: stderr}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash" &&
> uv run --no-project "${REPO_ROOT}/tests/checked_gate_test.py" GateTests -q
----------------------------------------------------------------------
Ran 39 tests in *s (glob)

OK
```
