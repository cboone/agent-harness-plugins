# Reduce Copilot rounds after a PR opens

## Context

An analysis of 132 PRs opened from 2026-09-29 to 2026-10-09 (55 in client repositories, 77 in personal ones) found 499 Copilot reviews: median 3 rounds per PR, mean 3.8, p90 7, and 36 PRs with five or more. Every review ran at Lite effort, which stays the setting.

What the data shows:

- **The pre-PR review is working; the tail comes after it.** Round 1 averaged about 1.1 findings per PR, but rounds 2 through 8 kept producing about 0.8 new findings per round. About two thirds of all findings arrived after round 1.
- **Late findings are not trivial.** The share Copilot labeled High was 33% in round 1 and 53% in rounds 6 and later. Nineteen PRs drew a High in round 4 or later, and 15 times a High appeared after two or more rounds without one.
- **Most of the tail comes from our own fixes.** Of the inline findings from round 2 onward, about 55% were in code or text the previous fix had just added, about 15% were siblings of an issue a fix had repaired in only one place, and about 30% were older code that earlier rounds had not flagged. The resolver commits a fix, runs `lint-and-fix` and pushes, so no local review ever sees fix code.
- **Narrow fixes produce chains.** #563 in this repository spent 19 rounds on successive bypasses of one path-safety check. Another PR spent 14 rounds patching a redaction blocklist one input form at a time before switching to logging client-supplied IDs only in their exact known formats. #545 and several other PRs, mostly sanitizers, parsers and version comparisons, show the same shape.
- **Rounds scale with size.** Mean rounds by diff-size quartile: 1.8, 3.3, 4.1, 5.9.

Recurring patterns Copilot finds that local review misses, with the share arriving after round 1:

| Pattern                                                                                                              | Approximate count | Later rounds |
| -------------------------------------------------------------------------------------------------------------------- | ----------------- | ------------ |
| A blocklist, regex or sanitizer bypassed by a sibling form of the same input                                         | 55                | 75%          |
| Docs, plans, READMEs, PR text or comments disagree with the code or each other                                       | 90                | 65%          |
| A parallel path, mirror copy or consumer not updated with its sibling                                                | 22                | 60%          |
| Time-window and boundary arithmetic: gaps, overlaps, inclusive edges, cursors                                        | 18                | 55%          |
| Agent-prose control flow: rule placed after the step that needs it, unhandled branch, conflicting rules across files | 25                | 55%          |
| Concurrency and stale writes: a late retry overwrites newer state, check-then-act                                    | 22                | 50%          |
| A validator that accepts semantically invalid input: nested unknown keys, duplicate keys, future times               | 25                | 50%          |
| Absent, empty, partial or paginated data treated as a clean pass                                                     | 25                | 45%          |
| Untrusted data reaching a shell, log, email, argv or workflow command                                                | 22                | 45%          |
| A test that cannot fail, does not run or is not isolated                                                             | 15                | 40%          |
| A wrong value crashes with a traceback instead of being reported                                                     | 18                | 35%          |
| Config or commands never run against the real platform                                                               | 32                | 25%          |
| A trust boundary claimed ("read-only", "least privilege") but not enforced                                           | 20                | 20%          |

The best-performing pre-PR sequence so far is `pr-review-toolkit`, fixes and suggestions, targeted re-reviews, `simplify` and `trim-comments`, then `pr`. This plan builds on that sequence and leaves it in place.

Follow-ups filed separately: [#580](https://github.com/cboone/agent-harness-plugins/issues/580) (roll out `REVIEW.md`) and [#581](https://github.com/cboone/agent-harness-plugins/issues/581) (check agent instructions against Copilot instructions).

## Goals

1. Every fix pushed in response to Copilot is reviewed locally first.
1. Fixes address the whole category of a finding, and repeated sibling findings escalate to a design question instead of another patch.
1. Each fix push leaves docs, plans, READMEs and the PR body consistent with the code.
1. The patterns above become an explicit checklist used both before the PR and on fix diffs.
1. Plans favor smaller PRs, and isolate high-risk code (sanitizers, parsers, validators) into its own PR.
1. Past an agreed round, findings that do not need to block are tracked as follow-ups instead of driving more rounds.

## Design decisions

- **One new skill, `review-anti-patterns`, holds the checklist and the scoped review procedure.** The name says what it looks for: recurring defect shapes, not patterns in general. It reviews a given diff range (the whole branch by default, or a fix diff) against the checklist, read-only, and returns findings in the same shape `review-until-clean` uses. It can run as a "targeted re-review" step before `pr`. The resolver calls it on each fix diff. One source avoids keeping byte-identical copies of the checklist in several plugins.
- **The checklist is phrased as reviewer questions, not categories.** For example: "For each rejected input form, what sibling forms exist (encodings, whitespace runs, case, IPv6, CRLF, Unicode, symlinked parents)? Would an allowlist or a structural parse remove the whole class?" and "What does this return for missing, empty, second-page and duplicate-key input?" Each item names the evidence that settles it.
- **Agent-prose items are first-class.** `SKILL.md` and reference files are reviewed as programs: trace each branch to a terminal status, check every rule appears before the step that depends on it, and compare the commands a skill runs with its permission block.
- **The fix review is bounded.** The resolver runs one review of the fix diff, fixes what it finds at Important severity, and re-reviews only the lines that second fix changed. It does not loop until clean. That keeps a Copilot round from turning into an open-ended local loop.
- **Sibling-chain escalation is about content, not counts.** `monitor-pr` step 7c says not to read the shape of finding counts as a signal, and that stays. The new rule fires on substance: when a finding is a sibling of one already fixed on this PR (same function or check, another input form or branch), the resolver stops patching and escalates with a design option, such as an allowlist, a structural parser or a narrower contract.
- **Late rounds triage instead of blocking.** `monitor-pr` gains `--triage-after <n|never>`, default 5 (the data's median is 3 and p90 is 7). From round `n + 1`, High findings still block, both in lines this PR changed and previously missed High findings in unchanged code. Medium and Low findings become follow-up issues through `create-deferred-issues` and do not block. `--triage-after never` restores the current behavior.
- **The fix review runs in a read-only subagent** where the harness has one (Claude Code). Elsewhere the agent reviews its own fix diff against the checklist. `review-until-clean`'s Codex and Claude backends are not used here, to keep each round short.
- **No change to Copilot effort or instruction plumbing here.** Lite stays. Instruction rollout and conflicts are #580 and #581.

## Phases

Each phase lands as its own PR, in this order, so the round count of each can be measured against the baseline.

### Phase 1: measurement script

Add `bin/copilot-rounds-report`, a Bash script that reproduces this analysis for a date range and a set of owners: PRs, Copilot rounds per PR (median, mean, p90), findings per round, High share per round, findings-free rounds and the client and non-client split. It reads with `gh api graphql` and `jq` only. The baseline below is its output for the analyzed range, so later runs compare like with like:

```bash
bin/copilot-rounds-report --owner cboone --owner CLIENT_ORG --since 2026-09-29 --until 2026-10-09 --author cboone --client-owner CLIENT_ORG
```

| Group      | PRs | Rounds | Median | Mean | p90 | 5+ rounds | Round 1 findings | Later findings | Findings-free rounds | Last round approves |
| ---------- | --- | ------ | ------ | ---- | --- | --------- | ---------------- | -------------- | -------------------- | ------------------- |
| Client     | 55  | 203    | 3      | 3.7  | 7   | 15        | 57               | 92             | 76                   | 29                  |
| Non-client | 77  | 303    | 3      | 3.9  | 7   | 23        | 88               | 201            | 93                   | 36                  |
| All        | 132 | 506    | 3      | 3.8  | 7   | 38        | 145              | 293            | 169                  | 65                  |

Findings per review by round: 1.1, 0.8, 0.9, 0.7, 0.9, 0.6, 0.8 for rounds 1 to 7 and 0.7 for round 8 on. High share of rated findings by round: 33%, 39%, 29%, 35%, 52%, 63%, 54%, then 47%; every finding in the range carried a severity badge. The script matched 133 PRs, one of which had only a Copilot error notice, and set aside 5 such notices in all. It was run on 2026-10-10, so open PRs from the range had gained rounds since the first count.

1. `bin/copilot-rounds-report` (load `write-bash-scripts` first).
1. Scrut coverage in `tests/scrut/` with a stubbed `gh` that serves fixture JSON, registered in the Makefile's `SCRUT_ENV` and CI's `scrut-env` list per `tests/AGENTS.md`.
1. `bin/AGENTS.md`: one line naming the script and stating it is not a merge gate.

### Phase 2: `review-anti-patterns` skill

1. New plugin via the `create-plugin` skill, starting at `1.0.0`, with catalog entry, README and Codex/OpenCode mirrors from `make build`.
1. `SKILL.md`: options `--range <rev-range>` (default: merge base with the default branch through the working tree), `--files <paths>` and `--severity important|nit`. Workflow: resolve the scope, read the changed hunks with enough surrounding context to see parallel paths, walk the checklist, return findings with the evidence each item asked for, and never edit.
1. `references/checklist.md`: the thirteen patterns as reviewer questions, each with what settles it and a short example from the analysis. Group them into code, agent prose and docs consistency so a scope that is all Markdown skips what cannot apply.
1. `references/mechanical-checks.md`: commands that settle the platform pattern where the project has them, such as `terraform validate`, `gcloud ... --validate-only`, `actionlint`, GraphQL schema validation, running each documented command once, and `plant-defects` for tests that cannot fail. The skill runs only checks the project already supports and reports the rest as unverified.

### Phase 3: resolver changes

All in `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md` unless noted.

1. **Fix the class.** In step 4's Valid Concerns and the review-body Valid row: before editing, state the general problem behind the finding, search the branch and its consumers for every instance (same shape elsewhere, parallel branches, mirror copies, callers), and fix them together. The summary row names the class and the extra sites fixed.
1. **Escalate sibling chains.** New rule in step 4: when a finding is a sibling of one this PR already fixed, record it, do not patch it, and end with a `Partial` status that names the chain and proposes a design option. `monitor-pr` already escalates on `Partial`.
1. **Consistency sweep.** New step between 4 and 5: list each identifier, flag, count, path and stated behavior the fixes changed, search docs, plans, READMEs, comments and the PR body for them, and correct whatever disagrees. Edit the PR body with `gh pr edit --body-file` when it disagrees.
1. **Review the fixes.** New step before step 5: run `review-anti-patterns --range <head-before-fixes>..HEAD` and fix Important findings, then review only the lines that second fix changed. Findings it declines go in the summary with a rationale. This step is skipped when the run changed no files.
1. Skill dependencies: add `review-anti-patterns` as required.
1. README: describe the three new steps and the escalation.
1. Version: `2.0.0` to `2.1.0`.

### Phase 4: `monitor-pr` changes

1. Step 7b: treat the resolver's sibling-chain `Partial` as a judgment escalation in step 9, quoting the chain and the proposed design option.
1. Add `--triage-after <n|never>` to Options, Ready Criteria and step 7c, with the blocking rules from Design decisions. Deferred findings are filed in one approved batch through `create-deferred-issues` and listed in the terminal report.
1. README: options table, the new escalation and the triage policy.
1. Version: minor bump.

### Phase 5: smaller, safer PRs

1. `address-issue` step 6: when a plan changes independent areas, propose splitting it into separate PRs. Put sanitizers, parsers, validators and security boundaries in their own PR, and prefer an allowlist or structural parse in the plan itself.
1. `review-plan`: add the same checks as plan review findings.
1. Versions: patch or minor bumps per the plugin development guide.

## Verification

- After each phase: `make build`, then `make test-all`; observe the final result. Run the `check-versions` skill before each PR.
- Phase 2: run `review-anti-patterns` against the fix commits of two of the redaction chains from the analysis and confirm it flags the sibling forms Copilot found in the following rounds. Those PRs are private, so this check runs locally and its results stay out of this repository.
- Phase 3: read the resolver end to end for the paths: a single Valid finding, a finding with extra instances, a sibling-chain escalation, and a run that changes no files.
- After the changes have been in use across a comparable number of PRs, rerun `bin/copilot-rounds-report` and compare rounds per PR, findings per round after round 1, and the fix-induced share against the baseline.
