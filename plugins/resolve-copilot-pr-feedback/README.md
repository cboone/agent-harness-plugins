# Resolve Copilot PR Feedback

Process and resolve GitHub Copilot automated PR review comments.

**Type:** Skill
**Trigger:** `/resolve-copilot-pr-feedback`

## What It Does

Fetches unresolved Copilot review threads via GraphQL, categorizes them (nitpick, outdated, incorrect, valid, deferred), resolves threads, and updates Copilot instruction files under `.github/` when Copilot feedback is incorrect. Helps you quickly triage automated suggestions after opening a PR.

## Usage

```text
/resolve-copilot-pr-feedback
```

## Examples

- "resolve copilot feedback" — fetches and processes Copilot review comments
- "check copilot review" — same behavior
- "handle copilot comments" — same behavior

## See Also

- [Address Review](../address-review/README.md) — work through a human-written review document
- [PR](../pr/README.md) — create the PR that Copilot will review
- [All plugins](../../README.md)
