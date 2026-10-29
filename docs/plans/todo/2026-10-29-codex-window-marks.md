# Window marks for Claude and Codex

Plan only, based on `origin/main` at `1a42b4534ac873b070130b6be16ced1cbc8f687d`; local `main` is older. The 2026-10-29 go-ahead covers this plan, not implementation or activation. Both harnesses need working, waiting and completed marks without renaming workmux windows.

## Confirmed facts

- Codex 0.165.0: an open-question inquiry (`gpt-6.1-sol`, low, read-only; session `01a18883-e998-7571-84a8-e6a2c341df91`) inspected installed schemas/descriptions. It found native activity/run-state titles, blocked “Action Required”, and the schemas below. Runtime emitted `SessionStart`, `UserPromptSubmit`, `PostToolUse`, `Stop`. No dedicated error hook was established; schemas do not prove firing order.
- Isolated `CODEX_HOME`/`HOME` PTY probes, with tmux variables removed and sample credentials for a local probe provider, captured OSC 0 `Ready → Starting → Ready` and animated `Working`/`Thinking` titles after submitting a prompt. No real credentials or live windows were used. Captures: `terminal-capture.bin` and `terminal-turn-capture.bin` in scratch directory `codex-window-marks-xpoq93pr`. Approval, error and final clearing remain unverified.
- Claude 2.1.312 executable: native `✳` (U+2733), busy `◐`/`◑`, mux-specific static-title switch. Settings select fleet-statusline/claude-powerline; the fleet wrapper saves usage limits, not titles. Enabled `workmux-status@workmux` 1.1.0 hooks set working on prompts/tools, waiting on permission/elicitation notifications, done on Stop; a user hook adds question waiting.
- Read-only config inspection: Codex already selects `activity`, `project-name`, `run-state`, `thread-title`, `task-progress`. Its `hooks.json` invokes `.dotfiles-data/bin/codex-workmux-hook.py`, which ignores subagents and maps prompts/tools to working, questions to waiting, Stop to done and Interrupt to clear. **No permission hook is registered.** `~/.config/tmux/tmux.conf` renders workmux `T/W/D`; `window-names.md` reserves exact worker names. These are separate from native pane titles.

## Proposed contract and carriers

Extend the repository `workmux` plugin with split hook manifests and a shared adapter based on the local helper. CONFIG retires duplicate registrations. Preserve native title ownership; add no watcher. Upstream workmux Codex hooks are another reference; verify their installer assumptions before reuse.

| State and existing mark                              | Claude event that sets it                                         | Codex event that sets it                             | Event that clears or replaces it                                                                      |
| ---------------------------------------------------- | ----------------------------------------------------------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Working: `` U+F021, blue; terminal tab `🐝`         | `UserPromptSubmit`; tool resumption                               | `UserPromptSubmit`; tool resumption                  | A wait, root Stop, interrupt or session end                                                           |
| Waiting: `` U+F251, yellow; terminal tab `⏳`       | Permission/elicitation notification; `PreToolUse:AskUserQuestion` | `PermissionRequest`; `PreToolUse:request_user_input` | Matching tool result/resolution resumes working; denial/cancel must clear; root Stop replaces it      |
| Completed: green, no extra window glyph              | Root `Stop`                                                       | Root `Stop`                                          | Next prompt; interrupt/session cleanup removes stale state                                            |
| Interrupted or closed: no status mark                | Verify cleanup event coverage                                     | `Interrupt`/`SessionEnd` candidates                  | Next root prompt starts working                                                                       |
| Error: attention required, proposed reuse of waiting | Verify `StopFailure` coverage                                     | No verified dedicated hook                           | Acknowledgment/retry or session cleanup; unresolved, never equate an error with successful completion |

The adapter observes only, returns no permission decisions, targets the originating pane/server, ignores subagents and preserves waits across unrelated parallel tool completions. Failures must leave the harness usable. Unverified transitions block activation.

Native pane titles retain Claude's `✳`/animation and Codex's spinner/“Action Required”; verify blocked entry/clearing. Do not derive workmux state from title text.

## CONFIG request and validation

After separate build approval, package the adapter in `plugins/workmux/`, add split manifests, bump its minor version/catalog descriptions and regenerate mirrors. CONFIG separately owns replacing `.codex/hooks.json` registrations, reviewing/trusting changed Codex hooks, disabling Claude's duplicate upstream status plugin/question hook, and updating `~/.config/tmux/window-names.md` for both harnesses. Preserve current glyphs, title settings, window formats and names unless a rendered test establishes a necessary change. No installation or activation belongs to this branch.

Before activation, capture event payloads and title bytes in isolated homes for both harnesses: prompt, completion, continued Stop, permission allow/deny/cancel, question answer/dismissal, elicitation, interrupt, API/tool error, exit/resume and subagent/parallel-tool overlap. Verify daemon-attached Codex pane identity separately from standalone runs. Commit scrut fixtures and refusing stubs for workmux/tmux; test missing tools, malformed input, duplicate/out-of-order events and unchanged window names. Plant a missing permission transition and an unrelated-tool wait clear; both tests must fail. Run scoped checks, `make build`, `make test-all`, version checks and required local reviews before a future PR.

Open questions: which prompt-resolution events actually fire, whether all question paths reach tool hooks, whether error stops emit usable events, and how native Codex activity clears after each outcome. Confirm these from live isolated runs before promising parity. [Official hook documentation](https://learn.chatgpt.com/docs/hooks) describes permission requests before approval and interruption cleanup; it supplements, rather than replaces, installed-harness evidence.
