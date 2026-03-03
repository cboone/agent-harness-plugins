# Create optimize-runner-usage Command Plugin

## Context

PR #169 added runner optimization patterns (paths-ignore, concurrency groups, timeout-minutes) to all CI/release template plugins (setup-ci, scaffold-go-cli, scaffold-go-library, setup-installers, etc.). New projects scaffolded with these plugins get the optimizations automatically. However, existing repositories that were set up before PR #169 still have unoptimized workflows. This command retrofits those optimizations onto existing GitHub Actions workflows.

Private GitHub repos pay for Actions minutes, and macOS runners cost 10x Linux runners, so reducing wasted minutes has real cost impact.

## Files to Create

### 1. `plugins/optimize-runner-usage/.claude-plugin/plugin.json`

Standard command plugin metadata. Version `1.0.0`.

```json
{
  "author": {
    "name": "Christopher Boone"
  },
  "commands": "./commands",
  "description": "Add paths-ignore, concurrency groups, and timeout-minutes to existing GitHub Actions workflows.",
  "homepage": "https://github.com/cboone/cboone-cc-plugins",
  "keywords": ["ci", "concurrency", "github-actions", "optimization", "timeout", "workflow"],
  "license": "MIT",
  "name": "optimize-runner-usage",
  "repository": "https://github.com/cboone/cboone-cc-plugins",
  "version": "1.0.0"
}
```

### 2. `plugins/optimize-runner-usage/commands/optimize-runner-usage.md`

The command file. Frontmatter with `disable-model-invocation: true`. Structured as a multi-step workflow that scans, classifies, previews, confirms, and applies optimizations.

#### Workflow Steps

**Step 1: Scan for workflow files.** List all `.yml`/`.yaml` files in `.github/workflows/`. Abort if none found.

**Step 2: Classify each workflow** by reading its `on:` triggers:

| Trigger pattern                                          | Classification                                                |
| -------------------------------------------------------- | ------------------------------------------------------------- |
| `push:` with `branches:` and/or `pull_request:`          | CI                                                            |
| `push:` with `tags:` only (no `branches:`)               | Release                                                       |
| `push:` with both `branches:` and `tags:`                | Mixed (treat as CI for paths-ignore, Release for concurrency) |
| `schedule:` / `workflow_dispatch:` only                  | Scheduled                                                     |
| Bare `push:` with no filters                             | Broad push                                                    |
| Name contains "gitleaks", "trufflehog", "secret", "scan" | Secret scanning (subset of Broad push)                        |
| `workflow_call:` trigger                                 | Reusable workflow                                             |

**Step 3: Analyze each workflow for missing optimizations.** For each file, check which of the three optimizations are already present and which are needed.

Eligibility rules:

- **paths-ignore**: Only CI workflows. NOT release, scheduled, secret scanning, or broad push. NOT if `paths:` (positive filter) already exists on the trigger. Standard list:

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

- **Concurrency**: All workflow types. CI/scheduled/broad use `cancel-in-progress: true`. Release/mixed use `cancel-in-progress: false`. If an existing but non-standard concurrency group is present, flag for user review (do not overwrite).

  ```yaml
  concurrency:
    group: ${{ github.workflow }}-${{ github.ref }}
    cancel-in-progress: true # or false for release/mixed
  ```

- **Timeout-minutes**: All jobs that lack it. Values by heuristic:

  | Job indicator                      | Timeout |
  | ---------------------------------- | ------- |
  | Release/publish/deploy jobs        | 30 min  |
  | Rust build (steps contain `cargo`) | 20 min  |
  | Vuln check, shellcheck, shell lint | 10 min  |
  | All other CI jobs                  | 15 min  |

**Step 4: Present summary and confirm.** Show a table of all workflows with classifications and proposed changes. Then, before applying paths-ignore to any workflow, ask once whether the project treats Markdown files as source code (if yes, remove `*.md` from the paths-ignore list). Confirm each workflow individually (apply all / review changes / skip / abort).

**Step 5: Apply changes** using the Edit tool. Order within each file: paths-ignore first (under each trigger), then concurrency (top-level, after `on:` block), then timeout-minutes (on each job, after `runs-on:`). Preserve existing YAML structure, indentation, and comments.

**Step 6: Summary.** List modified files and what was added. Note skipped workflows. Suggest running CI to verify.

#### Edge Cases

- **`paths:` already present**: Do not add `paths-ignore` (mutually exclusive). Note in summary.
- **Existing non-standard concurrency group**: Do not overwrite. Flag for manual review.
- **Mixed triggers (branches + tags)**: Add paths-ignore to branch triggers only. Use `cancel-in-progress: false`.
- **Already fully optimized**: Skip with a note.
- **Reusable workflows (`workflow_call:`)**: Skip paths-ignore. Add concurrency and timeouts normally.
- **Markdown as source code**: User-confirmed. Remove `*.md` from paths-ignore list.
- **Unparseable YAML**: Skip with warning.

#### Error Handling

- No `.github/workflows/` directory: abort with clear message.
- No workflow files found: abort with clear message.
- YAML parse errors: skip the file with a warning.

### 3. `plugins/optimize-runner-usage/README.md`

Standard plugin README following the pattern from setup-ci. Type: Command. Trigger: `/optimize-runner-usage`. See Also links to setup-ci and setup-secret-scanning.

## Files to Modify

### 4. `.claude-plugin/marketplace.json`

- Add the new plugin entry (alphabetically between `notify` and `pr`)
- Bump `metadata.version` from `1.19.0` to `1.20.0` (minor bump for new plugin)

### 5. Root `README.md`

**ToC**: Add a new "CI Optimization" subcategory under Commands, between "Code Quality" and "Scaffolding":

```markdown
<br>CI Optimization:
[Optimize Runner Usage](#optimize-runner-usage)
```

**Body**: Add a "CI Optimization" subsection under Commands (line ~270, between "Code Quality" and "Scaffolding"), with a subsection heading, one-line intro, and the plugin entry.

## Reference Files

- `plugins/setup-ci/commands/setup-ci.md`: Primary pattern reference for workflow steps, paths-ignore list, concurrency patterns, timeout values, and runner usage notes
- `plugins/setup-secret-scanning/commands/setup-secret-scanning.md`: Secret scanning edge case (no paths-ignore, yes concurrency/timeout)
- `docs/plans/done/2026-03-03-optimize-runner-usage.md`: The completed plan for PR #169 that established the optimization patterns

## Implementation Order

1. Create `plugins/optimize-runner-usage/.claude-plugin/plugin.json`
1. Create `plugins/optimize-runner-usage/commands/optimize-runner-usage.md`
1. Create `plugins/optimize-runner-usage/README.md`
1. Update `.claude-plugin/marketplace.json`
1. Update root `README.md`
1. Run `check-versions` skill
1. Run linters

## Verification

1. Run `bin/validate-json` and `bin/validate-plugins` to check JSON and plugin consistency
1. Run `check-versions` skill to verify version alignment
1. Run the repo's linters (`yarn lint` or equivalent) to check markdown and JSON formatting
1. Visually confirm README ToC follows one-entry-per-line convention
1. Verify YAML code blocks in the command file are syntactically correct
