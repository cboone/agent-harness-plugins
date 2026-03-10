# Zsh Style Guide

[Basics](#basics) · [Syntax](#syntax) · [Naming](#naming) · [Functions](#functions) · [Variables](#variables) · [Scope](#scope) · [Quoting](#quoting) · [Arguments](#arguments) · [Tests](#tests) · [Control flow](#control-flow) · [I/O](#io) · [Cleanup](#cleanup) · [Security](#security) · [Performance](#performance) · [Development](#development)

---

## Basics

### Script header

Include filename, author, date, and purpose at the top of scripts.

```zsh
#!/usr/bin/env zsh
# script-name -- Brief description of purpose
# Author: Name
# Date: 2026-01-15
```

---

### Shebang

Use `#!/usr/bin/env zsh` for portability.

| Use                  | Avoid        |
| -------------------- | ------------ |
| `#!/usr/bin/env zsh` | `#!/bin/zsh` |
| `#!/usr/bin/env zsh` | `#!/bin/sh`  |

---

### Strict mode

Start scripts with `setopt` flags to catch errors early. Zsh uses option names instead of single-letter flags.

```zsh
setopt ERR_EXIT        # exit on command failure (like set -e)
setopt NO_UNSET        # error on undefined variables (like set -u)
setopt PIPE_FAIL       # catch failures in pipelines (like set -o pipefail)
```

The short-form equivalent `emulate -LR zsh` resets all options to zsh defaults and scopes them locally, which is useful in functions meant for distribution.

---

### Main function

Encapsulate script logic in a `main` function called at the end.

```zsh
function main() {
  # script logic here
}

main "${@}"
```

---

### Dual-purpose scripts

Use `ZSH_EVAL_CONTEXT` to detect if the script is being sourced or executed. This variable contains a colon-separated list of evaluation contexts.

```zsh
if [[ ${ZSH_EVAL_CONTEXT} == toplevel ]]; then
  main "${@}"
fi
```

| Use                                     | Avoid                      |
| --------------------------------------- | -------------------------- |
| `[[ ${ZSH_EVAL_CONTEXT} == toplevel ]]` | `[[ ${0} == ${(%):-%x} ]]` |

---

### File extensions

Use `.zsh` for sourced library files, configuration files, and plugin files. Use no extension for executable scripts.

| File type         | Extension | Example           |
| ----------------- | --------- | ----------------- |
| Executable script | none      | `deploy-project`  |
| Library / plugin  | `.zsh`    | `git-helpers.zsh` |
| Completion        | none      | `_my-command`     |
| Configuration     | `.zsh`    | `aliases.zsh`     |

---

## Syntax

### Command substitution

Use `$(...)`, not backticks. Supports nesting and clearer quoting.

| Use                 | Avoid                  |
| ------------------- | ---------------------- |
| `result=$(command)` | `` result=`command` `` |

---

### Variable expansion

Use `${var}`, not `$var`. Braces prevent ambiguity in concatenation.

| Use                  | Avoid              |
| -------------------- | ------------------ |
| `${filename}_backup` | `$filename_backup` |
| `${array[1]}`        | `$array[1]`        |

---

### Parameter expansion operators

Use parameter expansions instead of external commands for string operations.

| Operator            | Effect                       | Example                  |
| ------------------- | ---------------------------- | ------------------------ |
| `${var#pattern}`    | Remove shortest prefix match | `${path#*/}`             |
| `${var##pattern}`   | Remove longest prefix match  | `${path##*/}` (basename) |
| `${var%pattern}`    | Remove shortest suffix match | `${file%.*}` (strip ext) |
| `${var%%pattern}`   | Remove longest suffix match  | `${path%%/*}`            |
| `${var/pat/rep}`    | Replace first match          | `${str/old/new}`         |
| `${var//pat/rep}`   | Replace all matches          | `${str//old/new}`        |
| `${var:offset:len}` | Substring extraction         | `${str:0:5}`             |
| `${#var}`           | String length                | `${#filename}`           |

Nested expansions reduce temporary variables:

```zsh
# Extract filename without extension from a path
local name="${${path##*/}%.*}"
```

---

### Expansion flags

Zsh supports parameter expansion flags in the `${(flags)var}` syntax. Use these instead of external commands.

| Flag     | Effect                            | Example                    |
| -------- | --------------------------------- | -------------------------- |
| `(L)`    | Lowercase                         | `${(L)str}`                |
| `(U)`    | Uppercase                         | `${(U)str}`                |
| `(C)`    | Capitalize words                  | `${(C)str}`                |
| `(s:d:)` | Split on delimiter                | `${(s:/:)path}`            |
| `(j:d:)` | Join with delimiter               | `${(j:,:)array}`           |
| `(u)`    | Remove duplicates                 | `${(u)array}`              |
| `(o)`    | Sort ascending                    | `${(o)array}`              |
| `(O)`    | Sort descending                   | `${(O)array}`              |
| `(q)`    | Shell-safe quoting                | `${(q)str}`                |
| `(Q)`    | Remove one level of quoting       | `${(Q)str}`                |
| `(P)`    | Treat value as parameter name     | `${(P)name}` (indirection) |
| `(z)`    | Lexical word splitting            | `${(z)cmdline}`            |
| `(@)`    | Preserve array elements in quotes | `"${(@)array}"`            |

---

### Arithmetic

Use `((...))` for statements and `$((...))` for expressions.

| Use                           | Avoid                      |
| ----------------------------- | -------------------------- |
| `((i++))`                     | `let i++`                  |
| `$((x + 1))`                  | `expr ${x} + 1`            |
| `for ((i=1; i<=10; i++)); do` | `for i in $(seq 1 10); do` |

Zsh arithmetic supports floating-point when using `zmodload zsh/mathfunc`.

---

### Extended globbing

Enable extended globbing for powerful pattern matching.

```zsh
setopt EXTENDED_GLOB
```

| Pattern          | Matches                                      |
| ---------------- | -------------------------------------------- |
| `**/*.zsh`       | Recursive match                              |
| `*.txt~README*`  | All `.txt` except those starting with README |
| `^*.log`         | Everything except `.log` files               |
| `file<1-10>.txt` | `file1.txt` through `file10.txt`             |
| `*(#i)readme*`   | Case-insensitive match                       |

---

### Glob qualifiers

Glob qualifiers filter matches by file attributes. Append them in parentheses after a glob pattern.

| Qualifier | Selects                          | Example                   |
| --------- | -------------------------------- | ------------------------- |
| `(.)`     | Regular files only               | `*(.)`                    |
| `(/)`     | Directories only                 | `*(/)`                    |
| `(@)`     | Symbolic links                   | `*(@)`                    |
| `(*)`     | Executable files                 | `*(*)`                    |
| `(m-N)`   | Modified within last N days      | `*(m-1)` (modified today) |
| `(om)`    | Sort by modification time        | `*(om)` (newest first)    |
| `(On)`    | Reverse sort by name             | `*(On)`                   |
| `(N)`     | Null glob (no error if no match) | `*.txt(N)`                |
| `(D)`     | Include dotfiles                 | `*(D)`                    |
| `([1])`   | First match only                 | `*(om[1])` (newest file)  |

Use `(N)` when a glob may match nothing, to avoid "no matches found" errors:

```zsh
for file in *.log(N); do
  process "${file}"
done
```

---

### Command existence

Use `command -v`, not `which`. `which` is not POSIX and behaves inconsistently across systems.

| Use              | Avoid       |
| ---------------- | ----------- |
| `command -v git` | `which git` |

In zsh, `(( ${+commands[git]} ))` is an alternative that checks the command hash table directly.

---

### Keyword placement

Place `then` and `do` on the same line as `if`, `for`, and `while`.

| Use                  | Avoid                    |
| -------------------- | ------------------------ |
| `if [[ ... ]]; then` | `if [[ ... ]]`<br>`then` |
| `for x in ...; do`   | `for x in ...`<br>`do`   |

---

### Heredoc quoting

Quote heredoc tags to prevent variable interpolation.

| Use       | Avoid   |
| --------- | ------- |
| `<<'EOF'` | `<<EOF` |

---

## Naming

### Function naming

Use `snake_case` for function names.

| Use              | Avoid          |
| ---------------- | -------------- |
| `get_user_input` | `GetUserInput` |
| `process_file`   | `processFile`  |

---

### Variable naming

Use `ALL_CAPS` for globals and exported variables, `lower_case` for locals.

| Use                   | Avoid                 |
| --------------------- | --------------------- |
| `local file_path`     | `local FILE_PATH`     |
| `readonly CONFIG_DIR` | `readonly config_dir` |

---

### Private naming

Prefix private or internal functions and variables with an underscore. This convention is standard in zsh plugins and completion functions.

| Use            | Avoid                    |
| -------------- | ------------------------ |
| `_helper_func` | `helper_func` (internal) |
| `_cache_data`  | `cache_data` (internal)  |

Note: this differs from the Bash convention where underscores are reserved for system use. In the zsh ecosystem, underscore prefixes are the established convention for private/internal identifiers, especially for completion functions.

---

### Descriptive names

Use descriptive variable names, not abbreviations.

| Use            | Avoid |
| -------------- | ----- |
| `file_listing` | `fl`  |
| `user_count`   | `uc`  |

---

### Magic numbers

Replace magic numbers with named constants.

| Use                                           | Avoid      |
| --------------------------------------------- | ---------- |
| `readonly TIMEOUT=30`<br>`sleep "${TIMEOUT}"` | `sleep 30` |

---

### Error code constants

Prefix error code constants with `E_`.

```zsh
readonly E_NOTFOUND=65
readonly E_PERMISSION=77
```

---

## Functions

### Function syntax

Use `function name() { }` with both the keyword and parentheses, matching the Bash style guide.

| Use                      | Avoid                  |
| ------------------------ | ---------------------- |
| `function my_func() { }` | `my_func() { }`        |
| `function my_func() { }` | `function my_func { }` |

---

### Local variables

Declare function variables with `local` to avoid polluting global scope.

| Use                  | Avoid          |
| -------------------- | -------------- |
| `local name="value"` | `name="value"` |

---

### Argument declaration

Assign positional parameters to named local variables at the top.

```zsh
function process_file() {
  local input_file="${1}"
  local output_file="${2}"
  # ...
}
```

---

### Autoloading

Use `autoload -Uz` for functions that should be loaded on first use. The `-U` flag suppresses alias expansion during loading, and `-z` forces zsh-style word splitting.

```zsh
autoload -Uz my_function
```

Place autoloaded function files in a directory on `fpath`. Each file contains the function body without the surrounding `function name() { ... }` wrapper.

---

### Anonymous functions

Anonymous functions execute immediately at the point of definition. Use them for one-time initialization that needs local scope.

```zsh
() {
  local temp_var="temporary"
  # initialization code
  # temp_var is not visible outside
}
```

---

### Hook functions

Zsh provides built-in hook functions that run at specific points. Use `add-zsh-hook` to register them safely (avoids overwriting existing hooks).

```zsh
autoload -Uz add-zsh-hook

function _update_title() {
  print -Pn "\e]0;%~\a"
}
add-zsh-hook precmd _update_title
```

| Hook       | When it runs                        |
| ---------- | ----------------------------------- |
| `chpwd`    | After the working directory changes |
| `precmd`   | Before each prompt                  |
| `preexec`  | Before each command execution       |
| `periodic` | Every `PERIOD` seconds              |
| `zshexit`  | When the shell exits                |

---

### TRAP functions

Zsh supports named trap functions as an alternative to the `trap` builtin.

```zsh
function TRAPINT() {
  print "Caught SIGINT"
  return $((128 + $1))
}
```

| Function    | Signal                                            |
| ----------- | ------------------------------------------------- |
| `TRAPINT`   | SIGINT                                            |
| `TRAPTERM`  | SIGTERM                                           |
| `TRAPEXIT`  | EXIT                                              |
| `TRAPZERR`  | Non-zero exit (like `ERR_EXIT` but as a function) |
| `TRAPDEBUG` | Before each command                               |

---

### Functions over aliases

Prefer functions over aliases for reusable commands. Functions accept arguments and support local variables.

```zsh
# Use
function ll() {
  ls -la "${@}"
}

# Avoid
alias ll='ls -la'
```

---

## Variables

### typeset over declare

Use `typeset` for explicit variable declarations. It is the native zsh builtin; `declare` is a bash compatibility alias.

| Use                | Avoid              |
| ------------------ | ------------------ |
| `typeset -i count` | `declare -i count` |

---

### Type flags

Use `typeset` flags for explicit typing.

| Flag | Purpose              | Example                            |
| ---- | -------------------- | ---------------------------------- |
| `-i` | Integer              | `typeset -i count=0`               |
| `-a` | Indexed array        | `typeset -a items=(one two three)` |
| `-A` | Associative array    | `typeset -A config=([key]=value)`  |
| `-r` | Read-only            | `typeset -r CONSTANT="value"`      |
| `-g` | Global (inside func) | `typeset -g GLOBAL_VAR="value"`    |
| `-x` | Export               | `typeset -x PATH`                  |

Flags combine: `typeset -ri MAX_RETRIES=3` creates a read-only integer.

---

### Arrays

Zsh arrays use 1-based indexing by default. This is a key difference from Bash.

```zsh
typeset -a fruits=(apple banana cherry)

echo "${fruits[1]}"      # "apple" (not fruits[0])
echo "${fruits[-1]}"     # "cherry" (negative indexing works)
echo "${#fruits[@]}"     # 3 (array length)
echo "${fruits[@]}"      # all elements
```

| Operation        | Syntax                     |
| ---------------- | -------------------------- |
| Access element   | `${array[1]}`              |
| All elements     | `${array[@]}`              |
| Length           | `${#array[@]}`             |
| Append           | `array+=(new_item)`        |
| Slice            | `${array[2,4]}`            |
| Delete element   | `array[2]=()`              |
| Check membership | `(( ${array[(Ie)item]} ))` |

---

### Associative arrays

Declare associative arrays with `typeset -A`.

```zsh
typeset -A config=(
  [host]="localhost"
  [port]="8080"
  [debug]="true"
)

echo "${config[host]}"           # "localhost"
echo "${(k)config}"              # all keys
echo "${(v)config}"              # all values
echo "${(kv)config}"             # keys and values interleaved
```

---

### Declaration and assignment

Separate `local` declaration from command substitution to preserve exit codes. `local` always returns 0, masking command failures.

| Use                         | Avoid              |
| --------------------------- | ------------------ |
| `local var`<br>`var=$(cmd)` | `local var=$(cmd)` |

---

### Constants

Declare constants with `readonly` or `typeset -r`.

| Use                      | Avoid           |
| ------------------------ | --------------- |
| `readonly MAX_RETRIES=3` | `MAX_RETRIES=3` |

---

### Warn on accidental globals

Enable `WARN_CREATE_GLOBAL` to catch accidental global variable creation inside functions.

```zsh
setopt WARN_CREATE_GLOBAL
```

This helps find missing `local` declarations during development.

---

## Scope

### Local variables in functions

Variables declared with `local` or `typeset` inside a function are scoped to that function. Always use `local` for function variables.

```zsh
function process() {
  local result=""    # scoped to this function
  result=$(compute)
  echo "${result}"
}
```

---

### typeset implicit scoping

Variables created with `typeset` inside functions are automatically local (without needing the `-g` flag). This is a difference from Bash's `declare`.

```zsh
function example() {
  typeset counter=0    # automatically local
  typeset -g shared=0  # explicitly global
}
```

---

### Subshell variable scope

Variables modified inside pipelines or subshells don't affect the parent scope.

```zsh
count=0
echo "a b c" | while read -r word; do
  ((count++))  # modified in subshell
done
echo "${count}"  # still 0
```

Use process substitution instead:

```zsh
# Use: process substitution avoids subshell
while read -r word; do
  ((count++))
done < <(echo "a b c" | tr ' ' '\n')
```

---

### Temporary directory changes

Use a subshell for temporary `cd` to avoid affecting the parent shell.

| Use                      | Avoid                              |
| ------------------------ | ---------------------------------- |
| `(cd /some/dir && make)` | `cd /some/dir`<br>`make`<br>`cd -` |

---

## Quoting

### Quote expansions

Always quote variable and command expansions.

| Use             | Avoid         |
| --------------- | ------------- |
| `"${variable}"` | `${variable}` |
| `"$(command)"`  | `$(command)`  |

Note: zsh does not perform word splitting on unquoted parameter expansions by default (unlike Bash). However, always quoting is still best practice because it protects against glob expansion and makes intent clear.

---

### Array expansion in quotes

Use the `(@)` flag to preserve array elements as separate words inside double quotes.

| Use             | Effect                          |
| --------------- | ------------------------------- |
| `"${(@)array}"` | Each element stays separate     |
| `"${array[@]}"` | Same effect in zsh              |
| `"${array[*]}"` | All elements joined as one word |

---

### RC_QUOTES option

Enable `RC_QUOTES` to allow `''` inside single-quoted strings instead of breaking out.

```zsh
setopt RC_QUOTES

echo 'It''s a test'  # prints: It's a test
```

Without `RC_QUOTES`, you must break the string:

```zsh
echo 'It'\''s a test'
```

---

### Single quotes

Prefer single quotes over backslash escaping for literal strings.

| Use             | Avoid          |
| --------------- | -------------- |
| `'Hello World'` | `Hello\ World` |

---

### Arrays over splitting

Use arrays instead of relying on word splitting for lists.

```zsh
# Use
files=("file one.txt" "file two.txt")
cp "${files[@]}" dest/

# Avoid
files="file one.txt file two.txt"
cp ${files} dest/
```

---

## Arguments

### Long options

Prefer long options for readability in scripts.

| Use                   | Avoid |
| --------------------- | ----- |
| `--recursive --force` | `-rf` |

---

### Parameter validation

Validate required parameters at the script level, not inside every function.

```zsh
function main() {
  if [[ -z "${1:-}" ]]; then
    echo "Usage: ${0} <file>" >&2
    exit 1
  fi
  process_file "${1}"
}
```

---

### Argument arrays

Build command arguments in arrays to handle quoting safely.

```zsh
typeset -a args=()
args+=(--flag)
args+=(--option "value")
command "${args[@]}"
```

---

## Tests

### Double brackets

Use `[[ ]]`, not `[ ]`. Double brackets support pattern matching, regex, and safer syntax.

| Use                  | Avoid              |
| -------------------- | ------------------ |
| `[[ -f "${file}" ]]` | `[ -f "${file}" ]` |

---

### Pattern matching

Inside `[[ ]]`, the `==` operator supports glob patterns on the right-hand side. Quote the RHS to match literally.

```zsh
# Pattern match (unquoted RHS)
[[ ${filename} == *.txt ]]

# Literal match (quoted RHS)
[[ ${filename} == "${expected}" ]]
```

---

### Regex matching

Use `=~` for regex matching inside `[[ ]]`. Capture groups are available in the `match` array (or `BASH_REMATCH` with `RE_MATCH_PCRE`).

```zsh
if [[ ${version} =~ '^([0-9]+)\.([0-9]+)' ]]; then
  echo "Major: ${match[1]}, Minor: ${match[2]}"
fi
```

---

### Explicit string tests

Use explicit `-n` and `-z` tests for string checks.

| Use                 | Avoid              |
| ------------------- | ------------------ |
| `[[ -n "${var}" ]]` | `[[ "${var}" ]]`   |
| `[[ -z "${var}" ]]` | `[[ ! "${var}" ]]` |

---

### Equality operator

Use `==` for equality, not `=`.

| Use                         | Avoid                      |
| --------------------------- | -------------------------- |
| `[[ "${var}" == "value" ]]` | `[[ "${var}" = "value" ]]` |

---

### Exit code tests

Test command exit codes directly instead of capturing output.

| Use                               | Avoid                                   |
| --------------------------------- | --------------------------------------- |
| `if grep -q 'pattern' file; then` | `if [[ $(grep 'pattern' file) ]]; then` |

---

### Arithmetic tests

Use `(( ))` for numeric comparisons.

| Use               | Avoid                   |
| ----------------- | ----------------------- |
| `(( count > 0 ))` | `[[ ${count} -gt 0 ]]`  |
| `(( ${#array} ))` | `[[ ${#array} -gt 0 ]]` |

---

## Control flow

### Default case

Always include a default `*)` case in `case` statements.

```zsh
case "${action}" in
  start) start_service ;;
  stop) stop_service ;;
  *)
    echo "Unknown action: ${action}" >&2
    exit 1
    ;;
esac
```

---

### Negated conditions

Avoid `if ! condition` with an else branch; invert the logic instead.

```zsh
# Use
if is_valid; then
  handle_valid
else
  handle_invalid
fi

# Avoid
if ! is_valid; then
  handle_invalid
else
  handle_valid
fi
```

---

### Simple conditionals

Use `&&`/`||` for simple one-line conditionals.

| Use                                | Avoid                                        |
| ---------------------------------- | -------------------------------------------- |
| `[[ -f "${f}" ]] && source "${f}"` | `if [[ -f "${f}" ]]; then source "${f}"; fi` |

---

### Intentional failures

Use `|| true` to allow commands to fail without triggering `ERR_EXIT`.

| Use                                   | Avoid               |
| ------------------------------------- | ------------------- |
| `grep pattern file &#124;&#124; true` | `grep pattern file` |

---

### Check return values

Always check command return values with `$?` or `if`.

```zsh
if ! cp source dest; then
  echo "Copy failed" >&2
  exit 1
fi
```

---

### Pipeline status

Use `pipestatus` (lowercase, no `$` prefix) to check the exit code of each command in a pipeline. This is the zsh equivalent of Bash's `PIPESTATUS`.

```zsh
cmd1 | cmd2 | cmd3
echo "${pipestatus[@]}"  # e.g., "0 1 0"
```

| Zsh                | Bash               |
| ------------------ | ------------------ |
| `${pipestatus[@]}` | `${PIPESTATUS[@]}` |

---

### Meaningful exit codes

Return distinct exit codes for different failure modes.

```zsh
readonly E_SUCCESS=0
readonly E_INVALID_ARGS=1
readonly E_FILE_NOT_FOUND=2
readonly E_PERMISSION_DENIED=3
```

---

## I/O

### Error messages

Send error messages to stderr.

| Use                | Avoid          |
| ------------------ | -------------- |
| `echo "error" >&2` | `echo "error"` |

---

### Stdout for data

Reserve stdout for machine-parsable output; use stderr for human messages.

```zsh
function get_users() {
  echo "Fetching users..." >&2  # progress to stderr
  cut -d: -f1 /etc/passwd       # data to stdout
}
```

---

### Temporary files

Use `mktemp` to create temporary files securely.

| Use             | Avoid                |
| --------------- | -------------------- |
| `tmp=$(mktemp)` | `tmp=/tmp/myfile.$$` |

---

### Process substitution

Zsh supports three forms of process substitution:

| Form      | Behavior                                       |
| --------- | ---------------------------------------------- |
| `<(list)` | Provides command output as a file descriptor   |
| `>(list)` | Sends output to a command                      |
| `=(list)` | Creates a temporary file containing the output |

The `=(...)` form is unique to zsh and useful when a command needs a real file path, not a file descriptor:

```zsh
# diff needs seekable files; =(…) provides them
diff =(sort file1) =(sort file2)
```

---

### Heredocs

Quote heredoc tags to prevent variable interpolation. Use descriptive tags.

| Use             | Avoid     |
| --------------- | --------- |
| `<<'SQL_QUERY'` | `<<'EOF'` |
| `<<'CONFIG'`    | `<<EOF`   |

---

### Direct file input

Pass files directly to commands or use redirection.

| Use                   | Avoid                          |
| --------------------- | ------------------------------ |
| `grep pattern < file` | `cat file &#124; grep pattern` |
| `grep pattern file`   | `cat file &#124; grep pattern` |

---

### Line-by-line reading

Use `while read` to iterate over lines.

| Use                           | Avoid                         |
| ----------------------------- | ----------------------------- |
| `while IFS= read -r line; do` | `for line in $(cat file); do` |

---

## Cleanup

### Exit trap

Use `trap` or a `TRAPEXIT` function to run cleanup code on exit.

```zsh
function cleanup() {
  rm -f "${tmp_file}"
}
trap cleanup EXIT
```

Or using the named function form:

```zsh
function TRAPEXIT() {
  rm -f "${tmp_file}"
}
```

---

### Always blocks

Zsh supports `always` blocks that run regardless of errors, similar to `try/finally`.

```zsh
{
  # code that might fail
  risky_operation
} always {
  # always runs, even if the try block fails
  rm -f "${tmp_file}"
}
```

The `TRY_BLOCK_ERROR` variable is set to a non-zero value if the try block failed. Reset it to 0 to prevent the error from propagating.

---

### Preserve exit code

Save the exit code at the start of trap handlers to preserve it.

```zsh
function cleanup() {
  local exit_code="${?}"
  rm -f "${tmp_file}"
  exit "${exit_code}"
}
```

---

### Restore options

Use `emulate -L zsh` in functions to scope option changes locally.

```zsh
function my_function() {
  emulate -L zsh
  setopt EXTENDED_GLOB  # only affects this function
  # ...
}
```

---

## Security

### Avoid eval

Never use `eval`. It introduces code injection risks and makes debugging difficult.

```zsh
# Use: safe alternative with arrays
typeset -a files=("${user_input}")
ls "${files[@]}"

# Avoid: allows command injection
eval "ls ${user_input}"
```

---

### Avoid print -P with untrusted input

`print -P` performs prompt expansion, which can execute embedded commands. Never use it with untrusted content.

```zsh
# Use: escape % characters in untrusted content
local safe="${untrusted//\%/%%}"
print -P "${safe}"

# Avoid: prompt expansion on untrusted input
print -P "${untrusted}"
```

---

### Validate external input

Validate and sanitize all input from external sources.

```zsh
# Validate: ensure input is a number
if [[ ! ${input} =~ '^[0-9]+$' ]]; then
  echo "Invalid input: expected a number" >&2
  return 1
fi
```

---

### Secure temporary files

Use `mktemp` and set restrictive permissions.

```zsh
local tmp
tmp=$(mktemp)
chmod 600 "${tmp}"
trap "rm -f '${tmp}'" EXIT
```

---

### SUID/SGID prohibition

Never use SUID/SGID on shell scripts; use `sudo` for privilege escalation.

---

## Performance

### Prefer builtins over external commands

Zsh has many builtins that replace common external commands. Avoid spawning subprocesses for operations zsh handles natively.

| Use (builtin)           | Avoid (external)           |
| ----------------------- | -------------------------- |
| `${var//old/new}`       | `echo "${var}" &#124; sed` |
| `${(L)var}`             | `echo "${var}" &#124; tr`  |
| `${var##*/}`            | `basename "${var}"`        |
| `${var%/*}`             | `dirname "${var}"`         |
| `print -r -- "${text}"` | `echo "${text}"`           |
| `(( count++ ))`         | `count=$(expr ${count}+1)` |

---

### zcompile for startup

Pre-compile frequently sourced files with `zcompile` to reduce startup time.

```zsh
zcompile "${HOME}/.zshrc"
```

Compiled `.zwc` files load faster than text files. Zsh automatically uses the compiled version if it exists and is newer than the source.

---

### Avoid unnecessary subshells

Each `$(...)` creates a subshell. Use parameter expansion or builtins when possible.

```zsh
# Use: builtin parameter expansion
local ext="${filename##*.}"

# Avoid: subshell for simple operations
local ext=$(echo "${filename}" | awk -F. '{print $NF}')
```

---

### Use arrays for data

Use arrays instead of string manipulation with `cut`, `awk`, or `tr`.

```zsh
# Use: split once, access elements
typeset -a parts=("${(@s:/:)path}")
echo "${parts[1]}"

# Avoid: repeated external calls
echo "${path}" | cut -d/ -f1
```

---

## Development

### Syntax check

Validate syntax before running.

```zsh
zsh -n script.zsh
```

---

### Debug tracing

Support optional debug tracing with a `TRACE` environment variable.

```zsh
[[ -n "${TRACE:-}" ]] && setopt XTRACE
```

---

### Static analysis

ShellCheck has limited zsh support. Run it with `--shell=bash` for scripts that use mostly POSIX-compatible constructs, but be aware that zsh-specific syntax will produce false positives.

For zsh-specific linting, consider:

- `zsh -n` for syntax validation
- `zsh -o NO_EXEC` as an alternative syntax check

---

### Code comments

Comment non-obvious code to explain intent.

```zsh
# Strip ANSI color codes from output before logging
clean_output="${output//\x1b\[[0-9;]*m/}"
```

---

### Function documentation

Document functions with their purpose, arguments, outputs, and return values.

```zsh
# Compress and archive log files older than N days.
# Arguments:
#   $1 - Directory containing log files
#   $2 - Age threshold in days (default: 30)
# Outputs:
#   Writes archive path to stdout
# Returns:
#   0 on success, 1 on invalid arguments, 2 on compression failure
function archive_logs() {
  # ...
}
```

---

## Sources

Compiled by [Christopher Boone](https://cboone.github.io). Based on some of each of the following:

- [Oh My Zsh Code Style Guide](https://github.com/ohmyzsh/ohmyzsh/wiki/Code-Style-Guide)
- [Zsh Opinionated Best Practices](https://gist.github.com/ChristopherA/562c2e62d01cf60458c5fa87df046fbd) -- Christopher Allen
- [Zsh User's Guide](https://zsh.sourceforge.io/Guide/) -- Peter Stephenson
- [Zsh Completion Style Guide](https://github.com/zsh-users/zsh/blob/master/Etc/completion-style-guide)
- [Zsh Development Guide](https://github.com/zsh-users/zsh/blob/master/Etc/zsh-development-guide)
- [Zsh Manual](https://zsh.sourceforge.io/Doc/Release/)
- [Oh My Zsh Secure Code Guidelines](https://github.com/ohmyzsh/ohmyzsh/wiki/Secure-Code)
