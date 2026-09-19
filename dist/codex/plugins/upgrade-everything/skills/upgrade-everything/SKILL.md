---
name: upgrade-everything
description: >-
  Assess every version reference in a repository, evaluate available upgrades
  with repo-specific risk and reward, and present selectable upgrade options.
---

# Upgrade Everything

Audit every version reference in a repository, resolve current upstream versions, evaluate each available upgrade with repo-specific reward and risk, then apply only the upgrades the user explicitly selects.

## Skill dependencies

- **Required:** `lint-and-fix`
- **Optional:** `triage-dependabot-prs`

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

Then check whether Dependabot already proposes any of these upgrades. Take `OWNER/REPO` from the `origin` remote (`git remote -v`); in a fork, that is the fork, not the upstream. List its open PRs once, naming the repository explicitly:

```bash
gh pr list --repo OWNER/REPO --author app/dependabot --state open --limit 500 --json number,title,headRefName,baseRefName,body,changedFiles,files
```

If the list returns exactly as many PRs as `--limit` allows, it may be cut off: re-run with a higher limit before matching, so an open proposal is not missed. Match each candidate to a PR only when the PR's `baseRefName` is the branch being audited (normally the default branch), by dependency name and by a file the PR touches, and record the PR number and the version it targets. A PR aimed at another branch cannot land here and proposes nothing for this audit. A single-dependency title names the target (`bump NAME from A to B`); a grouped PR lists its updates in the body (``Updates `NAME` from A to B``). Those lines carry no directory, so for a group across several directories, tie the dependency to the candidate's directory through the body's `Bumps the GROUP group with N updates in the DIR directory: NAMES` lines: the PR covers the candidate only when the line for its directory names the dependency. A touched file in that directory is not enough, since it can belong to another dependency in the group. When that line leaves the names off, as it does for a long list, read the candidate's manifest and lockfile changes in `gh pr diff N --repo OWNER/REPO`. `files` lists at most the first 100 paths of a PR: when `changedFiles` is larger, read the full list with `gh pr diff N --repo OWNER/REPO --name-only` before matching on paths. A grouped body can be truncated: when it contains `_Description has been truncated_`, or lists fewer Updates lines than the title announces, read the manifest and lockfile changes with `gh pr diff N --repo OWNER/REPO` before concluding the PR does not cover a candidate. When `gh` is unavailable or unauthenticated, the repository has no GitHub remote, or the command fails for any other reason, skip this check and say so in the audit summary. It is supporting evidence, so its failure never stops the audit.

### 5. Classify Candidates

Build one numbered candidate record for every discovered upgrade opportunity. If a version surface is already current, summarize it separately as up to date unless the user asked for a full inventory.

Each candidate must include:

- Current value and latest value
- Upgrade type: patch, minor, major, digest, SHA, runtime, schema, channel, or unknown
- Source of truth and confidence
- Reward rating and reasons
- Risk rating and reasons
- Required validation
- Open Dependabot PR, if any, and the version it targets
- Recommendation

Use `./references/risk-reward.md` for the reward and risk model. Risk affects ordering and recommendation, not inclusion.

### 6. Present the Upgrade Matrix

Present a Markdown matrix grouped by ecosystem and surface. Include every candidate, including high-risk, blocked, unknown, and low-reward upgrades.

Use this shape:

```text
| # | Ecosystem | Surface | Current | Latest | Type | Reward | Risk | Confidence | Open PR | Recommendation | Validation |
|---|-----------|---------|---------|--------|------|--------|------|------------|---------|----------------|------------|
```

After the matrix, list up-to-date surfaces and unresolved upstream lookups separately. Make the distinction between "not selected yet", "not recommended", and "blocked" explicit.

When an open Dependabot PR already targets the latest value, the upgrade is already proposed. Recommend handling that PR with the `triage-dependabot-prs` skill rather than applying the upgrade locally, and say so in the Recommendation cell (for example, `Recommended: triage #42`). When the PR targets an older version than the latest, note that a local upgrade will supersede it.

### 7. Ask for Selection

Ask the user which upgrades to apply. Offer these choices:

- Apply all upgrades
- Apply only low-risk upgrades
- Apply only selected candidate numbers
- Audit only
- Apply all except custom exclusions
- Triage the open Dependabot PRs instead, for the candidates that have one (invoke the `triage-dependabot-prs` skill)

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
- Dependabot PRs superseded

Include any commands that failed and the concrete candidate numbers affected. Under "Dependabot PRs superseded", list each open Dependabot PR that an applied upgrade makes redundant, and suggest closing them with the `triage-dependabot-prs` skill once the upgrade merges.

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
