# Common Operations

Reusable patterns for git and `gh` CLI operations.

## Base Branch Detection

Detect the repository's default branch. Use `gh` as the primary method and fall back to `git`:

**Primary:**

```bash
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
```

**Fallback** (if `gh` is unavailable or the command fails):

```bash
git remote show origin | grep 'HEAD branch' | sed 's/.*: //'
```

Use the detected value as `<base-branch>` in subsequent commands (e.g., `git diff <base-branch>...HEAD`).

## Push with Upstream Fallback

Try a plain push first. If the branch has no upstream, set one:

```bash
git push
```

If that fails with "no upstream branch":

```bash
git push -u origin HEAD
```

## Checking Remote Tracking Status

Determine whether the current branch tracks a remote:

```bash
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "no upstream"
```

If the output is "no upstream", the branch needs `git push -u origin HEAD` for the first push.

## Conventional Commit Format

```text
type: short description
```

Keep the subject line under 72 characters. Use imperative mood ("add", not "added" or "adds").

### Types

| Type       | Use for                                     |
| ---------- | ------------------------------------------- |
| `feat`     | New functionality                           |
| `fix`      | Bug fix                                     |
| `docs`     | Documentation changes only                  |
| `refactor` | Code restructuring without behavior change  |
| `test`     | Adding or updating tests                    |
| `chore`    | Build, tooling, or maintenance changes      |
| `style`    | Formatting, whitespace, or cosmetic changes |

### Issue References

- `fixes #N` for bug fix branches (`fix/*`)
- `closes #N` for other branch types

## Branch Naming

Use `TYPE/SLUG` format:

| Prefix      | Use for                |
| ----------- | ---------------------- |
| `feat/`     | New features           |
| `fix/`      | Bug fixes              |
| `docs/`     | Documentation changes  |
| `refactor/` | Code restructuring     |
| `chore/`    | Maintenance tasks      |
| `feature/`  | Alternative to `feat/` |

The slug should be a lowercase, hyphen-separated description (e.g., `fix/login-timeout`, `feat/add-retry-logic`).

Include issue numbers when working from an issue: `fix/42-login-timeout`.
