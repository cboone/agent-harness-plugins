# Testing Zsh Plugins and Sourced Libraries

Conventions for testing zsh plugins, sourced helper files, and library code with scrut. These patterns differ from standard CLI binary testing because the code under test is `source`d rather than executed as a standalone binary.

## Shell Selection

Use the `--shell zsh` flag when running scrut tests that require zsh:

```bash
scrut test --shell zsh tests/scrut/
scrut update --shell zsh tests/scrut/
```

In the Makefile, add a dedicated target:

```makefile
.PHONY: test-scrut
test-scrut:
	scrut test --shell zsh tests/scrut/

.PHONY: test-scrut-update
test-scrut-update:
	scrut update --shell zsh tests/scrut/
```

## Source-Based Invocation

Replace `"${TOOL_BIN}"` with `source` to load the file under test. Use `$TESTDIR` to reference the directory containing the test file:

```scrut
$ source "${TESTDIR}/../src/helpers.zsh" && my_helper_function "arg1"
expected output
```

`$TESTDIR` is set automatically by scrut (inherited from cram) and always points to the directory where the `.md` test file lives. Build relative paths from there to reach the source files.

## One Command Per Block

Each fenced scrut block supports only one `$` command line (plus optional `>` continuation lines). Any additional `$` lines are interpreted as expected output, not as commands to execute.

Correct, two separate blocks:

````markdown
## Load helper

```scrut
$ source "${TESTDIR}/../src/helpers.zsh" && echo "loaded"
loaded
```

## Call function

```scrut
$ source "${TESTDIR}/../src/helpers.zsh" && my_function "test"
result
```
````

Wrong, second `$` line is treated as expected output:

````markdown
## Load and call

```scrut
$ source "${TESTDIR}/../src/helpers.zsh"
$ my_function "test"
result
```
````

Because scrut does not preserve sourced definitions across separate blocks, you must `source` the file in every block that needs it. Chain the source and the function call with `&&` on the same command line.

## ERR_EXIT and shopt Pitfall

### Problem

Scrut uses internal bash commands (`shopt`, `alias -p`) between blocks to manage shell state. When a sourced zsh file sets `ERR_EXIT` (or `set -e`) at the top level of the file, those bash commands fail under zsh, causing all subsequent blocks to error out with messages like:

```text
shopt: command not found
```

### Workaround

Do not set `ERR_EXIT` at the file level in zsh code that will be tested with scrut. Instead, use `emulate -LR zsh` with strict options inside individual functions:

Good:

```zsh
# helpers.zsh

function my_function() {
  emulate -LR zsh
  setopt ERR_EXIT NO_UNSET PIPE_FAIL

  # function body with strict error handling
}
```

Bad:

```zsh
# helpers.zsh

setopt ERR_EXIT NO_UNSET PIPE_FAIL

function my_function() {
  # function body
}
```

The `emulate -L zsh` call resets options to zsh defaults for the function scope, and the subsequent `setopt` applies strict options only within that function. This keeps scrut's inter-block state management working while still enforcing strict error handling in your code.

## Complete Example

A full test file for a zsh helper library:

````markdown
# Helper functions

Tests for the zsh helper library in `src/helpers.zsh`.

## Source without errors

```scrut
$ source "${TESTDIR}/../src/helpers.zsh" && echo "ok"
ok
```

## Format name

```scrut
$ source "${TESTDIR}/../src/helpers.zsh" && format_name "Jane" "Doe"
Doe, Jane
```

## Format name with missing argument

```scrut
$ source "${TESTDIR}/../src/helpers.zsh" && format_name "Jane" 2>&1 | head -1
Error: last name is required
[1]
```

## Validate config file

```scrut
$ cd "$(mktemp -d)" \
>   && printf 'key: value\n' > config.yaml \
>   && source "${TESTDIR}/../src/helpers.zsh" \
>   && validate_config config.yaml
Config is valid
```
````
