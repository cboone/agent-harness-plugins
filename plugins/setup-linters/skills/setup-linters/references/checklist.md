# Checklist

Quick-reference lookup table for the setup-linters skill. Each row maps a project type to its recommended tools, install commands, config files, and package manager scripts.

## Language-Specific Linters

| Language      | Tools                                            | Install Command                                                                                                                                                                             | Config Files                                       | Scripts / Targets            | Reference                   |
| ------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | ---------------------------- | --------------------------- |
| JavaScript/TS | ESLint + Prettier + plugins                      | `npm install -D eslint @eslint/js @eslint/json eslint-config-prettier eslint-plugin-import eslint-plugin-unicorn eslint-plugin-promise eslint-plugin-regexp eslint-plugin-security globals` | `eslint.config.js`, `.prettierrc.json`             | `lint`, `format`, `lint:fix` | `./languages/javascript.md` |
| Go            | golangci-lint + gofmt + goimports                | `brew install golangci-lint`                                                                                                                                                                | `.golangci.yml`                                    | `lint`, `fmt`, `vet`         | `./languages/go.md`         |
| Python        | Ruff                                             | `uv add --dev ruff`                                                                                                                                                                         | `pyproject.toml` `[tool.ruff]`                     | `lint`, `format`             | `./languages/python.md`     |
| Rust          | clippy + rustfmt                                 | _(built-in, no install)_                                                                                                                                                                    | `rustfmt.toml`                                     | `cargo clippy`, `cargo fmt`  | `./languages/rust.md`       |
| Ruby          | RuboCop                                          | `bundle add rubocop --group development`                                                                                                                                                    | `.rubocop.yml`                                     | `rubocop`, `rubocop -a`      | `./languages/ruby.md`       |
| Shell         | ShellCheck + shfmt                               | `brew install shellcheck shfmt`                                                                                                                                                             | `.shellcheckrc`, `.editorconfig`                   | `lint`, `fmt`                | `./languages/shell.md`      |
| Zsh           | shellcheck + shfmt + shellharden + checkbashisms | `brew install shellcheck shfmt shellharden devscripts`                                                                                                                                      | `.shellcheckrc`, `.editorconfig`                   | `check-zsh`, `format-zsh`    | `./languages/zsh.md`        |
| Swift         | SwiftLint + SwiftFormat                          | `brew install swiftlint swiftformat`                                                                                                                                                        | `.swiftlint.yml`, `.swiftformat`, `.swift-version` | `lint`, `fmt`, `lint-fix`    | `./languages/swift.md`      |

## Cross-Language and File-Type Tools

| Tool              | Scope                           | When to Offer                                                 | Install Command                                      | Config Files                          | Reference                 |
| ----------------- | ------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------- | ------------------------------------- | ------------------------- |
| Prettier          | JSON, YAML, Markdown, CSS, HTML | All projects                                                  | `npm install -D prettier`                            | `.prettierrc.json`, `.prettierignore` | `./tools/prettier.md`     |
| EditorConfig      | All file types                  | All projects                                                  | _(no install, editor support built-in)_              | `.editorconfig`                       | `./tools/editorconfig.md` |
| markdownlint-cli2 | Markdown files                  | All projects with `*.md` files                                | `npm install -D markdownlint-cli2`                   | `.markdownlint-cli2.jsonc`            | `./tools/markdownlint.md` |
| Stylelint         | CSS/SCSS/Less                   | When CSS/SCSS/Less files detected                             | `npm install -D stylelint stylelint-config-standard` | `.stylelintrc.json`                   | `./tools/stylelint.md`    |
| Knip              | Unused JS deps/exports          | When `package.json` detected **and** JS/TS source files exist | `npm install -D knip`                                | `knip.json`                           | `./tools/knip.md`         |
| Hadolint          | Dockerfiles                     | When `Dockerfile` detected                                    | `brew install hadolint`                              | `.hadolint.yaml`                      | `./tools/hadolint.md`     |
| Actionlint        | GitHub Actions workflows        | When `.github/workflows/` detected                            | `brew install actionlint`                            | _(none needed)_                       | `./tools/actionlint.md`   |
| Taplo             | TOML files                      | When `*.toml` files detected                                  | `brew install taplo`                                 | `taplo.toml` (optional)               | `./tools/taplo.md`        |
| yamllint          | YAML files                      | When project has many YAML files                              | `uv tool install yamllint`                           | `.yamllint.yml`                       | `./tools/yamllint.md`     |
| cspell            | Spelling in code/docs           | All projects                                                  | `npm install -D cspell`                              | `cspell.json`                         | `./tools/cspell.md`       |

## CI Integration

| Scope             | Reference                      |
| ----------------- | ------------------------------ |
| GitHub Actions CI | `./tools/github-actions-ci.md` |
