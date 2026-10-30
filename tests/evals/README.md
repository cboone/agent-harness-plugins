# Skill evaluations

These opt-in checks call the existing authenticated Codex CLI. They are separate from CI.

## Trim-text branch scope

The [runner](trim-text-scopes.py) consumes [scenario data](../data/trim-text-default-scopes.json), checks five scope states, and verifies changed-unit preservation in a temporary Git fixture. It uses gpt-6.1-sol at low effort in read-only sandboxes. Git signing must work to sign fixture commits. Outputs remain in the printed directory.

```bash
uv run --no-project --python 3.13 tests/evals/trim-text-scopes.py \
  --out-dir "$(mktemp -d "${TMPDIR:-/tmp}/trim-text-eval.XXXXXX")"
```

`--scope-reply PATH` checks an existing scope reply without model calls. `--prose-only` runs only the Git prose check.

## Comment alias and mixed scope

The same runner consumes [comment scope scenarios](../data/trim-scope.json) with `--comments-only`. It materializes a signed Git fixture, invokes the alias and its direct `trim-text` equivalents independently, and checks exact eligible units, per-file profiles, ticketless TODO flags, and unchanged files, index and HEAD. A mixed prose/comment branch case checks both profiles together. Expected results stay outside model prompts; suggested wording is not compared.

```bash
uv run --no-project --python 3.13 tests/evals/trim-text-scopes.py --comments-only \
  --out-dir "$(mktemp -d "${TMPDIR:-/tmp}/trim-comments-eval.XXXXXX")"
```

`--comment-replies PATH` checks saved `comments-alias-reply.json`, `comments-equivalent-reply.json` and `comments-mixed-reply.json` without model calls. It checks reported scope and classification only; unchanged Git state is checked during live evaluation.
