---
name: add-community-files
description: >-
  Add standard community files to a project: CONTRIBUTING.md, CODE_OF_CONDUCT.md,
  SECURITY.md, and a pull request template. Use when the user says "add community
  files", "add contributing guide", "prepare for open source", "add code of
  conduct", "add security policy", or any variant involving adding community or
  open-source readiness files to a project.
---

# Add Community Files

Add standard community files to a project preparing for public release. Detects the project's build system and tooling to populate contribution guidelines with relevant setup, test, and lint commands.

**Files generated:**

| File                               | Description                          |
| ---------------------------------- | ------------------------------------ |
| `CONTRIBUTING.md`                  | Contribution guidelines              |
| `CODE_OF_CONDUCT.md`               | Contributor Covenant v3.0            |
| `.github/SECURITY.md`              | Security vulnerability report policy |
| `.github/PULL_REQUEST_TEMPLATE.md` | Pull request template                |

## Workflow

### 1. Gather Parameters

#### Auto-detect project identity

1. Run `git remote get-url origin` to get the remote URL.
1. Normalize the remote and extract owner/repo:
   - Strip any trailing `.git` suffix.
   - If the remote is SSH-style (e.g., `git@github.com:owner/repo`), convert the `host:` prefix to an HTTPS-style URL (e.g., `https://github.com/owner/repo`).
   - From the normalized URL, take the last two path segments as `GITHUB-OWNER/PROJECT-NAME`.
1. If no remote exists, fall back to the README.md H1 heading, then the directory name.
1. Store `PROJECT-NAME` and `GITHUB-OWNER/PROJECT-NAME` for placeholder substitution.

#### Detect contact method for Code of Conduct

1. Try `git config user.email`.
1. Ask the user which contact method to use for Code of Conduct reports:
   - Email address (pre-fill with the detected email)
   - GitHub Discussions URL: `https://github.com/GITHUB-OWNER/PROJECT-NAME/discussions`
   - GitHub Issues URL: `https://github.com/GITHUB-OWNER/PROJECT-NAME/issues`
1. Store the chosen value as `CONTACT-EMAIL`.

#### Detect build system

Scan for build system markers using Glob. Use the first match:

| Marker           | Build system | Install           | Build            | Test                    | Lint                  | Format                   |
| ---------------- | ------------ | ----------------- | ---------------- | ----------------------- | --------------------- | ------------------------ |
| `Makefile`       | Make         | (check targets)   | `make build`     | `make test`             | `make lint`           | `make fmt`               |
| `package.json`   | Node.js      | `npm install`     | `npm run build`  | `npm test`              | `npm run lint`        | `npm run format`         |
| `Cargo.toml`     | Cargo        | (none)            | `cargo build`    | `cargo test`            | `cargo clippy`        | `cargo fmt`              |
| `pyproject.toml` | Python (uv)  | `uv sync`         | (none)           | `uv run pytest`         | `uv run ruff check`   | `uv run ruff format`     |
| `go.mod`         | Go           | `go mod download` | `go build ./...` | `go test ./...`         | `golangci-lint run`   | `gofmt -w .`             |
| `Gemfile`        | Ruby         | `bundle install`  | (none)           | `bundle exec rake test` | `bundle exec rubocop` | `bundle exec rubocop -A` |

If a Makefile is present, read it and parse available target names. Use Makefile targets when they exist (they often wrap the underlying tool). For example, if both `go.mod` and a Makefile with `test` and `lint` targets exist, prefer `make test` and `make lint`.

If `package.json` is present, read the `scripts` object to discover available script names. Use the actual script names rather than guessing.

Detect linting tools from config files:

| Config file(s)                                 | Tool          |
| ---------------------------------------------- | ------------- |
| `.golangci.yml`, `.golangci.yaml`              | golangci-lint |
| `eslint.config.*`, `.eslintrc.*`               | ESLint        |
| `.prettierrc*`, `prettier.config.*`            | Prettier      |
| `ruff.toml`, `[tool.ruff]` in `pyproject.toml` | Ruff          |
| `.shellcheckrc`                                | ShellCheck    |
| `clippy.toml`, `.clippy.toml`                  | Clippy        |
| `.rubocop.yml`                                 | RuboCop       |

Store detected commands for use in templates:

- `INSTALL-COMMAND`
- `BUILD-COMMAND`
- `TEST-COMMAND`
- `LINT-COMMAND`
- `FORMAT-COMMAND`
- `REQUIREMENT-LIST` (language runtime version, required tools)

### 2. Check Existing Files

Check whether each target file already exists:

| File               | Path                                 |
| ------------------ | ------------------------------------ |
| CONTRIBUTING.md    | `./CONTRIBUTING.md`                  |
| CODE_OF_CONDUCT.md | `./CODE_OF_CONDUCT.md`               |
| SECURITY.md        | `./.github/SECURITY.md`              |
| PR template        | `./.github/PULL_REQUEST_TEMPLATE.md` |

For each file that exists, ask the user before overwriting.

If `.github/` does not exist, create it.

Report findings to the user before proceeding.

### 3. Generate CONTRIBUTING.md

1. Read `./references/contributing.md`.
1. Substitute all placeholders (`PROJECT-NAME`, `GITHUB-OWNER`, etc.) with detected values.
1. Fill the Development Setup section with detected build commands:
   - Replace `REQUIREMENT-LIST` with detected language runtime and tools.
   - Replace `INSTALL-COMMAND`, `BUILD-COMMAND`, `TEST-COMMAND`, `LINT-COMMAND`, and `FORMAT-COMMAND` with detected commands.
   - If a command is not applicable (e.g., no separate build step), remove that line.
1. Adapt the Code Style section to reference the detected linting/formatting tools.
1. Remove the `## Notes` section (it is documentation for the template, not for the output file).
1. Write to `./CONTRIBUTING.md`.

### 4. Generate CODE_OF_CONDUCT.md

1. Read `./references/code-of-conduct.md`.
1. Substitute `CONTACT-EMAIL` with the user's chosen contact method.
1. Remove the `## Notes` section.
1. Write to `./CODE_OF_CONDUCT.md`.

### 5. Generate .github/SECURITY.md

1. Read `./references/security.md`.
1. Optionally adapt the "What Qualifies" section based on project type (e.g., add "container escape vulnerabilities" for container tools, "credential exposure" for CLI tools that handle secrets).
1. Remove the `## Notes` section.
1. Write to `./.github/SECURITY.md`.

### 6. Generate .github/PULL_REQUEST_TEMPLATE.md

1. Read `./references/pr-template.md`.
1. Adapt the checklist:
   - If a specific test command was detected, reference it in the "tests pass" item (e.g., "All new and existing tests pass (`make test`)").
   - If a `CHANGELOG.md` exists in the project, add: "I have updated \[CHANGELOG](../CHANGELOG.md) if this is a user-facing change".
1. Remove the `## Notes` section.
1. Write to `./.github/PULL_REQUEST_TEMPLATE.md`.

### 7. Summary

Print a summary table:

```text
| File                                | Status  |
| ----------------------------------- | ------- |
| CONTRIBUTING.md                     | Created |
| CODE_OF_CONDUCT.md                  | Created |
| .github/SECURITY.md                | Created |
| .github/PULL_REQUEST_TEMPLATE.md   | Created |
```

Use "Created", "Skipped (exists)", or "Updated" as appropriate.

Suggest next steps:

- Review each file and customize project-specific sections
- Commit the new files
- Consider enabling GitHub Discussions if using that as the CoC contact method
- Run `/lint-and-fix` to check formatting

## Error Handling

- **No git remote:** Use the directory name as `PROJECT-NAME` and ask the user for the GitHub owner.
- **No build system detected:** Use generic placeholders (`YOUR-INSTALL-COMMAND`, etc.) and warn the user to fill them in manually.
- **Write permission failures:** Report which files failed and suggest checking file permissions.
