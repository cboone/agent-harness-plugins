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
  detection use refresh-project-scaffolding; for credential-leak hardening use
  set-up-secret-scanning.
---

# Pin Everything

Pin every version surface in a repository as a one-shot supply-chain hardening pass: SHA pins for actions, integrity hashes for Corepack, exact pins for package-manager dependencies (in application context), version-file refs for language runtimes, and explicit versions for install commands. Optionally generates a weekly drift-audit script and tightens Dependabot.

This skill is a generalization of the canonical hardening pass executed in [PR #250](https://github.com/cboone/agent-harness-plugins/pull/250) on `agent-harness-plugins` itself. Adopters who want to repeat that pass on their own repositories run the skill end-to-end. Adopters who only want a subset (for example, SHA-pinning actions) can stop after the relevant step.

## Workflow

### 1. Audit the Repo for Version Surfaces

Scan the working tree for every version surface, then output a categorized table (file paths, count of refs, current pin state).

Surfaces to detect:

| Category                    | Detection                                                                                                                                                                                                 |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GitHub Actions `uses:` refs | Glob `.github/workflows/*.{yml,yaml}` and `.github/actions/**/action.{yml,yaml}`; also grep `**/*.md` for `uses:` lines (scaffolded reference docs and templates often embed real refs); grep for `uses:` |
| Reusable workflow refs      | Same files plus the same Markdown sweep; grep for `uses:` lines containing `.github/workflows/`                                                                                                           |
| `packageManager` field      | Read `package.json`; check `.packageManager`                                                                                                                                                              |
| `package.json` deps         | Read `package.json`; flag `^`/`~` ranges in `dependencies`/`devDependencies`. **Skip `peerDependencies`** — see step 6.                                                                                   |
| Language version files      | Glob `.tool-versions`, `.nvmrc`, `.node-version`, `.ruby-version`, `.python-version`, `rust-toolchain.toml`, `build.zig.zon`; also grep `Gemfile` for a `ruby` directive                                  |
| `go.mod` `go` directive     | Read `go.mod`; capture the directive line                                                                                                                                                                 |
| Inline language pins in CI  | Grep workflows for `node-version:`, `ruby-version:`, `go-version:`, `python-version:`, `zig-version:` (without `-file` suffix)                                                                            |
| `go install` pins           | Grep for `go install <path>@<ref>` where `<ref>` is `latest`, a `vN.Y.Z` tag (with optional prerelease), or a pseudo-version (`v0.0.0-YYYYMMDDhhmmss-<12-hex>`)                                           |
| `cargo install` pins        | Grep for `cargo install` with or without `--locked --version`                                                                                                                                             |
| `pip` / `uv` pins           | Grep for `pip install`, `uv pip install`, `uv add`, `uv tool install`, `uvx` (with or without `==`)                                                                                                       |
| `npx` pins                  | Grep for `npx <name>` (with or without `@version`)                                                                                                                                                        |
| Schema URLs                 | Grep `*.json` and `*.yaml` for `$schema` URLs containing `@latest`. Pinning is per-publisher (see step 7).                                                                                                |

Exclude vendored directories from all greps: `node_modules/`, `.yarn/`, `vendor/`, `dist/`, `target/`, `.venv/`. Markdown templates with `uses:` refs that the consuming repo distributes downstream (skill scaffolds, README install snippets, etc.) are still in scope: real refs there should be pinned and refreshed against upstream just like CI workflows. The deliberate exclusions for placeholder paths (`OWNER/REPO`, `<...>`, etc.) are documented in step 7 and apply to install commands, not `uses:` refs.

Print the output as a Markdown table grouped by category, with one row per file showing the file path, the count of matching refs, and a one-word state (`pinned` / `unpinned` / `mixed`).

### 2. Confirm Scope with the User

Present the categorized findings. The default is to pin everything in the repo that is not deliberately user-facing. User-facing means scaffolded README install instructions, placeholder paths in skill templates, and similar documentation that downstream users will customize.

Ask the user to confirm or trim the scope. Offer per-category opt-out (e.g., "skip pip pinning", "skip Dependabot config", "actions only"). If the user invokes the skill with `--scope <comma-list>`, use that list directly; otherwise prompt.

If the user requested `--dry-run`, or invoked the skill with audit-only phrasing (e.g. "audit version pins", "audit pins", "report unpinned versions", or any other request that asks for findings without changes), perform the audit only and stop here. Treat all audit-shaped trigger phrases the same as `--dry-run` so the README's "audit version pins" example does not silently fall into the mutating path.

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

| Inline form                       | Version-file form                                                                                                                                                                           |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `node-version: "X"`               | `.tool-versions` if it has a `nodejs` line, else `.nvmrc`, else `.node-version`                                                                                                             |
| `ruby-version: "X"`               | `.tool-versions` if it has a `ruby` line, else `.ruby-version`, else `Gemfile` (if it has a `ruby` directive)                                                                               |
| `go-version: "stable"` or `"X.Y"` | `go-version-file: "go.mod"`                                                                                                                                                                 |
| `python-version: "X.Y"`           | `astral-sh/setup-uv`: omit input (reads `pyproject.toml` `requires-python` directly). `actions/setup-python`: `python-version-file: ".python-version"`; create `.python-version` if missing |
| `zig-version: "X.Y.Z"`            | Action-direct (`mlugg/setup-zig`): omit (reads `build.zig.zon`). Wrapper (`cboone/gh-actions/.../run-zig-ci.yml` v2.2.0+): `zig-version-file: "build.zig.zon"`                              |

**Reuse the file that already pins this language.** Audit step 1 already enumerates which version files exist in the repo and what each one contains. Mere existence is not enough — a `.tool-versions` that lists only `python` and `ruby` will not configure Node when CI loads it. Verify the file has an entry for the language being configured before pointing the `*-version-file` input at it. If `.nvmrc` is present, point `node-version-file` at it instead of introducing a parallel `.tool-versions`. The whole purpose of the version-file rewrite is to make CI and local dev agree on a single source of truth; emitting a second file (or pointing at a file that lacks the relevant entry) silently re-creates the drift or breaks the workflow.

If no version file pins this language, either add a line to an existing `.tool-versions` (preferred when one is already present) or create the language's conventional file (`.tool-versions` with the language's line, `.python-version` for Python, `rust-toolchain.toml` for Rust) with current LTS / stable values. Reference `./references/language-runtimes.md` for the LTS / stable lookup commands per language and the per-language fallback order.

**Python special case: do not create `.python-version` for `astral-sh/setup-uv` workflows.** uv reads `pyproject.toml`'s `[project] requires-python` directly, so `pyproject.toml` is the version source. Adding a separate `.python-version` creates a second source that uv ignores and that local tooling and CI can drift apart on; the established convention in this repo (see `plugins/set-up-ci/skills/set-up-ci/SKILL.md` and `plugins/set-up-ci/skills/set-up-ci/references/ci-python.md`) is to keep `requires-python` as the only version source for uv workflows. If `requires-python` is missing, add it to `pyproject.toml`; do not create a parallel `.python-version`. Only create `.python-version` when the workflow uses `actions/setup-python`, which has no equivalent automatic source.

**Normalize the file's value to an exact `X.Y.Z` before treating the rewrite as a pin.** Existing version files routinely carry moving forms that look pinned but aren't: `.nvmrc` accepts aliases like `lts/*`, `lts/iron`, `node`, and `latest`; `.ruby-version`, `.python-version`, and `.tool-versions` entries are often major-only (`3.4`) or truncated to major+minor (`3.13`). CI that reads any of those values resolves them at install time, so each fresh runner can pick a different patch release while the workflow still claims to be "pinned to" the file. After selecting (or creating) the file, inspect its current contents and, if the value is anything other than an exact `X.Y.Z`, rewrite it to the matching exact release **within the existing release line**: the latest patch in the same major for Node.js (so `.nvmrc = 23` becomes the highest `23.x.y`, not the current LTS major), and the latest patch in the same X.Y feature line for Ruby and Python (so `.ruby-version = 3.4` becomes the highest `3.4.z`, not whatever `3.5.x` may already be cut). Reach for the global LTS / stable lookup only when no version file existed before this pass and a fresh release line is being chosen. See `./references/language-runtimes.md` for both the in-series and the create-from-scratch lookup commands. Only then has the runtime actually been pinned.

### 5. Pin the Corepack `packageManager` Field with SHA-512 Integrity

If `package.json` has `"packageManager": "<yarn|pnpm>@X.Y.Z"`:

1. Compute the SHA-512 integrity hash via Corepack itself. Run `corepack use yarn@X.Y.Z` for Yarn or `corepack use pnpm@X.Y.Z` for pnpm — either form downloads the requested release, computes the integrity hash, and writes the suffixed `<yarn|pnpm>@X.Y.Z+sha512.<hash>` form into `package.json`'s `packageManager` field in one command. (`corepack prepare ... --activate` only prepares and activates the binary globally; it does not touch `package.json`.) Fall back to fetching the upstream tarball and computing `shasum -a 512` if Corepack is unavailable: Yarn lives at `https://repo.yarnpkg.com/${X.Y.Z}/packages/yarnpkg-cli/bin/yarn.js`; pnpm lives at `https://registry.npmjs.org/pnpm/-/pnpm-${X.Y.Z}.tgz`. Use `shasum -a 512` (portable across macOS and Linux); `sha512sum` is Linux-only.
2. Rewrite the field as `"<yarn|pnpm>@X.Y.Z+sha512.<hash>"`.
3. Verify with `corepack enable && (yarn|pnpm) --version`.

npm-managed projects have no equivalent integrity surface in `package.json` — rely on `package-lock.json`'s per-package integrity hashes plus `npm ci` in CI. Skip this step when `packageManager` is absent or names `npm`.

Reference: `./references/yarn-corepack.md` (Yarn-specific `.yarnrc.yml` hardening covered in step 8 does not apply to pnpm).

### 6. Exact-Pin Package-Manager Dependencies (Application Context Only)

Strip `^`/`~` ranges from manifests, replacing each with the exact version locked in the lockfile. **Discriminate library from application before touching the manifest** — exact-pinning a library's manifest breaks downstream version unification.

| Ecosystem | Application discriminator                                                                                                                         | Library discriminator                                              | Default if app     |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ------------------ |
| Node.js   | Lockfile committed AND (`"private": true` OR no published `name` exposure)                                                                        | Library packages with `name`/`exports` configured for distribution | Pin manifest       |
| Ruby      | No `*.gemspec`; `Gemfile.lock` committed                                                                                                          | `*.gemspec` present (gem)                                          | Pin from lockfile  |
| Python    | `requirements.txt` or `uv.lock` committed; no library distribution name                                                                           | `pyproject.toml` declares a published distribution                 | Pin to `==`        |
| Rust      | `Cargo.lock` committed AND crate has a binary target (`[[bin]]`, `src/main.rs`, or `src/bin/*.rs`; `publish = false` is also a strong app signal) | Crate exposes `[lib]`; `Cargo.lock` typically not committed        | Exact-pin manifest |

When the discriminator is ambiguous (monorepo workspaces, hybrid crates, gems with bin entrypoints), prompt the user. **Always pin the lockfile** even for libraries — that is what `yarn install --frozen-lockfile` and friends consume in CI. Only the _manifest_ changes between app and library treatment.

**Never exact-pin Node.js `peerDependencies`.** They express the range of host versions a package is compatible with; rewriting them to `==X.Y.Z` overconstrains downstream installers and can break otherwise compatible consumers. Leave the existing range (caret, pessimistic, or `>=`) intact even when pinning `dependencies` and `devDependencies`. The same logic applies to `optionalPeerDependencies`. The audit in step 1 already excludes `peerDependencies`; do not reintroduce them here.

### 7. Pin Install Commands

For every install invocation in CI templates, Makefiles, scripts, and skill docs:

| Command                                                   | Pinned form                                      | Upstream-of-record                                                                                                     |
| --------------------------------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| `go install <path>@latest`                                | `go install <path>@vX.Y.Z`                       | GitHub releases for the path's repo, falling back to its Tags API for repos that publish version tags without releases |
| `cargo install <crate>` (no version)                      | `cargo install --locked --version X.Y.Z <crate>` | crates.io                                                                                                              |
| `pip install <pkg>` (no `==`)                             | `pip install '<pkg>==X.Y.Z'`                     | PyPI                                                                                                                   |
| `uv pip install <pkg>`                                    | `uv pip install '<pkg>==X.Y.Z'`                  | PyPI                                                                                                                   |
| `uv add <pkg>`                                            | `uv add '<pkg>==X.Y.Z'`                          | PyPI                                                                                                                   |
| `uv tool install <pkg>`                                   | `uv tool install '<pkg>==X.Y.Z'`                 | PyPI                                                                                                                   |
| `uvx <pkg> [args]` (no `==`)                              | `uvx '<pkg>==X.Y.Z' [args]`                      | PyPI                                                                                                                   |
| `npx <tool>` (no `@version`, in CI without prior install) | `npx <tool>@X.Y.Z`                               | npm registry                                                                                                           |

**Preserve the uv verb when adding a `==` pin.** The four uv install surfaces are not interchangeable and rewriting one as another silently changes scope: `uv pip install` mutates the active environment, `uv add` records the dependency in `pyproject.toml` and `uv.lock`, `uv tool install` installs a tool persistently to the user-global `~/.local/bin`, and `uvx` (alias for `uv tool run`) executes a tool ephemerally from a cached install. Pin in place, never swap.

**Skip user-facing placeholders.** If the install path contains `OWNER/REPO`, `GITHUB-USERNAME`, `PROJECT-NAME`, or `<...>`-style placeholders, leave the `@latest` (or unversioned form) intact — it's a template the downstream user will customize.

**Skip local-dev examples that resolve via lockfile.** `npx prettier --write .` inside a `package.json` repo with a committed `prettier` devDependency is fine unpinned; the lockfile is the version of record.

**Schema URLs (`$schema: ...@latest`).** Whether they can be pinned depends on the publisher. JSON Schema Store and similar registries expose versioned URLs (e.g., `https://json.schemastore.org/foo-1.2.3.json`); rewrite the `@latest` form to the current versioned URL when one exists. Some publishers only ship a moving `@latest` URL with no immutable mirror — record those in the audit summary as "publisher exposes no versioned URL" and exclude them from the step 11 re-audit. Do not block verification on a surface that has no upstream pinning mechanism. Schema URL pins are also out of scope for the recurring drift audit emitted by step 10 — see that step's preamble for why.

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

Dependabot does not cover four surface families: language version files (`.tool-versions`, `.nvmrc`, `.node-version`, `.ruby-version`, `Gemfile`, `.python-version`, `go.mod`, `rust-toolchain.toml`, `build.zig.zon`), `packageManager`, action SHAs in `.md` templates, and install-command pins inside scripts. Schema URLs (step 7) are a fifth Dependabot-uncovered family but are deliberately out of scope here: drift detection is publisher-specific (JSON Schema Store, vendored cloud schemas, and ad-hoc registries each expose versioned URLs differently, and many publishers expose no versioned URL at all), so a generic auditor would either always-pass or always-flag. Record schema URL pins in the step 1 audit summary instead and refresh them by hand when the publisher cuts a new version. If the user wants drift coverage for the four covered families:

1. Read `./references/scripts/version-audit-template`.
2. Tailor it to the surfaces actually present in the repo (drop unused `audit_*` functions, adjust grep paths to match the user's directory layout).
3. Write the result to `bin/version-audit` and `chmod +x`.
4. Read `./references/scripts/version-audit-workflow-template.yml`.
5. Refresh the `actions/checkout` SHA against current upstream (per [Refresh Own SHAs at Scaffold Time](#refresh-own-shas-at-scaffold-time)). Confirm the cron schedule and `ISSUE_LABEL` suit the project, then write the result to `.github/workflows/version-audit.yml`. Scan paths are configured in the script's `SCAN_PATHS`, not the workflow.

Skip this step if `--no-audit` was passed. Reference: `./references/version-audit.md`.

### 11. Verify and Commit

1. Re-run the audit from step 1 and confirm zero unpinned surfaces remain (modulo the deliberate exclusions confirmed in step 2 and any schema URLs whose publisher exposes no versioned upstream — see step 7).
2. Invoke the `lint-and-fix` skill via the Skill tool to run project linters and formatters.
3. If the user has REUSE/SPDX licensing set up (root `REUSE.toml` present), invoke `manage-repo-licensing` to add SPDX coverage for any newly emitted files (`bin/version-audit`, `.github/workflows/version-audit.yml`, `.github/dependabot.yml`) and run `reuse lint`.
4. Commit with a Conventional Commits message scoped to what was pinned. Default to one commit per category for clarity (e.g. `chore: SHA-pin third-party action refs`, `chore: pin install commands`, `chore: add Dependabot config`). If the user prefers a single bundled commit, do that instead.

## Options

- `--scope <comma-list>` — restrict the run to a subset of surface categories. Categories: `actions`, `runtimes`, `corepack` (covers both Yarn and pnpm via Corepack — see step 5), `manifest`, `installs`, `yarnrc` (Yarn-only `.yarnrc.yml` hardening — see step 8), `dependabot`, `audit`. Example: `--scope actions,runtimes`.
- `--no-audit` — skip step 10 (do not emit `bin/version-audit` or its workflow).
- `--no-dependabot` — skip step 9 (do not write `.github/dependabot.yml`).
- `--dry-run` — perform the audit (step 1) and report findings, but do not edit any files.

## Error Handling

- **Tag does not resolve to a commit.** Annotated tags resolve via the tag object; lightweight tags resolve directly. If `gh api repos/<r>/git/ref/tags/<t>` returns a `tag` type, recurse through `.object.sha` to find the commit. The `gh api repos/<r>/commits/<tag>` endpoint sidesteps this entirely and is the preferred path.
- **Action does not support a version-file input.** For action-direct `mlugg/setup-zig`, omit the version input entirely — the action reads `build.zig.zon`'s `minimum_zig_version` by default. The `cboone/gh-actions/.../run-zig-ci.yml` wrapper (v2.2.0+) exposes a real `zig-version-file: "build.zig.zon"` input. For other languages without a `*-version-file` input, pin inline to the value from the version file rather than dropping pinning entirely.
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

The example SHAs in this skill's own reference docs rot as upstream actions cut new releases. Before emitting any scaffolded workflow or template into a user's repo, refresh both the SHA and the `# vX.Y.Z` comment for each `uses:` ref against current upstream. The canonical example commits in [`cboone/agent-harness-plugins`](https://github.com/cboone/agent-harness-plugins) (the SHA-pin pass from PR #250 onwards) are the source of truth — when they update, the skill's references should follow.

For a quick refresh of a single ref:

```bash
TAG="$(gh release view --repo OWNER/REPO --json tagName --jq '.tagName')"
SHA="$(gh api "repos/OWNER/REPO/commits/${TAG}" --jq '.sha')"
echo "${SHA} # ${TAG}"
```

Dependabot in the consuming user's repo keeps the emitted refs current after the initial scaffold.
