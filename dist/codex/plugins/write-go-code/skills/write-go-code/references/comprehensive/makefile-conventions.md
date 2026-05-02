# Makefile Conventions for run-go-ci.yml v3

The `cboone/gh-actions` reusable CI workflow (`run-go-ci.yml@v3.0.0`) calls Makefile targets directly. All Go projects using this workflow must follow these conventions.

## Required Targets

These five targets must exist in every Go project Makefile:

| Target  | Command                                      | Purpose          |
| ------- | -------------------------------------------- | ---------------- |
| `vet`   | `go vet ./...`                               | Static analysis  |
| `test`  | `go test -v -race ./...`                     | Run tests        |
| `lint`  | `golangci-lint run ./...`                    | Go linting only  |
| `build` | `go build ./...` or `go build -o bin/name .` | Compile          |
| `fmt`   | gofmt check pattern (see below)              | Check formatting |

## Key Rules

### `make fmt` must be a format check

- Exits non-zero when files need formatting
- Does **not** modify files
- Pattern:

```makefile
fmt: ## Check formatting (exits non-zero if files need formatting)
	@test -z "$$(gofmt -l .)" || { gofmt -l . && exit 1; }
```

- Repos that want a write-mode target should use `format` as the target name:

```makefile
format: ## Format code (write mode)
	go fmt ./...
```

### `make lint` must run only Go linting

- Calls only `golangci-lint run ./...`
- Does not include other linters (markdownlint, shellcheck, actionlint, etc.)
- Repos with broader lint targets should use `lint-all` as the umbrella:

```makefile
lint: ## Run golangci-lint
	golangci-lint run ./...

lint-all: lint ## Run all linters
	markdownlint-cli2 "**/*.md"
	actionlint
```

### `make test` should include `-v -race`

- `-v` provides verbose output for CI log readability
- `-race` enables the race detector
