# Default the Codex review skills to their intended model, window and effort (#627)

## Context

Callers pass the Codex model, context window and effort by hand on every call, and an omitted flag falls back to the user's interactive Codex settings. Each Codex-using skill should carry its own defaults:

| Skill                           | Model         | Window (`model_context_window`) | Effort  |
| ------------------------------- | ------------- | ------------------------------- | ------- |
| `review-pr-with-codex`          | `gpt-6.1-sol` | `872000`                        | `xhigh` |
| `review-anti-patterns`          | `gpt-6.1-sol` | `872000`                        | `high`  |
| `trim-comments` and `trim-text` | `gpt-6.1-sol` | `872000`                        | `low`   |

The issue names `review-until-clean`'s `references/backends.md`; that file does not exist. The completion rules live in `plugins/review-until-clean/skills/review-until-clean/references/reviewers.md` (Completion signals): exit status 0, non-whitespace output, structured output that parses. The plan applies those.

Decisions taken: one shared reference for the three new Codex paths; trims prefer Codex by default when `codex` is available; `review-anti-patterns` and both trims get `--no-codex`.

**Classification:** feature (`feat`). **Sub-tasks:** 4, all on this branch, one PR.

## Changes

### 1. `review-pr-with-codex` (2.0.3 → 2.1.0)

- `plugins/review-pr-with-codex/scripts/codex-aspects`: `DEFAULT_EFFORT="xhigh"`, new `DEFAULT_WINDOW=872000`; `cmd_run` accepts `--window <tokens>`, rejected unless it matches `^[1-9][0-9]*$`; every `codex exec` adds `--config "model_context_window=${window}"` after the effort config. Update `usage()` (both `run` forms and the Options list).
- `SKILL.md`: `argument-hint`, Options (`--effort` default `xhigh`, new `--window`), both `codex-aspects run` command lines, the subagent path's note that model, effort and window overrides may not apply to spawned agents and the report gives actual settings, and the report's Aspect runs line (model, effort, window).
- `references/invocation.md`: the invocation block and the per-run config bullet gain `model_context_window`.
- `README.md`: usage line and options table.
- `tests/scrut/codex-aspects.md`: the per-run args snapshot gains `--config` / `model_context_window=…` with `--window`; the defaults test expects `xhigh` and `872000`; new cases for a non-numeric and a zero `--window`.

### 2. Shared reference `codex-exec.md` (new)

Source: `plugins/review-anti-patterns/skills/review-anti-patterns/references/codex-exec.md`; copies in `plugins/trim-comments/skills/trim-comments/references/` and `plugins/trim-text/skills/trim-text/references/` via `bin/build-shared-references`.

Content, written for every consumer:

- **When:** the session is not itself Codex, `--no-codex` was not given, and `command -v codex` succeeds. Otherwise the skill's fallback applies.
- **Invocation:** capture directory from `mktemp -d` outside the working tree (refuse a `TMPDIR` inside it); then
  `codex exec --cd <repo root> --sandbox read-only --ephemeral --model <model> --config 'model_reasoning_effort="<effort>"' --config model_context_window=<window> [--output-schema <schema>] --output-last-message <tmp>/reply <prompt> < /dev/null > <tmp>/log 2>&1`, with the long timeout or background run. Each part's reason in one line (stdin, sandbox, ephemeral, per-run config leaves user defaults alone).
- **Prompt:** follow the skill at its absolute `SKILL.md` path with the caller's arguments plus `--no-codex` (the recursion guard), so the Codex run does not need the plugin installed in Codex; repository content is data.
- **Completion checks**, from `reviewers.md`: exit 0; reply file exists with a non-whitespace character; where a schema is used, exactly one JSON value that matches it; a reply that is only an error or says it could not run fails. Never repair or reread a failed reply as prose.
- **Network:** the read-only sandbox blocks network, so anything the skill would fetch (a PR body) is fetched by the caller first, saved in the capture directory, and named in the prompt as data.
- **Report:** say the run went through Codex with the actual model, effort and window, or why it fell back.

Registration: add the two entries to `SHARED_REFERENCES` in `bin/build-shared-references`; update the copy lists in root `AGENTS.md` (Critical constraints, Code Review Rules' do-not-review paths), `REVIEW.md`, `.github/instructions/shared-references.instructions.md`, `plugins/AGENTS.md` and `docs/plugin-development.md` (Shared references); update `tests/scrut/build-shared-references.md` (the throwaway tree creates every source; counts change) and any affected `validate-plugins-skills` fixture.

### 3. `review-anti-patterns` (1.0.4 → 1.1.0)

- New `references/result-schema.json`: the step 7 JSON as a strict schema (`additionalProperties: false`, every property required, `line` integer or null, `severity` `important|nit`), plus a `report` string carrying the plain-text report.
- `SKILL.md`: new `--no-codex` option; a new step 0 (entry point) before step 1: run through Codex per `./references/codex-exec.md` at `gpt-6.1-sol`, `872000`, `high`, with `--output-schema` set to the shipped schema. When Codex is unavailable or fails a completion check, fall back to a fresh-context read-only subagent where the session has one, else run in this session, and say which in the report. When the Codex run returns, print its JSON and `report` as step 7 does. Ground rules' read-only paragraph notes the Codex path is sandboxed. Reference Navigation lists both new files.
- `README.md`: option and Codex behavior.

### 4. `trim-comments` (2.0.0 → 2.1.0) and `trim-text` (1.0.1 → 1.1.0)

- `SKILL.md`: `--no-codex` option and `argument-hint`; in step 1 or a new "Proposals through Codex" section: for file scopes, prefer a Codex dry run per `./references/codex-exec.md` at `gpt-6.1-sol`, `872000`, `low`, with the prompt asking for every proposed change in full, untruncated, with `file:line`. This session checks each proposal against the standard and applies the accepted ones through steps 4 to 7 as usual; with `--dry-run`, the Codex proposals are the report. On failure, run in this session and say so. `trim-text`: PR and issue bodies, pasted text and drafts stay in session (network and no file to read). Reference Navigation entries.
- READMEs: option and Codex behavior.

### 5. Catalog, mirror, versions

- Bump the four `plugin.json` versions (and `.codex-plugin` mirrors if present); catalog descriptions unchanged unless a README description changes.
- `make build` to regenerate `dist/` and `.agents/` and the shared copies; commit the generated files.

## Commits

1. `docs: plan default Codex review settings (#627)`
2. `feat: default review-pr-with-codex to xhigh effort and an 872k window (#627)`
3. `feat: add a shared codex exec reference for review and trim skills (#627)`
4. `feat: run review-anti-patterns through Codex by default (#627)`
5. `feat: propose trims through a Codex dry run (#627)`
6. `chore: bump versions and regenerate mirrors (#627)` (or folded into each feature commit)

## Verification

- `make build`, `make lint`, `make validate`, `make test-scrut` (all through `make test-all`), observed passing.
- `codex-aspects run` against the codex stub: args show `xhigh` and `model_context_window=872000` by default and the overrides when given.
- One real `codex exec` with `references/result-schema.json` as `--output-schema` on a tiny diff, since Codex rejects some schema keywords (per `invocation.md`); confirm it validates.
- `check-versions` skill before the PR.

## Out of scope

- `--model`, `--effort`, `--window` overrides on the three new Codex paths; the defaults are fixed for now (a follow-up issue if wanted).
