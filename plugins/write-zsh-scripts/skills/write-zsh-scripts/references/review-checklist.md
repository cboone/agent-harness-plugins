# Zsh Review Checklist

Applies to zsh scripts, plugins, configuration files and completion functions (`*.zsh`, zsh dotfiles, and files with a zsh shebang or a `#compdef` line). Cite findings as `write-zsh-scripts: Rule name`.

## Important

- **Strict mode**: An executable script sets `setopt ERR_EXIT NO_UNSET PIPE_FAIL` near the top. Sourced files, plugins and completions are exempt.
- **Scoped options**: A function in a sourced file or plugin that changes options starts with `emulate -L zsh`, so the change does not leak into the user's shell.
- **No accidental globals**: Function variables are declared `local` or `typeset`; anything meant to be global uses `typeset -g`. Sourced code must not leave stray variables in the user's shell.
- **One-based arrays**: Array indexing starts at 1. Code ported from Bash does not read `${array[0]}` or loop from 0.
- **Masked exit codes**: `local` is declared separately from a command substitution, so the command's failure is not hidden.
- **Checked commands**: A command whose failure matters is checked with `if` or `||` wherever `ERR_EXIT` does not apply.
- **Pipeline scope**: Variables set inside `cmd | while read` are not relied on afterwards; process substitution keeps them in the current shell.
- **No eval**: `eval` is not used; arrays replace it.
- **Prompt expansion**: `print -P` never receives untrusted text unless `%` has been escaped as `%%`.
- **Hook registration**: Hooks are added with `add-zsh-hook`, never by redefining `precmd`, `preexec` or `chpwd`, which would replace other plugins' hooks.
- **Safe temporary files**: Temporary files come from `mktemp`, get `chmod 600` when they hold anything sensitive, and are removed by a trap or an `always` block.
- **Completion results**: A completion function returns zero when it added matches and nonzero otherwise, and a direct `compadd` call passes `"${expl[@]}"`. A call made through `_wanted` or another helper that injects the expansion does not repeat it.

## Nits

- **Shebang**: `#!/usr/bin/env zsh`.
- **Main function**: Script logic sits in a `main` function called at the end as `main "${@}"`.
- **Braced and quoted expansions**: `"${var}"` and `"$(cmd)"`, even though zsh does not word-split by default, to prevent glob expansion and show intent.
- **Array expansion**: `"${array[@]}"` or `"${(@)array}"` to keep elements separate inside quotes.
- **Command substitution**: `$(...)`, never backticks.
- **Tests and arithmetic**: `[[ ... ]]` for tests, `((...))` for arithmetic statements and `$((...))` for expressions.
- **Function syntax**: `function name() { ... }`, with both the keyword and the parentheses. Autoloaded function files hold only the body.
- **Naming**: `snake_case` functions, lowercase local variables, `ALL_CAPS` constants declared `readonly`, and an underscore prefix for private helpers and variables.
- **typeset over declare**: `typeset`, with type flags such as `-a`, `-A` and `-i`, instead of `declare`.
- **Autoloading**: `autoload -Uz` for functions loaded on first use.
- **Builtins over external commands**: Parameter expansion (`${var##*/}`, `${(L)var}`, `${var//old/new}`) and `print -r --` instead of `basename`, `tr`, `sed` or `echo` for simple string work.
- **Command checks**: `command -v` or `(( ${+commands[name]} ))`, not `which`.
- **Errors to stderr**: Error and progress messages go to stderr; stdout carries only data.
- **Default case**: A `case` statement has a `*)` branch that handles unexpected values.
- **Temporary cd**: A temporary directory change runs in a subshell.
- **File extensions**: Libraries, plugins and configuration snippets use `.zsh`; executables and completion functions have no extension.
- **Completion descriptions**: Groups are described with `_description`, not text passed straight to `compadd`, and `curcontext` is made local when `_arguments -C` is used.

## Do not flag

- **Formatting**: Indentation and spacing that `shfmt` produces.
- **Linter findings**: Anything ShellCheck or `zsh -n` reports when it runs in CI, and ShellCheck warnings about zsh-only syntax such as expansion flags and glob qualifiers.
- **Sourced files**: Missing strict mode or `main` function in rc files, plugins, libraries and completion functions.
- **Private underscores**: Leading underscores on internal names; unlike Bash, this is the zsh convention.
