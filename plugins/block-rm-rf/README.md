# Block rm -rf

Blocks recursive `rm` commands before they execute.

**Type:** Hook
**Requires:** [`trash`](https://hasseg.org/trash/). Install via [Homebrew](https://brew.sh): `brew install trash`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Block rm -rf** from the available plugins.

### Using with OpenCode

OpenCode loads the plugin automatically when [`OPENCODE_CONFIG_DIR`](../../README.md#using-with-opencode) is set to this repository's `dist/opencode/` mirror. The TypeScript plugin lives at [`opencode/index.ts`](./opencode/index.ts) and uses the `tool.execute.before` hook to apply the same regex and rejection message as the Claude Code version.

For users who prefer declarative permission rules over a custom message, this snippet in `opencode.json` blocks recursive `rm` natively:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "bash": {
      "rm -*r*": "deny",
      "rm --recursive*": "deny"
    }
  }
}
```

The plugin remains the higher-fidelity option because it preserves the "use `trash` instead" remediation hint.

## What It Does

Intercepts `rm -rf`, `rm -r`, `rm -R`, `rm --recursive`, and variants before they run. Rejects the command and suggests using `trash` instead, which moves files to the system Trash rather than permanently deleting them.

## When It Fires

This hook runs as a `PreToolUse` hook on the `Bash` tool. Every time Claude Code is about to execute a shell command, the hook inspects it for recursive `rm` patterns and blocks the command if one is found.

## See Also

- [All plugins](../../README.md)
