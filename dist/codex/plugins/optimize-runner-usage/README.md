# Optimize Runner Usage

Add paths-ignore, concurrency groups, and timeout-minutes to existing GitHub Actions workflows.

**Type:** Command
**Trigger:** `/optimize-runner-usage`

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Scans all workflow files in `.github/workflows/`, classifies each one by its trigger pattern (CI, Release, Secret scanning, etc.), and adds missing optimizations:

- **paths-ignore**: Skip CI runs for documentation-only changes (root-level `*.md`, `docs/**`, LICENSE, agent config files)
- **Concurrency groups**: Cancel in-progress runs when new commits are pushed to the same branch
- **timeout-minutes**: Prevent runaway jobs from consuming unlimited minutes

Each optimization is applied only where appropriate. For example, `paths-ignore` is added to CI workflows but not to release or secret scanning workflows. Release workflows use `cancel-in-progress: false` to avoid aborting deployments.

## Usage

```text
/optimize-runner-usage
```

## Examples

- "optimize runner usage": scans workflows and applies all three optimizations
- "add concurrency groups to my workflows": same behavior (all three are checked)
- "reduce CI costs": same behavior

## See Also

- [Set-Up CI](../set-up-ci/README.md): create CI workflows from scratch (includes these optimizations by default)
- [Set-Up Secret Scanning](../set-up-secret-scanning/README.md): add secret scanning workflows
- [All plugins](../../../../README.md)
