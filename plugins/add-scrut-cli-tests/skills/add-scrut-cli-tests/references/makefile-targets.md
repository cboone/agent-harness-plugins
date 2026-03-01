# Makefile Targets

Scrut test targets to add to the project Makefile.

## Template

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

## Placeholders

| Placeholder   | Description                                   | Example               |
| ------------- | --------------------------------------------- | --------------------- |
| `TOOL_BIN`    | Environment variable name for the binary path | `BOPCA_BIN`           |
| `BINARY_PATH` | Path to the built binary                      | `$(CURDIR)/bin/bopca` |
| `TESTS_DIR`   | Directory containing scrut test files         | `tests/scrut/`        |

## Notes

- `test-scrut` depends on `build` so the binary is compiled before tests run. For interpreted languages (shell scripts, Python, Ruby) where no build step is needed, remove the `: build` dependency from `test-scrut` and `test-scrut-update`. The binary path points directly to the executable script.
- The presence check (`command -v scrut`) gives a clear error message if scrut is not installed.
- `test-scrut-update` uses `--replace` to overwrite the original files and `--assume-yes` to skip confirmation prompts.
- `test-all` chains both unit tests (`test`) and scrut tests (`test-scrut`).
- Add all three targets to the `.PHONY` declaration.
- Use tab characters for Makefile indentation (not spaces).
