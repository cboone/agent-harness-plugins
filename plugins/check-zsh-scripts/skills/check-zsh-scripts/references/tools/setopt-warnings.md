# setopt warn_create_global warn_nested_var

## Purpose

Detect variable scope issues using zsh's built-in warning options.

## Command

```bash
zsh -c 'setopt warn_create_global warn_nested_var; source <file>'
```

## Options

### warn_create_global

Warns when a function creates a global variable without explicitly declaring it with `typeset -g` or `declare -g`. Helps catch accidental global variable leaks from functions.

Example warning:

```text
script.zsh:15: scalar parameter foo created globally in function bar
```

Fix: Add `local foo` or `typeset -g foo` (if the global is intentional).

### warn_nested_var

Warns when a nested function shadows a variable from an outer function. Helps catch unintentional variable name collisions.

Example warning:

```text
script.zsh:22: numeric parameter count set in enclosing scope in function inner
```

Fix: Rename the inner variable or use `local` to explicitly declare a new scope.

## Interpretation

- **Structured scripts with functions**: Most warnings are actionable. Functions should declare their variables with `local`.
- **`.zshrc` and config files**: Many warnings are expected and harmless. These files intentionally set global state (e.g., `PATH`, `EDITOR`, prompt variables). Acknowledge rather than fix.
- **Plugin/framework code**: Warnings about global variables may be intentional (plugins expose variables for user configuration). Check whether `typeset -g` is the right fix.

## Side Effects

This command **sources the file**, which means:

- Any commands in the file will execute
- Environment variables may be modified
- Files may be created or modified
- External commands in the file will run

Review the file's contents before running this check on untrusted scripts. For files with significant side effects, consider extracting functions into a separate file for testing, or skip this check.

## SKIP_SETOPT_CHECK

Because this step is the only part of the pipeline that executes code, generated `check-zsh.zsh` scripts (and any wrapper invoking this check) should honor a `SKIP_SETOPT_CHECK=1` opt-out:

```zsh
if [[ "${SKIP_SETOPT_CHECK:-}" == "1" ]]; then
  print "==> setopt warnings: skipped (SKIP_SETOPT_CHECK=1)"
else
  # run the setopt check
fi
```

Design rationale:

- **Opt-out, not opt-in**: The check is a core part of the 7-tool pipeline and runs by default during local development. Do not invert this to require an opt-in flag.
- **CI compatibility**: The `setup-ci` zsh CI workflow template sets `SKIP_SETOPT_CHECK: "1"` in the job `env` to keep lint jobs purely static analysis. Generated check scripts must honor this env var to interoperate.
- **Local override**: Users with significant side effects in their scripts (or sandboxed environments) can also set `SKIP_SETOPT_CHECK=1` interactively.

## Notes

- Most useful for library-style zsh scripts with multiple functions.
- Combine with `emulate -L zsh` to reset options to zsh defaults before sourcing:

  ```bash
  zsh -c 'emulate -L zsh; setopt warn_create_global warn_nested_var; source <file>'
  ```

- The `-L` flag to `emulate` makes the option setting local to the current scope.
