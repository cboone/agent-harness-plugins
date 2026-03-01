---
description: Set up scrut snapshot-based CLI integration testing for a CLI project.
disable-model-invocation: true
---

# Add Scrut CLI Tests

Set up [scrut](https://github.com/facebookincubator/scrut) snapshot-based CLI integration testing for a CLI project with Makefile targets and CI workflow integration.

## Prerequisites

- A CLI project that produces a binary or has an executable entry point
- A `.github/workflows/ci.yml` workflow (or equivalent CI workflow file) is recommended for CI integration

## Workflow

### 1. Detect the Project Type

Identify the project language by checking for manifest files:

| Marker(s)                        | Language |
| -------------------------------- | -------- |
| `go.mod`                         | Go       |
| `Package.swift`                  | Swift    |
| `Cargo.toml`                     | Rust     |
| `pyproject.toml`, `setup.py`     | Python   |
| `Gemfile`, `*.gemspec`           | Ruby     |
| Executable scripts (no manifest) | Shell    |

If no manifest is found and executable shell scripts exist in the root, `bin/`, or `scripts/`, treat the project as a shell script CLI.

If the project type cannot be determined, ask the user what language the project uses and where the binary or executable is located.

Check for an existing `tests/scrut/` directory; if present, warn and ask whether to add to it or abort.

### 2. Gather Project Information

Collect the following, inferring from existing files where possible:

- **Binary name**: determine by project type:
  - **Go**: check the Makefile `build` target for the output binary name (look for `-o bin/NAME` or `-o NAME`), or derive from the last segment of the module path in `go.mod`
  - **Swift**: check `Package.swift` for executable target names, or check the Makefile `build` target
  - **Rust**: check `Cargo.toml` for `[[bin]]` entries or the `name` field under `[package]`
  - **Python**: check `pyproject.toml` for `[project.scripts]` entries
  - **Ruby**: check the gemspec for `executables` or look in `bin/` or `exe/`
  - **Shell**: use the script filename as the binary name
- **Binary path**: determine the full path used to run the binary:
  - **Compiled languages** (Go, Swift, Rust): typically `bin/NAME` or a build output directory (e.g., `$(CURDIR)/bin/NAME`)
  - **Interpreted languages** (Python, Ruby, Shell): the script path itself (e.g., `bin/NAME`, `./NAME`)
- **Environment variable name**: derive from the binary name, uppercased with hyphens replaced by underscores, suffixed with `_BIN` (e.g., `bopca` becomes `BOPCA_BIN`, `my-tool` becomes `MY_TOOL_BIN`)
- **Build required**: whether a build step is needed before running tests (yes for compiled languages, no for interpreted languages)

If the user already provided some or all of these in their initial request, do not re-ask.

### 3. Create Test Directory

Create the `tests/scrut/` directory:

```bash
mkdir -p tests/scrut
```

### 4. Create Starter Test Files

Generate two starter test files using the templates from the references:

1. **`tests/scrut/help.md`**: uses the template from the Help Test Template section below. Replace `TOOL` with the binary name, `TOOL_BIN` with the environment variable name, and run the binary with `--help` to capture the actual help output for the initial snapshot.

1. **`tests/scrut/version.md`**: uses the template from the Version Test Template section below. Replace `TOOL` with the binary name, `TOOL_BIN` with the environment variable name.

To populate the initial help output snapshot:

```bash
TOOL_BIN="BINARY_PATH" scrut create --title "Root help" '"${TOOL_BIN}" --help'
```

If `scrut` is not installed locally, write the test files with placeholder output and instruct the user to run `make test-scrut-update` after installing scrut to populate the snapshots.

### 5. Add Makefile Targets

If no `Makefile` exists:

- For **compiled languages** (Go, Swift, Rust): ask the user to create one or offer to generate a minimal Makefile with `build` and `test-scrut` targets appropriate to the language
- For **interpreted languages** (Python, Ruby, Shell): create a minimal Makefile with just the scrut targets (no build dependency needed)

If a `Makefile` exists, check for any of these targets: `test-scrut`, `test-scrut-update`, `test-all`. If any exist, warn and ask before overwriting.

Add the Makefile targets from the Makefile Targets section below:

- Replace `TOOL_BIN` with the environment variable name
- Replace `BINARY_PATH` with the path to the built binary or executable script
- Replace `TESTS_DIR` with `tests/scrut/`
- **If the project does not require a build step** (shell scripts, interpreted languages), remove the `build` dependency from `test-scrut` and `test-scrut-update` targets

Append `test-scrut test-scrut-update test-all` to the `.PHONY` declaration (or create one if it does not exist).

If the Makefile has an `all` target, consider adding `test-all` to it or replacing `test` with `test-all` as appropriate. Ask the user if unsure.

### 6. Update CI Workflow

Look for the CI workflow file:

```bash
ls .github/workflows/ci.yml .github/workflows/ci.yaml
```

If found, add a `test-scrut` job using the template from the CI Job Template section below:

- **Copy the language setup step(s)** from the existing CI workflow (e.g., `actions/setup-go`, Swift toolchain setup, `actions/setup-python`, Rust toolchain setup). If the workflow has multiple language setup steps, include only the ones needed to build the project binary. For shell script projects, no language setup step is needed.
- Detect the runner OS from the existing workflow (e.g., `ubuntu-latest`, `macos-latest`) and use the same value
- Determine the latest scrut release tag for `SCRUT_VERSION` (run `gh release list --repo facebookincubator/scrut --limit 1 --json tagName --jq '.[0].tagName'`)
- Place the new job after existing test jobs
- If the workflow uses job dependencies (`needs`), set up appropriate dependencies for the new job

If no CI workflow exists, skip this step and note that the user should add CI workflow configuration manually.

### 7. Build and Run Tests

Build the binary (if applicable) and run the scrut tests to verify the setup:

```bash
make test-scrut
```

If `scrut` is not installed locally, inform the user to install from the facebookincubator/scrut GitHub releases. Determine the latest release tag (run `gh release list --repo facebookincubator/scrut --limit 1 --json tagName --jq '.[0].tagName'`):

```bash
mkdir -p ~/.local/bin
gh release download SCRUT_VERSION --repo facebookincubator/scrut --pattern 'scrut-SCRUT_VERSION-SCRUT_PLATFORM.tar.gz' --dir /tmp
tar -xzf /tmp/scrut-SCRUT_VERSION-SCRUT_PLATFORM.tar.gz -C /tmp
cp /tmp/scrut-SCRUT_PLATFORM/scrut ~/.local/bin/
```

Replace `SCRUT_VERSION` with the pinned release tag (e.g., `v0.4.3`) and `SCRUT_PLATFORM` with the appropriate identifier (e.g., `macos-aarch64`, `linux-x86_64`).

Scrut does not currently publish checksums or signatures with its releases, so integrity verification is not yet possible. If checksums become available in the future, add a verification step after the download, mirroring the guidance in the CI Job Template section below.

Ensure `~/.local/bin` is on `PATH`. If it is not already, add it to your shell profile (e.g., `export PATH="$HOME/.local/bin:$PATH"` in `~/.zshrc` or `~/.bashrc`).

If tests fail because the expected output does not match, update the snapshots:

```bash
make test-scrut-update
```

Then re-run to confirm:

```bash
make test-scrut
```

### 8. Update markdownlint Config

If a markdownlint config exists (`.markdownlint-cli2.jsonc`, `.markdownlint.jsonc`, `.markdownlint.yaml`, or `.markdownlint.json`), add `"MD014": false` to disable the "dollar signs used before commands" rule. Scrut test files use `$ command` notation that triggers this rule.

If no markdownlint config exists, skip this step.

### 9. Summary

Print a summary of what was created and modified:

- List every file created (`tests/scrut/help.md`, `tests/scrut/version.md`)
- List every file modified (`Makefile`, `.github/workflows/ci.yml`)
- Note the key Makefile targets:
  - `make test-scrut`: run scrut tests
  - `make test-scrut-update`: update test snapshots
  - `make test-all`: run both unit tests and scrut tests
- Remind the user to review the starter test files and add tests for additional commands and error cases
- Point to the Scrut Test Format section below for writing new tests

## Error Handling

- If no recognized project manifest is found and no executable scripts exist, ask the user what language the project uses and where the binary or executable is located
- If no `Makefile` exists and the project is a compiled language, warn that a build step is needed and offer to create a minimal Makefile, or suggest the relevant scaffolding skill (e.g., `scaffold-go-cli` for Go projects)
- If no `Makefile` exists and the project is an interpreted language, offer to create a minimal Makefile with just the scrut test targets
- If `tests/scrut/` already exists, ask before adding or overwriting files
- If `scrut` is not installed locally, write test files with placeholder output and explain how to install scrut and update snapshots
- If the Makefile does not have a `build` target and the project requires one, ask the user which target builds the binary
- If no CI workflow exists, skip the CI step and inform the user
- If `make test-scrut` fails, check the output and attempt to fix; if the issue is stale snapshots, run `make test-scrut-update`

---

## Reference: Help Test

Starter test file template for verifying `--help` output.

### Template

Write `tests/scrut/help.md` with the following content:

````markdown
# Help output

Tests for TOOL help commands.

## Root help

```scrut
$ "${TOOL_BIN}" --help
HELP_OUTPUT
```

## Short help flag

```scrut
$ "${TOOL_BIN}" -h
HELP_OUTPUT
```
````

### Placeholders

| Placeholder   | Description                                         | Example                 |
| ------------- | --------------------------------------------------- | ----------------------- |
| `TOOL`        | Human-readable tool name                            | `bopca`                 |
| `TOOL_BIN`    | Environment variable name for the binary path       | `BOPCA_BIN`             |
| `HELP_OUTPUT` | Actual output from running the binary with `--help` | (captured during setup) |

### Notes

- Both `--help` and `-h` should produce identical output. If they differ, adjust accordingly.
- The `HELP_OUTPUT` should be the exact output captured from running the binary. Use `scrut create` or `scrut update` to populate this.
- To bootstrap the test file with actual output, write the template with a `* (glob+)` placeholder for the output, then run `make test-scrut-update` to replace it with the real output.
- If the tool has subcommands, add a separate test file for subcommand help output (e.g., `subcommand-help.md`).

---

## Reference: Version Test

Starter test file template for verifying version command output.

### Template

Write `tests/scrut/version.md` with the following content:

````markdown
# Version output

Tests for TOOL version commands.

## Version command

```scrut
$ "${TOOL_BIN}" version
TOOL v* (glob)
  commit: * (glob)
  built:  * (glob)
```

## Version flag

```scrut
$ "${TOOL_BIN}" --version
TOOL v* (glob)
  commit: * (glob)
  built:  * (glob)
```
````

### Placeholders

| Placeholder | Description                                         | Example     |
| ----------- | --------------------------------------------------- | ----------- |
| `TOOL`      | Human-readable tool name (as printed by the binary) | `bopca`     |
| `TOOL_BIN`  | Environment variable name for the binary path       | `BOPCA_BIN` |

### Notes

- Version output typically contains dynamic values (version number, commit hash, build timestamp). Use `(glob)` patterns for these lines.
- The template assumes the version output format includes version, commit, and build timestamp. Adjust the expected output to match the project's actual version format.
- If the project only supports `--version` and not a `version` subcommand (or vice versa), remove the test case that does not apply.
- If the project does not have version output yet, skip this test file and note it as a follow-up.

---

## Reference: Makefile Targets

Scrut test targets to add to the project Makefile.

### Template

```makefile
## Run scrut CLI tests
test-scrut: build
	@echo "Running scrut CLI tests..."
	@if ! command -v scrut >/dev/null 2>&1; then \
		echo "scrut not installed. Install from https://github.com/facebookincubator/scrut"; \
		exit 1; \
	fi
	TOOL_BIN="BINARY_PATH" scrut test TESTS_DIR

## Update scrut test expectations
test-scrut-update: build
	TOOL_BIN="BINARY_PATH" scrut update --replace --assume-yes TESTS_DIR

## Run all tests (unit + scrut)
test-all: test test-scrut
```

### Placeholders

| Placeholder   | Description                                   | Example               |
| ------------- | --------------------------------------------- | --------------------- |
| `TOOL_BIN`    | Environment variable name for the binary path | `BOPCA_BIN`           |
| `BINARY_PATH` | Path to the built binary                      | `$(CURDIR)/bin/bopca` |
| `TESTS_DIR`   | Directory containing scrut test files         | `tests/scrut/`        |

### Notes

- `test-scrut` depends on `build` so the binary is compiled before tests run. For interpreted languages (shell scripts, Python, Ruby) where no build step is needed, remove the `: build` dependency from `test-scrut` and `test-scrut-update`. The binary path points directly to the executable script.
- The presence check (`command -v scrut`) gives a clear error message if scrut is not installed.
- `test-scrut-update` uses `--replace` to overwrite the original files and `--assume-yes` to skip confirmation prompts.
- `test-all` chains both unit tests (`test`) and scrut tests (`test-scrut`).
- Add all three targets to the `.PHONY` declaration.
- Use tab characters for Makefile indentation (not spaces).

---

## Reference: CI Job

GitHub Actions job template for running scrut CLI tests.

### Template

```yaml
test-scrut:
  name: Test CLI (Scrut)
  runs-on: RUNNER_OS
  steps:
    - name: Checkout code
      uses: actions/checkout@v6

    LANGUAGE_SETUP_STEPS

    - name: Install scrut
      env:
        GH_TOKEN: ${{ github.token }}
      run: |
        mkdir -p "${HOME}/.local/bin"
        echo "${HOME}/.local/bin" >> "${GITHUB_PATH}"
        gh release download SCRUT_VERSION --repo facebookincubator/scrut --pattern 'scrut-SCRUT_VERSION-SCRUT_PLATFORM.tar.gz' --dir /tmp
        tar -xzf /tmp/scrut-SCRUT_VERSION-SCRUT_PLATFORM.tar.gz -C /tmp
        cp /tmp/scrut-SCRUT_PLATFORM/scrut "${HOME}/.local/bin/"

    - name: Run scrut CLI tests
      run: make test-scrut
```

### Placeholders

| Placeholder            | Description                                                         | Example                         |
| ---------------------- | ------------------------------------------------------------------- | ------------------------------- |
| `RUNNER_OS`            | GitHub Actions runner OS                                            | `macos-latest`, `ubuntu-latest` |
| `LANGUAGE_SETUP_STEPS` | Language setup steps copied from the project's existing CI workflow | (see Notes)                     |
| `SCRUT_VERSION`        | Pinned scrut release tag                                            | `v0.4.3`                        |
| `SCRUT_PLATFORM`       | Platform identifier from scrut release assets                       | `macos-aarch64`, `linux-x86_64` |

### Notes

- `LANGUAGE_SETUP_STEPS` should be copied from the project's existing CI workflow. Common examples:
  - **Go**: `actions/setup-go@v6` with `go-version` and caching settings matching the existing workflow
  - **Swift**: Swift is preinstalled on macOS runners; for Ubuntu runners, use a Swift setup action or install step
  - **Rust**: `dtolnay/rust-toolchain` with the appropriate toolchain version
  - **Python**: `actions/setup-python@v5` with `python-version` matching the existing workflow
  - **Ruby**: `ruby/setup-ruby@v1` with `ruby-version` matching the existing workflow
  - **Shell**: no language setup step needed; remove the placeholder entirely
- Copy the language setup verbatim from the existing CI workflow to ensure version consistency and caching configuration are preserved.
- Scrut is installed via `gh release download` from `facebookincubator/scrut`. The upstream install script is not used because its `get_latest_version()` function hardcodes `ukautz/scrut`, and it installs to a directory not in `PATH` on GitHub Actions runners.
- The `SCRUT_VERSION` tag pins the download to a specific release for reproducible builds. Check [scrut releases](https://github.com/facebookincubator/scrut/releases) for available versions.
- Scrut does not currently publish checksums or signatures with its releases, so integrity verification is not yet possible. If checksums become available in the future, add a verification step after the download.
- The `SCRUT_PLATFORM` value must match the runner OS: use `macos-aarch64` for `macos-latest` and `linux-x86_64` for `ubuntu-latest`.
- The job relies on `make test-scrut`, which handles building the binary (if applicable) and running tests.
- Match the `runs-on` value and language setup steps to the project's existing CI configuration.
- Place this job alongside other test jobs in the workflow. If the workflow uses job dependencies, this job typically depends on the lint job (if any).

---

## Reference: Scrut Test Format

Reference for writing scrut test files. See the [scrut documentation](https://facebookincubator.github.io/scrut/) for the complete specification.

### File Structure

Scrut test files are standard Markdown files (`.md`) containing fenced code blocks with the `scrut` language identifier. Each file represents a group of related test cases. All test cases within a single file share the same shell process, so variables, aliases, and exports persist across blocks.

Lines starting with `$` are shell commands. Lines starting with `>` are command continuations. All other lines within the code block are expected output.

### Assertion Types

#### Exact match (default)

The expected output must match exactly, line by line:

```scrut
$ echo "hello world"
hello world
```

#### Glob matching

Use `*` (any characters) and `?` (one character) with the `(glob)` suffix:

```scrut
$ my-tool version
my-tool v* (glob)
  commit: * (glob)
  built:  * (glob)
```

#### Regex matching

Use regular expressions with the `(regex)` suffix:

```scrut
$ my-tool version
my-tool v\d+\.\d+\.\d+ (regex)
```

#### Escaped matching

Match output containing non-printable characters (ANSI escapes, tabs) with the `(escaped)` suffix:

```scrut
$ printf "foo\tbar"
foo\tbar (escaped)
```

### Quantifiers

Quantifiers control how many output lines a single expectation line can match:

| Quantifier | Meaning            | Example     |
| ---------- | ------------------ | ----------- |
| `?`        | Zero or one line   | `* (glob?)` |
| `*`        | Zero or more lines | `* (glob*)` |
| `+`        | One or more lines  | `* (glob+)` |

Common pattern for matching variable-length output:

```scrut
$ my-tool --help
Usage:
  my-tool [command]
* (glob+)
```

### Exit Codes

By default, scrut expects exit code 0. Specify non-zero exit codes with bracket notation as the last line of expected output:

```scrut
$ my-tool --bad-flag 2>&1 | head -1
Error: unknown flag "--bad-flag"
[1]
```

### Empty Output

When a command should produce no output, leave the code block empty after the command:

```scrut
$ my-tool --quiet version
```

### Stderr

By default, scrut validates stdout only. To validate stderr, use the `output_stream` attribute:

```scrut {output_stream: stderr}
$ my-tool --bad-flag
Error: unknown flag "--bad-flag"
[1]
```

To validate combined stdout and stderr, either use the attribute or redirect in the command:

```scrut
$ my-tool bad-command 2>&1 | head -1
Error: unknown command "bad-command" for "my-tool"
```

### Per-Test Configuration

Attributes can be set in curly braces after the language tag:

| Attribute       | Description                 | Example                         |
| --------------- | --------------------------- | ------------------------------- |
| `timeout`       | Max execution time          | `{timeout: 10s}`                |
| `fail_fast`     | Stop document on failure    | `{fail_fast: true}`             |
| `output_stream` | Stream to validate          | `{output_stream: stderr}`       |
| `environment`   | Extra environment variables | `{environment: {"KEY": "val"}}` |

### Document Configuration (Frontmatter)

YAML frontmatter controls document-level settings:

```yaml
---
prepend:
  - "../shared/setup.md"
defaults:
  timeout: 10s
total_timeout: 30s
---
```

### Built-in Environment Variables

Scrut provides these variables in every test execution:

| Variable    | Description                             |
| ----------- | --------------------------------------- |
| `$TESTDIR`  | Directory containing the test file      |
| `$TESTFILE` | Name of the current test file           |
| `$TMPDIR`   | Fresh temporary directory per test file |

### Tips

- Use `NO_COLOR=1` to suppress color codes in output.
- Pipe through `head`, `tail`, or `grep` to test specific lines.
- Use `$(mktemp -d)` for operations that create files.
- Sort non-deterministic output with `| sort`.
- Prefer JSON output with `jq` extraction over snapshotting raw text for structured data.
- Use one test file per logical group of related behaviors (e.g., `help.md`, `version.md`, `error-handling.md`).
- Run `make test-scrut-update` to regenerate expected output after intentional changes.
