# Tier-aware notify banners and sounds

Design proposal for #638. Implementation starts only after the decisions at the end are made.

## Context

`notify` was built for a person running a few independent sessions, one per repository. Many sessions now run in tiers, each in a named tmux window, often on more than one tmux server:

- **Top coordinator:** one session that keeps the person's list of open asks, one line per ask, and relays between projects.
- **Leads:** a conductor per project, plus standing sessions such as monitors. They are the only sessions that ask the person anything. When one needs an answer, it asks once in its own window and sends the top coordinator one line for the list.
- **Workers:** one per workstream worktree. A worker reports to its lead by message and never asks the person anything. Its permission prompts still appear in its own window.

Most turns in this setup start from a message sent by another session or from a background task, and those turns already end silently. Two kinds of turn still look like the person's own: a brief that a launcher passes as a worker's first prompt, and text that tooling types into a pane. Both carry the `human` turn origin, verified in a worker's transcript, so the existing origin rule cannot hold them back.

The issue lists four mismatches: the subtitle (`<repo> · <task>`) does not say where to act, every session looks and sounds equally urgent, repository chimes blur together because every worker in a repository shares one, and clicking a banner goes nowhere. Sessions outside such a setup must keep working as they do now.

Survey findings that shape the design:

- **Visibility suppression never runs inside tmux.** tmux 3.2 and later set `TERM_PROGRAM=tmux` in every pane, so `originating_pane_visible` finds no known terminal and posts the completion banner even when the person is watching the pane. The tmux server's global environment still holds the real terminal (`TERM_PROGRAM=Apple_Terminal`), and so does `__CFBundleIdentifier`. The `focused` client flag works when tmux has `focus-events on`.
- **A Claude session's name is in its pane title.** Claude Code sets the title to a status glyph and the session name, such as `✳ ATLAS`. Unnamed sessions show a generated task title. Codex sets no name.
- **Some window names use icon-font glyphs** from Unicode private-use areas, which macOS banners cannot render. jq's `\p{Co}` finds them.
- **A waiting `alerter` is expensive.** Measured on macOS 26 with `alerter` 26.5, three silent banners whose `alerter` processes waited for a click cost `usernoted` 1.17 s of CPU per 10 s (11.7% of a core) against nothing at rest, and the three processes used 1.79 s of their own over the same stretch. That is the load the fire-and-forget change in 4.0.0 removed.

## Goals and non-goals

Goals:

- Name where to act on every banner from a tiered session, as `<tmux session>: <window>`.
- Post a banner or sound only when nothing else will reach the person, so a banner never repeats an ask that already has a line in the top coordinator's list or a relay through a lead.
- Let the chime say which tier is calling, and spread one repository's workers across pitches.
- Keep every session outside a configured setup exactly as it is today.

Non-goals:

- Push notifications. `notify` posts local macOS banners only, and the separate `push-notification` plugin is untouched.
- Deciding what goes on the top coordinator's list. That stays with the sessions' own instructions.
- Producing sound files. The separately produced chime set changes in its own repository (see [Changes in the sound set's repository](#changes-in-the-sound-sets-repository)).

## Tiers and how a session finds its tier

Four tiers: `top`, `lead`, `worker` and `direct`. `direct` covers every other session once tiers are configured: a repository's home window, an ad hoc task window, or a worktree session the person works with directly. A session with no tier configuration at all is _untiered_ and behaves exactly as today.

### Signals

Each signal is something any tmux user or harness already has. Only the patterns that match them are specific to one setup.

| Field     | Source                                                                                 | Available                 |
| --------- | -------------------------------------------------------------------------------------- | ------------------------- |
| `window`  | tmux window name of `$TMUX_PANE`                                                       | in tmux                   |
| `session` | tmux session name                                                                      | in tmux                   |
| `server`  | tmux server name, the socket's basename from `$TMUX` (`default` unless `-L` names one) | in tmux                   |
| `name`    | pane title without leading status glyphs: the Claude session name when it has one      | in tmux; Claude Code only |
| `dir`     | `$CLAUDE_PROJECT_DIR`, or the hook's working directory                                 | always                    |

One `tmux display-message` call reads the first four fields, replacing the call that reads the pane title today. A workmux handle shows up as the window name or the worktree directory, so it needs no field of its own.

### Rules file

`${XDG_CONFIG_HOME:-$HOME/.config}/agent-harness-notify/tiers` holds one rule per line:

```text
# tier    field    pattern (POSIX extended regular expression)
top       window   ^coordinator$
worker    window   ^w[ ]
lead      window   ^conductor$
lead      name     ^[[:upper:]][[:upper:][:digit:] /&-]*$
```

- The pattern is the rest of the line, leading whitespace removed, matched with bash `=~`. Write a significant space as `[ ]`, since editors strip trailing spaces, and use classes such as `[[:upper:]]` rather than ranges such as `[A-Z]`, whose meaning depends on the locale.
- The first matching rule wins. A session that matches none is `direct`.
- Blank lines and lines starting with `#` are skipped. A line with an unknown tier or field, or a pattern bash cannot compile, is skipped too.
- A rule on a field that is unavailable, such as `window` outside tmux, does not match.

The example classifies a top coordinator and leads by window name, treats any session whose name is all capitals as a standing session, and marks workers by a window prefix. A setup that keeps worktrees in a fixed layout can match workers by `dir` instead, which also keeps a worktree the person works in directly out of the worker tier.

### Precedence and defaults

1. `NOTIFY_TIER=top|lead|worker|direct` in the harness's environment wins, so a launcher can set the tier when it starts a session, with or without tmux. Any other value is ignored.
2. Otherwise the rules file decides, as above.
3. With neither, the session is untiered. The plugin ships no rules, so nothing changes until a person writes some.

`notify explain`, a new subcommand for checking a configuration, prints the current pane's tier, the rule that matched, its place, and the sound each role would play.

## What fires, per tier and event

| Event                                         | `top`  | `lead` | `worker`                 | `direct` | Untiered |
| --------------------------------------------- | ------ | ------ | ------------------------ | -------- | -------- |
| Done, turn started by a prompt                | posts  | posts  | silent                   | posts    | posts    |
| Done, turn started by a session, task or wake | silent | silent | silent                   | silent   | silent   |
| Permission prompt                             | posts  | posts  | posts, title `Worker: …` | posts    | posts    |
| Question, elicitation dialog or plan approval | posts  | posts  | posts, title `Worker: …` | posts    | posts    |

"Posts" means a banner with its role's sound. Done banners stay subject to visibility suppression, which this change makes work inside tmux. Questions and permission prompts post whatever the focus, as today.

Why, and how each relates to the top coordinator's list and the relay through leads:

- **Lead and top, Done after a prompt:** the person started this turn in that window, so the banner says their own conversation has a reply; it is not a new ask. If the reply ends with an ask, the window holds it and the session adds its one line to the list as its instructions say. The banner is the transient alert and the list stays the record.
- **Every tier, Done after a message or background task:** silent, as today. Anything a lead raises during such a turn reaches the person only through its window and its line on the list, never as a banner. This is the path most asks in the tiered setup take.
- **Lead and top, blocking prompts:** a permission prompt, question dialog or plan approval stops the session until the person answers in that window. A session stopped at a prompt cannot send its line to the list, so the banner is the only signal and does not repeat one.
- **Worker, Done:** silent. A worker reports to its lead by message, and the lead relays what the person needs. Its prompt-started turns are mostly briefs or text typed by tooling, so a banner would repeat the report. A person typing in a worker's window is usually watching it; a setup that wants banners there can classify those sessions as `direct`.
- **Worker, blocking prompts:** posts. A worker stopped at a permission prompt cannot message its lead, and the lead gets no idle notice while the prompt waits, so nothing else reaches anyone. A question from a worker breaks the worker rules, and the `Worker:` title makes that visible while still unblocking the session.
- **Direct and untiered:** exactly today's events. `direct` adds only the place subtitle and its own sounds.

## Banner text

- **Title:** unchanged, with a `Worker:` prefix and a space for the worker tier.
- **Subtitle:** with tiers configured and a tmux pane, the place `<tmux session>: <window>`. Private-use glyphs are removed from the window name; if nothing is left, the Claude session name stands in, and without a name the subtitle is the tmux session alone. Outside tmux, or untiered, it stays `<repo> · <task>`. The tmux server is left out, so sessions with the same name on two servers share a place.
- **Body, icon and limits:** unchanged.

### Mockups

A sample setup: tmux session `hub` holds the top coordinator (window `coordinator`, session name `HUB`) and a standing monitor in a window named with one icon-font glyph (session name `MONITOR`); tmux session `atlas` is a project with its conductor (window `conductor`) and a worker (window `w 42-fix-parser`); `sample-repo` is a repository's home window. Sounds use `NOTIFY_SOUND_SET=Chord`, with the built-in sound in parentheses.

```text
┌ Claude Code ───────────────────────────────────────────────────────┐
│ Done                                                               │
│ atlas: conductor                                                   │
│ Draft PR 12 is ready: the parser fix passes every check.           │
└────────────────────────────────────────────────────────────────────┘
  lead, Done after your prompt: Chord-lead-stop-<n> (Glass)

┌ Claude Code ───────────────────────────────────────────────────────┐
│ Worker: Approve Bash?                                              │
│ atlas: w 42-fix-parser                                             │
│ make test                                                          │
└────────────────────────────────────────────────────────────────────┘
  worker, permission prompt: Chord-worker-permission-<n> (Funk)
```

| Tier and event               | Title                           | Subtitle                   | Body                                                 | Sound                                |
| ---------------------------- | ------------------------------- | -------------------------- | ---------------------------------------------------- | ------------------------------------ |
| top, Done after a prompt     | `Done`                          | `hub: coordinator`         | `Two decisions wait in atlas: conductor.`            | `Chord-top-stop-<n>` (Glass)         |
| top, question                | `Question`                      | `hub: coordinator`         | `Close the three stale items?`                       | `Chord-top-attention-<n>` (Tink)     |
| top, permission              | `Approve Bash?`                 | `hub: coordinator`         | `gh pr view 12`                                      | `Chord-top-permission-<n>` (Funk)    |
| lead, Done after a prompt    | `Done`                          | `atlas: conductor`         | `Draft PR 12 is ready: the parser fix passes every…` | `Chord-lead-stop-<n>` (Glass)        |
| lead, Done after a message   | none                            |                            |                                                      | none                                 |
| lead, two questions          | `2 questions`                   | `atlas: conductor`         | `Start the parser workstream now? (+1 more)`         | `Chord-lead-attention-<n>` (Tink)    |
| lead, permission             | `Approve Bash?`                 | `atlas: conductor`         | `make release`                                       | `Chord-lead-permission-<n>` (Funk)   |
| lead, plan approval          | `Plan ready for review`         | `atlas: conductor`         | `Split the parser into two passes`                   | `Chord-lead-attention-<n>` (Tink)    |
| lead in a glyph-named window | `Question`                      | `hub: MONITOR`             | `Silence the disk alert until Monday?`               | `Chord-lead-attention-<n>` (Tink)    |
| worker, Done                 | none                            |                            |                                                      | none                                 |
| worker, permission           | `Worker: Approve Bash?`         | `atlas: w 42-fix-parser`   | `make test`                                          | `Chord-worker-permission-<n>` (Funk) |
| worker, question             | `Worker: Question`              | `atlas: w 42-fix-parser`   | `Rename the parser module?`                          | `Chord-worker-attention-<n>` (Tink)  |
| worker, plan approval        | `Worker: Plan ready for review` | `atlas: w 42-fix-parser`   | `Split the parser into two passes`                   | `Chord-worker-attention-<n>` (Tink)  |
| direct, Done after a prompt  | `Done`                          | `sample-repo: sample-repo` | `Fixed the flaky test.`                              | `Chord-direct-stop-<n>` (Glass)      |
| untiered or outside tmux     | `Done`                          | `sample-repo · fix-parser` | `Fixed the flaky test.`                              | `Chord-stop-<n>` (Glass)             |

## Sounds

### Mapping

- **The role still sets the gesture:** `stop` for completion, `permission` for permission prompts, `attention` for questions, elicitation and plan approval.
- **The tier picks a subset:** a tiered session looks for `<prefix>-<tier>-<role>-<n>` files, counted from `0` to the first gap like today's set. Without index `0` it falls back to the plain `<prefix>-<role>-<n>` set, then to the built-in sound, so a session never goes silent for lack of files.
- **The place picks the variant:** with a place, the hash key is the place string instead of the repository name, so a conductor and each of its workers get their own pitch, while each tier's subset sets the timbre. Without a place it stays the repository name.
- **Untiered sessions:** unchanged, down to the selected index.
- **Without a sound set:** every tier keeps Glass, Funk and Tink. Telling tiers apart by ear then rests on which events fire.

### What the sound set needs

The installed chime set has 40 slots per role: four timbres across ten degrees of one pentatonic scale. Tier subsets fit it without new rendering: one timbre per tier, ten degrees each, installed under the tier names. A suggested starting assignment, to settle by listening: the sonar ping for `top`, the handbell for `lead`, the soft chime for `worker` and the bar for `direct`. The plain 40-slot set stays for untiered use.

The set's two open follow-ups change weight:

- **Equal perceived loudness across the range** comes first. Once timbre carries the tier, a timbre that sounds quieter reads as less urgent by accident. Equalize the set, then decide by listening whether any tier gets a deliberate offset.
- **Nearby variants per slot** matter less. Silent worker completions and per-place hashing remove most exact repeats, so park this until listening with tiers shows a need. If it comes back, add an optional `-v<k>` suffix chosen at random, which needs no saved state and works with tier subsets.

## Clicking a banner

Clicking can take the person to the session's window only while the `alerter` that posted the banner is still running, because `alerter` reports the click on its own standard output. The plugin stops every `alerter` with `SIGKILL` 2 seconds after launch, which keeps the banner but drops the click. The options:

1. **Keep `alerter` waiting for ask banners**, then on a click select the tmux window and pane, select the terminal tab showing that tmux session (by its tty, through AppleScript for Terminal and iTerm2) and bring the terminal forward. It works, but each waiting banner costs about 4% of a core in `usernoted` plus about 5% in its own process (measured above), until it is clicked, dismissed, expired or stopped at the session's next prompt. It needs a cap on waiting processes and brings back the load that 4.0.0 removed.
2. **A `notify focus` subcommand**, bound to a key, jumps to the newest open ask with the same window and tab selection. It costs nothing between events and works across tmux servers, but the person binds a key, and the plugin has to publish a stable path to the script, since installed plugin paths include the version.
3. **Neither:** the place subtitle names the window and the person switches by hand.

What clicking a stopped banner does today is unverified. Banners are posted as Terminal, so a click may bring Terminal forward without choosing a tab.

## Visibility suppression inside tmux

Inside tmux, `originating_pane_visible` reads the terminal from `__CFBundleIdentifier`, and failing that from the tmux server's global `TERM_PROGRAM` (`tmux show-environment -g TERM_PROGRAM`). Outside tmux it keeps `TERM_PROGRAM`. Both values come from where the tmux server started, so a client attached from another terminal is compared with the wrong application, and the banner is posted; every unknown still posts. The README gains the `focus-events on` requirement. This applies to every tmux user, tiered or not, because it restores documented behavior.

## One banner per session

Each session keeps at most one banner. All of a session's events share one group, so a new banner replaces the last, and the session's next prompt removes it with `alerter --remove`. Notification Center then holds one current banner per waiting session instead of a second, stale list of asks next to the top coordinator's. Replacing by group is how the plugin already keeps sessions apart. Removing is unverified under Terminal impersonation, because `alerter --list` sees none of the banners posted as Terminal on the development Mac; check it by eye before relying on it, and drop that half if it fails. Hook commands do not change, so Codex keeps its trust in them.

## Configuration summary

| Setting                | Where                                                          | Effect                                                |
| ---------------------- | -------------------------------------------------------------- | ----------------------------------------------------- |
| Tier rules             | `${XDG_CONFIG_HOME:-$HOME/.config}/agent-harness-notify/tiers` | Classifies sessions; its presence turns tiers on      |
| `NOTIFY_TIER`          | harness environment                                            | Forces a tier, for launchers or sessions outside tmux |
| `NOTIFY_SOUND_SET`     | harness environment                                            | Unchanged; tier subsets are found by name             |
| `NOTIFY_WAIT_LIMIT`    | harness environment                                            | Unchanged                                             |
| tmux `focus-events on` | tmux configuration                                             | Needed for visibility suppression                     |

## Codex parity

- Tier detection and banner text depend on tmux, the environment and the working directory, so they are the same for Codex. Codex sets no session name, so `name` rules never match a Codex session.
- Codex wires `Stop`, `UserPromptSubmit` and `PreToolUse:request_user_input`. The worker policy silences Codex worker completions, which matters more than for Claude Code, since Codex cannot tell a turn started by another session from a typed one.
- Codex has no permission hook. A Codex worker stopped at an approval prompt relies on Codex's own terminal notification, which knows nothing of tiers. This is a known limitation.
- Hook definitions do not change, so trusted Codex hooks stay trusted.

## Outside a tiered setup

- **No rules file and no `NOTIFY_TIER`:** every title, subtitle, body, sound and event is as today. The existing scrut expectations stay as they are.
- **Plain checkout, single session, no tmux:** unchanged. A `dir` rule or `NOTIFY_TIER` can still give such a session a tier; without a place it keeps `<repo> · <task>` and the repository hash.
- **Changes everyone sees:** visibility suppression starts working inside tmux, and a session's banners replace one another.

## Risks

- **Misclassification.** A lead taken for a worker loses the Done banners for the person's own prompts; a worker taken for a lead is as noisy as today. `notify explain` and first-match order keep rules easy to check.
- **Prompts typed by tooling** still count as the person's own in lead sessions, so a launcher that resumes a lead with a prompt posts a Done banner.
- **A turn typed in a worker's window and then left** posts nothing.
- **The pane title** can be changed by other programs, and Codex sets no name.
- **Regular expressions:** a locale-dependent range or a trailing space stripped by an editor makes a rule miss. The README examples avoid both, and tests run in the C and UTF-8 locales.
- **Shared session names** across tmux servers give two sessions one place and one hash.
- **Chime changes:** tiered sessions' chimes change once, since the hash key changes.
- **Terminal detection inside tmux** follows where the tmux server started and can name the wrong application; that only ever posts a banner.
- **Removing banners** may not work under Terminal impersonation (see [One banner per session](#one-banner-per-session)).
- **Cost:** one tmux call with more fields replaces an existing one, plus a small file read. Removing banners adds one short `alerter` run per prompt.

## Test plan

- **Unchanged suites:** `tests/scrut/notifications.md` and `tests/scrut/notification-sounds.md` keep their expectations, which pins untiered behavior.
- **New document,** `tests/scrut/notification-tiers.md`, through `tests/fixtures/check-notifications` with its tmux stub extended to return session, window, server and title from test variables, and a fixture `XDG_CONFIG_HOME`:
  - Rules: each field, first match wins, comments and blank lines, unknown tier or field, a pattern bash cannot compile, a missing file, `NOTIFY_TIER` precedence and invalid values, and multibyte window names in the C and UTF-8 locales.
  - Events: the policy table for every tier, for Claude Code and Codex, including silent worker completions and `Worker:` titles.
  - Text: the place subtitle, private-use glyphs replaced by the session name, then by the tmux session, and the old subtitle outside tmux.
  - Sounds: tier subset, fallback to the plain set, fallback to the built-in sound, and the place as hash key, with pinned `cksum` vectors.
  - Visibility: `TERM_PROGRAM=tmux` with `__CFBundleIdentifier`, with only the global tmux environment, and with neither.
  - One banner per session: shared group, and removal at the next prompt.
  - `notify explain` output.
- **Planted defects** (`plant-defects`), each shown to fail its test: worker completions posted, rule order ignored, glyphs kept, tier subset skipped, the tmux terminal fallback removed.
- **Parsing and runtime:** `/bin/bash -n` under bash 3.2, and the new document timed alone against the half-of-ten-minutes budget.
- **By hand on macOS:** sample banners for each tier from a real rules file, a Done banner suppressed while its pane is watched in tmux, and banner removal checked in Notification Center.

## Implementation outline

- `plugins/notify/scripts/notify`: tier detection and rules parsing, the place, the event policy, title prefix, tier sound subsets and hash key, the tmux terminal fallback, per-session groups and removal, and `explain` (plus `focus` if chosen).
- `plugins/notify/README.md`: tiers, rules file, place subtitle, sound subsets, `focus-events`, and the click answer.
- Tests and fixture as above; register any new paths in the Makefile's `SCRUT_ENV` and CI's `scrut-env`.
- Version 4.2.0 in both manifests, `make build`, `make test-all` and `check-versions`.

## Changes in the sound set's repository

These happen where the chime set is produced, under their own go-ahead:

1. Install tier subsets as `notify-chime-<tier>-<role>-<n>.aiff` for `top`, `lead`, `worker` and `direct`, one timbre each across the ten degrees, next to the plain 40-slot set, and teach the installer's stale-file cleanup the new names.
2. Hold a listening round to assign timbres to tiers, starting from the suggestion above.
3. Equalize perceived loudness before installing the subsets, then decide any per-tier offset by listening.
4. Park nearby variants; if revived, use the `-v<k>` suffix contract above.

## Decisions

1. **Event policy:** adopt the table above, with silent worker completions. Recommended.
2. **Tier detection:** a rules file over `window`, `session`, `server`, `name` and `dir`, with `NOTIFY_TIER` taking precedence and no shipped defaults. Recommended.
3. **Banner text:** the `<tmux session>: <window>` subtitle for every tiered session in tmux, `direct` included, and the `Worker:` title prefix. Recommended.
4. **Sounds:** tier subsets by file name, the place as hash key, built-in sounds unchanged per tier, loudness equalization before the subsets, variants parked. Recommended.
5. **Clicking:** no waiting `alerter`. Recommended: neither option in this change, with `notify focus` filed as a follow-up issue. Alternatively, build `notify focus` here.
6. **Visibility inside tmux:** fix it in this change. Recommended.
7. **One banner per session:** replace by group in this change, and remove at the next prompt if a check by eye confirms `alerter --remove` works. Recommended.

## Log

- 2026-10-22: Surveyed the plugin, the sound-set history and a tiered setup. Measured the cost of waiting `alerter` processes with silent sample banners. Found visibility suppression inert inside tmux. Wrote this proposal.
