# Push Notification

Send push notifications through ntfy when work finishes or needs a decision, on request or from another skill, including from remote and cloud sessions.

**Type:** Skill
**Trigger:** `/push-notification [message]`
**Requires:** [`curl`](https://curl.se/), [`jq`](https://jqlang.org/), and an [ntfy](https://ntfy.sh) topic (ntfy.sh or self-hosted)

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Asks like "notify me when this finishes", "ping my phone when CI passes" or "send me the PR link when it's ready" become one push notification, sent once the outcome is known. Other skills can send one too, at completion or at a point that needs your decision, without each reimplementing the transport. Because it publishes over HTTP, it works from remote and cloud sessions, where the [`notify`](../notify/README.md) hook's macOS banners never arrive.

The skill writes the notification for a lock screen: the outcome first, a short body, a click URL to the pull request, run or session, and a priority chosen by urgency (`default` for a completion, `high` when a session is waiting on you). It keeps secrets, client names and private repository details out of the message and its click URL unless you have said your server is private, because anyone who knows a topic name on ntfy.sh can read it.

A bundled `push-notification` script does the sending. It posts an ntfy JSON publish request with `curl`, without the `ntfy` CLI. The access token goes to `curl` in a header file only you can read, never on a command line, and neither the token nor the topic is ever printed. The backend sits behind a small interface documented at the top of the script, so Pushover, Slack incoming webhooks and similar can be added later; ntfy is the only one that ships.

## Configuration

Settings live in `${XDG_CONFIG_HOME:-$HOME/.config}/push-notification/config` (or the file `PUSH_NOTIFICATION_CONFIG` names), as `KEY=value` lines the script parses but never runs. A non-empty environment variable of the same name overrides each one, which suits cloud sessions; an empty one is ignored and does not clear a configured value. A `PUSH_NOTIFICATION_CONFIG` that names a missing file is an error rather than a silent fall back to the defaults.

| Key                         | Meaning                             | Default           |
| --------------------------- | ----------------------------------- | ----------------- |
| `NTFY_SERVER`               | ntfy server URL                     | `https://ntfy.sh` |
| `NTFY_TOPIC`                | Topic to publish to                 | none; required    |
| `NTFY_TOKEN`                | Access token for a protected server | none              |
| `PUSH_NOTIFICATION_BACKEND` | Backend to use; only `ntfy` ships   | `ntfy`            |

A file that holds `NTFY_TOPIC` or `NTFY_TOKEN` must be mode `600`, or the script refuses to use it, because on ntfy.sh the topic name is all that guards a topic. With no topic configured, the skill reports what is missing and how to set it up rather than sending to a guessed topic. Choose a long random topic name on ntfy.sh, since the name is all that protects it.

## Usage

```text
/push-notification
/push-notification "Deploy finished"
/push-notification --title "Review needs a decision" --priority high
/push-notification --dry-run
```

| Option               | Description                                                    |
| -------------------- | -------------------------------------------------------------- |
| `[message]`          | What to say; composed from the work just done when absent      |
| `--title <text>`     | Title to use instead of a composed one                         |
| `--priority <level>` | `min`, `low`, `default`, `high` or `urgent`                    |
| `--tag <tag>`        | Tag or emoji shortcode, such as `white_check_mark`; repeatable |
| `--click <url>`      | URL to open when the notification is tapped                    |
| `--dry-run`          | Show the request, without the topic or token, and send nothing |

## Recommended Permissions

This skill runs its bundled script, which prompts for permission. To allow it automatically, add this rule to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(bash \"*/push-notification\" *)"]
  }
}
```

If you already have a `permissions.allow` array, merge this entry into it. The rule lets the agent send notifications without asking each time; leave it out if you want to approve every send.

## Examples

- "notify me when the tests finish": runs the tests, then sends one notification with the result
- "ping my phone if the build needs me": sends a `high` priority notification when the session is blocked on a decision
- "send me the PR link": sends the PR title with the PR as the click URL
