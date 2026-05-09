# Add Community Files

Add standard community files to a project preparing for public release: CONTRIBUTING.md, CODE_OF_CONDUCT.md, .github/SECURITY.md, and a pull request template.

**Type:** Skill
**Trigger:** `/add-community-files`

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Detects the project's build system (Makefile, package.json, Cargo.toml, pyproject.toml, go.mod, Gemfile) and populates contribution guidelines with relevant setup, build, test, and lint commands. Generates four files:

- **CONTRIBUTING.md**: contribution guidelines with development setup, code style, commit message conventions, and pull request process
- **CODE_OF_CONDUCT.md**: Contributor Covenant v3.0 with a configurable contact method
- **.github/SECURITY.md**: security vulnerability reporting policy using GitHub's private reporting
- **.github/PULL_REQUEST_TEMPLATE.md**: pull request template with description, type of change, and checklist

Checks for existing files before writing and asks before overwriting.

## Usage

```text
/add-community-files
```

## Examples

- "add community files": generate all four files
- "add contributing guide": same behavior
- "prepare for open source": same behavior
- "add code of conduct": same behavior
- "add security policy": same behavior

## See Also

- [Scaffold New Repo](../scaffold-new-repo/README.md): foundational repo boilerplate (LICENSE, README, .gitignore)
- [Set-Up Linters](../set-up-linters/README.md): linter and formatter setup
- [Bootstrap Project](../bootstrap-project/README.md): full project assessment and setup
- [All plugins](../../../../README.md)
