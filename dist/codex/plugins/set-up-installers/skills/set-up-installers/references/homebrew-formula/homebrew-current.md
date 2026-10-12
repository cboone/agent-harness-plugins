# Current Homebrew Guidance

This reference was checked against official Homebrew documentation on 2026-05-03. Refresh the linked docs when the task depends on current Homebrew behavior.

## Authoritative Sources

- [Formula Cookbook](https://docs.brew.sh/Formula-Cookbook)
- [Acceptable Formulae](https://docs.brew.sh/Acceptable-Formulae)
- [`Formula` Ruby API](https://docs.brew.sh/rubydoc/Formula.html)

## Core Rules

- A formula is Ruby code using the `Formula` API.
- Stable formulae use a stable source `url` and `sha256`. Tagged release tarballs are preferred when they exist.
- HEAD builds use `head "https://github.com/owner/repo.git", branch: "main"` and are for development or pre-release installs.
- Formula names should follow how the project markets itself. The filename and class must correspond by strict CamelCase conversion, such as `foo-bar.rb` to `FooBar`.
- `desc`, `homepage`, and `license` should be filled in. Use SPDX license identifiers where possible.
- Declare dependencies with `depends_on`, including build-only dependencies such as `depends_on "go" => :build`.
- Use `on_macos`, `on_linux`, `on_arm`, and `on_intel` blocks for platform-specific declarations outside `def install` and `test do`.
- Inside `def install` and `test do`, use conditionals such as `OS.mac?`, `OS.linux?`, `Hardware::CPU.arm?`, and `Hardware::CPU.intel?`.
- Use `uses_from_macos` when a dependency can come from macOS on supported versions but needs a Homebrew formula elsewhere.
- Avoid Homebrew options for new `homebrew/core` formulae. In private taps, prefer simple always-on behavior unless the user explicitly needs variants.

## Go Formulae

Use Homebrew's Go helper for source builds:

```ruby
system "go", "build", *std_go_args(output: bin/"project-name"), "."
```

`std_go_args` currently supplies `-trimpath` and an output path, with optional `ldflags`, `gcflags`, and `tags`.

For a `main` package below the repo root, pass that package path:

```ruby
system "go", "build", *std_go_args(output: bin/"project-name"), "./cmd/project-name"
```

## Completions and Man Pages

Use `generate_completions_from_executable` when the installed executable can generate shell completions:

```ruby
generate_completions_from_executable(bin/"project-name", "completion")
```

Install manual pages under `man1`, `man5`, or another `share/man` path exposed by Homebrew helpers:

```ruby
man1.install Dir["man/man1/*"]
```

## Caveats

Use `caveats` for setup instructions that are specific to the Homebrew package, non-standard paths, environment variables, service startup, or config files:

```ruby
def caveats
  <<~EOS
    Configuration file: #{etc}/project-name/config.yaml
  EOS
end
```

Keep caveats actionable. Do not repeat generic README content.

## Services

Use a `service` block when `brew services` should manage a launchd or systemd service.

For package-provided service files, install the file and provide the service name:

```ruby
service do
  name macos: "homebrew.mxcl.project-name"
end
```

For formula-defined services, use `run`:

```ruby
service do
  run [opt_bin/"project-name", "--config", etc/"project-name/config.yaml"]
end
```

## Tests

Homebrew prefers tests that exercise basic functionality without credentials, user input, network assumptions, or heavyweight services. `--help` and `--version` tests are weak, but better than no test when the tool cannot be exercised safely in the formula sandbox.

Use assertions around command output when possible:

```ruby
test do
  assert_match "expected text", shell_output("#{bin}/project-name --help")
end
```

For commands that return expected failures, pass the expected status to `shell_output`:

```ruby
test do
  assert_match "missing token", shell_output("#{bin}/project-name check 2>&1", 1)
end
```

## Validation Commands

Use these commands when available:

```bash
brew style Formula/project-name.rb
brew audit --strict --online --formula Formula/project-name.rb
brew install --build-from-source --verbose ./Formula/project-name.rb
brew test project-name
```

For new formulae intended for `homebrew/core`, also use `brew audit --new --formula`.
