# Conditional Features

Apply these modifications to the base `.goreleaser.yml` template and release workflow based on detected project features. Each section describes how to detect the feature and what to change.

## Shell Completions

### Detection

Check for a `completion` subcommand in the project:

1. Look for `cmd/completion.go`
1. Grep Go files for cobra completion command registration (e.g., `"completion"` in `AddCommand` calls or `cobra.Command` literals)
1. Try running `go run . completion --help` to confirm the subcommand exists

If any of these succeed, the project has shell completions.

### goreleaser.yml Modifications

Replace the basic `test` block in `brews` with a custom `install` block that generates completions:

```yaml
brews:
  - # ... (keep all other fields from the base template)
    install: |
      bin.install "PROJECT-NAME"

      generate_completions_from_executable(bin/"PROJECT-NAME", "completion")
    test: |
      assert_match version.to_s, shell_output("#{bin}/PROJECT-NAME --version")
```

The `generate_completions_from_executable` Homebrew helper automatically calls the binary's `completion` subcommand for bash, zsh, and fish, and installs the output files in the correct locations.

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

**Add man page installation to the brew formula** in the `install` block:

```yaml
brews:
  - # ... (keep all other fields)
    install: |
      bin.install "PROJECT-NAME"
      man1.install Dir["man/man1/*"]
    test: |
      assert_match version.to_s, shell_output("#{bin}/PROJECT-NAME --version")
```

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

**Add a macOS requirement** to the brew formula using `custom_block`:

```yaml
brews:
  - # ... (keep other fields)
    custom_block: |
      depends_on :macos
```

### release-workflow.yml Modifications

Change the runner to `macos-latest`:

```yaml
jobs:
  goreleaser:
    runs-on: macos-latest
```

## Combining Features

When multiple conditional features are present, combine all applicable modifications into a single configuration. The most common combination is **completions + man pages** (as seen in bopca).

### Example: Completions + Man Pages

```yaml
before:
  hooks:
    - go mod tidy
    - mkdir -p man/man1
    - go run . man man/man1

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

brews:
  - # ... (keep all other fields)
    install: |
      bin.install "PROJECT-NAME"
      man1.install Dir["man/man1/*"]

      generate_completions_from_executable(bin/"PROJECT-NAME", "completion")
    test: |
      assert_match version.to_s, shell_output("#{bin}/PROJECT-NAME --version")
```

### Example: Completions + Man Pages + macOS Only

```yaml
before:
  hooks:
    - go mod tidy
    - mkdir -p man/man1
    - go run . man man/man1

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

brews:
  - # ... (keep all other fields)
    install: |
      bin.install "PROJECT-NAME"
      man1.install Dir["man/man1/*"]

      generate_completions_from_executable(bin/"PROJECT-NAME", "completion")
    custom_block: |
      depends_on :macos
    test: |
      assert_match version.to_s, shell_output("#{bin}/PROJECT-NAME --version")
```

Note: When macOS-only, remove the Windows format override from archives and change the release workflow runner to `macos-latest`.

## Notes

- The detection steps are heuristics; always present detected features to the user for confirmation before applying
- `generate_completions_from_executable` is a Homebrew helper that calls the binary's completion subcommand for each shell (bash, zsh, fish) and installs the output
- `man1.install Dir["man/man1/*"]` is a Homebrew helper that installs man pages into the correct system location
- The `before.hooks` section runs before each build; `go mod tidy` ensures dependencies are clean
- When combining man pages with macOS-only, the `files` section in archives still works (man pages are included in the macOS archives)
