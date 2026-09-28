# Branch Review: feature/add-fan-out-option-to-worktree-creation

Base: `main` (merge base `17be4a6a`)
Commits: 5
Files changed: 27 (1 added, 26 modified, 0 deleted, 0 renamed)
Reviewed through: `ebb392c0`

## Summary

This branch defines combined and per-issue worktree creation for several GitHub issues. The three fan-out flags, branch preflight, sequential launch completion, prompt composition, and combined `address-issue` workflow are documented in the canonical skills. The launcher and its Scrut fixtures were extended, and the Codex mirror was regenerated.

The branch needs two behavior corrections before it is ready for a pull request. The full repository check passed, including 610 Scrut test cases, but the plan's live scratch-repository scenarios were not observed in this review.

## Changes by Area

### Worktree launcher

Both byte-identical `launch-workmux` copies gained `--resolve-issue-branch` for read-only branch preflight and `--await-completion` for a detached launch with an observable exit result. The new mode confirms a worktree and handles failures, timeouts, and temporary-file ownership. `tests/scrut/launch-workmux.md` and two fixture stubs cover those helper paths; `Makefile` isolates their environment variables.

Files: `plugins/address-issue-in-worktree/scripts/launch-workmux`, `plugins/create-worktree/scripts/launch-workmux`, `tests/scrut/launch-workmux.md`, `tests/fixtures/git-worktree-stub`, `tests/fixtures/workmux-stub`, `Makefile`.

### Issue and worktree skills

Both worktree skills now describe combined mode and fan-out mode, with `--each` and `--separate` as aliases for `--fan-out`. `create-worktree` classifies a list of issue numbers as issues. `address-issue` describes one combined plan and approval gate across several issues.

Files: the three `plugins/*/skills/*/SKILL.md` files and three plugin READMEs for `address-issue`, `address-issue-in-worktree`, and `create-worktree`.

### Packaging and plan

The three plugin manifests have minor version bumps. The branch adds `docs/plans/todo/2026-09-27-fan-out-worktree-creation.md` and updates eleven generated files under `dist/codex/`. No dependencies, schemas, or CI workflows changed.

## File Inventory

- **Added (1):** `docs/plans/todo/2026-09-27-fan-out-worktree-creation.md`.
- **Modified canonical files (15):** `Makefile`; three plugin manifests, three plugin READMEs, three plugin skills, two `launch-workmux` copies, two fixture stubs, and `tests/scrut/launch-workmux.md`.
- **Modified generated files (11):** Codex copies under `dist/codex/plugins/` for the three affected plugins.
- **Deleted or renamed:** None.

## Plan Compliance

**Verdict: Partial compliance.** Nine of twelve grouped outcomes are complete (75%); three are partial.

### Done

1. Define combined mode as the default in both worktree skills.
1. Support `--fan-out`, `--each`, and `--separate` as equivalent fan-out flags.
1. Extend `address-issue` to fetch, check, plan, and report several issues under one approval gate, with commit references for the issues addressed.
1. Gather issues and resolve branch ambiguity before fan-out launches.
1. Launch fan-out worktrees sequentially after an observable `workmux add` result.
1. Report completed failures and stop on an uncertain timeout.
1. Classify several issue numbers as issues in `create-worktree`.
1. Document per-issue results and update the three plugin READMEs and minor versions.
1. Regenerate the Codex mirror and add focused helper tests.

### Partially done

1. **Combined prompt:** both skills join issue prompts, but the examples can mask an early `compose-issue-prompt` failure. See issue 1 below.
1. **Option interactions:** the single-issue equivalence promise conflicts with the fan-out option rejection rules. See issue 2 below.
1. **Verification:** `make test-all` passed. The plan's live scratch-repository scenarios, including a real window, session handoff, closed issue, and multi-issue approval flow, were not run in this review. The new Scrut cases exercise the launcher, not the complete skill workflows.

The implementation stays within the plan's named plugin and test areas. Its `Makefile` environment isolation is a justified addition. I found no unplanned dependency or API surface.

## Code Quality Assessment

**Verdict: Needs changes before a pull request.** The helper's detached handoff and cleanup paths have focused tests, and the two shipping copies remain aligned. The skill text has two behavior defects that the helper tests do not cover. No findings arose from the applicable Bash, Scrut, or Markdown style checklists.

### Issue 1: An early combined prompt failure can be hidden

In both combined-mode examples, a brace group runs one `compose-issue-prompt` per issue and pipes the group to `launch-workmux`. If the first composer fails but the last succeeds, the group's status is the last command's status; the launcher can create a worktree with only the later issue in its prompt. This contradicts the requirement that the prompt carry every issue.

Evidence: `plugins/address-issue-in-worktree/skills/address-issue-in-worktree/SKILL.md:57-63` and `plugins/create-worktree/skills/create-worktree/SKILL.md:57-63`.

**Correction:** require every composition to succeed before invoking the launcher, then join the completed prompt pieces in order. Cover a failed early composition as well as the successful combined prompt.

### Issue 2: Single-issue fan-out flags do not preserve single-issue options

Both skills say that any fan-out alias with one issue behaves exactly like the single-issue workflow. Their option rules reject `--resource` in both skills and `--branch` in `create-worktree` whenever a fan-out flag is present. For one issue, those options can serve the one worktree, so the rejection changes the promised behavior.

Evidence: `plugins/address-issue-in-worktree/skills/address-issue-in-worktree/SKILL.md:33-43` and `plugins/create-worktree/skills/create-worktree/SKILL.md:34-48,328-330`.

**Correction:** apply multi-worktree option rejections only when more than one distinct issue remains after duplicate removal, or explicitly narrow the single-issue promise and update the plan and READMEs. Add a single-issue alias case with `--resource` and, for `create-worktree`, `--branch`.

## Validation and Limits

- `make test-all` passed: Markdown lint, Prettier, ShellCheck, shfmt, actionlint, JSON and plugin validation, generated-mirror validation, and 610 Scrut test cases.
- `workmux list --help` and `workmux list --json` confirmed the documented filter and JSON fields on this machine.
- I did not create real worktrees, tmux windows, GitHub issue changes, or a PR while reviewing.
- The branch was clean before the review file was saved. This review is through `ebb392c0`; the review file itself is not part of the evaluated diff.
