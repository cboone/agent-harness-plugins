# Add pin-everything Skill Plugin

## Context

PR [cboone/cboone-cc-plugins#250](https://github.com/cboone/cboone-cc-plugins/pull/250) executed a one-time pin-everything pass on this repository: SHA-pinned every `uses:` ref, pinned all runtime versions and install commands, migrated scaffolded CI to language version files, added a weekly drift-audit, and tightened Dependabot. The methodology is in the head of whoever ran the pass and in the commit messages and skill template diffs.

The next time someone wants to harden a repository against supply-chain drift the same way, they should not have to re-derive the methodology from a closed PR. This plan adds a `pin-everything` skill that codifies the playbook so Claude can execute it on any project, not just `cboone-cc-plugins`.

The skill mirrors what #250 did, generalized to arbitrary repos. The work in #250 itself is the canonical reference implementation; the skill points adopters at it.

## Approach

Pure skills plugin (SKILL.md and references only — no hooks, no scripts emitted by the plugin itself). Parallels in scope and structure with `setup-linters`, `setup-installers`, `manage-repo-licensing`. The skill walks Claude through:

1. Detecting every version surface in the target repo
2. Reporting current pinning state and proposing fixes
3. Applying SHA pins, integrity hashes, exact-version pins, and version-file refs
4. Optionally generating a drift-audit script tailored to the surfaces found
5. Wiring Dependabot to cover what it can

The skill does not silently rewrite a repo: it presents detected surfaces and confirms which categories to pin before each batch. Adopters who only want SHA-pinning of actions, for example, can stop after step 3.

A small companion script `references/scripts/version-audit-template` is bundled inside the plugin so the skill can install it (or a tailored variant of it) into the user's repo. This is a *plugin-emitted* script, not a script the plugin itself runs — Claude reads the template, customizes for the surfaces found, and writes the result to the user's `bin/`.

## Implementation order note

PR #250 merged on 2026-04-30 (commit `9aac8f3`); this worktree has been rebased onto the resulting `main`. Implementation can proceed. The skill's reference docs should cite permalinks into the merged commits (`bin/version-audit`, `.github/workflows/version-audit.yml`, the SHA-pinned `uses:` refs across `plugins/*/skills/*/references/`) as the canonical worked example.

A companion guidance gap was filed as [cboone/cboone-cc-plugins#256](https://github.com/cboone/cboone-cc-plugins/issues/256) (clarify references/ layout convention). The plan below adopts the corrected convention (flat `references/` for workflow skills) ahead of the fix landing in `create-plugin`.

## Files to Create

### 1. `plugins/pin-everything/.claude-plugin/plugin.json`

Standard plugin metadata. Fields alphabetized per convention. Version `1.0.0`. Marketplace category: `ci-and-release` (per the `readme-updates.md` Subcategory Guide: "CI workflows, installers, release automation, repo audits"; pin-everything is a repo-audit/hardening pass and sits naturally next to `setup-secret-scanning` and `update-everything`).

```json
{
  "$schema": "https://anthropic.com/claude-code/plugin.schema.json",
  "author": { "email": "cboone@sent.com", "name": "Christopher Boone" },
  "description": "Pin every version surface in a repository to commit hashes, integrity digests, or specific versions. SHA-pins GitHub Actions, integrity-pins Yarn via Corepack, exact-pins package-manager dependencies, migrates scaffolded CI to language version files, and pins install commands (go install, cargo install, pip, uv, npx). Optionally generates a weekly drift-audit script and tightens Dependabot.",
  "homepage": "https://github.com/cboone/cboone-cc-plugins/tree/main/plugins/pin-everything",
  "keywords": ["dependencies", "pinning", "security", "supply-chain", "versioning"],
  "license": "MIT",
  "name": "pin-everything",
  "repository": "https://github.com/cboone/cboone-cc-plugins",
  "skills": "./skills",
  "version": "1.0.0"
}
```

### 2. `plugins/pin-everything/skills/pin-everything/SKILL.md`

The main deliverable. Frontmatter has only `name` and `description`. Description includes trigger phrases. Body uses `## Workflow` with numbered steps.

Trigger phrases: "pin everything", "pin all versions", "harden version pinning", "SHA-pin actions", "SHA-pin all the actions", "pin to commit hashes", "audit version pins", "pin all uses to commit hashes". Mention supply-chain hardening so the skill triggers on phrasing like "harden against supply-chain attacks".

Boundary note in the description: `pin-everything` is a one-shot hardening pass — for ongoing template drift detection, point users at `update-everything`; for credential-leak hardening, point users at `setup-secret-scanning`. This prevents trigger collisions on overlapping phrases like "audit my repo" / "check what's outdated".

Body structure (each step lives under its own explicit `### N. Step Name` heading where N is the literal step number 1 through 11; the `1.` markers below are markdown auto-numbering, not the rendered headings):

1. **Audit the repo for version surfaces.** Scan for: `.github/workflows/*.{yml,yaml}` `uses:` refs, `package.json` `packageManager` field, `package.json` deps with carets/tildes, `.tool-versions` / `.nvmrc` / `.ruby-version` / `rust-toolchain.toml` / `build.zig.zon`, `go.mod` `go` directive, inline language-version pins in scaffolded workflows (`node-version: "X"`, `ruby-version: "X"`, `go-version: "stable"`, `zig-version:`), `go install ...@latest|@vX`, `cargo install <crate>` (with or without `--locked`/`--version`), `pip install <pkg>`, `uv pip install <pkg>`, `uv add <pkg>`, `npx <tool>` (with or without `@version`), schema URLs with `@latest`. Output a categorized table (file paths, line counts, current pin state).

1. **Confirm scope with the user.** Present the categorized findings. Default: pin everything that's not deliberately user-facing (placeholder install instructions like `go install github.com/OWNER/REPO@latest` in scaffolded READMEs stay unpinned). Offer per-category opt-out (e.g., "skip pip pinning", "skip Dependabot config").

1. **SHA-pin GitHub Actions.** For every `uses:` ref to a third-party or org-owned action, resolve the latest release tag to a 40-character commit SHA via `gh api repos/<repo>/git/ref/tags/<tag>` (recursing through annotated tag objects). Replace the tag ref with the SHA and append a `# vX.Y.Z` comment. Handle `dtolnay/rust-toolchain@stable` (channel ref → branch SHA, comment `# stable`). For org-owned reusable workflow refs (`org/repo/.github/workflows/foo.yml@vN`), pin them too — tag immutability isn't a function of repo ownership. Reference: `./references/github-actions.md`.

1. **Pin language runtimes via version files.** Replace inline `node-version: "X"`, `ruby-version: "X"`, `go-version: "stable"|"MINIMUM"` in scaffolded CI templates with `node-version-file: ".tool-versions"`, `ruby-version-file: ".tool-versions"`, `go-version-file: "go.mod"`. Detect missing version files in the user's repo and create them with current LTS / stable values. For Zig (no version-file input on most actions), pass `version: ""` to fall through to `build.zig.zon`'s `minimum_zig_version`. Reference: `./references/language-runtimes.md`.

1. **Pin Yarn (Corepack) with SHA-512 integrity.** If `package.json` has `"packageManager": "yarn@X.Y.Z"`, compute the tarball SHA-512 (preferred: `corepack prepare yarn@X.Y.Z --activate` then read the resulting `packageManager` field; fall back to fetching the tarball and `sha512sum` if Corepack isn't available) and rewrite as `"yarn@X.Y.Z+sha512.<hash>"`. Verify with `corepack enable && yarn --version`. Reference: `./references/yarn-corepack.md`.

1. **Exact-pin package-manager dependencies (application context only).** Strip carets/tildes from `package.json` `devDependencies` and `dependencies`, replacing with the exact version locked in `yarn.lock` / `package-lock.json` / `pnpm-lock.yaml`. **Discriminate library from application before pinning the manifest:**
   - **Node.js**: presence of a committed lockfile + `"private": true` (or absence of `bin`/library-style export config) → application; pin manifest. Library packages → leave caret ranges, pin lockfile only.
   - **Ruby**: `*.gemspec` present → library; do not pin `Gemfile` exactly. App-only repo (no gemspec, `Gemfile.lock` committed) → pin from lockfile.
   - **Python**: `pyproject.toml` declares a published distribution name and lacks an application entrypoint → library; leave version specifiers alone. App with `requirements.txt` or `uv.lock` → pin to `==`.
   - **Rust**: `Cargo.lock` committed AND crate has a `[[bin]]` target (or is a workspace of bin crates) → application; exact-pin manifest. Library crate (`Cargo.lock` typically not committed, exposes `[lib]`) → leave `^X.Y.Z` ranges; exact-pinning a lib crate breaks downstream version unification.
   When the discriminator is ambiguous, prompt the user.

1. **Pin install commands.** For every `go install <path>@latest`, `cargo install <crate>` (without `--version`), `pip install <pkg>` (without `==`), `uv pip install <pkg>`, `uv add <pkg>`, `npx <tool>` (without `@version`) in CI templates, Makefiles, and skill docs:
   - **Skip user-facing placeholders** (paths containing `OWNER/REPO`, `GITHUB-USERNAME`, `PROJECT-NAME`).
   - **Skip local-dev examples** that resolve via lockfile (e.g., `npx prettier --write .` in a `package.json` repo).
   - For real tool installs: look up current upstream latest (GitHub releases for `go install`, crates.io for `cargo install`, PyPI for `pip`/`uv`, npm registry for `npx`) and write the pinned form (`@vX.Y.Z`, `--locked --version X.Y.Z <crate>`, `'<pkg>==X.Y.Z'`, `<tool>@X.Y.Z`).
   Reference: `./references/install-commands.md`.

1. **Tighten `.yarnrc.yml` (if present).** Make security-strict defaults explicit so future Corepack migrations cannot silently re-enable scripts or whitelist arbitrary git sources: `enableScripts: false`, `enableTelemetry: false`, `defaultSemverRangePrefix: ""`. Reference: `./references/yarn-corepack.md`.

1. **Add Dependabot config.** Create or merge `.github/dependabot.yml` with weekly schedule, split groups by update-type (minor-patch / major), 10-PR cap per ecosystem. Cover `github-actions` and whichever package ecosystems are present (`npm`, `cargo`, `pip`, `bundler`, `gomod`). Reference: `./references/dependabot.md`.

1. **Optionally generate a version-audit script.** If the user wants drift coverage for the surfaces Dependabot can't track (`.tool-versions`, `packageManager`, action SHAs in `.md` templates, install-command pins inside scripts), tailor `references/scripts/version-audit-template` to the surfaces found and write it to the user's `bin/version-audit`. Pair with a `.github/workflows/version-audit.yml` that runs weekly, opens / updates / closes a single labeled issue. Reference: `./references/version-audit.md`.

1. **Verify and commit.** Re-run the audit (step 1) and confirm zero unpinned surfaces remain (modulo deliberate exclusions). Run project linters via the `lint-and-fix` skill. If the user has REUSE/SPDX licensing set up (root `REUSE.toml` present), invoke `manage-repo-licensing` to add SPDX coverage for any newly emitted files (`bin/version-audit`, `.github/workflows/version-audit.yml`, `.github/dependabot.yml`) and run `reuse lint`. Commit with a Conventional Commits message scoped to what was pinned (one commit per category for clarity, or one bundled commit if the user prefers).

The body also includes:

- An `## Options` section: `--scope <comma-list>` (subset of the surface categories), `--no-audit` (skip step 10), `--no-dependabot` (skip step 9), `--dry-run` (audit and report, no edits).
- An `## Error Handling` section: tags don't resolve to commits (annotated vs lightweight handling), version-file action input not supported, ambiguous user-facing vs tool-install distinction in install commands, conflicting existing Dependabot config.
- A `## Refresh own SHAs at scaffold time` section noting that the SHAs in the skill's own `references/` examples rot, and that scaffolders should refresh from the canonical example commits in `cboone-cc-plugins` itself.

### 3. `plugins/pin-everything/skills/pin-everything/references/checklist.md`

Single-page rapid checklist for the impatient: every surface, the pinning command, and a one-line "what to verify". Mirrors the structure of `setup-linters`'s `references/checklist.md`.

### 4. `plugins/pin-everything/skills/pin-everything/references/github-actions.md`

How to SHA-pin every `uses:` ref. Covers:

- Resolving annotated vs lightweight tags (`gh api repos/<r>/git/ref/tags/<t>` returns either `commit` or `tag` type; recurse through tag objects to get the commit SHA, or use `gh api repos/<r>/commits/<tag>` which always returns the commit SHA directly).
- Channel-style refs (`dtolnay/rust-toolchain@stable`): pin the action repo to the SHA of the named branch's HEAD; the toolchain channel is a separate concern (handled by `rust-toolchain.toml` in the user repo).
- Reusable workflow refs (`org/repo/.github/workflows/foo.yml@vN`): same SHA-pinning treatment as actions; tag immutability is not a function of repo ownership.
- Major version held intentionally vs current latest: when to bump, how to verify breaking changes (read release notes for the upstream major).
- Comment format `# vX.Y.Z` so Dependabot's PR diffs are readable.

### 5. `plugins/pin-everything/skills/pin-everything/references/language-runtimes.md`

Per-language version-file recipes:

| Language | Action | Version-file input | File format | If file is missing |
| --- | --- | --- | --- | --- |
| Node.js | `actions/setup-node` | `node-version-file: '.tool-versions'` | `nodejs <version>` | Create with current LTS |
| Ruby | `ruby/setup-ruby` | `ruby-version-file: '.tool-versions'` | `ruby <version>` | Create with current stable |
| Go | `actions/setup-go` | `go-version-file: 'go.mod'` | `go X.Y` directive | Always present in Go projects |
| Python | `astral-sh/setup-uv` | (uv reads `pyproject.toml`) | `requires-python` | Add to `pyproject.toml` |
| Rust | `dtolnay/rust-toolchain` | `rust-toolchain.toml` | `[toolchain] channel = "stable"` | Create or use input field |
| Zig | `mlugg/setup-zig` | `version-file: build.zig.zon` (action-direct) or `version: ""` (via cboone/gh-actions wrapper, falls through) | `minimum_zig_version` in `build.zig.zon` | Always present in Zig projects |

Document the LTS / stable lookup commands for each language so the skill can populate missing files automatically.

### 6. `plugins/pin-everything/skills/pin-everything/references/install-commands.md`

Per-package-manager pinning recipes with the upstream-of-record for each:

| Manager | Pinned form | Upstream-of-record |
| --- | --- | --- |
| `go install` | `<path>@vX.Y.Z` | GitHub releases for the path's repo |
| `cargo install` | `--locked --version X.Y.Z <crate>` | crates.io |
| `pip install` | `'<pkg>==X.Y.Z'` | PyPI |
| `uv pip install` / `uv add` | `'<pkg>==X.Y.Z'` | PyPI |
| `npx` | `<tool>@X.Y.Z` (CI without prior install) | npm registry |
| `brew install` (formula) | _no in-line version pin_ | — (deliberately unpinned in the general case) |
| `brew install` (cask) | `version "X.Y.Z"` in tap-managed cask | — (only when project owns the tap) |

`brew install` is left unpinned by default because Homebrew formulae do not accept an inline `@version` argument; reproducible installs require a custom tap. When the user maintains their own tap (e.g. via `add-goreleaser-homebrew`), the cask `version` field is the pinning surface and falls under that tap's release process, not under this skill.

Document the user-facing-vs-tool-install discriminator: if the install path contains `OWNER`, `REPO`, `GITHUB-USERNAME`, `PROJECT-NAME`, or `<...>`-style placeholders, leave as `@latest` — it's a template for the user's project.

### 7. `plugins/pin-everything/skills/pin-everything/references/yarn-corepack.md`

How to:

- Compute Yarn's SHA-512 integrity hash and write `"yarn@X.Y.Z+sha512.<hash>"` in `packageManager`.
- Make `.yarnrc.yml` security-strict explicitly (`enableScripts: false`, `enableTelemetry: false`, `defaultSemverRangePrefix: ""`).
- Detect and revert harmful additions made by Corepack migrations (`approvedGitRepositories: ["**"]`, `enableScripts: true`).

### 8. `plugins/pin-everything/skills/pin-everything/references/dependabot.md`

`dependabot.yml` template with:

- Weekly schedule.
- Per-ecosystem split groups (`<ecosystem>-minor-patch` and `<ecosystem>-major`) so minor/patch can auto-merge later while majors get human review.
- 10-PR cap per ecosystem (raised default — SHA-pinning produces finer-grained PRs than tag-pinning).
- `versioning-strategy: increase` for `npm` so existing exact pins aren't widened.
- Note on the four surfaces Dependabot does not cover: `.tool-versions`, `packageManager`, SHAs inside `.md` templates, install-command pins inside scripts. These are handled by the version-audit script in the next reference.

### 9. `plugins/pin-everything/skills/pin-everything/references/version-audit.md`

How to install and tailor the bundled `version-audit-template` script. Topics:

- Surfaces audited (the four Dependabot can't cover).
- Per-surface upstream-of-record APIs (GitHub releases, npm registry, crates.io, PyPI, nodejs.org/dist/index.json, repo.yarnpkg.com/tags).
- Issue-management workflow (single labeled issue; create / update / close).
- How to tailor the template to the surfaces actually present (e.g., remove `audit_pip_install_pins` if the target repo has no pip pins).
- How to extend the script when new surfaces appear.

### 10. `plugins/pin-everything/skills/pin-everything/references/scripts/version-audit-template`

The bash script template, copy-adapted from `bin/version-audit` (landed in PR #250). Header comment notes it is a template — the skill rewrites function signatures and file-paths to fit the consuming repo before writing it to that repo's `bin/`. The template-as-committed must pass `shellcheck -S warning` and `shfmt -d` (use real bash syntax with placeholders that parse cleanly: e.g. `# REPLACE: function audit_<surface>` rather than `<<placeholder>>` markers that break syntax).

### 11. `plugins/pin-everything/skills/pin-everything/references/scripts/version-audit-workflow-template.yml`

The companion `version-audit.yml` GitHub Actions workflow template (copy-adapted from `.github/workflows/version-audit.yml` in #250). Skill writes a customized version into the user's `.github/workflows/`. Use placeholder strings that parse as valid YAML so `actionlint` can run on the template-as-committed (e.g. concrete repo refs that resolve, with comments marking what the skill should substitute downstream).

### 12. `plugins/pin-everything/README.md`

Standard plugin README with description, trigger phrases, what gets pinned, what doesn't, and links to references.

## Files to Modify

### 13. `.claude-plugin/marketplace.json`

- Bump `metadata.version` (minor): catalog gained a plugin.
- Insert new entry alphabetically by plugin `name`. At implementation time the alphabetical slot is between `pr` and `release` (verify against the current state — other branches may have added entries). The slot relative to surrounding plugins is irrelevant to which `category` is assigned.
- Mirror all shared fields from `plugin.json` plus `category: "ci-and-release"` and `source: "./plugins/pin-everything"`.

### 14. `README.md`

Two places, per `create-plugin`'s `readme-updates.md` reference (the marketplace flow handles per-plugin install commands; no Installation-section edit is needed):

- ToC: insert `∙ [Pin Everything](#pin-everything)` alphabetically in the **CI and Release** Skills subcategory line. Current alphabetical neighbors there: between `Optimize Runner Usage` and `Setup CI`.
- Description: insert an H3 section alphabetically under `## Skills` with description paragraph and `> **Trigger:** /pin-everything` + `> **Details:** [README](./plugins/pin-everything/README.md)` blockquote.

### 15. `CLAUDE.md` / `AGENTS.md`

Insert the new directory tree fragment alphabetically. Match the depth of existing entries (`.claude-plugin/`, `README.md`, `skills/<plugin>/SKILL.md`, `skills/<plugin>/references/*.md`, `skills/<plugin>/references/scripts/*`). The `scripts/` subdir under `references/` is novel to this skill (other skills with topical references use `languages/` or `tools/`), so flag this when reviewing.

## Verification

- [ ] `bin/validate-json` passes (marketplace.json + plugin.json are valid)
- [ ] `bin/validate-plugins` passes (structure conventions hold)
- [ ] `bin/build-opencode-mirror` produces a clean diff (skill mirrors regenerate); verify that the mirror script handles `references/scripts/` containing non-`.md` files (executable bash and YAML) without error — current mirrors are markdown-only, so this is the first skill emitting that combination
- [ ] `yarn lint` passes (markdownlint + prettier on all new `.md`)
- [ ] `shellcheck -S warning` and `shfmt -d` pass on the bundled `version-audit-template` script as committed (placeholders intact)
- [ ] `actionlint` passes on the bundled workflow template as committed (placeholders chosen so the file stays valid YAML and references resolvable refs)
- [ ] SKILL.md frontmatter has only `name` and `description`
- [ ] All reference files reachable from SKILL.md via relative paths
- [ ] Plugin name matches directory name in `plugin.json`
- [ ] Marketplace entry shared fields match `plugin.json`; `category: "ci-and-release"` matches the README ToC subcategory placement
- [ ] README ToC follows one-link-per-line `∙` format
- [ ] CLAUDE.md / AGENTS.md tree entry uses correct indentation and alphabetical placement
- [ ] Trigger phrases in SKILL.md description fire the skill on plausible user prompts (sanity check: "pin everything", "harden version pinning in this repo", "SHA-pin all the actions") — every example phrase here must appear in the description's trigger list
- [ ] Step numbers cited in `## Options` (e.g. `--no-audit` referring to step 10, `--no-dependabot` referring to step 9) match the actual workflow step headings; update both sides if the workflow gets reordered
- [ ] Library-vs-application discriminator in step 6 correctly classifies the smoke-test repo before exact-pinning the manifest (see Manual smoke-test plan additions below)

## Manual smoke-test plan

1. Spin up a fresh sample repo with: a basic `.github/workflows/ci.yml` using `actions/checkout@v4`, a `package.json` with caret deps, a `Makefile` with `go install ...@latest`, and no Dependabot config.
2. Run the skill (`/pin-everything`) end-to-end.
3. Confirm:
   - Every `uses:` is SHA-pinned with a `# vX.Y.Z` comment.
   - `package.json` deps are exact-pinned and `packageManager` has SHA-512 integrity.
   - `Makefile` `go install` is pinned to a specific tag.
   - `.tool-versions` exists with current Node LTS.
   - `.github/dependabot.yml` exists with split groups.
   - `bin/version-audit` exists and runs cleanly.
   - `actionlint` and `yarn lint` (if applicable) pass.
4. Run the skill again on the now-pinned repo. Confirm it reports "no unpinned surfaces" and does not propose changes.
5. Repeat with a **library** sample repo (a Rust crate exposing only `[lib]` with no committed `Cargo.lock`, or a Ruby gem with `*.gemspec`). Confirm step 6 detects the library context and **does not** exact-pin the manifest, leaving caret / pessimistic ranges intact while still pinning everything else (actions, runtimes, install commands, Dependabot).
6. If the smoke-test repo has REUSE/SPDX set up (root `REUSE.toml`), confirm step 11 invokes `manage-repo-licensing` and that `reuse lint` passes against newly emitted files.

## References

- PR [cboone/cboone-cc-plugins#250](https://github.com/cboone/cboone-cc-plugins/pull/250) — canonical example implementation that this skill generalizes (merged 2026-04-30 as commit `9aac8f3`).
- Issue [cboone/cboone-cc-plugins#256](https://github.com/cboone/cboone-cc-plugins/issues/256) — `create-plugin` references-layout guidance gap surfaced while reviewing this plan; the plan adopts the corrected (flat) convention ahead of the fix landing.
- [cboone/gh-actions#40](https://github.com/cboone/gh-actions/issues/40), [cboone/gh-actions#41](https://github.com/cboone/gh-actions/issues/41) — upstream wrappers / `zig-version-file` follow-ups; once landed, the skill's reference docs should be updated to recommend the wrappers over direct third-party refs and the `version-file` input over the `zig-version: ""` passthrough.
- [cboone/cboone-cc-plugins#248](https://github.com/cboone/cboone-cc-plugins/issues/248), [cboone/cboone-cc-plugins#249](https://github.com/cboone/cboone-cc-plugins/issues/249) — downstream template-update follow-ups; the skill should mirror those swaps when they land.
- [cboone/cboone-cc-plugins#189](https://github.com/cboone/cboone-cc-plugins/issues/189) — original SHA-pinning ask, closed by #250; the historical context is useful for explaining the convention shift.
- `plugins/create-plugin/skills/create-plugin/SKILL.md` and its `references/` — authority on plugin structure conventions for this repo. Follow it for `plugin.json`, `marketplace.json`, README, CLAUDE.md updates.
