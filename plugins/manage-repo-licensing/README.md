# Manage Repo Licensing

Bootstrap, audit, and maintain REUSE-style mixed-license coverage in a repository.

**Type:** Skill
**Trigger:** `/manage-repo-licensing` (also activates automatically)

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Manage Repo Licensing** from the available plugins.

## What It Does

Encodes a REUSE-style workflow for repositories with mixed licensing (code, prose, config, generated artifacts, third-party reference material). The skill is a structured companion: it frames policy, standardizes placement, drives verification with `reuse lint`, and keeps SPDX, `LICENSES/`, `NOTICE`, and `REUSE.toml` in sync. It is not an automated sweeper.

Three operating modes:

- **Bootstrap** -- new repository: populate `LICENSES/`, author `NOTICE` and root `REUSE.toml`, apply SPDX headers or sidecars, produce a clean `reuse lint`.
- **Maintain** -- existing repository: audit drift, normalize license filenames, fold sidecars into `REUSE.toml` groups, strip inline SPDX from prose covered by the prose group, fix common drift patterns.
- **New-file drop** -- a single newly added file needs an SPDX header or sidecar. One-commit operation.

## Requirements

- [`reuse`](https://reuse.software/) tool. Install via Homebrew: `brew install reuse` (or via pipx: `pipx install reuse`).

## Usage

```text
/manage-repo-licensing
```

The skill activates when the user mentions licensing, SPDX headers, `REUSE.toml`, `NOTICE`, `LICENSES/` normalization, dual licensing, or `reuse lint` cleanup.

## Examples

- "license this repo" -- Bootstrap mode
- "audit license coverage" -- Maintain mode
- "this new file needs a license header" -- New-file drop
- "/manage-repo-licensing"

## See Also

- [Add Community Files](../add-community-files/README.md): adds CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, PR template (sibling repo-bootstrap concern)
- [All plugins](../../README.md)
