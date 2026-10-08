# Resolve Copilot PR Feedback

Process and resolve GitHub Copilot automated PR review comments.

**Type:** Skill
**Trigger:** `/resolve-copilot-pr-feedback`
**Requires:** [`gh`](https://cli.github.com/) (authenticated)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Fetches unresolved Copilot review threads via GraphQL, categorizes them (nitpick, outdated, incorrect, valid, deferred, advisory, or no concern for review text that states nothing to act on), resolves threads, and updates Copilot instruction files under `.github/` when Copilot feedback is incorrect. Also fetches Copilot's **review bodies**, where Copilot states findings without opening a thread: in its lead paragraph, in lists of open or previously missed findings, in file-summary tables, and wherever it puts them next. Those findings have no thread to reply to or resolve, so a thread-only query cannot see them.

The skill reads each review body as text rather than parsing its layout. Copilot reshapes that layout often, and the text always says what it found, so the bundled script returns each body raw and complete, with the review comment ids it links to, and the skill lists every concern the review states. Each concern is settled as a restatement of a thread or an earlier disposition, a new finding, an advisory request for human review, which the summary quotes at the top, or nothing of concern. A new layout therefore costs nothing: there is no parser to fall behind. Copilot's error and excluded-files notices are recognized by reading them, never read as clean reviews, and named in the summary so `monitor-pr` can request a fresh review.

An audit of every Copilot review, review comment and pull request comment reports feedback the fetches cannot reach. It never reports "no unresolved Copilot feedback" without having run all three checks. Because Copilot re-emits the same body finding in every later review, the skill reads back its own prior summary comments, reads only the reviews submitted since the newest one plus the newest review of the current head, and verifies each finding against the current code before acting, so already-handled findings are noted rather than re-fixed. Each disposition links its exact source review in the single final summary comment; fixed dispositions name their commit, while no-change dispositions state their evidence or rationale.

After reaching a terminal workflow state, posts a required final summary comment to the PR for every outcome, including no unresolved feedback, non-code-change resolutions, code-change resolutions, partial processing, and failures when PR context and GitHub authentication are available. If the summary cannot be posted, the workflow reports that incomplete state and preserves the intended summary for retry instead of claiming success. No-op runs reuse an existing same-head no-op summary instead of adding duplicate comments. Helps you quickly triage automated suggestions after opening a PR.

## Usage

```text
/resolve-copilot-pr-feedback
```

## Recommended Permissions

This skill runs custom scripts and git commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(bash \"*/resolve-copilot-threads\" *)", "Bash(git push*)", "Bash(gh api --paginate repos/*/issues/*/comments*)", "Bash(mktemp -u \"${TMPDIR:-/tmp}/copilot-reply-*\")", "Bash(rm -f *copilot-reply-*)", "Bash(gh pr comment *)", "Bash(mktemp -u \"${TMPDIR:-/tmp}/copilot-summary-*\")", "Bash(rm -f *copilot-summary-*)"]
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
