# Skip GitHub Release Creation When a Release Workflow Exists

## Context

The release skill (step 11) always tries to create a GitHub Release manually via `gh release create` after pushing a tag. However, many projects already have a GitHub Actions release workflow (e.g., `.github/workflows/release.yml`) that automatically creates a GitHub Release when a version tag is pushed. In those cases, the manual `gh release create` duplicates or conflicts with the automated workflow.

All scaffolded release workflows in this repository (Go CLI, Go library, Rust CLI, GoReleaser+Homebrew) share the same trigger pattern: `on: push: tags: - "v*"`. They create GitHub Releases automatically via GoReleaser or `softprops/action-gh-release`.

The fix: detect tag-triggered release workflows during pre-flight checks and conditionally skip the manual `gh release create` step.

## Detection Approach

Add a Grep command to the step 1 pre-flight parallel block:

```bash
grep -rl '"v\*"' .github/workflows/*.yml .github/workflows/*.yaml 2>/dev/null
```

If this returns any files, a release workflow exists. The `"v*"` string inside `.github/workflows/` is a highly specific signal: tag-triggered workflows matching `v*` are almost always release workflows. This avoids requiring `yq` and keeps detection simple.

## Files to Modify

### 1. `plugins/release/skills/release/SKILL.md`

Four areas need changes:

**Step 1 (Pre-Flight Checks):** Add the grep command to the parallel block. Note the result as a flag (e.g., "release workflow detected" or "no release workflow detected").

**Step 11 prompt:** Change the prompt wording based on detection:
- No workflow: "Push and create a GitHub Release for vVERSION?" (current behavior)
- Workflow detected: "Push commit and tag for vVERSION? (release workflow detected; it will create the GitHub Release automatically)"

**Step 11 "If the user declines":** Conditional manual commands:
- No workflow: show all three commands (push HEAD, push tag, `gh release create`) as today
- Workflow detected: show only the two push commands, note the workflow will handle the release

**Step 11 "If the user accepts" (11c-11e):** Add a branch after 11b:
- If a release workflow was detected: report that the workflow will create the GitHub Release when it runs, skip 11c/11d entirely, and go straight to 11e with adjusted output (no GitHub Release URL, note workflow will handle it)
- If no workflow detected: proceed with existing 11c/11d/11e unchanged

**Error Handling section:** Add a new entry: "Release workflow detected: skip manual GitHub Release creation; the workflow will create it when the tag is pushed."

### 2. `plugins/release/README.md`

Add `Bash(grep *)` to the recommended permissions array (line 47) so the workflow detection grep does not trigger a permission prompt.

### 3. `plugins/release/.claude-plugin/plugin.json`

Bump version from `1.2.0` to `1.3.0` (new capability: workflow-aware release).

### 4. `.claude-plugin/marketplace.json`

Mirror the version bump from `1.2.0` to `1.3.0` on line 304.

## Verification

1. Read the modified SKILL.md end-to-end to confirm the flow is coherent
2. Use `check-versions` skill to verify plugin.json and marketplace.json versions match
3. Review the conditional logic to ensure both paths (workflow exists / no workflow) are complete and consistent
