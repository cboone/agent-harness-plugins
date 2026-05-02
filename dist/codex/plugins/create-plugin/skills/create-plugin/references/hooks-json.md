# hooks.json Reference

Hooks plugins use a `hooks/hooks.json` file to declare event-driven behaviors that run shell commands in response to Claude Code lifecycle events.

## File Location

```text
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

| Category       | When it fires                                                              |
| -------------- | -------------------------------------------------------------------------- |
| `Notification` | User attention needed (idle prompt, permission prompt, elicitation dialog) |
| `PostToolUse`  | After a tool call completes (observe only; cannot block)                   |
| `PreCompact`   | Before automatic context compaction                                        |
| `PreToolUse`   | Before a tool call executes (can block it by exiting with code 2)          |
| `Stop`         | When Claude Code finishes a task                                           |

## Matchers

Matchers within a category specify which specific events trigger the hook:

| Matcher                  | Category     | Triggers when                                 |
| ------------------------ | ------------ | --------------------------------------------- |
| `idle_prompt`            | Notification | Claude is waiting for user input              |
| `elicitation_dialog`     | Notification | Claude is asking a question                   |
| `permission_prompt`      | Notification | Claude needs permission to proceed            |
| Tool name (e.g., `Bash`) | PostToolUse  | After the specified tool call completes       |
| `auto`                   | PreCompact   | Automatic compaction is triggered             |
| Tool name (e.g., `Bash`) | PreToolUse   | When the specified tool is about to be called |
| _(none)_                 | Stop         | No matcher needed; fires on any stop          |

Not all hook entries need a matcher. The Stop category in the existing notify plugin has no matcher field. PreToolUse and PostToolUse matchers use the tool name (e.g., `Bash`, `Write`, `Edit`) to filter which tool calls trigger the hook. PostToolUse hooks are observe-only: they cannot block tool calls and always exit 0.

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

## Example: PreToolUse Guard

This example intercepts Bash commands before they run and delegates the decision to a plugin-local script:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "hooks": [
          {
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/check-command",
            "type": "command"
          }
        ],
        "matcher": "Bash"
      }
    ]
  }
}
```

The script receives the tool input as JSON on stdin. Exit code 0 allows the tool call; exit code 2 blocks it (stderr is shown to Claude as the rejection reason).

## Notes

- Each hook entry has `"type": "command"` -- this is currently the only supported type.
- Multiple hooks can fire for the same category with different matchers.
- PreToolUse hooks receive JSON on stdin with the tool input (e.g., `.input.command` for Bash). Exit 0 to allow, exit 2 to block.
- PostToolUse hooks receive JSON on stdin with the tool input. They are observe-only (exit code is ignored). Use for logging, analysis, or triggering side effects after a tool completes.
- Stop hooks receive JSON on stdin containing `transcript_path` and other context.
- Scripts referenced in hooks should be executable (`chmod +x`).
