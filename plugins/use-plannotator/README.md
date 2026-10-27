# Use Plannotator

Send answerable asks, review attachments, and follow-ups through Plannotator Inbox.

**Type:** Skill
**Trigger:** `/use-plannotator` (also activates automatically)

## Installation

Follow the [installation guide](../../README.md#install) and select **Use Plannotator**.
For Codex, see [Using with Codex CLI](../../README.md#using-with-codex-cli) and
[known limitations](../../README.md#codex-cli-known-limitations).

## Requirements

- A connected Plannotator Inbox providing message sending, thread reading and reply waiting.
- The project's existing approval and message-routing rules.

## Usage

Use `/use-plannotator` in Claude Code or `$use-plannotator` in Codex when sending
an Inbox ask or review. The skill keeps decisions answerable, attaches review
files and follows up in the original thread after acting on an answer.

PR review action cards explicitly make Done mean ready to merge. Project merge
authority and additional confirmation requirements still apply.

## Examples

- "Ask in the Inbox which layout to use, with the comparison attached."
- "Send this PR for review with an action card."
- "Reply in the review thread with the result of the approved change."

## See Also

- [PR](../pr/README.md): prepare and open a pull request.
- [All plugins](../../README.md)
