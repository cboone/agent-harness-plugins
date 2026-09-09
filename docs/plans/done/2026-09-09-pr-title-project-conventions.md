# Make the PR title style yield to project conventions

Addresses [#322](https://github.com/cboone/agent-harness-plugins/issues/322).

## Context

`plugins/pr/skills/pr/SKILL.md:237` states an absolute rule:

> - Do not include a conventional-commit type prefix in the PR title.

That is a reasonable house default, but because it is phrased as an absolute it outranks everything it should be deferring to: a project whose CI **rejects** a PR title without a type prefix, and the user's own global `CLAUDE.md`, which asks for Conventional Commits on PR titles.

The reported failure (`swing-left/frontend#1690`): that repo's `.github/workflows/lint-commits.yml` pipes `github.event.pull_request.title` into commitlint on `opened`, `edited`, `synchronize`, and `reopened`. Following the skill produced `Assert the single-claimer invariant in the applyAsanaDecision race test`, which failed the required check with `subject-empty` and `type-empty`. Retitling to `test(api): assert the single-claimer invariant in the publish race test` fixed it. The failure is silent at creation time: `gh pr create` succeeds and the check only goes red afterward.

Intended outcome: the skill's title rules become a *default* that is applied only when no project convention is detected, and the skill notices when a PR-title lint check goes red instead of leaving it to be discovered later.

### What the exploration turned up

- **`pr` is the only skill that creates PRs.** Nothing in `plugins/` runs `gh pr edit`, and no other plugin asserts a PR-title style. `sentence case` appears exactly once in the whole tree, at `pr/SKILL.md:236`.
- **The commit-message side is already conditional**, so the issue's "this probably applies elsewhere" note does not expand the scope. `plugins/commit/skills/commit/SKILL.md:106-115` already says "Match the repository's existing style. If there is no clear convention, default to conventional commits format," and `pr/SKILL.md:174` inherits that same detect-then-match posture 26 lines *above* the absolute PR-title rule. PR titles are the one place the pattern was never applied.
- **All four title bullets need scoping, not just the prefix one.** Under commitlint's defaults, `subject-case` rejects a capitalized subject and `header-max-length` is 72, not 70. Fixing only the prefix bullet would still emit `feat: Add the thing` at 70 characters into a repo that rejects both.
- **Nothing in `plugins/` mentions commitlint** and the `pr` skill never reads `CLAUDE.md`, `AGENTS.md`, or `.github/copilot-instructions.md`. This repo's own agent config states no PR-title convention, so the detection must degrade cleanly to today's behavior here.

### Patterns to reuse rather than invent

- **CI workflow scanning**: `plugins/lint-and-fix/skills/lint-and-fix/SKILL.md:86-95` (`#### CI Workflow Detection`) already establishes the Glob-then-read idiom over `.github/workflows/*.yml` and `*.yaml`. Match its shape and wording.
- **Deference phrasing**: `plugins/commit/skills/commit/SKILL.md:115` for "match the repository, else default", and `plugins/write-lean-code/skills/write-lean-code/SKILL.md:38` for "read the invoking project's CLAUDE.md (or equivalent agent-config file) ... before applying the generic guidance below."
- **Commit type selection**: `pr/SKILL.md:175` already lists the types (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `style`). The new title logic should reference that step rather than restate the list.

## Approach

All changes are to the `pr` plugin. Detection lives in step 7, where the title is composed, not in step 1, so the change stays contained.

### 0. Rename this plan file first

`docs/plans/todo/322-immutable-noodle.md` is an auto-generated name. Rename it to `docs/plans/todo/2026-09-09-pr-title-project-conventions.md` before doing anything else, matching the convention in `docs/plans/` (`2026-05-02-codex-cli-native-plugins.md`). The `pr` skill's own Plan Name Cleanup rules (`pr/SKILL.md:313-324`) will otherwise do this at commit time.

### 1. Add title-convention detection to step 7

`plugins/pr/skills/pr/SKILL.md` — insert a new `#### Detect the title convention` subsection between line 230 (the `Analyze all commits...` paragraph) and line 232 (`#### Title`).

State that the title rules are this skill's default and yield to a convention the project enforces or documents, then check three signals in order, stopping at the first match:

1. **CI lints the PR title.** Glob `.github/workflows/*.yml` and `*.yaml` and read each. Look for a workflow that feeds `github.event.pull_request.title` into a linter, either piped into `commitlint` or through an action such as `amannn/action-semantic-pull-request`. Make the distinction explicit: a commitlint config alone (`.commitlintrc*`, `commitlint.config.*`, or a `commitlint` key in `package.json`) is **not** sufficient, because it usually lints commit messages rather than the PR title. The reference to `github.event.pull_request.title` is what constrains the title. When such a workflow exists, read the commitlint config it uses and follow its `type-enum`, `scope-enum`, `subject-case`, and `header-max-length` values instead of the defaults.
1. **Project agent config states a PR title format.** Read `CLAUDE.md`, `AGENTS.md`, and `.github/copilot-instructions.md` in the repository root, and honor user-level instructions already present in context. This is the half that fixes the second half of the bug: the skill overrode the user's global preference, not just the project's CI.
1. **Merged PR titles are consistent.** Fallback: `gh pr list --state merged --limit 20 --json title --jq '.[].title'`. If most match `^[a-z]+(\([^)]+\))?!?:\s`, match that style.

Close with: if no signal matches, no convention is enforced, so use the defaults. Record whether a PR-title lint workflow was found, because the new step 8 keys off it.

### 2. Rewrite the `#### Title` block

Replace lines 232-237 so all four bullets become the no-convention default:

- When a convention was detected, follow it and skip the defaults. Derive the type from the branch commits using the same type selection as step 4 (`pr/SKILL.md:175`), use the project's scope vocabulary if it defines one, and respect its configured length and subject case. Note that commitlint defaults mean `type(scope): lowercase subject` at 72 characters or fewer.
- Otherwise, keep today's four bullets verbatim (under 70 characters, summarize the overall change, sentence case, no type prefix).

### 3. Add step 8, "Verify the Title Check"

Insert before the current `### 8. Report Results` (line 295) and renumber that to `### 9. Report Results`. Verified: nothing in `SKILL.md` or `README.md` cross-references step 8, so renumbering is safe (the only step references are at lines 91 and 201, both pointing at steps 4, 6, and 7).

The new step is skipped entirely unless step 7 found a PR-title lint workflow. When it did:

```bash
gh pr checks --json name,state,link 2> /dev/null || true
```

Note that `gh pr checks` exits non-zero when checks are failing *or* still pending, so a non-zero exit is not an error here, and that checks frequently have not registered yet immediately after `gh pr create`. Three outcomes:

- **Passed**: continue to step 9.
- **Failed**: report the failing check name and reason, and hand the user the exact remediation with a corrected title: `gh pr edit --title "<corrected title>"`. Do **not** run `gh pr edit` automatically.
- **Pending or nothing reported**: say so and continue.

State that the step is best-effort and must never block the workflow, matching the existing posture for issue detection (`pr/SKILL.md:353`).

### 4. Report and error-handling updates

- In renumbered step 9, add a reported item: whether a project PR title convention was detected and which signal matched.
- In `## Error Handling` (line 343-355), add one bullet for a red PR-title lint check pointing at step 8. Do not add a bullet for `gh pr checks` failing outright; the `|| true` already covers it.

### 5. `plugins/pr/README.md`

- `## What It Does` (line 15): note that the PR title follows a project convention when one is enforced or documented, and falls back to the house style otherwise.
- `## Recommended Permissions` (line 32): add `Bash(gh pr list *)` (merged-title fallback) and `Bash(gh pr checks *)` (step 8) to the single-line `allow` array. `gh pr edit` is deliberately **not** added, since the skill only suggests it.

### 6. Version and mirrors

- Bump `plugins/pr/.claude-plugin/plugin.json` from `1.5.5` to `1.6.0` (minor: new capability and a meaningful behavior change, per `AGENTS.md`).
- Mirror the same version into the `pr` entry in `.claude-plugin/marketplace.json` (line 315 block). The `description` fields are unchanged and must stay identical across both files and the root `README.md:43`.
- Recompute `metadata.version` with `bin/compute-catalog-state` and paste the result. Do not hand-derive it (current value: `catalog-M63-m79-p147-n51`).
- Run `bin/build-codex-marketplace` and `bin/build-opencode-mirror`, and commit the `dist/` results.
  - `dist/codex/plugins/pr/skills/pr/SKILL.md` and `.../plugin.json` are **real committed copies** that will otherwise drift.
  - `dist/opencode/skills/pr` is a symlink to the source, so nothing there needs editing.
  - Important: `.github/workflows/ci.yml:43-46` only runs `bin/build-opencode-mirror` before `git diff --exit-code dist/`. A stale codex mirror will **not** fail CI, so the codex regeneration has to be done deliberately.
- Run the `check-versions` skill before opening the PR.

## Files to modify

| File | Change |
| --- | --- |
| `plugins/pr/skills/pr/SKILL.md` | Detection subsection, rewritten `#### Title`, new step 8, renumbered step 9, error-handling bullet |
| `plugins/pr/README.md` | "What It Does" sentence, two added permission entries |
| `plugins/pr/.claude-plugin/plugin.json` | `1.5.5` → `1.6.0` |
| `.claude-plugin/marketplace.json` | `pr` version, recomputed `metadata.version` |
| `dist/codex/plugins/pr/**` | Regenerated |
| `docs/plans/todo/322-immutable-noodle.md` | Renamed, then moved to `docs/plans/done/` at PR time |

Out of scope: the issue's "probably applies anywhere else" note. The commit-message guidance in `commit` and in `pr` step 4 is already conditional, and no other plugin asserts a PR-title style, so there is nothing else to relax. Worth reporting back on the issue.

## Verification

1. **Repo validation** (all must pass):

   ```bash
   yarn lint
   bin/validate-json
   bin/validate-plugins
   bin/build-opencode-mirror && git diff --exit-code dist/
   ```

   Run `bin/build-codex-marketplace` first, so the codex regeneration is already committed when the `git diff --exit-code dist/` check runs.

1. **Catalog state agrees**: `bin/compute-catalog-state` output must equal `.metadata.version` in `.claude-plugin/marketplace.json`. Confirm with `bin/compute-catalog-state` and `jq -r '.metadata.version' .claude-plugin/marketplace.json`.

1. **Versions agree**: run the `check-versions` skill; `plugin.json` and the marketplace entry must both read `1.6.0`.

1. **Codex mirror is faithful**: the body of `dist/codex/plugins/pr/skills/pr/SKILL.md` must match the source except for the frontmatter `description`, which the build rewrites to the single-line marketplace description. Confirm with a diff ignoring the frontmatter block.

1. **Behavioral check, no-convention path** (this repo): run `/pr` on a scratch branch here. This repo has no PR-title lint workflow and no PR-title convention in its agent config, and its merged PR titles are mixed, so all three signals must miss and the title must come out in today's house style, with step 8 skipped. This is the regression check that the change is genuinely additive.

1. **Behavioral check, convention path**: run `/pr` on a branch in a repo whose CI lints the PR title (the reporting case is `swing-left/frontend`, whose `.github/workflows/lint-commits.yml` pipes `github.event.pull_request.title` into commitlint). The title must come out as `type(scope): lowercase subject`, and step 8 must report the title check's state. If that repo is not convenient, reproduce locally by adding a throwaway workflow containing `github.event.pull_request.title` piped to `commitlint` and confirming detection signal 1 fires.

1. **Fallback signal check**: in a repo with no title-lint workflow but with consistently conventional merged PR titles, confirm signal 3 fires via `gh pr list --state merged --limit 20 --json title`.
