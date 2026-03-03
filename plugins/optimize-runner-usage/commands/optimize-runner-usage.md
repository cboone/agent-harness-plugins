---
description: Add paths-ignore, concurrency groups, and timeout-minutes to existing GitHub Actions workflows.
disable-model-invocation: true
---

# Optimize Runner Usage

Scan existing GitHub Actions workflows and add missing runner-usage optimizations: `paths-ignore` filters, concurrency groups, and `timeout-minutes` on jobs.

Private GitHub repos pay for Actions minutes, and macOS runners cost 10x Linux runners. These optimizations reduce wasted minutes by skipping unnecessary runs, cancelling superseded builds, and preventing runaway jobs.

## Workflow

### 1. Scan for Workflow Files

Use Glob to find all `.yml` and `.yaml` files in `.github/workflows/`.

If the `.github/workflows/` directory does not exist, abort with:

> No `.github/workflows/` directory found. This command optimizes existing GitHub Actions workflows. Use `/setup-ci` to create a CI workflow from scratch.

If no workflow files are found, abort with:

> No workflow files found in `.github/workflows/`. Use `/setup-ci` to create a CI workflow.

### 2. Classify Each Workflow

Read each workflow file and classify it based on its `on:` triggers.

GitHub Actions allows `on:` in multiple forms:

- Mapping form: `on: { push: ..., pull_request: ... }` (or multi-line equivalents)
- Single-event shorthand: `on: push`
- Multi-event shorthand: `on: [push, pull_request]`

Before classifying, normalize shorthand forms to mapping shape:

- `on: push` becomes `on: { push: {} }`
- `on: [push, pull_request]` becomes `on: { push: {}, pull_request: {} }`

If applying edits would require rewriting `on:` from shorthand into a mapping (for example, to add `paths-ignore` under `push:`), perform the rewrite explicitly, updating `on:` to a mapping while preserving existing semantics.

Then classify workflows using the normalized `on:` structure:

| Trigger pattern                                               | Classification  |
| ------------------------------------------------------------- | --------------- |
| `pull_request:` (any configuration)                           | CI              |
| `push:` with `branches:` (optionally plus `pull_request:`)    | CI              |
| `push:` with `tags:` only (no `branches:` or `pull_request:`) | Release         |
| `push:` with both `branches:` and `tags:`                     | Mixed           |
| `schedule:` / `workflow_dispatch:` only                       | Scheduled       |
| Bare `push:` with no filters                                  | Broad push      |
| Workflow name or filename contains secret scanning keyword    | Secret scanning |
| `workflow_call:` trigger                                      | Reusable        |

Secret scanning keywords: "gitleaks", "trufflehog", "secret", "scan" (case-insensitive).

Secret scanning is a subset of Broad push: if a workflow has a bare `push:` and matches a secret scanning keyword, classify it as Secret scanning rather than Broad push.

For the secret scanning keyword check, inspect in this order:

1. The workflow-level `name:` field (if present)
1. The workflow filename (without directory path) as a fallback
1. Optionally, job-level `name:` values as additional signals

Mixed workflows (both `branches:` and `tags:` on push) are not eligible for `paths-ignore` because it cannot be scoped to branch pushes only. They use `cancel-in-progress: false` for concurrency.

### 3. Analyze Each Workflow for Missing Optimizations

For each workflow file, check which of the three optimizations are already present and which are needed.

#### paths-ignore

**Eligible**: CI workflows only.

**Not eligible**: Release, Mixed, Scheduled, Secret scanning, Broad push, or Reusable workflows. Also not eligible if the trigger already has a `paths:` (positive filter), since `paths` and `paths-ignore` are mutually exclusive in GitHub Actions. Mixed workflows are excluded because `paths-ignore` under `push:` applies to both branch and tag pushes and cannot be scoped to branches only.

Standard `paths-ignore` list:

```yaml
paths-ignore:
  - "*.md"
  - "docs/**"
  - "LICENSE"
  - ".editorconfig"
  - ".claude/**"
  - "**/CLAUDE.md"
  - "**/AGENTS.md"
```

Add `paths-ignore` under each eligible trigger (`push:` and `pull_request:`).

#### Concurrency

**Eligible**: All workflow types.

Two concurrency group patterns are used, depending on classification:

**Ref-scoped pattern** (CI, Scheduled, Broad push, Mixed, Secret scanning, Reusable):

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # or false, per table below
```

**Tag-scoped pattern** (Release only):

```yaml
concurrency:
  group: ${{ github.repository }}-${{ github.workflow }}
  cancel-in-progress: false
```

Release workflows use the tag-scoped pattern because each tag push produces a unique `github.ref` (e.g., `refs/tags/v1.0.0`), so including it in the group never deduplicates concurrent runs. The tag-scoped pattern serializes all runs of the same release workflow regardless of which tag triggered them.

`cancel-in-progress` values by classification:

| Classification                  | `cancel-in-progress` | Concurrency pattern |
| ------------------------------- | -------------------- | ------------------- |
| CI, Scheduled, Broad push       | `true`               | Ref-scoped          |
| Mixed, Secret scanning          | `false`              | Ref-scoped          |
| Release                         | `false`              | Tag-scoped          |
| Reusable                        | `true`               | Ref-scoped          |

If an existing concurrency group is present but uses a different `group:` expression than the expected pattern for that classification, flag it for user review. Do not overwrite non-standard concurrency groups automatically.

If an existing concurrency group matches the expected pattern for that classification, check only whether `cancel-in-progress` needs updating.

#### timeout-minutes

**Eligible**: All jobs that lack a `timeout-minutes` key.

Assign timeouts by heuristic:

| Job indicator                                                 | Timeout |
| ------------------------------------------------------------- | ------- |
| Release, publish, or deploy jobs (by job name or steps)       | 30 min  |
| Rust build jobs (steps contain `cargo build` or `cargo test`) | 20 min  |
| Vuln check, shellcheck, or shell lint jobs                    | 10 min  |
| All other CI jobs                                             | 15 min  |

### 4. Present Summary and Confirm

Display a summary table of all workflows with their classifications and proposed changes:

```text
File                        Classification   paths-ignore   concurrency   timeout
ci.yml                      CI               + add          + add         + add (15m)
release.yml                 Release          skip           + add         + add (30m)
gitleaks.yml                Secret scanning  skip           + add         + add (15m)
```

Use `+` for additions, `skip` for not applicable, and a checkmark or note for already present.

**Markdown as source code**: Before applying `paths-ignore` to any workflow, ask once whether the project treats Markdown files as source code (e.g., a documentation-focused project where Markdown linting is a CI step). If yes, remove `"*.md"` from the `paths-ignore` list for all workflows.

**Confirmation**: Ask the user to confirm changes for each workflow individually, with options:

1. **Apply all**: Apply all proposed changes to all workflows
1. **Review each**: Step through each workflow one at a time
1. **Skip**: Skip a specific workflow
1. **Abort**: Stop without making any changes

### 5. Apply Changes

Use the Edit tool to apply changes. Order within each file:

1. **paths-ignore** first (under each eligible trigger)
1. **Concurrency group** second (top-level, after the `on:` block and before the next top-level key)
1. **timeout-minutes** third (on each job, after `runs-on:`)

Preserve existing YAML structure, indentation, and comments. Do not reformat or reorder existing content.

### 6. Summary

Print a final summary:

- List every modified file and what was added to each
- Note any skipped workflows and why (already optimized, user skipped, flagged for manual review)
- Suggest running CI to verify the changes do not break anything:

> Run your CI pipeline to verify the optimized workflows behave correctly. If any workflow skips when it should run, check the `paths-ignore` patterns.

## Edge Cases

- **`paths:` already present**: Do not add `paths-ignore` (mutually exclusive in GitHub Actions). Note in the summary.
- **Existing non-standard concurrency group**: Do not overwrite. Flag for the user to review manually. The expected pattern depends on classification: tag-scoped for Release, ref-scoped for all others.
- **Tag-triggered workflows (Release)**: Use the tag-scoped concurrency pattern (`${{ github.repository }}-${{ github.workflow }}`) instead of the ref-scoped pattern, because each tag produces a unique `github.ref` that never deduplicates. Always use `cancel-in-progress: false`.
- **Mixed triggers (branches + tags on push)**: Do not add `paths-ignore` (cannot be scoped to branches only without splitting the workflow). Add concurrency with `cancel-in-progress: false` and `timeout-minutes` as normal.
- **Already fully optimized**: Skip with a note that no changes are needed.
- **Reusable workflows (`workflow_call:`)**: Skip `paths-ignore`. Add concurrency and timeouts normally.
- **Markdown as source code**: User-confirmed. Remove `"*.md"` from the `paths-ignore` list.
- **Unparseable YAML**: Skip the file with a warning and continue with remaining files.

## Error Handling

- **No `.github/workflows/` directory**: Abort with a clear message suggesting `/setup-ci`.
- **No workflow files found**: Abort with a clear message suggesting `/setup-ci`.
- **YAML parse errors**: Skip the individual file with a warning and continue processing other files.
- **Empty workflow file**: Skip with a note.
