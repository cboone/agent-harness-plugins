# Branch Review: feature/357-create-worktree-record

Base: `main` (merge base `b6842523`)
Reviewed through: `0381ba0d`

Addresses [#357](https://github.com/cboone/agent-harness-plugins/issues/357).

## Summary

Lets a worktree declare and hold a named exclusive resource, so work that cannot run in parallel is recorded rather than remembered. A new bundled script, `manage-resource-claims`, owns a shared claim file in the main worktree's `.claude/`; `create-worktree` and `address-issue-in-worktree` check it before creating a worktree and record a claim after; `suggest-next-issue` reads it so it can answer "what can I work on in parallel" from state instead of from the user's memory.

The claim is advisory throughout. A held resource is reported and asked about, never refused, because the issue is explicit that a user who overrides always has a reason.

## Changes by Area

### The claim store

`manage-resource-claims` is a Bash script with `list`, `check`, `claim`, `release`, and `prune` subcommands, following the conventions already set by `compose-issue-prompt`: `die()` writing `scriptname: message` to stderr, the jq check deferred until after argument parsing so `--help` works without it, and a validation ladder over the input document.

Claims live in the main worktree's `.claude/worktree-resources.local.json`, resolved from the first record of `git worktree list --porcelain`. That is what makes one file reachable from every linked worktree, which is the whole mechanism: worktrees share a repository but not a working tree.

Files: `plugins/create-worktree/scripts/manage-resource-claims`, `plugins/address-issue-in-worktree/scripts/manage-resource-claims` (byte-identical, per rule 18).

### Skill surfaces

`create-worktree` gained `--resource`, `--release-resource`, and `--list-resources`, and grew from five workflow steps to seven: a claim-only short circuit at the front, and a claim check before the prompt is composed. `address-issue-in-worktree` gained `--resource` and one new step, placed ahead of "Mark Issue In Progress". `suggest-next-issue` reads the claim file, weighs a resource conflict as a high signal, gained a "Safe to Parallelize" category and `--parallel-only`, and ends its summary with who holds what.

Files: the three `SKILL.md` bodies and their READMEs.

### Tests and tooling

A new scrut suite covers both script copies, driving `git worktree list --porcelain` through the existing `git-worktree-stub` so staleness is deterministic rather than dependent on the ambient repository. `tests/scrut/repo-tooling.md` gained a third `cmp` guard. `Makefile` and `.github/workflows/ci.yml` gained the two `*_BIN` variables and the `WORKTREE_RESOURCES_FILE` entry in `SCRUT_UNSET`.

Files: `tests/scrut/manage-resource-claims.md`, `tests/scrut/repo-tooling.md`, `Makefile`, `.github/workflows/ci.yml`.

### Catalog and docs

Three minor version bumps, a recomputed catalog state tag, both generated mirrors, plus `AGENTS.md` (three scripts, three guards), the root README external-tools bullet, and a `.gitignore` entry.

## File Inventory

**Added**: the plan, both script copies, the new scrut suite.

**Modified**: three `plugin.json` manifests and their `marketplace.json` entries, three `SKILL.md` bodies, three plugin READMEs, the root README, `AGENTS.md`, `Makefile`, `.github/workflows/ci.yml`, `.gitignore`, `tests/scrut/repo-tooling.md`.

**Deleted or renamed**: none.

Generated trees under `dist/` and `.agents/` move with the source and are excluded above.

## Notable Changes

- **First state file under a project's `.claude/`.** No plugin in this repository previously read or wrote one, so this sets the precedent. The `.local.json` suffix follows `settings.local.json`, which already signals "personal, gitignored".
- **A third duplicated script pair.** Rule 18 forbids sharing across plugins, so the copies are kept identical by a `cmp` guard. Changing one without the other now fails the build in three places rather than two.
- **`SCRUT_UNSET` grew an entry.** That list is hand-maintained by design; the new `WORKTREE_RESOURCES_FILE` override would otherwise make the suite sensitive to the developer's environment.

## Plan Compliance

Plan: `docs/plans/todo/2026-09-12-worktree-exclusive-resource-claims.md`.

**Verdict: full compliance.** Every numbered change in the plan landed, in the form the plan described, and the two design decisions most likely to drift (the claim file location and `suggest-next-issue` reading the file directly rather than shipping a third script copy) were both implemented as written.

All ten planned changes are done. Two details are worth recording:

- The plan predicted the catalog tag would become `catalog-M65-m95-p141-n52`. It became `catalog-M67-m95-p142-n54` because `main` gained two plugins while this branch was open. The plan said to take `bin/compute-catalog-state` as authoritative over its own arithmetic, which is what happened.
- The plan's subcommand table described the stale marker as `stale=yes`; the implementation emits `state=stale`, since state is one field with two values rather than two fields. The plan was corrected to match rather than the other way round.

**Deviations**: several additions beyond the plan, all from review rather than from scope creep. `cmd_check` rejects an option-shaped resource name, matching `cmd_claim`. The claim file is serialized by a PID-owned mutex, validated against a contract that read and write share, and held to one claim per resource. `claim` refuses a live foreign holder unless `--take-over` names that exact holder. Each closes a defect found in the code this branch adds.

**Fidelity**: the advisory-not-a-lock constraint is honored, with the distinction the review process sharpened. The claim is advisory **about the resource**: nothing prevents anyone using the DAW or the port, and `suggest-next-issue` flags rather than hides unless parallel-safe work was asked for. It is deliberately not advisory **about the file**: `claim` refuses a resource another worktree still holds, because `check` and the write are separate operations and a takeover nobody was asked about is the outcome the feature exists to prevent. `--take-over` is how an approved one proceeds, and it names the holder so consent cannot transfer to a different one. That is a stricter reading than the first draft of this branch took, and the correct one.

## Code Quality Assessment

**Overall: ready to merge.**

### Strengths

- **Staleness is derived, never stored.** A claim cannot outlive its worktree, and nothing has to hook worktree removal, which neither skill performs. This removes an entire class of bug rather than handling it.
- **`check` exits 3 on a held resource.** A distinct exit code lets the skill branch without parsing prose, which matters because the prose is the part most likely to be reworded later.
- **Undetermined staleness is distinguished from "nothing is live".** `live_worktrees` returns non-zero when git cannot answer, and `decorate_claims` then marks nothing stale. The naive version, treating an empty list as "no worktrees exist", would report every claim stale and `prune` would clear a file full of valid claims.
- **Writes are atomic.** `mktemp` beside the target plus `mv` means a reader never sees a half-written document, and the temp file is removed on both failure paths.
- **A malformed file is refused, not reset.** Overwriting something the user may have hand-edited loses more than it saves.
- **Test coverage tracks the failure modes, not just the happy path**: a claim replacing a stale claim, a takeover from a live holder, a re-claim from the same worktree, release by resource and by worktree, an empty file, a malformed file, running outside a repository, and `--help` on a PATH without jq.

### Issues addressed during review

- `cmd_check` accepted an option-shaped argument as a resource name, so `check --json` reported "free" and exited 0. Fixed in `0381ba0d` with a regression test.
- The merge from `main` silently dropped two `SCRUT_ENV` entries and two `scrut-env` entries: both sides had inserted at the same position and git kept only one, without a conflict marker in the `ci.yml` case. Caught by the scrut suite and restored before the merge was committed.

### Suggestions, not blocking

- `prune` invokes `git worktree list --porcelain` twice: once to confirm git can answer, once inside `decorate_claims`. Harmless, and the alternative is threading the result through an extra parameter.
- `SCRUT_ENV` in the `Makefile` and `scrut-env` in `ci.yml` are two hand-maintained lists that must agree, and they now collide on merge whenever two branches add an entry. Neither is sorted, so the collision is positional. Worth considering whether CI should assert the two lists match.

### Completeness

No TODO, FIXME, or stub markers in the new code. Every new capability has scrut coverage and README documentation. The three follow-ups identified during the work are filed as [#409](https://github.com/cboone/agent-harness-plugins/issues/409), [#410](https://github.com/cboone/agent-harness-plugins/issues/410), and [#411](https://github.com/cboone/agent-harness-plugins/issues/411), so nothing known is left undocumented.
