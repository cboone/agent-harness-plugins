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

## Comment alias and mixed scope

The same runner consumes [comment scope scenarios](../data/trim-scope.json) with `--comments-only`. It materializes a signed Git fixture, invokes the alias and its direct `trim-text` equivalents independently, and checks exact eligible units, per-file profiles, ticketless TODO flags, and unchanged files, index and HEAD. A mixed prose/comment branch case checks both profiles together. Expected results stay outside model prompts; suggested wording is not compared.

```bash
uv run --no-project --python 3.13 tests/evals/trim-text-scopes.py --comments-only \
  --out-dir "$(mktemp -d "${TMPDIR:-/tmp}/trim-comments-eval.XXXXXX")"
```

`--comment-replies PATH` checks saved `comments-alias-reply.json`, `comments-equivalent-reply.json` and `comments-mixed-reply.json` without model calls. It checks reported scope and classification only; unchanged Git state is checked during live evaluation.

## Moved notes and declined proposals

`--moved-only` extends the same runner with [a moved-docstring fixture](../data/trim-moved-comments.json). A branch moves and copies a stale dated link-format note. The evaluator checks the alias, direct comment profile and pasted prose independently, using supplied dry-run proposals. Stale-note rewrites must be accepted; a supported warning must have current-code evidence; each declined proposal must have a location and reason. Live runs also verify unchanged files, index and HEAD.

```bash
uv run --no-project tests/evals/trim-text-scopes.py --moved-only \
  --out-dir "$(mktemp -d "${TMPDIR:-/tmp}/trim-moved-eval.XXXXXX")"
```

`--moved-replies PATH` checks saved `moved-alias-reply.json`, `moved-direct-reply.json` and `moved-prose-reply.json` without model calls. `--skill-root PATH` selects an isolated copy of the canonical skill tree for policy plants. Live evaluations use `gpt-6.1-sol`, low effort, window `872000`, and a read-only sandbox. The response schema describes report fields without supplying expected decisions. This opt-in check measures proposal checking and reporting on these cases; it does not prove all future model runs will comply or execute apply-mode writes.

The moved-note cases include an opaque redirect callback whose provider's accepted URL formats cannot be established from the supplied code. The report must flag that check as unresolved instead of treating the warning as confirmed.

`--parents-only` supplies hypothetical successful trim results to the commit and PR skills' final reporting steps. Both reports must relay a decline's location, reason and supporting evidence. It does not execute commits, pushes or GitHub writes.

```bash
uv run --no-project tests/evals/trim-text-scopes.py --parents-only \
  --out-dir "$(mktemp -d "${TMPDIR:-/tmp}/trim-parent-eval.XXXXXX")"
```

`--parent-replies PATH` checks saved `parent-commit-reply.json` and `parent-pr-reply.json` without model calls. The same `--skill-root` option supports isolated caller-policy plants.
