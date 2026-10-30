# Fold comment trimming into trim-text

Issue: [Fold trim-comments into trim-text](https://github.com/cboone/agent-harness-plugins/issues/597).

## Scope and boundary

Give prose and code comments one standard and workflow in `trim-text`, with comment-specific rules in a `code-comments` profile. Keep both plugin registrations, skill names, triggers and existing caller spellings. Preserve report-only Codex runs in the read-only sandbox. Keep `trim-text`'s existing no-argument PR/branch selection; explicit `branch` scope handles mixed files. Preserve `trim-comments`' no-argument comment scope through its alias.

TOOLING confirmed the alias fits the brief's compatibility boundary and requested a scope-equivalence test. Later catalog removal is outside this branch; note its follow-up in the PR body without filing it.

## Prior art

- [Vale style packages](https://vale.sh/explorer) compose reusable rules through `BasedOnStyles`. [Vale's standard library](https://vale.sh/blog/std) lets a house style extend shared rules. Use the separation of shared rules and variant overrides; adding a linter dependency would not implement this skill workflow.
- [Anthropic's skill-creator guide](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) places domain variants in references read as needed. Use this layout for comment-only rules and worked examples, keeping prose callers from loading them.
- Existing `trim-text` profiles already separate PR/issue bodies and agent instructions. Extend that mechanism. `bin/build-shared-references` already distributes common references across isolated plugins. Copying the core standard would remove drift but retain two trim steps, the limitation the issue identifies.

## Implementation

1. Add the comment profile: language-aware extraction, changed comments and directly preceding comments, test scaffolding, stylesheets, protected directives and doctests, ticketless TODO flags, docstring retention and worked examples. Preserve comment-only edits and verify unchanged code.
2. Extend file detection and branch scope to classify prose and source files per profile. Preserve generated/secret filters, path handling, changed-unit boundaries, dirty-file commit exclusions, parent continuation behavior and read-only proposal validation.
3. Replace `trim-comments`' duplicated workflow with a compatibility alias to the comment profile, retaining its scope and options. Declare the dependency and handle an unavailable target explicitly. Update descriptions, READMEs and relevant references without changing caller invocations.
4. Bump `trim-text` minor and `trim-comments` major; regenerate mirrors with `make build`. Preserve shared-reference freshness checks and add only meaningful affected coverage.

## Validation and delivery

Use the full local review order: anti-patterns plus simplify, focused Codex review, report-only comment/prose trims, disposable-clone baseline Semgrep, then `lint-and-fix --no-push`, repository `check-versions`, and exact-tree signed-commit tidy. Record rounds, findings, checks and any planted defects in a review ledger.

During iteration run only affected Scrut documents, with `SCRUT_JOBS=2` or less. Before pushing, acquire `~/Work/projects/.locks/tooling-full-suite.d` atomically, write the worker handle to `owner`, and run one `make test-all` with `SCRUT_JOBS=2`; release only the acquired lock with a trap. Existing fixture lint/environment-isolation failures and the macOS setpgid failure tracked in issue 697 stay outside scope and must be reported accurately. Push and open a ready PR only after required gates and checks are satisfied, then report to TOOLING. TOOLING merges; live configuration stays untouched.

## Completion

Implemented the unified workflow and compatibility alias. The opt-in evaluator passed all seven scope requests and rejected the planted wrong-profile handoff. Reviews, trims, baseline Semgrep, version checks and the locked final suite completed. The full suite reproduced only the known fixture operand-contract failure, which TOOLING approved carrying through publication. See the [review ledger](../../reviews/2026-10-30-fold-trims-ledger.md) for measured results and review dispositions.
