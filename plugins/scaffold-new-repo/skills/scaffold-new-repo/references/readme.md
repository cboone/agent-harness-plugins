# README.md Template

Replace `PROJECT-NAME` with the project name in title case and `SHORT-DESCRIPTION` with the one-sentence description.

````markdown
# PROJECT-NAME

SHORT-DESCRIPTION

## Installation

INSTALLATION-PLACEHOLDER

## Usage

TODO

## License

[MIT License](./LICENSE). TL;DR: Do whatever you want with this software, just keep the copyright notice included. The authors aren't liable if something goes wrong.
````

## Installation Placeholders by Project Type

Use the appropriate placeholder based on the project type:

### Go CLI

```markdown
## Installation

```bash
go install github.com/cboone/PROJECT-NAME@latest
```
```

### Go Library

```markdown
## Installation

```bash
go get github.com/cboone/PROJECT-NAME
```
```

### Shell

```markdown
## Installation

Clone the repository:

```bash
git clone https://github.com/cboone/PROJECT-NAME.git
```
```

### JavaScript

```markdown
## Installation

```bash
npm install PROJECT-NAME
```
```

### Ruby

```markdown
## Installation

```bash
gem install PROJECT-NAME
```
```

### Generic

```markdown
## Installation

TODO
```

## Notes

- The heading uses the project name in title case (e.g., `my-cool-tool` becomes `My Cool Tool`).
- The description is a single sentence, not wrapped in a section header.
- The License section always uses the full blurb with the `[MIT License](./LICENSE)` link.
