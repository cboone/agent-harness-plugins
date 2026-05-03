# Formula Patterns

These templates show shapes to adapt, not complete formulae to paste unchanged. Replace placeholders, verify licenses, and validate the result with Homebrew.

## Stable Prebuilt Binary

Use this when GitHub Releases or another stable source publishes archives that already contain binaries.

```ruby
class ProjectName < Formula
  desc "Short project description"
  homepage "https://github.com/OWNER/project-name"
  version "0.1.0"
  license "MIT"

  on_macos do
    on_intel do
      url "https://github.com/OWNER/project-name/releases/download/v0.1.0/project-name-0.1.0-darwin-amd64.tar.gz"
      sha256 "SHA256_FOR_DARWIN_AMD64"
    end

    on_arm do
      url "https://github.com/OWNER/project-name/releases/download/v0.1.0/project-name-0.1.0-darwin-arm64.tar.gz"
      sha256 "SHA256_FOR_DARWIN_ARM64"
    end
  end

  def install
    bin.install "project-name"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/project-name --version")
  end
end
```

Add `on_linux` blocks when Linux release assets exist. Use `depends_on :macos` when the project is macOS-only.

## Stable Go Source Build

Use this when the formula should build from a tagged source archive.

```ruby
class ProjectName < Formula
  desc "Short project description"
  homepage "https://github.com/OWNER/project-name"
  url "https://github.com/OWNER/project-name/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "SHA256_FOR_SOURCE_TARBALL"
  license "MIT"

  depends_on "go" => :build

  def install
    system "go", "build", *std_go_args(output: bin/"project-name"), "."
  end

  test do
    assert_match "project-name", shell_output("#{bin}/project-name --help")
  end
end
```

If the command lives below the repository root, replace `"."` with a package path such as `"./cmd/project-name"`.

## HEAD-only Go Source Build

Use this when no tagged release exists or the user intentionally wants a development build.

```ruby
class ProjectName < Formula
  desc "Short project description"
  homepage "https://github.com/OWNER/project-name"
  head "https://github.com/OWNER/project-name.git", branch: "main"
  license "MIT"

  depends_on "go" => :build

  def install
    system "go", "build", *std_go_args(output: bin/"project-name"), "./cmd/project-name"
  end

  test do
    assert_match "project-name", shell_output("#{bin}/project-name --help")
  end
end
```

Do not add stable `url` or `sha256` unless a stable source exists.

## GoReleaser-generated Formula Review

For GoReleaser-managed formulae, inspect these surfaces:

- Generated-file header, if GoReleaser emits one
- `desc`, `homepage`, `version`, and `license`
- Platform and architecture URL blocks
- Runtime dependencies
- Installed binaries
- Completions, man pages, and config assets included in release archives
- Caveats and tests

Prefer changing `.goreleaser.yml` in the source repository when generated output is wrong. Hand edits to generated formulae should be reserved for cases where the tap intentionally owns a manual override.

## Shell Tool with Config and Service

Use this when the package installs scripts and service assets instead of compiling a binary.

```ruby
class ProjectName < Formula
  desc "Short project description"
  homepage "https://github.com/OWNER/project-name"
  url "https://github.com/OWNER/project-name/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "SHA256_FOR_SOURCE_TARBALL"
  license "MIT"

  depends_on "dependency-name"

  def install
    bin.install "scripts/project-name"
    zsh_completion.install "completions/_project-name" if File.exist?("completions/_project-name")
    (share/"project-name").install "config/project-name.conf.example"
    prefix.install "LaunchAgents/homebrew.mxcl.project-name.plist"
  end

  def caveats
    <<~EOS
      Configuration example:
        #{share}/project-name/project-name.conf.example

      To start the service:
        brew services start project-name
    EOS
  end

  service do
    name macos: "homebrew.mxcl.project-name"
  end

  test do
    assert_match "project-name", shell_output("#{bin}/project-name --help")
  end
end
```

Use `post_install` only when the formula must initialize user-visible state after installation. Prefer installing examples and explaining setup in `caveats` when that is enough.
