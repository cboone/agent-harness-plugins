# Silence completion banners for turns no one typed

## Context

Heavy subagent use, from plugins and from a `/loop` conductor session, makes `notify`'s `Done` banners noisy. `notify` already ignores payloads with `agent_id`, so in-process subagents post nothing. The rest come from two sources:

- **Headless Codex runs.** `codex exec` fires the plugin's Codex `Stop` hook; a probe run confirmed it posts a banner. Each run has a fresh session, so the per-turn completion marker never deduplicates them. Callers include `review-anti-patterns`, `review-pr-with-codex`, `trim-comments`, `trim-text` and the sl-health-monitor investigations. Codex's guardian auto-review subagents also run as their own sessions. The `Stop` payload carries `transcript_path` but no session source; the transcript's first line, a `session_meta` record, has `payload.source`: `"cli"` for the TUI, `"exec"` for `codex exec`, and `{"subagent": …}` for subagents.
- **Claude Code turns that no prompt started.** A background task or agent finishing, a peer session's message, a `/loop` or cron wake, and an idle notice each start a main-session turn that ends with `Stop`. In the past week these outnumbered typed prompts by about two to one. Each turn's prompt record carries `turnOrigin`: `human`, `peer`, `task_notification`, `scheduled`, `system` or `sdk`. Older records carry `origin.kind` (`human`, `peer`, `task-notification`) or only `isMeta`. Every record of a turn shares its `promptId`, and messages that arrive mid-turn are `queued_command` attachments, not new prompt records.

Decisions taken: only the macOS banners change, not ntfy pushes or Claude Code's own notifications. Headless Codex runs never post a completion banner. A Claude completion banner fires only when the turn began with the user's prompt, at that turn's end; later wakes stay silent. The fix lives in `notify` alone.

**Classification:** fix (`fix`). One PR on this branch.

## Changes

### 1. `plugins/notify/scripts/notify` (4.1.0 → 4.1.1)

- `codex-stop`: read the first line of `transcript_path` with `head -n 1`; post nothing when its `session_meta` `payload.source` is `"exec"` or an object (a subagent). A missing or unreadable transcript, or any other source, keeps the banner.
- `cc-stop`: classify the current turn from the transcript, newest line first, as the existing extractors do. Take the `promptId` of the newest user record that has one, and read that turn's user records back to the first user record with a different `promptId`, leaving out compaction summaries (`isCompactSummary`) when other records remain:
  - when a record has `turnOrigin`, or failing that `origin.kind`, post only for `human`;
  - otherwise, post unless every prompt record (a user record that is not a tool result) is `isMeta`;
  - with no transcript or no `promptId`, post, as now.
- Suppressed turns post nothing and leave the completion marker alone. Questions, permission prompts and elicitations are unchanged.

### 2. Tests

`tests/fixtures/check-notifications` and `tests/scrut/notifications.md`: Codex `exec` and subagent sources are silent and `cli` posts; Claude turns from `human` post, from `task_notification`, `peer`, `scheduled` and `sdk` are silent, from `origin.kind` alone follow the same rule, from `isMeta`-only prompts are silent, a compaction summary does not override its turn, and a turn without `promptId` posts.

### 3. Documentation

`plugins/notify/README.md`: describe which completions post in What It Does and both When it fires sections.

## Verification

`make build`, `make lint`, `make validate`, `make test-scrut` (at least the notifications documents), and the `check-versions` skill.
