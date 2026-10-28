# Skill evaluations

These opt-in checks call the existing authenticated Codex CLI. They are separate from CI.

## Trim-text branch scope

The [runner](trim-text-scopes.py) consumes [scenario data](../data/trim-text-default-scopes.json), checks five scope states, and verifies changed-unit preservation in a temporary Git fixture. It uses gpt-6.1-sol at low effort in read-only sandboxes. Git signing must work to sign fixture commits. Outputs remain in the printed directory.

```bash
uv run --no-project --python 3.13 tests/evals/trim-text-scopes.py \
  --out-dir "$(mktemp -d "${TMPDIR:-/tmp}/trim-text-eval.XXXXXX")"
```

`--scope-reply PATH` checks an existing scope reply without model calls. `--prose-only` runs only the Git prose check.
