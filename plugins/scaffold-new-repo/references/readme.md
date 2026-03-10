# README Template

Replace `PROJECT-NAME` with the exact binary or repository name (kebab-case), `SHORT-DESCRIPTION` with the one-sentence description, and `GITHUB-USERNAME` with the user's GitHub username.

```markdown
# PROJECT-NAME

SHORT-DESCRIPTION

## Installation

INSTALLATION-PLACEHOLDER

## Usage

TODO

## License

[MIT License](./LICENSE). TL;DR: Do whatever you want with this software, just keep the copyright notice included. The authors aren't liable if something goes wrong.
```

## Installation Placeholders by Project Type

Replace `INSTALLATION-PLACEHOLDER` with the body content below (the `## Installation` heading is already in the base template).

### Go CLI

````markdown
```bash
go install github.com/GITHUB-USERNAME/PROJECT-NAME@latest
```
````

### Go Library

````markdown
```bash
go get github.com/GITHUB-USERNAME/PROJECT-NAME
```
````

### Shell

````markdown
Clone the repository:

```bash
git clone https://github.com/GITHUB-USERNAME/PROJECT-NAME.git
```
````

### JavaScript

````markdown
```bash
npm install PROJECT-NAME
```
````

### Ruby

````markdown
```bash
gem install PROJECT-NAME
```
````

### Pascal

````markdown
Clone the repository:

```bash
git clone https://github.com/GITHUB-USERNAME/PROJECT-NAME.git
```
````

### Python

````markdown
```bash
uv run PROJECT-NAME
```
````

### Rust

````markdown
```bash
cargo install PROJECT-NAME
```
````

### Swift

````markdown
Add the dependency in your `Package.swift`:

```swift
dependencies: [
    .package(url: "https://github.com/GITHUB-USERNAME/PROJECT-NAME", from: "1.0.0")
]
```
````

### Generic

```markdown
TODO
```

## Notes

- The heading uses the exact binary or repository name (e.g., `# my-cool-tool`), not a titleized version.
- The description is a single sentence, not wrapped in a section header.
- The License section always uses the full blurb with the `[MIT License](./LICENSE)` link.
