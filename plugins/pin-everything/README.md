# Pin Everything

Pin every version surface in a repository to commit hashes, integrity digests, or specific versions as a one-shot supply-chain hardening pass.

**Type:** Skill
**Trigger:** `/pin-everything` (also activates automatically)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Walks an existing repository through a one-shot hardening pass that closes the surfaces an attacker can reach via mutable version refs. The skill audits the repo, presents the findings, confirms scope with the user, then pins each category in turn:

- **GitHub Actions `uses:` refs** — replaced with 40-char commit SHAs and `# vX.Y.Z` comments (covers reusable workflows and channel refs too).
- **Yarn via Corepack** — `packageManager: yarn@X.Y.Z` rewritten to `yarn@X.Y.Z+sha512.<hash>`; `.yarnrc.yml` strict defaults made explicit.
- **Package-manager dependencies** — exact-pinned in application context (Node.js, Ruby, Python, Rust); left as ranges in library context to avoid breaking downstream version unification.
- **Language runtimes in CI** — inline `node-version: "X"` etc. swapped for `node-version-file: ".tool-versions"` and friends; missing version files created with current LTS / stable values.
- **Install commands** — `go install`, `cargo install`, `pip install`, `uv add`, `npx <tool>` rewritten with explicit pinned forms (skipping placeholder paths in scaffolded templates).
- **Dependabot** — `.github/dependabot.yml` created or merged with weekly schedule, split groups by update-type, 10-PR cap per ecosystem.
- **Drift audit (optional)** — bundled `version-audit` script and weekly workflow cover the four surfaces Dependabot does not (`.tool-versions`, `packageManager`, action SHAs in `.md` templates, install-command pins inside scripts).

The skill confirms scope before each batch and supports per-category opt-out, so adopters who only want SHA-pinned actions can stop after the first batch. A `--dry-run` mode reports findings without editing.

## Requirements

- [`gh`](https://cli.github.com/) (authenticated). Install via Homebrew: `brew install gh`.
- [`jq`](https://jqlang.org/). Install via Homebrew: `brew install jq`.
- [`corepack`](https://github.com/nodejs/corepack) (only when pinning Yarn or pnpm via `package.json`'s `packageManager` field; step 5 invokes `corepack use yarn@…` or `corepack use pnpm@…` and verifies with the corresponding `--version`). Bundled with modern Node.js; activate via `corepack enable`.
- [`reuse`](https://reuse.software/) (only when the consuming repo has REUSE/SPDX licensing set up). Install via Homebrew: `brew install reuse`.
- [`curl`](https://curl.se/) and Bash 4+ (only when the bundled `version-audit` script is generated; the script's drift checks against `nodejs.org`, `repo.yarnpkg.com`, `registry.npmjs.org`, `crates.io`, and `pypi.org` use `curl`, and its `declare -A` associative arrays require Bash 4+). `curl` ships with macOS and most Linux distros; macOS ships only Bash 3.2 by default, so install Bash 4+ via Homebrew: `brew install bash`.

## Usage

```text
/pin-everything [--scope <comma-list>] [--no-audit] [--no-dependabot] [--dry-run]
```

| Option            | Effect                                                                                                                                                                       |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--scope <list>`  | Restrict to a subset of categories: `actions,runtimes,corepack,manifest,installs,yarnrc,dependabot,audit` (the `corepack` scope covers Yarn and pnpm; `yarnrc` is Yarn-only) |
| `--no-audit`      | Skip generating `bin/version-audit` and its workflow                                                                                                                         |
| `--no-dependabot` | Skip writing `.github/dependabot.yml`                                                                                                                                        |
| `--dry-run`       | Audit and report; do not edit any files                                                                                                                                      |

## Recommended Permissions

This skill runs `gh api` queries to resolve action tags to SHAs, `curl` lookups against language and registry endpoints, `corepack` (with a `shasum` fallback) to compute Yarn integrity hashes, `chmod +x` to mark the emitted `bin/version-audit` script executable, and `git add` / `git commit` to land the resulting changes. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": [
      "Bash(gh api:*)",
      "Bash(gh release view:*)",
      "Bash(curl:*)",
      "Bash(corepack use:*)",
      "Bash(corepack enable)",
      "Bash(yarn --version)",
      "Bash(pnpm --version)",
      "Bash(shasum:*)",
      "Bash(chmod +x:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)"
    ]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "pin everything in this repo" — full hardening pass
- "harden against supply-chain attacks" — same behavior
- "SHA-pin all the actions" — actions-only scope
- "audit version pins" — `--dry-run` style audit only
- `/pin-everything --scope actions,dependabot` — actions + Dependabot only

## See Also

- [Set-Up Secret Scanning](../set-up-secret-scanning/README.md): credential-leak hardening (sibling supply-chain concern)
- [Refresh Project Scaffolding](../refresh-project-scaffolding/README.md): ongoing template-drift detection (different cadence)
- [Manage Repo Licensing](../manage-repo-licensing/README.md): SPDX coverage for newly emitted files
- [Lint and Fix](../lint-and-fix/README.md): invoked after pinning to format affected files
- [All plugins](../../README.md)
