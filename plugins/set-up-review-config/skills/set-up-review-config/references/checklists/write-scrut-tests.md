# Scrut Tests Review Checklist

Applies to scrut snapshot test files, usually `tests/scrut/*.md`. Cite findings as `write-scrut-tests: Rule name`.

## Important

- **Binary through a variable**: Tests call the tool under test through an environment variable such as `"${TOOL_BIN}"`, never through a fixed or relative path.
- **Asserted exit codes**: Every block that expects a failure ends with its exit code, such as `[1]`.
- **Isolated side effects**: Commands that create, modify or delete files run in a temporary directory from `$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")`, never in the repository or a fixed location.
- **Deterministic output**: Output whose order can vary is sorted, and versions, timestamps, hashes and paths are matched with `(glob)`, so the test does not fail at random.
- **Intentional snapshot updates**: After a snapshot update, `(glob)` and `(regex)` lines have not been replaced with the literal values of one run.
- **One command per zsh block**: In zsh plugin tests, each block has a single `$` line, because further `$` lines are read as expected output, and `ERR_EXIT` is not set at file level.

## Nits

- **File layout**: One `kebab-case.md` file per behavior group, such as `help.md` or `error-handling.md`, under `tests/scrut/`.
- **Headings**: A level-1 heading names the test group and a level-2 heading names each test case.
- **One assertion per block**: Each block checks one behavior, so a failure points at one place.
- **Block order**: Happy path first, then variations, edge cases and errors.
- **Continuation lines**: Long `&&` chains are split with the `>` continuation prefix.
- **Exact matches for stable text**: Help text and error messages are pinned exactly; `(glob+)` covers variable-length sections and `(regex)` is used only when a glob cannot express the pattern.
- **No color**: `NO_COLOR=1` instead of `(escaped)` matching for colored output.
- **Relevant error output**: Error cases redirect stderr with `2>&1` or use `{output_stream: stderr}`, and use `head -1` when a framework appends usage text.
- **Structured output**: JSON is checked through specific `jq` fields rather than a raw snapshot.
- **Test environment**: Test-specific variables are set inline or with the `environment` attribute.
- **Critical setup**: A setup block that later blocks depend on uses `{fail_fast: true}`.
- **Explained tests**: A test whose purpose is not obvious from its heading has a short description.

## Do not flag

- **Expected output**: Wording, spelling and formatting inside expected output lines, which pin the tool's real output.
- **Markdown style in test files**: Markdown conventions apply to the prose around the blocks, not to the blocks themselves.
- **Globs for dynamic values**: `(glob)` patterns on values that change between builds or machines.
