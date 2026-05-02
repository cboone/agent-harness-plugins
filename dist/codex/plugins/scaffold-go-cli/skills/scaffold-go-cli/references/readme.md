# README Template

Use this template for the project `README.md`. Replace `PROJECT-NAME` (kebab-case), `PROJECT-DESCRIPTION`, and `GITHUB-USERNAME` with the actual values.

````markdown
# PROJECT-NAME

PROJECT-DESCRIPTION

## Installation

### Homebrew

```sh
brew install GITHUB-USERNAME/tap/PROJECT-NAME
```

### From source

```sh
go install github.com/GITHUB-USERNAME/PROJECT-NAME@latest
```

### From release

Download a binary from the [releases page](https://github.com/GITHUB-USERNAME/PROJECT-NAME/releases).

### Build locally

```sh
git clone https://github.com/GITHUB-USERNAME/PROJECT-NAME.git
cd PROJECT-NAME
make build
./bin/PROJECT-NAME
```

## Usage

```sh
PROJECT-NAME
```

## License

[MIT License](./LICENSE). TL;DR: Do whatever you want with this software, just keep the copyright notice included. The authors aren't liable if something goes wrong.
````

## Notes

- The heading uses the exact binary/repository name in kebab-case (e.g., `# gh-problemas`, `# my-tool`)
- The one-liner description matches what was provided for `go.mod` and GoReleaser
- Installation section covers all four install methods: Homebrew, `go install`, release binary, and local build
- Usage section is a placeholder for the user to fill in
- License section uses the standard MIT license wording
