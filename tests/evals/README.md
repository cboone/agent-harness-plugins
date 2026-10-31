# Skill evaluations

These opt-in checks call the existing authenticated Codex CLI. They are separate from CI.

## Trim-text branch scope

The [runner](trim-text-scopes.py) consumes [scenario data](../data/trim-text-default-scopes.json), checks five scope states, and verifies changed-unit preservation in a temporary Git fixture. It uses gpt-6.1-sol at low effort in read-only sandboxes. Git signing must work to sign fixture commits. Outputs remain in the printed directory.

```bash
uv run --no-project --python 3.13 tests/evals/trim-text-scopes.py \
  --out-dir "$(mktemp -d "${TMPDIR:-/tmp}/trim-text-eval.XXXXXX")"
```

`--scope-reply PATH` checks an existing scope reply without model calls. `--prose-only` runs only the Git prose check.

## Anti-pattern edit mode

The [runner](anti-patterns-edit.py) executes one bounded edit-mode run in a disposable Git repository. Its committed range changes the endpoint contract and introduces a missing module. The checks require both a tracked sibling correction and a new untracked sibling to reach the measured fix diff and final review inputs. Existing assertions, HEAD, refs and the index must stay unchanged. Exact phase results, captures, commands and logs remain in the output directory.

Requires an existing authenticated Codex CLI, Node.js with its test runner, Git, `jq` and working Git signing. The run uses `gpt-6.1-sol` at `medium` effort with the CLI's normal execution permissions; it passes no sandbox override. Only the disposable fixture and external captures are authorized for writes. The two report-only phases use the documented current-session fallback with read-only instructions, not a sandbox. It does not contact GitHub, install dependencies or alter user configuration. This opt-in run is separate from `make test-all` and CI.

```bash
uv run --no-project tests/evals/anti-patterns-edit.py \
  --out-dir "$(mktemp -d "${TMPDIR:-/tmp}/anti-pattern-edit-eval.XXXXXX")"
```

`--check-only` validates a saved `--out-dir` without model calls. The runner refuses optimized Python so its assertions cannot disappear. The runner refuses nonempty output directories for live attempts. Coverage is checked from captured Git trees, the actual final input manifest and phase results; those artifacts do not prove every future model run will follow the workflow.
