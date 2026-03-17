# Zsh

## Tools

Seven complementary tools from the `check-zsh-scripts` skill, each targeting a different class of issue:

| Tool                          | Purpose                              | Zsh Support  | Auto-Fix |
| ----------------------------- | ------------------------------------ | ------------ | -------- |
| `zsh -n`                      | Syntax check (parse without execute) | Native       | No       |
| `zcompile`                    | Compile to wordcode                  | Native       | No       |
| `shellcheck --shell=bash`     | Static analysis                      | Limited      | No       |
| `checkbashisms`               | Identify bash-specific constructs    | Indirect     | No       |
| `shellharden --check`         | Safer syntax suggestions             | Limited      | Suggest  |
| `zsh -c 'setopt ...; source'` | Variable scope warnings              | Native       | No       |
| `shfmt -ln zsh`               | Shell formatter                      | Experimental | Yes      |

## Install

```bash
# Homebrew (recommended)
brew install shellcheck shfmt shellharden

# checkbashisms (from devscripts)
brew install devscripts
```

On Ubuntu CI, use `apt-get install devscripts` for checkbashisms, `cargo install --locked shellharden` for shellharden, and the `mfinelli/setup-shfmt@v4` action for shfmt. ShellCheck is pre-installed on `ubuntu-latest`.

## Config

### .shellcheckrc

For zsh projects, create a minimal `.shellcheckrc` in the project root. Bash-specific optional checks are omitted because they produce false positives on zsh code. The `--shell=bash --exclude=SC1090,SC2039,SC2154,SC2168,SC2296,SC2299` flags are handled per-invocation in the check script.

```ini
# Follow source directives for cross-file analysis
external-sources=true
```

For mixed bash/zsh projects, the bash-oriented optional checks from `shell.md` can remain in `.shellcheckrc` since they only fire on files ShellCheck identifies as bash (from the shebang). The zsh check script overrides with `--shell=bash` and its own `--exclude` list.

### .editorconfig

Add a zsh section with shfmt-specific properties:

```ini
[*.zsh]
indent_style = space
indent_size = 2
binary_next_line = true
space_redirects = true
switch_case_indent = true
```

Also add entries for dotfiles if the project includes them:

```ini
[.zshrc]
indent_style = space
indent_size = 2
binary_next_line = true
space_redirects = true
switch_case_indent = true

[.zshenv]
indent_style = space
indent_size = 2
binary_next_line = true
space_redirects = true
switch_case_indent = true
```

## Generated Scripts

When setting up zsh linting, generate these two scripts in the target project. They run the 7-tool pipeline as a single `make check-zsh` invocation.

### scripts/lib/find-zsh-files.zsh

File discovery helper sourced by the check script. Finds all zsh files by extension and shebang.

```zsh
#!/usr/bin/env zsh
# Find all zsh files in the project.
# Outputs one file path per line. Source this file to populate the ZSH_FILES array.

typeset -ga ZSH_FILES=()

# By extension
for f in **/*.zsh(.N); do
  ZSH_FILES+=("$f")
done

# Dotfiles
for name in .zshrc .zshenv .zprofile .zlogin .zlogout zshrc zshenv zprofile zlogin zlogout; do
  for f in **/${name}(.N); do
    ZSH_FILES+=("$f")
  done
done

# By shebang (files without .zsh extension)
for f in scripts/*(.N) bin/*(.N); do
  [[ -f "$f" ]] || continue
  # Skip files already found by extension
  (( ${ZSH_FILES[(Ie)$f]} )) && continue
  head -1 "$f" 2>/dev/null | grep -Eq '#!/usr/bin/env zsh|#!/bin/zsh' && ZSH_FILES+=("$f")
done

# Deduplicate
typeset -Ua ZSH_FILES
```

### scripts/check-zsh.zsh

Main check script. Runs each tool, collects results, and prints a summary.

```zsh
#!/usr/bin/env zsh
setopt ERR_EXIT NO_UNSET PIPE_FAIL

script_dir="${0:A:h}"
source "${script_dir}/lib/find-zsh-files.zsh"

if (( ${#ZSH_FILES} == 0 )); then
  print "No zsh files found."
  exit 0
fi

print "Checking ${#ZSH_FILES} zsh file(s)..."
print

typeset -i errors=0

# 1. Syntax check (zsh -n)
print "==> zsh -n (syntax check)"
for f in "${ZSH_FILES[@]}"; do
  if ! zsh -n "$f" 2>&1; then
    (( errors++ ))
  fi
done
print

# 2. Compile check (zcompile)
print "==> zcompile (compile check)"
for f in "${ZSH_FILES[@]}"; do
  if zsh -c 'zcompile "$1"' _ "$f" 2>&1; then
    rm -f "${f}.zwc"
  else
    (( errors++ ))
    rm -f "${f}.zwc"
  fi
done
print

# 3. shellcheck (static analysis, best-effort with --shell=bash)
if command -v shellcheck &>/dev/null; then
  print "==> shellcheck --shell=bash"
  for f in "${ZSH_FILES[@]}"; do
    if ! shellcheck --shell=bash --exclude=SC1090,SC2039,SC2154,SC2168,SC2296,SC2299 "$f" 2>&1; then
      (( errors++ ))
    fi
  done
else
  print "==> shellcheck: not installed (skipping)"
fi
print

# 4. checkbashisms
if command -v checkbashisms &>/dev/null; then
  print "==> checkbashisms"
  for f in "${ZSH_FILES[@]}"; do
    # checkbashisms output is informational for zsh; do not count as errors
    checkbashisms "$f" 2>&1 || true
  done
else
  print "==> checkbashisms: not installed (skipping)"
fi
print

# 5. shellharden (safety suggestions)
if command -v shellharden &>/dev/null; then
  print "==> shellharden --check"
  for f in "${ZSH_FILES[@]}"; do
    if ! shellharden --check "$f" 2>&1; then
      (( errors++ ))
    fi
  done
else
  print "==> shellharden: not installed (skipping)"
fi
print

# 6. setopt warnings (variable scoping)
# NOTE: This step sources (executes) each file. Set SKIP_SETOPT_CHECK=1 to disable.
if [[ "${SKIP_SETOPT_CHECK:-}" == "1" ]]; then
  print "==> setopt warnings: skipped (SKIP_SETOPT_CHECK=1)"
else
print "==> setopt warn_create_global/warn_nested_var"
for f in "${ZSH_FILES[@]}"; do
  # Skip config files that intentionally set globals
  case "${f:t}" in
    .zshrc|.zshenv|.zprofile|.zlogin|.zlogout|zshrc|zshenv|zprofile|zlogin|zlogout)
      print "  Skipping ${f} (config file, globals expected)"
      continue
      ;;
  esac
  zsh -c 'emulate -L zsh; setopt warn_create_global warn_nested_var; source "$1"' _ "$f" 2>&1 || true
done
fi
print

# 7. shfmt (formatting check)
# NOTE: shfmt -ln zsh is experimental. Parse failures on zsh-specific
# constructs are counted as errors, but the script continues checking
# remaining files.
if command -v shfmt &>/dev/null; then
  print "==> shfmt -ln zsh -d"
  for f in "${ZSH_FILES[@]}"; do
    if ! shfmt -ln zsh -d "$f" 2>&1; then
      (( errors++ ))
    fi
  done
else
  print "==> shfmt: not installed (skipping)"
fi
print

# Summary
if (( errors > 0 )); then
  print "Done. ${errors} check(s) failed."
  exit 1
else
  print "Done. All checks passed."
fi
```

## Commands

```bash
# Full check pipeline
./scripts/check-zsh.zsh

# Format only (all zsh files including dotfiles)
source scripts/lib/find-zsh-files.zsh && shfmt -ln zsh -w "${ZSH_FILES[@]}"

# Syntax check only
for f in **/*.zsh(.N); do zsh -n "$f"; done
```

## Makefile Targets

```makefile
.PHONY: check-zsh format-zsh

check-zsh: ## Run all zsh checks (7-tool pipeline)
	./scripts/check-zsh.zsh

format-zsh: ## Format zsh scripts (all zsh files including dotfiles)
	zsh -c 'source scripts/lib/find-zsh-files.zsh && shfmt -ln zsh -w "$${ZSH_FILES[@]}"'
```

## Notes

- **Cross-reference**: The `check-zsh-scripts` skill provides interactive checking with the same 7-tool pipeline. This reference generates the scripts so the pipeline runs in CI via `make check-zsh`.
- **shfmt experimental mode**: `shfmt -ln zsh` is experimental. If shfmt fails to parse a zsh-specific construct, the failure is counted as an error and the overall run will fail, but the script continues checking remaining files.
- **setopt side effects**: The setopt check **executes code** by sourcing files (it is not purely static analysis). The generated script skips config dotfiles that set globals by design. To disable this step (e.g., for projects where sourcing has unacceptable side effects), set `SKIP_SETOPT_CHECK=1` before running.
- **Mixed bash/zsh projects**: Both `shell.md` and `zsh.md` tool stacks can coexist. ShellCheck uses the shebang for `.sh` files and `--shell=bash` override for `.zsh` files. shfmt uses default dialect for `.sh` files and `-ln zsh` for `.zsh` files.
- **SC3xxx codes**: SC3000-series codes only fire with `--shell=sh`, not `--shell=bash`. Since the zsh check script uses `--shell=bash`, no SC3xxx filtering is needed.
