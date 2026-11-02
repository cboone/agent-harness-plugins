# AGENTS.md Section Template

The section Codex reads for code review rules. Codex applies the root `AGENTS.md` and any nested `AGENTS.md` that covers a changed file, and posts only P0 and P1 findings on GitHub. Copilot code review also reads the root `AGENTS.md`, and so does Claude Code Review when `CLAUDE.md` is a symlink to it, so the section stays short: every interactive agent session loads it too.

Uppercase words are placeholders, filled as described in `./references/code-review-skill.md`.

## Section

Append the heading and the block when the file has no `## Code Review Rules` heading. When it has one, write only the block, inside that section.

```markdown
## Code Review Rules

<!-- BEGIN set-up-review-config -->

- Review each changed file against its checklist in `.github/skills/code-review/`; the `SKILL.md` there maps file patterns to checklists.
- Rules under a checklist's Important heading are P1. All other checklist rules are P2 or lower.
- When a finding matches a checklist rule, start it with the checklist name and the exact rule name, for example CITATION-EXAMPLE. Otherwise start it with `Uncited:` and describe the concrete defect; never invent a rule name.
- For uncited findings, behavior defects, data loss or leaks, and build or release failures are Important (P1); style, naming and wording are Nit (P2 or lower). Important findings block merging and must all be reported; uncited Nits count toward the same five-Nit cap.
- Combine repeats of the same defect across files into one finding listing the affected paths, unless they need different fixes.
- Do not report what these CI checks already report: CI-CHECKS.
- Do not review these paths: SKIP-PATHS.
- Claude Code Review takes its severities from `REVIEW.md`.
- Rules outside this block take precedence over it.

<!-- END set-up-review-config -->
```

## New File

When `AGENTS.md` does not exist and creating it is confirmed, write an H1 naming the repository, one blank line, then the section above.
