# Block rm -rf

Blocks recursive `rm` commands before they execute.

**Type:** Hook
**Requires:** [`trash`](https://hasseg.org/trash/) — install via [Homebrew](https://brew.sh): `brew install trash`

## What It Does

Intercepts `rm -rf`, `rm -r`, `rm -R`, `rm --recursive`, and variants before they run. Rejects the command and suggests using `trash` instead, which moves files to the system Trash rather than permanently deleting them.

## When It Fires

This hook runs as a `PreToolUse` hook on the `Bash` tool. Every time Claude Code is about to execute a shell command, the hook inspects it for recursive `rm` patterns and blocks the command if one is found.

## See Also

- [All plugins](../../README.md)
