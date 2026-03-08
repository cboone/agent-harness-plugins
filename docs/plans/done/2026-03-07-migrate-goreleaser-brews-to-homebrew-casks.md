# Migrate GoReleaser Templates from `brews:` to `homebrew_casks:`

Closes #157, #178, #180.

## Context

GoReleaser v2.10 deprecated the `brews:` configuration section in favor of `homebrew_casks:`. The old `brews:` approach generated Homebrew formulas for pre-compiled binaries, but formulas are meant for building from source. The new `homebrew_casks:` generates proper Homebrew casks, which is the correct artifact type for pre-compiled binaries.

Three plugins generate or reference GoReleaser configs using the deprecated `brews:` section. This plan migrates all of them to `homebrew_casks:`, adds cask-specific features (quarantine removal hooks, structured completions/manpages fields), and provides migration guidance for existing projects.

Issue #178 specifically documents a real failure: `hooks.post.install` in casks expects a **string**, not a YAML list. Two consecutive release failures in `cboone/snappy` resulted from this schema difference.

## Files to Modify

### 1. `plugins/add-goreleaser-homebrew/commands/add-goreleaser-homebrew.md`

**Version bump: 1.2.1 -> 2.0.0** (breaking: generated output format changes fundamentally)

#### Workflow text updates

- **Line 44**: Change "dependencies to declare in the formula" to "dependencies to declare in the cask"
- **Lines 97-99**: Update step 7 bullet descriptions:
  - Completions: "add completion generation to `before.hooks`, include in `archives.files`, and set the `completions:` field"
  - Man pages: "add `before.hooks`, `archives.files`, and set the `manpages:` field"
  - macOS-only: "restrict `goos`/`goarch`, remove Windows format override" (remove `depends_on :macos` reference)
- **Line 136**: "publish Homebrew formulas" -> "publish Homebrew casks"

#### Base template (lines 229-240)

Replace the `brews:` block with:

```yaml
homebrew_casks:
  - binaries:
      - PROJECT-NAME
    repository:
      owner: GITHUB-USERNAME
      name: homebrew-tap
      token: "{{ .Env.HOMEBREW_TAP_TOKEN }}"
    homepage: "https://github.com/GITHUB-USERNAME/PROJECT-NAME"
    description: "PROJECT-DESCRIPTION"
    license: MIT
    hooks:
      post:
        install: |
          system_command "/usr/bin/xattr", args: ["-dr", "com.apple.quarantine", "#{staged_path}/PROJECT-NAME"]
```

Key differences:
- `brews:` -> `homebrew_casks:`
- Remove `directory: Formula` (casks default to `Casks/`)
- Remove `test:` block (casks don't support test blocks)
- Add `binaries:` array (replaces implicit `bin.install`)
- Add quarantine removal hook (prevents Gatekeeper errors for unsigned binaries)

#### Template notes (lines 242-256)

Update to reflect cask changes:
- Note `homebrew_casks:` replaces deprecated `brews:` (GoReleaser v2.10+)
- Note `directory` defaults to `Casks` and is omitted
- Note quarantine removal hook prevents "App is damaged" Gatekeeper errors
- Note casks do not support `test:` blocks
- Note `binaries:` replaces the `install:` block
- Remove formula-specific notes

#### Conditional feature: Shell completions (lines 372-388)

**Architectural change**: Formulas used `generate_completions_from_executable` at install time. Casks require pre-generated completion files in the archive.

Replace with three parts:

1. **`before.hooks`**: Generate completions during build:

```yaml
before:
  hooks:
    - go mod tidy
    - mkdir -p completions
    - go run . completion bash > completions/PROJECT-NAME.bash
    - go run . completion zsh > completions/PROJECT-NAME.zsh
    - go run . completion fish > completions/PROJECT-NAME.fish
```

2. **`archives.files`**: Include completions in the archive:

```yaml
archives:
  - # ... (keep all other fields)
    files:
      - src: completions/*
        dst: completions
```

3. **`homebrew_casks:` completions field**:

```yaml
homebrew_casks:
  - # ... (keep all other fields)
    completions:
      bash: completions/PROJECT-NAME.bash
      zsh: completions/PROJECT-NAME.zsh
      fish: completions/PROJECT-NAME.fish
```

Update explanatory text to describe the pre-generation approach.

#### Conditional feature: Man pages (lines 389-439)

The `before.hooks` and `archives.files` sections remain the same. Replace the `brews:` install block (lines 432-439) with:

```yaml
homebrew_casks:
  - # ... (keep all other fields)
    manpages:
      - man/man1/PROJECT-NAME.1
```

Update explanatory text: replace `man1.install Dir["man/man1/*"]` references with `manpages:` array description.

#### Conditional feature: macOS only (lines 442-483)

- Build matrix restriction and archive format override removal: unchanged
- **Remove** the `custom_block: depends_on :macos` section (lines 476-483). Casks are inherently macOS-oriented; the quarantine removal hook (already in the base template) serves the macOS purpose
- Runner change to `macos-latest`: unchanged

#### Combined examples (lines 495-574)

Replace all combined examples with cask equivalents. Key structure for completions + man pages:

```yaml
before:
  hooks:
    - go mod tidy
    - mkdir -p man/man1 completions
    - go run . man man/man1
    - go run . completion bash > completions/PROJECT-NAME.bash
    - go run . completion zsh > completions/PROJECT-NAME.zsh
    - go run . completion fish > completions/PROJECT-NAME.fish

archives:
  - # ...
    files:
      - src: man/man1/*
        dst: man/man1
      - src: completions/*
        dst: completions

homebrew_casks:
  - # ...
    manpages:
      - man/man1/PROJECT-NAME.1
    completions:
      bash: completions/PROJECT-NAME.bash
      zsh: completions/PROJECT-NAME.zsh
      fish: completions/PROJECT-NAME.fish
```

For macOS-only variant: add restricted build matrix, no Windows format override, `macos-latest` runner.

#### Notes section (lines 576-583)

Remove `generate_completions_from_executable` and `man1.install` notes. Add notes about pre-generated completions, `manpages:` array, `binaries:` array, and no `test:` block.

#### HOMEBREW_TAP_TOKEN section (lines 586-655)

- Line 590: "push formula updates" -> "push cask updates"
- Line 629: "push formula updates" -> "push cask updates"

#### New section: "Reference: Migrating Existing Projects"

Add after HOMEBREW_TAP_TOKEN, with guidance for projects migrating from formula to cask:

1. Update `.goreleaser.yml`: replace `brews:` with `homebrew_casks:` per the template
2. Create `tap_migrations.json` in the tap repository:
   ```json
   { "PROJECT-NAME": "PROJECT-NAME" }
   ```
3. Delete old formula from tap repo after first successful cask release
4. Note: `hooks.post.install` is a **string**, not a list (documents the #178 failure)

### 2. `plugins/scaffold-go-cli/commands/scaffold-go-cli.md`

**Version bump: 1.4.2 -> 2.0.0** (breaking: generated output format changes)

#### Text updates

- Line 17: "GoReleaser Homebrew formula" -> "GoReleaser Homebrew cask"
- Line 207: "publish Homebrew formulas" -> "publish Homebrew casks"

#### `.goreleaser.yml` template (lines 571-582)

Replace `brews:` block with same `homebrew_casks:` structure as add-goreleaser-homebrew base template.

#### Template notes (lines 584-594)

Update to match add-goreleaser-homebrew notes (cask-specific).

#### HOMEBREW_TAP_TOKEN section (lines 839-910)

- Line 845: "push formula updates" -> "push cask updates"
- Line 884: "push formula updates" -> "push cask updates"

### 3. `plugins/setup-installers/commands/setup-installers.md`

**Version bump: 1.3.1 -> 1.4.0** (minor: detection logic change, standalone formula templates unaffected)

The standalone `Formula/` Ruby class templates (lines 107-179) are NOT affected. Those are real Homebrew formulas for projects without GoReleaser.

#### Detection updates

- **Line 51**: Change `brews:` detection to `homebrew_casks:` or `brews:` (detect both new and legacy)
- **Line 91**: "GoReleaser exists with a `brews:` section" -> "GoReleaser exists with a `homebrew_casks:` or `brews:` section"
- **Line 99**: "GoReleaser exists without a `brews:` section" -> "GoReleaser exists without a `homebrew_casks:` or `brews:` section"

### 4. Version bumps in plugin.json files

- `plugins/add-goreleaser-homebrew/.claude-plugin/plugin.json`: 1.2.1 -> 2.0.0
- `plugins/scaffold-go-cli/.claude-plugin/plugin.json`: 1.4.2 -> 2.0.0
- `plugins/setup-installers/.claude-plugin/plugin.json`: 1.3.1 -> 1.4.0

### 5. `.claude-plugin/marketplace.json`

Update versions for all three plugins to match their plugin.json. Marketplace `metadata.version` stays at 1.20.0 (no plugins added or removed).

## Design Decisions

1. **Always include quarantine removal hook**: GoReleaser produces unsigned binaries. Without it, macOS users get "App is damaged" errors. Included in the base template, not a conditional feature.

2. **Pre-generated completions**: The biggest functional change. Formulas could run `generate_completions_from_executable` at install time. Casks require files to exist in the archive. Completion files are generated in `before.hooks`, included in `archives.files`, and referenced via the `completions:` field.

3. **No test block**: Casks don't support `test:` blocks. This is a functional loss but matches how Homebrew casks work.

4. **Major version bumps for add-goreleaser-homebrew and scaffold-go-cli**: The generated `.goreleaser.yml` format changes fundamentally (formula to cask). This is a breaking change.

5. **Minor version bump for setup-installers**: Detection logic adds `homebrew_casks:` recognition, but standalone formula generation is unaffected.

6. **`hooks.post.install` is a string**: Issue #178 documents real failures from using a YAML list. The template must use the string form with `|` block scalar.

7. **Standalone formulas in setup-installers unchanged**: The `Formula/PROJECT-NAME.rb` Ruby class templates are for non-GoReleaser projects. They are real formulas, not part of the GoReleaser deprecation.

## Commit Sequence

1. `feat!: migrate add-goreleaser-homebrew from brews to homebrew_casks` - all changes to add-goreleaser-homebrew.md + plugin.json version bump
2. `feat!: migrate scaffold-go-cli from brews to homebrew_casks` - all changes to scaffold-go-cli.md + plugin.json version bump
3. `feat: update setup-installers to detect homebrew_casks` - detection logic changes + plugin.json version bump
4. `chore: update marketplace versions for goreleaser migration` - marketplace.json version updates

## Verification

1. Read each modified file and verify all `brews:` references are gone (except in setup-installers detection which checks both)
2. Verify YAML template syntax is valid (properly indented, string-not-list for hooks)
3. Verify HOMEBREW_TAP_TOKEN sections are still in sync between add-goreleaser-homebrew and scaffold-go-cli
4. Verify all plugin.json versions match their marketplace.json entries
5. Run `check-versions` skill to confirm version consistency
