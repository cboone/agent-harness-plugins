# Fix check-zsh-scripts: Remove beautysh, fix shellcheck and zcompile (#212, #208)

## Context

The check-zsh-scripts skill has three bugs:

1. **beautysh has no zsh support** (#212): beautysh treats all input as bash, conflicting with shfmt and producing incorrect formatting for zsh-specific syntax. It should be removed entirely.
1. **`shellcheck --shell=zsh` does not exist** (#208): ShellCheck only supports sh/bash/dash/ksh. The command fails with "Unknown shell: zsh".
1. **`zcompile` invocation is broken** (#208): `zsh -c 'zcompile "$1"' -- <file>` fails because `--` is interpreted as a filename by zsh, not as an option separator.

## Version

Bump check-zsh-scripts from 2.0.0 to 2.1.0 (minor). Do not bump `metadata.version` in marketplace.json (no plugins added/removed from the catalog).

## Commits

Two logical commits, both referencing their respective issues:

### Commit 1: `fix: correct shellcheck and zcompile invocations in check-zsh-scripts (#208)`

Fix the two broken commands.

**shellcheck fix**: Change `--shell=zsh` to `--shell=bash` with `--exclude` for known zsh false positives:

```bash
shellcheck --shell=bash --exclude=SC1090,SC2039,SC2154,SC2168,SC2296,SC2299 <file>
```

The SC3000-series codes (too numerous for `--exclude`) remain handled as filtered output in the reporting step.

**zcompile fix**: Change `--` to `_` as the `$0` placeholder:

```bash
zsh -c 'zcompile "$1"' _ <file>
```

#### Files

1. **`plugins/check-zsh-scripts/skills/check-zsh-scripts/SKILL.md`**
   - Line 23: `shellcheck --shell=zsh` -> `shellcheck --shell=bash` in tool table
   - Line 82: `zsh -c 'zcompile "$1"' -- <file>` -> `zsh -c 'zcompile "$1"' _ <file>`
   - Line 96: `shellcheck --shell=zsh <file>` -> `shellcheck --shell=bash --exclude=SC1090,SC2039,SC2154,SC2168,SC2296,SC2299 <file>`
   - Lines 98-99: Update filter note to clarify that `--exclude` handles the stable codes, and SC3000-series should be filtered from output

1. **`plugins/check-zsh-scripts/skills/check-zsh-scripts/references/tools/shellcheck.md`**
   - Line 1: `# shellcheck --shell=zsh` -> `# shellcheck (zsh scripts)`
   - Line 5: Update purpose to note that ShellCheck does not support `--shell=zsh`; `--shell=bash` is used as the closest approximation
   - Line 10: Fix the command to `shellcheck --shell=bash --exclude=SC1090,SC2039,SC2154,SC2168,SC2296,SC2299 <file>`

1. **`plugins/check-zsh-scripts/skills/check-zsh-scripts/references/tools/zcompile.md`**
   - Line 10: Fix to `zsh -c 'zcompile "$1"' _ <file>`
   - Add note explaining `_` is the conventional `$0` placeholder

1. **`plugins/check-zsh-scripts/README.md`**
   - Line 20: `shellcheck --shell=zsh` -> `shellcheck` (description text, no need for the flag detail here)

### Commit 2: `fix!: remove beautysh from check-zsh-scripts (#212)`

Remove beautysh entirely. Bump version to 2.1.0.

#### Files

1. **`plugins/check-zsh-scripts/skills/check-zsh-scripts/SKILL.md`**
   - Lines 3-5 (frontmatter description): Remove "beautysh,"
   - Line 28: Delete beautysh row from tool table
   - Line 56: Remove `command -v beautysh`
   - Line 145: Remove "and rely on beautysh" from shfmt fallback note
   - Lines 149-155: Delete entire section 3h (Code Formatting with beautysh)
   - Line 171: Delete beautysh row from results table
   - Lines 184-191: Rewrite fix section to reference only shfmt; remove `beautysh <file>` and "then beautysh" note
   - Line 213: Remove beautysh fallback from shfmt parse error handling

1. **`plugins/check-zsh-scripts/skills/check-zsh-scripts/references/tools/beautysh.md`**
   - Delete this file

1. **`plugins/check-zsh-scripts/skills/check-zsh-scripts/references/tools/shfmt.md`**
   - Lines 71-81: Remove "Comparison with beautysh" section (table and coexistence note)
   - Lines 85-86: Remove beautysh fallback mention in notes

1. **`plugins/check-zsh-scripts/.claude-plugin/plugin.json`**
   - Remove "beautysh," from description (line 5)
   - Remove "beautysh" from keywords (line 7)
   - Bump version to "2.1.0" (line 12)

1. **`plugins/check-zsh-scripts/README.md`**
   - Remove beautysh from description (line 20)
   - Remove beautysh requirements entry (line 25)
   - Remove `"Bash(beautysh *)"` from permissions JSON (line 42)

1. **`.claude-plugin/marketplace.json`**
   - Remove "beautysh," from description (line 115)
   - Remove "beautysh" from keywords (line 117)
   - Bump version to "2.1.0" (line 122)

1. **`README.md` (root)**
   - Line 197: Remove "and `beautysh`" from description
   - Line 200: Remove beautysh from the Requires list

1. **`CLAUDE.md`**
   - Line 77: Remove `│                   ├── beautysh.md` from directory tree

1. **`AGENTS.md`**
   - Line 77: Remove `│                   ├── beautysh.md` from directory tree

## Verification

1. Confirm shellcheck command works: `shellcheck --shell=bash --exclude=SC1090,SC2039,SC2154,SC2168,SC2296,SC2299 /dev/null` (should exit 0)
1. Confirm zcompile command works: create a temp zsh file and run `zsh -c 'zcompile "$1"' _ /tmp/test.zsh`
1. Grep for any remaining "beautysh" references: `grep -r beautysh plugins/check-zsh-scripts/`
1. Grep for remaining `--shell=zsh`: `grep -r 'shell=zsh' plugins/check-zsh-scripts/`
1. Grep for old zcompile pattern: `grep -r "zcompile.*-- " plugins/check-zsh-scripts/`
1. Run `/check-versions` skill to verify plugin.json and marketplace.json versions match
