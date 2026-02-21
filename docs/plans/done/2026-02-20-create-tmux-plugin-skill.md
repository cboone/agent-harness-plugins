# 2026-02-20: Create Tmux Plugin Scaffolding Skill

## Context

Four tmux plugin repos (tmux-binding-help, tmux-conf, tmux-theme-alabaster, tmux-package-status) follow identical structural conventions. Creating a new tmux plugin requires the same boilerplate every time: entry point, scripts directory, helpers, TPM-compatible setup, and a README with specific install sections. This skill automates that scaffolding, following TPM Redux conventions.

Issue: #34

## Files to Create

```text
plugins/create-tmux-plugin/
├── .claude-plugin/
│   └── plugin.json
├── README.md
└── skills/
    └── create-tmux-plugin/
        ├── SKILL.md
        └── references/
            ├── entry-point.md     # <plugin-name>.tmux template
            ├── helpers.md         # scripts/helpers.sh template
            ├── license.md         # MIT License template
            ├── main-script.md     # scripts/<name>.sh template
            └── readme.md          # README.md template for generated tmux plugin
```

## Files to Update

- `.claude-plugin/marketplace.json`: add entry between `create-plugin` and `create-worktree`, bump `metadata.version` from `1.12.0` to `1.13.0`
- Root `README.md`: add ToC link in Scaffolding subcategory + add H3 description section
- `CLAUDE.md`: add directory tree entry between `create-plugin/` and `create-worktree/`

## Implementation Steps

### 1. Create `plugins/create-tmux-plugin/.claude-plugin/plugin.json`

Standard skills plugin metadata. Keywords: `bash`, `plugin`, `scaffolding`, `tmux`, `tpm`. Category: `productivity`. Version: `1.0.1`.

### 2. Create SKILL.md

Workflow-style skill (modeled on `scaffold-go-cli`) with these steps:

1. **Gather Project Information**: plugin name (kebab-case, `tmux-` prefix suggested), short description, list of configurable options with defaults. Generate a single example option if none specified.
1. **Detect User Identity**: `gh api user -q .login` and `git config user.name`, with fallback to asking.
1. **Verify Target Directory**: use current dir if named after plugin and empty, else create subdirectory. Warn if `.tmux` files exist.
1. **Initialize Git**: `git init` (skip if already a repo).
1. **Generate Entry Point**: `PLUGIN-NAME.tmux` from `./references/entry-point.md`, `chmod +x`.
1. **Generate helpers.sh**: `scripts/helpers.sh` from `./references/helpers.md` (identical across all tmux plugins).
1. **Generate Main Script**: `scripts/PLUGIN-NAME.sh` from `./references/main-script.md`, `chmod +x`.
1. **Generate LICENSE**: from `./references/license.md` with YEAR and COPYRIGHT-HOLDER.
1. **Generate README.md**: from `./references/readme.md` with plugin name, description, GitHub username, and configurable options.
1. **Ask About Optional Features**: scrut test skeleton, GitHub Actions CI, workmux layout.
1. **Generate Optional Files**: Makefile + tests dir (scrut), `.github/workflows/scrut.yml` (CI, implies scrut), `.workmux.yaml` (workmux).
1. **Create Initial Commit**: `git add -A && git commit -S -m "feat: scaffold tmux plugin"`.
1. **Summary**: list files, show options table, note next steps.

### 3. Create 5 reference files

- **entry-point.md**: `PLUGIN-NAME.tmux` template with `CURRENT_DIR`, source helpers, `main()` function, `get_tmux_option` calls. No `set -euo pipefail` (runs via tmux `run-shell`).
- **helpers.md**: `get_tmux_option()` function. Sourced, not executed. Uses `"${var}"` quoting and `[[ ]]` tests.
- **main-script.md**: `scripts/PLUGIN-NAME.sh` stub with `CURRENT_DIR`, sources helpers, `main()` with TODO placeholder and common pattern examples.
- **readme.md**: README template with three install sections (TPM Redux recommended, Manual, TPM deprecated with warning), Configuration section, License section.
- **license.md**: Standard MIT License template with YEAR and COPYRIGHT-HOLDER placeholders.

### 4. Create per-plugin README.md

Standard per-plugin README following the template from `create-plugin/references/readme-updates.md`. See Also links to scaffold-new-repo and write-shell-scripts.

### 5. Update marketplace.json

- Insert entry alphabetically between `create-plugin` and `create-worktree`
- Bump `metadata.version` from `"1.12.0"` to `"1.13.0"`

### 6. Update root README.md

**ToC** (Scaffolding subcategory): insert `∙ [Create Tmux Plugin](#create-tmux-plugin)` between `Add GoReleaser Homebrew` and `Scaffold Go CLI`.

**Description section** (under `### Scaffolding`): insert H4 block between `Add GoReleaser Homebrew` and `Scaffold Go CLI` with trigger `/create-tmux-plugin` and details link.

### 7. Update CLAUDE.md

Add directory tree entry between `create-plugin/` and `create-worktree/`.

### 8. Run `check-versions` skill

Verify version correctness and consistency.

## Design Decisions

- **No `set -euo pipefail` in entry point or helpers**: tmux's `run-shell` context makes strict mode problematic (early exit causes silent plugin failures). Matches the pattern in existing tmux-binding-help repo.
- **Example option when none specified**: generates `@PLUGIN-NAME-enabled` with default `on` so the helpers.sh and option-reading pattern is demonstrated, not just inert.
- **Optional features asked in step 10 (not step 1)**: keeps initial gathering focused on essentials. Matches scaffold-go-cli's handling of optional Viper/Charmbracelet.
- **Plugin name prefix**: suggests `tmux-` but does not require it. Warning in Error Handling section.
- **Manual install uses XDG paths**: `${XDG_DATA_HOME:-$HOME/.local/share}/tmux/plugins/` for modern convention.

## Verification

1. Confirm all new files are created with correct structure
1. Run `check-versions` to verify marketplace.json and plugin.json are in sync
1. Verify root README.md ToC and description section have the new entry in correct alphabetical order
1. Verify CLAUDE.md directory tree has the new entry
1. Read through SKILL.md to confirm workflow steps are clear and reference file paths are correct
