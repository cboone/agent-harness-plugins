# Notify repository sound set

Issue: [#595](https://github.com/cboone/agent-harness-plugins/issues/595)

Status: Approved for implementation.

## Scope

Add an opt-in sound set for Claude Code and Codex CLI through the shared notify script. Sound production and rotation are excluded. The prerequisite #594 is merged; notify starts at 4.0.0.

## Implementation

1. Add a Bash 3.2-compatible resolver in `plugins/notify/scripts/notify`. Accept `NOTIFY_SOUND_SET` only when it matches `^[A-Za-z0-9._-]+$`. Unset, empty and invalid settings preserve built-in sounds.
1. Map Glass to `stop`, Funk to `permission`, and Tink to `attention` at every event call site. Leave detached delivery unchanged.
1. Count contiguous indices starting at zero in `~/Library/Sounds`, accepting `.aiff`, `.wav` and `.caf`. Stop at the first missing index and count an index once even when several extensions exist. A missing role uses its built-in sound.
1. Hash the bytes of `repo_name()` with POSIX `cksum`, without a trailing newline. Pin test vectors. Use the same hash modulo each role's count; matching counts produce matching indices. Worktrees share their repository identity; outside Git, the subtitle's folder-name fallback applies.
1. Pass the selected extensionless sound name to `alerter`. Update every stop, permission, question, elicitation and plan-approval call site.
1. Extend `tests/fixtures/check-notifications` and scrut coverage with isolated sound directories for defaults, known repository names, supported extensions, duplicate extensions, gaps, missing roles, invalid prefixes, differing counts, non-repository fallback and worktree identity.
1. Document configuration, file naming, macOS lookup order and Terminal notification sound permission in the notify README. Bump both notify manifests to 4.1.0 and regenerate mirrors with `make build`.

## Validation and delivery

Run relevant formatting, linting, validation and `make test-scrut`, observing final results. Confirm parsing under macOS `/bin/bash` 3.2. Commit the plan first, then commit implementation and generated artifacts in signed commits referencing #595. Keep the issue in progress; pushing and opening a PR are separate follow-up actions.
