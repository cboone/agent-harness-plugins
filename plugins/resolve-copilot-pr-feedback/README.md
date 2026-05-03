# Resolve Copilot PR Feedback

Process and resolve GitHub Copilot automated PR review comments.

**Type:** Skill
**Trigger:** `/resolve-copilot-pr-feedback`

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Fetches unresolved Copilot review threads via GraphQL, categorizes them (nitpick, outdated, incorrect, valid, deferred), resolves threads, and updates Copilot instruction files under `.github/` when Copilot feedback is incorrect. After reaching a terminal workflow state, posts a required final summary comment to the PR for every outcome, including no unresolved feedback, non-code-change resolutions, code-change resolutions, partial processing, and failures when PR context and GitHub authentication are available. If the summary cannot be posted, the workflow reports that incomplete state and preserves the intended summary for retry instead of claiming success. Empty-fetch no-op runs reuse an existing same-head no-op summary instead of adding duplicate comments. Helps you quickly triage automated suggestions after opening a PR.

## Usage

```text
/resolve-copilot-pr-feedback
```

## Recommended Permissions

This skill runs custom scripts and git commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(bash */resolve-copilot-threads *)", "Bash(git push*)", "Bash(mktemp /tmp/copilot-reply-*)", "Bash(rm -f /tmp/copilot-reply-*)", "Bash(gh pr comment *)", "Bash(mktemp /tmp/copilot-summary-*)", "Bash(rm -f /tmp/copilot-summary-*)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "resolve copilot feedback": fetches and processes Copilot review comments
- "check copilot review": same behavior
- "handle copilot comments": same behavior

## See Also

- [Address Review](../address-review/README.md): work through a human-written review document
- [PR](../pr/README.md): create the PR that Copilot will review
- [All plugins](../../README.md)
