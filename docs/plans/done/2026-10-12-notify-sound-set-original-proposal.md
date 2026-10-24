# Plan for Issue #595: Notify opt-in per-repository sound set

Status: Historical proposal, superseded by the [approved implementation plan](2026-10-12-notify-repository-sound-set.md). The original proposed details below are retained for reference; the linked plan records the implementation and validation results.

**Classification:** feature (`feat`). #594 is merged, so no sequencing block.

## Context

Every notify alert plays Glass, Funk or Tink in every repository, so concurrent sessions repeat the same sound. `NOTIFY_SOUND_SET=<prefix>` opts into a user-installed set of variants in `~/Library/Sounds`, picked per repository by a stable hash.

## Changes

1. Rename this plan to `docs/plans/todo/2026-10-12-notify-sound-set.md` and commit it.
1. `plugins/notify/scripts/notify`:
   - Add `resolve_sound <role> <builtin>`: if `NOTIFY_SOUND_SET` matches `^[A-Za-z0-9._-]+$`, count `${HOME}/Library/Sounds/<prefix>-<role>-<n>.{aiff,wav,caf}` from `n=0` to the first gap; with a count, print `<prefix>-<role>-<hash mod count>`, otherwise the built-in name.
   - Hash: `printf '%s' "$(repo_name)" | cksum | cut -d ' ' -f 1` (POSIX CRC-32, identical on macOS and Linux, no new dependency, bash 3.2 safe). Compute once per run, only when the set is enabled and a role has files.
   - Replace literal `"Tink"`, `"Funk"`, `"Glass"` at the five call sites with `"$(resolve_sound attention Tink)"`, `permission Funk`, `stop Glass`. Same index for all roles of a repository falls out of using one hash.
   - Update the header comment briefly.
1. `tests/fixtures/check-notifications`: export `HOME="${test_dir}/home"` and unset `NOTIFY_SOUND_SET` by default; add scenarios that create stub files and print the `--sound` value:
   - `sound-set`: 3 variants per role for `sample-repo`, expected index pinned from `cksum` (test vector);
   - `sound-set-gap`: files 0, 1 and 3, so count is 2;
   - `sound-set-missing-role`: only `stop` files; a permission or question alert falls back to Funk or Tink;
   - `sound-set-invalid`: prefix `../x` keeps Glass;
   - `sound-set-worktree`: worktree reports the same variant as the primary checkout;
   - mixed extensions (`.wav`, `.caf`) counted.
   - Plus a direct test-vector case: `cksum` of a couple of fixed names, so a hash change is caught.
1. `tests/scrut/notifications.md`: one section per scenario above; existing cases already cover "unset keeps Glass, Funk and Tink".
1. `plugins/notify/README.md`: "Shared event sounds" bullet mentions the option; new "Per-repository sound set" section with the setting, role table, file naming, gap rule, fallback, hash note, lookup order (`~/Library/Sounds`, `/Library/Sounds`, `/System/Library/Sounds`) and the System Settings > Notifications > Terminal sound permission. Use `write-markdown` and `write-bash-scripts` skills.
1. Bump `plugins/notify/.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` to 4.1.0; `make build` for `dist/`.

## Commits

- `docs: add plan for notify sound set (#595)`
- `feat: pick a per-repository notify sound from an opt-in set (#595)` (script, tests, README)
- `chore: bump notify to 4.1.0 (#595)` plus regenerated mirror

## Verification

`make lint`, `make validate`, `make test-scrut SCRUT_TEST_DIR=tests/scrut/notifications.md`, then `make test-all`; `/bin/bash -n` parse case covers bash 3.2. Run the check-versions skill.
