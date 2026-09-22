# Observe Copilot findings and format drift before monitor-pr dispatches

Tracks #461.

## Context

`monitor-pr` step 4 dispatches to step 7b when "Copilot reviewed the current head with open threads, review-body findings, or review-body format drift". None of those three conditions is observable from the step 3 snapshot: its Copilot probe returns only `id`, `commit_id`, `submitted_at` and `state`, and no step before dispatch runs `resolve-copilot-threads fetch` or `fetch-reviews`, or computes `hasFormatDrift`. The agent running the watch has been filling the gap ad hoc. When it does not, a current-head review with findings looks the same as a clean one, and a drift-only review falls through to the wait branch, which is the outcome #459 set out to prevent.

The Ready Criteria Copilot row and the README sign-off paragraph already describe the axis in terms of `fetch` and `fetch-reviews`, so the documented contract is correct and only the observation is missing.

**Intended outcome:** step 3 observes the three signals with read-only commands, step 4 dispatches on what it observed, and the Dependabot and `--no-fix` paths get the same observation without invoking anything that pushes.

## Design decisions

| Decision                      | Choice                                                                                                                                                                                                                                                                              |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Observation mechanism         | `monitor-pr` ships a byte-identical copy of `resolve-copilot-threads` and runs its read-only `fetch` and `fetch-reviews` commands in step 3 (user decision)                                                                                                                         |
| Why a copy                    | Rule 18 of `bin/validate-plugins` requires every `${CLAUDE_PLUGIN_ROOT}/scripts/NAME` reference in a `SKILL.md` body to resolve inside its own plugin and rejects version-blind locator globs, so the two plugins cannot share one file. Same pattern as the three worktree helpers |
| Why not a prose probe         | A conservative clean recognizer still needs four separate body checks (suppressed marker, table severity items, nested severity summaries, exact verdict heading) to avoid reading a `ccr-overview-v2` approval that carries table findings as clean                                |
| Why not resolver-only routing | It posts one no-op summary comment per clean head SHA, and Dependabot and `--no-fix` still need a read-only probe, so two mechanisms end up maintained                                                                                                                              |
| Drift guard                   | One `cmp` testcase in `tests/scrut/repo-tooling.md`, beside the existing three                                                                                                                                                                                                      |
| Version                       | `monitor-pr` 1.4.0 to 1.5.0 (new capability). `resolve-copilot-pr-feedback` is unchanged, so it does not move                                                                                                                                                                       |

## Changes

### 1. Bundle the script

Copy `plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads` to `plugins/monitor-pr/scripts/resolve-copilot-threads`, preserving the executable bit. Do not modify either copy.

### 2. `plugins/monitor-pr/skills/monitor-pr/SKILL.md`

**Step 3, after the existing metadata probe.** Add a short script-setup note (the `${CLAUDE_PLUGIN_ROOT}` placeholder is substituted by Claude Code; on a harness that does not substitute it, locate the shipped copy with `**/monitor-pr/**/scripts/resolve-copilot-threads`, confirm it with `test -x`, and reuse that absolute path), then the feedback probe, run only when the metadata probe's `commit_id` equals `headRefOid`:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/resolve-copilot-threads" fetch OWNER REPO PR_NUMBER |
  jq -c '{openThreads: length, locations: [.[].location]}'
```

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/resolve-copilot-threads" fetch-reviews OWNER REPO PR_NUMBER |
  jq -c --argjson review_id REVIEW_ID '
    [.[] | select(.id == $review_id)] | last
    | {id, url, hasFormatDrift, findings: (.findings | length)}'
```

Points the prose has to make:

- **Both commands are read-only.** Neither writes to the PR, so the probe runs on Dependabot PRs and under `--no-fix` exactly as it does anywhere else.
- **Project the fields, do not print the whole result.** `fetch-reviews` returns every Copilot review with its complete `reviewBody`, and a watch takes this snapshot on every tick.
- **Gate on the current head.** Running the probe when the newest review is stale wastes two calls on a tick that goes to step 7a regardless. `fetch` reports every unresolved Copilot thread on the PR, whatever review opened it, so gating it this way loses nothing the Ready Criteria ask for.
- **Match on `id`, not on the head SHA.** `--confirm-clean` produces two reviews against one head, and only the `id` separates them. `fetch-reviews` carries no `commit_id`, which is why the metadata probe stays.
- **A `null` result is not a failure.** `fetch-reviews` skips a review with an empty body, so a review the metadata probe found can be absent here. Treat that as no review-body findings and no drift, and keep the thread signal.
- **`fetch-reviews` refetches the reviews endpoint the metadata probe already read.** That is accepted so each command stays standalone and copy-pasteable, and it only happens on ticks where a current-head review exists.

**Step 4, the Copilot findings condition.** Restate it as: Copilot reviewed the current head, the step 3 feedback probe reported open threads, review-body findings, or format drift, **and** step 7b has not already been invoked for that review `id`. The `id` clause is what stops an immutable review-body finding from re-dispatching on every later tick; it is the guard step 7b already documents, lifted into the condition that reads it.

Also update the Dependabot sentence under the dispatch list to name the probe rather than an unobservable condition.

**Ready Criteria, Copilot row.** Restate the axis against the probe: a current-head review exists, the probe reports no open threads and no format drift, and either it reports no review-body findings or step 7b has already returned `Completed` or `No unresolved Copilot feedback` for that review `id`.

**Step 7b, the once-per-review guard and the escalation rule.** Keep the `id` guard. Rewrite the escalation rule, which today keys on the unobservable condition: after a `Completed` or `No unresolved Copilot feedback` report for review `id` R, escalate per step 9 when the next snapshot's probe still reports open threads, or still reports format drift for R. **Review-body findings are the exception and must not escalate.** Review bodies are immutable, so a finding the resolver just recorded as handled still appears in that body and always will; the processed-review record, not the probe, is what clears it. Without this carve-out, making the condition observable would turn every noted review-body finding into a false escalation.

**Step 7d, `--confirm-clean`.** Judge the confirming review by the probe: no open threads, no format drift, and no review-body findings. When the confirming review does carry findings, step 4 dispatches it to step 7b under its own `id`, and the resolver's outcome decides the pair: `No unresolved Copilot feedback` means everything in that body was already recorded, so the pair completes; `Completed` means the review surfaced something real, so reset the count per the existing rule.

**`--no-fix`.** State that the probe still runs, and only the step 7b invocation is replaced by a report.

### 3. `plugins/monitor-pr/skills/monitor-pr/references/checkpoint.md`

Extend the Snapshot row to carry the probe result alongside the review identity: open-thread count, review-body finding count, and the format-drift flag for the current-head review.

### 4. `plugins/monitor-pr/README.md`

- Numbered item 3 of "What It Does": say the skill observes the findings and drift with a read-only probe before dispatching, rather than implying the dispatch is free-standing.
- "What counts as a Copilot sign-off": say where the thread fetch and review-body fetch run.
- "Recommended Permissions": add `Bash(bash \"*/resolve-copilot-threads\" *)`, the same path-agnostic rule `resolve-copilot-pr-feedback` recommends, so one entry covers both copies.

### 5. `plugins/monitor-pr/.claude-plugin/plugin.json`

Version 1.4.0 to 1.5.0.

### 6. Repository documentation

- `plugins/AGENTS.md`: extend the byte-identical helpers bullet to cover the `resolve-copilot-threads` pair alongside the three worktree helpers.
- `docs/plugin-development.md`: update the duplicated-scripts paragraph and the rule 18 paragraph, which currently name only `resolve-copilot-pr-feedback` as shipping `resolve-copilot-threads`.

### 7. Tests and wiring

- `Makefile`: add `MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN` to `SCRUT_ENV`.
- `.github/workflows/ci.yml`: add the same entry to the `scrut-env` block.
- `tests/scrut/repo-tooling.md`: add a section and a `cmp` testcase holding the two copies byte-identical, in the style of the three worktree testcases.
- `tests/scrut/resolve-copilot-threads.md`: add one testcase running `parse-reviews` through the `monitor-pr` copy over an existing fixture, so the shipped file is proven to run rather than only proven to match.

### 8. Regenerate

Run `make build` and commit the `dist/` results. `bin/list-shell-scripts` discovers the new script on its own, so no lint glob changes.

## Verification

1. `make build` leaves no further diff on a second run, and `dist/codex/plugins/monitor-pr/scripts/resolve-copilot-threads` exists.
1. `make test-all` passes: lint, validate (rule 18 resolves the new reference to a shipped executable), and scrut including the new `cmp` and `parse-reviews` testcases.
1. The `check-versions` skill reports `monitor-pr` at 1.5.0 with no catalog drift.
1. Plant the defect: edit one byte of `plugins/monitor-pr/scripts/resolve-copilot-threads` and confirm the new `cmp` testcase fails, then restore it.
1. Run the probe commands by hand against a real PR that has a current-head Copilot review, and confirm the projected output names the review, its finding count, and its drift flag.
1. Read step 4 against the probe output for three cases and confirm each reaches the intended branch: a clean current-head review (axis clean), a review with a review-body finding already processed under its `id` (axis clean, no re-dispatch, no escalation), and a drift-only review (step 7b).

## Out of scope

- Adding `commit_id` to the `parse-reviews` output, which would let step 3 collapse to a single Copilot call. That changes `resolve-copilot-pr-feedback` and its scrut expectations, and belongs in its own issue.
- Any change to the resolver's parsing, classification or summary rules.
