# Resolve Copilot PR Feedback

Process and resolve GitHub Copilot automated PR review comments.

**Type:** Skill
**Trigger:** `/resolve-copilot-pr-feedback`

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Fetches unresolved Copilot review threads via GraphQL, categorizes them (nitpick, outdated, incorrect, valid, deferred), resolves threads, and updates Copilot instruction files under `.github/` when Copilot feedback is incorrect. Also fetches Copilot's **review bodies**, where Copilot files findings under a "suppressed comments" section instead of opening a thread, typically on lines the latest push did not touch. Those findings have no thread to reply to or resolve, so a thread-only query cannot see them; the skill parses them out of the review body, handles them like any other feedback, and records each one in the summary comment. It never reports "no unresolved Copilot feedback" without having checked both places. Because Copilot re-emits the same suppressed finding in every later review, the skill reads back its own prior summary comments and verifies each finding against the current code before acting, so already-handled findings are noted rather than re-fixed. After reaching a terminal workflow state, posts a required final summary comment to the PR for every outcome, including no unresolved feedback, non-code-change resolutions, code-change resolutions, partial processing, and failures when PR context and GitHub authentication are available. If the summary cannot be posted, the workflow reports that incomplete state and preserves the intended summary for retry instead of claiming success. No-op runs reuse an existing same-head no-op summary instead of adding duplicate comments. Helps you quickly triage automated suggestions after opening a PR.

## Usage

```text
/resolve-copilot-pr-feedback
```

## Recommended Permissions

This skill runs custom scripts and git commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(bash \"*/resolve-copilot-threads\" *)", "Bash(git push*)", "Bash(gh api --paginate repos/*/issues/*/comments*)", "Bash(mktemp -u /tmp/copilot-reply-*)", "Bash(rm -f /tmp/copilot-reply-*)", "Bash(gh pr comment *)", "Bash(mktemp -u /tmp/copilot-summary-*)", "Bash(rm -f /tmp/copilot-summary-*)"]
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
