---
name: upgrade-everything
description: >-
  Assess every version reference in a repository, check current upstream
  versions, evaluate repo-specific risk and reward, and present selectable
  upgrade options. Use when the user says "upgrade everything", "upgrade all
  versions", "check dependency upgrades", "assess upgrades", "update
  dependencies", "what can be upgraded", or asks for a full upgrade audit.
  Always includes every discovered upgrade candidate in the plan and applies
  upgrades only after explicit user selection.
---

# Upgrade Everything

Audit every version reference in a repository, resolve current upstream versions, evaluate each available upgrade with repo-specific reward and risk, then apply only the upgrades the user explicitly selects.

## Workflow

### 1. Record the Audit Date

Run `date` before searching for upstream versions. Upgrade data is date-sensitive, so include the exact date in the audit summary and in any later note about unresolved or stale upstream information.

### 2. Detect Repository Shape

Detect the repository root, project languages, package managers, CI systems, release tooling, and whether the repo is an application, public library, template, plugin marketplace, or monorepo. Exclude generated, vendored, and cache directories from all version searches.

Always exclude at least:

- `.git/`
- `node_modules/`
- `.yarn/`
- `.lake/`
- `vendor/`
- `dist/`
- `target/`
- `.venv/`
- lockfile cache directories

Use `./references/version-surfaces.md` to decide which files and literals to inspect.

### 3. Discover Version Surfaces

Use the `pin-everything` surface coverage as the baseline, then add upgrade-specific surfaces. Inventory package manifests and lockfiles, GitHub Actions refs, reusable workflows, language runtime files, Docker and devcontainer images, tool install commands, package manager pins, schema URLs, marketplace and plugin versions, release config versions, and unclassified version-like literals in scripts, docs, and config.

For each discovered surface, record:

- File path and owning ecosystem
- Current value and surrounding context
- Whether a package manager, lockfile, generator, or template owns the value
- Whether the surface is user-facing documentation, executable automation, build metadata, or published API metadata

Do not classify a candidate as out of scope merely because the upgrade looks risky or low value.

### 4. Resolve Upstream Versions

Resolve current upstream versions from authoritative sources for each ecosystem. Use package registries, GitHub releases or tags, container registries, language and toolchain channels, schema publisher metadata, and project-specific release files where relevant.

Use `./references/upgrade-sources.md` for source-of-truth selection. Record the source URL or command, lookup date, latest value, and confidence. If upstream resolution fails, keep the candidate in the plan with status `Blocked` or `Unknown` instead of dropping it.

### 5. Classify Candidates

Build one numbered candidate record for every discovered upgrade opportunity. If a version surface is already current, summarize it separately as up to date unless the user asked for a full inventory.

Each candidate must include:

- Current value and latest value
- Upgrade type: patch, minor, major, digest, SHA, runtime, schema, channel, or unknown
- Source of truth and confidence
- Reward rating and reasons
- Risk rating and reasons
- Required validation
- Recommendation

Use `./references/risk-reward.md` for the reward and risk model. Risk affects ordering and recommendation, not inclusion.

### 6. Present the Upgrade Matrix

Present a Markdown matrix grouped by ecosystem and surface. Include every candidate, including high-risk, blocked, unknown, and low-reward upgrades.

Use this shape:

```text
| # | Ecosystem | Surface | Current | Latest | Type | Reward | Risk | Confidence | Recommendation | Validation |
|---|-----------|---------|---------|--------|------|--------|------|------------|----------------|------------|
```

After the matrix, list up-to-date surfaces and unresolved upstream lookups separately. Make the distinction between "not selected yet", "not recommended", and "blocked" explicit.

### 7. Ask for Selection

Ask the user which upgrades to apply. Offer these choices:

- Apply all upgrades
- Apply only low-risk upgrades
- Apply only selected candidate numbers
- Audit only
- Apply all except custom exclusions

Do not apply upgrades until the user explicitly selects a scope. If the user asks for audit-only, stop after reporting the matrix.

### 8. Apply Selected Upgrades

Apply only selected candidates. Preserve each ecosystem's normal update mechanism:

- Use package manager commands for manifests and lockfiles.
- Use targeted YAML, JSON, TOML, or lockfile-aware edits for configuration values.
- Do not hand-edit lockfiles when a package manager owns them.
- Preserve library constraints unless the user explicitly chooses to tighten them.
- Keep generated files under their generator's ownership where that generator is known.

Process upgrades in dependency-aware order: toolchain and package manager pins first, package manifests and lockfiles next, CI and release configuration after that, then documentation or template references.

### 9. Verify and Summarize

Run the relevant verification for the selected upgrades: package manager checks, lockfile consistency checks, tests, build commands, and CI or release validators present in the repo. After edits, invoke the `lint-and-fix` skill to run project linters and formatters.

Summarize the result under these headings:

- Upgraded
- Skipped by user
- Blocked
- Failed
- Already up to date
- Follow-up validation

Include any commands that failed and the concrete candidate numbers affected.

## Reference Navigation

- `./references/version-surfaces.md` - surfaces to discover before resolving upstream versions
- `./references/upgrade-sources.md` - authoritative upstream sources by ecosystem
- `./references/risk-reward.md` - reward, risk, confidence, recommendation, and validation model

## Error Handling

- **Upstream source unavailable:** Keep the candidate in the matrix with `Unknown` latest value, low confidence, and a clear blocked reason.
- **Ambiguous ownership:** Ask before editing if a version could be generated, owned by a lockfile, or part of public library compatibility metadata.
- **Package manager update fails:** Capture the failure, mark only the affected candidates as failed, and ask whether to continue with independent candidates.
- **High-risk migration notes:** Include the upgrade in the matrix with the migration note summarized and validation expanded. Do not hide it.
- **Conflicting lockfiles:** Stop before editing and ask which package manager owns the project.
