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

Use the detected value as `<default-branch>` in subsequent commands (e.g., `git diff <default-branch>...HEAD`).

### Two different placeholders

Keep these distinct, because they diverge exactly when it matters:

- **`<default-branch>`** is what the detection above returns: the repository's default branch, usually `main`.
- **`<base-branch>`** is the branch a pull request targets. It is normally the same thing, but for a stacked PR it is the parent feature branch instead.

Skills that only ever work against the repository default (`merge-main`, `rebase-onto-main`) use `<default-branch>`. The `pr` skill distinguishes the two, because it detects a stacked-PR parent from the reflog and falls back to `<default-branch>` when that parent is missing, merged, or the current branch itself.

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

This limit is a default. A project that enforces its own convention wins: a commitlint config, a commit-msg hook, or a stated format in `AGENTS.md`, `CLAUDE.md`, or `.github/copilot-instructions.md`. Note that `@commitlint/config-conventional` sets `header-max-length` to 100.

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

| Prefix      | Use for                   |
| ----------- | ------------------------- |
| `feature/`  | New features              |
| `fix/`      | Bug fixes                 |
| `docs/`     | Documentation changes     |
| `refactor/` | Code restructuring        |
| `chore/`    | Maintenance tasks         |
| `feat/`     | Alternative to `feature/` |

The slug should be a lowercase, hyphen-separated description (e.g., `fix/login-timeout`, `feature/add-retry-logic`).

`feature/` is the primary spelling because it is what the `create-worktree` and `create-worktree-from-issue` skills emit; `feat/` is accepted everywhere `feature/` is.

**Include the issue number when working from an issue**, immediately after the type prefix: `fix/42-login-timeout`. The `pr` skill's primary issue-detection strategy parses `TYPE/N-description` out of the branch name, so a branch without the number forces a slower GitHub search that can match the wrong issue or none at all.

## Reading Collections with `gh api`

Any `gh api` call that returns a list is paginated. GitHub serves 30 items per page by default and caps a page at 100, and `gh api` returns only the first page unless told otherwise. A single-page read succeeds, exits 0, and silently reports a truncated view of the data.

Always pass `--paginate` when the result is a collection:

```bash
gh api --paginate repos/OWNER/REPO/issues/NUMBER/comments --jq '.[] | .body'
```

```bash
gh api --paginate repos/OWNER/REPO/pulls/NUMBER/reviews --jq '.[] | .id'
```

This matters most for checks that ask "has this already been handled?". A skill that scans prior comments for its own marker and reads only page one will stop finding that marker once the thread grows past 30 comments, and will redo work it already did.

`--paginate` also changes the shape of the output for `--jq`: pages are concatenated, so filters must handle a stream of arrays rather than one array. `--slurp` collects them back into a single array when a filter needs to see the whole collection at once.

When a permission rule allowlists these reads, match the flag as it is actually invoked. A rule for `Bash(gh api repos/*)` does not cover `gh api --paginate repos/*`, because the flag comes first.
