---
name: pin-everything
description: >-
  Pin every version surface in a repository to commit hashes, integrity digests,
  or specific versions as a one-shot supply-chain hardening pass. Use when the
  user says "pin everything", "pin all versions", "harden version pinning",
  "SHA-pin actions", "SHA-pin all the actions", "pin to commit hashes",
  "audit version pins", "pin all uses to commit hashes", or wants to harden a
  repository against supply-chain attacks. SHA-pins GitHub Actions, integrity-
  pins Yarn via Corepack, exact-pins application package-manager dependencies,
  migrates scaffolded CI to language version files, pins install commands, and
  optionally generates a weekly drift-audit script. For ongoing template-drift
  detection use update-everything; for credential-leak hardening use
  setup-secret-scanning.
---

# Pin Everything

Pin every version surface in a repository as a one-shot supply-chain hardening pass: SHA pins for actions, integrity hashes for Corepack, exact pins for package-manager dependencies (in application context), version-file refs for language runtimes, and explicit versions for install commands. Optionally generates a weekly drift-audit script and tightens Dependabot.

This skill is a generalization of the canonical hardening pass executed in [PR #250](https://github.com/cboone/cboone-cc-plugins/pull/250) on `cboone-cc-plugins` itself. Adopters who want to repeat that pass on their own repositories run the skill end-to-end. Adopters who only want a subset (for example, SHA-pinning actions) can stop after the relevant step.

## Workflow

### 1. Audit the Repo for Version Surfaces

Scan the working tree for every version surface, then output a categorized table (file paths, count of refs, current pin state).

Surfaces to detect:

| Category                    | Detection                                                                                                                      |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| GitHub Actions `uses:` refs | Glob `.github/workflows/*.{yml,yaml}` and `.github/actions/**/action.{yml,yaml}`; grep for `uses:`                             |
| Reusable workflow refs      | Same files; grep for `uses:` lines containing `.github/workflows/`                                                             |
| `packageManager` field      | Read `package.json`; check `.packageManager`                                                                                   |
| `package.json` deps         | Read `package.json`; flag `^`/`~` ranges in `dependencies`/`devDependencies`/`peerDependencies`                                |
| Language version files      | Glob `.tool-versions`, `.nvmrc`, `.ruby-version`, `rust-toolchain.toml`, `build.zig.zon`                                       |
| `go.mod` `go` directive     | Read `go.mod`; capture the directive line                                                                                      |
| Inline language pins in CI  | Grep workflows for `node-version:`, `ruby-version:`, `go-version:`, `python-version:`, `zig-version:` (without `-file` suffix) |
| `go install` pins           | Grep for `go install <path>@<ref>` where `<ref>` is `latest` or a `vN.Y.Z` tag                                                 |
| `cargo install` pins        | Grep for `cargo install` with or without `--locked --version`                                                                  |
| `pip` / `uv` pins           | Grep for `pip install`, `uv pip install`, `uv add` (with or without `==`)                                                      |
| `npx` pins                  | Grep for `npx <name>` (with or without `@version`)                                                                             |
| Schema URLs                 | Grep `*.json` and `*.yaml` for `$schema` URLs containing `@latest`                                                             |

Exclude vendored directories from all greps: `node_modules/`, `.yarn/`, `vendor/`, `dist/`, `target/`, `.venv/`.

Print the output as a Markdown table grouped by category, with one row per file showing the file path, the count of matching refs, and a one-word state (`pinned` / `unpinned` / `mixed`).

### 2. Confirm Scope with the User

Present the categorized findings. The default is to pin everything in the repo that is not deliberately user-facing. User-facing means scaffolded README install instructions, placeholder paths in skill templates, and similar documentation that downstream users will customize.

Ask the user to confirm or trim the scope. Offer per-category opt-out (e.g., "skip pip pinning", "skip Dependabot config", "actions only"). If the user invokes the skill with `--scope <comma-list>`, use that list directly; otherwise prompt.

If the user requested `--dry-run`, perform the audit only and stop here.

### 3. SHA-Pin GitHub Actions

For every `uses:` ref to a third-party or org-owned action:

1. Resolve the ref to a 40-character commit SHA. Prefer `gh api repos/<repo>/commits/<tag>` (always returns the commit SHA directly, even for annotated tags). If that fails, fall back to `gh api repos/<repo>/git/ref/tags/<tag>` and recurse through the tag object until a commit SHA is found.
2. Replace the tag with the SHA and append a `# vX.Y.Z` comment. Example: `uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2`.
3. Channel-style refs (e.g. `dtolnay/rust-toolchain@stable`): pin to the SHA of the named branch's HEAD (`gh api repos/<repo>/commits/<branch>`) and use `# stable` (or the branch name) as the comment.
4. Reusable workflow refs (`org/repo/.github/workflows/foo.yml@vN`): pin them too. Tag immutability is not a function of repo ownership.
5. First-party `./` refs (e.g. `uses: ./.github/actions/local`): leave unpinned; they resolve to the current commit by definition.

Reference: `./references/github-actions.md` for full recipes including annotated-vs-lightweight tag handling and how to bump a held major version.

### 4. Pin Language Runtimes via Version Files

Replace inline pins in scaffolded CI with version-file refs so the version of record is a single file in the repo:

| Inline form                       | Version-file form                                                                                                                                          |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `node-version: "X"`               | `node-version-file: ".tool-versions"`                                                                                                                      |
| `ruby-version: "X"`               | `ruby-version-file: ".tool-versions"`                                                                                                                      |
| `go-version: "stable"` or `"X.Y"` | `go-version-file: "go.mod"`                                                                                                                                |
| `python-version: "X.Y"`           | `python-version-file: ".python-version"`                                                                                                                   |
| `zig-version: "X.Y.Z"`            | Action-direct (`mlugg/setup-zig`): omit (reads `build.zig.zon`). Wrapper (`cboone/gh-actions/.../zig-ci.yml` v2.2.0+): `zig-version-file: "build.zig.zon"` |

If the corresponding version file is missing in the repo, create it with current LTS / stable values. Reference `./references/language-runtimes.md` for the LTS / stable lookup commands per language.

### 5. Pin Yarn (Corepack) with SHA-512 Integrity

If `package.json` has `"packageManager": "yarn@X.Y.Z"`:

1. Compute the SHA-512 integrity hash. Preferred path: `corepack use yarn@X.Y.Z` — this downloads the requested Yarn release, computes the integrity hash, and writes the suffixed `yarn@X.Y.Z+sha512.<hash>` form into `package.json`'s `packageManager` field in one command. (`corepack prepare ... --activate` only prepares and activates the binary globally; it does not touch `package.json`.) Fall back to fetching `https://repo.yarnpkg.com/${X.Y.Z}/packages/yarnpkg-cli/bin/yarn.js` and computing `shasum -a 512` if Corepack is unavailable (`shasum` is portable across macOS and Linux; `sha512sum` is Linux-only).
2. Rewrite the field as `"yarn@X.Y.Z+sha512.<hash>"`.
3. Verify with `corepack enable && yarn --version`.

Reference: `./references/yarn-corepack.md`.

### 6. Exact-Pin Package-Manager Dependencies (Application Context Only)

Strip `^`/`~` ranges from manifests, replacing each with the exact version locked in the lockfile. **Discriminate library from application before touching the manifest** — exact-pinning a library's manifest breaks downstream version unification.

| Ecosystem | Application discriminator                                                                                                                         | Library discriminator                                              | Default if app     |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ------------------ |
| Node.js   | Lockfile committed AND (`"private": true` OR no published `name` exposure)                                                                        | Library packages with `name`/`exports` configured for distribution | Pin manifest       |
| Ruby      | No `*.gemspec`; `Gemfile.lock` committed                                                                                                          | `*.gemspec` present (gem)                                          | Pin from lockfile  |
| Python    | `requirements.txt` or `uv.lock` committed; no library distribution name                                                                           | `pyproject.toml` declares a published distribution                 | Pin to `==`        |
| Rust      | `Cargo.lock` committed AND crate has a binary target (`[[bin]]`, `src/main.rs`, or `src/bin/*.rs`; `publish = false` is also a strong app signal) | Crate exposes `[lib]`; `Cargo.lock` typically not committed        | Exact-pin manifest |

When the discriminator is ambiguous (monorepo workspaces, hybrid crates, gems with bin entrypoints), prompt the user. **Always pin the lockfile** even for libraries — that is what `yarn install --frozen-lockfile` and friends consume in CI. Only the *manifest* changes between app and library treatment.

### 7. Pin Install Commands

For every install invocation in CI templates, Makefiles, scripts, and skill docs:

| Command                                                   | Pinned form                                      | Upstream-of-record                  |
| --------------------------------------------------------- | ------------------------------------------------ | ----------------------------------- |
| `go install <path>@latest`                                | `go install <path>@vX.Y.Z`                       | GitHub releases for the path's repo |
| `cargo install <crate>` (no version)                      | `cargo install --locked --version X.Y.Z <crate>` | crates.io                           |
| `pip install <pkg>` (no `==`)                             | `pip install '<pkg>==X.Y.Z'`                     | PyPI                                |
| `uv pip install <pkg>` / `uv add <pkg>`                   | `uv pip install '<pkg>==X.Y.Z'`                  | PyPI                                |
| `npx <tool>` (no `@version`, in CI without prior install) | `npx <tool>@X.Y.Z`                               | npm registry                        |

**Skip user-facing placeholders.** If the install path contains `OWNER/REPO`, `GITHUB-USERNAME`, `PROJECT-NAME`, or `<...>`-style placeholders, leave the `@latest` (or unversioned form) intact — it's a template the downstream user will customize.

**Skip local-dev examples that resolve via lockfile.** `npx prettier --write .` inside a `package.json` repo with a committed `prettier` devDependency is fine unpinned; the lockfile is the version of record.

Reference: `./references/install-commands.md`.

### 8. Tighten `.yarnrc.yml` (If Present)

Make security-strict defaults explicit so future Corepack migrations cannot silently re-enable scripts or whitelist arbitrary git sources:

```yaml
enableScripts: false
enableTelemetry: false
defaultSemverRangePrefix: ""
```

Also detect and revert harmful additions made by past Corepack migrations: `approvedGitRepositories: ["**"]`, `enableScripts: true`. Reference: `./references/yarn-corepack.md`.

### 9. Add Dependabot Config

Create or merge `.github/dependabot.yml` with:

- Weekly schedule.
- Per-ecosystem split groups (`<ecosystem>-minor-patch` and `<ecosystem>-major`) so minor/patch can auto-merge later while majors get human review.
- 10-PR cap per ecosystem (raised from the default of 5 — SHA-pinning produces finer-grained PRs than tag-pinning).
- `versioning-strategy: increase` for `npm` (and for `pip` if step 6 exact-pinned Python requirements to `==X.Y.Z`) so existing exact pins are not widened on the first Dependabot bump.
- Coverage for `github-actions` plus whichever package ecosystems are present in the repo (`npm`, `cargo`, `pip`, `bundler`, `gomod`).

Skip this step if `--no-dependabot` was passed. Reference: `./references/dependabot.md`.

### 10. Optionally Generate a Version-Audit Script

Dependabot does not cover four surfaces: `.tool-versions`, `packageManager`, action SHAs in `.md` templates, and install-command pins inside scripts. If the user wants drift coverage for these:

1. Read `./references/scripts/version-audit-template`.
2. Tailor it to the surfaces actually present in the repo (drop unused `audit_*` functions, adjust grep paths to match the user's directory layout).
3. Write the result to `bin/version-audit` and `chmod +x`.
4. Read `./references/scripts/version-audit-workflow-template.yml`.
5. Refresh the `actions/checkout` SHA against current upstream (per [Refresh Own SHAs at Scaffold Time](#refresh-own-shas-at-scaffold-time)). Confirm the cron schedule and `ISSUE_LABEL` suit the project, then write the result to `.github/workflows/version-audit.yml`. Scan paths are configured in the script's `SCAN_PATHS`, not the workflow.

Skip this step if `--no-audit` was passed. Reference: `./references/version-audit.md`.

### 11. Verify and Commit

1. Re-run the audit from step 1 and confirm zero unpinned surfaces remain (modulo the deliberate exclusions confirmed in step 2).
2. Invoke the `lint-and-fix` skill via the Skill tool to run project linters and formatters.
3. If the user has REUSE/SPDX licensing set up (root `REUSE.toml` present), invoke `manage-repo-licensing` to add SPDX coverage for any newly emitted files (`bin/version-audit`, `.github/workflows/version-audit.yml`, `.github/dependabot.yml`) and run `reuse lint`.
4. Commit with a Conventional Commits message scoped to what was pinned. Default to one commit per category for clarity (e.g. `chore: SHA-pin third-party action refs`, `chore: pin install commands`, `chore: add Dependabot config`). If the user prefers a single bundled commit, do that instead.

## Options

- `--scope <comma-list>` — restrict the run to a subset of surface categories. Categories: `actions`, `runtimes`, `yarn`, `manifest`, `installs`, `yarnrc`, `dependabot`, `audit`. Example: `--scope actions,runtimes`.
- `--no-audit` — skip step 10 (do not emit `bin/version-audit` or its workflow).
- `--no-dependabot` — skip step 9 (do not write `.github/dependabot.yml`).
- `--dry-run` — perform the audit (step 1) and report findings, but do not edit any files.

## Error Handling

- **Tag does not resolve to a commit.** Annotated tags resolve via the tag object; lightweight tags resolve directly. If `gh api repos/<r>/git/ref/tags/<t>` returns a `tag` type, recurse through `.object.sha` to find the commit. The `gh api repos/<r>/commits/<tag>` endpoint sidesteps this entirely and is the preferred path.
- **Action does not support a version-file input.** For action-direct `mlugg/setup-zig`, omit the version input entirely — the action reads `build.zig.zon`'s `minimum_zig_version` by default. The `cboone/gh-actions/.../zig-ci.yml` wrapper (v2.2.0+) exposes a real `zig-version-file: "build.zig.zon"` input. For other languages without a `*-version-file` input, pin inline to the value from the version file rather than dropping pinning entirely.
- **Ambiguous user-facing vs tool-install distinction.** If the install path looks like a real tool but lives in a scaffolded README under a `Usage:` heading or similar, prompt the user. Default to leaving placeholder-shaped paths unpinned.
- **Conflicting existing Dependabot config.** If `.github/dependabot.yml` already exists, do not overwrite — merge: keep user-specific groups and schedules, add only the missing ecosystems and the standard split-group structure for ecosystems that lacked it. Show the diff before writing.
- **Library detected when user expected an app pin.** Surface the library discriminator explicitly ("`Cargo.lock` not committed and crate exposes `[lib]` only — treating as a library and skipping manifest exact-pinning"). Let the user override per-ecosystem if the heuristic is wrong.

## Reference Templates

- `./references/checklist.md` — single-page rapid checklist for every surface and its pinning command
- `./references/github-actions.md` — SHA-pinning recipes (annotated tags, channel refs, reusable workflows, held majors)
- `./references/language-runtimes.md` — per-language version-file recipes and LTS / stable lookup commands
- `./references/install-commands.md` — per-package-manager pinning recipes and upstream-of-record APIs
- `./references/yarn-corepack.md` — Yarn SHA-512 integrity, `.yarnrc.yml` strictness, Corepack migration handling
- `./references/dependabot.md` — `dependabot.yml` template with split groups, schedule, and PR caps
- `./references/version-audit.md` — how to install and tailor the bundled `version-audit-template` script
- `./references/scripts/version-audit-template` — bash audit-script template (the skill writes a tailored copy to the user's `bin/`)
- `./references/scripts/version-audit-workflow-template.yml` — companion GitHub Actions workflow template

## Refresh Own SHAs at Scaffold Time

The example SHAs in this skill's own reference docs rot as upstream actions cut new releases. Before emitting any scaffolded workflow or template into a user's repo, refresh both the SHA and the `# vX.Y.Z` comment for each `uses:` ref against current upstream. The canonical example commits in [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) (the SHA-pin pass from PR #250 onwards) are the source of truth — when they update, the skill's references should follow.

For a quick refresh of a single ref:

```bash
TAG="$(gh release view --repo OWNER/REPO --json tagName --jq '.tagName')"
SHA="$(gh api "repos/OWNER/REPO/commits/${TAG}" --jq '.sha')"
echo "${SHA} # ${TAG}"
```

Dependabot in the consuming user's repo keeps the emitted refs current after the initial scaffold.
