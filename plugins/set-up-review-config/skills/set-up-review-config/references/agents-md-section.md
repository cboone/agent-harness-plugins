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
- Start each finding with the checklist name and the rule name, for example `write-go-code: Checked errors`.
- Do not report what these CI checks already report: CI-CHECKS.
- Do not review these paths: SKIP-PATHS.
- Claude Code Review takes its severities from `REVIEW.md`.
- Rules outside this block take precedence over it.

<!-- END set-up-review-config -->
```

## New File

When `AGENTS.md` does not exist and creating it is confirmed, write an H1 naming the repository, one blank line, then the section above.
