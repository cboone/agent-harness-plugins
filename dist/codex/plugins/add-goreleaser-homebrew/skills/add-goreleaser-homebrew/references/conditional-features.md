# Conditional Features

Apply these modifications to the base `.goreleaser.yml` template and release workflow based on detected project features. Each section describes how to detect the feature and what to change.

**Note:** All `before.hooks` examples below use `go run .`, which assumes the main package is at the repository root. If `builds.main` is a subdirectory (e.g., `./cmd/PROJECT-NAME`), replace `go run .` with `go run ./cmd/PROJECT-NAME` in all hook commands.

## Shell Completions

### Detection

Check for a `completion` subcommand in the project:

1. Look for `cmd/completion.go`
1. Grep Go files for cobra completion command registration (e.g., `"completion"` in `AddCommand` calls or `cobra.Command` literals)
1. Try running `go run . completion --help` to confirm the subcommand exists

If any of these succeed, the project has shell completions.

### goreleaser.yml Modifications

**Add a `before` hook** to generate completion files during the build:

```yaml
before:
  hooks:
    - go mod tidy
    - mkdir -p completions
    - go run . completion bash > completions/PROJECT-NAME.bash
    - go run . completion zsh > completions/PROJECT-NAME.zsh
    - go run . completion fish > completions/PROJECT-NAME.fish
```

**Add completion files to the archive** by adding a `files` section to `archives`:

```yaml
archives:
  - # ... (keep all other fields)
    files:
      - src: completions/*
        dst: completions
```

**Add completions to the cask config**:

```yaml
homebrew_casks:
  - # ... (keep all other fields from the base template)
    completions:
      bash: completions/PROJECT-NAME.bash
      zsh: completions/PROJECT-NAME.zsh
      fish: completions/PROJECT-NAME.fish
```

Completion files are pre-generated during the build via `before.hooks`, included in the release archive via `archives.files`, and referenced in the cask via the `completions:` field. This replaces the formula approach of running `generate_completions_from_executable` at install time.

## Man Pages

### Detection

Check for man page generation capability in the project:

1. Look for `cmd/man.go`
1. Grep Go files for `cobra/doc` or `mango` imports (common man page generators for Cobra CLIs)
1. Try running `go run . man --help` to confirm the subcommand exists

If any of these succeed, the project can generate man pages.

### goreleaser.yml Modifications

**Add a `before` hook** to generate man pages during the build:

```yaml
before:
  hooks:
    - go mod tidy
    - mkdir -p man/man1
    - go run . man man/man1
```

**Add man pages to the archive** by adding a `files` section to `archives`:

```yaml
archives:
  - formats:
      - tar.gz
    format_overrides:
      - goos: windows
        formats:
          - zip
    name_template: "{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}"
    files:
      - src: man/man1/*
        dst: man/man1
```

**Add man pages to the cask config**:

```yaml
homebrew_casks:
  - # ... (keep all other fields)
    manpages:
      - man/man1/PROJECT-NAME.1
```

Man page files are pre-generated during the build via `before.hooks`, included in the release archive via `archives.files`, and referenced in the cask via the `manpages:` field. For projects with multiple man pages (e.g., per-subcommand), add an entry for each file.

## macOS Only

### Detection

Check whether the project targets macOS exclusively:

1. Look for `//go:build darwin` or `// +build darwin` build constraints in `.go` files
1. Check the Makefile for `GOOS=darwin` in build commands
1. Check for macOS-specific dependencies (e.g., `darwin` in `go.mod` comments, Objective-C bindings, or Apple framework imports)
1. If detection is inconclusive, ask the user

### goreleaser.yml Modifications

**Restrict the build matrix** to macOS only:

```yaml
builds:
  - # ... (keep other fields)
    goos:
      - darwin
    goarch:
      - arm64
```

Note: Use `goarch: [arm64]` for Apple Silicon-only tools. Use `goarch: [amd64, arm64]` if the tool should also support Intel Macs.

**Remove the Windows format override** from archives (no longer needed):

```yaml
archives:
  - formats:
      - tar.gz
    name_template: "{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}"
```

### .github/workflows/release.yml Modifications

Pass `runs-on: macos-latest` as an input to the reusable workflow:

```yaml
jobs:
  release:
    uses: cboone/gh-actions/.github/workflows/release-go-binaries.yml@91f9abd25d4f82354c0f950dfc8b6d7525b0f5b5 # v3.0.0
    with:
      go-version-file: go.mod
      runs-on: macos-latest
    secrets:
      HOMEBREW_TAP_TOKEN: ${{ secrets.HOMEBREW_TAP_TOKEN }}
```

## Combining Features

When multiple conditional features are present, combine all applicable modifications into a single configuration. The most common combination is **completions + man pages** (as seen in bopca).

### Example: Completions + Man Pages

```yaml
before:
  hooks:
    - go mod tidy
    - mkdir -p man/man1 completions
    - go run . man man/man1
    - go run . completion bash > completions/PROJECT-NAME.bash
    - go run . completion zsh > completions/PROJECT-NAME.zsh
    - go run . completion fish > completions/PROJECT-NAME.fish

archives:
  - formats:
      - tar.gz
    format_overrides:
      - goos: windows
        formats:
          - zip
    name_template: "{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}"
    files:
      - src: man/man1/*
        dst: man/man1
      - src: completions/*
        dst: completions

homebrew_casks:
  - # ... (keep all other fields)
    manpages:
      - man/man1/PROJECT-NAME.1
    completions:
      bash: completions/PROJECT-NAME.bash
      zsh: completions/PROJECT-NAME.zsh
      fish: completions/PROJECT-NAME.fish
```

### Example: Completions + Man Pages + macOS Only

```yaml
before:
  hooks:
    - go mod tidy
    - mkdir -p man/man1 completions
    - go run . man man/man1
    - go run . completion bash > completions/PROJECT-NAME.bash
    - go run . completion zsh > completions/PROJECT-NAME.zsh
    - go run . completion fish > completions/PROJECT-NAME.fish

builds:
  - main: .
    binary: PROJECT-NAME
    env:
      - CGO_ENABLED=0
    goos:
      - darwin
    goarch:
      - arm64
    ldflags:
      - -s -w
      - -X main.version={{.Version}}

archives:
  - formats:
      - tar.gz
    name_template: "{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}"
    files:
      - src: man/man1/*
        dst: man/man1
      - src: completions/*
        dst: completions

homebrew_casks:
  - # ... (keep all other fields)
    manpages:
      - man/man1/PROJECT-NAME.1
    completions:
      bash: completions/PROJECT-NAME.bash
      zsh: completions/PROJECT-NAME.zsh
      fish: completions/PROJECT-NAME.fish
```

Note: When macOS-only, remove the Windows format override from archives and pass `runs-on: macos-latest` to the reusable release workflow.

## Notes

- The detection steps are heuristics; always present detected features to the user for confirmation before applying
- Completion files must be pre-generated during build time via `before.hooks` (unlike formulas, which could generate them at install time with `generate_completions_from_executable`)
- Man pages are referenced via the `manpages:` array, which lists file paths relative to the archive root
- The `binaries:` array replaces the formula `install:` block for listing binaries to install
- Casks do not support `test:` blocks; version testing works differently in the Homebrew cask ecosystem
- The `before.hooks` section runs before each build; `go mod tidy` ensures dependencies are clean
- When combining man pages with macOS-only, the `files` section in archives still works (man pages are included in the macOS archives)
