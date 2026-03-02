# 2026-03-01 Create `bootstrap-project` skill

## Context

We have many scaffolding and setup commands/skills that each handle one aspect of project setup: `scaffold-new-repo`, `scaffold-go-cli`, `scaffold-go-library`, `setup-ci`, `setup-gitleaks`, `setup-linters`, `setup-installers`, `add-goreleaser-homebrew`, and `add-scrut-cli-tests`. Currently, users must know which ones to run, in what order, and which overlap. This skill will assess a repository, determine what is needed, present a plan, and execute all applicable tools in the correct order.

## Design decisions

- **Name**: `bootstrap-project`
- **Type**: Skill (not command), to allow reasoning during assessment
- **Approval flow**: Assess, present plan, wait for user approval, then execute
- **Scope**: Both brand-new and existing repos

## Files to create

### 1. `plugins/bootstrap-project/.claude-plugin/plugin.json`

Standard plugin.json with `"skills": "./skills"`, version `1.0.0`.

### 2. `plugins/bootstrap-project/skills/bootstrap-project/SKILL.md`

The main skill file. Frontmatter with trigger phrases like "bootstrap this project", "set up everything", "scaffold everything", "full project setup".

**Workflow**:

#### Step 1: Detect project type

Scan for language markers (reuse the detection table from `setup-ci` and `setup-linters`):

| Marker                                           | Type                                        |
| ------------------------------------------------ | ------------------------------------------- |
| `go.mod` + (`main.go` or `cmd/`)                 | Go CLI                                      |
| `go.mod` without main.go/cmd/                    | Go library                                  |
| `package.json` + JS/TS source files              | JavaScript/TypeScript                       |
| `pyproject.toml`, `setup.py`, `requirements.txt` | Python                                      |
| `Cargo.toml`                                     | Rust                                        |
| `Gemfile`, `*.gemspec`                           | Ruby                                        |
| `*.sh`, `bin/*`, `scripts/*`                     | Shell                                       |
| No recognizable files                            | New/empty repo (ask user for intended type) |

#### Step 2: Detect existing infrastructure

Check for files/directories that indicate what is already set up:

| Check                            | Indicates               | Provided by                               |
| -------------------------------- | ----------------------- | ----------------------------------------- |
| `LICENSE`                        | License exists          | scaffold-new-repo                         |
| `README.md`                      | README exists           | scaffold-new-repo                         |
| `CHANGELOG.md`                   | Changelog exists        | scaffold-new-repo                         |
| `AGENTS.md` or `CLAUDE.md`       | Agent config exists     | scaffold-new-repo                         |
| `.github/workflows/ci.yml`       | CI exists               | setup-ci / scaffold-go-\*                 |
| `.github/workflows/release.yml`  | Release workflow exists | scaffold-go-\* / add-goreleaser-homebrew  |
| `.github/workflows/gitleaks.yml` | Gitleaks exists         | setup-gitleaks                            |
| `.goreleaser.yml`                | GoReleaser exists       | scaffold-go-cli / add-goreleaser-homebrew |
| `Makefile`                       | Build targets exist     | scaffold-go-\* / setup-ci                 |
| Linter config files              | Linters exist           | setup-linters / scaffold-go-library       |
| `tests/scrut/`                   | Scrut tests exist       | add-scrut-cli-tests                       |
| `install.sh` or `Formula/`       | Installers exist        | setup-installers                          |

#### Step 3: Build the plan

Using overlap rules from `references/overlap-rules.md`, determine which tools to run. Key overlap rules:

- If `scaffold-go-cli` will run: skip `setup-ci`, skip `add-goreleaser-homebrew` (both are included)
- If `scaffold-go-library` will run: skip `setup-ci` (included); `add-goreleaser-homebrew` and `setup-installers` are not applicable for libraries
- If a Go scaffolder runs: still run `setup-linters` but only for cross-language tools (Prettier, EditorConfig, markdownlint) since Go-specific linters are already configured
- `setup-gitleaks` is always independent (no overlap with other tools)
- `add-scrut-cli-tests` is applicable only if the project produces a CLI binary

Execution order (dependencies flow downward):

1. `scaffold-new-repo` (foundation: LICENSE, README, .gitignore, agent config)
1. `scaffold-go-cli` OR `scaffold-go-library` (language-specific scaffolding, if applicable)
1. `setup-ci` (if not already covered by step 2)
1. `setup-linters` (cross-language tools, or full setup if no Go scaffolder ran)
1. `setup-gitleaks` (secret scanning)
1. `add-goreleaser-homebrew` (if Go CLI and not already covered by step 2)
1. `setup-installers` (if CLI project)
1. `add-scrut-cli-tests` (if CLI project)

#### Step 4: Present the plan to user

Show a table with each tool, its status (Already set up / Will run / Skipped / Not applicable), and what it will do. Ask user to confirm or deselect items.

#### Step 5: Execute

Invoke each confirmed tool in order:

- For **skills** (`setup-linters`): use the `Skill` tool
- For **commands** (`scaffold-new-repo`, `scaffold-go-cli`, etc.): use the `Skill` tool (commands are also registered as slash commands)

Between each invocation, verify success before proceeding to the next tool.

#### Step 6: Summary

Print a summary of everything that was set up, any issues encountered, and suggested next steps (like running `lint-and-fix` or making an initial commit).

### 3. `plugins/bootstrap-project/skills/bootstrap-project/references/overlap-rules.md`

Reference file documenting the overlap rules between tools as a decision table. Structured as "if X runs, then skip/scope-down Y" entries.

### 4. `plugins/bootstrap-project/README.md`

Standard per-plugin README following the existing pattern (Type, Trigger, Installation, What It Does, Usage, See Also).

## Files to modify

### 5. `.claude-plugin/marketplace.json`

- Add `bootstrap-project` entry (alphabetically, between `block-rm-rf` and `clean-up-agent-config`)
- Bump `metadata.version` from `1.17.0` to `1.18.0`

### 6. `README.md` (root)

- Add to ToC under **Skills > Scaffolding** (new subcategory)
- Add description section under Skills

### 7. `CLAUDE.md`

- Add `bootstrap-project/` to the directory tree

## Verification

1. Check that `plugin.json` version matches `marketplace.json` entry
1. Verify the skill triggers on `/bootstrap-project` and on phrases like "bootstrap this project"
1. Test against a brand-new empty repo: should offer the full pipeline
1. Test against an existing Go CLI project with CI already set up: should skip `setup-ci` and `scaffold-go-cli`, offer only the missing pieces
1. Run `/check-versions` to verify version consistency
