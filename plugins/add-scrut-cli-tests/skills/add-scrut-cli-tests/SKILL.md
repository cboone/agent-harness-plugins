---
name: add-scrut-cli-tests
description: >-
  Set up scrut snapshot-based CLI integration testing for a Go CLI project.
  Use when the user says "add scrut tests", "add CLI tests", "set up scrut",
  "add e2e tests", "add integration tests", "scrut cli tests",
  "add snapshot tests", or asks to set up CLI integration testing with scrut
  for a Go project.
---

# Add Scrut CLI Tests

Set up [scrut](https://github.com/facebookincubator/scrut) snapshot-based CLI integration testing for a Go CLI project with Makefile targets and CI workflow integration.

## Prerequisites

- A Go CLI project with a `Makefile` and a `build` target that produces a binary
- A `.github/workflows/ci.yml` workflow (or equivalent CI workflow file)

## Workflow

### 1. Verify the Project

Confirm the current directory is a Go CLI project with a build pipeline:

- Check that `go.mod` exists (required; abort if missing)
- Check that a `Makefile` exists with a `build` target (required; abort if missing)
- Check for an existing `tests/scrut/` directory; if present, warn and ask whether to add to it or abort

### 2. Gather Project Information

Collect the following, inferring from existing files where possible:

- **Binary name**: check the Makefile `build` target for the output binary name (look for `-o bin/NAME` or `-o NAME`), or derive from the last segment of the module path in `go.mod`
- **Binary path**: determine the full path used in the Makefile build target (typically `bin/NAME` or `$(CURDIR)/bin/NAME`)
- **Environment variable name**: derive from the binary name, uppercased with hyphens replaced by underscores, suffixed with `_BIN` (e.g., `bopca` becomes `BOPCA_BIN`, `my-tool` becomes `MY_TOOL_BIN`)

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

Check the existing Makefile for any of these targets: `test-scrut`, `test-scrut-update`, `test-all`. If any exist, warn and ask before overwriting.

Add the Makefile targets from `./references/makefile-targets.md`:

- Replace `TOOL_BIN` with the environment variable name
- Replace `BINARY_PATH` with the path to the built binary (e.g., `$(CURDIR)/bin/NAME`)
- Replace `TESTS_DIR` with `tests/scrut/`

Append `test-scrut test-scrut-update test-all` to the `.PHONY` declaration (or create one if it does not exist).

If the Makefile has an `all` target, consider adding `test-all` to it or replacing `test` with `test-all` as appropriate. Ask the user if unsure.

### 6. Update CI Workflow

Look for the CI workflow file:

```bash
ls .github/workflows/ci.yml .github/workflows/ci.yaml
```

If found, add a `test-scrut` job using the template from `./references/ci-job.md`:

- Detect the Go version from the existing workflow's `go-version` field and use the same value
- Detect the runner OS from the existing workflow (e.g., `ubuntu-latest`, `macos-latest`) and use the same value
- Place the new job after existing test jobs
- If the workflow uses job dependencies (`needs`), set up appropriate dependencies for the new job

If no CI workflow exists, skip this step and note that the user should add CI workflow configuration manually.

### 7. Build and Run Tests

Build the binary and run the scrut tests to verify the setup:

```bash
make test-scrut
```

If `scrut` is not installed locally, inform the user to install from the facebookincubator/scrut GitHub releases:

```bash
gh release download --repo facebookincubator/scrut --pattern 'scrut-*-PLATFORM.tar.gz' --dir /tmp
tar -xzf /tmp/scrut-*-PLATFORM.tar.gz -C /tmp
cp /tmp/scrut-PLATFORM/scrut ~/.local/bin/
```

Replace `PLATFORM` with the appropriate identifier (e.g., `macos-aarch64`, `linux-x86_64`).

If tests fail because the expected output does not match, update the snapshots:

```bash
make test-scrut-update
```

Then re-run to confirm:

```bash
make test-scrut
```

### 8. Summary

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

- If `go.mod` does not exist, abort with a message that this skill requires an existing Go project
- If no `Makefile` exists, abort and suggest creating one first (or use the `scaffold-go-cli` skill)
- If `tests/scrut/` already exists, ask before adding or overwriting files
- If `scrut` is not installed locally, write test files with placeholder output and explain how to install scrut and update snapshots
- If the Makefile does not have a `build` target, ask the user which target builds the binary
- If no CI workflow exists, skip the CI step and inform the user
- If `make test-scrut` fails, check the output and attempt to fix; if the issue is stale snapshots, run `make test-scrut-update`
