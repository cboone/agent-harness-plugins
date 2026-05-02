# Upgrade Everything

Assess every version reference in a repository, evaluate available upgrades with repo-specific risk and reward, and present selectable upgrade options.

**Type:** Skill
**Trigger:** `/upgrade-everything` (also activates automatically)

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Upgrade Everything** from the available plugins.

## What It Does

Builds a complete upgrade audit for the current repository by inventorying version references, resolving current upstream versions, and evaluating each available upgrade against repo-specific reward and risk. The result is a selectable Markdown matrix that includes every discovered upgrade candidate, including high-risk or low-value items, so the user can decide what to apply.

The skill applies only the upgrades the user explicitly selects. When applying upgrades, it preserves each ecosystem's normal update mechanism: package manager commands for manifests and lockfiles, targeted structured edits for configuration, and no hand-edited lockfiles when a package manager owns them.

## Usage

```text
/upgrade-everything
```

## Examples

- "upgrade everything"
- "check dependency upgrades"
- "what can be upgraded in this repo?"
- "assess upgrades but do not apply anything"

## See Also

- [Pin Everything](../pin-everything/README.md): harden mutable version references before or after upgrade review
- [Update Everything](../update-everything/README.md): audit plugin template drift rather than dependency currency
- [Release](../release/README.md): update release metadata after selected upgrades land
- [Lint and Fix](../lint-and-fix/README.md): format and verify files after upgrades
- [All plugins](../../README.md)
