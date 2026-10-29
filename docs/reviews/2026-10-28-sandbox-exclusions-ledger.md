# Sandbox exclusions ledger

## Authority and status

Worker `512-sandbox-exclusions`, reporting only to TOOLING by `mailbox-post`.
Chris's go-ahead: Inbox, 2026-10-28 at 7:38 PM ET, thread "Tooling next batch,
Oct 28 evening", build through a PR ready for review. TOOLING merges.
Branch `fix/512-sandbox-exclusions`; base `main`. Initial merge base with
`origin/main`: `a2e56c535ed6326cc8d531d945fbb6c627a9b335`.

Both issue bodies and every comment were read using explicit repository
arguments. Each issue had one comment, the 2026-10-28 parity amendment.
Repository metadata: active, not a fork, no parent; only origin is configured,
pointing to `cboone/agent-harness-plugins`. Initial branch was clean.
`corepack yarn install --immutable` passed with Yarn 4.18.0.

## Source inventory

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

## Source changes and checks

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

## Remaining validation

Helper diagnostics, the complete semantic catalog sweep, launch/resource
matrix, plants, review loops, Semgrep, final lint, full tests, version audit,
tidy and publication remain pending. No clean review state or passing
acceptance matrix is claimed. Do not retry a denied probe, add permission
rules, or change real settings to obtain missing evidence. TOOLING has the
open Claude harness questions and the probe limitations.

## Nighttime checkpoint

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

1. Read TOOLING's answer to the open Claude harness fact request (mailbox
   question `000002`). Keep the restrictive probe denials distinct from
   executed resource denials. Obtain the remaining matching and resource
   evidence without broad shell exemptions or real settings changes.
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
