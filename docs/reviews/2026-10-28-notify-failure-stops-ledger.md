# Failure-stop notification ledger

## Authority and state

- Workstream: notify banners for error and refusal stops, both harnesses, [issue 642](https://github.com/cboone/agent-harness-plugins/issues/642).
- Worker: `642-notify-failure-stops`; conductor: TOOLING. Branch: `feat/642-notify-failure-stops`.
- Go-ahead: Inbox, “Tooling next batch, Oct 28 evening,” 2026-10-28, 7:38 PM ET, build through a ready PR. TOOLING merges.
- Base and initial HEAD: `a2e56c535ed6326cc8d531d945fbb6c627a9b335`, also the merge base with `origin/main` at investigation start.
- Repository verified active, non-fork, owned by `cboone`. Issue body and all comments read. `corepack yarn install --immutable` passed.
- Scope decision: Inbox, 8:41 PM ET, relayed by TOOLING: one shared plan, then a linked pair. This branch implements Claude banners through a ready PR. Codex's event-stream watcher follows on a separately placed branch; obtain project, handle, branch, and base from TOOLING and run `check-worktree-place` first. No live installation or configuration change. Checkpoint by 9:40 PM ET; TOOLING parks at 9:45 PM ET and resumes after 8 AM ET.
- Shared plan committed at `docs/plans/todo/2026-10-28-shared-turn-failure-notifications.md`. Claude implementation and committed stub fixtures now exercise error/refusal/approval separation, all tiers, focus/background/completion suppression boundaries, delayed persistence, stale metadata, identity fallback, and subagent exclusion.

## Claude Code evidence

Installed runtime: Claude Code 2.1.312. `claude --help` confirmed `--setting-sources` and `--settings`. A print-mode probe used a separate `CLAUDE_CONFIG_DIR`, empty setting sources, explicit scratch settings containing capture-only hooks, an empty strict MCP configuration, and a local HTTP stub. No real credentials or installed hooks were used. The local stub returned a labeled HTTP 400 API error. The process exited 1 and captured this event:

```json
{
  "hook_event_name": "StopFailure",
  "error": "unknown",
  "last_assistant_message": "API Error: 400 Labeled notify fixture API error"
}
```

The payload also included `session_id`, `transcript_path`, `cwd`, `prompt_id`, and `effort`. No `Stop` event was captured. The runtime's `fRr` implementation constructs `StopFailure` with `error`, optional `error_details`, and `last_assistant_message`, matching on the error value. Runtime refusal detection checks `message.stop_reason === "refusal"`; its `qn` helper requires `isApiErrorMessage` on assistant refusals and separately recognizes `model_refusal_no_fallback` system records. The runtime schema and `s1n` conversion preserve that system subtype in transcripts. No safeguard refusal was provoked. Approval waits use fixtures rather than a live permission prompt.

## Codex evidence

Installed runtime: codex-cli 0.165.0. A live `codex app-server generate-json-schema --experimental` run generated the supported hook enum, including `Stop`, `PermissionRequest`, and `PostModelRequest`, but no `StopFailure`.

An isolated `codex exec --json` probe used a separate `CODEX_HOME`, a scratch repository, and a local HTTP provider stub without credentials or hooks. HTTP 400 produced `thread.started`, `turn.started`, `error`, and `turn.failed`, exiting 1. No banner was posted.

Exact-version source confirms the dispatch boundary:

- [Turn execution, tag rust-v0.165.0](https://github.com/openai/codex/blob/rust-v0.165.0/codex-rs/core/src/session/turn.rs): `Stop` runs in the successful result branch around line 737. Terminal errors emit an error and end the turn around lines 903 to 924 without running `Stop`.
- [Model request hook inputs](https://github.com/openai/codex/blob/rust-v0.165.0/codex-rs/hooks/src/events/model_request.rs): `PostModelRequest` supplies `status`, a nullable string `error`, and token usage. It supplies no terminal-turn flag or typed refusal discriminator.
- The turn implementation emits that hook inside `try_run_sampling_request`, before the outer retry decision around lines 1805 to 1867. Treating every failed request as a stopped turn would produce false banners for recoverable failures.

A watcher can observe app-server `error` notifications with `willRetry` and `turn/completed` with `turn.status == "failed"` and `turn.error`. Typed `codexErrorInfo` includes `cyberPolicy` and `misalignmentPolicyViolation`; not every policy error's public mapping has been verified. Approval requests use separate `item/commandExecution/requestApproval`, `item/fileChange/requestApproval`, and `item/permissions/requestApproval` methods, while thread status exposes `waitingOnApproval` and `waitingOnUserInput`. These are protocol surfaces, not a terminal-failure plugin hook. Approval-wait and refusal fixtures remain unrun.

## Delivery and validation

The terminal-event gap was reported as a scope stop, then resolved by the linked-pair decision above. This PR adds only Claude's failure hook; Codex behavior remains documented pending the watcher follow-on. The paired issue stays open until both halves land.

Scratch evidence is retained at `/tmp/notify-642-runtime-evidence/`. No real configuration, installed hooks, software installation, or live banners changed. A fresh read-only Codex fact check with `gpt-6.1-sol`, low effort, exited 0 with a non-empty complete reply, corroborating the terminal-event gap and watcher surfaces. Its reply and log are `codex-answer.txt` and `codex-answer.log` in that directory. This was a harness-fact check, not an implementation review.

Notify advances 4.2.1 to 4.3.0 for the new banner capability. `make build`, shell formatting, ShellCheck, and the new Scrut document passed (3 testcases). Full checks and local reviews remain pending.

## Planted defects

| Planted defect                                  | Instrument            | Observed result                        | Regression coverage              |
| ----------------------------------------------- | --------------------- | -------------------------------------- | -------------------------------- |
| Disable structured refusal detection            | Scrut failure banners | Exit 50; refusal titles became Error   | Refusal titles in both cases     |
| Apply worker completion suppression to failures | Scrut failure banners | Exit 50; worker banners missing        | Worker error and refusal banners |
| Keep refusal metadata across a new prompt       | Scrut failure banners | Exit 50; new-turn title became Refusal | New-turn error title             |

## Structural review loop

Nit round: fresh read-only Codex anti-patterns and report-only simplify, both gpt-6.1-sol/high/872000. Both completed with exit 0 and validated output; before/after scope comparison showed no writes. Artifacts: /tmp/notify-642-checks.cLIarv/. An initial simplify launch lacked its rendered scope because the repository-local helper refused self-review; stopped its recorded PID 55633 (exit 143), recorded as incomplete, then rendered through the installed helper. The complete replacement is simplify-valid.json; anti.json is the anti-pattern report.

| Reviewer's title                                                                        | Reviewer's label | Our severity                                           | Take or record                                           | Review again                           |
| --------------------------------------------------------------------------------------- | ---------------- | ------------------------------------------------------ | -------------------------------------------------------- | -------------------------------------- |
| Absent or partial data: unavailable metadata permits raw refusal text in banners        | important        | Important: violates the refusal text omission contract | Taken: all invalid_request bodies use fixed descriptions | Yes, behavior                          |
| Sibling input forms: metadata messages incorrectly clear a current refusal              | important        | Important: current refusal mislabeled as error         | Taken: reuse TURN_JQ.kind for all prompt classification  | Yes, behavior                          |
| Tests that cannot fail: the background fixture does not exercise background suppression | nit              | Nit: missing boundary coverage                         | Taken: promptId plus ordinary-completion control         | Yes, structural round already advances |
| Tests that cannot fail: delayed persistence does not reliably require a retry           | nit              | Nit: unreliable boundary coverage                      | Taken: tail stub persists metadata after the first read  | Yes, structural round already advances |
| Parallel paths: untiered failure sounds use a different hash key                        | nit              | Nit: inconsistent sound variant                        | Taken: resolve sound before computing untiered place     | Yes, behavior                          |
| Parallel paths: the shared-plan link breaks in the Codex distribution                   | nit              | Nit: broken documentation link                         | Taken: repository URL                                    | No for this edit alone                 |
| write-bash-scripts: Checked commands: Test jq's predicate exit status directly.         | suggestion       | Nit: local simplification                              | Taken: boolean jq -e pipeline                            | No for this edit alone                 |

All findings taken without severity downgrades. The prompt classifier reuse closes the identified input-form class, including metadata, local-command output, and older human records. The next structural round is Important and includes report-only simplify. Full focused review, trims, semgrep, lint-and-fix, test-all, version checks, tidy, push and ready PR remain pending.

## Additional plant checks

| Planted defect                     | Instrument            | Observed result                             | Regression coverage                               |
| ---------------------------------- | --------------------- | ------------------------------------------- | ------------------------------------------------- |
| Forward raw invalid_request text   | Scrut failure banners | Exit 50; private text appeared              | Fixed API-error body                              |
| Treat metadata as a new prompt     | Scrut failure banners | Exit 50; metadata/local-output became Error | Metadata and local-output refusal titles          |
| Apply origin filtering to failures | Scrut failure banners | Exit 50; background failure banners missing | Background completion control and failure banners |
| Remove refusal-read retries        | Scrut failure banners | Exit 50; delayed refusal became Error       | Synchronized delayed persistence                  |

Structural Important round starts against the restored fixed tree, with the original Nit round retained. Both anti-patterns and report-only simplify use fresh read-only gpt-6.1-sol/high/872000 contexts.

## Recurrence stop

At 9:33 PM ET on 2026-10-28, the structural Important round completed. Both reviewers exited 0 with validated, complete output. The before/after scope comparison showed identical trees and no writes. Report-only simplify found no further proposals or recurrence. Anti-patterns reported this finding in the unchanged attention-log plugin:

| Reviewer's title                                                             | Reviewer's label | Our severity                                                                                                                                     | Take or record                                                                   | Review again                                      |
| ---------------------------------------------------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------- | ------------------------------------------------- |
| Parallel paths: attention-log retains the fixed prompt-classification defect | important        | Important: the banner and watcher's attention record can disagree on whether the same stop is a refusal; the sibling defect predates this branch | Record pending TOOLING's structural scope decision; not fixed and not downgraded | Only after the decision; preserve the round count |

Evidence: `plugins/attention-log/scripts/attention-log` `REFUSAL_JQ` clears refusal metadata on every user string record, including `isMeta: true` and local-command output, and does not clear it on an older `human` prompt. Notify now uses `TURN_JQ.kind`, preserving metadata/local output and recognizing older prompt records. The new fixture input forms therefore expose an existing classification difference between the two plugins. No attention-log files changed on this branch. Reviewer artifacts are `important-anti.json`, `important-anti.log`, `important-simplify.json`, and `important-simplify.log` under `/tmp/notify-642-checks.cLIarv/`.

End state: **stopped: recurring defect**. TOOLING must decide whether to extend the shared classification fix to attention-log in this PR or keep that pre-existing sibling work separate. The worker has not widened scope. No reviewer Important label was downgraded.

Round counts: structural Nit 1, structural Important 1; report-only simplify included in both. The malformed first simplify launch is recorded as incomplete and never called clean. Focused Codex review 0; trims 0. Seven planted defects were detected on the intended assertions with exit 50. The fully restored tree passed all 4 failure-fixture testcases. `make build`, shfmt, ShellCheck, and macOS Bash syntax checks passed. Baseline semgrep, lint-and-fix, make test-all, check-versions, tidy, push, ready PR, and CI remain unrun. No live banners, installed hooks, user configuration, or software installations changed.

Resume from this stop only after TOOLING's scope/design answer and restart go-ahead. Then continue the structural loop from its existing count, followed by the full remaining local review order and ready PR. Codex's watcher remains the separately placed follow-on; obtain its project, handle, branch and base and run `check-worktree-place` before starting that branch. TOOLING merges, never the worker.

## Shared-classifier restart

TOOLING relayed the 9:39 PM ET Inbox answer, “One shared check, in this PR,” authorizing the classifier fix across notify and attention-log and overnight continuation through the ready PR. This supersedes the nighttime parking deadline and resolves the recurrence scope stop. No live configuration, hooks, or installed software changes are authorized.

The same decision accepts a semgrep baseline with partial parsing limited to shell files, provided coverage and unparsed files are recorded and ShellCheck passes on those files. Partial parsing in other languages still stops.

Notify owns scripts/claude-transcript.jq; build-shared-references copies it byte-for-byte into attention-log. Both entry points load its prompt classification and shows_refusal predicate. Contract fixtures exercise metadata, local output, older human prompts, tool results, ordinary replies, and fixture-local helper replacement to prove consumption. attention-log advances 1.0.0 to 1.0.1 for the classification fix; notify remains 4.3.0 on this branch. Next structural round: Important 2, with report-only simplify; counts remain Nit 1/Important 1 completed.

Fetched origin/main at restart. GitHub item 656 is an open resource-claims issue, not a PR; no matching open PR was found. Recheck related merges and overlap before publication; rebase only if the authorized condition holds.

| Planted defect                             | Instrument                           | Observed result                                       | Regression coverage                      |
| ------------------------------------------ | ------------------------------------ | ----------------------------------------------------- | ---------------------------------------- |
| Diverge only attention-log classifier copy | Shared-copy check and contract Scrut | Generator exit 1; Scrut exit 50 on copy identity only | Copy identity and both-consumer contract |

The first divergent-copy plant also exposed a trailing-comment loader boundary: command substitution strips trailing newlines, so an appended jq expression could be swallowed by a final comment. Both loaders now append a newline explicitly, and the fixture helper includes a trailing comment. Repeating the divergent-copy plant then failed only the intended identity testcase (2 passed, 1 failed), while the generator returned 1 for the divergent attention-log copy. The original copy was restored exactly.

Shared-copy generator tests passed 10/10; contract tests passed 3/3; restored notify failure tests passed 4/4. The existing attention-log suite initially found a minimal-PATH regression from invoking dirname before its jq dependency check. Script-directory resolution now uses Bash parameter expansion; its existing no-jq testcase guards that behavior. The attention-log suite rerun passed 54/54. Structural Important 2 starts after these checks, with the existing Nit 1 and Important 1 counts preserved.

## Structural loop completion

Structural Important 2 completed with zero findings in both anti-patterns and report-only simplify. Both fresh read-only gpt-6.1-sol/high/872000 runs exited 0 with validated complete replies. The before/after scope comparison showed identical trees and no writes. Artifacts: `shared-important-anti.json`, `shared-important-simplify.json`, their logs, and `shared-important-{scope,after}.json` in `/tmp/notify-642-checks.cLIarv/`.

End state: **clean at Important**. Preserved totals: structural Nit 1, Important 2, simplify included in every round; no Critical round needed. The authorized shared classifier closed the earlier recurrence. Eight targeted defect plants have been detected, including the divergent-copy plant. The earlier incomplete simplify launch remains recorded as incomplete.

The focused Codex loop now starts its Nit round. Selected aspects: code, errors, tests, comments. Types is omitted because this change adds no typed data model or type definitions. Settings: gpt-6.1-sol, high effort, 872000 context, read-only. This is a separate loop with count 0 before this run. Trims, baseline semgrep, lint-and-fix, make test-all, check-versions, exact-tree tidy, push and ready PR remain pending.

## Focused review completion

The focused Codex Nit round completed with zero findings in code, errors, tests, and comments. Each installed-helper run exited 0 with validated schema output. The before/after scope comparison showed identical trees and no writes. Artifacts: `focused-nit/`, `focused-nit-statuses.json`, and `focused-{scope,after}.json` in `/tmp/notify-642-checks.cLIarv/`. Settings: gpt-6.1-sol/high/872000, read-only. Types was omitted because no type definitions changed.

End state: **clean at Nit**. Focused loop count: Nit 1, no further round needed. Structural totals remain Nit 1/Important 2, clean at Important. Required trims now run once each, gpt-6.1-sol/low/872000, read-only proposals only. No behavior changes are planned. Baseline semgrep, lint-and-fix, make test-all, check-versions, tidy, push and PR remain pending.

## Trims

One read-only Codex run per trim skill completed with exit 0 and complete file lists and proposal tables. Settings: gpt-6.1-sol/low/872000. Both remained read-only. Accepted all five comment proposals and all three prose proposals after checking their before/after text against the files. The stale heredoc comment was removed; the other edits shorten comments or clarify prose. No code fences, snapshot expectations, requirements, authority, evidence, or review counts changed. No behavior changed, so no further review round is required for these edits.

Reviewer label: proposal; our severity: Nit; take or record: all eight taken; review again: no, comments/prose only. Artifacts: `trim-comments.{txt,log}` and `trim-text.{txt,log}` in `/tmp/notify-642-checks.cLIarv/`.

Current local review state: structural clean at Important (Nit 1/Important 2), focused clean at Nit (Nit 1), trims complete (one round each). Semgrep baseline and final repository validation are next; no push or PR yet.

## Baseline semgrep

Recovered the completed scan after a model-capacity interruption; no scan rerun was needed. Semgrep 1.180.0 exited 0 in the disposable shared clone `/tmp/notify-642-checks.cLIarv/semgrep-clone`, with `SEMGREP_REPO_NAME=cboone/agent-harness-plugins` and `semgrep scan --config auto --baseline-commit a2e56c535ed6326cc8d531d945fbb6c627a9b335 --json --output /tmp/notify-642-checks.cLIarv/semgrep.json`. Metrics were not disabled. The scan was limited to baseline changes: 54 rules, 15 targets, zero findings, 75.8% parsed lines; 16 files matched ignore patterns. With no current findings, semgrep skipped its comparison-side baseline scan as its normal baseline-command behavior.

PartialParsing warnings affected shell only:

| File                                          | Unparsed span                                               |
| --------------------------------------------- | ----------------------------------------------------------- |
| `bin/build-shared-references`                 | Lines 56, 57, 76, 77: parameter expansions                  |
| `plugins/attention-log/scripts/attention-log` | Lines 10 to 730: parser warning spanning most of the script |
| `plugins/notify/scripts/notify`               | Line 32: arithmetic conditional                             |

No non-shell parse warning was reported. ShellCheck passed on all three files after the interruption. This result counts under the explicit 9:39 PM ET shell-only partial-parsing rule, with the limits above; it is not a claim of complete Semgrep coverage. Raw JSON, log and exit status are `semgrep.json`, `semgrep.log`, and `semgrep.exit` in the scratch folder.

Next: apply lint-and-fix with no push. Scrut files remain check-only because project policy forbids reformatting them; no bulk Markdown fixer will run over those snapshots. Use the configured formatter on changed non-Scrut source paths, then run the full project lint and test-all commands.

## Final lint and main integration

The first final lint pass found MD038 in the plan's `Worker:` prefix span; removed the trailing code-span space. This is a prose-only fix. The rerun of `make lint` passed all Markdown/Prettier, ShellCheck, shfmt and actionlint checks. The formatter ran on changed non-Scrut source files only; Scrut snapshots remained check-only. No behavior changed.

Refreshing main found `e8667c85610d10882e7c33078748c7113b1c4a8e`, with overlap in `bin/build-shared-references`, its Scrut fixture and the development guide. Resource-claims issue 656's PR 665 merged at 2:43 PM ET on 2026-10-28 (`78386666cdce00aa7efd09eff6cc9252335f034d`), already an ancestor of the original base. The authorized conditional rebase therefore proceeds before publication, preserving main's shared review-policy copy and this branch's classifier copy. Revalidate combined fixture counts, versions and generated copies, then run final checks against the new actual merge base. Review counts stay preserved.

## Rebased validation

Rebased onto main `e8667c85610d10882e7c33078748c7113b1c4a8e`, now the actual merge base. The only conflict was shared-copy Scrut setup/output: preserved main's review-policy fixture plus this branch's classifier fixture, with five copies in total. Notify, attention-log, their shared helper, and behavioral fixtures compare byte-for-byte equal to `feat/642-notify-failure-stops-pre-rebase`. The shared-copy generator preserves both entries, and `make build` wrote no stale copies. All 15 replayed commits have valid GPG signatures. No feature behavior changed, so prior review rounds remain valid and are not restarted.

Repeated the baseline scan only because the base changed. `semgrep scan --config auto --baseline-commit e8667c85610d10882e7c33078748c7113b1c4a8e` ran in `/tmp/notify-642-checks.cLIarv/semgrep-rebased-clone` with the same repository slug and JSON output settings, metrics enabled. Exit 0, zero findings, 54 rules, 15 targets, 76.0% parsed lines, 16 ignored files. Shell-only PartialParsing spans: generator lines 57, 58, 77, 78; attention-log lines 10 to 730; notify line 32. No non-shell parse warning. Raw artifacts: `semgrep-rebased.{json,log,exit}` in the scratch folder. ShellCheck must pass these files in the final project lint, as it did before rebase.

Repository check-versions skill: default branch verified as main; all 60 plugin directories are registered, manifest versions are valid and owned only by manifests, and Codex manifests agree. Changed plugins: notify 4.2.1 to 4.3.0 for the banner capability, attention-log 1.0.0 to 1.0.1 for the classifier fix. No version or catalog issue. Report saved as `versions.json` in the scratch folder.

Final lint-and-fix remains no-push: apply allowed formatters to changed source paths, keep Scrut snapshots check-only, and use make test-all for final complete lint/validation/test verification. Source fixes, if any, will be committed before exact-tree tidy.

## Final repository checks

make test-all completed with exit 0: full Markdown/Prettier, ShellCheck, shfmt, actionlint, JSON/plugin/catalog/mirror/fixture validation, and all 47 Scrut documents passed. 1721 testcases succeeded, zero failed, zero skipped. This includes the combined five-copy generator fixture and both-consumer classifier contract after rebase. Artifacts: test-all.log, test-all.exit and test-summary.json in the scratch folder.

Lint-and-fix --no-push result: success; unresolved or skipped required lint work: none. Markdownlint remained check-only on Scrut files under the project prohibition on reformatting snapshots. Prettier and shfmt ran on allowed changed source paths; the only remaining lint defect found was the plan code-span spacing, fixed and rechecked. All three partially parsed shell files passed full ShellCheck. No code behavior changed after the completed reviews.

Pre-publication state: structural clean at Important (Nit 1/Important 2), focused clean at Nit (Nit 1), trims once each complete, eight targeted plants detected, baseline semgrep accepted with documented shell coverage limits, versions clear. The shared plan covers both harnesses; this PR implements Claude and shared classification, with the Codex watcher pending its separately placed follow-on. The paired issue stays open. No live configuration, installed hooks, new software or live banners changed.

Next operations are exact-tree tidy, push to cboone/agent-harness-plugins, ready PR, green CI and TOOLING handoff. Tidy verification, PR identity and final CI status will be recorded in the worker mailbox/checkpoint after those operations, avoiding another content-changing commit solely to record a PR URL. TOOLING merges; the worker never merges.

## Resource-fix integration after publication

Ready PR 679 was created at https://github.com/cboone/agent-harness-plugins/pull/679 with head e8c9800284c2a95a485a596273165e4b62d21be9. Stored title/body, base main and non-draft state were verified. The paired issue remains open. The earlier exact-tree tidy produced three signed commits and tree eed7463cfed505b0c60e536fc7e55649fa8515d7, identical to its pre-tidy backup.

Resource-claims cause PR 677 then landed on main at 26acdbfec2d70593d563f5fcc78d52f9680d4cd0, overlapping the shared-copy fixture and attention-log. GitHub reported the published PR conflicting, with no checks registered. This is the resource fix anticipated by the standing rebase instruction. Per that authorization, the local branch was rebased again, retaining a pre-resource-rebase backup and preserving all three signed commits. The fixture now retains seven shared-copy entries. The published remote head has not been rewritten.

Main also advanced attention-log to 1.0.1, so this branch now advances it to 1.0.2. Its classifier loader reuses main's existing symlink-aware helper-directory resolver. The contract fixture runs attention-log through a symlink and passed 3/3. This integration preserves main's lock helper without editing its generated copies. A new negative control checks the loader's symlink boundary before final integrated validation.

| Planted defect                                                                          | Instrument               | Observed result | Regression coverage           |
| --------------------------------------------------------------------------------------- | ------------------------ | --------------- | ----------------------------- |
| Resolve classifier from the symlink entry's parent instead of the real plugin directory | Shared-consumer contract | Pending         | Symlinked attention-log entry |

After the integrated result is checked, updating the published PR following rebase needs force-with-lease permission under the no-force rule. Route that final publication action to TOOLING with the exact expected remote head; do not execute a force flag without explicit approval. No PR merge is authorized for the worker.
