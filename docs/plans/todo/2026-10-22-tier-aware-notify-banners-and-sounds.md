# Tier-aware notify banners and sounds

Approved design for #638, with the decisions recorded at the end.

## Context

`notify` was built for a person running a few independent sessions, one per repository. Many sessions now run in tiers, each in a named tmux window, often on more than one tmux server:

- **Top coordinator:** one session that keeps the person's list of open asks, one line per ask, and relays between projects.
- **Leads:** a conductor per project, plus standing sessions such as monitors. They are the only sessions that ask the person anything. When one needs an answer, it sends the top coordinator one line for the list, then asks once in its own window.
- **Workers:** one per workstream worktree. A worker reports to its lead by message and never asks the person anything. Its permission prompts still appear in its own window.

Most turns in this setup start from a message sent by another session or from a background task, and those turns already end silently. Two kinds of turn still look like the person's own: a brief that a launcher passes as a worker's first prompt, and text that tooling types into a pane. Both carry the `human` turn origin, verified in a worker's transcript, so the existing origin rule cannot hold them back.

The issue lists four mismatches: the subtitle (`<repo> · <task>`) does not say where to act, every session looks and sounds equally urgent, repository chimes blur together because every worker in a repository shares one, and clicking a banner goes nowhere. Sessions outside such a setup must keep working as they do now.

Survey findings that shape the design:

- **Visibility suppression never runs inside tmux.** tmux 3.2 and later set `TERM_PROGRAM=tmux` in every pane, so `originating_pane_visible` finds no known terminal and posts the completion banner even when the person is watching the pane. The tmux server's global environment still holds the real terminal (`TERM_PROGRAM=Apple_Terminal`), and so does `__CFBundleIdentifier`. The `focused` client flag works when tmux has `focus-events on`.
- **A Claude session's name is in its transcript.** `claude --name` writes `agent-name` records, and renaming writes `custom-title` records, repeated through the file. A fixed-string `grep` finds them in a 460 MB transcript in 0.06 s, where a reversed `jq` scan takes 1.8 s. The pane title shows the same name, but an unnamed session's pane title is a generated task title that a name rule could match by accident. Codex sets no name.
- **Some window names use icon-font glyphs** from Unicode private-use areas, which macOS banners cannot render. jq's `\p{Co}` finds them.
- **A later process cannot find a delivered banner.** `alerter` removes and replaces banners by listing the notifications delivered under the impersonated Terminal identity. Run in a new process with that identity, the same call returns nothing, even while a fresh banner is up, so `--remove` and same-group replacement never take effect. Only the process that posted a banner can remove it, which needs a waiting `alerter`: three of them cost `usernoted` 11.7% of a core plus about 15% in their own processes, measured on macOS 26 with `alerter` 26.5.

## Goals and non-goals

Goals:

- Name where to act on every banner from a tiered session, as `<tmux session>: <window>`.
- Post a banner or sound only when nothing else will reach the person, so a banner never repeats an ask that already has a line in the top coordinator's list or a relay through a lead.
- Let the chime say which tier is calling, and spread one repository's workers across pitches.
- Keep every untiered session's banners exactly as they are today.

Non-goals:

- Push notifications. `notify` posts local macOS banners only, and the separate `push-notification` plugin is untouched.
- Deciding what goes on the top coordinator's list. That stays with the sessions' own instructions.
- Clicking a banner. The README keeps its line that a click does not focus the originating terminal or pane.
- Producing sound files. The separately produced chime set changes on its own (see [What the sound set needs](#what-the-sound-set-needs)).

## Tiers and how a session finds its tier

Three tiers: `top`, `lead` and `worker`. A session that no setting places in a tier is _untiered_ and behaves exactly as today, apart from the visibility fix.

### Signals

Each signal is something any tmux user or harness already has. Only the patterns that match them are specific to one setup.

| Field     | Source                                                                                 | Available                  |
| --------- | -------------------------------------------------------------------------------------- | -------------------------- |
| `window`  | tmux window name of `$TMUX_PANE`                                                       | in tmux                    |
| `session` | tmux session name                                                                      | in tmux                    |
| `server`  | tmux server name, the socket's basename from `$TMUX` (`default` unless `-L` names one) | in tmux                    |
| `name`    | Claude session name, from the newest `agent-name` or `custom-title` record             | named Claude Code sessions |
| `dir`     | `$CLAUDE_PROJECT_DIR`, or the hook's working directory                                 | always                     |

One `tmux display-message` call reads the session and window names. The transcript is read for `name` only when a rule needs it, or when a window name is all glyphs. A workmux handle shows up as the window name or the worktree directory, so it needs no field of its own.

### Rules file

`${XDG_CONFIG_HOME:-$HOME/.config}/agent-harness-notify/tiers` holds one rule per line:

```text
# tier    field    pattern (POSIX extended regular expression)
top       window   ^coordinator$
worker    dir      ^/home/sample/projects/[^/]+/[^/]+/[^/]+
lead      name     ^[[:upper:]][[:upper:][:digit:] /&-]*$
lead      window   ^conductor$
```

- The pattern is the rest of the line, leading and trailing whitespace removed, matched with bash `=~`. Write a significant trailing space as `[ ]`, and use classes such as `[[:upper:]]` rather than ranges such as `[A-Z]`, whose meaning depends on the locale.
- The first matching rule wins. A session that matches none stays untiered.
- Only whole lines are comments. Lines that do not start with a tier name, lines with an unknown field, and patterns bash cannot compile are skipped.
- A field that is empty or unavailable, such as `window` outside tmux or `name` for an unnamed session, matches nothing.

The example places the top coordinator by window name, workers by a fixed worktree layout, standing sessions by an all-capitals session name, and conductors by window name. Matching workers by worktree path keeps a worktree the person works in directly, outside any project, untiered.

### Precedence and defaults

1. `NOTIFY_TIER=top|lead|worker` in the harness's environment wins, so a launcher can set the tier when it starts a session, with or without tmux. Any other value is ignored.
2. Otherwise the rules file decides, as above.
3. With neither, the session is untiered. The plugin ships no rules, so nothing changes until a person writes some.

`notify explain [TRANSCRIPT]` checks a configuration by printing the current pane's tier, the matching rule, the subtitle and the sound each role would play. Run with `!` from a Claude Code prompt, it finds the session's transcript through `$CLAUDE_CODE_SESSION_ID`, so `name` rules apply. It fails, naming what it could not read: the tiers file, a transcript argument, or a transcript for `$CLAUDE_CODE_SESSION_ID` (decision 10). So `name: none` never hides a failed read.

## What fires, per tier and event

| Event                                              | `top`  | `lead` | `worker`                 | Untiered |
| -------------------------------------------------- | ------ | ------ | ------------------------ | -------- |
| Done, turn started by a typed prompt               | posts¹ | posts¹ | silent                   | posts    |
| Done, turn started by a session, task or wake      | silent | silent | silent                   | silent   |
| Permission prompt                                  | posts  | posts  | posts, title `Worker: …` | posts    |
| Plan approval                                      | silent | silent | posts, title `Worker: …` | posts    |
| Question (`AskUserQuestion`, `request_user_input`) | silent | silent | silent                   | posts    |
| Elicitation dialog                                 | posts  | posts  | posts, title `Worker: …` | posts    |

¹ Except a Claude Code turn in which the person answered or rejected one of the session's question or plan prompts. A Codex top or lead session always posts it.

"Posts" means a banner with its role's sound. Done banners stay subject to visibility suppression, which this change makes work inside tmux. Permission, elicitation and plan banners post whatever the focus, as today. The rule behind the table: a banner is for a prompt the harness or an MCP server raises, which the session cannot announce with a line on the list and which can be answered only in its pane.

Why, and how each relates to the top coordinator's list and the relay through leads:

- **Every tier, Done after a message or background task:** silent, as today. Anything a lead raises during such a turn reaches the person through its window and its line on the list, never as a banner. This is the path most asks in the tiered setup take.
- **Lead and top, questions and plan approvals:** silent. The session sends its line to the list before it asks, so the list already carries the ask, and a banner would be a second channel for it.
- **Lead and top, permission prompts and elicitation dialogs:** posts. A permission prompt comes from the harness and an elicitation dialog from an MCP server mid-call, not from the session, so no line on the list announces either, and the session cannot send one while stopped at the prompt.
- **Lead and top, Done after a typed prompt:** the person started this turn in that window, so the banner says their own conversation has a reply; it is not a new ask. A turn in which the person answered one of the session's question or plan prompts posts nothing: the person was just at the window, and the list carried the ask. The Claude Code transcript shows this: the turn holds an `AskUserQuestion` or `ExitPlanMode` call with an answer or Claude Code's rejection text, while a call that failed before reaching the person, such as an input validation error, does not count. Codex writes a failed `request_user_input` call in the same form as an answered one, so the check is Claude Code only, and a Codex lead may post a Done that repeats a question just answered. A reply typed to a question asked in plain text cannot be told apart from a new request, so that turn's Done still posts.
- **Worker, Done:** silent. A worker reports to its lead by message, and the lead relays what the person needs. Its prompt-started turns are mostly briefs or text typed by tooling, so a banner would repeat the report.
- **Worker, permission prompts, elicitation dialogs and plan approvals:** posts. A worker stopped at any of them cannot message its lead. The lead gets no idle notice while the prompt waits, so nothing else announces it. The `Worker:` title says which kind of session is stopped.
- **Worker, questions:** silent. Workers never ask the person anything.
- **Untiered:** exactly today's events.

## Banner text

- **Title:** unchanged, with a `Worker:` prefix and a space for the worker tier.
- **Subtitle:** for a tiered session in tmux, the place `<tmux session>: <window>`. Private-use glyphs are removed from the window name; if nothing is left, the Claude session name stands in, and without a name the subtitle is the tmux session alone. A tiered session outside tmux, and every untiered session, keeps `<repo> · <task>`. The tmux server is left out, so sessions with the same name on two servers share a place.
- **Body, icon, groups and limits:** unchanged.

### Mockups

A sample setup: tmux session `hub` holds the top coordinator (window `coordinator`, session name `HUB`) and a standing monitor in a window named with one icon-font glyph (session name `MONITOR`); tmux session `atlas` is a project with its conductor (window `conductor`) and a worker (window `w 42-fix-parser`); `sample-repo` is an untiered repository session. Sounds use `NOTIFY_SOUND_SET=Chord`, with the built-in sound in parentheses.

```text
┌ Claude Code ───────────────────────────────────────────────────────┐
│ Approve Bash?                                                      │
│ atlas: conductor                                                   │
│ make release                                                       │
└────────────────────────────────────────────────────────────────────┘
  lead, permission prompt: Chord-lead-permission-<n> (Funk)

┌ Claude Code ───────────────────────────────────────────────────────┐
│ Worker: Approve Bash?                                              │
│ atlas: w 42-fix-parser                                             │
│ make test                                                          │
└────────────────────────────────────────────────────────────────────┘
  worker, permission prompt: Chord-worker-permission-<n> (Funk)
```

| Tier and event                        | Title                           | Subtitle                   | Body                                                 | Sound                                |
| ------------------------------------- | ------------------------------- | -------------------------- | ---------------------------------------------------- | ------------------------------------ |
| top, Done after a typed prompt        | `Done`                          | `hub: coordinator`         | `Two decisions wait in atlas: conductor.`            | `Chord-top-stop-<n>` (Glass)         |
| top, permission                       | `Approve Bash?`                 | `hub: coordinator`         | `gh pr view 12`                                      | `Chord-top-permission-<n>` (Funk)    |
| lead, Done after a typed prompt       | `Done`                          | `atlas: conductor`         | `Draft PR 12 is ready: the parser fix passes every…` | `Chord-lead-stop-<n>` (Glass)        |
| lead, Done after answering a question | none                            |                            |                                                      | none                                 |
| lead, Done after a message            | none                            |                            |                                                      | none                                 |
| lead, question or plan approval       | none                            |                            |                                                      | none                                 |
| lead, permission                      | `Approve Bash?`                 | `atlas: conductor`         | `make release`                                       | `Chord-lead-permission-<n>` (Funk)   |
| lead in a glyph-named window          | `Approve WebFetch?`             | `hub: MONITOR`             | `https://status.example.com/`                        | `Chord-lead-permission-<n>` (Funk)   |
| worker, Done                          | none                            |                            |                                                      | none                                 |
| worker, question                      | none                            |                            |                                                      | none                                 |
| worker, permission                    | `Worker: Approve Bash?`         | `atlas: w 42-fix-parser`   | `make test`                                          | `Chord-worker-permission-<n>` (Funk) |
| worker, elicitation                   | `Worker: Question`              | `atlas: w 42-fix-parser`   | `Sign in to the sample server`                       | `Chord-worker-attention-<n>` (Tink)  |
| worker, plan approval                 | `Worker: Plan ready for review` | `atlas: w 42-fix-parser`   | `Split the parser into two passes`                   | `Chord-worker-attention-<n>` (Tink)  |
| untiered                              | `Done`                          | `sample-repo · fix-parser` | `Fixed the flaky test.`                              | `Chord-stop-<n>` (Glass)             |

## Sounds

### Mapping

- **The role still sets the gesture:** `stop` for completion, `permission` for permission prompts, `attention` for questions, elicitation and plan approval.
- **The tier picks a subset:** a tiered session looks for `<prefix>-<tier>-<role>-<n>` files, counted from `0` to the first gap like today's set. Without index `0` it falls back to the plain `<prefix>-<role>-<n>` set, then to the built-in sound, so a session never goes silent for lack of files.
- **The place picks the variant:** with a place, the hash key is the place string instead of the repository name, so a conductor and each of its workers get their own pitch, while each tier's subset sets the timbre. Without a place it stays the repository name.
- **Untiered sessions:** unchanged, down to the selected index.
- **Without a sound set:** every tier keeps Glass, Funk and Tink. Telling tiers apart by ear then rests on which events fire.

### What the sound set needs

The installed chime set has 40 slots per role: four timbres across ten degrees of one pentatonic scale. Tier subsets fit it without new rendering: one timbre per tier, ten degrees each, installed under the tier names next to the plain 40-slot set, which stays for untiered sessions. Which timbre goes to which tier is a listening decision.

The set's two open follow-ups change weight:

- **Equal perceived loudness across the range** comes first. Once timbre carries the tier, a timbre that sounds quieter reads as less urgent by accident. Equalize the set, then decide by listening whether any tier gets a deliberate offset.
- **Nearby variants per slot** matter less. Silent worker completions, silent lead questions and per-place hashing remove most exact repeats, so park this until listening with tiers shows a need. If it comes back, an optional `-v<k>` suffix chosen at random needs no saved state and works with tier subsets.

## Visibility suppression inside tmux

Inside tmux, `originating_pane_visible` reads the terminal from `__CFBundleIdentifier`, and failing that from the tmux server's global `TERM_PROGRAM` (`tmux show-environment -g TERM_PROGRAM`). Outside tmux it keeps `TERM_PROGRAM`. Both values come from where the tmux server started, so a client attached from another terminal is compared with the wrong application, and the banner is posted; every unknown still posts. The README gains the `focus-events on` requirement. This applies to every tmux user, untiered sessions included, because it restores documented behavior.

## Banner groups

Groups stay as they are: one per event kind and session. Removing a session's banner at its next prompt, or having its banners replace one another, was considered and dropped. Under Terminal impersonation a later process cannot find, remove or replace a banner (see [Context](#context)), and keeping each `alerter` waiting so it could remove its own banner costs the load the fire-and-forget change in 4.0.0 removed.

## Configuration summary

| Setting                | Where                                                          | Effect                                                |
| ---------------------- | -------------------------------------------------------------- | ----------------------------------------------------- |
| Tier rules             | `${XDG_CONFIG_HOME:-$HOME/.config}/agent-harness-notify/tiers` | Places sessions in tiers                              |
| `NOTIFY_TIER`          | harness environment                                            | Forces a tier, for launchers or sessions outside tmux |
| `NOTIFY_SOUND_SET`     | harness environment                                            | Unchanged; tier subsets are found by name             |
| `NOTIFY_WAIT_LIMIT`    | harness environment                                            | Unchanged                                             |
| tmux `focus-events on` | tmux configuration                                             | Needed for visibility suppression                     |

## Codex parity

- Tier detection and banner text depend on tmux, the environment and the working directory, so they are the same for Codex. Codex sets no session name, so `name` rules never match a Codex session.
- Codex wires `Stop`, `UserPromptSubmit` and `PreToolUse:request_user_input`. The worker policy silences Codex worker completions, which matters more than for Claude Code, since Codex cannot tell a turn started by another session from a typed one. Tiered Codex questions post nothing, like Claude Code's.
- A Codex top or lead session posts its Done after every typed turn, even one that answered a `request_user_input` call. Codex writes that call's validation errors, an unavailable mode, a subagent caller and a cancelled request as a `function_call_output`, the same form an answer takes, so the answered check is Claude Code only (decision 9).
- Codex has no permission hook. A Codex worker stopped at an approval prompt relies on Codex's own terminal notification, which knows nothing of tiers. This is a known limitation.
- Hook definitions do not change, so trusted Codex hooks stay trusted.

## Outside a tiered setup

- **No rules file and no `NOTIFY_TIER`, or no matching rule:** every title, subtitle, body, sound and event is as today. The existing scrut expectations stay as they are.
- **Plain checkout, single session, no tmux:** unchanged. A `dir` rule or `NOTIFY_TIER` can still give such a session a tier; without a place it keeps `<repo> · <task>` and the repository hash.
- **The one change everyone sees:** visibility suppression starts working inside tmux.

## Risks

- **Misclassification.** A lead taken for a worker loses the Done banners for the person's own prompts; a worker taken for a lead is as noisy as today. `notify explain` and first-match order keep rules easy to check.
- **Prompts typed by tooling** still count as the person's own in lead sessions, so a launcher that resumes a lead with a prompt posts a Done banner.
- **A turn typed in a worker's window and then left** posts nothing.
- **A reply to a plain-text question** posts a Done banner in a lead session, since it looks like a new request.
- **The transcript format** is Claude Code's own; if the session-name records change, `name` rules stop matching and the session falls through to later rules.
- **Regular expressions:** a locale-dependent range or a trailing space stripped by an editor makes a rule miss. The README examples avoid both, and tests run in the C and UTF-8 locales.
- **Shared session names** across tmux servers give two sessions one place and one hash.
- **Chime changes:** tiered sessions' chimes change once, since the hash key changes.
- **Terminal detection inside tmux** follows where the tmux server started and can name the wrong application; that only ever posts a banner.
- **Cost:** for tiered sessions, one tmux call, a small file read, one `jq` call for the window name and, when needed, one `grep` of the transcript. With no tiers file and no `NOTIFY_TIER`, a session only checks that the file is absent. A session that matches no rule has still read the rules, asked tmux for its names and, for a `name` rule, searched its transcript.

## Test plan

- **Unchanged suites:** `tests/scrut/notifications.md` and `tests/scrut/notification-sounds.md` keep their expectations, which pins untiered behavior.
- **New document,** `tests/scrut/notification-tiers.md`, through `tests/fixtures/check-notifications` with its tmux stub extended to return session and window names and the global environment from test variables, and a fixture `XDG_CONFIG_HOME`:
  - Rules: each field, first match wins, comments and blank lines, unknown tier or field, a pattern bash cannot compile, a missing file, no matching rule, `NOTIFY_TIER` precedence and invalid values, and multibyte window names in the C and UTF-8 locales.
  - Events: the policy table for every tier, for Claude Code and Codex, including silent worker completions, `Worker:` titles and silent Done after an answered question or plan.
  - Text: the place subtitle, private-use glyphs replaced by the session name, then by the tmux session, and the old subtitle outside tmux.
  - Sounds: tier subset, fallback to the plain set, fallback to the built-in sound, and the place as hash key, with pinned `cksum` vectors.
  - Visibility: `TERM_PROGRAM=tmux` with `__CFBundleIdentifier`, with only the global tmux environment, and with neither.
  - `notify explain` output.
- **Planted defects** (`plant-defects`), each shown to fail its test: worker completions posted, rule order ignored, glyphs kept, tier subset skipped, the tmux terminal fallback removed, the answered-question check skipped.
- **Parsing and runtime:** `/bin/bash -n` under bash 3.2, and the new document timed alone against the half-of-ten-minutes budget.
- **By hand on macOS:** `notify explain` in each kind of window with a real rules file, and a Done banner suppressed while its pane is watched in tmux.

### Plant table

Each defect was planted alone in `plugins/notify/scripts/notify` on 2026-10-22, the named document was run, and the script was restored. The unmodified tree passed first.

| Planted defect                                    | Instrument expected to catch it | What happened  | Test that covers it now                                    |
| ------------------------------------------------- | ------------------------------- | -------------- | ---------------------------------------------------------- |
| Worker completions post                           | `notification-tiers.md`         | 1 case failed  | Worker posts only permission, plan and elicitation prompts |
| Last matching rule wins (no `break`)              | `notification-tiers.md`         | 1 case failed  | First valid rule wins                                      |
| Private-use glyphs kept in the window name        | `notification-tiers.md`         | 1 case failed  | Icon-font window names give way to the session name        |
| Tier sound subset skipped                         | `notification-tiers.md`         | 1 case failed  | Tier sound subsets and their fallbacks                     |
| tmux terminal fallback removed                    | `notifications.md`              | 2 cases failed | Both visible-pane cases under tmux                         |
| Only the global tmux environment fallback removed | `notifications.md`              | 1 case failed  | Visible pane with the terminal from the tmux server        |
| Answered-prompt check skipped                     | `notification-tiers.md`         | 1 case failed  | Lead completion after an answered question or plan         |
| Codex answered check reads past the turn's start  | `notification-tiers.md`         | 1 case failed  | None: the Codex check was removed (decision 9)             |
| Session-name record type not checked              | `notification-tiers.md`         | 1 case failed  | Rule on the session name, skipping a quoted record         |
| `Worker:` title prefix dropped                    | `notification-tiers.md`         | 1 case failed  | Worker posts only permission, plan and elicitation prompts |
| Lead and top plan approvals post                  | `notification-tiers.md`         | 2 cases failed | Lead and top policy cases                                  |
| Tiered questions post                             | `notification-tiers.md`         | 3 cases failed | Worker, lead and top policy cases                          |
| Unmatched sessions become leads                   | `notification-tiers.md`         | 2 cases failed | Session matching no rule stays untiered; No matching rule  |
| `dir` ignores `$CLAUDE_PROJECT_DIR`               | `notification-tiers.md`         | 1 case failed  | Rule on the working directory, then the project directory  |
| Tiered elicitation silent                         | `notification-tiers.md`         | 3 cases failed | Worker, lead and top policy cases                          |
| Empty field allowed to match                      | `notification-tiers.md`         | 1 case failed  | No matching rule, and no session name to match             |

Two judges were strengthened before planting, since each would have stayed green: the quoted session-name record now carries a top-level `agentName`, and the no-name rule became `^`, which an empty string matches. A half-second settle window in the policy scenarios first missed slow alerts under a full parallel run; the scenarios now wait until no detached notifier process remains, and 24 concurrent runs printed identical results.

## Implementation outline

- `plugins/notify/scripts/notify`: tier detection and rules parsing, the session name, the place, the event policy with the answered-prompt check, the title prefix, tier sound subsets and hash key, the tmux terminal fallback, and `explain`.
- `plugins/notify/README.md`: tiers, rules file, event policy, place subtitle, sound subsets and `focus-events`.
- Tests and fixture as above; register any new paths in the Makefile's `SCRUT_ENV` and CI's `scrut-env`.
- Version 4.2.0 in both manifests, `make build`, `make test-all` and `check-versions`.

## Decisions

Made on 2026-10-22, after review against the top coordinator's rules on asks and reports.

1. **Event policy:** the table above. Every tier keeps turns not started by a typed prompt silent. Workers post only permission, elicitation and plan approval prompts, titled `Worker: …`. Top and leads post only permission and elicitation prompts, plus Done for a typed turn that answered none of their question or plan prompts. Untiered sessions stay byte-identical.
2. **Tier detection:** the rules file and `NOTIFY_TIER`, with no shipped defaults. Workers match by project worktree path, and unmatched sessions stay untiered.
3. **Banner text:** the `<tmux session>: <window>` subtitle, the Claude session name in place of glyph-only window names, and the `Worker:` title prefix.
4. **Sounds:** per-tier subsets with fallbacks, hashed on the place. Built-in sounds stay unchanged.
5. **Clicking:** not pursued.
6. **Visibility inside tmux:** fixed in this change, for untiered sessions too.
7. **Banner groups:** unchanged. Removal and replacement cannot work under Terminal impersonation.
8. **Sound set changes:** outside this change. The tier subsets above work with whatever sounds are installed.
9. **Codex answered check:** dropped. Codex writes failed `request_user_input` calls in the same form as answers, so a Codex top or lead Done always posts after a typed turn, and may repeat a question just answered.
10. **`explain` failures:** `explain` fails on every input it cannot read, including a `$CLAUDE_CODE_SESSION_ID` whose transcript it cannot find or read, while the hooks keep passing over the same inputs.

## Log

- 2026-10-22: Surveyed the plugin, the sound-set history and a tiered setup. Measured the cost of waiting `alerter` processes with silent sample banners. Found visibility suppression inert inside tmux. Wrote the proposal.
- 2026-10-22: Decisions made. Verified that a later process cannot see delivered banners under Terminal impersonation, so banner removal was dropped. Rewrote the plan as the approved design.
- 2026-10-22: Elicitation dialogs post in every tier, like permission prompts, since an MCP server raises them and only the session's pane can answer them.
- 2026-10-22: Review found failed Codex `request_user_input` calls silencing a lead's Done, the Codex instance of a defect fixed for Claude Code. The answered check became Claude Code only (decision 9).
- 2026-10-22: Review found `explain`'s automatic transcript lookup passing over a missing or unreadable transcript, the instance of a gap fixed for a transcript argument. The lookup now fails the same way (decision 10).
