# Makefile LDFLAGS Update

The Makefile mirrors GoReleaser's ldflags so local `make build` produces a binary with the same metadata wiring (just sourced from `git` and `date` instead of GoReleaser templates).

## Target State

Ensure these definitions are present near the top of the Makefile, alongside any existing `VERSION` variable:

```makefile
VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
COMMIT  ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo "none")
DATE    ?= $(shell date -u +%Y-%m-%dT%H:%M:%SZ)

LDFLAGS := -s -w \
	-X main.version=$(VERSION) \
	-X main.commit=$(COMMIT) \
	-X main.date=$(DATE)
```

The `build` target uses `$(LDFLAGS)`:

```makefile
build:
	mkdir -p $(OUTDIR)
	go build -ldflags "$(LDFLAGS)" -o $(OUTDIR)/$(BINARY) .
```

Some projects already wrap `-ldflags` differently (for example `go build $(LDFLAGS) ...` where `LDFLAGS` already includes the `-ldflags "..."` shape). Preserve whichever shape is in use. The non-negotiable invariant is that the three `-X main.*` entries reach `go build`.

## Edit Strategy

1. **`VERSION` variable.** If it already exists, leave it. If not, add it using the `git describe --tags --always --dirty` fallback shown above.
1. **`COMMIT` variable.** Add it if missing. Use `git rev-parse --short HEAD` with the `echo "none"` fallback so make does not fail in a non-git checkout.
1. **`DATE` variable.** Add it if missing. Use `date -u +%Y-%m-%dT%H:%M:%SZ` so the date is UTC and matches GoReleaser's RFC 3339 formatting.
1. **`LDFLAGS` variable.** Find the existing definition. Append the missing `-X main.commit=...` and `-X main.date=...` entries. Do not remove any existing entries.
1. **`build` target.** Confirm it passes `$(LDFLAGS)` to `go build`. If it already does (whether as `-ldflags "$(LDFLAGS)"` or as a self-contained `$(LDFLAGS)` shorthand), leave it alone. If not, update it to do so.

## Important Make Conventions

- Use tabs (not spaces) for recipe indentation. Make is unforgiving about this.
- Use `?=` for `VERSION`, `COMMIT`, and `DATE` so values can be overridden from the environment (for example by CI or by a developer pinning a specific commit). Use `:=` for `LDFLAGS` so the `-X` substitution happens once at parse time.
- Do not export the variables. They only need to be visible to recipes in this Makefile, and exporting them can leak into `go build`'s environment in surprising ways.

## Notes

- The `git describe --tags --always --dirty` fallback echoes `dev` when the repo has no tags. This matches the package-level default in `main.go` and keeps the local-build experience predictable.
- The `git rev-parse --short HEAD` fallback echoes `none` to match `main.go`'s default. A non-git checkout (rare for development, common for source tarballs) will then show `commit: none` in the version output.
- The `date -u` fallback never fails; it always produces a value, so no `||` clause is needed.
- Some projects use `BUILD_DATE` instead of `DATE`, or `GIT_COMMIT` instead of `COMMIT`. Either is fine; keep the existing names. The only thing that has to match between the Makefile and `main.go` is the right-hand side of each `-X` entry (`main.version`, `main.commit`, `main.date`).
