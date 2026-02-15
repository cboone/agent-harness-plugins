# hooks.json Reference

Hooks plugins use a `hooks/hooks.json` file to declare event-driven behaviors that run shell commands in response to Claude Code lifecycle events.

## File Location

```
plugins/PLUGIN-NAME/hooks/hooks.json
```

## Structure

```json
{
  "hooks": {
    "CATEGORY_NAME": [
      {
        "hooks": [
          {
            "command": "SHELL_COMMAND",
            "type": "command"
          }
        ],
        "matcher": "MATCHER_NAME"
      }
    ]
  }
}
```

## Hook Categories

Categories correspond to Claude Code lifecycle events:

| Category | When it fires |
|----------|---------------|
| `Notification` | User attention needed (idle prompt, permission prompt, elicitation dialog) |
| `PreCompact` | Before automatic context compaction |
| `Stop` | When Claude Code finishes a task |

## Matchers

Matchers within a category specify which specific events trigger the hook:

| Matcher | Category | Triggers when |
|---------|----------|---------------|
| `idle_prompt` | Notification | Claude is waiting for user input |
| `elicitation_dialog` | Notification | Claude is asking a question |
| `permission_prompt` | Notification | Claude needs permission to proceed |
| `auto` | PreCompact | Automatic compaction is triggered |
| *(none)* | Stop | No matcher needed; fires on any stop |

Not all hook entries need a matcher. The Stop category in the existing notify plugin has no matcher field.

## Script References

Use `${CLAUDE_PLUGIN_ROOT}` to reference scripts relative to the plugin root directory. This variable is resolved by Claude Code at runtime.

```json
{
  "command": "${CLAUDE_PLUGIN_ROOT}/scripts/my-script arg1 arg2",
  "type": "command"
}
```

## Example: Notification Hooks

Simplified example based on the `notify` plugin (see `plugins/notify/hooks/hooks.json` for the full version):

```json
{
  "hooks": {
    "Notification": [
      {
        "hooks": [
          {
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/notify 'Claude Code' '' 'Waiting for input\u2026' Ping",
            "type": "command"
          }
        ],
        "matcher": "idle_prompt"
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/notify stop",
            "type": "command"
          }
        ]
      }
    ]
  }
}
```

## Notes

- Each hook entry has `"type": "command"` -- this is currently the only supported type.
- Multiple hooks can fire for the same category with different matchers.
- Stop hooks receive JSON on stdin containing `transcript_path` and other context.
- Scripts referenced in hooks should be executable (`chmod +x`).
