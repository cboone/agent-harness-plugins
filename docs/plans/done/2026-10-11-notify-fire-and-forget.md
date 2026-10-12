# Notify: fire-and-forget alerts without click-to-focus (#594)

## Context

Every notify alert leaves an `alerter` waiting so a banner click can focus the originating pane. Each waiting `alerter` 26.5 polls `usernoted` every 0.2 seconds, and the cost grows roughly with the square of the number waiting: a dozen across sessions saturated `usernoted` and used about three cores. #591 bounded each session to one waiting `alerter` plus a 30-minute watchdog, which is not enough with many sessions. Click-to-focus is no longer needed, and `SIGKILL` about a second after launch still delivers the banner, with sound, and leaves it in Notification Center. So every harness should launch `alerter`, wait a short delivery grace period, and stop it with `SIGKILL`.

Classification: feature (breaking). Commit prefix `feat`.

## Decision: `NOTIFY_WAIT_LIMIT`

Keep `NOTIFY_WAIT_LIMIT`, repurposed as the delivery grace period in whole seconds, default `2`. Anyone already using the issue's `NOTIFY_WAIT_LIMIT=2` workaround keeps working, and the knob stays available if a banner is lost under load. Same regex validation as today (`^[1-9][0-9]{0,8}$`). OpenCode reads the same variable, so all three harnesses behave alike.

## Changes

### 1. `plugins/notify/scripts/notify`

- Header comment: events fire detached and `alerter` is stopped after delivery; drop click wording.
- Remove `FOCUS_SCRIPT`; move `bundle_id_for` (only its six-terminal `case`, default `com.apple.Terminal`) into `notify` for `originating_pane_visible`, which currently shells out to `focus-pane --bundle-id`.
- `WAIT_LIMIT` default `2`, comment rewritten as the delivery grace period.
- Keep `FIRE_TIMEOUT` as a backstop for an `alerter` the grace-period `SIGKILL` never reaches; update its comment.
- Remove `stop_session_alerters` (per-session `pkill`) and `compute_tmux_state`.
- Keep `stop_alerter` (PID plus start-time check, `SIGKILL`) and its comment about `SIGTERM`/`SIGINT` removing the banner.
- Rewrite `fire_alerter_detached`: keep group suffix, Stop dedupe marker, visibility suppression and optional sound. The detached subshell launches `alerter` in the background with output to `/dev/null`, records its `lstart`, sleeps `WAIT_LIMIT` unless it exits first (poll in 1-second steps with `kill -0`, as the watchdog loop does now), then calls `stop_alerter`. No result capture and no click handling. Keep the `disown` comment.

### 2. Delete `plugins/notify/scripts/focus-pane`

Its only remaining use, `--bundle-id`, moves into `notify`.

### 3. `plugins/notify/opencode/index.ts`

- Remove `FOCUS_SCRIPT`, `TmuxState`, `computeTmuxState`, the `tmux` argument at the three call sites and in `AlerterArgs`.
- Add `WAIT_LIMIT` read from `process.env.NOTIFY_WAIT_LIMIT` with the same validation and default.
- `fireAlerterDetached` uses `Bun.spawn(["alerter", ...], { stdout: "ignore", stderr: "ignore" })` inside `try`, then a `setTimeout` that calls `proc.kill("SIGKILL")` when `proc.exitCode === null`. Keep `--timeout` as the same backstop. Spawn failures stay silent.

### 4. `plugins/notify/README.md`

- Replace the click-to-focus bullet with a fire-and-forget bullet: banners stay in Notification Center, clicking one does nothing beyond what macOS does.
- Move the supported-terminal list (now used only by the visibility check) into the visibility bullet; delete the "Click-to-focus details" section.
- Codex section: drop "and click routing".
- Notes and caveats: replace the #591 waiting-alerter caveat with the grace-period behavior: `SIGKILL` after `NOTIFY_WAIT_LIMIT` seconds (default 2) on every harness, why `SIGKILL`, and raising it if banners go missing under load. Drop "`alerter` blocks waiting for user interaction" wording in the first bullet.

### 5. Tests: `tests/fixtures/check-notifications` and `tests/scrut/notifications.md`

- Remove the `click`, `replace`, `other-session` and `watchdog` scenarios and their scrut cases.
- `duplicate`: stop holding the stub and drop the `kill -0` check, which would race the grace period.
- Add `delivery`: held stub with `NOTIFY_WAIT_LIMIT=1`; assert the stub stops within 6 seconds under parallel load and no `SIGTERM` was logged. Scrut case "Alerter stops after delivery".
- Keep the `unset NOTIFY_WAIT_LIMIT` line (comment unchanged in spirit).

### 6. Repository docs

- `.github/instructions/shell.instructions.md`: replace the two notify bullets (lock-free launch, watchdog and click-to-focus) with one: `notify` stops each `alerter` with `SIGKILL` after the grace period on purpose, since `SIGTERM`/`SIGINT` remove the banner, and two concurrent hooks each stop only their own `alerter`.
- `docs/plugin-development.md`: drop `focus-pane` from the notify tree.

### 7. Versions and mirrors

- Bump notify to the next major version in `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`: `4.0.0`, since #606 released `3.0.0` while this work was under review.
- `make build`, then run the `check-versions` skill.

## Commits

1. `feat!: make notify alerts fire-and-forget (#594)` for script, OpenCode, tests, README, docs, versions.
2. `chore: rebuild mirrors for notify (#594)`.
3. Plan file commit(s) along the way.

## Verification

- `make lint`, `make validate`, `make test-scrut SCRUT_TEST_DIR=tests/scrut/notifications.md`, then `make test-all`.
- `/bin/bash -n plugins/notify/scripts/notify` (covered by scrut).
- Manual on macOS: pipe a sample payload to `notify codex-stop` and `cc-question` with real `alerter`; confirm the banner and sound appear, the banner remains in Notification Center, and `pgrep -fl alerter` is empty after about 3 seconds.

### Manual results (2026-10-11)

Run with Homebrew's unpatched `alerter` 26.5 first on `PATH`, ahead of the locally patched build from #454.

- `cc-question`: the banner appeared, one `alerter` was running at 1 second, and none remained at 4 seconds.
- `codex-stop`: the banner appeared, and no `alerter` remained at 4 seconds.
- Five `cc-question` alerts from separate sessions fired back to back: all five banners appeared and stayed in Notification Center, and no `alerter` remained at 4 seconds.
- Alerts fired within the same moment play a single sound. macOS appears to merge the sounds before the stop applies.
- OpenCode was not checked by hand. Its detached `sh` stop was checked with Bun 1.4.2 and a stub `alerter`.

### Merge with #606

PR #606 removed the OpenCode adapter and released notify `3.0.0`. Merging `main` dropped this branch's OpenCode changes (section 3) and the OpenCode caller of `scripts/fire-alerter`, which now serves the Claude Code and Codex hooks only.

## Follow-up

- #454 (locally patched `alerter`) can be revisited once this lands; note it in the PR.
