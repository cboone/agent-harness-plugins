# Tmpfile Pattern

Use tmpfiles when passing long content to git or `gh` CLI commands. This keeps Bash commands short and prevents Claude Code permission prompts triggered by complex-looking command strings.

## When to Use

- PR bodies (`gh pr create --body-file`)
- Issue bodies (`gh issue create --body-file`)
- Review replies (script `--body-file` flags)
- Any `gh` subcommand that accepts `--body-file` and the content is more than a few lines

## Three-Step Workflow

### 1. Create the tmpfile

Generate a unique path with `mktemp -u`:

```bash
mktemp -u /tmp/gh-pr-body-XXXXXX
# Returns a unique path that does NOT exist on disk, e.g.: /tmp/gh-pr-body-x4y5z6
```

**The `-u` flag is required.** Without it, `mktemp` creates an empty file at the path it prints, and the Write tool refuses to overwrite a file it has not Read first (`File has not been read yet. Read it first before writing to it.`). Since the file is empty by construction there is no reason to Read it, so plain `mktemp` forces a pointless Read or leaves the write to fail. With `-u`, the path is unique but unoccupied, so Write creates it fresh. The flag is portable for this purpose: both implementations leave nothing on disk at the path they print. macOS `mktemp(1)` documents `-u` as unlinking the temp file before `mktemp` exits; GNU documents `-u` (`--dry-run`) as printing a name without creating anything.

**Caveat:** `-u` does not atomically reserve the name, which is why both man pages call it "unsafe" and discourage it in general. The trade-off is acceptable here because the Write follows immediately and the content is a PR, issue, or release body rather than a secret. Do not carry this pattern over to security-sensitive temp files; for those, use plain `mktemp` and write through a shell redirect instead of the Write tool.

Use a descriptive prefix that reflects the purpose (`gh-pr-body`, `gh-issue-body`, `copilot-reply`, etc.). On macOS/BSD, `mktemp` only replaces trailing `X` characters, so the template must end with the `XXXXXX` run (do not add suffixes like `.md` after it). That trailing `XXXXXX` is replaced by `mktemp` with random characters. Always capture the returned path and use it in subsequent commands.

### 2. Write content with the Write tool

Use the Write tool (not `echo` or `cat`) to write the full content to the path returned by `mktemp -u`. The Write tool handles multiline content natively and keeps the subsequent Bash command short.

### 3. Pass `--body-file` to the command

Run the `gh` command with `--body-file` pointing to the path returned by `mktemp -u` (shown as `TMPFILE` below), in a **separate message** issued only after the Write tool has returned:

```bash
gh pr create --title "Add user authentication" --body-file TMPFILE
```

## Never Batch the Write With the Command

Issue the Write call (step 2) and the `gh` call (step 3) as two separate, sequential messages. Wait for Write to return before invoking `gh`.

`gh` reads the body file at invocation time. If both calls go out in a single parallel batch, `gh` can run before the file exists and will create the pull request, issue, or release with an **empty body**. That is a silent failure: the command still succeeds and still prints a URL, so it is only caught later, by hand.

This is a deliberate exception to the general preference for parallel tool calls. That preference applies to calls with no dependencies between them. These two have a dependency: `gh --body-file` consumes the file that Write produces.

## Cleanup

Issue cleanup as a **separate Bash tool call** after the `gh` command:

```bash
rm -f TMPFILE
```

Each Bash tool invocation runs unconditionally, so the cleanup runs whether the `gh` command succeeded or failed, and the `gh` command's exit code is preserved by the harness without any shell-level wrapping.

Do not chain the cleanup onto the `gh` command, and do not wrap it to preserve the exit code. In particular, never write:

```bash
# BAD - breaks in zsh
gh pr create --title "..." --body-file TMPFILE; status=$?; rm -f TMPFILE; exit $status
```

In zsh (the macOS default shell), `status` and `pipestatus` are read-only built-in aliases for `$?` and `${pipestatus[@]}`. Assigning to either fails with `read-only variable: status`, so this wrapper exits non-zero and mis-reports a successful `gh` call as failed. Keep cleanup in its own Bash tool call instead.

## Examples

### GitHub issue

```bash
mktemp -u /tmp/gh-issue-body-XXXXXX
# Returns: /tmp/gh-issue-body-a1b2c3
```

Write body content via the Write tool to the returned path, then, in a separate message:

```bash
gh issue create --title "Fix login timeout" --body-file /tmp/gh-issue-body-a1b2c3 --label "bug"
```

```bash
rm -f /tmp/gh-issue-body-a1b2c3
```

### Pull request

```bash
mktemp -u /tmp/gh-pr-body-XXXXXX
# Returns: /tmp/gh-pr-body-x4y5z6
```

Write PR body via the Write tool to the returned path, then, in a separate message:

```bash
gh pr create --title "Add retry logic to API client" --body-file /tmp/gh-pr-body-x4y5z6
```

```bash
rm -f /tmp/gh-pr-body-x4y5z6
```

### Review reply

```bash
mktemp -u /tmp/copilot-reply-XXXXXX
# Returns a unique path, e.g.: /tmp/copilot-reply-r7s8t9
```

Write reply via the Write tool to the returned path, then, in a separate message, pass it to the reply command with `--body-file`.

## Anti-Patterns

**Never pipe content inline:**

```bash
# BAD - triggers permission prompts
echo "Long body content..." | gh issue create --title "Title" --body-file -
```

**Never use `--body` with long inline content:**

```bash
# BAD - long string triggers permission prompts
gh pr create --title "Title" --body "## Summary\n\n- Change 1\n- Change 2\n..."
```

**Never use HEREDOC for long `gh` arguments:**

```bash
# BAD - HEREDOC with long content still triggers prompts
gh pr create --title "Title" --body "$(cat << 'EOF'
## Summary

- Change 1
- Change 2
- Change 3
EOF
)"
```

The tmpfile pattern is always safer for content that might exceed a few lines.
