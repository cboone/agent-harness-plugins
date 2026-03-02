# Create `setup-ci` Command Plugin

## Context

CI setup is currently scattered across multiple plugins: `scaffold-go-cli` and `scaffold-go-library` create CI workflows during project scaffolding, `setup-linters` can optionally create lint CI, and `setup-gitleaks` handles secret scanning. There is no single command to add CI to an existing project that already has code but no GitHub Actions workflows.

This command fills that gap: detect the project's language(s), create a GitHub Actions CI workflow with appropriate parallel jobs (test, lint, format, vulnerability check), and create matching Makefile targets for local development.

## Scope

**In scope:**

- CI workflow (`.github/workflows/ci.yml`) with test, lint, format, and vuln check jobs
- Makefile targets matching the CI jobs
- Language detection: Go CLI, Go library, JavaScript/TypeScript, Python, Rust, Ruby, Shell
- Multi-language projects (monorepo-style combined workflow)
- Suggesting complementary plugins (`/setup-gitleaks`, `/setup-linters`, `/add-scrut-cli-tests`)

**Out of scope:**

- Release workflows (suggest `/add-goreleaser-homebrew` instead)
- Gitleaks setup (suggest `/setup-gitleaks` instead)
- Linter config files (suggest `/setup-linters` instead)
- Test file creation
- Docker/deployment CI
- Multi-OS matrix testing
- Code coverage upload

## Files to Create

```text
plugins/setup-ci/
├── .claude-plugin/
│   └── plugin.json
├── README.md
└── commands/
    └── setup-ci.md
```

## Files to Modify

- `.claude-plugin/marketplace.json`: add plugin entry, bump `metadata.version` from `1.16.0` to `1.17.0`
- `README.md`: add to ToC and Commands > Scaffolding section
- `CLAUDE.md`: add to directory tree

## Implementation

### 1. `plugins/setup-ci/.claude-plugin/plugin.json`

Standard command plugin manifest with `"commands": "./commands"`. Version `1.0.0`.

### 2. `plugins/setup-ci/commands/setup-ci.md`

Frontmatter: `disable-model-invocation: true`, description.

#### Workflow Steps

**Step 1. Detect project type.** Scan for language markers (same detection table as `setup-linters` SKILL.md lines 20-34):

| Marker                                             | Language              |
| -------------------------------------------------- | --------------------- |
| `go.mod`                                           | Go                    |
| `package.json` + source files                      | JavaScript/TypeScript |
| `pyproject.toml` / `setup.py` / `requirements.txt` | Python                |
| `Cargo.toml`                                       | Rust                  |
| `Gemfile` / `*.gemspec`                            | Ruby                  |
| `*.sh` / `bin/*` / `scripts/*`                     | Shell                 |

Go sub-detection: `main.go` or `cmd/` directory = CLI, otherwise = library.
JS/TS sub-detection: lockfile type determines package manager (npm/yarn/pnpm/bun).

If multiple languages detected, create a multi-language workflow with one job per language.

**Step 2. Check for existing CI.** Look for `.github/workflows/ci.yml` and other workflow files. If CI exists, present it and ask: overwrite, merge missing jobs, or abort.

**Step 3. Check for existing Makefile.** Scan for existing CI-relevant targets (`test:`, `lint:`, `fmt:`, `vet:`, `vuln:`, `build:`). Report which exist and which will be added. If no Makefile, offer to create one.

**Step 4. Create CI workflow.** Generate `.github/workflows/ci.yml` from the appropriate language template (see Reference sections below). All templates share:

- Triggers: push to main, pull requests targeting main
- `permissions: contents: read`
- Separate parallel jobs
- `actions/checkout@v6`

**Step 5. Create or update Makefile targets.** Add missing targets that the CI workflow references. Only add targets that do not already exist. Ask before modifying existing targets.

**Step 6. Summary.** List files created/modified. Suggest:

- `/setup-gitleaks` for secret scanning
- `/setup-linters` for linter configuration (if no linter configs detected)
- `/add-scrut-cli-tests` for CLI snapshot testing (if CLI project detected)
- `/add-goreleaser-homebrew` for release automation (if Go project detected)

#### Reference Templates

The command file includes these inline Reference sections:

1. **Go CLI CI Workflow** (3 parallel jobs: test, lint, vulncheck). Based on `scaffold-go-cli/commands/scaffold-go-cli.md` lines 592-654. Uses `make test`, `make vet`, `make fmt`, `govulncheck`.

1. **Go Library CI Workflow** (5 parallel jobs: test with version matrix, lint via golangci-lint, build, format, vulncheck). Based on `scaffold-go-library/commands/scaffold-go-library.md` lines 628-726. `MINIMUM-GO-VERSION` placeholder.

1. **JavaScript/TypeScript CI Workflow** (jobs: test, lint, format, optional typecheck). Based on `setup-linters` GitHub Actions CI reference. Uses `actions/setup-node@v4`, detected package manager.

1. **Python CI Workflow** (jobs: test, lint, format). Uses `astral-sh/setup-uv@v5`, ruff.

1. **Rust CI Workflow** (jobs: test, lint, format, build). Uses `dtolnay/rust-toolchain@stable`, `Swatinem/rust-cache@v2`.

1. **Ruby CI Workflow** (jobs: test, lint). Uses `ruby/setup-ruby@v1`.

1. **Shell CI Workflow** (jobs: lint). Uses ShellCheck action + shfmt.

1. **Multi-Language CI Workflow** pattern: combine language-specific jobs into one workflow file.

1. **Makefile Templates** per language: Go CLI (adapted from scaffold-go-cli), Go Library (adapted from scaffold-go-library), JS/TS (`npm test`/`npm run lint`), Python (uv + ruff), Rust (cargo), Ruby (bundle exec), Shell (shellcheck + shfmt).

#### Error Handling

- Not a git repo: warn, suggest `git init`, continue
- No language detected: offer generic workflow with checkout + `make test`/`make lint`
- Existing CI: ask before overwriting (covered in step 2)
- Missing Makefile: offer to create; if declined, note that CI will fail without targets

### 3. `plugins/setup-ci/README.md`

Per-plugin README following the standard template. Type: Command. Trigger: `/setup-ci`. See Also links to setup-gitleaks, setup-linters, scaffold-go-cli, scaffold-go-library.

### 4. Registry and Docs Updates

**marketplace.json:** Add `setup-ci` entry (category: `"productivity"`, version: `"1.0.0"`). Bump `metadata.version` to `"1.17.0"`.

**README.md ToC:** Add under Commands > Scaffolding, between "Setup Gitleaks" and "Setup Installers":

```markdown
∙ [Setup CI](#setup-ci)
```

**README.md body:** Add `#### Setup CI` section in Commands > Scaffolding.

**CLAUDE.md:** Add `setup-ci/` to the directory tree.

## Key Patterns to Reuse

- Command structure: `plugins/setup-gitleaks/commands/setup-gitleaks.md` (frontmatter, workflow steps, references, error handling)
- Go CLI CI template: `plugins/scaffold-go-cli/commands/scaffold-go-cli.md` lines 592-654
- Go Library CI template: `plugins/scaffold-go-library/commands/scaffold-go-library.md` lines 628-726
- Non-Go CI snippets: `plugins/setup-linters/skills/setup-linters/references/tools/github-actions-ci.md`
- Language detection: `plugins/setup-linters/skills/setup-linters/SKILL.md` lines 20-34

## Verification

1. Run `/setup-ci` in a Go CLI project and verify it creates the correct ci.yml and Makefile targets
1. Run `/setup-ci` in a project with existing CI and verify the overwrite/merge/abort flow works
1. Run `/setup-ci` in a JS/TS project and verify the correct workflow template is used
1. Verify the command suggests `/setup-gitleaks` and `/setup-linters` at the end
1. Run `/check-versions` to verify marketplace.json and plugin.json versions are consistent
1. Run linters to verify formatting of all new files
