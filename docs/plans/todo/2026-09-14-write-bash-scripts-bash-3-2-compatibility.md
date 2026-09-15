# write-bash-scripts: bash 3.2 compatibility (#390)

## Context

The `write-bash-scripts` guide prescribes `set -euo pipefail`, braces on every expansion, `main "${@}"`, and quoted `"${array[@]}"`. Under `set -u`, bash 3.2 (macOS `/bin/bash`, and what `#!/usr/bin/env bash` resolves to on a stock Mac) treats an empty `"${@}"`, `"${*}"`, or `"${array[@]}"` as unbound and aborts. It exempts only the unbraced `"$@"` and `"$*"`. Bash 5.x expands all of them to nothing, so scripts written to the guide pass on Linux and Homebrew bash and fail on a stock Mac (cboone/gh-actions#87: 31 of 31 cases failed at `main "${@}"`). The guide also recommends `readarray`, which bash 3.2 lacks.

Outcome: every example in the guide runs under strict mode on bash 3.2 and 5.3, and the guide says what to avoid when a script must run on macOS.

### Verified on this machine (bash 3.2.57 and 5.3.15, ShellCheck 0.11.0)

- Fails on 3.2 with no arguments or an empty array: `f "${@}"`, `"${*}"`, `local rest=("${@}")`, `"${a[@]}"` (including `local -a a=()`).
- Works on 3.2: `f "$@"`, `"$*"`, `${#}`, `${a[@]+"${a[@]}"}` (preserves spaces and empty elements), `((${#a[@]} > 0))`, `"${!a[@]}"`, a `while IFS= read -r` loop appending to an array.
- Trap: `f "${@:-}"` passes one empty argument instead of none.
- Missing on 3.2: `readarray`/`mapfile`, `declare -A`, `${v,,}`/`${v^^}`, `declare -n`, `[[ -v v ]]`, `${a[-1]}`, `|&`, `&>>`, `shopt -s globstar`. Replacements verified: `tr '[:upper:]' '[:lower:]'`, `printf -v` plus `${!name}`, `[[ -n "${v+set}" ]]`, `${a[${#a[@]}-1]}`, `2>&1 |`, `>> file 2>&1`.
- ShellCheck with this repo's `.shellcheckrc` (`require-variable-braces` enabled and confirmed firing on `$x`) accepts `"$@"`, `"$*"`, and `${items[@]+"${items[@]}"}` with no findings.
- Not affected: the `main "${@}"` in `write-lean-code` and `scaffold-lean-library` references is zsh, and zsh with `nounset` expands empty `"${@}"` and arrays fine.
- All-version strict-mode bugs in the same guide: `[[ "${TRACE}" ]] && set -x` aborts under `set -u` on 3.2 and 5.3; `((i++))` from 0 exits under `set -e` on 5.3 (3.2 continues). `((i += 1))` and `[[ -n "${TRACE:-}" ]]` work on both.
- From bash's own CHANGES file (tiswww.case.edu/php/chet/bash/CHANGES): the empty-array `set -u` fix is in the bash-4.4-rc2 section, so bash 4.0 through 4.3 fail on empty `"${array[@]}"` too; `((` and `[[` became subject to `set -e` in bash-4.1-alpha. No primary source covers braced `"${@}"` on 4.0 through 4.3, so the guide states only the verified 3.2 and 5.x behavior for it.
- Found during execution: the Subprocess variable scope example at HEAD also fails on 3.2, because the `while` loop returns its last body command's status (`((count++))` from 0) and `pipefail` propagates it.

### Scope decisions

- The repo's own scripts that use `"${@}"` with empty lists are out of scope; file a follow-up issue.
- Fix the `TRACE` and `((i++))` examples here, in their own commit.

## Changes

### Commit 1: `fix: keep write-bash-scripts guidance working on bash 3.2 (#390)`

`plugins/write-bash-scripts/skills/write-bash-scripts/references/BASH.md`:

1. **Main function** and **Dual-purpose scripts**: `main "${@}"` becomes `main "$@"`.
1. **Variable expansion**: add the carve-out. `"$@"` and `"$*"` stay unbraced because bash 3.2 exempts only those spellings from `set -u` when there are no arguments. Individual parameters keep braces (`${1}`, or `${1:-}` when optional). Add a `"$@"` / `"${@}"` row to the table, and warn that `"${@:-}"` passes one empty argument.
1. **Variadic functions**: `local rest=("${@}")` becomes `local -a rest=("$@")`.
1. **Functions over aliases**: `ls -la "${@}"` becomes `ls -la "$@"`.
1. **Array expansion**: keep the table; add that an array which can be empty needs `${array[@]+"${array[@]}"}` or a `((${#array[@]} > 0))` check under `set -u` on bash 3.2, with a short example of each.
1. **Process substitution**: drop `readarray` from the lead sentence; show collecting lines into an array with a `while IFS= read -r` loop (every version), then `readarray -t` labelled bash 4 and later.
1. **New `### Bash 3.2 (macOS)` at the end of Basics** (H3, so the H2 nav line is unchanged): why it matters, a Use-instead table for the verified items above, linking back to Variable expansion, Array expansion, and Process substitution; `|&` and `&>>` go in a sentence after the table to keep pipes out of table cells. Close with the `((BASH_VERSINFO[0] < 4))` guard for scripts that require bash 4, matching `plugins/pin-everything/skills/pin-everything/references/scripts/version-audit-template`.

`plugins/write-bash-scripts/skills/write-bash-scripts/SKILL.md`:

1. Script Structure: `main "$@"`.
1. Syntax: `${var}` not `$var`, except `"$@"` and `"$*"`.
1. Quoting: guard arrays that can be empty with `${array[@]+"${array[@]}"}`.
1. Add a short `### Bash 3.2 (macOS)` bullet list pointing at the reference section.

Versioning and mirrors:

1. Bump `write-bash-scripts` 2.0.3 to 2.0.4 (patch, bug fix) in `plugins/write-bash-scripts/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
1. Recompute `metadata.version` with `bin/compute-catalog-state` (expected `catalog-M70-m103-p157-n57`).
1. Regenerate mirrors with `bin/build-codex-marketplace` and `bin/build-opencode-mirror`.

### Commit 2: `fix: make write-bash-scripts examples survive strict mode`

Body notes it was found while addressing #390. In `BASH.md`:

1. **Debug tracing**: `[[ "${TRACE}" ]] && set -x` becomes `[[ -n "${TRACE:-}" ]] && set -x` (also satisfies the guide's own Explicit tests rule).
1. **Arithmetic** table: `((i++))` becomes `((i += 1))` in the Use column, with a sentence that a post-increment from 0 evaluates to 0 and exits under `set -e`. `for ((i=1; i<=10; i++))` stays, since the loop header's status is not checked.
1. **Subprocess variable scope** example: `((count++))` becomes `((count += 1))`.
1. Regenerate mirrors. No further version bump (2.0.4 is unreleased on this branch).

### Commit 3: plan file

Commit this plan under `docs/plans/todo/` (cboone repo convention keeps plans).

### Follow-up issue

File with the `create-issue` skill: repo scripts not safe on bash 3.2 under `set -u`. List `bin/build-codex-marketplace:269`, `bin/check-cross-references:268`, `plugins/publish-report-board/scripts/report-board:857-865`, `plugins/notify/scripts/notify:520`, `plugins/notify/scripts/focus-pane:54`, `plugins/{create-worktree,address-issue-in-worktree}/scripts/launch-workmux:92,276,304` (byte-identical copies), and `tests/fixtures/{tmux-stub,gh-stub,cross-reference-fixture}`. Note which are reachable with empty lists in normal use, and propose running the scrut suites under `/bin/bash` 3.2 to catch empty-array expansions the grep cannot see. Link #390.

## Verification

1. Extract every changed Bash snippet into scratchpad scripts and run each with `set -euo pipefail` and no arguments under both `/bin/bash` (3.2) and Homebrew `bash` (5.3); all exit 0. Run the same with the pre-change snippets to confirm the 3.2 failures reproduce.
1. `shellcheck --rcfile=.shellcheckrc -s bash` on those scripts: no findings.
1. `bin/check-cross-references` on the two changed skill files.
1. `make test-all` (markdownlint, Prettier, shellcheck, shfmt, actionlint, `validate-json`, `validate-plugins` including mirror freshness and catalog state, scrut).
1. `check-versions` skill before opening a PR.
