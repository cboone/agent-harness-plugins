---
applyTo: "**/scripts/**,**/bin/**,**/tests/fixtures/**"
---

# Shell script review instructions

Bundled scripts here run on macOS and Linux alike, so portability findings are welcome. These specific ones are not defects, and have been checked:

- **`find -maxdepth` and `-mmin` are portable.** Both are present in BSD `find` on macOS as well as GNU `find`, and `find <path> -maxdepth 0 -mmin +N` works on both. Do not report either as a GNU-only extension.
- **`flock` is deliberately absent.** macOS has no `flock(1)`, which is why mutual exclusion here uses `mkdir`, which is atomic on every filesystem these scripts run on.
- **`kill -0 <pid>` is a liveness test, not a terminate.** It is the POSIX interface and keeps its name under the neutral-terminology convention, which exempts names the world already fixed.
- **`local` is declared separately from command substitution** (`local x` then `x="$(cmd)"`) on purpose: `local` always returns 0 and would mask the command's exit code.
- **`# shellcheck disable=SC2016` at file scope is intentional** in scripts built around `jq` filters. The `$name` tokens inside single-quoted `jq` programs are `jq` variables bound with `--arg`, not shell expansions.

Two checks are disabled in `.shellcheckrc` by design and should not be raised in review: `check-extra-masked-returns` (SC2312) and `check-set-e-suppressed` (SC2310).

## Conventions worth enforcing

- `#!/usr/bin/env bash`, then `set -euo pipefail`.
- `${var}` braces, `[[ ]]` over `[ ]`, `$(...)` over backticks, a default `*)` case in every `case`.
- Errors go to stderr through a `die` helper that prefixes the script name; stdout carries only the command's own output.
- Never chain a tmpfile cleanup onto the command that consumed it with `; status=$?`. In zsh, the macOS default shell, `status` is a read-only alias for `$?` and the assignment fails.
