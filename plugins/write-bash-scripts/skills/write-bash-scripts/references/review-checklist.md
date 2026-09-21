# Bash Review Checklist

Applies to Bash scripts and sourced Bash libraries (`*.sh`, `*.bash`, and extensionless files with a Bash shebang). Cite findings as `write-bash-scripts: Rule name`.

## Important

- **Strict mode**: An executable script sets `set -euo pipefail` near the top. Sourced libraries are exempt.
- **Quoted expansions**: Variable expansions and command substitutions are quoted, as in `"${var}"` and `"$(cmd)"`, unless word splitting is intended and commented.
- **Arrays for lists**: Lists of arguments or file names are held in arrays and expanded as `"${array[@]}"`, never built by splitting a string.
- **Masked exit codes**: `local` or `readonly` is declared separately from a command substitution, so the command's failure is not hidden behind the declaration's success.
- **Checked commands**: A command whose failure matters is checked with `if` or `||` wherever `set -e` does not apply, such as inside conditions, functions called from conditions, and non-final pipeline stages.
- **Safe increments**: Counters use `((i += 1))`, not `((i++))`, which returns a failure status when `i` is 0 and so exits under `set -e`. The increment in a `for ((...))` header is fine.
- **No eval**: `eval` is not used, especially on anything built from input; arrays replace it.
- **Pipeline scope**: Variables set inside `cmd | while read` are not relied on afterwards, since the loop runs in a subshell. Process substitution (`done < <(cmd)`) keeps them.
- **Safe temporary files**: Temporary files and directories come from `mktemp` and are removed by a `trap ... EXIT` handler.
- **Option-safe globs**: Wildcards that reach commands such as `rm` start with `./`, so a file name beginning with `-` is not parsed as an option.
- **No ls parsing**: File lists come from globs or `find -print0`, never from parsing `ls` output.
- **Privileged writes**: Root-owned files are written with `sudo tee`, not `sudo echo ... >`, and scripts never rely on SUID or SGID.
- **Bash 3.2 compatibility**: A script that can run on a stock Mac avoids `readarray`, `mapfile`, `declare -A`, `${var,,}`, namerefs and `[[ -v ]]`, and guards possibly empty arrays under `set -u` as `${array[@]+"${array[@]}"}`. A script that needs bash 4 checks `BASH_VERSINFO` and exits with a clear message.

## Nits

- **Shebang**: `#!/usr/bin/env bash`.
- **Main function**: Script logic sits in a `main` function called at the end as `main "$@"`.
- **Braced variables**: `${var}` rather than `$var`, except `"$@"` and `"$*"`, which stay unbraced.
- **Command substitution**: `$(...)`, never backticks.
- **Tests and arithmetic**: `[[ ... ]]` for tests, `((...))` for arithmetic statements and `$((...))` for expressions, not `[ ... ]`, `let`, `expr` or `$[...]`.
- **Function syntax**: `function name() { ... }`, with both the keyword and the parentheses.
- **Naming**: `snake_case` functions, lowercase local variables, and `ALL_CAPS` constants declared `readonly`.
- **Local variables**: Variables inside functions are declared `local`.
- **Errors to stderr**: Error and progress messages go to stderr; stdout carries only data.
- **Temporary cd**: A temporary directory change runs in a subshell, as in `(cd dir && make)`.
- **Line reading**: Lines are read with `while IFS= read -r line`, not `for line in $(cat file)`.
- **Default case**: A `case` statement has a `*)` branch that handles unexpected values.
- **Command checks**: Tool availability is tested with `command -v`, not `which`.
- **No useless cat**: Commands read files directly or through redirection instead of `cat file | cmd`.
- **File extensions**: Executables have no extension; sourced libraries use `.sh` or `.bash`.
- **Function comments**: Non-trivial functions document their arguments, outputs and return codes, and scripts document their exit codes.

## Do not flag

- **Formatting**: Indentation and spacing that `shfmt` produces.
- **ShellCheck findings**: Anything ShellCheck reports when it runs in CI.
- **Unbraced argument lists**: `"$@"` and `"$*"` are deliberately unbraced.
- **Sourced files**: Missing strict mode or `main` function in a library meant to be sourced.
- **Commented word splitting**: An unquoted expansion with a comment explaining that splitting is intended.
