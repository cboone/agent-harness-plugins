# monitor-pr: dispatch conditions that are ready to process

Addresses [#385](https://github.com/cboone/agent-harness-plugins/issues/385).

## Context

Step 4 of the `monitor-pr` skill dispatches on the first matching condition in an ordered list. Condition 6, "checks pending or running: wait, then return to step 3", sits above condition 8, "Copilot reviewed the current head with open threads or findings". Any in-flight check therefore stalls the Copilot cycle, even when there is actionable feedback sitting at the current head waiting to be resolved.

That trade goes the wrong way. A pending check is not something the skill can act on; Copilot feedback is. Resolving the feedback ends in a push that supersedes the in-flight check run, and an extra check run is cheaper than serializing the Copilot cycle behind every one. Each Copilot round already invalidates the previous review by construction, so the loop was always going to come back around.

The ordering appears to be incidental rather than considered: the step's own rationale sentence justifies only conditions 2 and 3 preceding condition 5, and the original planning document carried the same order with no comment.

## Approach

Sort the list so that every numbered condition is work the skill can do now, and demote waiting to an explicit fallthrough at the end. This reaches the outcome the issue asks for while leaving "take the first match" as a mechanical rule, rather than introducing a per-condition readiness test the agent has to apply correctly on every tick.

The promotion covers the findings condition only. The distinction that decides it:

- **Processing an existing review is durable.** The fixes land whatever the checks go on to do, so there is no reason to serialize it behind a check the skill cannot influence.
- **Requesting a new review is perishable.** Any push invalidates a review rendered against the old head, and it spends a round against the step 7c budget either way. Both request paths (conditions 7 and 8) therefore keep a passing-checks precondition.

## Changes

### 1. `plugins/monitor-pr/skills/monitor-pr/SKILL.md`, step 4

Rewrite the lead paragraph to state that waiting is a fallthrough, not a condition, and expand the one-line ordering rationale into two bullets covering the branch-sync ordering and the durable-versus-perishable distinction above.

Then, in the list:

- Delete "Checks pending or running: wait, then return to step 3" from position 6.
- Promote "Copilot reviewed the current head with open threads or findings" above the old wait, and note that running checks do not hold it back.
- Add `Checks pass` to the `--confirm-clean` condition. It was gated only by list position; the precondition makes today's behavior explicit now that nothing above it blocks it.
- Point the two Copilot conditions at **step 7b** and **step 7a** by name instead of both saying "go to step 7". They are neighbors now, and the bare step number no longer distinguishes them.
- Append the fallthrough: "Nothing above matched: wait, then return to step 3."

### 2. `plugins/monitor-pr/skills/monitor-pr/SKILL.md`, step 2

The interval table has rows for "Checks actively running" and "Awaiting a Copilot review at the current head". Dispatch order used to guarantee only one applied; the fallthrough can satisfy both at once. Add a tie-break: when more than one row applies, take the shorter wait.

### 3. `plugins/monitor-pr/skills/monitor-pr/SKILL.md`, step 7b and Error Handling

Guard against unbounded re-invocation. Nothing currently stops step 7b from running against the same review repeatedly: if `resolve-copilot-pr-feedback` reports success while those threads stay open, step 3 re-snapshots, the findings condition matches again, and 7b runs again, with no new review and no push to break the cycle. The step 7c budget does not bound it, because it counts completed reviews rather than invocations.

The defect predates this change, but the reorder makes it reachable during the check window rather than only after checks conclude. Add a rule to step 7b capping invocation at once per review, escalating per step 9 instead, and a matching bullet to Error Handling.

### 4. `plugins/monitor-pr/README.md`

Its "What It Does" list paraphrases the same priority order. Swap the two Copilot bullets to match the new order, note that the findings path does not wait on checks, and add the new escalation to the "It stops and asks" paragraph.

### 5. Versioning and generated trees

- `plugins/monitor-pr/.claude-plugin/plugin.json`: `1.1.0` to `1.1.1`. A patch, per the repo's rules: prompt adjustment, not a new capability.
- `.claude-plugin/marketplace.json`: mirror that version into the `monitor-pr` entry, then recompute `metadata.version` with `bin/compute-catalog-state`. It moves from `catalog-M64-m94-p143-n52` to `catalog-M64-m94-p144-n52`.
- Regenerate both mirrors with `bin/build-codex-marketplace` and `bin/build-opencode-mirror`, and commit the results. The Codex mirror rewrites the skill description from the marketplace entry, so it will not match the source file byte for byte; that is expected.

## Verification

1. `make validate` (`bin/validate-json` plus `bin/validate-plugins`, which enforces marketplace agreement, the catalog state tag, and generated-tree freshness).
1. `make lint` for markdownlint and Prettier over the edited Markdown.
1. `make test-all` before opening the PR.
1. Read step 4 back as a dispatcher would: confirm every numbered condition has somewhere to go, and that the conditions below any match are mutually exclusive with it. When condition 7 matches, Copilot is missing or stale, so 8 and 9 (both requiring a review at the current head) cannot match; when 8 matches, 9 cannot, because one clean review does not satisfy `--confirm-clean`. That mutual exclusivity is what makes the sorted list sufficient without a runtime readiness test.
1. Exercise it against a live PR where Copilot has reviewed the current head with findings while a check is still running, which is the case that prompted the issue. The skill should dispatch to step 7b rather than waiting.
