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

Replace `INSTALLATION-PLACEHOLDER` with the body content below (the `## Installation` heading is already in the base template).

### Go CLI

````markdown
```bash
go install github.com/cboone/PROJECT-NAME@latest
```
````

### Go Library

````markdown
```bash
go get github.com/cboone/PROJECT-NAME
```
````

### Shell

````markdown
Clone the repository:

```bash
git clone https://github.com/cboone/PROJECT-NAME.git
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

### Generic

```markdown
TODO
```

## Notes

- The heading uses the project name in title case (e.g., `my-cool-tool` becomes `My Cool Tool`).
- The description is a single sentence, not wrapped in a section header.
- The License section always uses the full blurb with the `[MIT License](./LICENSE)` link.
