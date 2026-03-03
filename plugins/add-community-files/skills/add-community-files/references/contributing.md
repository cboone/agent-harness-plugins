<!-- markdownlint-disable relative-links -->
<!-- This is a template file; relative links target the destination project. -->

# Contributing to PROJECT-NAME

Thank you for your interest in contributing to PROJECT-NAME.

Please note that this project has a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold it.

## Reporting Issues

- **Bug reports and feature requests:** Use the [issue tracker](https://github.com/GITHUB-OWNER/PROJECT-NAME/issues/new/choose)
- **Questions and ideas:** Use [GitHub Discussions](https://github.com/GITHUB-OWNER/PROJECT-NAME/discussions)
- **Security vulnerabilities:** See [SECURITY.md](.github/SECURITY.md)

## Development Setup

### Requirements

- REQUIREMENT-LIST

### Getting Started

```bash
# Clone the repository
git clone https://github.com/GITHUB-OWNER/PROJECT-NAME.git
cd PROJECT-NAME

# Install dependencies
INSTALL-COMMAND

# Build
BUILD-COMMAND

# Run tests
TEST-COMMAND

# Run linter
LINT-COMMAND
```

## Code Style

- Run `LINT-COMMAND` before committing
- Run `FORMAT-COMMAND` to format code

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```text
<type>: <description>
```

**Types:**

- `feat`: new feature
- `fix`: bug fix
- `docs`: documentation changes
- `refactor`: code refactoring (no functional change)
- `test`: adding or updating tests
- `build`: build system or dependency changes
- `ci`: CI configuration changes
- `chore`: maintenance tasks

**Examples:**

```text
feat: add user authentication endpoint
fix: resolve race condition in worker pool
docs: update installation instructions
refactor: simplify configuration loading
test: add unit tests for validation logic
chore: update linter to latest version
```

## Pull Request Process

1. Fork the repository
1. Create a feature branch
1. Make your changes
1. Ensure tests pass: `TEST-COMMAND`
1. Ensure linting passes: `LINT-COMMAND`
1. Submit a pull request

### Branch Naming

Use descriptive branch names with a type prefix:

- `feature/*`: new features
- `fix/*`: bug fixes
- `docs/*`: documentation changes
- `refactor/*`: code refactoring
- `test/*`: test additions or fixes

## Notes

This template contains the following placeholders for substitution:

| Placeholder        | Replace with                              |
| ------------------ | ----------------------------------------- |
| `PROJECT-NAME`     | Repository/project name                   |
| `GITHUB-OWNER`     | GitHub owner (user or organization)       |
| `REQUIREMENT-LIST` | Language runtime, tools, and dependencies |
| `INSTALL-COMMAND`  | Dependency install command                |
| `BUILD-COMMAND`    | Build command                             |
| `TEST-COMMAND`     | Test command                              |
| `LINT-COMMAND`     | Lint command                              |
| `FORMAT-COMMAND`   | Format command                            |

The SKILL.md workflow instructs the agent to detect the project's build system
and fill these in automatically:

- **Makefile projects:** `make build`, `make test`, `make lint`, `make fmt`
- **Node projects:** `npm install`, `npm test`, `npm run lint`
- **Cargo projects:** `cargo build`, `cargo test`, `cargo clippy`
- **Python projects:** `uv sync`, `uv run pytest`, `uv run ruff check`
- **Go module projects:** `go build ./...`, `go test ./...`, `golangci-lint run`

If no build system is detected, leave generic placeholders and warn the user.
