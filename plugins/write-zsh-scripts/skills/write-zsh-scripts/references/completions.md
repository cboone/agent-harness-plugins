# Zsh Completion Function Conventions

[Formatting](#formatting) · [Prohibited syntax](#prohibited-syntax) · [Descriptions](#descriptions) · [Tags and context](#tags-and-context) · [Helper functions](#helper-functions) · [Return values](#return-values) · [Caching](#caching) · [Style lookups](#style-lookups)

These conventions are drawn from the upstream [zsh completion-style-guide](https://github.com/zsh-users/zsh/blob/master/Etc/completion-style-guide) and completion system documentation.

---

## Formatting

### Indentation

Use 2-space indentation. Use 4 spaces for continuation lines.

```zsh
_my_command() {
  local curcontext="${curcontext}" state line
  typeset -A opt_args

  _arguments -C \
      '1:command:->cmds' \
      '*::arg:->args'
}
```

---

### Line length

Maximum line length is 79 characters. Exception: long `_arguments` specification strings may exceed this when breaking them would reduce readability.

---

### Keyword placement

Place `then` and `do` on the same line, after a semicolon.

| Use                  | Avoid                    |
| -------------------- | ------------------------ |
| `if [[ ... ]]; then` | `if [[ ... ]]`<br>`then` |
| `for x in ...; do`   | `for x in ...`<br>`do`   |

---

### Function declaration

Completion functions use the bare name form without the `function` keyword, following upstream zsh convention. The function name starts with `_`.

```zsh
_my_command() {
  # ...
}
```

This differs from the general scripting convention. Completion functions follow the upstream zsh project's style, where `_name() { }` is the standard form.

---

## Prohibited syntax

Never use these constructs in completion functions. They work in zsh but are considered non-standard or obscure.

| Prohibited form            | Use instead                       |
| -------------------------- | --------------------------------- |
| `for x in $y; myfunc $x`   | `for x in $y; do myfunc $x; done` |
| `if { [[ ... ]] } { ... }` | `if [[ ... ]]; then ... fi`       |
| `foreach x (...) ... end`  | `for x in ...; do ... done`       |
| `() for 1 { ... } $x`      | Standard `for` loop               |

---

## Descriptions

Descriptions appear in completion menus and help text. Follow these rules consistently.

### Capitalization and punctuation

- No trailing periods
- No initial capital letters (except acronyms that are always uppercase)

| Use                        | Avoid                       |
| -------------------------- | --------------------------- |
| `'recurse subdirectories'` | `'Recurse subdirectories.'` |
| `'enable TLS encryption'`  | `'Enable TLS Encryption.'`  |

---

### Mood

Use imperative mood (command form), not indicative.

| Use                        | Avoid                       |
| -------------------------- | --------------------------- |
| `'recurse subdirectories'` | `'recurses subdirectories'` |
| `'set output format'`      | `'sets output format'`      |

---

### Option values

When an option takes a value, describe the action rather than naming the placeholder.

| Use                              | Avoid                       |
| -------------------------------- | --------------------------- |
| `'use specified input encoding'` | `'use input encoding NAME'` |
| `'connect to specified host'`    | `'connect to HOST'`         |

---

### Units and defaults

Put units in parentheses in group descriptions. Put defaults in brackets.

```zsh
'--timeout[set request timeout (ms)]:timeout (ms) [5000]:'
'--retries[set retry count]:count [3]:'
```

---

### Singular form

Use singular form when describing what is being completed (one item at a time).

| Use           | Avoid          |
| ------------- | -------------- |
| `'file'`      | `'files'`      |
| `'user name'` | `'user names'` |

---

### State action descriptions

Omit descriptions for `->state` actions. The state name itself is the documentation.

```zsh
# Use
'1:command:->cmds'

# Avoid
'1:command (select a subcommand):->cmds'
```

---

## Tags and context

### Register tags before use

Always register tags with `_tags` or use a helper function (`_wanted`, `_requested`, `_alternative`) before offering matches. This lets users configure which completions they see via `zstyle`.

```zsh
_tags files directories
while _tags; do
  _requested files && _files
  _requested directories && _path_files -/
done
```

---

### Make curcontext local

When a function uses `_arguments` with `-C`, make `curcontext` local.

```zsh
_my_command() {
  local curcontext="${curcontext}" state line
  typeset -A opt_args

  _arguments -C \
      '1:command:->cmds' \
      '*::arg:->args'
}
```

---

### Use \_description for descriptions

Generate completion group descriptions with `_description`. Never pass description text directly to `compadd`.

```zsh
local expl
_description files expl 'source file'
compadd "${expl[@]}" -- "${files[@]}"
```

---

### Always include expl in compadd

Every `compadd` call must include `"${expl[@]}"` (or the equivalent from `_description`). This carries the group name, description, and sorting flags.

```zsh
# Correct
_description users expl 'user name'
compadd "${expl[@]}" -- "${users[@]}"

# Wrong: missing expl
compadd -- "${users[@]}"
```

---

### Sort flags go to \_description

Pass `-1V` (unsorted unique) or `-2J` (sorted group) flags to `_description`, not to `compadd`. The `_description` function embeds them in the `expl` array.

```zsh
# Correct
_description -V users expl 'user name'
compadd "${expl[@]}" -- "${users[@]}"

# Wrong: sort flag on compadd
_description users expl 'user name'
compadd -V users "${expl[@]}" -- "${users[@]}"
```

---

### Tag naming

Choose simple, short, plural tag names. Reuse existing tags from the completion system when they apply.

Common existing tags:

| Tag           | Used for             |
| ------------- | -------------------- |
| `files`       | Regular files        |
| `directories` | Directories          |
| `commands`    | Executable commands  |
| `options`     | Command-line options |
| `users`       | User names           |
| `hosts`       | Host names           |
| `processes`   | Process IDs or names |
| `urls`        | URLs                 |

---

## Helper functions

Use existing helper functions instead of building ad hoc completion logic.

### \_arguments

The primary function for parsing command-line options and arguments. Handles option specs, mutually exclusive groups, and subcommand dispatch.

```zsh
_arguments \
    '-v[verbose output]' \
    '-o+[output file]:file:_files' \
    '(-q -v)'{-q,--quiet}'[suppress output]' \
    '1:input file:_files' \
    '*:extra files:_files'
```

---

### \_values

Complete a list of values, optionally with sub-arguments. Useful for comma-separated value lists.

```zsh
_values 'log level' \
    'debug[show debug messages]' \
    'info[show info messages]' \
    'warn[show warnings only]' \
    'error[show errors only]'
```

---

### \_wanted

Test whether a tag is wanted and, if so, call a completion function. Combines `_tags`, `_requested`, and `_all_labels` in one call.

```zsh
_wanted users expl 'user name' compadd -- "${users[@]}"
```

---

### \_requested

Test if a tag is in the current tag set. Use when you need to check a tag without immediately adding completions.

```zsh
if _requested hosts; then
  # expensive host lookup
  typeset -a hosts=($(get_hosts))
  _wanted hosts expl 'host name' compadd -- "${hosts[@]}"
fi
```

---

### \_alternative

Loop over multiple tag sets automatically. Each argument specifies a tag, description, and action.

```zsh
_alternative \
    'users:user name:_users' \
    'hosts:host name:_hosts' \
    'files:file:_files'
```

---

### \_all_labels

Loop over tag labels, calling a completion function for each. Used after `_tags` or `_requested` for manual control.

```zsh
_tags users hosts
while _tags; do
  while _next_label users expl 'user name'; do
    compadd "${expl[@]}" -- "${users[@]}"
  done
  while _next_label hosts expl 'host name'; do
    compadd "${expl[@]}" -- "${hosts[@]}"
  done
done
```

---

## Return values

### Return zero on success

Return zero if the function added any matches. Return non-zero if no matches were added.

```zsh
_my_command() {
  local -a matches=(one two three)
  compadd -- "${matches[@]}" && return 0
  return 1
}
```

---

### Check nmatches

When you need to know whether previous completion calls added matches, check `compstate[nmatches]`.

```zsh
local start_matches="${compstate[nmatches]}"
_files
if (( compstate[nmatches] > start_matches )); then
  # files were added
fi
```

---

## Caching

### Persistent cache

Use `_store_cache` and `_retrieve_cache` for expensive computations that should persist across sessions.

```zsh
_my_packages() {
  local cache_id="my_packages"
  typeset -a packages

  if ! _retrieve_cache "${cache_id}"; then
    packages=($(expensive_package_list))
    _store_cache "${cache_id}" packages
  fi

  _wanted packages expl 'package' compadd -- "${packages[@]}"
}
```

---

### In-memory cache

For data that should persist within a session but not across sessions, use global variables with a `_cache_` prefix.

```zsh
if [[ -z "${_cache_my_data}" ]]; then
  _cache_my_data=($(compute_data))
fi
```

---

### Cache invalidation

Consider whether style-dependent contexts or changing system state affect cache validity. Invalidate caches when the underlying data may have changed.

---

## Style lookups

### zstyle context format

The full context string for completion styles follows this format:

```text
:completion:FUNCTION:COMPLETER:COMMAND:ARGUMENT:TAG
```

Each field narrows the scope. Users configure styles with patterns like:

```zsh
zstyle ':completion:*:descriptions' format '%B%d%b'
zstyle ':completion:*:*:kill:*' menu yes select
```

---

### Testing styles

Use `zstyle -t` for boolean style tests. It returns zero if the style value is `yes`, `true`, `on`, or `1`.

```zsh
if zstyle -t ":completion:${curcontext}:options" verbose; then
  # show verbose completions
fi
```

---

### Retrieving style values

| Flag | Returns                  | Example                             |
| ---- | ------------------------ | ----------------------------------- |
| `-b` | Boolean (0/1 in `REPLY`) | `zstyle -b ':...' verbose val`      |
| `-s` | String (first match)     | `zstyle -s ':...' format val`       |
| `-a` | Array                    | `zstyle -a ':...' hosts val`        |
| `-t` | Test (boolean return)    | `if zstyle -t ':...' verbose; then` |

---

## Sources

- [Zsh Completion Style Guide](https://github.com/zsh-users/zsh/blob/master/Etc/completion-style-guide) -- upstream zsh project
- [Zsh Completion System](https://zsh.sourceforge.io/Doc/Release/Completion-System.html) -- zsh manual
- [Zsh Completion Widgets](https://zsh.sourceforge.io/Doc/Release/Completion-Widgets.html) -- zsh manual
