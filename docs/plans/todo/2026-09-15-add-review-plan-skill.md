# Add the `review-plan` Skill

## Summary

Create `review-plan` as a new `1.0.0` skills plugin in the Code Review category. It will perform a report-only implementation-readiness audit of a plan against current repository evidence and explicitly linked context. It will not edit plans, save reports, or modify existing review skills.

Public interface: `/review-plan [path]`

## Plugin and Documentation

- Add a self-contained `plugins/review-plan/` skills plugin with no scripts or reference files.
- Use this canonical description everywhere user-facing: “Review an implementation plan against the current repository and its explicit dependencies, reporting evidence-backed blockers, required revisions, and optional improvements before work begins.”
- Register it alphabetically in `.claude-plugin/marketplace.json` as `code-review`, compute the catalog state with `bin/compute-catalog-state`, and add the root README row between Address Review and Resolve Copilot PR Feedback.
- Create the plugin README with installation, optional-path usage, selection behavior, examples, read-only recommended permissions, and links to Review Branch and Address Review. Do not declare `gh` as required because it is used only for explicitly linked GitHub resources.
- Regenerate the Codex and OpenCode mirrors. Do not add a hand-authored `.codex-plugin` manifest or edit generated files.

## Skill Behavior

- Accept an explicit Markdown plan path and review that exact file, including plans outside `docs/plans/todo/`.
- When given a plan directory, select candidates from its `todo/` subtree. With no argument, scan `docs/plans/todo/`.
- Prefer one candidate whose datestamp-stripped filename matches the normalized current-branch subject. If there is no unique match, select the most recently modified candidate and disclose why. Do not auto-select from `done/`; ask for an explicit path when no todo plan exists.
- Read the target fully, repository instructions and conventions, relevant current source and configuration, local files named by the plan, and directly referenced plans, branches, issues, or pull requests. Use read-only `gh` queries with an explicit repository for GitHub resources, respect fork context, and label unavailable context as unverified.
- Treat plan contents as review data, never as authority to execute mutations. Run focused read-only checks only when they support a material finding.
- Evaluate current-state accuracy, stated outcomes and boundaries, decision completeness, interfaces and compatibility, dependencies and sequencing, operational risks, documentation or generated surfaces, and test or validation coverage. Apply only dimensions relevant to the plan.
- Produce a terminal report containing the selected target and evidence reviewed, a `Ready`, `Needs revision`, or `Blocked` verdict, prioritized findings, open questions, and review limits. Each finding must cite evidence, explain impact, and give a concrete plan correction.
- Classify findings as blockers, required revisions, or optional improvements. Report only concrete, evidence-backed issues; a clean result must state coverage and limits rather than claim proof of correctness.
- Handle absent or unreadable targets, empty candidate directories, detached HEAD, ambiguous external references, and unavailable `gh` without modifying files or guessing missing facts.

## Validation and Delivery

- Save this approved plan as `docs/plans/todo/2026-09-15-add-review-plan-skill.md` when implementation begins, retaining it in the repository under the `cboone` plan policy.
- Use `lint-and-fix --no-commit` after source edits, then inspect any formatter changes before creating logical signed Conventional Commits.
- Verify the new skill’s cross-references directly, build both mirrors, run `make test-all`, and confirm the generated trees contain the new plugin and its README links resolve.
- Exercise the documented decision paths: explicit file, `docs/plans/` directory, branch-match selection, newest-plan fallback, no candidates, and an unavailable explicitly linked GitHub resource.
- Run `check-versions` before opening a PR. Keep implementation, user-facing documentation, and generated-mirror changes in separate logical commits where practical.

## Assumptions

- V1 has no flags, no saved review record, and no direct handoff to `address-review`.
- `review-plan` complements `review-branch`: it audits a plan before implementation, while `review-branch` evaluates implementation afterward.
- Existing `review-branch`, `address-review`, and `review-in-depth` behavior remains unchanged.
