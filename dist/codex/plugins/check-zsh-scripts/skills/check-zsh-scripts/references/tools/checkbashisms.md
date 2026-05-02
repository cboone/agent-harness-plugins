# checkbashisms

## Purpose

Identify bash-specific constructs. Part of the Debian `devscripts` package. Originally designed to find bashisms in POSIX sh scripts, but useful for zsh to flag constructs that are bash-specific and may behave differently.

## Command

```bash
checkbashisms <file>
```

## Installation

macOS:

```bash
brew install devscripts
```

Linux (Debian/Ubuntu):

```bash
apt install devscripts
```

## Interpretation for Zsh

Most `checkbashisms` output is informational rather than actionable for zsh scripts. Many "bashisms" are also valid zsh syntax (e.g., `[[ ]]`, arrays, `local`).

### Constructs That Truly Differ Between Bash and Zsh

Focus on these when reviewing output:

- `BASH_SOURCE`, `BASH_VERSINFO`, `BASH_COMMAND`: Bash-only variables with no zsh equivalent
- `shopt`: Bash-only; zsh uses `setopt`/`unsetopt`
- `enable`: Bash builtin; different semantics in zsh
- `declare -n` (namerefs): Bash 4.3+; zsh has no direct equivalent (use `${(P)var}` instead)
- `$RANDOM` seeding: Behavior differs between bash and zsh
- `readarray`/`mapfile`: Bash-only; zsh uses `${(f)"$(command)"}` or `read -A`
- `compgen`, `complete`: Bash completion system; zsh uses `compctl`/`compadd`

### Expected False Positives

These are flagged by `checkbashisms` but work fine (or have equivalents) in zsh:

- `[[ ]]` double brackets
- `local` keyword
- Arrays with `=()`
- `$(command)` substitution
- Here-strings `<<<`
- Process substitution `<()` and `>()`

## Notes

- Treat output as a reference for potential bash/zsh differences, not as errors.
- Most useful when migrating scripts from bash to zsh or writing scripts that should work in both.
