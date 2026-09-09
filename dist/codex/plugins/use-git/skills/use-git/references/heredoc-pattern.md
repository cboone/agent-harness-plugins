# HEREDOC Pattern

Use HEREDOCs for short, predictable-length content passed to git commands. The primary use case is commit messages.

## When to Use

- Commit messages (`git commit -S -m`)
- Tag messages when they are short (`git tag -a -m`)
- Any git argument where the content is a few lines at most

## When NOT to Use

- PR bodies, issue bodies, release notes, or review replies (use the tmpfile pattern instead)
- Any content that could grow beyond a few lines
- Any `gh` CLI command offering a file flag such as `--body-file` or `--notes-file`

## The Pattern

```bash
git commit -S -m "$(
  cat << 'EOF'
type: description here
EOF
)"
```

### Key Details

- **Single-quoted `'EOF'`**: Prevents the shell from expanding variables (`$VAR`) or running subshells (`` `cmd` ``) inside the HEREDOC. Always use `'EOF'`, not unquoted `EOF`.
- **GPG signing**: The `-S` flag ensures every commit is signed. The sandbox cannot access GPG keys, so resort immediately to the unsandboxed Bash command.
- **Indentation**: The closing `EOF` must appear on its own line with no leading whitespace (unless using `<<-` with tab indentation, which is fragile).

## Multi-Line Commit Messages

For commit messages with a body:

```bash
git commit -S -m "$(
  cat << 'EOF'
type: short description

Longer explanation of why this change was made.
Additional context or references.
EOF
)"
```

The first line is the subject. A blank line separates the subject from the body.

## Common Commit Types

| Type       | Use for                                     |
| ---------- | ------------------------------------------- |
| `feat`     | New functionality                           |
| `fix`      | Bug fix                                     |
| `docs`     | Documentation changes only                  |
| `refactor` | Code restructuring without behavior change  |
| `test`     | Adding or updating tests                    |
| `chore`    | Build, tooling, or maintenance changes      |
| `style`    | Formatting, whitespace, or cosmetic changes |
