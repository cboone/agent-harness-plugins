# README Template

Use this template for the project `README.md`. Replace `PROJECT-NAME` (kebab-case), `PROJECT-DESCRIPTION`, `GITHUB-USERNAME`, and `ZIG-VERSION` with the actual values.

````markdown
# PROJECT-NAME

PROJECT-DESCRIPTION

## Installation

### Homebrew

```bash
brew install GITHUB-USERNAME/tap/PROJECT-NAME
```

### From source

```bash
git clone https://github.com/GITHUB-USERNAME/PROJECT-NAME.git
cd PROJECT-NAME
zig build -Doptimize=ReleaseSafe
```

The binary will be at `zig-out/bin/PROJECT-NAME`.

### From release

Download a binary from the [releases page](https://github.com/GITHUB-USERNAME/PROJECT-NAME/releases).

## Usage

```bash
PROJECT-NAME --help
```

## Development

Requires Zig ZIG-VERSION. `build.zig.zon`'s `minimum_zig_version` is the single source of truth, and CI and the release workflow both read it rather than restating the version, so that is the toolchain the project is built and tested against. Zig is pre-1.0 and each minor release breaks the standard library, so treat a newer Zig as an upgrade to make deliberately rather than a version that happens to work.

Homebrew's `zig` formula is unpinned and moves to the next minor release on upgrade, which will not match this project's pin. Install Zig from [ziglang.org/download](https://ziglang.org/download/) or through a version manager instead.

```bash
make check   # format check, build and tests: run this before pushing
make help    # list every target
```

## License

[MIT](LICENSE)
````

## Notes

- The heading uses the exact binary and repository name in kebab-case.
- The one-liner description matches what was provided for the project.
- The installation section covers three methods: Homebrew, from source, and a release binary. Zig has no equivalent of `go install` or `cargo install`, so building from source is the fallback.
- Homebrew installation requires a Homebrew tap to be set up (see `/set-up-installers`).
- The Development section carries the Homebrew warning on purpose. Homebrew's Zig floats to the next minor version on `brew upgrade`, and Zig is pre-1.0 with breaking stdlib changes in every minor release, so an upgraded Homebrew Zig stops compiling the project without anything in the repository having changed.
- The Usage section is a placeholder for the user to fill in.
