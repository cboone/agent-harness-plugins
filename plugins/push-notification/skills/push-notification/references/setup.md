# Setup

Give these steps to the user when `check` reports that the backend is not configured. The user does them; never create the config file with a topic or token you chose, and never ask for the token to be pasted into the conversation.

## 1. Choose a topic

On ntfy.sh, a topic is public to anyone who knows its name, so the name works like a password. Pick a long, random one, for example from:

```bash
printf 'agent-%s\n' "$(openssl rand -hex 12)"
```

A self-hosted ntfy server with access control can use any name, protected by an access token instead.

## 2. Subscribe on the phone

Install the ntfy app (Android or iOS), add a subscription to that topic, and for a self-hosted server, add the server URL in the app first.

On iOS with a self-hosted server, instant background delivery needs the server to forward polls upstream, normally `upstream-base-url: "https://ntfy.sh"` in its configuration; see [iOS instant notifications](https://docs.ntfy.sh/config/#ios-instant-notifications). Without it, notifications can arrive late. A successful send confirms that the server published the message, not that the phone showed it.

## 3. Write the config file

The helper reads `${XDG_CONFIG_HOME:-$HOME/.config}/push-notification/config`, or the file named by `PUSH_NOTIFICATION_CONFIG`. It holds `KEY=value` lines; blank lines and lines starting with `#` are ignored, and the file is parsed, never run as shell.

```text
# Server URL; defaults to https://ntfy.sh
NTFY_SERVER=https://ntfy.example.com
# Topic to publish to; required
NTFY_TOPIC=agent-3f9c2a7e5b1d48c6a0e2f7b4
# Access token, for a server with access control; optional
NTFY_TOKEN=tk_...
```

Make the file readable by its owner alone. The helper refuses to use a file that holds `NTFY_TOPIC` or `NTFY_TOKEN` and is readable by anyone else, since on ntfy.sh the topic name works like a password:

```bash
chmod 600 "${XDG_CONFIG_HOME:-$HOME/.config}/push-notification/config"
```

## 4. Or use environment variables

Every key is also an environment variable of the same name, and a non-empty one overrides the file. That suits remote and cloud sessions, where the variables can come from the environment's secret settings rather than a file: `NTFY_SERVER`, `NTFY_TOPIC`, `NTFY_TOKEN`, and `PUSH_NOTIFICATION_BACKEND` (only `ntfy` today). An empty variable is ignored, so it cannot clear a value set in the file; remove the line from the file instead. If `PUSH_NOTIFICATION_CONFIG` is set, the file it names must exist.

## 5. Confirm

`check` should end with `ready: yes`. A `send --title "Test" --dry-run` shows the request without sending; a plain `send --title "Test"` should arrive on the phone.
