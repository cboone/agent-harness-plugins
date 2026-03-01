---
name: add-scrut-cli-tests
description: >-
  Set up scrut snapshot-based CLI integration testing for a CLI project.
  Use when the user says "add scrut tests", "add CLI tests", "set up scrut",
  "add e2e tests", "add integration tests", "scrut cli tests",
  "add snapshot tests", or asks to set up CLI integration testing with scrut
  for any CLI project.
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

1. **`tests/scrut/help.md`**: uses the template from `./references/help-test.md`. Replace `TOOL` with the binary name, `TOOL_BIN` with the environment variable name, and run the binary with `--help` to capture the actual help output for the initial snapshot.

1. **`tests/scrut/version.md`**: uses the template from `./references/version-test.md`. Replace `TOOL` with the binary name, `TOOL_BIN` with the environment variable name.

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

Add the Makefile targets from `./references/makefile-targets.md`:

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

If found, add a `test-scrut` job using the template from `./references/ci-job.md`:

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

Scrut does not currently publish checksums or signatures with its releases, so integrity verification is not yet possible. If checksums become available in the future, add a verification step after the download, mirroring the guidance in `./references/ci-job.md`.

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
- Point to the scrut test format reference in `./references/test-format.md` for writing new tests

## Reference Navigation

- `./references/makefile-targets.md`: Makefile target templates for scrut test commands
- `./references/ci-job.md`: GitHub Actions CI job template for installing and running scrut
- `./references/help-test.md`: starter test template for `--help` output
- `./references/version-test.md`: starter test template for version command output
- `./references/test-format.md`: scrut test format reference with assertion types, exit codes, and patterns

## Error Handling

- If no recognized project manifest is found and no executable scripts exist, ask the user what language the project uses and where the binary or executable is located
- If no `Makefile` exists and the project is a compiled language, warn that a build step is needed and offer to create a minimal Makefile, or suggest the relevant scaffolding skill (e.g., `scaffold-go-cli` for Go projects)
- If no `Makefile` exists and the project is an interpreted language, offer to create a minimal Makefile with just the scrut test targets
- If `tests/scrut/` already exists, ask before adding or overwriting files
- If `scrut` is not installed locally, write test files with placeholder output and explain how to install scrut and update snapshots
- If the Makefile does not have a `build` target and the project requires one, ask the user which target builds the binary
- If no CI workflow exists, skip the CI step and inform the user
- If `make test-scrut` fails, check the output and attempt to fix; if the issue is stale snapshots, run `make test-scrut-update`
