# Coordinate per-repository notify chime sounds

## Context

Notify alerts use the same macOS sounds in every repository (Glass, Funk, Tink), so with many concurrent sessions one sound repeats over and over. Each repository should get its own variant of each event's sound. The goal is variety, not recognizing a repository by ear, and the sounds must work well together when they overlap.

This plan is the integration record for work that spans this repository and a private sound-generation project. It tracks the issues, worktrees, sequencing and end-to-end verification. Implementation plans live with each issue.

## Design

- One key and one pentatonic scale for every sound, so any overlap is consonant. Two octaves give about 10 slots.
- A deterministic hash of the main repository name picks the slot. Worktrees share their repository's slot. Collisions are acceptable, so no state is saved.
- The event sets the gesture and the slot sets the pitch: a single soft bell for `stop`, short rising two-note figures for `permission` and `attention`.
- Each built-in sound maps to one role: Glass to `stop`, Funk to `permission`, Tink to `attention`.
- Contract between the two sides: files named `<prefix>-<role>-<n>.aiff` in `~/Library/Sounds`, `<n>` from `0` without gaps, the same count for every role. notify counts from `0` to the first gap and falls back to the built-in sound for a role with no files.
- Opt-in through `NOTIFY_SOUND_SET=<prefix>`; unset keeps today's sounds. The generated set uses the prefix `notify-chime`.
- Several timbres share the hash: the slot index covers every timbre and scale degree combination (four timbres by ten degrees), so a repository's roles share both timbre and pitch, and the naming contract does not change. Chosen on 2026-10-11.
- Installation: the generation project renders, converts to 16-bit AIFF and installs the files. Dotfiles only set `NOTIFY_SOUND_SET`. Chosen on 2026-10-11.

## Work items

| Item                                | Where                  | Status                                        |
| ----------------------------------- | ---------------------- | --------------------------------------------- |
| Sound-set selection in notify, #595 | this repository        | implemented locally; no PR yet                |
| Catalog entry for the chime set     | private catalog        | merged                                        |
| Chime generation and install        | private generation lab | installed; PR open                            |
| Set `NOTIFY_SOUND_SET`              | dotfiles               | committed; takes effect once #595 is released |

## Sequencing

1. #606 removed OpenCode support and released notify 3.0.0, so #595 covers the `notify` script only. #594 (fire-and-forget alerts) rewrites the same script and takes the next major version. #595 starts from `main` after #594 merges, or from the #594 branch with a rebase once it lands.
2. The catalog entry comes first on the generation side, because the experiment takes its ID.
3. The generation work stops for a listening comparison (a grid of a few keys, timbres and decay lengths, plus an overlap render) before it commits to a timbre. Chris chooses.
4. #595 does not depend on the real sounds: its tests use stub files. The two sides meet at the naming contract.
5. End-to-end verification follows once both sides land and the dotfiles set the prefix.

## Verification

- [x] A custom sound in `~/Library/Sounds` plays through `alerter --sound` (2026-10-11).
- [ ] With `NOTIFY_SOUND_SET` unset, alerts keep Glass, Funk and Tink.
- [ ] Real alerts from two repositories with different slots play their own variants, from both Claude Code and Codex CLI.
- [ ] Two worktrees of one repository play the same variant.
- [ ] Several overlapping alerts sound consonant and do not clip, including alerts with different timbres.

## Log

- 2026-10-11: Filed #595 and the two private generation issues. Custom sound playback verified.
- 2026-10-11: Started planning sessions for the catalog entry and the generation work. #595 waits for #594 to merge; the #594 session reports when its PR opens and merges.
- 2026-10-11: Catalog entry merged. Generation experiment and installer built; listening grids rendered for a timbre, decay and key choice. A duplicate catalog PR from the generation session is open.
- 2026-10-11: First listening round chose three timbres, each with its own decay, and asked for a fourth with a sonar-ping quality, all four in the hash. Duplicate catalog PR closed.
- 2026-10-11: #606 removed OpenCode support (notify 3.0.0). #595 narrowed to the `notify` script; #594 needs a new major version.
- 2026-10-11: #594 rebased on #606 and moved to notify 4.0.0, with a new `fire-alerter` launch helper; #595 selects sounds in `notify` before that helper and is a minor bump on 4.0.0.
- 2026-10-12: #594 merged (#607), unblocking #595. Second listening round chose F# minor pentatonic one octave lower (F#4 to E6, ten degrees), all four timbres with the bar kept, and a sonar ping with a faint short echo.
- 2026-10-12: Chime set installed: 120 files (40 per role), 16-bit mono AIFF, 1.65 s; the level was raised toward Tink's. #595 implemented on its branch.
- 2026-10-12: Range confirmed one octave lower again, F#3 to E5, after a side-by-side comparison with F#4 to E6; the installed set already uses it. Level set just below Tink. Generation PR open.
