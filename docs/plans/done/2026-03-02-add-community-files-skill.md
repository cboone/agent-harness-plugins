# 2026-03-02: Add Community Files Skill (Issue #32)

## Context

Open-source projects approaching public release need standard community files: contribution guidelines, a code of conduct, a security policy, and a PR template. These files are largely templated but should adapt to the specific project. This skill automates adding them, detecting the project's build system and tooling to populate CONTRIBUTING.md with relevant setup instructions.

Language-agnostic. CHANGELOG, .editorconfig, .cspell.yaml, and .markdownlint-cli2.jsonc are excluded (covered by other skills).

Pattern sources: bopca (has all four files), stipple (has CONTRIBUTING.md only).

## Files to Create

```text
plugins/add-community-files/
├── .claude-plugin/
│   └── plugin.json
├── README.md
└── skills/
    └── add-community-files/
        ├── SKILL.md
        └── references/
            ├── contributing.md
            ├── code-of-conduct.md
            ├── security.md
            └── pr-template.md
```

## Files to Edit

- `.claude-plugin/marketplace.json`: add entry alphabetically (between `add-goreleaser-homebrew` and `add-scrut-cli-tests`), bump `metadata.version` `1.18.0` to `1.19.0`
- `README.md` (root): add ToC entry and body section under Skills > Scaffolding
- `CLAUDE.md`: add directory tree entry under `## Structure`

## Implementation Steps

### 1. Create plugin.json

```json
{
  "author": { "name": "Christopher Boone" },
  "description": "Add standard community files to a project: CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, and PR template",
  "homepage": "https://github.com/cboone/cboone-cc-plugins",
  "keywords": ["code-of-conduct", "community", "contributing", "open-source", "security"],
  "license": "MIT",
  "name": "add-community-files",
  "repository": "https://github.com/cboone/cboone-cc-plugins",
  "skills": "./skills",
  "version": "1.0.0"
}
```

### 2. Create reference files (4 files)

Each reference file contains a complete template with `PROJECT-NAME`, `GITHUB-OWNER/PROJECT-NAME`, and `CONTACT-EMAIL` placeholders. A `## Notes` section at the bottom documents substitutions and customization points (not copied into output).

#### `references/contributing.md`

Language-agnostic template. Sections:

1. **Introduction**: welcoming message, Code of Conduct reference
1. **Reporting Issues**: bug reports via issue tracker, questions via Discussions, security via SECURITY.md
1. **Development Setup**: prerequisites, clone, install, build, test commands (all placeholders; SKILL.md instructs the agent to fill these by scanning the actual project)
1. **Code Style**: lint, format commands (populated from detected tooling)
1. **Commit Messages**: Conventional Commits format with type list (feat, fix, docs, refactor, test, build, ci, chore) and examples
1. **Pull Request Process**: fork, branch, make changes, run tests/lint, submit PR
1. **Branch Naming**: `feature/*`, `fix/*`, `docs/*`, `refactor/*`, `test/*`

The template provides the structural framework. The SKILL.md workflow instructs the agent to detect the project's build system (Makefile, package.json, Cargo.toml, pyproject.toml, etc.) and fill in the Development Setup, Code Style, and testing commands accordingly.

Source pattern: `/Users/ctm/Development/bopca/CONTRIBUTING.md` (structure), stipple CONTRIBUTING.md (simpler variant for reference)

#### `references/code-of-conduct.md`

Full Contributor Covenant **v3.0** text. Sections: Our Pledge, Encouraged Behaviors, Restricted Behaviors (+ Other Restrictions), Reporting an Issue, Addressing and Repairing Harm (4-rung enforcement ladder: Warning, Temporarily Limited Activities, Temporary Suspension, Permanent Ban), Scope, Attribution.

Single placeholder: `CONTACT-EMAIL` in the Reporting section. The skill offers alternatives: email address, GitHub Discussions URL, or Issues URL.

Source: `/Users/ctm/Development/bopca/CODE_OF_CONDUCT.md`

#### `references/security.md`

Security vulnerability reporting policy for `.github/SECURITY.md`. Sections:

1. **Reporting a Vulnerability**: use GitHub's private vulnerability reporting (not public issues)
1. **What to Include**: description, reproduction steps, impact, suggested fix
1. **Response Timeline**: acknowledgment within 24h, initial assessment within 48h
1. **What Qualifies**: generic guidance (injection, data exposure, auth bypass, etc.)
1. **Out of Scope**: upstream dependencies, physical access, social engineering

Source: `/Users/ctm/Development/bopca/.github/SECURITY.md`

#### `references/pr-template.md`

PR template for `.github/PULL_REQUEST_TEMPLATE.md`. Sections:

1. **Description**: HTML comment prompt
1. **Related Issue**: `Fixes #` link
1. **Type of Change**: checkboxes (bug fix, new feature, breaking change, documentation)
1. **Checklist**: read CONTRIBUTING, follows style, added tests, tests pass, docs updated

Source: `/Users/ctm/Development/bopca/.github/PULL_REQUEST_TEMPLATE.md`

### 3. Create SKILL.md

**Frontmatter**: `name: add-community-files`, trigger phrases: "add community files", "add contributing guide", "prepare for open source", "add code of conduct", "add security policy".

**Workflow**:

#### Step 1. Gather Parameters

Auto-detect:

- **Project name**: from git remote URL (last segment), or README.md H1, or directory name
- **GitHub owner/repo**: from git remote URL
- **Contact method for CoC**: try `git config user.email`, ask user (offer: email, GitHub Discussions URL, GitHub Issues URL)

Detect build system:

- Scan for Makefile, package.json, Cargo.toml, pyproject.toml, go.mod, Gemfile, etc.
- Identify available targets/scripts (e.g., parse Makefile target names, package.json scripts)
- Detect linting tools from config files (golangci-lint, eslint, ruff, clippy, etc.)

#### Step 2. Check Existing Files

Check for each target file:

| File               | Path                                 | If exists              |
| ------------------ | ------------------------------------ | ---------------------- |
| CONTRIBUTING.md    | `./CONTRIBUTING.md`                  | Ask before overwriting |
| CODE_OF_CONDUCT.md | `./CODE_OF_CONDUCT.md`               | Ask before overwriting |
| SECURITY.md        | `./.github/SECURITY.md`              | Ask before overwriting |
| PR template        | `./.github/PULL_REQUEST_TEMPLATE.md` | Ask before overwriting |

Report findings. Create `.github/` directory if needed.

#### Step 3. Generate CONTRIBUTING.md

Read `./references/contributing.md`. Substitute placeholders. Fill Development Setup with detected build commands:

- **Makefile projects**: `make build`, `make test`, `make lint`, `make fmt`
- **Node projects**: `npm install`, `npm test`, `npm run lint`
- **Cargo projects**: `cargo build`, `cargo test`, `cargo clippy`
- **Python projects**: `uv sync`, `uv run pytest`, `uv run ruff check`
- Adapt Code Style section to detected linting/formatting tools

#### Step 4. Generate CODE_OF_CONDUCT.md

Read `./references/code-of-conduct.md`. Substitute `CONTACT-EMAIL`.

#### Step 5. Generate .github/SECURITY.md

Read `./references/security.md`. Substitute `PROJECT-NAME` and `GITHUB-OWNER/PROJECT-NAME`. Adapt the "What Qualifies" section based on project type if relevant.

#### Step 6. Generate .github/PULL_REQUEST_TEMPLATE.md

Read `./references/pr-template.md`. Adapt checklist items based on detected tooling (e.g., reference the specific test command, mention CHANGELOG if one exists).

#### Step 7. Summary

Print table of files created/skipped and next steps.

**Error Handling**: missing git remote (use directory name), no build system detected (use generic placeholders and warn), write permission failures.

### 4. Create per-plugin README.md

Standard format: Type (Skill), Trigger (`/add-community-files`), Installation boilerplate, What It Does (detects project build system and adapts content), Usage, Examples, See Also (scaffold-new-repo, setup-linters, all plugins).

No Recommended Permissions section (file creation uses Write tool).

### 5. Update marketplace.json

Add entry alphabetically between `add-goreleaser-homebrew` and `add-scrut-cli-tests`. Bump `metadata.version` from `1.18.0` to `1.19.0`. Description and keywords must match plugin.json.

### 6. Update root README.md

**ToC** (Scaffolding subcategory):

```markdown
<br>Scaffolding:
[Add Community Files](#add-community-files)
∙ [Bootstrap Project](#bootstrap-project)
```

**Body** (before Bootstrap Project under `### Scaffolding`):

```markdown
#### Add Community Files

Add standard community files to a project preparing for public release: CONTRIBUTING.md, CODE_OF_CONDUCT.md, .github/SECURITY.md, and a pull request template. Detects the project's build system and tooling to populate contribution guidelines with relevant setup, test, and lint commands.

> **Trigger:** `/add-community-files`
> **Details:** [README](./plugins/add-community-files/README.md)
```

### 7. Update CLAUDE.md

Add `add-community-files/` directory tree entry in the `## Structure` section, alphabetically (between `add-scrut-cli-tests/` and `address-review/`):

```text
    ├── add-community-files/          # Community files skill
    │   ├── .claude-plugin/
    │   │   └── plugin.json
    │   ├── README.md
    │   └── skills/
    │       └── add-community-files/
    │           ├── SKILL.md
    │           └── references/
    │               ├── code-of-conduct.md
    │               ├── contributing.md
    │               ├── pr-template.md
    │               └── security.md
```

## Verification

1. All 7 new files exist with correct content (plugin.json, README.md, SKILL.md, 4 reference files)
1. `plugin.json` version matches `marketplace.json` entry version (both `1.0.0`)
1. `marketplace.json` `metadata.version` is `1.19.0`
1. SKILL.md frontmatter `name` matches directory name (`add-community-files`)
1. Root README ToC and body entries are correctly formatted (one link per line, `∙` prefix)
1. Run `check-versions` skill to validate version consistency
1. Run `lint-and-fix` to check formatting
