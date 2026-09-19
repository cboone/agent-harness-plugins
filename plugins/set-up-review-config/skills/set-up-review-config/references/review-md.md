# REVIEW.md Template

The root `REVIEW.md` that Claude Code Review sends to every agent that finds and verifies findings. Its agents may not open other files, so the block copies each installed checklist's Important rules and points at the checklists only for Nits.

Uppercase words are placeholders, filled as described in `./references/code-review-skill.md`.

## File

When `REVIEW.md` does not exist, write the whole file. When it exists, write only the part from the BEGIN line through the END line.

```markdown
# Review instructions

<!-- BEGIN set-up-review-config -->

## What Important means here

Reserve Important for findings that would break behavior, lose or leak data, or break the build or a release, and for the checklist rules below. Other style, naming and wording findings are Nit at most.

IMPORTANT-RULES

## Nits

Nits come from the checklists in `.github/skills/code-review/`, and the `SKILL.md` there maps file patterns to checklists. Start each finding with the checklist name and the rule name, for example `write-go-code: Checked errors`.

## Cap the nits

Report at most five Nits per review. If you found more, say "plus N similar items" in the summary instead of posting them inline. If everything you found is a Nit, lead the summary with "No blocking issues."

## After the first review

On later reviews of the same pull request, post Important findings only and do not raise new Nits.

## Do not report

- Anything these CI checks already report: CI-CHECKS.
- Changes in these paths: SKIP-PATHS.
- Anything a checklist's Do not flag section excludes.

Rules outside this block take precedence over it.

<!-- END set-up-review-config -->
```

## IMPORTANT-RULES

For each installed checklist, in the order of `./references/guides.md`, a level-3 heading naming the guide and the file types it covers, then the bullets under that checklist's `## Important` heading, copied verbatim:

```markdown
### write-go-code (Go files)

- **Checked errors**: Every returned error is handled or returned. Discarding one with `_` needs a comment explaining why it cannot matter.
```

The CI-CHECKS and SKIP-PATHS lines follow the same rules as in the entry skill: replace the CI line with "Formatting and lint findings are Nits." when CI runs no checks, and remove the skip line when there are no skip paths.
