# REVIEW.md Template

The root `REVIEW.md` that Claude Code Review sends to every agent that finds and verifies findings. Its agents may not open other files, so the block copies each installed checklist's Important rules inline. It deliberately does not copy the Nit rules: they would multiply the size of a file that every finding and verification agent reads, for findings this reviewer caps at five and drops after the first review. Copilot reads the checklists themselves and applies the Nits there.

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

This file does not carry the checklists' Nit rules. An agent reading it may not open another file, so what it guarantees is the Important rules above; the full Nit lists live in the checklists under `.github/skills/code-review/`, where Copilot code review applies them file by file. Report the Nits you can see in the diff yourself, and when one matches a rule you know from a checklist, start the finding with the checklist name and the rule name, for example `write-go-code: Checked errors`.

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

CI-CHECKS and SKIP-PATHS hold the same values as in the entry skill. When CI runs no checks, remove the CI line rather than replacing it: the list names what not to report, and the paragraph under "What Important means here" already keeps formatting and lint findings at Nit. The skip line is always present, since it names at least the installed checklists.
