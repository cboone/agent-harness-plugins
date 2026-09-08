# Dependabot Configuration

How to write `.github/dependabot.yml` for repositories that have been pinned by this skill.

## Why Dependabot Matters Even More After Pinning

SHA-pinning is a one-shot hardening pass; without something keeping pins current, they rot. Dependabot is the standard mechanism for proposing version bumps automatically, opening one PR per outdated dependency on a schedule. Once SHA pins are in place, Dependabot's PR diffs become more readable (the `# vX.Y.Z` comment is what users see in the diff title) and easier to review.

The configuration below is structured around the post-pinning workflow:

- **Weekly schedule** — daily is too noisy when every action and every dep gets its own PR.
- **Split groups by update-type** — minor/patch can auto-merge later (separate concern); majors get human review.
- **10-PR cap per ecosystem** — raised from the default of 5 because SHA-pinning produces finer-grained PRs than tag-pinning.
- **`versioning-strategy: increase` for `npm`** — tells Dependabot to bump the existing exact pin instead of widening the range. Without this, Dependabot will rewrite `"prettier": "3.8.3"` as `"prettier": "^3.9.0"` on the next bump, undoing step 6.

## Template

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    open-pull-requests-limit: 10
    groups:
      actions-minor-patch:
        patterns: ["*"]
        update-types: [minor, patch]
      actions-major:
        patterns: ["*"]
        update-types: [major]
    commit-message:
      prefix: chore
      include: scope

  - package-ecosystem: npm
    directory: /
    schedule:
      interval: weekly
    versioning-strategy: increase
    open-pull-requests-limit: 10
    groups:
      npm-minor-patch:
        patterns: ["*"]
        update-types: [minor, patch]
      npm-major:
        patterns: ["*"]
        update-types: [major]
    commit-message:
      prefix: chore
      include: scope
```

Add additional `- package-ecosystem:` blocks for whichever package ecosystems are present in the repo:

| Ecosystem present | Detection                              | Add block with `package-ecosystem:` |
| ----------------- | -------------------------------------- | ----------------------------------- |
| Cargo (Rust)      | `Cargo.toml`                           | `cargo`                             |
| Pip / uv (Python) | `pyproject.toml` or `requirements.txt` | `pip`                               |
| Bundler (Ruby)    | `Gemfile`                              | `bundler`                           |
| Go modules        | `go.mod`                               | `gomod`                             |
| Composer (PHP)    | `composer.json`                        | `composer`                          |
| Docker            | `Dockerfile`                           | `docker`                            |

The same shape applies — weekly schedule, split groups, 10-PR cap, `commit-message` prefix.

## `versioning-strategy` Per Ecosystem

| Ecosystem        | Strategy                                                                         |
| ---------------- | -------------------------------------------------------------------------------- |
| `npm`            | `versioning-strategy: increase` (preserves exact pins from step 6)               |
| `cargo`          | _no strategy needed_ (cargo is exact-version-by-default for `=X.Y.Z` pins)       |
| `pip`            | `versioning-strategy: increase` if you've pinned to `==X.Y.Z`; default otherwise |
| `bundler`        | _no strategy field_; uses the lockfile as the source of truth                    |
| `gomod`          | _no strategy field_; uses `go.sum` as the source of truth                        |
| `github-actions` | _no strategy field_; SHA pins with `# vX.Y.Z` comments are bumped one-for-one    |

## What Dependabot Does Not Cover

Four surface families are outside Dependabot's scope:

1. **Language version files** — `.tool-versions`, `.nvmrc`, `.node-version`, `.ruby-version`, `.python-version`. There's no Dependabot ecosystem for any of these per-language pin files (asdf-style `.tool-versions` and the per-language fallback files are silent surfaces). Drift accumulates until something triggers a manual bump.
2. **`packageManager` field** — Dependabot recognizes the field but does not propose updates to it.
3. **Action SHAs in `.md` templates** — Dependabot only scans workflow files, not markdown.
4. **Install-command pins inside scripts** — `go install`, `cargo install`, `pip install`, `npx <tool>@X.Y.Z` lines in shell scripts and Makefiles are invisible to Dependabot.

These four surface families are exactly what the bundled `version-audit-template` covers (step 10 of the skill). After enabling Dependabot, generate the audit script too — together they cover everything.

## Conflicting Existing Config

If `.github/dependabot.yml` already exists, do not overwrite. Merge:

1. Read the existing config.
2. For each ecosystem block already present: keep the user's `schedule`, `directory`, and any `groups` they've defined. If their `open-pull-requests-limit` is below 10, suggest raising it. If `versioning-strategy` is missing for `npm` or `pip` (after step 6 pinning), suggest adding `increase`.
3. For each ecosystem present in the repo but missing from the config: add a new block from the template.
4. Show the diff before writing. Let the user accept, modify, or skip.

## Auto-Merge Wiring (Optional, Out of Scope for This Skill)

The `*-minor-patch` group exists to make later auto-merge wiring simple. A separate workflow (out of scope for `pin-everything`) can listen for Dependabot PRs against that group and merge them after CI passes. Major bumps stay in the `*-major` group for human review. Set up that wiring with a dedicated skill or hand-rolled workflow once you have confidence in your CI.
