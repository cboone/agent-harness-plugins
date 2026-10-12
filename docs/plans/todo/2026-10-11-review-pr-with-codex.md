# Add the review-pr-with-codex skill (#603)

## Context

`review-until-clean` uses Codex as a reviewer, but it runs one general review per round inside a fix loop. There is no catalog skill for a single, thorough, multi-aspect review by Codex, comparable to what `pr-review-toolkit:review-pr` produces in Claude Code. Issue #603 settles the design: six aspects adapted from `pr-review-toolkit`, two entry points (Codex subagents inside Codex CLI, parallel `codex exec` runs inside Claude Code), read-only review aspects, a gated `simplify` step with write access, and per-run model and effort defaults.

## Approach

One new plugin, `plugins/review-pr-with-codex/` at `1.0.0`, with two bundled helpers so the failure checks are structural rather than prose the agent must remember:

- `review-scope`: a byte-identical copy of `plugins/review-until-clean/scripts/review-scope`. It already computes the four scope buckets (committed since merge base, staged, unstaged, untracked), the symlink-relevant untracked list, and a content-addressed snapshot. The snapshot doubles as the read-only check: it must be unchanged after every review aspect, on both entry points. Rule 18 forbids cross-plugin script references, so it is copied, with a scrut drift testcase like the existing `resolve-copilot-threads` pair.
- `codex-aspects` (new Bash script, `write-bash-scripts` conventions, macOS Bash 3.2 compatible like `review-scope`). Subcommands:
  - `schema`: prints the findings JSON Schema: `aspect` (echoed, must match), `summary`, `strengths[]`, `findings[]` with `severity` (`critical|important|suggestion`), `file`, `line`, `title`, `detail`, `fix`, `confidence`. Strict (all properties required, `additionalProperties: false`), no lookaround patterns, per `backends.md`.
  - `prompt --aspect NAME --scope FILE`: renders one aspect prompt from `references/aspects/NAME.md` (found relative to the script's own location, like `publish-report-board`'s templates), the scope block (buckets, untracked symlinks as `path -> target`, empty buckets omitted), the guideline files to read (`AGENTS.md` and `CLAUDE.md` chains), and the output contract. Used by both entry points, so the Codex subagent and the `codex exec` run get identical instructions.
  - `run --aspect NAME [--aspect NAME...] --scope FILE --out-dir DIR [--model M] [--effort E]`: launches one `codex exec` per aspect in parallel (`&` and `wait`), each with `--sandbox read-only`, or `workspace-write` for `simplify`, which must run alone, `--ephemeral`, `--output-schema`, `-o`, `-m`, `-c model_reasoning_effort=…`, and `< /dev/null`. `DIR` must be outside the working tree (the script refuses a path inside it). Prints one JSON status object per aspect: `ok` or `failed` with the reason (non-zero exit, missing file, empty file, schema mismatch, wrong `aspect` or `reviewed` echo). Exit status 3 when any aspect failed.
  - `validate --aspect NAME --scope FILE OUTPUT`: the same output checks, for a reply the Codex entry point saved from a subagent.
  - `changes --before FILE --after FILE`: diff the content trees of two `review-scope` results and report exactly which paths changed and which of them were outside the first scope. It detects lasting changes made during the review aspects, though not index-only changes, ignored untracked files or reverted edits, and measures what `simplify` changed, so the report's list of `simplify` edits is measured, not taken from Codex's word.

### Skill workflow (`skills/review-pr-with-codex/SKILL.md`)

Arguments mirror `review-pr`: aspect names (`code errors tests comments types simplify`) or `all` (default), plus `--base <ref>`, `--model <model>` (default `gpt-6.1-sol`) and `--effort <level>` (default `medium`). Steps:

1. Resolve the scope with `review-scope`; stop on an empty scope, and on `committed_covered: false` follow `review-until-clean`'s handling.
1. Decide applicable aspects from the diff (`code` always; `errors`, `tests`, `comments`, `types` per the issue's table, with the criteria in `references/aspects.md`). Record each skipped aspect and why.
1. Pick the entry point by which way of reaching a Codex model the session has: a session running on Codex that can spawn Codex subagents (`spawn_agent` in Codex CLI) uses the subagent path, never another harness's subagents, which run its own models; otherwise `codex exec` through `codex-aspects run`. Check `codex` availability first on the exec path; authentication failures surface as failed aspect runs.
1. Run the review aspects in parallel, read-only. Subagent path: each subagent's task is `codex-aspects prompt` output plus explicit read-only instructions, passing model and effort when the spawn tool accepts them (otherwise the report says the session's settings were used); save each reply and run `codex-aspects validate`. When subagents are unavailable, run aspects one after another in the session and say so in the report.
1. Recompute the snapshot. If it moved, report which aspect could have written, and treat the run as failed for the read-only invariant.
1. Any failed or empty aspect is reported as failed, never clean, and blocks the "no Critical" claim.
1. `simplify` runs only when requested, every other selected aspect succeeded, and none reported Critical. Exec path: `codex-aspects run --aspect simplify`; subagent path: one subagent with write instructions. Bracket it with `review-scope` and `changes`.
1. Merge into the `review-pr` report: Critical, Important, Suggestions (each `[aspect] description [file:line]`), Strengths, Recommended action, plus an "Aspect runs" table (aspect, status, skip reason, entry point, model, effort, parallel or sequential) and a "Simplify changes" section. Output in chat; nothing is saved or pushed.

### References

- `references/aspects/{code,errors,tests,comments,types,simplify}.md`: the six `pr-review-toolkit` agents adapted to the output schema, each with a modification notice. `code` points at `AGENTS.md`/`CLAUDE.md`. Review aspects state they are read-only; `simplify` limits edits to in-scope files and must preserve behavior.
- `references/aspects.md`: applicability criteria and argument parsing.
- `references/invocation.md`: the exec rules, citing `review-until-clean`'s `backends.md` reasoning (why plain `codex exec`, `< /dev/null`, outside-tree outputs, every failure signal), and the subagent path's signals (non-empty reply plus schema validation; no exit status).

### Licensing

`pr-review-toolkit` is Apache-2.0 (Anthropic, `anthropics/claude-plugins-official`) with no upstream NOTICE. The plugin ships `LICENSE-APACHE` (full text), a `NOTICE` naming the source, its license and that the aspect prompts were modified, and uses the SPDX expression `MIT AND Apache-2.0` in both `plugin.json` and the catalog entry (no validator restricts the value). The mirrors copy the plugin directory whole, so both files reach `dist/`.

## Files

- New: `plugins/review-pr-with-codex/{.claude-plugin/plugin.json,README.md,NOTICE,LICENSE-APACHE,scripts/review-scope,scripts/codex-aspects,skills/review-pr-with-codex/SKILL.md,skills/review-pr-with-codex/references/…}`
- New: `tests/scrut/codex-aspects.md`, `tests/fixtures/codex-stub` (a fake `codex` that writes valid, empty, malformed or no output, or exits non-zero, per an environment variable, and records its arguments so tests can assert `--sandbox`, `--ephemeral`, `-m`, `-c` and stdin from `/dev/null`).
- Modified: `.claude-plugin/marketplace.json` (category `code-review`), root `README.md` (Code Review row and External tools bullet: `codex`, `jq`), `Makefile` `SCRUT_ENV` and `.github/workflows/ci.yml` `scrut-env` (`CODEX_ASPECTS_BIN`, `CODEX_STUB_BIN`, the second `review-scope` path), `tests/scrut/repo-tooling.md` (identical-copy testcase for `review-scope`), `plugins/AGENTS.md` and `docs/plugin-development.md` (name the new identical pair).
- Generated: `make build` output under `dist/` and `.agents/`.

## Verification

- `make test-all` (lint, validate including cross-references and the Codex inventory budget, scrut), observing the final result.
- Scrut covers `codex-aspects` usage errors, schema shape, prompt rendering (symlink rendering, empty buckets omitted), each failure class through the stub, parallel runs reporting per-aspect status, the outside-tree `--out-dir` check, `simplify` running alone with `workspace-write`, and `changes` detecting in-scope and out-of-scope edits.
- Manual acceptance from Claude Code against a real branch: applicable aspects run in parallel through `codex exec`; a forced failure (for example an unknown model) is reported as failed; `simplify` is skipped when a Critical finding exists; the snapshot is unchanged after review aspects.
- Manual acceptance from Codex CLI with the plugin installed from the mirror: the same report through subagents.
- `check-versions` before the PR.
