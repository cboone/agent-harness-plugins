# shellcheck (zsh scripts)

## Purpose

Static analysis for shell scripts. ShellCheck does not support `--shell=zsh`; `--shell=bash` is used as the closest approximation. Results require filtering for zsh false positives.

## Command

```bash
shellcheck --shell=bash --exclude=SC1090,SC2039,SC2154,SC2168,SC2296,SC2299 <file>
```

## Installation

```bash
brew install shellcheck
```

## SC Codes That Reliably Apply to Zsh

These checks target patterns that are genuinely problematic in zsh:

- **SC2086**: Double quote to prevent globbing and word splitting
- **SC2046**: Quote command substitution to prevent word splitting
- **SC2034**: Variable appears unused (verify it is not exported or used by a framework). May need project-specific exclusion for: zsh completion system variables (`PREFIX`, `SUFFIX`, `IPREFIX`, `ISUFFIX`), cross-file globals consumed in a different file, and indirect expansion via `${(P)var_name}`
- **SC2148**: Tips depend on target shell (missing shebang)
- **SC2059**: Don't use variables in printf format string
- **SC2162**: `read` without `-r` will mangle backslashes

## SC Codes That Commonly False-Positive on Zsh

These should be filtered or presented with a caveat:

- **SC2296, SC2299**: Zsh parameter expansion flags like `${(f)var}`, `${(k)assoc}`, `${(s.:.)var}`
- **SC2154**: Variables set by zsh frameworks (oh-my-zsh, prezto, zinit) or by `zstyle`
- **SC1090**: Cannot follow non-constant source (common with zsh plugin managers)
- **SC2039**: Zsh-specific features flagged as "not supported in sh"
- **SC3000-series**: Zsh features flagged as "not POSIX" (only fires with `--shell=sh`, not `--shell=bash`; no filtering needed when using `--shell=bash`)
- **SC2168**: `local` is only valid in functions (zsh allows `local` in anonymous functions and sourced contexts)

## Zsh Support Status

ShellCheck has no native zsh mode. When used with `--shell=bash` on zsh scripts, many checks assume bash semantics. The tool is most useful for catching quoting issues and unused variables, less useful for zsh-specific constructs.

## Guidance

- Present results with a note about limited zsh support.
- Filter the known false-positive SC codes listed above.
- If more than half the output is filtered, note this to the user and suggest focusing on native zsh tools (`zsh -n`, `zcompile`, `setopt` warnings).
