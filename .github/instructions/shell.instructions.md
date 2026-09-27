---
applyTo: "**/scripts/**,**/bin/**,**/tests/fixtures/**"
---

# Shell script review instructions

Bundled scripts here run on macOS and Linux alike, so portability findings are welcome. These specific ones are not defects, and have been checked:

- **`git worktree list --porcelain -z` is the only form that is parsed.** The newline-delimited form splits a worktree path containing a newline across two apparent fields. NUL is the one byte a path cannot hold, so `-z` plus `read -r -d ''` is correct for every path a filesystem allows. A `read -d ''` loop also needs `|| [[ -n "${line}" ]]` so a final field carrying no terminator is not discarded.
- **`flock` is deliberately absent.** macOS has no `flock(1)`, which is why mutual exclusion here uses `mkdir`, which is atomic on every filesystem these scripts run on.
- **`kill -0 <pid>` is a liveness test, not a terminate.** It is the POSIX interface and keeps its name under the neutral-terminology convention, which exempts names the world already fixed.
- **A `"$(< path)"` read is always preceded by `-f` and `-r` tests.** That expansion fails during expansion rather than as a command, so a redirection on the assignment and a trailing `||` both miss it and Bash exits with its own unprefixed diagnostic. `-r` alone is insufficient: it is true for a readable directory. A scrut case in `tests/scrut/repo-tooling.md` enforces this.
- **`local` is declared separately from command substitution** (`local x` then `x="$(cmd)"`) on purpose: `local` always returns 0 and would mask the command's exit code.
- **`# shellcheck disable=SC2016` at file scope is intentional** in scripts built around `jq` filters. The `$name` tokens inside single-quoted `jq` programs are `jq` variables bound with `--arg`, not shell expansions.
- **`jq`'s `sub` and `gsub` take an optional third flags argument.** `sub/3` and `gsub/3` are builtins alongside `sub/2` and `gsub/2`, so `sub("^\\*\\*Findings:\\*\\*"; ""; "i")` is a case-insensitive substitution, not a call with a surplus operand. Confirm with `jq -n 'builtins | map(select(startswith("sub/") or startswith("gsub/")))'`, which lists all four. The same applies to `scan/2`, `match/2`, `test/2`, `capture/2` and `splits/2`; this file's scripts have used a flagged `scan` since before the flagged `sub` appeared.
- **`jq`'s `scan` emits capture arrays when the pattern has groups.** The builtin maps each match to `[.captures[].string]` when the regex has capture groups, and to the whole-match string only when it has none. `"a1 b2" | [scan("([a-z])([0-9])")]` yields `[["a","1"],["b","2"]]`, so `.[0]`, `.[1]`, and so on after a grouped `scan` index capture groups, not characters.
- **`gh api --paginate` without `--jq` concatenates REST array pages into one array.** A paginated array endpoint yields a single JSON document, so a downstream `type == "array"` check holds at any page count and no flattening step is needed. `--jq` is what changes this: gh applies the filter to each page separately, so `--paginate --jq 'length'` over three pages emits three numbers. `--slurp` is for the array-of-arrays shape and is required only when page boundaries must be preserved, as in a probe that pipes into a standalone `jq` and takes `last` across all pages. The `gh api --help` line "Each page is a separate JSON array or object" describes the GraphQL and object-returning cases; do not read it as applying to REST array endpoints.

Two checks are disabled in `.shellcheckrc` by design and should not be raised in review: `check-extra-masked-returns` (SC2312) and `check-set-e-suppressed` (SC2310).

## Conventions worth enforcing

- `#!/usr/bin/env bash`, then `set -euo pipefail`.
- `${var}` braces, `[[ ]]` over `[ ]`, `$(...)` over backticks, a default `*)` case in every `case`.
- Errors go to stderr through a `die` helper that prefixes the script name; stdout carries only the command's own output.
- Never chain a tmpfile cleanup onto the command that consumed it with `; status=$?`. In zsh, the macOS default shell, `status` is a read-only alias for `$?` and the assignment fails.

- Shell function arguments include the subcommand words. In a `gh()` fixture that receives `gh release create <tag>`, `${1}` is `release`, `${2}` is `create`, and `${3}` is the tag.
