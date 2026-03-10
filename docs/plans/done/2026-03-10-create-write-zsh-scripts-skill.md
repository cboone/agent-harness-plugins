# Create write-zsh-scripts Skill

## Context

The repository has style guide skills for Bash (`write-shell-scripts`), Go (`write-go-code`), and Markdown (`write-markdown`), but none for zsh. Zsh has distinct conventions for scripting, parameter expansion, arrays, globbing, and a rich completion system that differ significantly from Bash. This skill will provide a comprehensive zsh style guide, drawing from the Oh My Zsh Code Style Guide, the upstream zsh completion-style-guide, the zsh development guide, Christopher Allen's zsh best practices gist, and the zsh.sourceforge.io documentation.

The user confirmed: plugin name `write-zsh-scripts`, with completions in a separate reference file.

Follow-up (out of scope): consider renaming `write-shell-scripts` to `write-bash-scripts` for consistency.

## Files to Create

### 1. `plugins/write-zsh-scripts/.claude-plugin/plugin.json`

Standard plugin manifest, version `1.0.0`, category `code-quality`:

```json
{
  "author": { "name": "Christopher Boone" },
  "description": "Applies zsh style conventions when creating or editing zsh scripts, configurations, and completions.",
  "homepage": "https://github.com/cboone/cboone-cc-plugins",
  "keywords": ["completions", "format", "scripts", "style", "zsh"],
  "license": "MIT",
  "name": "write-zsh-scripts",
  "repository": "https://github.com/cboone/cboone-cc-plugins",
  "skills": "./skills",
  "version": "1.0.0"
}
```

### 2. `plugins/write-zsh-scripts/skills/write-zsh-scripts/SKILL.md`

Frontmatter with trigger description, then summary of key conventions (following the `write-shell-scripts` SKILL.md pattern). Sections:

- **Key Conventions** summary with subsections: Script Structure, Naming, Syntax, Quoting, Variables and Scope, Zsh-Specific Features
- **Completions**: pointer to `./references/completions.md`
- **Validation**: how to check zsh scripts (zsh -n, shellcheck with `--shell=zsh` where supported, shfmt)

### 3. `plugins/write-zsh-scripts/skills/write-zsh-scripts/references/ZSH.md`

Comprehensive zsh scripting guide (~800-1000 lines), following BASH.md's format with navigation links at top, horizontal rule separators between subsections, and Use/Avoid tables. Sections:

1. **Basics**: shebang (`#!/usr/bin/env zsh`), strict mode (`setopt ERR_EXIT NO_UNSET PIPE_FAIL`), main function pattern, file extensions (`.zsh` for libraries, no extension for executables), dual-purpose detection via `ZSH_EVAL_CONTEXT`
1. **Syntax**: command substitution, variable expansion `${var}`, parameter expansion operators (`#`, `##`, `%`, `%%`, `/`, `//`), expansion flags (`(L)`, `(U)`, `(s)`, `(j)`, `(u)`, `(o)`, `(q)`, `(Q)`, `(P)`), arithmetic `((...))`, extended globbing (`setopt EXTENDED_GLOB`), glob qualifiers
1. **Naming**: functions (`snake_case`), local variables (`lower_case`), constants (`ALL_CAPS` with `readonly` or `typeset -r`), private functions/variables (`_prefix`)
1. **Functions**: preferred syntax (`function name() { }`), `local` for all function variables, autoloading (`autoload -Uz`), anonymous functions (`() { ... }`), hook functions (`chpwd`, `precmd`, `preexec`), TRAP functions (`TRAPINT`, `TRAPZERR`)
1. **Variables**: `typeset` over `declare`, explicit type flags (`-i`, `-a`, `-A`, `-r`, `-g`), arrays (1-based indexing), associative arrays, `setopt WARN_CREATE_GLOBAL`
1. **Scope**: `local` in functions, `typeset` implicit local scope in functions, subshell variable isolation, `(( ))` scope
1. **Quoting**: always quote expansions, `"${(@)array}"` for word-splitting in quoted context, `RC_QUOTES` option, single vs double quotes
1. **Tests**: `[[ ]]` over `[ ]`, pattern matching in `[[ ]]`, regex with `=~`, arithmetic tests with `(( ))`
1. **Control flow**: keyword placement (`then`/`do` on same line), case statements, exit codes, `pipestatus` array (zsh equivalent of bash `PIPESTATUS`)
1. **I/O**: stderr for errors, `mktemp` for temp files, process substitution (`<()`, `>()`, `=()`), heredocs
1. **Cleanup**: `trap` handlers, `TRAP*` functions, `always` blocks (`{ ... } always { ... }`)
1. **Security**: avoid `eval`, avoid `print -P` with untrusted input (escape `%` chars), validate external input, `mktemp` for secure temp files
1. **Performance**: prefer builtins over external commands, `zcompile` for startup-critical scripts, use arrays instead of string splitting
1. **Development**: syntax check with `zsh -n`, ShellCheck (limited zsh support), debug tracing with `setopt XTRACE`
1. **Sources**: attribution to all researched guides

### 4. `plugins/write-zsh-scripts/skills/write-zsh-scripts/references/completions.md`

Zsh completion function conventions (~400-500 lines), drawn primarily from the upstream `Etc/completion-style-guide`. Sections:

1. **Formatting**: 2-space indent, 4-space continuation, 79-char line limit, `then`/`do` on same line
1. **Prohibited syntax**: short loops, alternative conditionals, `foreach`, unusual tricks
1. **Descriptions**: no trailing periods, no initial capitals (except acronyms), imperative mood, units in parentheses, defaults in brackets, singular form
1. **Tags and context**: register tags before offering matches, make `curcontext` local, use `_description` for all descriptions, every `compadd` must include `"$expl[@]"`, pass sort flags to `_description` not `compadd`
1. **Helper functions**: when to use `_arguments`, `_values`, `_wanted`, `_requested`, `_alternative`, `_all_labels`
1. **Return values**: return zero if matches added, use `compstate[nmatches]`
1. **Caching**: `_store_cache` / `_retrieve_cache` pattern, `_cache_` prefix for globals
1. **Style lookups**: `zstyle -t`, `-b`, `-s`, `-a` flags, context string format

### 5. `plugins/write-zsh-scripts/README.md`

Standard plugin README following the write-shell-scripts pattern:

- Type: Skill, Trigger: `/write-zsh-scripts` (also activates automatically)
- Installation instructions
- What It Does section
- Usage and Examples
- See Also (link to write-shell-scripts, lint-and-fix)

## Files to Modify

### 6. `.claude-plugin/marketplace.json`

- Add `write-zsh-scripts` entry in alphabetical position (after `write-shell-scripts`)
- Bump `metadata.version` from `1.23.0` to `1.24.0` (new plugin added)

### 7. `README.md`

- Add `Write Zsh Scripts` to the Code Quality ToC section (after Write Shell Scripts): `\n∙ [Write Zsh Scripts](#write-zsh-scripts)`
- Add a description entry in the Code Quality skills section after Write Shell Scripts

### 8. `CLAUDE.md`

- Add `write-zsh-scripts/` directory tree under the plugins structure

## Verification

1. Validate JSON: `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))"` and same for plugin.json
1. Check version match: plugin.json version matches marketplace.json entry
1. Check alphabetical ordering in marketplace.json
1. Review ZSH.md for completeness against researched sources
1. Review completions.md against upstream completion-style-guide
1. Invoke `/write-zsh-scripts` to verify skill loads and summary is accurate
