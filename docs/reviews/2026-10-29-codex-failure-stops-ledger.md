# Codex failure-stop watcher ledger

## Authority and state

Worker `642-codex-failure-stops`, conductor TOOLING, branch `feat/642-codex-failure-stops`. The brief relays the morning go-ahead through a ready PR; TOOLING merges. The shared plan and Claude implementation from [the merged banner PR](https://github.com/cboone/agent-harness-plugins/pull/679), its ledger, and [the paired issue and comments](https://github.com/cboone/agent-harness-plugins/issues/642) were read. The shared contract remains unchanged.

Repository ownership checks confirm active, non-fork `cboone/agent-harness-plugins`, with no upstream remote. Initial HEAD and fetched `origin/main` merge base: `89ceace915dc3e06053a607d5a35e7b144544dbf`. Local `main` predates the plan, so the required main-branch plan was read from fetched `origin/main`. `corepack yarn install --immutable` passed.

## Runtime evidence and design stop

Installed Codex reports `codex-cli 0.165.0`. Commands executed against that binary:

- `codex app-server --help`: stdio, Unix socket and WebSocket transports; stdio is the default.
- `codex app-server proxy --help`: explicitly proxies stdio bytes to a **running** app-server control socket.
- `codex app-server daemon --help`: daemon lifecycle commands include start, stop and durable bootstrap. None was executed.
- `codex app-server generate-json-schema --experimental --out <scratch>/schema`: completed successfully without starting a server. `ErrorNotification` requires `threadId`, `turnId`, `error` and `willRetry`. `TurnCompletedNotification` requires `threadId` and `turn`. Typed error metadata includes `cyberPolicy` and `misalignmentPolicyViolation`.

Evidence directory: `/tmp/notify-642-codex-evidence.jKhYYT`, created by this worker. It contains the generated protocol schema and captured server/proxy help. Schema generation confirms wire shapes only; policy-to-refusal semantics and multi-client notification routing remain unverified. No policy refusal was provoked. The [official platform overview](https://developers.openai.com/blog/codex-as-a-platform) corroborates the app-server lifecycle integration surface; installed runtime evidence governs this design.

Proposed lifecycle: extend notify with an explicitly launched client of an existing Codex app-server socket, reusing `codex app-server proxy` rather than adding a daemon manager or dependency. The watcher would never start or restart the daemon. It would exit on EOF or disconnection, preserve thread/turn deduplication, and require explicit later activation. A stdio-only adapter still needs a producer connected to the relevant Codex runtime; schema fixtures alone would not establish delivery.

**Stopped before implementation:** this proposed watcher needs a running daemon, which the brief explicitly makes a design stop. TOOLING must resolve whether to authorize this dependency before live routing tests or implementation. Connection ownership, observing already-running threads without resuming them, metadata for session/tmux identity, and typed policy mappings must then be confirmed from Codex before building. No daemon was started or connected, no installed config or hooks changed, no software installed, and no banner delivered. No implementation reviews, plants, Semgrep, full suite, version bump, push or PR have run.

## Private runtime probe after conductor authorization

TOOLING authorized the existing-socket client design in this conversation, with a disposable private server for live checks and an explicit stop if passive observation requires server or thread mutation. Shipped code must never manage a daemon, add dependencies or activate installed config. The eventual PR must leave live activation to Chris (he/him).

The probe used a separate `CODEX_HOME` under the evidence directory, a private Unix socket there, and a loopback HTTP provider returning a controlled HTTP 400. It used no credentials, model service or shared fleet socket. The producer created one disposable thread and started one test turn. The observer sent only `initialize`, `initialized`, `thread/loaded/list` and `thread/read`.

The first JSON-lines probe timed out at initialization; server PID `61324` was stopped by that recorded PID. Exact-tag source then established the transport mismatch: `codex app-server proxy` copies raw bytes; the Unix control socket expects a WebSocket handshake and frames. A corrected stdlib-only test client completed that handshake through the proxy. This test code is retained as `probe.py` in the evidence directory, not shipped plugin code. The second server PID `33730` was stopped by that recorded PID, exited 0, and was confirmed absent afterward. `server.stopped` records cleanup. No server remains running from either probe.

Live result: the producer received `error` with `willRetry: false`, followed by `turn/completed` with `status: failed`, sharing thread and turn IDs. The read-only observer saw `thread/started` and `thread/status/changed`, but neither terminal event, despite successfully listing and reading the thread before the test turn. `thread/read` returned thread/session IDs, cwd, rollout path and nullable name; it exposed no tmux location. No tmux association or policy semantics is considered confirmed.

**Stopped at the passive-subscription boundary.** Generated protocol methods expose `thread/unsubscribe` but no `thread/subscribe`. Exact-tag `thread_processor.rs` confirms `thread/read` only returns metadata; `thread_lifecycle.rs` routes thread events to subscribed connection IDs. Passive reads did not establish a terminal-event subscription. No observer resume, start, settings update or other thread mutation was attempted. Further attachment work requires a design decision from TOOLING under the explicit stop. Policy probes, implementation, fixtures/plants, reviews and publication remain pending.

Artifacts: `probe-result-ws.txt`, `notify_fixture_producer.jsonl`, `notify_fixture_observer.jsonl`, `started.json`, `server.pid`, `server.stopped`, and exact-tag source files in the evidence directory. Source provenance: `rust-v0.165.0`, fetched from `openai/codex` through read-only GitHub API calls. The initial JSON-lines timeout remains an unsuccessful probe, not a passing check.

## Rollout and callback source comparison

TOOLING ruled out passive socket observation and authorized only live source checks followed by one attachment recommendation. No implementation is authorized until TOOLING answers. No thread owned by another session was resumed or subscribed to.

The installed binary remains `codex-cli 0.165.0`. New probes reused the same isolated `CODEX_HOME` and private socket. Local HTTP fixtures exercised an ordinary HTTP 400, three synthetic policy-coded HTTP 400 responses, an SSE stream failure followed by HTTP 400, a stream failure followed by recovery, and an ordinary success control. No real provider or safeguard refusal was requested. Capture-only config hooks and `notify` wrote scratch files, never banners. `hooks/list` provided each test hook's current hash; those reviewed capture-only definitions were trusted in the isolated config's state map. A second inventory confirmed all six hooks trusted. No bypass flag or installed configuration was used.

### Rollout JSONL

Live rollout snapshots show `event_msg.payload.type: task_complete` with matching `turn_id` and `error` on a terminal failure. There is no literal `status: failed` or `willRetry` in this record: the non-null typed terminal error is the equivalent failure signal. Success omits `error`. `session_meta.payload.id` and `session_id` identify the thread; `turn_context` and terminal records identify the turn.

| Controlled provider input           | Persisted terminal `error.codex_error_info` | App-server `codexErrorInfo`   |
| ----------------------------------- | ------------------------------------------- | ----------------------------- |
| Ordinary HTTP 400                   | `other`                                     | `other`                       |
| `cyber_policy` HTTP 400             | `cyber_policy`                              | `cyberPolicy`                 |
| `bio_policy` HTTP 400               | `bio_policy`                                | `other`                       |
| `misalignment_policy_violation` 400 | `misalignment_policy_violation`             | `misalignmentPolicyViolation` |

These mappings were measured from the runtime, not inferred from message wording. All three policy fixtures used the same generic message. The rollout preserves biological-policy classification that the public app-server schema loses.

For both retry fixtures the producer stream emitted `error` with `willRetry: true`. A disk snapshot taken when the second HTTP request arrived contained no `task_complete`, error event or stream-error event. The final-failure case subsequently persisted one `task_complete` with `error`; the recovered case persisted one without `error`. Thus a tail cannot reconstruct intermediate retries or label each request failure, but it can safely distinguish terminal failure by waiting for the matching completion record. Exact-tag `rollout/src/policy.rs` corroborates that individual `Error` and `StreamError` events are transient and omitted from persistence. Reading an arbitrary tail without retained thread identity and turn matching is insufficient.

### Config hooks and notify

`SessionStart` and `UserPromptSubmit` supplied session identity and the actual rollout path. `PostModelRequest` fired on failed requests with `session_id`, `turn_id`, `transcript_path`, `status: failed` and a string `error`. It supplied neither typed policy metadata nor a retry/terminal discriminator. In the retry case it fired twice for the same turn; in the recovered case the failed callback preceded successful completion. It cannot itself determine a failure banner.

`Stop` and the legacy notify program produced no capture for any failed or policy-coded turn. Both fired for the ordinary successful control and recovered retry, proving the handlers were functional. Notify's successful payload included `thread-id` and `turn-id`. `SessionEnd` fired on server shutdown for successful and failed threads alike, without terminal-error metadata. No tested hook or notify callback supplies a complete failed/refused-turn signal.

### Recommended attachment and stop

Use an explicitly launched **rollout-file watcher**, with an explicit thread ID, rollout path and session/tmux presentation context supplied by the owning launcher. It reads only that rollout, retains `session_meta` identity, follows new records, and handles matching `task_complete.error` once per thread/turn. The three measured typed policy values map to refusal with the existing fixed refusal body; other typed errors map to error. Completed turns without an error stay silent. This avoids socket subscriptions, daemon management, new dependencies and callbacks that confuse retried requests with terminal failure. The shared presentation/classifier contract remains unchanged.

The launcher must own watcher shutdown and supply the real session location; inheriting a shared daemon's environment would not establish that location. The measured `SessionStart` payload can provide path/identity at future activation, but any hook activation or installed configuration change remains a later explicit decision. No launcher or watcher is built here. Legacy/ephemeral history, shutdown behavior, stale-record replay and approval waits remain implementation validation boundaries, not claimed passes from these probes.

Stopped pending TOOLING's attachment decision. Final probe server PID `51376` was recorded, stopped by PID, exited 0 and confirmed absent; preceding comparison server PID `21267` likewise exited 0. Artifacts under `sources-probe/` include `results.txt`, per-case event and rollout snapshots, pre-second-request snapshots, trusted `hooks-list.json`, `hooks.jsonl`, `notify.jsonl`, `probe.py`, and PID/cleanup records. `sources-probe-first-run/` preserves the earlier comparison. These are diagnostic fixtures only; no plugin code, real config, installed hooks, dependencies or live banners changed.

## Approved implementation and boundary checks

TOOLING approved the explicitly launched rollout watcher in this conversation, including the three measured policy mappings, launcher-supplied presentation context, per-thread/turn delivery and fixture coverage. The go-ahead covers building through a ready PR; activation remains separate for Chris and SL-VF. No launcher, installed config or hook registration is changed. New Codex runs are limited to the required local reviews.

Notify advances from 4.3.0 to 4.4.0 for the watcher capability. `watch-codex-failures` follows an already existing file while its explicit supervising PID remains running. It reads session metadata during catch-up, skips historical completions, buffers partial lines and drains complete records before exit. `--once` explicitly processes historical records. A persistent atomic delivery claim prevents duplicates across concurrent readers and restarts. The notifier receives explicit presentation context and retains existing titles, tiers, sound selection and fixed refusal descriptions. The shared Claude classifier is unchanged.

Targeted Scrut verification passed: 11 cases, zero failures/skips, with `/bin/bash` (macOS Bash 3.2) for the watcher. Cases cover terminal errors, all three policy types, retries/recovery, approval waits, subagents, untyped errors, thread/turn separation, concurrent readers, restarts, identity/message fallbacks, tier titles, non-tmux presentation, stale history, partial appends, owner shutdown and identity mismatch. Committed stubs refuse live alerter/tmux resolution. `make build` and targeted ShellCheck passed. Review comparison base is fixed at `89ceace915dc3e06053a607d5a35e7b144544dbf`.

Plants ran in exact scratch copies of the plugin, never in installed code. The first campaign exposed an ambiguous subagent test: it shared the positive control's identity, so deduplication masked removal of the exclusion. Giving the sample its own turn closed that test gap. Removing just the watcher's refusal body normalization remained safe because the notifier independently supplies the fixed body; this is a passing negative control, not a detected defect. The verified campaign removed both protections to test disclosure end to end. Artifacts: `plants-verified/results.json` and per-plant stdout/stderr under the evidence directory.

| Planted defect                                   | Instrument              | Observed result                      | Regression coverage                                      |
| ------------------------------------------------ | ----------------------- | ------------------------------------ | -------------------------------------------------------- |
| Stop recognizing `bio_policy`                    | Refusal fixture         | Wrong error title/body               | Typed policy refusals                                    |
| Remove watcher-only refusal body normalization   | Refusal fixture         | Stayed green, notifier still redacts | Negative control for independent presentation protection |
| Remove both refusal body protections             | Refusal fixture         | Private sample text appeared         | Typed policy refusals                                    |
| Omit thread ID from delivery key                 | Distinct-thread fixture | Missing second alert, exit 1         | Same turn ID in distinct threads                         |
| Treat untyped errors as typed                    | Quiet fixture           | Extra wrong failure                  | Untyped-error exclusion                                  |
| Give recovered completions an error              | Quiet fixture           | Extra wrong failure                  | Recovered-turn exclusion                                 |
| Treat a turn start as terminal failure           | Quiet fixture           | Extra banner, exit 1                 | Approval-wait exclusion                                  |
| Disable the atomic delivery claim                | Duplicate fixture       | Extra alerts, exit 1                 | Duplicate/restart handling                               |
| Omit turn ID from delivery key                   | Duplicate fixture       | Missing second alert, exit 1         | Distinct-turn handling                                   |
| Remove subagent exclusion                        | Quiet fixture           | Extra alert                          | Subagent exclusion                                       |
| Remove name fallback                             | Identity fixture        | Wrong banner name                    | Thread identity fallback                                 |
| Change missing-message fallback                  | Identity fixture        | Wrong body                           | Fixed error fallback                                     |
| Process historical completions on follow startup | Follow fixture          | Extra alert, exit 1                  | Catch-up exclusion                                       |
| Discard partial-line prefix                      | Follow fixture          | JSON parse failure, exit 1           | Partial appends                                          |
| Ignore supervisor exit                           | Follow fixture          | Watcher stayed running, exit 1       | Supervisor shutdown                                      |
| Remove expected-thread validation                | Mismatch fixture        | Incorrect success, exit 0            | Thread mismatch rejection                                |

The verified campaign detected all 15 defects and preserved the one expected-green negative control. Full local reviews, baseline Semgrep, lint-and-fix, test-all, version checks, tidy and publication remain pending.

## Structural Nit round

Fresh read-only anti-patterns and report-only simplify ran in parallel with `gpt-6.1-sol`, high effort, 872000 context, stdin closed, approval policy never and web search disabled. Both exited 0 with non-empty schema-valid replies. The scope comparison found no lasting changes. Artifacts: `reviews/structural-nit/` under the evidence directory. GitHub reads were unavailable inside the sandbox; ownership and archive status were already verified by this worker. Tests were intentionally not run by reviewers; worker results are recorded separately.

| Reviewer's title                                                                                 | Reviewer's label | Our severity                                                                 | Take or record                                                      | Review again      |
| ------------------------------------------------------------------------------------------------ | ---------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------- | ----------------- |
| Boundary arithmetic: catch-up discards failures appended after launch                            | `important`      | Important: loses a newly appended terminal failure                           | Taken: fixed initial byte boundary, byte-counted under C locale     | Yes, behavior     |
| Parallel paths: directory tier rules still consume inherited Claude context                      | `important`      | Important: selects the wrong tier and sound from another session's directory | Taken: clear inherited Claude directory context for Codex failures  | Yes, behavior     |
| Docs drift: the Codex event section still describes the previous release                         | `nit`            | Nit: obsolete adapter description beside accurate installation guidance      | Taken: describe the shipped rollout watcher and separate activation | No, docs          |
| write-bash-scripts: Safe temporary files: Extract the inline cleanup trap into a named function. | `suggestion`     | Nit: local readability improvement                                           | Taken: named cleanup function with the same recorded targets        | No, refactor only |

Targeted Scrut passed after these fixes: 13 cases, zero failures/skips. New deterministic cases append after the captured size but before history is read, include multibyte content, and supply a conflicting inherited Claude directory. Planting the original EOF-based catch-up behavior lost the startup append and failed the fixture with exit 1. Restoring inherited Claude directory selection produced the wrong Worker title and failed the exact output expectation. Both plants were detected; `structural-plants/results.json` records the results. Total detected defects: 17, plus one expected-green negative control. Targeted ShellCheck passed, including the committed byte-count synchronization stub. The structural loop advances to Important round 1; no prior defect class has recurred in a review.

## Structural Important round 1: recurring-defect stop

Both fresh read-only runs completed with exit 0, non-empty schema-valid replies and unchanged review scope. Settings remain `gpt-6.1-sol`, high effort, 872000 context, approval never, web search disabled and closed stdin. Simplify proposed nothing further. Anti-patterns reported two Important findings against source commit `2c1ce2bab50ef049e861a4b9151a72b7a71b5436`, with the same fixed comparison base. Artifacts: `reviews/structural-important/`. Reviewer network limitations and intentionally unrun tests remain distinct from the completed static review.

| Reviewer's title                                                        | Reviewer's label | Our severity                                                                                           | Take or record                                        | Review again                |
| ----------------------------------------------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------- | --------------------------- |
| Boundary arithmetic: supervisor shutdown can discard the final failure  | `important`      | Important: a final terminal record can be lost between EOF observation and supervisor-exit observation | Take, stopped pending conductor's structural decision | Yes, behavior if authorized |
| Parallel paths: byte-counting locale changes presentation tier matching | `important`      | Important: exporting the C locale changes existing Unicode-aware tier rules and sound selection        | Take, stopped pending conductor's structural decision | Yes, behavior if authorized |

The shutdown finding recurs in the terminal-record-loss class that the Nit round fixed at startup. The current follow loop checks EOF first, then checks supervisor liveness and exits without another read. A producer can append its final complete record between those observations. The existing shutdown fixture stops the supervisor only after delivery, so it does not cover that ordering. This is a concrete code path identified by static review; no runtime reproduction or new plant was run after the stop.

The locale finding follows from the fix's global `export LC_ALL=C` reaching the notifier. Bash tier-rule matching is locale-sensitive, so a Unicode uppercase name can select a different tier. Byte accounting must not change the launcher's presentation locale. No severity was downgraded and neither finding is fixed yet.

Recommended structural direction for TOOLING's decision: make startup, following, supervisor-exit observation and final draining explicit states over the same file descriptor; only stop after observing supervisor exit and then completing a final read to EOF. Keep C-locale byte length inside an accounting helper so it cannot reach presentation. Add deterministic producer/supervisor interleaving and Unicode-tier cases, and plant both original defects before resuming review. This proposal is not implementation authorization.

**End state: stopped: recurring defect.** Structural counts persist at Nit 1 and Important 1; no Important round 2, focused review, trims, Semgrep, final lint-and-fix/test-all/version check, tidy, push or PR has run. Earlier targeted tests and plants retain their measured passes but do not establish these new boundaries. Production code remains at the reviewed commit; only this stop record is added. TOOLING receives the findings and owns the design decision. No live activation or shared-daemon access occurred.

## TOOLING structural call and continuation

TOOLING explicitly approved the proposed structural fix in this conversation: startup, following, owner-exit and final-drain states on one descriptor, supervisor-exit observation before the final EOF drain, and a local C-locale accounting helper. This opens the stopped implementation and continuation gates without resetting review counts. Important round 1's accepted findings are now fixed; the next review is Important round 2.

The follower retains its descriptor and initial byte boundary. EOF leads to owner-exit observation, which either resumes following or enters final-drain. Only EOF observed in final-drain ends the reader. Byte length runs inside `byte_count` with a function-local locale; neither notification delivery nor tier rules inherit a changed locale.

The committed owner-check fixture pauses the watcher after the initial EOF, appends a complete terminal record, stops and reaps the fixture supervisor, then releases the check. The watcher delivers that record and exits. The Unicode fixture confirms the launcher's uppercase character-class rule selects the Worker tier for `ÉQUIPE`. Both execute with capture-only notification stubs. Targeted Scrut passed 15 cases with zero failures/skips; targeted ShellCheck and `make build` passed.

| Planted defect                                                      | Instrument                    | Observed result             | Regression coverage                                    |
| ------------------------------------------------------------------- | ----------------------------- | --------------------------- | ------------------------------------------------------ |
| Exit immediately after observing owner exit, without final draining | Shutdown-interleaving fixture | Missing final alert, exit 1 | Record appended between EOF and owner-exit observation |
| Export C locale from the watcher                                    | Unicode-tier fixture          | Worker prefix missing       | Unicode character-class tier rule                      |

Both plants were detected in scratch plugin copies. Artifacts: `lifecycle-plants/results.json` and per-plant output under the evidence directory. Total detected defects: 19, plus the expected-safe refusal-normalization negative control. The prior recurrence stop remains recorded above; no review budget was restarted. No launcher, installed configuration, hook activation or live banner changed.

## Structural Important round 2 result

Anti-patterns and report-only simplify both exited 0 with non-empty schema-valid replies, no findings and unchanged content/scope snapshots. Anti-patterns read all 27 canonical changed files, checked the lifecycle states and their sibling paths, and identified no further recurrence. Static Bash syntax, ShellCheck, shfmt and JSON parsing checks passed in the reviewer. Tests, plants and repository validators remained intentionally unrun inside the sandbox; worker runtime results are recorded above. Settings remained `gpt-6.1-sol`, high effort, 872000 context, read-only sandbox, approval never, web search disabled and closed stdin. The configured `CLAUDE.md` fallback guide was supplied explicitly; repository guides are paired with `AGENTS.md`.

Artifacts: `reviews/structural-important-2/` under the evidence directory. Source reviewed: `21c26e0d315fd244d5761ae94cd92701f88ae959`; fixed base unchanged. **Structural loop end: clean at Important.** Counts: Nit 1, Important 2. TOOLING received the loop précis through the mailbox. Proceed to the focused review loop without a new gate; activation remains separate.

## Focused Nit round

Selected code, errors, tests, comments and types. Types covers the normalized JSON discriminants and field invariants; simplify stays in the structural loop. Runs used the installed aspect helper with explicit `gpt-6.1-sol`, high effort, 872000 window, read-only sandbox, approval never, web disabled, closed stdin and `CLAUDE.md` fallback guidance. Base remained pinned. Code, errors, comments and types exited 0 with schema-valid replies. Tests failed with exit 1 and “Selected model is at capacity”; its missing reply was not treated as clean. That failure remains in the original run artifacts.

One explicitly announced replacement ran only the missing tests aspect with identical settings and unchanged scope. It exited 0 with a validated reply. The four completed results were preserved. Both scope comparisons found no changes. This completes one Nit round, not two rounds or a reset. Artifacts: `reviews/focused-nit/`, including separate `tests-replacement/` outputs. The error reviewer used a process-only stub to confirm the failure path; repository tests remained outside reviewer execution.

| Reviewer's title                                                                                           | Reviewer's label | Our severity                                                                             | Take or record                                                                            | Review again                                              |
| ---------------------------------------------------------------------------------------------------------- | ---------------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| write-bash-scripts: Checked commands: Notification startup failures are hidden behind successful dispatch. | `important`      | Important: a permanently claimed turn can lose its banner without any startup diagnostic | Taken: executable preflight before claiming, plus contextual detached-backend diagnostics | Yes, behavior                                             |
| write-scrut-tests: Asserted exit codes: Failed delivery followed by restart is untested.                   | `suggestion`     | Nit: missing regression coverage for an already enforced no-retry policy                 | Taken: failed dispatch and replay fixture                                                 | No for tests alone; the behavioral fix advances the round |

Code, comments and types reported no findings. No severity was downgraded. This backend-startup failure class differs from the resolved lifecycle record-loss class; no recurrence was identified in this round.

The watcher checks the existing alerter executable before creating a new delivery claim. Claimed turns remain claimed after a failed dispatch. Codex failure dispatch supplies thread/turn diagnostic context to the existing detached runner; immediate backend errors retain stderr and report their exit status. Other notification calls retain their existing quiet delivery behavior. Titles, tiers, sounds, shared classification and the no-retry policy remain unchanged.

Targeted Scrut passed 18 rollout cases and all 4 Claude failure cases. ShellCheck and the generated build passed. New committed fixtures cover unavailable executable lookup followed by repair, a detached backend exiting 127 with contextual stderr, and a notifier exiting 23 followed by replay with exactly one attempt. The async-error case waits for the diagnostic itself rather than assuming detached process completion.

| Planted defect                       | Instrument              | Observed result                        | Regression coverage                      |
| ------------------------------------ | ----------------------- | -------------------------------------- | ---------------------------------------- |
| Remove executable preflight          | Preflight fixture       | Unexpected successful dispatch, exit 1 | Missing backend does not consume a claim |
| Suppress detached backend stderr     | Backend-failure fixture | Expected diagnostic absent, exit 1     | Contextual startup failure reporting     |
| Remove a claim after failed dispatch | Dispatch/replay fixture | Two attempts instead of one, exit 1    | Failed delivery followed by restart      |

All three plants were detected in scratch copies. Artifacts: `delivery-plants/results.json` and per-plant outputs. Total detected defects: 22, plus one expected-safe negative control. The focused loop advances to Important round 1, with Nit 1 retained. Full checks, trims and publication remain pending.

## Focused Important round 1 result

All five aspects completed with exit 0 and schema-valid replies against source `7187df74fb43cb2e2b87e2e89ed6ecda5a292648`, with the fixed base unchanged. Code, errors, comments and types reported no findings. Tests reported one suggestion below the active threshold. The runner logged a non-fatal `child setpgid ... Operation not permitted` warning; it still waited for every model process and validated all five replies. No cancellation was requested or claimed. Both content and scope snapshots remained unchanged. Artifacts: `reviews/focused-important/`.

| Reviewer's title                                                                                          | Reviewer's label | Our severity                                                            | Take or record                                                                             | Review again            |
| --------------------------------------------------------------------------------------------------------- | ---------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ----------------------- |
| write-scrut-tests: Structured output: Untyped-error coverage misses error objects without typed metadata. | `suggestion`     | Nit: an existing validation predicate lacked direct regression coverage | Taken: missing, null and empty metadata cases, with a typed object-valued positive control | No, tests and docs only |

The added connection-error object follows the exact-version protocol's `CodexErrorInfoWire::HttpConnectionFailed` and snake-case serialization in `codex-rs/protocol/src/codex_error_info.rs`, fetched from tag `rust-v0.165.0`. It supplements captured rollout shapes rather than claiming a new live observation. Negative cases use distinct turn IDs so deduplication cannot hide an incorrectly accepted record.

Targeted Scrut passed 19 cases, zero failures/skips. Removing the typed-metadata predicate produced extra banners; restricting metadata to strings lost the typed-object positive control. Both plants failed the intended fixture with exit 1. Artifacts: `metadata-plants/results.json`. Total detected defects: 24, plus one expected-safe negative control.

**Focused loop end: clean at Important.** Counts: Nit 1, Important 1. The below-threshold test/doc edits change no production behavior and do not advance the loop. TOOLING receives this completed-loop précis; proceed to one read-only round each of comment and prose trims, then baseline Semgrep and final checks. No activation is included.

## Trims

One fresh read-only round each of trim-comments and trim-text completed with exit 0, non-empty replies in the required file-list/proposal shape, and unchanged snapshots. Settings: `gpt-6.1-sol`, low effort, 872000 context, approval never, web disabled and closed stdin. Artifacts: `reviews/trims/`.

Accepted the comment trim removing the fixture's redundant cleanup-boundary comment, and the prose trim replacing “It is shipped” with “It ships” in the notify README. Kept “fails before a claim is created”; the proposed “fails before claim creation” was less natural and did not improve clarity. Preserved audit quotations, authority decisions, counts, caveats, catalog wording and activation constraints. The README's reference to Chris now follows the shared-record naming convention. No production behavior changed, no technical claim was flagged, and no cut material needs another home.

## Baseline Semgrep

Ran native baseline mode in the disposable `git clone --shared` at `/tmp/notify-642-codex-evidence.jKhYYT/semgrep-clone`, head `2be0e924b884fb44d312ec8bd991b4116cd1ea30`. Command: `SEMGREP_REPO_NAME=cboone/agent-harness-plugins semgrep scan --config auto --baseline-commit 89ceace915dc3e06053a607d5a35e7b144544dbf`, with JSON output capture and no metrics-disabling option. The clone's head was verified against the source branch before scanning; no baseline checkout touched the worktree.

Result: exit 0, zero findings, 54 rules, 9 targets, approximately 99.9% parsed lines as reported by Semgrep. Native baseline mode limited targets to changed files; because there were no current findings, Semgrep skipped its second baseline-comparison pass. Default ignore patterns skipped 28 files, including test/generated surfaces. Fixture behavior is covered separately by Scrut and shell lint, not claimed as Semgrep coverage.

The sole parser warning is Shell `PartialParsing` in `plugins/notify/scripts/notify`, at line 32 (columns 37–46, arithmetic ternary) and line 877 (columns 21–37, case pattern). No other file or language has a partial-parsing error. ShellCheck and `/bin/bash -n` pass on that exact file, satisfying the brief's explicit Shell-only exception. This is a coverage-qualified scan, not a claim of complete parsing. Artifacts: `semgrep.json`, `semgrep.log`, `semgrep.exit` and `semgrep-clone.log` under the evidence directory. Production source remains unchanged after the scan.

## Final-check fixture integration

The first `make test-all` attempt passed lint but stopped in `bin/check-fixture-environments` before the full Scrut suite ran. It correctly required the new fixture and document to source the Git-environment reset, and required the fixture to use `capture_child` for retained diagnostics. That attempt exited 2 and is not a full-suite pass.

Added both Git resets and the shared diagnostic capture helper. Preflight diagnostics now replay through the helper; detached-backend diagnostics remain captured until child stderr closes, and failed dispatch retains its actual exit status. The capture integration changes tests only. Fixture validation and targeted ShellCheck pass. Targeted Scrut now passes 20 cases including the explicit environment-setup block. Repeated the three delivery plants against this harness integration; all still fail the intended assertions. These are repeat confirmations of existing plants, not three additional defects. Artifacts: `scrut-fixture-integration.log` and `delivery-plants-harness/results.json`.

The check-versions skill reports all clear: notify 4.3.0 → 4.4.0, matching Codex/source manifests, all 60 plugins registered, manifest-only version ownership. The new capability warrants the minor bump. Production scripts remain byte-identical to the Semgrep-scanned head. Full `make test-all` is rerun after the fixture integration; publication remains pending its observed result.

## Final local validation and publication boundary

`make test-all` passed after fixture integration: exit 0, all 51 Scrut documents and 1,802 cases succeeded, zero failures and zero skips. Markdown/Prettier, ShellCheck, shfmt, actionlint, JSON, fixture-environment, plugin/catalog, generated mirror and shared-copy validation all passed. The rollout document's 20 cases passed within that full run. Artifacts: `test-all-integrated.log`, `test-all-integrated.exit` and `final-test-summary.json`. The earlier validator-stopped run remains explicitly non-passing.

The `lint-and-fix --no-push` work is complete: scoped safe formatters and all required project lint/validation checks passed. Scrut snapshots were edited deliberately and checked, not bulk-formatted. The in-scope fixture integration fix was committed; no required check or tool was skipped. Final version audit remains clear at notify 4.4.0 with 60 registered plugins. Production scripts compare byte-for-byte with the Semgrep-scanned head.

Review totals: structural Nit 1 / Important 2, clean at Important; focused Nit 1 / Important 1, clean at Important; one completed read-only trim round each for comments and prose. Twenty-four unique defects were planted and detected, with one expected-safe negative control and repeat confirmations after harness integration. TOOLING's structural lifecycle call is implemented; no severity downgrade or unresolved finding remains. Semgrep retains its recorded Shell-only coverage qualification.

Publication proceeds through an exact-tree tidy backed by a local pre-tidy branch, signed logical commits, normal push and a ready PR. Tidy verification, PR identity and final CI state are recorded in the worker mailbox/checkpoint after those operations so this validated tree need not change solely to record a URL. The PR links the merged Claude banner half and closes the paired issue on merge. TOOLING merges; the worker never merges. Activation remains a separate step for Chris (he/him) and SL-VF after merge. No launcher wiring, installed configuration, hooks, software installation or live banners changed.
