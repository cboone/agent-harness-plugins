# Diff Output Formatting

User git configurations often include external diff tools (e.g., difftastic), custom color schemes, and pager settings optimized for human terminal reading. These settings produce output that is harder for Claude Code to parse accurately.

Always use these three flags on diff-producing git commands to get clean, standard unified diff output:

| Flag            | Purpose                                               |
| --------------- | ----------------------------------------------------- |
| `--no-ext-diff` | Bypass external diff tools; use built-in unified diff |
| `--no-color`    | Prevent ANSI escape codes in output                   |
| `--no-pager`    | Prevent interactive pager from blocking execution     |

## Why Unified Diff

Standard unified diff format (`-`/`+` prefixed lines with `@@` hunk headers) is:

- **Unambiguous**: explicit markers for additions and removals
- **Token-efficient**: no side-by-side padding or column alignment
- **Location-aware**: `@@ -L,N +L,N @@` headers map directly to line numbers for edits
- **Patch-compatible**: the same format used by `git apply`, code review tools, and patches

External diff tools like difftastic produce structural, side-by-side output that relies on column alignment. This format is lossy in plain text and harder to reason about programmatically.

## Commands That Need These Flags

### git diff

```bash
git --no-pager diff --no-ext-diff --no-color
```

Common variants:

```bash
# Staged changes
git --no-pager diff --no-ext-diff --no-color --cached

# Compare branch to base
git --no-pager diff --no-ext-diff --no-color <base-branch>...HEAD

# Stat summary only
git --no-pager diff --no-ext-diff --no-color --stat <base-branch>..HEAD

# Changed file names only
git --no-pager diff --no-ext-diff --no-color --name-only <base-branch>..HEAD

# Changed file names with status (added, modified, deleted)
git --no-pager diff --no-ext-diff --no-color --name-status <base-branch>..HEAD
```

### git log (with patches)

```bash
git --no-pager log --no-ext-diff --no-color -p
```

### git show

```bash
git --no-pager show --no-ext-diff --no-color
```

## Flag Placement

`--no-pager` is a git-level flag and must come before the subcommand. `--no-ext-diff` and `--no-color` are subcommand flags and come after:

```bash
git --no-pager diff --no-ext-diff --no-color
#   ^^^^^^^^^^       ^^^^^^^^^^^^  ^^^^^^^^^^
#   git flag         subcommand flags
```

## When These Flags Are Not Needed

Commands that do not produce diff output do not need these flags:

- `git status`
- `git log` (without `-p` or `--patch`)
- `git branch`
- `git add`, `git commit`, `git push`
- `git rev-parse`, `git merge-base`
