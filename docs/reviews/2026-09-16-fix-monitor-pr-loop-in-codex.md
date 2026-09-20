# Branch Review: fix/monitor-pr-loop-in-codex

Base: `origin/main` (merge base: `2c687d72`)
Commits: 1
Files changed: 8 (0 added, 8 modified, 0 deleted, 0 renamed)
Reviewed through: `c9bbca98`

## Summary

This branch makes monitor-pr continuation explicit across harnesses. It adds an in-chat scheduled-task path and a bounded foreground loop with a default of three ticks, ending with a checkpoint rather than an unsupported promise to continue after returning a response. The monitor-pr plugin advances from 1.2.0 to 1.3.0, with matching catalog and generated Codex updates.

## Changes by Area

- **Watch continuation:** `plugins/monitor-pr/skills/monitor-pr/SKILL.md` adds `--ticks`, distinguishes scheduled and foreground operation, and requires task shutdown on readiness or escalation. The generated Codex skill reflects these changes.
- **Usage documentation:** `plugins/monitor-pr/README.md` explains both paths, adds the option and an example, and clarifies what foreground sleep can do. The generated Codex README carries the same guidance.
- **Version and catalog metadata:** Canonical and generated plugin manifests use 1.3.0. Both marketplaces use `catalog-M74-m110-p162-n61`.

## File Inventory

Modified files:

- `.agents/plugins/marketplace.json`
- `.claude-plugin/marketplace.json`
- `dist/codex/plugins/monitor-pr/.claude-plugin/plugin.json`
- `dist/codex/plugins/monitor-pr/README.md`
- `dist/codex/plugins/monitor-pr/skills/monitor-pr/SKILL.md`
- `plugins/monitor-pr/.claude-plugin/plugin.json`
- `plugins/monitor-pr/README.md`
- `plugins/monitor-pr/skills/monitor-pr/SKILL.md`

No new, deleted, or renamed files are part of the reviewed commit. This review document is a subsequent local artifact.

## Notable Changes

The default foreground invocation now stops after three ticks even when the PR remains pending. This is an intentional user-visible behavior change, documented as a checkpoint. No dependencies, executable helpers, CI configuration, or permission allowlist entries change.

The scheduled-task capability is supported by current official documentation: in-chat tasks retain chat context and support minute-based follow-up loops. Standalone tasks instead start new chats, so the branch's explicit in-conversation destination matters. See [Scheduled tasks](https://learn.chatgpt.com/docs/automations?surface=app).

## Plan Compliance

No plan filename matches `monitor-pr-loop-in-codex` under `docs/plans/`, including `todo/` and `done/`. The older monitor-pr plans describe other work and were not treated as this branch's plan. Plan compliance is therefore not evaluated.

## Code Quality Assessment

**Verdict: Needs changes before merging.** The main continuation guidance is clear, and metadata and mirrors are consistent. Two operational gaps remain in the new wait-mechanism contract.

### Issues to Address

1. **P2: Define restoration of watch state at a foreground checkpoint.** Location: `plugins/monitor-pr/skills/monitor-pr/SKILL.md:93`. The new default interruption asks the user to rerun an invocation and prints generic counters, but the workflow never says to recognize that invocation as a continuation, restore prior state, or retain the non-counter guards. For example, a checkpoint immediately after requesting Copilot review must retain the requested head SHA and post-request quiet count; restarting step 1 without that state can request the same review again instead of escalating. The processed review IDs, per-check repair attempts, confirmation review and SHA, and original options also affect later dispatch. Specify a checkpoint schema and resume procedure that restores these values, resets only the per-invocation foreground tick count, and preserves `--no-fix`, `--confirm-clean`, the round budget, and any interval override. State whether resumption requires the same conversation or an explicit saved state artifact.

2. **P2: Restore a defined fallback when scheduling is unavailable or rejected.** Location: `plugins/monitor-pr/skills/monitor-pr/SKILL.md:89-91`. The previous instruction explicitly used foreground polling when `ScheduleWakeup` was unavailable or rejected. The replacement lists a Claude preference and a Codex scheduled-task path, but limits the foreground path to Codex CLI and OpenCode. Consequently, a Claude session without `ScheduleWakeup`, or a failed task creation on a scheduled surface, has no prescribed continuation path. Make selection depend on successful scheduler availability and creation; otherwise use the bounded foreground loop and announce that mechanism. Apply the same checkpoint semantics and tick limit to the fallback.

Both findings apply to the generated Codex skill as well. Fix canonical sources and regenerate rather than editing generated files.

### Strengths

- Clearly distinguishes an active foreground wait from continuation after a final response.
- Preserves exact-head Copilot readiness and the existing four-axis criteria.
- Requires cancellation of scheduled work on readiness and escalation.
- Documents the new option in both the skill and README, with an appropriate minor version bump and matching catalog state.

### Suggestions

Add a manual scenario checklist for reaching a checkpoint after requesting review, resuming with `--no-fix` and `--confirm-clean`, and handling scheduler rejection. The existing Scrut suite exercises repository helpers; it does not demonstrate agent-level continuation behavior.

### Validation

- `make lint`: passed, including Markdown, Prettier, ShellCheck, shfmt, and actionlint.
- `make validate`: passed, including canonical metadata and generated mirror validation.
- `bin/compute-catalog-state`: returned the committed `catalog-M74-m110-p162-n61`.
- `git diff --check`: passed.
- `make test-scrut`: passed, 423 succeeded, 0 failed, and 0 skipped.

No live monitor watch or scheduled task was created during this review. Structural checks cannot verify the continuation behavior described in the skill.

## Resolution

All three actionable items were accepted on 2026-09-16. The assessment above describes the reviewed commit; this section tracks subsequent remediation.

| #   | Item                                | Status   | Implementation                                                                                                                                                                                                                                                                                                              |
| --- | ----------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Restore foreground checkpoint state | Resolved | The bundled checkpoint reference specifies all watch fields, same-conversation or pasted-checkpoint resumption, restored options and guards, and a fresh snapshot before dispatch. Only the invocation tick count resets on resume.                                                                                         |
| 2   | Define scheduler fallback           | Resolved | Successful scheduler creation is required for scheduled operation. Unavailable, rejected, or failed scheduling selects bounded foreground polling, with cancellation of any previous scheduled continuation before switching.                                                                                               |
| 3   | Add manual scenario checklist       | Resolved | [Continuation verification](../plans/todo/2026-09-16-monitor-pr-continuation-verification.md) records build confirmation, checkpoint and option restoration, review-request guards, confirmation retention, and scheduler fallback scenarios. Harness readings remain untestable here, with requirements recorded per step. |

Items 1 and 2 are committed in `e565ff5e` (`fix: preserve monitor state across foreground checkpoints`). The monitor-pr patch version is 1.3.1; catalog state is `catalog-M74-m110-p163-n61`. Canonical and generated manifests match, all plugins remain registered, and the branch's overall bump from 1.2.0 to 1.3.1 includes the original continuation capability plus these fixes.

Remediation validation:

- `make build`: passed, regenerating the Codex and OpenCode mirrors. The protected `.agents` catalog required elevated sandbox access.
- `make test-all`: passed, including lint, validation, and 423 Scrut cases with 0 failed and 0 skipped.
- `bin/compute-catalog-state`: matched `catalog-M74-m110-p163-n61`.
- `git diff --check` and the staged diff whitespace check: passed.

The checklist is implemented, but its live harness scenarios were not run. Each step records why it is untestable in this remediation session and which environment is needed for an observed result.
