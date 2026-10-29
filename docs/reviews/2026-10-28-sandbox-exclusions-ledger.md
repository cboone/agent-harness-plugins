# Sandbox exclusions ledger

## Current status

Active overnight through a ready PR; TOOLING retains merging. Helper diagnostics,
the guarded matrix and initial plants are committed. The structural Nit round
has completed with findings, and its fixes are being verified. The resource
suite now passes 21 cases; the restored 20-case revision measured 60.46 seconds. No push or PR has occurred. Earlier
checkpoint sections below are historical, not current task status.

## Authority and status

Worker `512-sandbox-exclusions`, reporting only to TOOLING by `mailbox-post`.
Go-ahead from Chris (he/him): Inbox, 2026-10-28 at 7:38 PM ET, thread "Tooling next batch,
Oct 28 evening", build through a PR ready for review. TOOLING merges.
Branch `fix/512-sandbox-exclusions`; base `main`. Initial merge base with
`origin/main`: `a2e56c535ed6326cc8d531d945fbb6c627a9b335`.

Both issue bodies and every comment were read using explicit repository
arguments. Each issue had one comment, the 2026-10-28 parity amendment.
Repository metadata: active, not a fork, no parent; only origin is configured,
pointing to `cboone/agent-harness-plugins`. Initial branch was clean.
`corepack yarn install --immutable` passed with Yarn 4.18.0.

## Initial source inventory

The older `address-issue-in-worktree` plugin is now `workmux:start-issue`.
All three helpers belong to `plugins/workmux/scripts/`: `compose-issue-prompt`,
`launch-workmux`, `manage-resource-claims`. `workmux:create-worktree` shares them.
Existing launch tests and committed workmux/tmux/git stubs will be extended.

A repository-wide hidden-file sweep, excluding Git and dependency storage,
found no literal `excludedCommands` in active canonical sources. It found five
active copies of the assertion that keeping a stable `bash` token determines
permission allowlist matching:

- `workmux` start-issue and create-worktree skills.
- `monitor-pr` resolve-copilot-feedback skill.
- `publish-report-board` skill.
- `dependabot` triage-prs skill.

Their generated Codex copies must follow canonical edits through `make build`.
The completed 2026-09-09 locator plan also contains the assertion and remains
historical evidence. The `clean-up-agent-config` reference's tmpdir exclusion
concerns filesystem policy, not command exemption. Other sandbox statements,
including use-git's temporary-directory claims, still need scoped assessment.
This initial string inventory is not the completed semantic sweep.

## Harness evidence

Installed CLI versions read live: Claude Code 2.1.312, Codex CLI 0.165.0,
workmux 0.1.277. No update was requested or accepted.

Probe directory created and retained:
`/var/folders/52/k6wl64d16fb3hf60p98djgxc0000gp/T/sandbox-facts-512.uan1Od`.
Every settings/config file used below is inside that recorded directory.
No real user settings or credential files were read or changed.

### Fresh Claude Code question

Sonnet at low effort, `claude --print`, `/private/tmp`, no tools, no session
persistence, `--setting-sources ''`, an empty temporary `--settings` file,
strict empty MCP configuration. Asked open questions about command matching,
wrappers, pipelines and resource denials without supplying issue claims.
Process exited 0 and produced a nonempty answer.

The answer explicitly said its matching and resource details were recollection,
not confirmed by its current harness. Those details are **not accepted facts**.
Retained files: `claude-facts.txt`, `claude-stderr.txt`, `claude-settings.json`.
TOOLING received the open questions, requesting live-confirmed Claude evidence.

### Fresh Codex question

`gpt-6.1-sol`, low effort, ephemeral read-only `codex exec`, approval `never`,
`--ignore-user-config --ignore-rules`, `/private/tmp`, stdin closed. Asked open
questions without supplying issue claims. Exit 0, nonempty final reply, log
progressed through tool execution rather than waiting on stdin.

Confirmed by its CLI help and supplied session policy: sandbox selection and
approval are separate; this child was read-only with approval `never` and
restricted network; execpolicy rules exist (`--ignore-rules` is documented).
Command matching for paths, wrappers and pipelines remained unconfirmed.
No command exemption was established.

Its live `workmux --help` invocation failed during rolling-log initialization
with PermissionDenied / Operation not permitted. This confirms a log-write
requirement even for help; that child did not establish the log destination.
Its nested `codex sandbox macos --help` attempted execution and failed applying
the nested sandbox. This is not a successful sandbox behavior probe.
Retained files: `codex-facts.txt`, `codex-events.txt`, `codex-stderr.txt`.

### Native sandbox probe preparation

Created isolated `codex-home/config.toml` with `sandbox_mode = "read-only"`,
plus empty workspace, workmux-state and gh-config directories. With CODEX_HOME
and XDG_STATE_HOME pointing to these fixtures, `codex sandbox -C WORKSPACE
workmux --version` exited 2 before execution: `--permission-profile <NAME>` is
required. No custom permission profile was added; this does not prove a tool
denial or matching rule.

### Restrictive Claude Code live probes

Two more fresh Sonnet sessions used low effort, Bash only, `dontAsk`, empty
setting sources, strict empty MCP configuration and no session persistence.
Sandboxing was enabled and unsandboxed execution disabled in temporary settings.
Both completed with exit 0 and nonempty answers. No retry was requested.

The first ran `printf "sandbox-probe\\n"` successfully and bare
`workmux --version` with exit 101 and the rolling-log initialization panic.
Its answer also identified the sandbox's supplied filesystem/network limits.
Raw answer: `claude-live.txt`; stderr: `claude-live-stderr.txt`.

The second retained actual tool requests and results in
`claude-resources.jsonl`, using `--verbose --output-format stream-json`:

| Probe                                                                          | Observed result                                   | Limit                                      |
| ------------------------------------------------------------------------------ | ------------------------------------------------- | ------------------------------------------ |
| workmux version with XDG_STATE_HOME set to a fixture workspace state directory | Tool permission denied before execution           | No exit status or log-destination evidence |
| tmux list-sessions against `/private/tmp/tmux-502/work`                        | Exit 1, socket connection Operation not permitted | Socket access denied; no session IDs read  |
| gh config get editor with GH_CONFIG_DIR set to a synthetic fixture             | Tool permission denied before execution           | No gh config-read behavior established     |

The synthetic `gh-config/hosts.yml` contains only `github.com: {}`; the second
session's temporary settings read-denied that fixture path. No real credential
file was used. No tool permission was added and neither denied command was
retried. Direct host inspection confirmed the work tmux socket's path before
the read-only probe. The host's default socket did not exist; that distinct
failure was not interpreted as a sandbox denial.

These results distinguish a tool permission rejection from a running program's
resource denial. They do not establish exclusion-pattern behavior.

### Codex native execpolicy checker

`codex execpolicy check --help` was read from installed 0.165.0. It describes
command tokens and an optional `--resolve-host-executables` mode, gated by
`host_executable()` definitions. The following live checks used isolated
CODEX_HOME and only `matching.rules`, containing a **forbidden** rule, never
loaded into a real session:

```text
prefix_rule(pattern = ["workmux"], decision = "forbidden")
```

| Command tokens passed to the checker            | JSON result                                        |
| ----------------------------------------------- | -------------------------------------------------- |
| `workmux --version`                             | Matched prefix `["workmux"]`, decision `forbidden` |
| `/opt/homebrew/bin/workmux --version`           | `{"matchedRules":[]}`                              |
| `bash -c 'workmux --version'`                   | `{"matchedRules":[]}`                              |
| `bash -c 'printf prompt \| workmux add sample'` | `{"matchedRules":[]}`                              |

All checker processes exited 0. No checked command was executed. This confirms
the checker's default token matching only; the higher-level execution tool's
shell decomposition and resolved-executable mode remain untested. A no-match
result is not an allow decision and does not confer resource access.

## Initial source-only checkpoint

Replaced all five active stable-bash-token matching claims with guidance to
check the active harness, distinguish command approval from resource access,
report the command/resource/harness and stop dependent steps. Kept existing
invocations; no helper behavior has changed. Added no exclusion or permission
rule to user configuration.

Patch bumps: workmux 1.1.1 to 1.1.2; monitor-pr 3.4.0 to 3.4.1;
publish-report-board 1.3.1 to 1.3.2; dependabot 1.0.0 to 1.0.1.
`make build` completed and regenerated the mirrors. Scoped Markdown lint with
fix and Prettier checks passed; `git diff --check` passed. `make validate`
completed with all JSON, fixture environments and plugin validations passing.

## Tasks pending at the initial checkpoint

Helper diagnostics, the complete semantic catalog sweep, launch/resource
matrix, plants, review loops, Semgrep, final lint, full tests, version audit,
tidy and publication remain pending. No clean review state or passing
acceptance matrix is claimed. Do not retry denied real-resource probes or
change real settings. The scratch-only matching runs below are authorized by
TOOLING's follow-up; they are distinct controlled experiments.

## TOOLING follow-up before parking

At 9:38 PM ET, TOOLING declined to supply recollection and directed live
Claude Code matching runs, using `claude -p`, a temporary settings file and
limited setting sources so only that file loads. Sandbox enabled; one
`excludedCommands` variant per run: bare binary, absolute executable path,
bash script path, pipeline. Record observed outcomes, not inferred matching.

Each variant must exercise scratch resources only: a temporary directory
outside the sandbox allowlist, a private tmux server started with its own `-L`
name and stopped by its recorded PID, and a scratch gh-style config copy.
Never inspect or access real settings, real tmux servers or real gh config
for these runs. Supplement with CLI help and installed runtime text, labeled
as such. The earlier real work-socket read probe will not be repeated.

This answers mailbox question `000002`: use controlled live experiments,
not a fresh session's recollection. The earlier answers remain explicitly
unconfirmed where they described matching. The requested four-variant matrix
has not run. Resume by preparing its scratch fixture and private server,
recording every created path and process PID, then execute and clean up only
those recorded resources. Do not leave a private tmux server running across
the nighttime stop. TOOLING reiterated checkpoint/report by 9:40 PM ET and
parking at 9:45 PM ET.

## Nighttime checkpoint (superseded)

Checkpoint preparation at 9:37 PM ET, 2026-10-28, for the requested nighttime
stop around 9:40 PM ET. TOOLING parks the worker and controls its restart after
8 AM ET. This checkpoint does not complete either issue.

Signed commits so far:

- `de4af294`: plan and initial harness evidence.
- `f5f6b305`: five source corrections, four patch bumps and generated mirrors.

Both signatures verified as `G` through Git's log signature status. The tree
was clean before this checkpoint entry. Every fact-finding process and the
build/validation commands has completed; no child process or background wait
is still running. No push or PR has been attempted.

Resume from this ledger and the plan, then:

1. Follow the scratch-only live matrix direction above, which resolves mailbox
   question `000002`. Keep tool permission rejections distinct from executed
   resource denials. No real settings changes or real servers are involved.
2. Read the remaining sandbox/exemption hits before finishing the semantic
   sweep. The initial full hit list includes review/trim isolation settings,
   use-git's tmpfile assumptions, clean-up-agent-config policy examples,
   attention-log and notify parsing, Homebrew guidance, style references and
   repository validators. None has yet been classified as an additional
   command-exemption dependency. Historical plans remain historical.
3. Implement helper diagnostics and the committed, stub-guarded launch and
   resource matrix. No executable implementation or new test exists yet.
   Preserve existing detached-process completion and uncertain-delivery rules.
   Load `plant-defects` and commit tests before planting diagnostic defects.
4. Complete the full local review order and all remaining checks listed above.
   No review round has started. Recompute the actual origin/main merge base
   when review starts; do not treat the initial base as permanently current.
   TOOLING retains merging and issue labels.

All created temporary files are under the single recorded probe directory.
Keep it for resumption; do not remove files by a shared temporary-path pattern.

## Overnight continuation

TOOLING lifted the nighttime stop in this conversation at 9:39 PM ET and
directed continuing overnight through the PR, stopping only at the ordinary
process stops. This supersedes the parking/restart directions above.

### Scratch-only Claude Code matrix

Recorded fixture root: `/private/tmp/sandbox512-live.dW1szP`. It contains the
workspace, blocked output directory, synthetic `gh/hosts.yml` containing only
`github.com: {}`, the executable `bin/sandbox512-probe`, temporary settings,
prompts and raw JSONL tool results under `results/`. The executable attempts a
write, a private tmux connection, and a synthetic config read, reporting each
status independently. Settings read-deny only that synthetic config, enable
the sandbox, and supply the fixture's PATH. No tool allow rules were added.

Every run: Claude Code 2.1.312, Sonnet at low effort, Bash only, `dontAsk`,
`--setting-sources ''`, a distinct temporary `--settings` file, strict empty
MCP configuration, no persistence, stdin from the recorded prompt. All eight
variant/control processes exited 0 and produced nonempty JSONL including tool
requests, tool results and final results. The table records tool outcomes,
not merely the model's prose:

| Settings variant                | Exact invocation form                            | Observed tool/resource result                 |
| ------------------------------- | ------------------------------------------------ | --------------------------------------------- |
| No exclusions                   | Absolute fixture executable                      | Executed; write, socket and config all denied |
| `sandbox512-probe *`            | Bare fixture binary                              | Tool permission rejected before execution     |
| Absolute fixture path plus `*`  | Absolute fixture executable                      | Tool permission rejected before execution     |
| `bash ABSOLUTE_FIXTURE_PATH *`  | `bash ABSOLUTE_FIXTURE_PATH bash`                | Tool permission rejected before execution     |
| Absolute fixture path plus `*`  | `printf probe \| ABSOLUTE_FIXTURE_PATH pipeline` | Executed; all three resources denied          |
| No exclusions, binary control   | Same bare-binary command                         | Executed; all three resources denied          |
| No exclusions, bash control     | Same bash-script command                         | Executed; all three resources denied          |
| No exclusions, pipeline control | Same pipeline command                            | Executed; all three resources denied          |

The absolute-path baseline is also the absolute-path control. Exclusions
changed the direct commands' permission pathway, while the pipeline remained
confined. Because the excluded direct commands were not approved, their
resource operations did not execute; this is not proof they could access any
resource. No permission grant or broad shell exemption was used. This limited,
measured result is sufficient to reject a universal wrapper/pipeline exemption
assumption, not to recommend a replacement exemption pattern.

Installed-runtime text was read directly from the Claude executable, marked
as supplementary runtime text: it describes excludedCommands as Bash
permission-rule syntax, excluded commands still passing permission checks,
and strict mode accepting only trusted settings tiers, including `--settings`.
`claude --help` separately confirms the meaning of setting sources and settings.
These strings supplement the live controls; they are not execution results.

Private server name: `sandbox512-dW1szP`; socket:
`/private/tmp/tmux-502/sandbox512-dW1szP`. Server PIDs were recorded on creation
and stopped individually with TERM: 43129 (initial matrix), 78167 (controls),
11262 (native resource probes), 30877 (Codex worker resource probe). Each server
was newly created for these experiments with empty tmux configuration and a
scratch sleep pane. No real server was used by this matrix.

### Native tools and resource confirmation

A further isolated Sonnet run set XDG_STATE_HOME and GH_CONFIG_DIR through its
temporary settings environment, removing command-prefix permission ambiguity.
It executed exactly bare `workmux --version`, private-socket `tmux list-sessions`
and `gh config get editor`, once each. Raw tool results in
`results/resources.jsonl`: workmux exit 101 with the rolling-log PermissionDenied
panic; tmux exit 1 naming the private denied socket; gh exit 1 explicitly
naming the scratch `gh/hosts.yml` and operation not permitted. No real gh
configuration was read. The process exited 0 and completed its JSONL result.

This Codex worker's actual full-access tools ran the same scratch probe through
Bash: write, private socket and synthetic config all succeeded, exit 0.
That confirms this configured worker's resource behavior only, not a default
policy for every Codex installation. Its earlier execpolicy checker results
remain limited to the native checker's command-token input; no portable
command exemption is inferred.

The worker also ran `workmux --version` with XDG_STATE_HOME pointing at the
recorded scratch `workmux-state` directory. Exit 0, version 0.1.277; file listing
confirmed `workmux-state/workmux/workmux.log`. Installed workmux runtime text
also names workmux.log, XDG_STATE_HOME and fallback for nonabsolute XDG paths.
This confirms the diagnostic's log-location rule without touching real state.

The optional native Codex sandbox driver investigation used only
`codex-native/config.toml` under the scratch root and `/usr/bin/true` as the
subject. `--strict-config` is unsupported by that driver; a filesystem string
is rejected because a FilesystemPermissionsToml struct is required; empty
filesystem/network tables exited 134 with no output. No sandbox-resource
conclusion is drawn from those failed driver experiments. No real config was
loaded or custom profile installed.

### Implementation and scope decisions

`launch-workmux` adds resource/harness diagnostics to completed failed launch
logs, retaining original output and the original failure status. The shared
diagnostic library recognizes workmux log initialization, tmux socket and gh
config failures, plus other permission-denied output. It identifies native
Claude/Codex environment markers, explicitly labels nested/unknown contexts,
and accepts an optional diagnostic-only caller label.

Claim resource failures now add the harness and claim file/directory/lock
context before the original error. Minimal-PATH help initially exposed an
unnecessary new dirname dependency; pure Bash source-directory resolution
removed it. The existing 100-case claim suite then passed. The prompt composer
has no workmux/tmux/gh access and needs no behavioral change: it reads stdin
and jq. Its behavior is exercised for both harness identities and both Bash
and direct-executable entry points.

The catalog sweep also replaces use-git's unconditional tmpdir sandbox claims
with active-resource checks. Its patch bump is 1.3.5 to 1.3.6. Other sandbox
hits were classified: review/trim settings enforce their separate read-only
contracts; notify/attention-log recognize hook events or CLI flags; Homebrew's
formula sandbox guidance concerns formula tests; clean-up-agent-config lists
configuration surfaces; style references discuss lint/runtime environments;
repository validators check links and explicit review flags. None depends on
excludedCommands to exempt a helper. Generated copies follow canonical edits
through make build; completed plans remain historical evidence.

The new guarded fixture installs committed workmux/tmux/gh/git stubs and refuses
to proceed unless each resolves to its fixture path. The initial eight-case
Scrut document passed: four success cells for composing/launching/claiming;
sixteen resource/harness/invocation cells; a real-tool refusal; pinned
log/socket/config/claim diagnostics; and an unrelated failure control. Existing
launch-options suite passed 16/16. ShellCheck and shfmt passed for new helpers
and fixtures. The existing launcher suite is still running and is not yet
reported as passed. Plants and reviews have not started.

### Completed validation and plants

The existing launcher suite subsequently passed 68/68; claims passed 100/100,
options 16/16 and the new resource suite 8/8. Feature/test checkpoint:
`685a9c41`. Tests were committed before plants. Each plant passed Bash syntax
validation, then failed the actual Scrut document with the assertion below.
Original bytes were restored between plants; restored suite passed 8/8.

| Planted defect                                                                 | Instrument                                    | Observed result                                             | Regression coverage                                                |
| ------------------------------------------------------------------------------ | --------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------ |
| Disable workmux log-marker recognition                                         | Resource matrix and pinned message            | Failed, harness/resource diagnostic missing                 | Log failure cell and pinned log diagnostic                         |
| Replace socket resource identification                                         | Resource matrix and pinned message            | Failed, harness/resource diagnostic missing                 | Socket failure cells and pinned socket diagnostic                  |
| Replace gh config identification                                               | Resource matrix and pinned message            | Failed, harness/resource diagnostic missing                 | Config failure cells and pinned config diagnostic                  |
| Remove claim resource diagnostic                                               | Resource matrix and pinned message            | Failed, harness/resource diagnostic missing                 | Claim failure cells and pinned claim diagnostic                    |
| Replace native Codex label                                                     | Resource matrix and pinned messages           | Failed, harness/resource diagnostic missing                 | Both invocation forms under the Codex identity                     |
| Discard completed launch's original log                                        | Original-error assertions and pinned messages | Failed, original resource error missing                     | Original log/socket/config errors remain visible                   |
| Weaken matrix diagnostic assertion and disable log-marker recognition together | Independent pinned log snapshot               | Exactly 7 passed, 1 failed; pinned log diagnostic caught it | Independent snapshot remains necessary alongside matrix assertions |

Plant logs and `plants.json` are under the recorded scratch root's `results/`.
The final restored run after the weakened-judge experiment passed 8/8. No
temporary source mutation remains. All private servers and fact-finding
processes have finished. Structural and focused review rounds remain unstarted.

## Structural review: Nit round

Fixed review input: base `a2e56c535ed6326cc8d531d945fbb6c627a9b335`, head
`28f2c4386a5b79c30f2cd0966c6daa82cde4a5f8`, snapshot
`a2f4250aeed463475e0efdf3cf00820b9be04df2`. Artifacts are under the recorded
scratch root's `structural-nit/` directory.

- Report-only simplify: fresh read-only Codex, gpt-6.1-sol, high, window 872000.
  Exit 0, nonempty schema-valid result, no findings. The run could not write.
- Anti-pattern Codex attempt: same explicit settings, made read progress and
  exited 1 with "Selected model is at capacity"; no final result. Not clean.
- Permitted fallback: one fresh Opus high reader per production/tests/docs
  group. Read/Glob/Grep only, restricted mode, empty setting sources and MCP,
  temporary settings. No shell or write tools. Initial CLI schema validation
  rejected the draft-2020 dialect annotation before any model ran; the transport
  copy removed only `$schema`, retaining every constraint, and canonical jq
  validation remained required.
- The first fallback packets placed the skill outside the restricted read
  directory. Production/tests explicitly reported incomplete coverage; their
  findings are input, not a clean review. Documentation reported complete,
  but checklist availability was uncertain, so that attempt was not accepted
  as completion either. The packets were corrected by copying the unchanged
  public skill/references inside the permitted scope and including the directly
  referenced sibling stubs and isolation helpers. No read permission was added.
- Completion fallback: all three Opus high processes exited 0, read full files,
  returned nonempty canonical-check-valid JSON with complete=true and no
  unread files. Production: 5 findings; tests: 5; documentation: 3. Their
  original results and prior incomplete attempts are retained separately.
  This completes the same initial Nit round; no severity round was reset.
- Before/after scope comparison: identical tree
  `730c7b489002a531c4bb878add567df867b8aed3`, scope_changed=false, no lasting
  tracked/unignored content changes found. No test/check was run by the readers.

### Finding decisions

Overlapping observations are grouped below; original labels and full evidence
remain in `*-fallback.json` and `*-complete.json`. Every take is within the
branch's resource-diagnostic concern. No Important label is downgraded.

| Finding                                                                                         | Reviewer's label                 | Our severity and impact                                                                                                                        | Take or record                                                                                               | Review again                          |
| ----------------------------------------------------------------------------------------------- | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------- |
| Access wording conflates denials, disk errors, authentication failures and occupied claim locks | `nit`; initial tests `important` | Important: advice can send an agent to an unrelated approval flow                                                                              | Take: neutral operation context, original errors retained; actual denial and ordinary occupied-lock controls | Yes, helper output behavior changes   |
| Fixture leaves owned temporary trees                                                            | Initial tests `important`        | Important: standalone control retained a tree, and earlier Scrut execution directory also remained; repeated runs leave owned resources behind | Take: EXIT cleanup of recorded root, preserve uncertain/interrupted launches                                 | No separate round for test-only edits |
| Raw retained stderr and missing document-level Git reset                                        | Tests `important` for each       | Important: bin/check-fixture-environments reproduced both failures, blocking make validate                                                     | Take: capture_child and first-command Git isolation                                                          | No separate round for test-only edits |
| Unset HOME aborts failure reporting and cleanup                                                 | `nit`                            | Nit: edge-case error path aborts instead of reporting                                                                                          | Take: explicit unavailable-default-path context and fallback tests                                           | Yes, helper branch changes            |
| Prompt/raw-prompt/state temporary failures lack harness context                                 | `nit`                            | Important: the required diagnostic contract is absent on reachable setup failures                                                              | Take: guarded creation/read/render paths, retained errors/status and cleanup tests                           | Yes, helper error handling changes    |
| XDG_STATE_HOME omitted from ambient reset                                                       | `nit`                            | Nit: test-environment isolation rule missed                                                                                                    | Take: reset alongside other XDG inputs                                                                       | No, test-only                         |
| Native caller override, nested and unknown labels untested                                      | `nit`                            | Nit: uncovered new caller forms                                                                                                                | Take: explicit marker and invalid-override cases                                                             | No, test-only                         |
| Denial spellings and default/relative XDG paths untested                                        | `nit`                            | Nit: new diagnostic branches unguarded                                                                                                         | Take: alias, config-load, default/relative/missing HOME and unrelated-cause controls                         | No, test-only                         |
| Fixture mode/argument contract unclear                                                          | Initial tests `nit`              | Nit: misspelled check mode silently prints instead                                                                                             | Take: reject unknown mode and document arguments/exits                                                       | No, test-only                         |
| Sibling library lookup idioms differ                                                            | Initial production `nit`         | Nit: avoidable divergence after minimal-PATH correction                                                                                        | Take: pure Bash source-directory resolution in both callers                                                  | No independent behavioral change      |
| create-worktree composes before a second gh query can be checked                                | Documentation `nit`              | Nit: failed query causes misleading dependent errors, though no launch succeeds                                                                | Take: cache the existing query using the start-issue pattern and compose only after success                  | Covered by next full round            |
| New stop wording conflicts with best-effort and fan-out rules                                   | Initial documentation `nit`      | Nit: unnecessary stops can omit independent reports                                                                                            | Take: stop dependent steps and preserve existing continuation rules                                          | No, prose-only                        |
| Parallel README permission text and link omitted                                                | Documentation `nit`              | Nit: sibling retains the removed approval/access implication                                                                                   | Take: qualify both sections and link resource guidance                                                       | No, prose-only                        |
| Cleanup paragraph asserts one sandbox TMPDIR value                                              | Documentation `nit`              | Nit: unconfirmed universal path claim                                                                                                          | Take: runtime-dependent wording; examples remain examples                                                    | No, prose-only                        |
| Historical checkpoint text looks current                                                        | Initial documentation `nit`      | Nit: ambiguous handoff state                                                                                                                   | Take: current summary and historical section labels                                                          | No, bookkeeping                       |
| Log-path reconstruction duplicates workmux knowledge                                            | Initial production `nit`         | Not a demonstrated wrong path: live scratch workmux 0.1.277 confirmed the rule; HOME failure is handled separately                             | Record implementation coupling; retain required confirmed resource path                                      | No                                    |
| Stat/open mismatch might mislabel a blocked claim file as malformed                             | Initial production `nit`         | Not established: live scratch check returned exists=yes, readable=no and jq open denied, not a contradictory access probe                      | Record unverified pre-existing path; do not change claim semantics without evidence                          | No                                    |
| Unknown terminal caller receives agent-only approval text                                       | Initial production `nit`         | Nit: unnecessary policy text in stderr                                                                                                         | Take through neutral operation-only formatting; policy stays in skills                                       | Covered by helper-output follow-up    |

No Critical findings. The Nit round took behavior-changing fixes, so the
structural loop advances to its first Important round, including report-only
simplify again. No class has yet been fixed in an earlier structural round;
recurrence checks apply from the next round onward.

### Added verification

The revised Scrut resource document passes 17/17; measured standalone runtime
45.94 seconds. It now exercises actual stubbed claim-lock refusal without
creating a lock, occupied-lock/authentication/disk-space controls, all denial
spellings, XDG/HOME fallback forms, caller overrides/nesting, prompt/raw/state
creation, input/read rendering failures and owned fixture cleanup. New retained
output uses capture_child, and the document sources Git isolation first.
ShellCheck and the fixture-environment validator passed these edits.

A live scratch helper probe initially included punctuation as an extra argument;
it only exercised usage validation and is not diagnostic evidence. The corrected
single pipeline ran the actual launcher in the isolated Claude sandbox and
returned 1 after the workmux log panic, the Claude Code/resource-path diagnostic,
and the original workmux status 101. Raw results are in
`results/helper-live-corrected.jsonl`. This preceded the neutral-wording fix;
resource identification was confirmed, not a final-string snapshot.

The separate claim-read probe's direct call returned exists=yes, readable=no,
then jq open denied. Its list call printed no output; the effective claim-path
override was not confirmed, so that second result proves neither success nor
failure against the intended file. It is not used as acceptance evidence.

## Semgrep standing-rule update

TOOLING relayed Chris (he/him)'s tooling-project rule from Inbox at 9:39 PM ET:
a baseline scan that completes with partial parsing of shell files counts when
parse coverage/unparsed files are recorded and ShellCheck passes on those files.
Partial parsing in any other language still stops. The real baseline scan is
still mandatory in a disposable shared clone, with no metrics-off flag.

The fixture guard control now resolves a second committed gh stub outside the
expected stub directory, rather than leaving a real gh fallback available. This
allows a safe guard plant. Unknown harness, invocation, scenario and mode values
are rejected. The resulting 20-case document passes. `make validate` also passes
after the capture_child and Git-reset fixes. Tests are being committed before
plants against the added temporary-file, fallback and cleanup boundaries.

### Final-boundary plants after the Nit fixes

The committed 20-case revision was the baseline before these plants. Each
subject passed Bash syntax checks, each scenario passed its positive control,
and original bytes were restored between mutations. Targeted checks invoke
the same committed fixture assertions used by Scrut; caller snapshots use the
exact committed output contract. Detailed results are in `revision-plants/`.

| Planted defect                                                        | Instrument                                              | Observed result                                                        | Regression coverage                   |
| --------------------------------------------------------------------- | ------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------- |
| Remove each log/socket/config/claim resource identity                 | Guarded fixture check cases                             | Each failed on missing harness/resource context                        | Main resource matrix                  |
| Remove each prompt/raw/state/input/render diagnostic separately       | Corresponding guarded fixture case                      | All five failed on missing harness/resource context                    | Temporary setup/read/render cases     |
| Restore unguarded HOME expansion                                      | HOME-unset fixture case                                 | Failed on missing context after the aborted diagnostic                 | HOME-unset log case                   |
| Reintroduce approval advice for all failures                          | Authentication, disk-space and occupied-lock controls   | All three rejected prescribed approval advice                          | Non-denial controls                   |
| Remove typed-denial or config-load recognition separately             | Alias-specific fixture cases                            | Each rejected lost resource identity                                   | Denial spellings and config-load case |
| Drop original completed-launch output                                 | Socket error fixture case                               | Rejected missing original error                                        | Original-error retention assertion    |
| Break nested, explicit or invalid-override caller behavior separately | Exact caller snapshots                                  | All three changed the expected output                                  | Caller-form snapshots                 |
| Remove the owned-fixture EXIT trap                                    | Empty-owned-parent oracle after a completed mock launch | Helper still exited 0, but the retained fixture made the oracle fail   | Standalone cleanup case               |
| Skip the gh-path guard                                                | Full committed Scrut document                           | 19 passed, 1 failed; only an alternate committed gh stub was reachable | Unexpected-stub-location refusal      |

The cleanup plant's retained directory was recorded before removing only that
completed mock's owned directory. The full restored resource suite then passed
20/20; `/usr/bin/time -p` measured 60.46 seconds (user 5.74, system 8.90).
No temporary source mutation remained. Fixture assertion failures now replay
retained child output before EXIT cleanup; its new snapshot brings the suite
to 21/21. A final snapshot plant for that assertion follows its test commit.
