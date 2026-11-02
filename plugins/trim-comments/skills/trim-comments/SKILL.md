---
name: trim-comments
description: >-
  Trim and rewrite code comments in changed files or given paths: what the code
  does, then the minimum why. Use for "trim comments" or a comment that is too
  long or jargony; not for PR review comments or general code cleanup.
argument-hint: "[paths...] [--dry-run] [--no-commit] [--no-codex]"
---

# Trim Comments

Compatibility alias for comment trimming through `trim-text`'s `code-comments` profile. Keep this name, its triggers and its existing options working while the common standard and workflow live in `trim-text`.

## Handoff

Confirm that the `trim-text` skill is available. If unavailable, report `unavailable`, name the missing dependency, and leave files unchanged. Never recreate a second copy of its standard or workflow.

Invoke the `trim-text` skill with `--profile code-comments` and the original paths, named comment and options (`--dry-run`, `--no-commit`, `--no-codex`). With no paths or named comment, pass `branch` explicitly: the equivalent is `trim-text branch --profile code-comments`, using the verified remote default branch as the base. Do not choose a PR body or use its target branch as the base for this alias. With explicit paths, every comment in those files is in scope; a named comment is the whole scope. Pass paths as data without interpreting words such as `branch`, `pr` or `issue` as scope selectors: prefix a literal path with `./` when it conflicts with a selector.

The target resolves scope, classifies comments, edits, verifies, commits when allowed, and reports. It skips prose documents and symlinks, keeps code and protected comments unchanged, flags ticketless TODOs, and never pushes. Report-only proposals keep the target's read-only Codex sandbox and completion checks. Return its checked report directly; do not run another trim pass.

## Skill dependencies

- **Required:** `trim-text`
- **Optional:** None
