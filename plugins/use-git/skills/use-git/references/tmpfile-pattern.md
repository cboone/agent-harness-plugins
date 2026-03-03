# Tmpfile Pattern

Use tmpfiles when passing long content to git or `gh` CLI commands. This keeps Bash commands short and prevents Claude Code permission prompts triggered by complex-looking command strings.

## When to Use

- PR bodies (`gh pr create --body-file`)
- Issue bodies (`gh issue create --body-file`)
- Review replies (script `--body-file` flags)
- Any `gh` subcommand that accepts `--body-file` and the content is more than a few lines

## Three-Step Workflow

### 1. Create the tmpfile

Generate a unique path with `mktemp`:

```bash
mktemp /tmp/gh-pr-body-XXXXXX
# Returns a unique path, e.g.: /tmp/gh-pr-body-x4y5z6
```

Use a descriptive prefix that reflects the purpose (`gh-pr-body`, `gh-issue-body`, `copilot-reply`, etc.). On macOS/BSD, `mktemp` only replaces trailing `X` characters, so the template must end with the `XXXXXX` run (do not add suffixes like `.md` after it). That trailing `XXXXXX` is replaced by `mktemp` with random characters. Always capture the returned path and use it in subsequent commands.

### 2. Write content with the Write tool

Use the Write tool (not `echo` or `cat`) to write the full content to the path returned by `mktemp`. The Write tool handles multiline content natively and keeps the subsequent Bash command short.

### 3. Pass `--body-file` to the command

Run the `gh` command with `--body-file` pointing to the path returned by `mktemp` (shown as `TMPFILE` below):

```bash
gh pr create --title "Add user authentication" --body-file TMPFILE
```

## Cleanup

Always remove the tmpfile after the command completes, regardless of success or failure:

```bash
rm -f TMPFILE
```

## Examples

### GitHub issue

```bash
mktemp /tmp/gh-issue-body-XXXXXX
# Returns: /tmp/gh-issue-body-a1b2c3
```

Write body content via the Write tool to the returned path, then:

```bash
gh issue create --title "Fix login timeout" --body-file /tmp/gh-issue-body-a1b2c3 --label "bug"
```

```bash
rm -f /tmp/gh-issue-body-a1b2c3
```

### Pull request

```bash
mktemp /tmp/gh-pr-body-XXXXXX
# Returns: /tmp/gh-pr-body-x4y5z6
```

Write PR body via the Write tool to the returned path, then:

```bash
gh pr create --title "Add retry logic to API client" --body-file /tmp/gh-pr-body-x4y5z6
```

```bash
rm -f /tmp/gh-pr-body-x4y5z6
```

### Review reply

```bash
mktemp /tmp/copilot-reply-XXXXXX
# Returns a unique path, e.g.: /tmp/copilot-reply-r7s8t9
```

Write reply via the Write tool to the returned path, then pass to the reply command with `--body-file`.

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
