# Branch Review: feature/add-review-colleagues-pr-skill

Base: `main` (merge base: `340f3192`)
Commits: 5
Files changed: 11 (8 added, 3 modified, 0 deleted, 0 renamed)
Reviewed through: `37e42cc1`

## Resolution status

All four source findings are addressed in commit `ce384fa6`. The original assessment below records the review of `37e42cc1`; this section tracks the subsequent fixes and their verification.

- [x] **R1:** synchronization stops on any untracked or ignored content, before either fast-forward or reset. The README and plan describe this conservative policy and no longer promise that reset always prompts.
- [x] **R2:** the tracked-change check precedes equal-HEAD acceptance, and tracked cleanliness is checked again after synchronization.
- [x] **R3:** read-only GraphQL POST queries are explicitly permitted; REST writes and GraphQL mutations remain prohibited. Repository scoping covers GraphQL variables, linked-issue repositories, the initial lookup, and the global account endpoint.
- [x] **R4:** the sub-issue query requests bodies and URLs, accepts and uses the pagination cursor, and retrieves all pages. The assessment reads each body and discloses incomplete retrieval.

The source and README mirrors were regenerated. The new plugin remains at `1.0.0`, consistent with the repository's new-plugin rule.

### Resolution verification

- `make lint validate` passed after regenerating both distributions with `make build`. This covers Markdown lint, Prettier, ShellCheck, shfmt, actionlint, JSON validation, cross-references, catalog consistency, and mirror freshness. The edited plan and review also passed targeted lint in fix mode and formatting. The catalog remains `catalog-M71-m103-p156-n58`.
- Nine disposable-checkout command checks passed: staged and unstaged changes at equal and stale HEADs; untracked and ignored content at an incoming tracked path; non-overlapping untracked content; ignored build output; and a clean fast-forward with post-sync checks. Local content and HEAD were preserved when the guard blocked synchronization. No commits were created in the probe.
- GitHub accepted the revised GraphQL query against `microsoft/vscode#300108`, with the page size reduced to one. The result had no parent or sub-issues. This verifies query compatibility and the empty-result path, but does not establish multiple-page retrieval or reading real sub-issue acceptance criteria.
- Full end-to-end agent behavior and the destructive reset scenarios remain unverified. These limitations remain in the plan's behavioral checklist.
- The earlier Scrut failures below remain outstanding; this change does not modify their launcher, fixtures, or environment.

## Summary

This branch adds `review-colleague-pr`, a skill that briefs the user on someone else's pull request without posting feedback. It gathers requirements and prior discussion, distinguishes substantive reviews from thread replies, synchronizes the checkout, and separates blockers, follow-ups, questions, and pre-existing problems. The plugin is registered at `1.0.0` and included in both generated distributions.

**Verdict: needs changes before merge.** The review principles and packaging are sound, but the checkout safeguards can lose untracked content or review local edits as though they belonged to the PR. The API rules also contradict the required GraphQL commands, and sub-issue acceptance criteria are not fully retrieved.

## Changes by Area

- **Review workflow:** the new source skill defines intent gathering, checkout synchronization, discussion retrieval, re-review baselines, evidence standards, and the chat report. Files: `plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md` and its plugin README.
- **Plugin registration:** the manifest and canonical marketplace register a new Code Review plugin; the root README adds its description and authenticated `gh` requirement.
- **Distribution:** the Codex marketplace and plugin mirror add the plugin, and OpenCode gains a skill symlink. The shorter Codex frontmatter description is the expected generated transformation; the workflow body matches the source.
- **Planning:** the new plan records design decisions, implementation steps, verification scenarios, and the substantive-review observation from PR 417.

## File Inventory

### New files (8)

- `plugins/review-colleague-pr/.claude-plugin/plugin.json`
- `plugins/review-colleague-pr/README.md`
- `plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md`
- `dist/codex/plugins/review-colleague-pr/.claude-plugin/plugin.json`
- `dist/codex/plugins/review-colleague-pr/README.md`
- `dist/codex/plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md`
- `dist/opencode/skills/review-colleague-pr` (symlink)
- `docs/plans/todo/2026-09-14-add-review-colleagues-pr-skill.md`

### Modified files (3)

- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`
- `README.md`

There are no deleted or renamed files. This review document is outside the reviewed commit range.

## Notable Changes

- No package dependencies, executable helpers, CI configuration, or schemas change. The skill requires Git and authenticated GitHub CLI access.
- The catalog tag changes from `catalog-M70-m103-p156-n57` to `catalog-M71-m103-p156-n58`, correctly accounting for one new `1.0.0` plugin.
- Checkout synchronization includes a destructive reset path. The README omits reset from its suggested allow rules, but that does not establish that every downstream harness or existing permission configuration will prompt.

## Code Quality Assessment

### R1. P1: protect untracked content before a hard reset

Location: [SKILL.md:97](../../plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md#L97), with the reset at lines 107-115.

The cleanliness check explicitly excludes untracked files. A linked worktree with no local commits can therefore pass every reset condition while containing an untracked file at a path introduced by the rewritten PR. The prescribed hard reset can overwrite that file. Printing the old HEAD does not recover content that was never committed. This follows the documented behavior of [git reset --hard](https://git-scm.com/docs/git-reset).

**Required change:** detect untracked and ignored paths that the target tree could overwrite, and stop when they would be affected, or use a synchronization method that refuses such overwrites. Include this case in the behavioral verification. The tracked-files-only requirement in the plan itself needs correction.

### R2. P1: check for tracked edits before accepting an equal HEAD

Location: [SKILL.md:95](../../plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md#L95).

The equal-SHA path proceeds directly to requirements gathering before checking the working tree. With HEAD already at the PR head and a local edit in a changed source file, the committed diff describes the PR while the later whole-file reads and caller tracing see the local edit. The report can then attribute a local defect or fix to the colleague and cite lines that do not match the reviewed commit.

**Required change:** check tracked-file cleanliness before the equal-HEAD return. Stop on local edits, or consistently read committed blobs throughout the review. Verify the dirty-tree case with both matching and stale HEADs.

### R3. P2: permit read-only GraphQL queries in the API rule

Location: [SKILL.md:59](../../plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md#L59); affected commands at lines 135 and 162.

The ground rule forbids every `gh api` request whose method is not GET. Both required GraphQL commands supply fields, which makes GitHub CLI send POST according to the [gh api documentation](https://cli.github.com/manual/gh_api). An agent following the prohibition must skip the parent/sub-issue and thread-resolution reads; an agent executing the examples violates the ground rule.

**Required change:** distinguish read-only GraphQL queries from mutations. Explicitly permit query POST requests while retaining the prohibition on GraphQL mutations and REST writes. Make the repository-scoping rule account for GraphQL owner/repository variables and the global `user` endpoint too.

### R4. P2: retrieve sub-issue bodies before assessing requirements

Location: [SKILL.md:132](../../plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md#L132).

The parent/sub-issue query fetches the parent's body but only the number, title, and state of the first 50 sub-issues. No subsequent instruction fetches their bodies or remaining pages. When a linked issue delegates acceptance criteria to a sub-issue body, the review can declare those requirements met without ever seeing them.

**Required change:** retrieve sub-issue bodies and paginate the connection, or explicitly fetch each discovered sub-issue and disclose any remaining coverage limit. Verify a case where a requirement exists only in a sub-issue body.

### Strengths

- Evidence requirements are concrete: trace the behavior, cite source lines, and identify a failure scenario before presenting a concern as fact.
- The substantive-review rule correctly distinguishes original inline comments from replies, avoiding misleading re-review baselines.
- The report format keeps urgency, uncertainty, and pre-existing issues separate, and discourages duplicating resolved feedback.
- Source, catalog, README, and generated mirrors follow the repository's established structure. No unnecessary helper or dependency is introduced.

## Plan Compliance

Plan: [2026-09-14-add-review-colleagues-pr-skill.md](../plans/todo/2026-09-14-add-review-colleagues-pr-skill.md).

**Verdict: partial compliance.** Most deliverables are implemented faithfully, but the safety and requirements gaps affect core goals. Implementation progress is **9/12 grouped deliverables done (75%)**, with 3 partially done and none wholly absent. The groups below cover the plan's implementation sections; verification is assessed separately so written instructions are not mistaken for tested behavior.

### Done (9)

1. **Plugin layout and frontmatter:** the planned three source files exist, with trigger phrases and dependency information.
1. **Review principles:** careful and considerate review standards are present, including evidence, scope, urgency, and author-neutral language.
1. **PR resolution and options:** current-branch lookup, optional number, checkout identity checks, closed/draft state handling, requirement docs, and baseline options are described.
1. **Prior discussion and baseline selection:** REST collections are paginated, thread resolution is queried, and substantive reviews exclude thread-only replies. Actual GraphQL execution remains dependent on R3.
1. **Reading and CI workflow:** committed diffs, contextual reads, generated-file exclusions, re-review diffs, coverage disclosure, and CI-only verification are specified.
1. **Assessment:** requirements, architecture, urgency, questions, strengths, pre-existing issues, and prior feedback are covered.
1. **Report and error handling:** the report template and stopping behavior match the intended chat briefing.
1. **Plugin README:** description, dependency, options, example, comparisons, permissions, and links are present.
1. **Catalog and mirrors:** manifest, registration, root README, catalog tag, and both generated distributions are included.

### Partially done (3)

1. **Ground rules:** GitHub write prohibitions and untrusted-content handling are explicit, but the GET-only restriction contradicts the GraphQL workflow (R3).
1. **Checkout synchronization:** fast-forward, divergence, local-commit, and linked-worktree checks are present, but untracked content and equal-HEAD local edits remain unsafe (R1 and R2).
1. **Requirements gathering:** linked issues, parent issues, external docs, and the thin-requirements gate are present, but sub-issue bodies and pagination are missing (R4).

### Verification coverage

The plan lists four mechanical checks and eleven behavioral checks. The behavioral scenarios are descriptions, not evidence that the skill was exercised successfully.

- **Mechanical cross-references and full repository checks:** see Validation below.
- **Generated-tree cleanliness:** confirmed before saving this review; `git status --porcelain dist/ .agents/` produced no output.
- **Version check:** the new plugin is `1.0.0`, and the recomputed catalog tag matches. Full marketplace consistency is covered by repository validation.
- **Behavioral mirrors:** inspected the Codex workflow body and OpenCode symlink; the source workflow is preserved.
- **Behavioral re-review baseline:** partially evidenced. The plan records the PR 417 thread-reply observation, but does not record the required positive case with an actual substantive earlier review. That historical observation was not independently re-run here.
- **Behavioral read-only GitHub run, report quality, fast-forward, rewritten clean worktree, rewritten unsafe checkout, dirty tree, wrong checkout, thin requirements, and sub-issues:** unverified. No completed results are recorded in the branch, and these scenarios were not run during this review. This is an evidence gap, not proof that nobody attempted them.

### Deviations and fidelity

- The final plan replaces scratch query files with inline single-line GraphQL queries. The source follows that revision; this is consistent with the no-files posture.
- The commit sequence separates plugin authoring, registration, mirror generation, and recorded findings. That is a reasonable organizational change with no harmful ordering effect.
- The plan's original tracked-only cleanliness policy and GET-only rule are reproduced in the implementation. R1 and R3 are therefore design defects as well as implementation findings; literal plan compliance would not fix them.
- No unrelated feature work or dependency additions appear in the diff. The plan remains in `todo/`, consistent with the outstanding verification and fixes.

## Validation

- **Passed:** Markdown lint, Prettier, ShellCheck, shfmt, actionlint, JSON validation, and all plugin validations, including cross-references and generated-tree freshness.
- **Passed:** check-versions assessment. The only changed plugin is new at `1.0.0`; marketplace coverage and version agreement pass validation, and `bin/compute-catalog-state` returns the committed `catalog-M71-m103-p156-n58`.
- **Passed:** `git diff --check`; the saved review also passed targeted Markdown lint in fix mode and Prettier formatting.
- **Failed:** `make test-all` exited 2 at Scrut. Its final result was 402 test cases across 8 documents: 390 succeeded, 12 failed, 0 skipped. All failures are in `tests/scrut/launch-workmux.md`, whose source, helper, and launcher are unchanged on this branch.
- **Confirmed environment limitation:** ten failures reject valid generated branch names. The fixture delegates validation to `/usr/bin/git`, which fails because the Xcode license has not been accepted. Running the same validation with the Git on PATH succeeds. No license or system configuration was changed.
- **Unresolved test failures:** two additional cases fail because expected `prompt_path` and `tmux-log` files are absent. Their causes were not established. They are not attributed to this plugin, but the full suite cannot be reported as passing.
- **Not exercised:** an end-to-end run of the new skill against a colleague's PR or the planned destructive synchronization scenarios. Static checks do not establish those behaviors.

The full command output is available locally at `/tmp/review-colleague-branch-tests.log`. Only this review document was added to the working tree; no implementation files were changed or committed.

## Next Action

R1-R4 are resolved in source and the mirrors are regenerated. Complete the remaining behavioral scenarios and resolve the environment/test failures before treating the full verification plan as complete.

The resolution status above supersedes the original findings for follow-up work.
