---
name: use-plannotator
description: >-
  Send answerable asks and review files through Plannotator Inbox, then act
  on replies in the same thread. Use for "ask in the Inbox", "send for
  review", or "PR review action card" when Plannotator Inbox is connected.
---

# Use Plannotator

## Workflow

1. **Check the connection and authority.** Use the connected Inbox's message,
   thread-read and reply-wait capabilities. Read their current tool descriptions
   for accepted fields. If unavailable, report the missing connection through
   the session's usual channel; do not install or reconfigure it. Follow the
   project's routing and approval rules, including any separate confirmation
   required for consequential actions. Workers report through their conductor.
1. **Make asks answerable.** Send one ask per message with `send_message`, using
   a question block per decision, never a bare link. Start a thread with a short
   `thread` name and always pass a single-line plain-text `subject` naming the
   whole piece of work, broad enough to still fit after several rounds. For
   example, use "Plannotator fork setup" rather than "Should the fork be public
   or private?" Without an explicit subject, the first question's prompt becomes
   the subject and stops fitting once answered. Continue with `reply_to` naming
   a message in that thread. Give enough context to decide without the session's
   history. Use `:::question` for a single selection, `:::question-multi` for multiple selections,
   or `:::question-text` for free text. Put the question first, then context,
   choices and a recommendation when useful:

   ```markdown
   :::question
   Use the compact layout?

   The attached comparison shows both layouts. The compact version keeps the controls visible.

   - [ ] Use the compact layout
   - [ ] Keep the current layout

   Recommended: Use the compact layout
   :::
   ```

   Use `:::action` for an outside action only the recipient can perform that
   blocks progress, rather than for a decision, status update or checklist.
   Add `Stopped: <reason>` only when the session cannot continue until the
   response, and `Holds up: <work>` only for work actually waiting on it.
   Omit both from ordinary asks and reports.

1. **Attach review files.** Pass each file in `attachments` and link it from
   the message's context using its absolute path or unique attachment name.
   Prefer absolute paths to avoid depending on the connector's working folder.
   Include an image for visual decisions and the source when interaction matters.
   Check the send result for refused files or images that will not show.
1. **Keep the thread recoverable.** Save the returned thread ID, message ID,
   cursor and URL in the session's record. Use an `idempotency_key` for retries
   of the identical send. Before retrying from another project context, find
   the original thread rather than assuming that key still prevents duplicates.
   When a message replaces an open question, send it in the same thread
   with `supersedes` containing the earlier `<message id>/<key>` or message ID.
   Read the thread for current keys and states; supersede only open or picked
   questions. Withdraw stale questions this way even when no replacement is needed.
1. **Wait and interpret the response.** Use the project's existing waiting
   mechanism, or `wait_for_reply` with the thread ID and saved cursor. A
   `waiting` result is not an answer; retain its cursor for the next wait.
   Read the thread with `read_thread` to confirm the actual answer before acting
   on permission or a relayed reply. Act only on answered items; leave remaining
   questions open. Treat a skipped question as declined, an archived thread as
   closed without approval, and an acknowledgement as receipt rather than an
   answer. If a reply says “Set aside for now; don't wait on these”, stop waiting
   on the listed questions: they closed unanswered. Ask again only if still needed.
   Keep waiting when a thread is only marked read for later; that is not an answer.
1. **Act, then reply in the same thread.** Report what the answer led to with
   `reply_to`, including the result or any remaining blocker. Record the decision
   and update the session's existing tracking. Mark an action in `done` only
   after observing its completion. Archive a thread only when nothing remains
   for the recipient to read or answer.

## PR review action cards

Use a PR review action card when the PR needs the recipient's review. Link the
PR and explain what needs reviewing. State that **Done means ready to merge**;
it does not mean the PR has merged. Follow project merge authority and any
additional approval gates before merging. If merging belongs to another session
or the recipient, report readiness there and stop at that boundary.

```markdown
:::action
Review the PR for the compact layout
Check the attached comparison and the PR's behavior. Mark Done when it is ready to merge.

Where: https://github.com/example/project/pull/123
:::
```

After acting on Done, reply in that thread with the merge result or the remaining
gate. If the recipient marks Can't do it, read the reason and report the next
step without assuming approval.
