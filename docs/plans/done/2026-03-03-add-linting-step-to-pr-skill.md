# Add Linting Step to PR Skill

## Context

The PR skill (`/pr`) commits and pushes code without running linters first. This means code frequently gets pushed to the remote with lint and formatting errors, causing CI failures. The fix is to add a linting step between committing and pushing, using the existing `lint-and-fix` skill. This follows the same pattern already established by the `resolve-copilot-pr-feedback` skill (lines 247-262 of its SKILL.md).

## Changes

### 1. `plugins/pr/skills/pr/SKILL.md` (primary change)

**Insert new step 5 "Lint and Fix" between current step 4 (Commit Changes) and step 5 (Push to Remote).**

Insert after line 189 (end of current step 4):

````markdown
### 5. Lint and Fix

Run the `lint-and-fix` skill to catch lint and formatting errors before pushing. This prevents CI failures from code that does not pass project linters.

1. **Invoke the `lint-and-fix` skill** using the Skill tool with `--no-push`:

   ```text
   lint-and-fix --no-push
   ```

   This runs all detected project linters and formatters, auto-fixes what it can, manually resolves remaining issues, and commits the fixes without pushing.

1. **If no linters are detected**: Proceed to step 6. The absence of linters is not an error.
1. **If all linters pass** (with or without auto-fixes): Proceed to step 6. Any fix commits created by `lint-and-fix` will be included in the push.
1. **If linting issues remain after auto-fix and manual fix attempts**: Stop and report the unresolved lint errors. Do not push or create the PR. The user must resolve the remaining issues before retrying.
````

**Renumber subsequent steps:**

| Old | New | Title                   |
| --- | --- | ----------------------- |
| 5   | 6   | Push to Remote          |
| 6   | 7   | Create the Pull Request |
| 7   | 8   | Report Results          |

No internal cross-references use step numbers, so only the headings need updating.

**Add error handling entry** in the Error Handling section, after "Pre-commit hook failure" and before "Push rejected":

```markdown
- **Lint issues unresolved**: If the `lint-and-fix` skill reports unresolved issues after auto-fix and manual fix, stop before pushing. Report the remaining lint errors and suggest the user fix them manually before retrying `/pr`.
```

### 2. `plugins/pr/.claude-plugin/plugin.json`

Bump version from `1.4.3` to `1.5.0` (minor: new capability).

### 3. `.claude-plugin/marketplace.json`

Update the `pr` entry version from `1.4.3` to `1.5.0` to match. Do not bump `metadata.version` (no plugin added or removed).

### 4. `plugins/pr/README.md`

Update the "What It Does" description (line 21) to mention linting:

> Stages everything, generates a conventional commit message from the diff, runs project linters to catch issues before pushing, pushes the branch, and opens a PR with an auto-generated title and summary.

## Verification

1. Install the updated PR plugin locally
1. Run `/pr` on a project with linters configured: confirm linting runs between commit and push
1. Introduce a deliberate lint error and run `/pr`: confirm it stops before pushing and reports the error
1. Run `/pr` on a project with no linters: confirm it proceeds normally
1. Run `/check-versions` to verify version consistency
