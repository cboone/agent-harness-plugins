# README Template

Use this template for the project `README.md`. Replace `PROJECT-NAME` (kebab-case), `PROJECT-DESCRIPTION`, and `GITHUB-USERNAME` with the actual values.

````markdown
# PROJECT-NAME

PROJECT-DESCRIPTION

## Installation

### Homebrew

```bash
brew install GITHUB-USERNAME/tap/PROJECT-NAME
```

### cargo install

```bash
cargo install --git https://github.com/GITHUB-USERNAME/PROJECT-NAME
```

### From release

Download a binary from the [releases page](https://github.com/GITHUB-USERNAME/PROJECT-NAME/releases).

## Usage

```bash
PROJECT-NAME
```

## License

[MIT](LICENSE)
````

## Notes

- The heading uses the exact binary/repository name in kebab-case
- The one-liner description matches what was provided for `Cargo.toml`
- Installation section covers three methods: Homebrew, `cargo install`, and release binary
- Homebrew installation requires a Homebrew tap to be set up (see `/setup-installers`)
- Usage section is a placeholder for the user to fill in
